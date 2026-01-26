#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Unit tests for unmanic.webserver.api_v2.health_api module.

Tests the health check API endpoints including:
- Full health status
- Liveness probe
- Readiness probe
"""

import pytest
from unittest.mock import MagicMock, patch
import time

from unmanic.webserver.api_v2.health_api import ApiHealthHandler, _APP_START_TIME


class TestApiHealthHandlerRoutes:
    """Test route configuration."""

    def test_has_health_route(self):
        """Should have /health route."""
        routes = ApiHealthHandler.routes
        health_route = next((r for r in routes if r["path_pattern"] == r"/health"), None)
        assert health_route is not None
        assert "GET" in health_route["supported_methods"]
        assert health_route["call_method"] == "get_health"

    def test_has_liveness_route(self):
        """Should have /health/live route."""
        routes = ApiHealthHandler.routes
        live_route = next((r for r in routes if r["path_pattern"] == r"/health/live"), None)
        assert live_route is not None
        assert "GET" in live_route["supported_methods"]
        assert live_route["call_method"] == "get_liveness"

    def test_has_readiness_route(self):
        """Should have /health/ready route."""
        routes = ApiHealthHandler.routes
        ready_route = next((r for r in routes if r["path_pattern"] == r"/health/ready"), None)
        assert ready_route is not None
        assert "GET" in ready_route["supported_methods"]
        assert ready_route["call_method"] == "get_readiness"


class TestHealthChecks:
    """Test health check methods."""

    @pytest.fixture
    def handler(self):
        """Create a mock handler instance."""
        handler = ApiHealthHandler.__new__(ApiHealthHandler)
        handler.logger = MagicMock()
        handler.config = MagicMock()
        handler.config.get_config_path.return_value = "/tmp/test_config"
        handler.config.get_cache_path.return_value = "/tmp/test_cache"
        handler.config.read_version.return_value = "1.0.0"
        return handler

    def test_check_database_healthy(self, handler):
        """Database check should return healthy when accessible."""
        with patch("unmanic.libs.unmodels.lib.Database") as mock_db:
            mock_db.get_database.return_value = MagicMock()
            result = handler._check_database()
            assert result["status"] == "healthy"
            assert result["message"] == "OK"

    def test_check_database_unhealthy_not_initialized(self, handler):
        """Database check should return unhealthy when not initialized."""
        with patch("unmanic.libs.unmodels.lib.Database") as mock_db:
            mock_db.get_database.return_value = None
            result = handler._check_database()
            assert result["status"] == "unhealthy"
            assert "not initialized" in result["message"]

    def test_check_database_unhealthy_on_exception(self, handler):
        """Database check should return unhealthy on exception."""
        with patch("unmanic.libs.unmodels.lib.Database") as mock_db:
            mock_db.get_database.side_effect = Exception("Connection failed")
            result = handler._check_database()
            assert result["status"] == "unhealthy"
            assert "Connection failed" in result["message"]

    def test_check_config_path_healthy(self, handler):
        """Config path check should return healthy when accessible."""
        with patch("os.path.exists", return_value=True):
            with patch("os.access", return_value=True):
                result = handler._check_config_path()
                assert result["status"] == "healthy"

    def test_check_config_path_unhealthy_not_found(self, handler):
        """Config path check should return unhealthy when not found."""
        with patch("os.path.exists", return_value=False):
            result = handler._check_config_path()
            assert result["status"] == "unhealthy"
            assert "not found" in result["message"]

    def test_check_config_path_degraded_not_writable(self, handler):
        """Config path check should return degraded when not writable."""
        with patch("os.path.exists", return_value=True):
            with patch("os.access", return_value=False):
                result = handler._check_config_path()
                assert result["status"] == "degraded"
                assert "not writable" in result["message"]

    def test_check_cache_path_healthy(self, handler):
        """Cache path check should return healthy when accessible."""
        with patch("os.path.exists", return_value=True):
            with patch("os.access", return_value=True):
                result = handler._check_cache_path()
                assert result["status"] == "healthy"

    def test_check_cache_path_degraded_not_found(self, handler):
        """Cache path check should return degraded when not found."""
        with patch("os.path.exists", return_value=False):
            result = handler._check_cache_path()
            assert result["status"] == "degraded"
            assert "not found" in result["message"]


class TestAppStartTime:
    """Test application start time tracking."""

    def test_app_start_time_is_set(self):
        """APP_START_TIME should be set to a valid timestamp."""
        assert _APP_START_TIME > 0
        # Should be within the last hour (reasonable for test execution)
        assert time.time() - _APP_START_TIME < 3600

    def test_uptime_calculation(self):
        """Uptime should be calculable from APP_START_TIME."""
        uptime = int(time.time() - _APP_START_TIME)
        assert uptime >= 0


class TestFileHealthCheckRoute:
    """Test file health check route configuration."""

    def test_has_file_health_route(self):
        """Should have /health/file route."""
        routes = ApiHealthHandler.routes
        file_route = next((r for r in routes if r["path_pattern"] == r"/health/file"), None)
        assert file_route is not None
        assert "POST" in file_route["supported_methods"]
        assert file_route["call_method"] == "check_file_health"


class TestFileHealthCheck:
    """Test file health check endpoint."""

    @pytest.fixture
    def handler(self):
        """Create a mock handler instance."""
        handler = ApiHealthHandler.__new__(ApiHealthHandler)
        handler.logger = MagicMock()
        handler.config = MagicMock()
        handler.route = {"call_method": "check_file_health"}
        handler.set_status = MagicMock()
        handler.write = MagicMock()
        handler.write_success = MagicMock()
        handler.write_error = MagicMock()
        handler.build_response = MagicMock(side_effect=lambda schema, data: data)
        return handler

    def test_returns_error_for_missing_body(self, handler):
        """Should return 400 for missing request body."""
        import asyncio

        handler.get_body_arguments = MagicMock(return_value=None)

        asyncio.get_event_loop().run_until_complete(handler.check_file_health())

        handler.set_status.assert_called_with(400)
        handler.write.assert_called()
        assert "required" in str(handler.write.call_args).lower()

    def test_returns_error_for_missing_file_path(self, handler):
        """Should return 400 for missing file_path."""
        import asyncio

        # Non-empty dict but without file_path key
        handler.get_body_arguments = MagicMock(return_value={"other_key": "value"})

        asyncio.get_event_loop().run_until_complete(handler.check_file_health())

        handler.set_status.assert_called_with(400)
        handler.write.assert_called()
        assert "file_path" in str(handler.write.call_args).lower()

    def test_returns_error_for_nonexistent_file(self, handler):
        """Should return 404 for non-existent file."""
        import asyncio

        handler.get_body_arguments = MagicMock(return_value={"file_path": "/nonexistent/file.mkv"})

        with patch("unmanic.webserver.api_v2.health_api.os.path.exists", return_value=False):
            asyncio.get_event_loop().run_until_complete(handler.check_file_health())

        handler.set_status.assert_called_with(404)

    def test_returns_health_check_result(self, handler):
        """Should return health check result for valid file."""
        import asyncio
        from unmanic.libs.health_check import HealthStatus, HealthCheckResult

        handler.get_body_arguments = MagicMock(return_value={"file_path": "/test/file.mkv"})

        mock_result = HealthCheckResult(
            status=HealthStatus.HEALTHY,
            path="/test/file.mkv",
        )

        with patch("unmanic.webserver.api_v2.health_api.os.path.exists", return_value=True):
            with patch("unmanic.webserver.api_v2.health_api.UnmanicSettings") as mock_settings:
                mock_settings.return_value.health_check_timeout_seconds = 300
                mock_settings.return_value.health_check_algorithm = "md5"

                with patch("unmanic.webserver.api_v2.health_api.check_file_integrity") as mock_check:
                    mock_check.return_value = mock_result

                    asyncio.get_event_loop().run_until_complete(handler.check_file_health())

        handler.write_success.assert_called_once()

    def test_includes_checksum_when_requested(self, handler):
        """Should include checksum when include_checksum is True."""
        import asyncio
        from unmanic.libs.health_check import HealthStatus, HealthCheckResult

        handler.get_body_arguments = MagicMock(
            return_value={
                "file_path": "/test/file.mkv",
                "include_checksum": True,
            }
        )

        mock_result = HealthCheckResult(
            status=HealthStatus.HEALTHY,
            path="/test/file.mkv",
        )

        with patch("unmanic.webserver.api_v2.health_api.os.path.exists", return_value=True):
            with patch("unmanic.webserver.api_v2.health_api.UnmanicSettings") as mock_settings:
                mock_settings.return_value.health_check_timeout_seconds = 300
                mock_settings.return_value.health_check_algorithm = "md5"

                with patch("unmanic.webserver.api_v2.health_api.check_file_integrity") as mock_check:
                    mock_check.return_value = mock_result

                    with patch("unmanic.webserver.api_v2.health_api.get_file_checksum") as mock_checksum:
                        mock_checksum.return_value = "abc123def456"

                        asyncio.get_event_loop().run_until_complete(handler.check_file_health())

                        mock_checksum.assert_called_once_with("/test/file.mkv", algorithm="md5")

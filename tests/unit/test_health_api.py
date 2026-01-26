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
        with patch("unmanic.webserver.api_v2.health_api.Database") as mock_db:
            mock_db.get_database.return_value = MagicMock()
            result = handler._check_database()
            assert result["status"] == "healthy"
            assert result["message"] == "OK"

    def test_check_database_unhealthy_not_initialized(self, handler):
        """Database check should return unhealthy when not initialized."""
        with patch("unmanic.webserver.api_v2.health_api.Database") as mock_db:
            mock_db.get_database.return_value = None
            result = handler._check_database()
            assert result["status"] == "unhealthy"
            assert "not initialized" in result["message"]

    def test_check_database_unhealthy_on_exception(self, handler):
        """Database check should return unhealthy on exception."""
        with patch("unmanic.webserver.api_v2.health_api.Database") as mock_db:
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

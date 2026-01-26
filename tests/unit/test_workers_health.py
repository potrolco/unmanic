#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Unit tests for worker health check integration.

Tests the health check methods added to the Worker class in Phase 2.
"""

import os
import tempfile
import pytest
from unittest.mock import MagicMock, patch

from unmanic.libs.health_check import HealthStatus, HealthCheckResult


class TestWorkerPreTranscodeHealthCheck:
    """Test __run_pre_transcode_health_check method."""

    def test_returns_true_when_disabled(self):
        """Should return True when pre-check is disabled."""
        from unmanic.libs.workers import Worker

        # Create a mock Worker instance
        worker = MagicMock(spec=Worker)
        worker._log = MagicMock()
        worker.current_task = MagicMock()
        worker.current_task.get_source_abspath.return_value = "/test/file.mkv"

        # Mock settings to disable pre-check
        with patch("unmanic.libs.workers.UnmanicSettings") as mock_settings_class:
            mock_settings = MagicMock()
            mock_settings.enable_pre_transcode_health_check = False
            mock_settings_class.return_value = mock_settings

            # Call the method through the class
            result = Worker._Worker__run_pre_transcode_health_check(worker)
            assert result is True

    def test_returns_true_for_healthy_file(self):
        """Should return True for healthy file."""
        from unmanic.libs.workers import Worker

        worker = MagicMock(spec=Worker)
        worker._log = MagicMock()
        worker.current_task = MagicMock()
        worker.current_task.get_source_abspath.return_value = "/test/file.mkv"
        worker.current_task.task = MagicMock()

        with patch("unmanic.libs.workers.UnmanicSettings") as mock_settings_class:
            mock_settings = MagicMock()
            mock_settings.enable_pre_transcode_health_check = True
            mock_settings.health_check_timeout_seconds = 300
            mock_settings.fail_on_pre_check_corruption = True
            mock_settings_class.return_value = mock_settings

            with patch("unmanic.libs.workers.check_file_integrity") as mock_check:
                mock_check.return_value = HealthCheckResult(
                    status=HealthStatus.HEALTHY,
                    path="/test/file.mkv",
                )

                result = Worker._Worker__run_pre_transcode_health_check(worker)
                assert result is True
                mock_check.assert_called_once()

    def test_returns_false_for_corrupted_file_when_fail_enabled(self):
        """Should return False for corrupted file when fail_on_corruption is True."""
        from unmanic.libs.workers import Worker

        worker = MagicMock(spec=Worker)
        worker._log = MagicMock()
        worker.current_task = MagicMock()
        worker.current_task.get_source_abspath.return_value = "/test/file.mkv"
        worker.current_task.task = MagicMock()

        with patch("unmanic.libs.workers.UnmanicSettings") as mock_settings_class:
            mock_settings = MagicMock()
            mock_settings.enable_pre_transcode_health_check = True
            mock_settings.health_check_timeout_seconds = 300
            mock_settings.fail_on_pre_check_corruption = True
            mock_settings_class.return_value = mock_settings

            with patch("unmanic.libs.workers.check_file_integrity") as mock_check:
                mock_check.return_value = HealthCheckResult(
                    status=HealthStatus.CORRUPTED,
                    path="/test/file.mkv",
                    errors=["Invalid NAL unit"],
                )

                result = Worker._Worker__run_pre_transcode_health_check(worker)
                assert result is False

    def test_returns_true_for_corrupted_file_when_fail_disabled(self):
        """Should return True for corrupted file when fail_on_corruption is False."""
        from unmanic.libs.workers import Worker

        worker = MagicMock(spec=Worker)
        worker._log = MagicMock()
        worker.current_task = MagicMock()
        worker.current_task.get_source_abspath.return_value = "/test/file.mkv"
        worker.current_task.task = MagicMock()

        with patch("unmanic.libs.workers.UnmanicSettings") as mock_settings_class:
            mock_settings = MagicMock()
            mock_settings.enable_pre_transcode_health_check = True
            mock_settings.health_check_timeout_seconds = 300
            mock_settings.fail_on_pre_check_corruption = False
            mock_settings_class.return_value = mock_settings

            with patch("unmanic.libs.workers.check_file_integrity") as mock_check:
                mock_check.return_value = HealthCheckResult(
                    status=HealthStatus.CORRUPTED,
                    path="/test/file.mkv",
                    errors=["Invalid NAL unit"],
                )

                result = Worker._Worker__run_pre_transcode_health_check(worker)
                assert result is True

    def test_returns_true_for_warning_status(self):
        """Should return True for file with warnings."""
        from unmanic.libs.workers import Worker

        worker = MagicMock(spec=Worker)
        worker._log = MagicMock()
        worker.current_task = MagicMock()
        worker.current_task.get_source_abspath.return_value = "/test/file.mkv"
        worker.current_task.task = MagicMock()

        with patch("unmanic.libs.workers.UnmanicSettings") as mock_settings_class:
            mock_settings = MagicMock()
            mock_settings.enable_pre_transcode_health_check = True
            mock_settings.health_check_timeout_seconds = 300
            mock_settings.fail_on_pre_check_corruption = True
            mock_settings_class.return_value = mock_settings

            with patch("unmanic.libs.workers.check_file_integrity") as mock_check:
                mock_check.return_value = HealthCheckResult(
                    status=HealthStatus.WARNING,
                    path="/test/file.mkv",
                    warnings=["Minor issue"],
                )

                result = Worker._Worker__run_pre_transcode_health_check(worker)
                assert result is True


class TestWorkerPostTranscodeHealthCheck:
    """Test __run_post_transcode_health_check method."""

    def test_returns_true_when_disabled(self):
        """Should return True when post-check is disabled."""
        from unmanic.libs.workers import Worker

        worker = MagicMock(spec=Worker)
        worker._log = MagicMock()

        with patch("unmanic.libs.workers.UnmanicSettings") as mock_settings_class:
            mock_settings = MagicMock()
            mock_settings.enable_post_transcode_health_check = False
            mock_settings_class.return_value = mock_settings

            result = Worker._Worker__run_post_transcode_health_check(worker, "/test/output.mkv")
            assert result is True

    def test_returns_true_for_healthy_output(self):
        """Should return True for healthy output file."""
        from unmanic.libs.workers import Worker

        worker = MagicMock(spec=Worker)
        worker._log = MagicMock()
        worker.current_task = MagicMock()
        worker.current_task.task = MagicMock()

        with patch("unmanic.libs.workers.UnmanicSettings") as mock_settings_class:
            mock_settings = MagicMock()
            mock_settings.enable_post_transcode_health_check = True
            mock_settings.health_check_timeout_seconds = 300
            mock_settings_class.return_value = mock_settings

            with patch("unmanic.libs.workers.check_file_integrity") as mock_check:
                mock_check.return_value = HealthCheckResult(
                    status=HealthStatus.HEALTHY,
                    path="/test/output.mkv",
                )

                result = Worker._Worker__run_post_transcode_health_check(worker, "/test/output.mkv")
                assert result is True

    def test_returns_false_for_corrupted_output(self):
        """Should return False for corrupted output file."""
        from unmanic.libs.workers import Worker

        worker = MagicMock(spec=Worker)
        worker._log = MagicMock()
        worker.current_task = MagicMock()
        worker.current_task.task = MagicMock()

        with patch("unmanic.libs.workers.UnmanicSettings") as mock_settings_class:
            mock_settings = MagicMock()
            mock_settings.enable_post_transcode_health_check = True
            mock_settings.health_check_timeout_seconds = 300
            mock_settings_class.return_value = mock_settings

            with patch("unmanic.libs.workers.check_file_integrity") as mock_check:
                mock_check.return_value = HealthCheckResult(
                    status=HealthStatus.CORRUPTED,
                    path="/test/output.mkv",
                    errors=["Corrupted frame"],
                )

                result = Worker._Worker__run_post_transcode_health_check(worker, "/test/output.mkv")
                assert result is False

    def test_stores_health_check_result_in_task(self):
        """Should store health check result in task object."""
        from unmanic.libs.workers import Worker

        worker = MagicMock(spec=Worker)
        worker._log = MagicMock()
        worker.current_task = MagicMock()
        worker.current_task.task = MagicMock()

        with patch("unmanic.libs.workers.UnmanicSettings") as mock_settings_class:
            mock_settings = MagicMock()
            mock_settings.enable_post_transcode_health_check = True
            mock_settings.health_check_timeout_seconds = 300
            mock_settings_class.return_value = mock_settings

            with patch("unmanic.libs.workers.check_file_integrity") as mock_check:
                mock_check.return_value = HealthCheckResult(
                    status=HealthStatus.HEALTHY,
                    path="/test/output.mkv",
                )

                Worker._Worker__run_post_transcode_health_check(worker, "/test/output.mkv")

                # Verify task attributes were set
                assert worker.current_task.task.post_health_check_status == "healthy"
                assert worker.current_task.task.post_health_check_errors == []


class TestWorkerHealthCheckErrorHandling:
    """Test error handling in health check methods."""

    def test_pre_check_returns_true_on_exception(self):
        """Should return True on exception (don't block on errors)."""
        from unmanic.libs.workers import Worker

        worker = MagicMock(spec=Worker)
        worker._log = MagicMock()
        worker.current_task = MagicMock()
        worker.current_task.get_source_abspath.side_effect = Exception("Test error")

        with patch("unmanic.libs.workers.UnmanicSettings") as mock_settings_class:
            mock_settings = MagicMock()
            mock_settings.enable_pre_transcode_health_check = True
            mock_settings_class.return_value = mock_settings

            result = Worker._Worker__run_pre_transcode_health_check(worker)
            assert result is True

    def test_post_check_returns_true_on_exception(self):
        """Should return True on exception (don't block on errors)."""
        from unmanic.libs.workers import Worker

        worker = MagicMock(spec=Worker)
        worker._log = MagicMock()

        with patch("unmanic.libs.workers.UnmanicSettings") as mock_settings_class:
            mock_settings = MagicMock()
            mock_settings.enable_post_transcode_health_check = True
            mock_settings_class.return_value = mock_settings

            with patch("unmanic.libs.workers.check_file_integrity") as mock_check:
                mock_check.side_effect = Exception("Test error")

                result = Worker._Worker__run_post_transcode_health_check(worker, "/test/output.mkv")
                assert result is True

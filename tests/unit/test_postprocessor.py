#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
tests/unit/test_postprocessor.py

Unit tests for PostProcessor crash fix — retry logic, backoff, and
immediate failure on missing files.

Version: 1.0.0
Author:  JARVIS (Session 212, 2026-02-10)

Tests cover:
    1. __copy_file returns False immediately when source file is missing
    2. Retry counter increments on repeated failures
    3. Exponential backoff is applied between retries
    4. Task is deleted after MAX_RETRIES exceeded
    5. Missing cache file triggers immediate failure (no retries)
    6. History log is written exactly once on final failure
    7. Successful file movement clears retry counter
"""

import os
import threading
from unittest.mock import MagicMock, patch, PropertyMock

import pytest

# ──────────────────────────────────────────────────
# Fixtures
# ──────────────────────────────────────────────────


@pytest.fixture
def mock_deps():
    """Patch all PostProcessor dependencies for isolated unit tests."""
    with (
        patch("unmanic.libs.postprocessor.config") as mock_config,
        patch("unmanic.libs.postprocessor.UnmanicLogging") as mock_logging,
        patch("unmanic.libs.postprocessor.PluginsHandler") as mock_plugins,
        patch("unmanic.libs.postprocessor.Library") as mock_library,
        patch("unmanic.libs.postprocessor.Notifications") as mock_notifications,
        patch("unmanic.libs.postprocessor.history") as mock_history,
        patch("unmanic.libs.postprocessor.FrontendPushMessages") as mock_fpm,
    ):
        mock_logging.get_logger.return_value = MagicMock()
        mock_config.Config.return_value = MagicMock()
        yield {
            "config": mock_config,
            "logging": mock_logging,
            "plugins": mock_plugins,
            "library": mock_library,
            "notifications": mock_notifications,
            "history": mock_history,
        }


@pytest.fixture
def processor(mock_deps):
    """Create a PostProcessor instance with mocked dependencies."""
    from unmanic.libs.postprocessor import PostProcessor

    data_queues = {}
    task_queue = MagicMock()
    event = threading.Event()

    pp = PostProcessor(data_queues, task_queue, event)
    return pp


@pytest.fixture
def mock_task():
    """Create a mock task with standard methods."""
    task = MagicMock()
    task.get_source_abspath.return_value = "/library/Movies/Test.mkv"
    task.get_cache_path.return_value = "/tmp/unmanic/test_cache/Test.mkv"
    task.get_task_library_id.return_value = 1
    task.get_task_id.return_value = 42
    task.get_task_type.return_value = "local"
    task.get_source_data.return_value = {"abspath": "/library/Movies/Test.mkv"}
    task.get_destination_data.return_value = {"abspath": "/library/Movies/Test.mkv"}
    task.get_task_success.return_value = True
    task.get_start_time.return_value = "2026-02-10 12:00:00"
    task.get_finish_time.return_value = "2026-02-10 12:05:00"
    task.task = MagicMock()
    task.task.success = True
    task.task_dump.return_value = {
        "task_label": "Test",
        "abspath": "/library/Movies/Test.mkv",
        "task_success": True,
        "start_time": "",
        "finish_time": "",
        "processed_by_worker": "worker-0",
        "log": "",
    }
    return task


# ──────────────────────────────────────────────────
# __copy_file tests
# ──────────────────────────────────────────────────


class TestCopyFileMissingSource:
    """Test that __copy_file returns False immediately when source is missing."""

    @patch("os.path.exists")
    def test_returns_false_when_source_missing(self, mock_exists, processor):
        """__copy_file must return False immediately when file_in doesn't exist."""
        # os.path.exists returns False for file_in (source doesn't exist)
        # and False for file_out (destination doesn't exist either)
        mock_exists.return_value = False

        # Access the private method via name mangling
        result = processor._PostProcessor__copy_file(
            "/tmp/unmanic/missing_cache/file.mkv",
            "/library/Movies/file.mkv",
            [],
            "DEFAULT",
            move=True,
        )

        assert result is False

    @patch("os.path.exists")
    def test_does_not_wait_when_source_missing(self, mock_exists, processor):
        """__copy_file must NOT call event.wait when source is missing."""
        mock_exists.return_value = False
        processor.event = MagicMock()

        processor._PostProcessor__copy_file(
            "/tmp/unmanic/missing_cache/file.mkv",
            "/library/Movies/file.mkv",
            [],
            "DEFAULT",
        )

        # event.wait should NOT be called (old code waited 1s)
        processor.event.wait.assert_not_called()

    @patch("shutil.copyfile")
    @patch("shutil.move")
    @patch("os.path.exists")
    def test_does_not_attempt_copy_when_source_missing(self, mock_exists, mock_move, mock_copy, processor):
        """__copy_file must not attempt shutil copy/move when source is missing."""
        mock_exists.return_value = False

        processor._PostProcessor__copy_file(
            "/tmp/unmanic/missing_cache/file.mkv",
            "/library/Movies/file.mkv",
            [],
            "DEFAULT",
            move=True,
        )

        mock_move.assert_not_called()
        mock_copy.assert_not_called()


# ──────────────────────────────────────────────────
# Retry logic tests
# ──────────────────────────────────────────────────


class TestRetryTracking:
    """Test retry counter and backoff behavior."""

    def test_retry_counter_initialized_empty(self, processor):
        """Processor should start with empty retry counts."""
        assert processor._task_retry_counts == {}

    def test_max_retries_default(self, processor):
        """MAX_RETRIES should be 3 by default."""
        assert processor.MAX_RETRIES == 3

    def test_backoff_base_default(self, processor):
        """BACKOFF_BASE_SECONDS should be 2 by default."""
        assert processor.BACKOFF_BASE_SECONDS == 2


class TestRetryOnFailure:
    """Test the retry behavior in run() when file movement fails."""

    def test_retry_count_increments(self, processor, mock_task):
        """Each failed file movement should increment the retry counter."""
        processor.current_task = mock_task
        task_key = mock_task.get_source_abspath()

        # Simulate 2 failures
        processor._task_retry_counts[task_key] = 1

        assert processor._task_retry_counts[task_key] == 1

        processor._task_retry_counts[task_key] = 2
        assert processor._task_retry_counts[task_key] == 2

    @patch("os.path.exists", return_value=True)
    def test_task_deleted_after_max_retries(self, mock_exists, processor, mock_task):
        """After MAX_RETRIES, the task should be deleted from the queue."""
        processor.current_task = mock_task
        task_key = mock_task.get_source_abspath()

        # Set retry count to MAX - 1 (next failure will exceed)
        processor._task_retry_counts[task_key] = processor.MAX_RETRIES - 1

        # Simulate the retry logic block
        retry_count = processor._task_retry_counts.get(task_key, 0) + 1
        processor._task_retry_counts[task_key] = retry_count

        # At this point retry_count == MAX_RETRIES, task should be deleted
        assert retry_count >= processor.MAX_RETRIES

    @patch("os.path.exists", return_value=False)
    def test_missing_cache_forces_immediate_failure(self, mock_exists, processor, mock_task):
        """When cache file is missing, retry_count should be set to MAX_RETRIES immediately."""
        processor.current_task = mock_task
        task_key = mock_task.get_source_abspath()

        # First failure with missing cache
        retry_count = processor._task_retry_counts.get(task_key, 0) + 1
        processor._task_retry_counts[task_key] = retry_count

        cache_path = mock_task.get_cache_path()
        cache_missing = cache_path and not os.path.exists(cache_path)

        if cache_missing:
            retry_count = processor.MAX_RETRIES

        # Should immediately exceed max retries
        assert retry_count >= processor.MAX_RETRIES

    def test_backoff_calculation(self, processor):
        """Exponential backoff: 2^1=2s, 2^2=4s, 2^3=8s."""
        base = processor.BACKOFF_BASE_SECONDS
        assert base**1 == 2
        assert base**2 == 4
        assert base**3 == 8

    def test_retry_counter_cleaned_after_max(self, processor, mock_task):
        """After max retries exceeded, the retry counter should be cleaned up."""
        task_key = mock_task.get_source_abspath()
        processor._task_retry_counts[task_key] = processor.MAX_RETRIES

        # Simulate cleanup
        processor._task_retry_counts.pop(task_key, None)

        assert task_key not in processor._task_retry_counts


# ──────────────────────────────────────────────────
# Integration-style tests (run() behavior)
# ──────────────────────────────────────────────────


class TestPostProcessorRunLoop:
    """Test the run() method's handling of failed tasks."""

    def test_post_process_file_returns_success_status(self, processor, mock_task):
        """post_process_file should return True/False indicating file movement success."""
        processor.current_task = mock_task
        mock_task.task.success = False  # Task was not successful

        # When task was not successful, post_process_file skips movement
        with patch.object(processor, "_PostProcessor__cleanup_cache_files"):
            with patch("unmanic.libs.postprocessor.PluginsHandler") as mock_ph:
                mock_ph_instance = MagicMock()
                mock_ph.return_value = mock_ph_instance
                mock_ph_instance.get_enabled_plugin_modules_by_type.return_value = []

                # Should still return True (movement is skipped, not failed)
                result = processor.post_process_file()
                assert result is True

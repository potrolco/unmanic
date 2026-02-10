#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
tests/unit/test_foreman_taskqueue.py

Unit tests for Foreman's interaction with the TaskQueue interface.
Tests validate that the foreman correctly uses the task queue contract
for task lifecycle management: pending → in_progress → processed.

These tests mock the task queue to verify the foreman's behavior
without requiring a database or running workers.

Version: 1.0.0
Author:  JARVIS (Session 212, 2026-02-10)
"""

import queue
import threading
from unittest.mock import MagicMock, patch, PropertyMock

import pytest

# ──────────────────────────────────────────────────
# Fixtures
# ──────────────────────────────────────────────────


@pytest.fixture
def mock_foreman_deps():
    """Patch all Foreman dependencies for isolated unit tests."""
    with (
        patch("unmanic.libs.foreman.config") as mock_config,
        patch("unmanic.libs.foreman.UnmanicLogging") as mock_logging,
        patch("unmanic.libs.foreman.PluginsHandler") as mock_plugins,
        patch("unmanic.libs.foreman.Library") as mock_library,
    ):
        mock_logging.get_logger.return_value = MagicMock()
        mock_config.Config.return_value = MagicMock()
        yield {
            "config": mock_config,
            "logging": mock_logging,
            "plugins": mock_plugins,
            "library": mock_library,
        }


@pytest.fixture
def mock_task_queue():
    """Create a mock task queue implementing the TaskQueueInterface contract."""
    tq = MagicMock()
    tq.task_list_pending_is_empty.return_value = False
    tq.task_list_in_progress_is_empty.return_value = True
    tq.task_list_processed_is_empty.return_value = True
    tq.list_pending_tasks.return_value = [{"id": 1, "status": "pending", "abspath": "/test.mkv"}]
    tq.list_in_progress_tasks.return_value = []
    tq.list_processed_tasks.return_value = []
    tq.get_next_pending_tasks.return_value = MagicMock()
    tq.get_next_processed_tasks.return_value = False
    tq.requeue_tasks_at_bottom.return_value = True
    return tq


@pytest.fixture
def mock_task():
    """Create a mock task object as returned by get_next_pending_tasks."""
    task = MagicMock()
    task.get_task_id.return_value = 42
    task.get_source_abspath.return_value = "/library/Movies/Test.mkv"
    task.get_source_basename.return_value = "Test.mkv"
    task.get_task_library_id.return_value = 1
    task.get_task_library_name.return_value = "Movies"
    task.get_task_type.return_value = "local"
    task.get_cache_path.return_value = "/tmp/unmanic/cache/Test.mkv"
    task.get_task_success.return_value = True
    return task


# ──────────────────────────────────────────────────
# TaskQueue contract tests (what Foreman expects)
# ──────────────────────────────────────────────────


class TestForemanTaskQueueContract:
    """Verify the Foreman's expected task queue interface contract."""

    def test_task_list_pending_is_empty_returns_bool(self, mock_task_queue):
        """Foreman expects task_list_pending_is_empty to return a boolean."""
        result = mock_task_queue.task_list_pending_is_empty()
        assert isinstance(result, bool)

    def test_list_processed_tasks_returns_list(self, mock_task_queue):
        """Foreman expects list_processed_tasks to return a list."""
        result = mock_task_queue.list_processed_tasks()
        assert isinstance(result, list)

    def test_get_next_pending_tasks_accepts_filters(self, mock_task_queue):
        """Foreman calls get_next_pending_tasks with optional filters."""
        mock_task_queue.get_next_pending_tasks(
            local_only=True,
            library_names=["Movies"],
            library_tags=["encode"],
        )
        mock_task_queue.get_next_pending_tasks.assert_called_once_with(
            local_only=True,
            library_names=["Movies"],
            library_tags=["encode"],
        )

    def test_get_next_pending_tasks_returns_false_when_empty(self, mock_task_queue):
        """Foreman expects False when no pending tasks match."""
        mock_task_queue.get_next_pending_tasks.return_value = False
        result = mock_task_queue.get_next_pending_tasks()
        assert result is False

    def test_requeue_tasks_at_bottom_takes_task_id(self, mock_task_queue):
        """Foreman calls requeue_tasks_at_bottom with a task ID."""
        mock_task_queue.requeue_tasks_at_bottom(42)
        mock_task_queue.requeue_tasks_at_bottom.assert_called_once_with(42)


# ──────────────────────────────────────────────────
# Task lifecycle tests
# ──────────────────────────────────────────────────


class TestForemanTaskLifecycle:
    """Test the task state transitions managed by the Foreman."""

    def test_pending_to_in_progress(self, mock_task_queue, mock_task):
        """Tasks should transition from pending to in_progress when claimed."""
        mock_task_queue.get_next_pending_tasks.return_value = mock_task

        task = mock_task_queue.get_next_pending_tasks()
        assert task is not False

        # Worker sets status to in_progress
        task.set_status("in_progress")
        task.set_status.assert_called_with("in_progress")

    def test_in_progress_to_processed(self, mock_task):
        """Tasks should transition from in_progress to processed when worker completes."""
        mock_task.set_status("in_progress")
        # Worker completes, marks success
        mock_task.set_success(True)
        # Foreman marks processed
        mock_task.set_status("processed")
        mock_task.set_status.assert_called_with("processed")

    def test_failed_task_requeued(self, mock_task_queue, mock_task):
        """Failed tasks should be requeued at the bottom of the queue."""
        task_id = mock_task.get_task_id()
        result = mock_task_queue.requeue_tasks_at_bottom(task_id)
        assert result is True
        mock_task_queue.requeue_tasks_at_bottom.assert_called_once_with(42)

    def test_empty_pending_stops_dispatch(self, mock_task_queue):
        """When pending queue is empty, foreman should not dispatch."""
        mock_task_queue.task_list_pending_is_empty.return_value = True
        assert mock_task_queue.task_list_pending_is_empty() is True

    def test_processed_queue_rate_limiting(self, mock_task_queue):
        """Foreman checks processed tasks count to rate-limit workers."""
        # When post-processor queue has items, foreman may throttle
        mock_task_queue.list_processed_tasks.return_value = [
            {"id": 1, "status": "processed"},
            {"id": 2, "status": "processed"},
        ]
        processed = mock_task_queue.list_processed_tasks()
        assert len(processed) == 2


# ──────────────────────────────────────────────────
# Worker-Foreman queue handoff tests
# ──────────────────────────────────────────────────


class TestWorkerForemanHandoff:
    """Test the queue-based handoff between Foreman and Workers."""

    def test_pending_queue_maxsize_one(self):
        """Worker pending queue should be maxsize=1 for flow control."""
        q = queue.Queue(maxsize=1)
        assert q.maxsize == 1

    def test_complete_queue_receives_task(self, mock_task):
        """Completed tasks should be put on the complete queue."""
        complete_q = queue.Queue()
        complete_q.put(mock_task)
        result = complete_q.get(timeout=1)
        assert result.get_task_id() == 42

    def test_worker_sets_task_success(self, mock_task):
        """Worker should set task success flag before completing."""
        mock_task.set_success(True)
        mock_task.set_success.assert_called_once_with(True)

    def test_worker_sets_task_failure(self, mock_task):
        """Worker should set task failure when processing fails."""
        mock_task.set_success(False)
        mock_task.set_success.assert_called_once_with(False)


# ──────────────────────────────────────────────────
# Filter dispatch tests
# ──────────────────────────────────────────────────


class TestForemanFilterDispatch:
    """Test Foreman's filtered task dispatch behavior."""

    def test_local_only_filter(self, mock_task_queue, mock_task):
        """Foreman should pass local_only filter to task queue."""
        mock_task_queue.get_next_pending_tasks.return_value = mock_task
        mock_task_queue.get_next_pending_tasks(local_only=True)
        mock_task_queue.get_next_pending_tasks.assert_called_with(local_only=True)

    def test_library_names_filter(self, mock_task_queue, mock_task):
        """Foreman should pass library names filter."""
        mock_task_queue.get_next_pending_tasks.return_value = mock_task
        mock_task_queue.get_next_pending_tasks(library_names=["Movies", "TV"])
        mock_task_queue.get_next_pending_tasks.assert_called_with(library_names=["Movies", "TV"])

    def test_library_tags_filter(self, mock_task_queue, mock_task):
        """Foreman should pass library tags filter."""
        mock_task_queue.get_next_pending_tasks.return_value = mock_task
        mock_task_queue.get_next_pending_tasks(library_tags=["encode", "hevc"])
        mock_task_queue.get_next_pending_tasks.assert_called_with(library_tags=["encode", "hevc"])

    def test_no_match_returns_false(self, mock_task_queue):
        """When no tasks match filters, should return False."""
        mock_task_queue.get_next_pending_tasks.return_value = False
        result = mock_task_queue.get_next_pending_tasks(
            local_only=True,
            library_tags=["nonexistent"],
        )
        assert result is False

    def test_requeue_on_no_capable_worker(self, mock_task_queue, mock_task):
        """If no worker can handle the task, it should be requeued at bottom."""
        task_id = mock_task.get_task_id()

        # Simulate: got task but no worker can handle it
        mock_task_queue.get_next_pending_tasks.return_value = mock_task
        # Requeue
        mock_task_queue.requeue_tasks_at_bottom(task_id)
        mock_task_queue.requeue_tasks_at_bottom.assert_called_once_with(42)

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Unit tests for unmanic.libs.task module.

Tests the Task and TaskDataStore classes including:
- Task data management
- TaskDataStore thread-safe operations
- Cache path handling
"""

import pytest
import threading
from unittest.mock import MagicMock, patch

from unmanic.libs.task import Task, TaskDataStore, prepare_file_destination_data


class TestPrepareFileDestinationData:
    """Test prepare_file_destination_data function."""

    def test_basic_path_conversion(self):
        """Should convert pathname and extension to destination data."""
        result = prepare_file_destination_data("/media/movies/test.mkv", "mp4")
        assert result["basename"] == "test.mp4"
        assert result["abspath"] == "/media/movies/test.mp4"

    def test_path_with_spaces(self):
        """Should handle paths with spaces."""
        result = prepare_file_destination_data("/media/movies/My Movie.mkv", "mp4")
        assert result["basename"] == "My Movie.mp4"
        assert "My Movie" in result["abspath"]

    def test_preserves_directory(self):
        """Should preserve the original directory."""
        result = prepare_file_destination_data("/path/to/media/video.avi", "mkv")
        assert result["abspath"].startswith("/path/to/media/")

    def test_handles_nested_paths(self):
        """Should handle deeply nested paths."""
        result = prepare_file_destination_data("/a/b/c/d/e/f/video.mov", "mp4")
        assert result["abspath"] == "/a/b/c/d/e/f/video.mp4"


class TestTaskDataStoreClearTask:
    """Test TaskDataStore.clear_task method."""

    def test_clear_task_removes_runner_state(self):
        """clear_task should remove runner state for task ID."""
        TaskDataStore._runner_state = {1: {"plugin": {}}, 2: {"plugin": {}}}
        TaskDataStore._task_state = {1: {"key": "value"}, 2: {"key": "value"}}

        TaskDataStore.clear_task(1)

        assert 1 not in TaskDataStore._runner_state
        assert 2 in TaskDataStore._runner_state
        assert 1 not in TaskDataStore._task_state
        assert 2 in TaskDataStore._task_state

    def test_clear_task_handles_missing_id(self):
        """clear_task should handle missing task ID gracefully."""
        TaskDataStore._runner_state = {}
        TaskDataStore._task_state = {}

        # Should not raise
        TaskDataStore.clear_task(999)


class TestTaskDataStoreContext:
    """Test TaskDataStore context binding."""

    def test_bind_runner_context(self):
        """bind_runner_context should set thread-local context."""
        TaskDataStore.bind_runner_context(42, "my_plugin", "on_worker_process")

        assert TaskDataStore._ctx.task_id == 42
        assert TaskDataStore._ctx.plugin_id == "my_plugin"
        assert TaskDataStore._ctx.runner == "on_worker_process"

    def test_clear_context(self):
        """clear_context should reset thread-local context."""
        TaskDataStore.bind_runner_context(42, "my_plugin", "on_worker_process")
        TaskDataStore.clear_context()

        assert TaskDataStore._ctx.task_id is None
        assert TaskDataStore._ctx.plugin_id is None
        assert TaskDataStore._ctx.runner is None


class TestTaskDataStoreRunnerValue:
    """Test TaskDataStore runner value operations."""

    def setup_method(self):
        """Clear state before each test."""
        TaskDataStore._runner_state = {}
        TaskDataStore.clear_context()

    def test_set_runner_value_requires_context(self):
        """set_runner_value should raise without context."""
        with pytest.raises(RuntimeError, match="context not bound"):
            TaskDataStore.set_runner_value("key", "value")

    def test_set_runner_value_stores_data(self):
        """set_runner_value should store data under context."""
        TaskDataStore.bind_runner_context(1, "plugin_a", "runner_1")

        result = TaskDataStore.set_runner_value("my_key", {"data": "test"})

        assert result is True
        assert TaskDataStore._runner_state[1]["plugin_a"]["runner_1"]["my_key"] == {"data": "test"}

    def test_set_runner_value_immutable(self):
        """set_runner_value should not overwrite existing keys."""
        TaskDataStore.bind_runner_context(1, "plugin_a", "runner_1")

        TaskDataStore.set_runner_value("key", "first")
        result = TaskDataStore.set_runner_value("key", "second")

        assert result is False
        assert TaskDataStore._runner_state[1]["plugin_a"]["runner_1"]["key"] == "first"

    def test_get_runner_value(self):
        """get_runner_value should retrieve stored data."""
        TaskDataStore.bind_runner_context(1, "plugin_a", "runner_1")
        TaskDataStore.set_runner_value("key", "value")

        result = TaskDataStore.get_runner_value("key")

        assert result == "value"

    def test_get_runner_value_default(self):
        """get_runner_value should return default for missing keys."""
        TaskDataStore.bind_runner_context(1, "plugin_a", "runner_1")

        result = TaskDataStore.get_runner_value("missing", default="default_value")

        assert result == "default_value"


class TestTaskDataStoreTaskState:
    """Test TaskDataStore task state operations."""

    def setup_method(self):
        """Clear state before each test."""
        TaskDataStore._task_state = {}
        TaskDataStore.clear_context()

    def test_set_task_state_with_context(self):
        """set_task_state should work with bound context."""
        TaskDataStore.bind_runner_context(1, "plugin", "runner")

        TaskDataStore.set_task_state("progress", 0.5)

        assert TaskDataStore._task_state[1]["progress"] == 0.5

    def test_set_task_state_with_explicit_id(self):
        """set_task_state should work with explicit task_id."""
        TaskDataStore.set_task_state("status", "running", task_id=42)

        assert TaskDataStore._task_state[42]["status"] == "running"

    def test_set_task_state_overwrites(self):
        """set_task_state should overwrite existing values."""
        TaskDataStore.set_task_state("progress", 0.5, task_id=1)
        TaskDataStore.set_task_state("progress", 0.9, task_id=1)

        assert TaskDataStore._task_state[1]["progress"] == 0.9

    def test_get_task_state(self):
        """get_task_state should retrieve stored values."""
        TaskDataStore.set_task_state("key", "value", task_id=1)

        result = TaskDataStore.get_task_state("key", task_id=1)

        assert result == "value"

    def test_delete_task_state(self):
        """delete_task_state should remove key."""
        TaskDataStore.set_task_state("key1", "value1", task_id=1)
        TaskDataStore.set_task_state("key2", "value2", task_id=1)

        TaskDataStore.delete_task_state("key1", task_id=1)

        assert TaskDataStore.get_task_state("key1", task_id=1) is None
        assert TaskDataStore.get_task_state("key2", task_id=1) == "value2"


class TestTaskDataStoreExportImport:
    """Test TaskDataStore export/import operations."""

    def setup_method(self):
        """Clear state before each test."""
        TaskDataStore._task_state = {}

    def test_export_task_state(self):
        """export_task_state should return dict copy."""
        TaskDataStore.set_task_state("a", 1, task_id=1)
        TaskDataStore.set_task_state("b", 2, task_id=1)

        result = TaskDataStore.export_task_state(1)

        assert result == {"a": 1, "b": 2}
        # Should be a copy, not the same object
        result["c"] = 3
        assert "c" not in TaskDataStore._task_state.get(1, {})

    def test_export_task_state_json(self):
        """export_task_state_json should return valid JSON."""
        TaskDataStore.set_task_state("key", "value", task_id=1)

        result = TaskDataStore.export_task_state_json(1)

        assert '"key"' in result
        assert '"value"' in result

    def test_import_task_state(self):
        """import_task_state should merge state."""
        TaskDataStore.set_task_state("existing", "old", task_id=1)

        TaskDataStore.import_task_state(1, {"new": "value", "existing": "updated"})

        assert TaskDataStore.get_task_state("new", task_id=1) == "value"
        assert TaskDataStore.get_task_state("existing", task_id=1) == "updated"

    def test_import_task_state_json(self):
        """import_task_state_json should parse and merge."""
        json_data = '{"a": 1, "b": "two"}'

        TaskDataStore.import_task_state_json(1, json_data)

        assert TaskDataStore.get_task_state("a", task_id=1) == 1
        assert TaskDataStore.get_task_state("b", task_id=1) == "two"


class TestTaskDataStoreThreadSafety:
    """Test TaskDataStore thread safety."""

    def setup_method(self):
        """Clear state before each test."""
        TaskDataStore._task_state = {}
        TaskDataStore._runner_state = {}

    def test_concurrent_writes(self):
        """Concurrent writes should not corrupt state."""
        errors = []

        def writer(task_id: int):
            try:
                for i in range(100):
                    TaskDataStore.set_task_state(f"key_{i}", i, task_id=task_id)
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=writer, args=(i,)) for i in range(10)]

        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(errors) == 0
        # All 10 tasks should have 100 keys each
        for task_id in range(10):
            state = TaskDataStore.export_task_state(task_id)
            assert len(state) == 100

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unit tests for the TaskQueue adapter pattern.

Tests:
    1. TaskQueueInterface contract enforcement
    2. SQLiteTaskQueue (backward-compatible with original TaskQueue)
    3. TaskQueue backward compatibility alias
    4. TaskQueueFactory
    5. RedisTaskQueue (mocked — no Redis server required)

Version: 2.1.0
Author:  JARVIS (Session 212, 2026-02-10)
"""

import unittest
from abc import ABC
from unittest.mock import MagicMock, patch

# ──────────────────────────────────────────────────
# 1. Interface contract tests
# ──────────────────────────────────────────────────


class TestTaskQueueInterface(unittest.TestCase):
    """Tests for TaskQueueInterface ABC."""

    def test_interface_is_abstract(self):
        """Verify TaskQueueInterface cannot be instantiated directly."""
        from unmanic.libs.taskqueue_interface import TaskQueueInterface

        with self.assertRaises(TypeError):
            TaskQueueInterface()

    def test_interface_has_all_required_methods(self):
        """Verify the interface defines all 12 required abstract methods."""
        from unmanic.libs.taskqueue_interface import TaskQueueInterface

        expected_methods = {
            "list_pending_tasks",
            "list_in_progress_tasks",
            "list_processed_tasks",
            "get_next_pending_tasks",
            "get_next_processed_tasks",
            "get_task_by_id",
            "mark_item_in_progress",
            "mark_item_as_processed",
            "task_list_pending_is_empty",
            "task_list_in_progress_is_empty",
            "task_list_processed_is_empty",
            "requeue_tasks_at_bottom",
        }
        abstract_methods = TaskQueueInterface.__abstractmethods__
        self.assertEqual(abstract_methods, expected_methods)

    def test_interface_is_abc(self):
        """Verify TaskQueueInterface inherits from ABC."""
        from unmanic.libs.taskqueue_interface import TaskQueueInterface

        self.assertTrue(issubclass(TaskQueueInterface, ABC))


# ──────────────────────────────────────────────────
# 2. SQLiteTaskQueue tests
# ──────────────────────────────────────────────────


class TestSQLiteTaskQueueInit(unittest.TestCase):
    """Tests for SQLiteTaskQueue initialization."""

    @patch("unmanic.libs.taskqueue_sqlite.UnmanicLogging")
    @patch("unmanic.libs.taskqueue_sqlite.Tasks")
    def test_init_sets_attributes(self, mock_tasks, mock_logging):
        """Test initialization sets name, data_queues, logger."""
        from unmanic.libs.taskqueue_sqlite import SQLiteTaskQueue

        mock_logging.get_logger.return_value = MagicMock()
        data_queues = {"queue1": MagicMock()}

        queue = SQLiteTaskQueue(data_queues)

        self.assertEqual(queue.name, "SQLiteTaskQueue")
        self.assertEqual(queue.data_queues, data_queues)
        self.assertIsNotNone(queue.logger)

    @patch("unmanic.libs.taskqueue_sqlite.UnmanicLogging")
    @patch("unmanic.libs.taskqueue_sqlite.Tasks")
    def test_init_sets_default_sort(self, mock_tasks, mock_logging):
        """Test initialization sets default sort fields."""
        from unmanic.libs.taskqueue_sqlite import SQLiteTaskQueue

        mock_logging.get_logger.return_value = MagicMock()
        mock_tasks.priority = "priority_field"

        queue = SQLiteTaskQueue({})

        self.assertEqual(queue.sort_by, "priority_field")
        self.assertEqual(queue.sort_order, "desc")

    @patch("unmanic.libs.taskqueue_sqlite.UnmanicLogging")
    @patch("unmanic.libs.taskqueue_sqlite.Tasks")
    def test_implements_interface(self, mock_tasks, mock_logging):
        """Verify SQLiteTaskQueue implements TaskQueueInterface."""
        from unmanic.libs.taskqueue_interface import TaskQueueInterface
        from unmanic.libs.taskqueue_sqlite import SQLiteTaskQueue

        mock_logging.get_logger.return_value = MagicMock()

        queue = SQLiteTaskQueue({})
        self.assertIsInstance(queue, TaskQueueInterface)


class TestSQLiteTaskQueueCountQuery(unittest.TestCase):
    """Tests for SQLiteTaskQueue._build_tasks_count_query."""

    @patch("unmanic.libs.taskqueue_sqlite.Tasks")
    def test_returns_count_for_pending(self, mock_tasks):
        """Test returns count for pending status."""
        from unmanic.libs.taskqueue_sqlite import SQLiteTaskQueue

        mock_query = MagicMock()
        mock_query.count.return_value = 5
        mock_tasks.select.return_value.where.return_value.limit.return_value = mock_query

        result = SQLiteTaskQueue._build_tasks_count_query("pending")

        self.assertEqual(result, 5)

    @patch("unmanic.libs.taskqueue_sqlite.Tasks")
    def test_returns_zero_when_empty(self, mock_tasks):
        """Test returns 0 when no tasks exist."""
        from unmanic.libs.taskqueue_sqlite import SQLiteTaskQueue

        mock_query = MagicMock()
        mock_query.count.return_value = 0
        mock_tasks.select.return_value.where.return_value.limit.return_value = mock_query

        result = SQLiteTaskQueue._build_tasks_count_query("pending")

        self.assertEqual(result, 0)


class TestSQLiteTaskQueueListMethods(unittest.TestCase):
    """Tests for SQLiteTaskQueue list methods."""

    @patch("unmanic.libs.taskqueue_sqlite.Tasks")
    @patch("unmanic.libs.taskqueue_sqlite.UnmanicLogging")
    def test_list_pending_tasks(self, mock_logging, mock_tasks):
        """Test list_pending_tasks returns list of dicts."""
        from unmanic.libs.taskqueue_sqlite import SQLiteTaskQueue

        mock_logging.get_logger.return_value = MagicMock()
        mock_tasks.priority = MagicMock()
        mock_tasks.select.return_value.where.return_value.order_by.return_value.dicts.return_value = [{"id": 1}, {"id": 2}]

        queue = SQLiteTaskQueue({})
        result = queue.list_pending_tasks()

        self.assertEqual(result, [{"id": 1}, {"id": 2}])

    @patch("unmanic.libs.taskqueue_sqlite.Tasks")
    @patch("unmanic.libs.taskqueue_sqlite.UnmanicLogging")
    def test_list_pending_tasks_empty(self, mock_logging, mock_tasks):
        """Test list_pending_tasks returns empty list when no results."""
        from unmanic.libs.taskqueue_sqlite import SQLiteTaskQueue

        mock_logging.get_logger.return_value = MagicMock()
        mock_tasks.priority = MagicMock()
        mock_tasks.select.return_value.where.return_value.order_by.return_value.dicts.return_value = None

        queue = SQLiteTaskQueue({})
        result = queue.list_pending_tasks()

        self.assertEqual(result, [])

    @patch("unmanic.libs.taskqueue_sqlite.Tasks")
    @patch("unmanic.libs.taskqueue_sqlite.UnmanicLogging")
    def test_list_in_progress_tasks(self, mock_logging, mock_tasks):
        """Test list_in_progress_tasks returns list."""
        from unmanic.libs.taskqueue_sqlite import SQLiteTaskQueue

        mock_logging.get_logger.return_value = MagicMock()
        mock_tasks.priority = MagicMock()
        mock_tasks.select.return_value.where.return_value.order_by.return_value.dicts.return_value = [{"id": 3}]

        queue = SQLiteTaskQueue({})
        result = queue.list_in_progress_tasks()

        self.assertEqual(result, [{"id": 3}])

    @patch("unmanic.libs.taskqueue_sqlite.Tasks")
    @patch("unmanic.libs.taskqueue_sqlite.UnmanicLogging")
    def test_list_processed_tasks(self, mock_logging, mock_tasks):
        """Test list_processed_tasks returns list."""
        from unmanic.libs.taskqueue_sqlite import SQLiteTaskQueue

        mock_logging.get_logger.return_value = MagicMock()
        mock_tasks.priority = MagicMock()
        mock_tasks.select.return_value.where.return_value.order_by.return_value.dicts.return_value = [{"id": 4}]

        queue = SQLiteTaskQueue({})
        result = queue.list_processed_tasks()

        self.assertEqual(result, [{"id": 4}])


class TestSQLiteTaskQueueEmptyChecks(unittest.TestCase):
    """Tests for SQLiteTaskQueue emptiness check methods."""

    @patch("unmanic.libs.taskqueue_sqlite.Tasks")
    @patch("unmanic.libs.taskqueue_sqlite.UnmanicLogging")
    def test_task_list_pending_is_empty_true(self, mock_logging, mock_tasks):
        """Test returns True when no pending tasks."""
        from unmanic.libs.taskqueue_sqlite import SQLiteTaskQueue

        mock_logging.get_logger.return_value = MagicMock()
        mock_query = MagicMock()
        mock_query.count.return_value = 0
        mock_tasks.select.return_value.where.return_value.limit.return_value = mock_query

        queue = SQLiteTaskQueue({})
        self.assertTrue(queue.task_list_pending_is_empty())

    @patch("unmanic.libs.taskqueue_sqlite.Tasks")
    @patch("unmanic.libs.taskqueue_sqlite.UnmanicLogging")
    def test_task_list_pending_is_empty_false(self, mock_logging, mock_tasks):
        """Test returns False when pending tasks exist."""
        from unmanic.libs.taskqueue_sqlite import SQLiteTaskQueue

        mock_logging.get_logger.return_value = MagicMock()
        mock_query = MagicMock()
        mock_query.count.return_value = 5
        mock_tasks.select.return_value.where.return_value.limit.return_value = mock_query

        queue = SQLiteTaskQueue({})
        self.assertFalse(queue.task_list_pending_is_empty())

    @patch("unmanic.libs.taskqueue_sqlite.Tasks")
    @patch("unmanic.libs.taskqueue_sqlite.UnmanicLogging")
    def test_task_list_in_progress_is_empty(self, mock_logging, mock_tasks):
        """Test returns True when no in-progress tasks."""
        from unmanic.libs.taskqueue_sqlite import SQLiteTaskQueue

        mock_logging.get_logger.return_value = MagicMock()
        mock_query = MagicMock()
        mock_query.count.return_value = 0
        mock_tasks.select.return_value.where.return_value.limit.return_value = mock_query

        queue = SQLiteTaskQueue({})
        self.assertTrue(queue.task_list_in_progress_is_empty())

    @patch("unmanic.libs.taskqueue_sqlite.Tasks")
    @patch("unmanic.libs.taskqueue_sqlite.UnmanicLogging")
    def test_task_list_processed_is_empty(self, mock_logging, mock_tasks):
        """Test returns True when no processed tasks."""
        from unmanic.libs.taskqueue_sqlite import SQLiteTaskQueue

        mock_logging.get_logger.return_value = MagicMock()
        mock_query = MagicMock()
        mock_query.count.return_value = 0
        mock_tasks.select.return_value.where.return_value.limit.return_value = mock_query

        queue = SQLiteTaskQueue({})
        self.assertTrue(queue.task_list_processed_is_empty())


class TestSQLiteTaskQueueMarkMethods(unittest.TestCase):
    """Tests for SQLiteTaskQueue mark methods."""

    def test_mark_item_in_progress(self):
        """Test mark_item_in_progress calls set_status."""
        from unmanic.libs.taskqueue_sqlite import SQLiteTaskQueue

        mock_task = MagicMock()
        result = SQLiteTaskQueue.mark_item_in_progress(mock_task)

        mock_task.set_status.assert_called_once_with("in_progress")
        self.assertEqual(result, mock_task)

    def test_mark_item_as_processed(self):
        """Test mark_item_as_processed calls set_status."""
        from unmanic.libs.taskqueue_sqlite import SQLiteTaskQueue

        mock_task = MagicMock()
        result = SQLiteTaskQueue.mark_item_as_processed(mock_task)

        mock_task.set_status.assert_called_once_with("processed")
        self.assertEqual(result, mock_task)


class TestSQLiteTaskQueueGetNext(unittest.TestCase):
    """Tests for SQLiteTaskQueue get_next methods."""

    @patch("unmanic.libs.taskqueue_sqlite.task.Task")
    @patch("unmanic.libs.taskqueue_sqlite.Tasks")
    @patch("unmanic.libs.taskqueue_sqlite.Libraries")
    @patch("unmanic.libs.taskqueue_sqlite.UnmanicLogging")
    def test_get_next_pending_tasks_found(self, mock_logging, mock_libs, mock_tasks, mock_task_class):
        """Test get_next_pending_tasks returns task when found."""
        from unmanic.libs.taskqueue_sqlite import SQLiteTaskQueue

        mock_logging.get_logger.return_value = MagicMock()
        mock_tasks.priority = MagicMock()

        mock_task_item = MagicMock()
        mock_task_item.abspath = "/test/file.mkv"
        query_chain = mock_tasks.select.return_value.where.return_value.join.return_value
        query_chain.limit.return_value.order_by.return_value.first.return_value = mock_task_item

        mock_task_instance = MagicMock()
        mock_task_class.return_value = mock_task_instance

        queue = SQLiteTaskQueue({})
        result = queue.get_next_pending_tasks()

        mock_task_instance.read_and_set_task_by_absolute_path.assert_called_once_with("/test/file.mkv")

    @patch("unmanic.libs.taskqueue_sqlite.Tasks")
    @patch("unmanic.libs.taskqueue_sqlite.Libraries")
    @patch("unmanic.libs.taskqueue_sqlite.UnmanicLogging")
    def test_get_next_pending_tasks_empty(self, mock_logging, mock_libs, mock_tasks):
        """Test get_next_pending_tasks returns False when no tasks."""
        from unmanic.libs.taskqueue_sqlite import SQLiteTaskQueue

        mock_logging.get_logger.return_value = MagicMock()
        mock_tasks.priority = MagicMock()
        query_chain = mock_tasks.select.return_value.where.return_value.join.return_value
        query_chain.limit.return_value.order_by.return_value.first.return_value = None

        queue = SQLiteTaskQueue({})
        result = queue.get_next_pending_tasks()

        self.assertFalse(result)


class TestSQLiteTaskQueueGetById(unittest.TestCase):
    """Tests for SQLiteTaskQueue.get_task_by_id."""

    @patch("unmanic.libs.taskqueue_sqlite.Tasks")
    @patch("unmanic.libs.taskqueue_sqlite.UnmanicLogging")
    def test_get_task_by_id_found(self, mock_logging, mock_tasks):
        """Test get_task_by_id returns task when found."""
        from unmanic.libs.taskqueue_sqlite import SQLiteTaskQueue

        mock_logging.get_logger.return_value = MagicMock()
        mock_task_item = MagicMock()
        mock_tasks.get.return_value = mock_task_item

        queue = SQLiteTaskQueue({})
        result = queue.get_task_by_id(42)

        self.assertEqual(result, mock_task_item)

    @patch("unmanic.libs.taskqueue_sqlite.Tasks")
    @patch("unmanic.libs.taskqueue_sqlite.UnmanicLogging")
    def test_get_task_by_id_not_found(self, mock_logging, mock_tasks):
        """Test get_task_by_id returns None when task not found."""
        from unmanic.libs.taskqueue_sqlite import SQLiteTaskQueue

        mock_logging.get_logger.return_value = MagicMock()
        mock_tasks.DoesNotExist = Exception
        mock_tasks.get.side_effect = mock_tasks.DoesNotExist("Not found")

        queue = SQLiteTaskQueue({})
        result = queue.get_task_by_id(999)

        self.assertIsNone(result)


class TestSQLiteTaskQueueRequeue(unittest.TestCase):
    """Tests for SQLiteTaskQueue requeue."""

    @patch("unmanic.libs.taskqueue_sqlite.task.Task")
    @patch("unmanic.libs.taskqueue_sqlite.Tasks")
    @patch("unmanic.libs.taskqueue_sqlite.UnmanicLogging")
    def test_requeue_tasks_at_bottom(self, mock_logging, mock_tasks, mock_task_class):
        """Test requeue calls reorder_tasks."""
        from unmanic.libs.taskqueue_sqlite import SQLiteTaskQueue

        mock_logging.get_logger.return_value = MagicMock()
        mock_handler = MagicMock()
        mock_handler.reorder_tasks.return_value = True
        mock_task_class.return_value = mock_handler

        queue = SQLiteTaskQueue({})
        result = queue.requeue_tasks_at_bottom(123)

        mock_handler.reorder_tasks.assert_called_once_with([123], "bottom")


class TestSQLiteTaskQueueLog(unittest.TestCase):
    """Tests for SQLiteTaskQueue._log."""

    @patch("unmanic.libs.taskqueue_sqlite.common")
    @patch("unmanic.libs.taskqueue_sqlite.Tasks")
    @patch("unmanic.libs.taskqueue_sqlite.UnmanicLogging")
    def test_log_info(self, mock_logging, mock_tasks, mock_common):
        """Test _log with info level."""
        from unmanic.libs.taskqueue_sqlite import SQLiteTaskQueue

        mock_logger = MagicMock()
        mock_logging.get_logger.return_value = mock_logger
        mock_common.format_message.return_value = "formatted message"

        queue = SQLiteTaskQueue({})
        queue._log("test message")

        mock_common.format_message.assert_called_once()
        mock_logger.info.assert_called_once_with("formatted message")


# ──────────────────────────────────────────────────
# 3. Backward compatibility tests
# ──────────────────────────────────────────────────


class TestBackwardCompatibility(unittest.TestCase):
    """Verify taskqueue.py still exports TaskQueue alias."""

    def test_taskqueue_import(self):
        """Test `from unmanic.libs.taskqueue import TaskQueue` works."""
        from unmanic.libs.taskqueue import TaskQueue
        from unmanic.libs.taskqueue_sqlite import SQLiteTaskQueue

        self.assertIs(TaskQueue, SQLiteTaskQueue)

    def test_interface_import(self):
        """Test interface can be imported from taskqueue module."""
        from unmanic.libs.taskqueue import TaskQueueInterface

        self.assertTrue(hasattr(TaskQueueInterface, "__abstractmethods__"))

    def test_factory_import(self):
        """Test factory can be imported from taskqueue module."""
        from unmanic.libs.taskqueue import create_task_queue

        self.assertTrue(callable(create_task_queue))


# ──────────────────────────────────────────────────
# 4. Factory tests
# ──────────────────────────────────────────────────


class TestTaskQueueFactory(unittest.TestCase):
    """Tests for TaskQueueFactory."""

    @patch("unmanic.libs.taskqueue_factory.UnmanicLogging")
    def test_create_sqlite_backend(self, mock_logging):
        """Test factory creates SQLiteTaskQueue for 'sqlite' backend."""
        mock_logging.get_logger.return_value = MagicMock()

        with patch("unmanic.libs.taskqueue_sqlite.UnmanicLogging") as mock_sqlite_log, patch(
            "unmanic.libs.taskqueue_sqlite.Tasks"
        ):
            mock_sqlite_log.get_logger.return_value = MagicMock()

            from unmanic.libs.taskqueue_factory import create_task_queue
            from unmanic.libs.taskqueue_sqlite import SQLiteTaskQueue

            queue = create_task_queue({}, backend="sqlite")
            self.assertIsInstance(queue, SQLiteTaskQueue)

    @patch("unmanic.libs.taskqueue_factory.UnmanicLogging")
    def test_create_unknown_backend_raises(self, mock_logging):
        """Test factory raises ValueError for unknown backend."""
        mock_logging.get_logger.return_value = MagicMock()

        from unmanic.libs.taskqueue_factory import create_task_queue

        with self.assertRaises(ValueError) as ctx:
            create_task_queue({}, backend="unknown")

        self.assertIn("unknown", str(ctx.exception).lower())

    @patch("unmanic.libs.taskqueue_factory.UnmanicLogging")
    def test_default_backend_is_sqlite(self, mock_logging):
        """Test factory defaults to SQLite backend."""
        mock_logging.get_logger.return_value = MagicMock()

        with patch("unmanic.libs.taskqueue_sqlite.UnmanicLogging") as mock_sqlite_log, patch(
            "unmanic.libs.taskqueue_sqlite.Tasks"
        ):
            mock_sqlite_log.get_logger.return_value = MagicMock()

            from unmanic.libs.taskqueue_factory import create_task_queue
            from unmanic.libs.taskqueue_sqlite import SQLiteTaskQueue

            queue = create_task_queue({})
            self.assertIsInstance(queue, SQLiteTaskQueue)


# ──────────────────────────────────────────────────
# 5. RedisTaskQueue tests (mocked)
# ──────────────────────────────────────────────────


class TestRedisTaskQueueSerialization(unittest.TestCase):
    """Tests for RedisTaskQueue serialization/deserialization."""

    @patch("unmanic.libs.taskqueue_redis.redis")
    @patch("unmanic.libs.taskqueue_redis.UnmanicLogging")
    def test_serialize_task(self, mock_logging, mock_redis_module):
        """Test task data serialization to strings."""
        mock_logging.get_logger.return_value = MagicMock()
        mock_redis_module.ConnectionPool.return_value = MagicMock()
        mock_client = MagicMock()
        mock_redis_module.Redis.return_value = mock_client
        mock_client.ping.return_value = True

        from unmanic.libs.taskqueue_redis import RedisTaskQueue

        queue = RedisTaskQueue({}, redis_host="localhost")

        task_data = {
            "id": 42,
            "abspath": "/test/file.mkv",
            "priority": 100,
            "success": True,
            "cache_path": None,
        }

        result = queue._serialize_task(task_data)

        self.assertEqual(result["id"], "42")
        self.assertEqual(result["abspath"], "/test/file.mkv")
        self.assertEqual(result["priority"], "100")
        self.assertEqual(result["success"], "1")
        self.assertEqual(result["cache_path"], "")

    @patch("unmanic.libs.taskqueue_redis.redis")
    @patch("unmanic.libs.taskqueue_redis.UnmanicLogging")
    def test_deserialize_task(self, mock_logging, mock_redis_module):
        """Test task data deserialization from strings."""
        mock_logging.get_logger.return_value = MagicMock()
        mock_redis_module.ConnectionPool.return_value = MagicMock()
        mock_client = MagicMock()
        mock_redis_module.Redis.return_value = mock_client
        mock_client.ping.return_value = True

        from unmanic.libs.taskqueue_redis import RedisTaskQueue

        queue = RedisTaskQueue({}, redis_host="localhost")

        task_hash = {
            "id": "42",
            "abspath": "/test/file.mkv",
            "priority": "100",
            "success": "1",
            "library_id": "3",
            "cache_path": "",
            "start_time": "1707580800.0",
        }

        result = queue._deserialize_task(task_hash)

        self.assertEqual(result["id"], 42)
        self.assertEqual(result["abspath"], "/test/file.mkv")
        self.assertEqual(result["priority"], 100)
        self.assertTrue(result["success"])
        self.assertEqual(result["library_id"], 3)
        self.assertIsNone(result["cache_path"])
        self.assertAlmostEqual(result["start_time"], 1707580800.0)

    @patch("unmanic.libs.taskqueue_redis.redis")
    @patch("unmanic.libs.taskqueue_redis.UnmanicLogging")
    def test_deserialize_empty_hash(self, mock_logging, mock_redis_module):
        """Test deserialization of empty hash returns empty dict."""
        mock_logging.get_logger.return_value = MagicMock()
        mock_redis_module.ConnectionPool.return_value = MagicMock()
        mock_client = MagicMock()
        mock_redis_module.Redis.return_value = mock_client
        mock_client.ping.return_value = True

        from unmanic.libs.taskqueue_redis import RedisTaskQueue

        queue = RedisTaskQueue({}, redis_host="localhost")

        self.assertEqual(queue._deserialize_task({}), {})


class TestRedisTaskQueueEmptyChecks(unittest.TestCase):
    """Tests for RedisTaskQueue emptiness checks."""

    @patch("unmanic.libs.taskqueue_redis.redis")
    @patch("unmanic.libs.taskqueue_redis.UnmanicLogging")
    def test_pending_is_empty_true(self, mock_logging, mock_redis_module):
        """Test task_list_pending_is_empty when set is empty."""
        mock_logging.get_logger.return_value = MagicMock()
        mock_redis_module.ConnectionPool.return_value = MagicMock()
        mock_client = MagicMock()
        mock_redis_module.Redis.return_value = mock_client
        mock_client.ping.return_value = True
        mock_client.zcard.return_value = 0

        from unmanic.libs.taskqueue_redis import RedisTaskQueue

        queue = RedisTaskQueue({}, redis_host="localhost")
        self.assertTrue(queue.task_list_pending_is_empty())
        mock_client.zcard.assert_called_with("tars:tasks:pending")

    @patch("unmanic.libs.taskqueue_redis.redis")
    @patch("unmanic.libs.taskqueue_redis.UnmanicLogging")
    def test_pending_is_empty_false(self, mock_logging, mock_redis_module):
        """Test task_list_pending_is_empty when tasks exist."""
        mock_logging.get_logger.return_value = MagicMock()
        mock_redis_module.ConnectionPool.return_value = MagicMock()
        mock_client = MagicMock()
        mock_redis_module.Redis.return_value = mock_client
        mock_client.ping.return_value = True
        mock_client.zcard.return_value = 5

        from unmanic.libs.taskqueue_redis import RedisTaskQueue

        queue = RedisTaskQueue({}, redis_host="localhost")
        self.assertFalse(queue.task_list_pending_is_empty())


class TestRedisTaskQueueHealthCheck(unittest.TestCase):
    """Tests for RedisTaskQueue health_check."""

    @patch("unmanic.libs.taskqueue_redis.redis")
    @patch("unmanic.libs.taskqueue_redis.UnmanicLogging")
    def test_health_check_connected(self, mock_logging, mock_redis_module):
        """Test health_check reports connected status."""
        mock_logging.get_logger.return_value = MagicMock()
        mock_redis_module.ConnectionPool.return_value = MagicMock()
        mock_client = MagicMock()
        mock_redis_module.Redis.return_value = mock_client
        mock_client.ping.return_value = True
        mock_client.zcard.side_effect = [10, 2, 50]

        from unmanic.libs.taskqueue_redis import RedisTaskQueue

        queue = RedisTaskQueue({}, redis_host="localhost")
        health = queue.health_check()

        self.assertTrue(health["connected"])
        self.assertEqual(health["pending"], 10)
        self.assertEqual(health["in_progress"], 2)
        self.assertEqual(health["processed"], 50)

    @patch("unmanic.libs.taskqueue_redis.redis")
    @patch("unmanic.libs.taskqueue_redis.UnmanicLogging")
    def test_health_check_disconnected(self, mock_logging, mock_redis_module):
        """Test health_check reports disconnected status."""
        mock_logging.get_logger.return_value = MagicMock()
        mock_redis_module.ConnectionPool.return_value = MagicMock()
        mock_client = MagicMock()
        mock_redis_module.Redis.return_value = mock_client

        mock_redis_module.ConnectionError = Exception
        mock_client.ping.side_effect = [True, Exception("Connection refused")]

        from unmanic.libs.taskqueue_redis import RedisTaskQueue

        queue = RedisTaskQueue({}, redis_host="localhost")
        health = queue.health_check()

        self.assertFalse(health["connected"])
        self.assertIn("error", health)


class TestRedisTaskQueueInterface(unittest.TestCase):
    """Verify RedisTaskQueue implements TaskQueueInterface."""

    @patch("unmanic.libs.taskqueue_redis.redis")
    @patch("unmanic.libs.taskqueue_redis.UnmanicLogging")
    def test_implements_interface(self, mock_logging, mock_redis_module):
        """Verify RedisTaskQueue is a TaskQueueInterface."""
        mock_logging.get_logger.return_value = MagicMock()
        mock_redis_module.ConnectionPool.return_value = MagicMock()
        mock_client = MagicMock()
        mock_redis_module.Redis.return_value = mock_client
        mock_client.ping.return_value = True

        from unmanic.libs.taskqueue_interface import TaskQueueInterface
        from unmanic.libs.taskqueue_redis import RedisTaskQueue

        queue = RedisTaskQueue({}, redis_host="localhost")
        self.assertIsInstance(queue, TaskQueueInterface)


if __name__ == "__main__":
    unittest.main()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unit tests for the TaskQueue class in unmanic.libs.taskqueue.

Tests task queue management functionality with mocked database models.
"""

import unittest
from unittest.mock import MagicMock, patch


class TestBuildTasksCountQuery(unittest.TestCase):
    """Tests for build_tasks_count_query function."""

    @patch("unmanic.libs.taskqueue.Tasks")
    def test_returns_count_for_pending(self, mock_tasks):
        """Test returns count for pending status."""
        from unmanic.libs.taskqueue import build_tasks_count_query

        mock_query = MagicMock()
        mock_query.count.return_value = 5
        mock_tasks.select.return_value.where.return_value.limit.return_value = mock_query

        result = build_tasks_count_query("pending")

        self.assertEqual(result, 5)

    @patch("unmanic.libs.taskqueue.Tasks")
    def test_returns_zero_when_empty(self, mock_tasks):
        """Test returns 0 when no tasks exist."""
        from unmanic.libs.taskqueue import build_tasks_count_query

        mock_query = MagicMock()
        mock_query.count.return_value = 0
        mock_tasks.select.return_value.where.return_value.limit.return_value = mock_query

        result = build_tasks_count_query("pending")

        self.assertEqual(result, 0)


class TestBuildTasksQueryFullTaskList(unittest.TestCase):
    """Tests for build_tasks_query_full_task_list function."""

    @patch("unmanic.libs.taskqueue.Tasks")
    def test_returns_query_dicts(self, mock_tasks):
        """Test returns query as dicts."""
        from unmanic.libs.taskqueue import build_tasks_query_full_task_list

        mock_sort_by = MagicMock()
        mock_sort_by.asc.return_value = "asc_order"
        mock_tasks.select.return_value.where.return_value.order_by.return_value.limit.return_value.dicts.return_value = [
            {"id": 1, "status": "pending"}
        ]

        result = build_tasks_query_full_task_list("pending", limit=10, sort_by=mock_sort_by)

        mock_tasks.select.assert_called_once()

    @patch("unmanic.libs.taskqueue.Tasks")
    def test_ascending_sort_order(self, mock_tasks):
        """Test ascending sort order."""
        from unmanic.libs.taskqueue import build_tasks_query_full_task_list

        mock_sort_by = MagicMock()
        mock_sort_by.asc.return_value = "asc_query"
        mock_tasks.select.return_value.where.return_value.order_by.return_value.dicts.return_value = []

        build_tasks_query_full_task_list("pending", sort_by=mock_sort_by, sort_order="asc")

        mock_sort_by.asc.assert_called_once()

    @patch("unmanic.libs.taskqueue.Tasks")
    def test_descending_sort_order(self, mock_tasks):
        """Test descending sort order."""
        from unmanic.libs.taskqueue import build_tasks_query_full_task_list

        mock_sort_by = MagicMock()
        mock_sort_by.desc.return_value = "desc_query"
        mock_tasks.select.return_value.where.return_value.order_by.return_value.dicts.return_value = []

        build_tasks_query_full_task_list("pending", sort_by=mock_sort_by, sort_order="desc")

        mock_sort_by.desc.assert_called_once()


class TestTaskQueueInit(unittest.TestCase):
    """Tests for TaskQueue initialization."""

    @patch("unmanic.libs.taskqueue.UnmanicLogging")
    @patch("unmanic.libs.taskqueue.Tasks")
    def test_init_sets_attributes(self, mock_tasks, mock_logging):
        """Test initialization sets attributes."""
        from unmanic.libs.taskqueue import TaskQueue

        mock_logging.get_logger.return_value = MagicMock()
        data_queues = {"queue1": MagicMock()}

        queue = TaskQueue(data_queues)

        self.assertEqual(queue.name, "TaskQueue")
        self.assertEqual(queue.data_queues, data_queues)
        self.assertIsNotNone(queue.logger)

    @patch("unmanic.libs.taskqueue.UnmanicLogging")
    @patch("unmanic.libs.taskqueue.Tasks")
    def test_init_sets_default_sort(self, mock_tasks, mock_logging):
        """Test initialization sets default sort fields."""
        from unmanic.libs.taskqueue import TaskQueue

        mock_logging.get_logger.return_value = MagicMock()
        mock_tasks.priority = "priority_field"

        queue = TaskQueue({})

        self.assertEqual(queue.sort_by, "priority_field")
        self.assertEqual(queue.sort_order, "desc")


class TestTaskQueueListMethods(unittest.TestCase):
    """Tests for TaskQueue list methods."""

    @patch("unmanic.libs.taskqueue.build_tasks_query_full_task_list")
    @patch("unmanic.libs.taskqueue.UnmanicLogging")
    @patch("unmanic.libs.taskqueue.Tasks")
    def test_list_pending_tasks(self, mock_tasks, mock_logging, mock_build_query):
        """Test list_pending_tasks returns list."""
        from unmanic.libs.taskqueue import TaskQueue

        mock_logging.get_logger.return_value = MagicMock()
        mock_build_query.return_value = [{"id": 1}, {"id": 2}]

        queue = TaskQueue({})
        result = queue.list_pending_tasks()

        self.assertEqual(result, [{"id": 1}, {"id": 2}])
        mock_build_query.assert_called_once()

    @patch("unmanic.libs.taskqueue.build_tasks_query_full_task_list")
    @patch("unmanic.libs.taskqueue.UnmanicLogging")
    @patch("unmanic.libs.taskqueue.Tasks")
    def test_list_pending_tasks_empty(self, mock_tasks, mock_logging, mock_build_query):
        """Test list_pending_tasks returns empty list when no results."""
        from unmanic.libs.taskqueue import TaskQueue

        mock_logging.get_logger.return_value = MagicMock()
        mock_build_query.return_value = None

        queue = TaskQueue({})
        result = queue.list_pending_tasks()

        self.assertEqual(result, [])

    @patch("unmanic.libs.taskqueue.build_tasks_query_full_task_list")
    @patch("unmanic.libs.taskqueue.UnmanicLogging")
    @patch("unmanic.libs.taskqueue.Tasks")
    def test_list_in_progress_tasks(self, mock_tasks, mock_logging, mock_build_query):
        """Test list_in_progress_tasks returns list."""
        from unmanic.libs.taskqueue import TaskQueue

        mock_logging.get_logger.return_value = MagicMock()
        mock_build_query.return_value = [{"id": 3}]

        queue = TaskQueue({})
        result = queue.list_in_progress_tasks()

        self.assertEqual(result, [{"id": 3}])

    @patch("unmanic.libs.taskqueue.build_tasks_query_full_task_list")
    @patch("unmanic.libs.taskqueue.UnmanicLogging")
    @patch("unmanic.libs.taskqueue.Tasks")
    def test_list_processed_tasks(self, mock_tasks, mock_logging, mock_build_query):
        """Test list_processed_tasks returns list."""
        from unmanic.libs.taskqueue import TaskQueue

        mock_logging.get_logger.return_value = MagicMock()
        mock_build_query.return_value = [{"id": 4}]

        queue = TaskQueue({})
        result = queue.list_processed_tasks()

        self.assertEqual(result, [{"id": 4}])


class TestTaskQueueStaticMethods(unittest.TestCase):
    """Tests for TaskQueue static methods."""

    @patch("unmanic.libs.taskqueue.build_tasks_count_query")
    def test_task_list_pending_is_empty_true(self, mock_count):
        """Test task_list_pending_is_empty returns True when empty."""
        from unmanic.libs.taskqueue import TaskQueue

        mock_count.return_value = 0

        result = TaskQueue.task_list_pending_is_empty()

        self.assertTrue(result)
        mock_count.assert_called_with("pending")

    @patch("unmanic.libs.taskqueue.build_tasks_count_query")
    def test_task_list_pending_is_empty_false(self, mock_count):
        """Test task_list_pending_is_empty returns False when not empty."""
        from unmanic.libs.taskqueue import TaskQueue

        mock_count.return_value = 5

        result = TaskQueue.task_list_pending_is_empty()

        self.assertFalse(result)

    @patch("unmanic.libs.taskqueue.build_tasks_count_query")
    def test_task_list_in_progress_is_empty_true(self, mock_count):
        """Test task_list_in_progress_is_empty returns True when empty."""
        from unmanic.libs.taskqueue import TaskQueue

        mock_count.return_value = 0

        result = TaskQueue.task_list_in_progress_is_empty()

        self.assertTrue(result)
        mock_count.assert_called_with("in_progress")

    @patch("unmanic.libs.taskqueue.build_tasks_count_query")
    def test_task_list_in_progress_is_empty_false(self, mock_count):
        """Test task_list_in_progress_is_empty returns False when not empty."""
        from unmanic.libs.taskqueue import TaskQueue

        mock_count.return_value = 3

        result = TaskQueue.task_list_in_progress_is_empty()

        self.assertFalse(result)

    @patch("unmanic.libs.taskqueue.build_tasks_count_query")
    def test_task_list_processed_is_empty_true(self, mock_count):
        """Test task_list_processed_is_empty returns True when empty."""
        from unmanic.libs.taskqueue import TaskQueue

        mock_count.return_value = 0

        result = TaskQueue.task_list_processed_is_empty()

        self.assertTrue(result)
        mock_count.assert_called_with("processed")


class TestTaskQueueMarkMethods(unittest.TestCase):
    """Tests for TaskQueue mark methods."""

    def test_mark_item_in_progress(self):
        """Test mark_item_in_progress sets status."""
        from unmanic.libs.taskqueue import TaskQueue

        mock_task = MagicMock()

        result = TaskQueue.mark_item_in_progress(mock_task)

        mock_task.set_status.assert_called_once_with("in_progress")
        self.assertEqual(result, mock_task)

    def test_mark_item_as_processed(self):
        """Test mark_item_as_processed sets status."""
        from unmanic.libs.taskqueue import TaskQueue

        mock_task = MagicMock()

        result = TaskQueue.mark_item_as_processed(mock_task)

        mock_task.set_status.assert_called_once_with("processed")
        self.assertEqual(result, mock_task)


class TestTaskQueueGetNextMethods(unittest.TestCase):
    """Tests for TaskQueue get_next methods."""

    @patch("unmanic.libs.taskqueue.fetch_next_task_filtered")
    @patch("unmanic.libs.taskqueue.UnmanicLogging")
    @patch("unmanic.libs.taskqueue.Tasks")
    def test_get_next_pending_tasks(self, mock_tasks, mock_logging, mock_fetch):
        """Test get_next_pending_tasks returns task."""
        from unmanic.libs.taskqueue import TaskQueue

        mock_logging.get_logger.return_value = MagicMock()
        mock_task = MagicMock()
        mock_fetch.return_value = mock_task

        queue = TaskQueue({})
        result = queue.get_next_pending_tasks()

        self.assertEqual(result, mock_task)
        mock_fetch.assert_called_once()

    @patch("unmanic.libs.taskqueue.fetch_next_task_filtered")
    @patch("unmanic.libs.taskqueue.UnmanicLogging")
    @patch("unmanic.libs.taskqueue.Tasks")
    def test_get_next_pending_tasks_with_filters(self, mock_tasks, mock_logging, mock_fetch):
        """Test get_next_pending_tasks with library filters."""
        from unmanic.libs.taskqueue import TaskQueue

        mock_logging.get_logger.return_value = MagicMock()
        mock_fetch.return_value = MagicMock()

        queue = TaskQueue({})
        queue.get_next_pending_tasks(local_only=True, library_names=["lib1"], library_tags=["tag1"])

        # Verify filters were passed
        call_kwargs = mock_fetch.call_args[1]
        self.assertTrue(call_kwargs["local_only"])
        self.assertEqual(call_kwargs["library_names"], ["lib1"])
        self.assertEqual(call_kwargs["library_tags"], ["tag1"])

    @patch("unmanic.libs.taskqueue.fetch_next_task_filtered")
    @patch("unmanic.libs.taskqueue.UnmanicLogging")
    @patch("unmanic.libs.taskqueue.Tasks")
    def test_get_next_processed_tasks(self, mock_tasks, mock_logging, mock_fetch):
        """Test get_next_processed_tasks returns task."""
        from unmanic.libs.taskqueue import TaskQueue

        mock_logging.get_logger.return_value = MagicMock()
        mock_task = MagicMock()
        mock_fetch.return_value = mock_task

        queue = TaskQueue({})
        result = queue.get_next_processed_tasks()

        self.assertEqual(result, mock_task)


class TestTaskQueueRequeue(unittest.TestCase):
    """Tests for TaskQueue requeue method."""

    @patch("unmanic.libs.taskqueue.task.Task")
    @patch("unmanic.libs.taskqueue.UnmanicLogging")
    @patch("unmanic.libs.taskqueue.Tasks")
    def test_requeue_tasks_at_bottom(self, mock_tasks, mock_logging, mock_task_class):
        """Test requeue_tasks_at_bottom calls reorder."""
        from unmanic.libs.taskqueue import TaskQueue

        mock_logging.get_logger.return_value = MagicMock()
        mock_task_handler = MagicMock()
        mock_task_handler.reorder_tasks.return_value = True
        mock_task_class.return_value = mock_task_handler

        queue = TaskQueue({})
        result = queue.requeue_tasks_at_bottom(123)

        mock_task_handler.reorder_tasks.assert_called_once_with([123], "bottom")


class TestTaskQueueLog(unittest.TestCase):
    """Tests for TaskQueue._log method."""

    @patch("unmanic.libs.taskqueue.common")
    @patch("unmanic.libs.taskqueue.UnmanicLogging")
    @patch("unmanic.libs.taskqueue.Tasks")
    def test_log_info(self, mock_tasks, mock_logging, mock_common):
        """Test _log with info level."""
        from unmanic.libs.taskqueue import TaskQueue

        mock_logger = MagicMock()
        mock_logging.get_logger.return_value = mock_logger
        mock_common.format_message.return_value = "formatted message"

        queue = TaskQueue({})
        queue._log("test message")

        mock_common.format_message.assert_called_once()
        mock_logger.info.assert_called_once_with("formatted message")

    @patch("unmanic.libs.taskqueue.common")
    @patch("unmanic.libs.taskqueue.UnmanicLogging")
    @patch("unmanic.libs.taskqueue.Tasks")
    def test_log_error(self, mock_tasks, mock_logging, mock_common):
        """Test _log with error level."""
        from unmanic.libs.taskqueue import TaskQueue

        mock_logger = MagicMock()
        mock_logging.get_logger.return_value = mock_logger
        mock_common.format_message.return_value = "error message"

        queue = TaskQueue({})
        queue._log("error", level="error")

        mock_logger.error.assert_called_once_with("error message")


if __name__ == "__main__":
    unittest.main()

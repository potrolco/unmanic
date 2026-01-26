#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unit tests for the History class in unmanic.libs.history.

Tests historical task recording and retrieval functionality.
"""

import unittest
from unittest.mock import MagicMock, patch


class TestHistoryInit(unittest.TestCase):
    """Tests for History initialization."""

    @patch("unmanic.libs.history.UnmanicLogging")
    @patch("unmanic.libs.history.config.Config")
    def test_init_sets_attributes(self, mock_config, mock_logging):
        """Test that initialization sets name, settings, and logger."""
        from unmanic.libs.history import History

        mock_logger = MagicMock()
        mock_logging.get_logger.return_value = mock_logger

        history = History()

        self.assertEqual(history.name, "History")
        mock_config.assert_called_once()
        mock_logging.get_logger.assert_called_once_with(name="History")
        self.assertEqual(history.logger, mock_logger)


class TestGetHistoricTaskList(unittest.TestCase):
    """Tests for History.get_historic_task_list method."""

    @patch("unmanic.libs.history.CompletedTasks")
    @patch("unmanic.libs.history.UnmanicLogging")
    @patch("unmanic.libs.history.config.Config")
    def test_returns_all_tasks_without_limit(self, mock_config, mock_logging, mock_completed_tasks):
        """Test get_historic_task_list returns all tasks when no limit."""
        from unmanic.libs.history import History

        mock_query = MagicMock()
        mock_query.order_by.return_value = mock_query
        mock_query.dicts.return_value = [{"id": 1}, {"id": 2}]
        mock_completed_tasks.select.return_value = mock_query

        history = History()
        result = history.get_historic_task_list()

        mock_completed_tasks.select.assert_called_once()
        mock_query.order_by.assert_called_once()
        self.assertEqual(len(result), 2)

    @patch("unmanic.libs.history.CompletedTasks")
    @patch("unmanic.libs.history.UnmanicLogging")
    @patch("unmanic.libs.history.config.Config")
    def test_returns_limited_tasks(self, mock_config, mock_logging, mock_completed_tasks):
        """Test get_historic_task_list respects limit parameter."""
        from unmanic.libs.history import History

        mock_query = MagicMock()
        mock_query.order_by.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.dicts.return_value = [{"id": 1}]
        mock_completed_tasks.select.return_value = mock_query

        history = History()
        result = history.get_historic_task_list(limit=1)

        mock_query.limit.assert_called_once_with(1)


class TestGetTotalHistoricTaskListCount(unittest.TestCase):
    """Tests for History.get_total_historic_task_list_count method."""

    @patch("unmanic.libs.history.CompletedTasks")
    @patch("unmanic.libs.history.UnmanicLogging")
    @patch("unmanic.libs.history.config.Config")
    def test_returns_count(self, mock_config, mock_logging, mock_completed_tasks):
        """Test get_total_historic_task_list_count returns count."""
        from unmanic.libs.history import History

        mock_query = MagicMock()
        mock_query.order_by.return_value = mock_query
        mock_query.count.return_value = 42
        mock_completed_tasks.select.return_value = mock_query

        history = History()
        result = history.get_total_historic_task_list_count()

        self.assertEqual(result, 42)


class TestGetHistoricTaskListFilteredAndSorted(unittest.TestCase):
    """Tests for History.get_historic_task_list_filtered_and_sorted method."""

    @patch("unmanic.libs.history.CompletedTasks")
    @patch("unmanic.libs.history.UnmanicLogging")
    @patch("unmanic.libs.history.config.Config")
    def test_returns_all_without_filters(self, mock_config, mock_logging, mock_completed_tasks):
        """Test returns all tasks when no filters applied."""
        from unmanic.libs.history import History

        mock_query = MagicMock()
        mock_query.dicts.return_value = [{"id": 1}]
        mock_completed_tasks.select.return_value = mock_query

        history = History()
        result = history.get_historic_task_list_filtered_and_sorted()

        self.assertEqual(len(result), 1)

    @patch("unmanic.libs.history.CompletedTasks")
    @patch("unmanic.libs.history.UnmanicLogging")
    @patch("unmanic.libs.history.config.Config")
    def test_filters_by_id_list(self, mock_config, mock_logging, mock_completed_tasks):
        """Test filters by id_list."""
        from unmanic.libs.history import History

        mock_query = MagicMock()
        mock_query.where.return_value = mock_query
        mock_query.dicts.return_value = [{"id": 1}]
        mock_completed_tasks.select.return_value = mock_query

        history = History()
        result = history.get_historic_task_list_filtered_and_sorted(id_list=[1, 2])

        mock_query.where.assert_called()

    @patch("unmanic.libs.history.CompletedTasks")
    @patch("unmanic.libs.history.UnmanicLogging")
    @patch("unmanic.libs.history.config.Config")
    def test_filters_by_search_value(self, mock_config, mock_logging, mock_completed_tasks):
        """Test filters by search_value."""
        from unmanic.libs.history import History

        mock_query = MagicMock()
        mock_query.where.return_value = mock_query
        mock_query.dicts.return_value = []
        mock_completed_tasks.select.return_value = mock_query

        history = History()
        result = history.get_historic_task_list_filtered_and_sorted(search_value="test")

        mock_query.where.assert_called()

    @patch("unmanic.libs.history.CompletedTasks")
    @patch("unmanic.libs.history.UnmanicLogging")
    @patch("unmanic.libs.history.config.Config")
    def test_filters_by_task_success(self, mock_config, mock_logging, mock_completed_tasks):
        """Test filters by task_success."""
        from unmanic.libs.history import History

        mock_query = MagicMock()
        mock_query.where.return_value = mock_query
        mock_query.dicts.return_value = []
        mock_completed_tasks.select.return_value = mock_query

        history = History()
        result = history.get_historic_task_list_filtered_and_sorted(task_success=True)

        mock_query.where.assert_called()

    @patch("unmanic.libs.history.CompletedTasks")
    @patch("unmanic.libs.history.UnmanicLogging")
    @patch("unmanic.libs.history.config.Config")
    def test_filters_by_time_range(self, mock_config, mock_logging, mock_completed_tasks):
        """Test filters by after_time and before_time."""
        from unmanic.libs.history import History

        mock_query = MagicMock()
        mock_query.where.return_value = mock_query
        mock_query.dicts.return_value = []
        mock_completed_tasks.select.return_value = mock_query

        # Mock the finish_time attribute to support comparison operators
        mock_finish_time = MagicMock()
        mock_finish_time.__ge__ = MagicMock(return_value=MagicMock())
        mock_finish_time.__le__ = MagicMock(return_value=MagicMock())
        mock_completed_tasks.finish_time = mock_finish_time

        history = History()
        result = history.get_historic_task_list_filtered_and_sorted(after_time=1000, before_time=2000)

        # where should be called twice for time filters
        self.assertEqual(mock_query.where.call_count, 2)

    @patch("unmanic.libs.history.CompletedTasks")
    @patch("unmanic.libs.history.UnmanicLogging")
    @patch("unmanic.libs.history.config.Config")
    def test_order_ascending(self, mock_config, mock_logging, mock_completed_tasks):
        """Test ordering ascending."""
        from unmanic.libs.history import History

        mock_query = MagicMock()
        mock_query.order_by.return_value = mock_query
        mock_query.dicts.return_value = []
        mock_completed_tasks.select.return_value = mock_query

        # Mock the column
        mock_column = MagicMock()
        mock_column.asc.return_value = "asc_order"
        mock_completed_tasks.id = mock_column

        history = History()
        result = history.get_historic_task_list_filtered_and_sorted(order={"column": "id", "dir": "asc"})

        mock_query.order_by.assert_called_once()

    @patch("unmanic.libs.history.CompletedTasks")
    @patch("unmanic.libs.history.UnmanicLogging")
    @patch("unmanic.libs.history.config.Config")
    def test_order_descending(self, mock_config, mock_logging, mock_completed_tasks):
        """Test ordering descending."""
        from unmanic.libs.history import History

        mock_query = MagicMock()
        mock_query.order_by.return_value = mock_query
        mock_query.dicts.return_value = []
        mock_completed_tasks.select.return_value = mock_query

        # Mock the column
        mock_column = MagicMock()
        mock_column.desc.return_value = "desc_order"
        mock_completed_tasks.id = mock_column

        history = History()
        result = history.get_historic_task_list_filtered_and_sorted(order={"column": "id", "dir": "desc"})

        mock_query.order_by.assert_called_once()

    @patch("unmanic.libs.history.CompletedTasks")
    @patch("unmanic.libs.history.UnmanicLogging")
    @patch("unmanic.libs.history.config.Config")
    def test_pagination(self, mock_config, mock_logging, mock_completed_tasks):
        """Test pagination with length and start."""
        from unmanic.libs.history import History

        mock_query = MagicMock()
        mock_query.limit.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.dicts.return_value = []
        mock_completed_tasks.select.return_value = mock_query

        history = History()
        result = history.get_historic_task_list_filtered_and_sorted(start=10, length=20)

        mock_query.limit.assert_called_once_with(20)
        mock_query.offset.assert_called_once_with(10)


class TestGetCurrentPathOfHistoricTasksById(unittest.TestCase):
    """Tests for History.get_current_path_of_historic_tasks_by_id method."""

    @patch("unmanic.libs.history.CompletedTasks")
    @patch("unmanic.libs.history.UnmanicLogging")
    @patch("unmanic.libs.history.config.Config")
    def test_returns_paths_for_ids(self, mock_config, mock_logging, mock_completed_tasks):
        """Test returns paths for given IDs."""
        from unmanic.libs.history import History

        mock_query = MagicMock()
        mock_query.where.return_value = mock_query
        mock_query.dicts.return_value = [{"id": 1, "abspath": "/path/to/file"}]
        mock_completed_tasks.select.return_value = mock_query

        history = History()
        result = history.get_current_path_of_historic_tasks_by_id(id_list=[1])

        mock_query.where.assert_called_once()

    @patch("unmanic.libs.history.CompletedTasks")
    @patch("unmanic.libs.history.UnmanicLogging")
    @patch("unmanic.libs.history.config.Config")
    def test_returns_all_without_id_list(self, mock_config, mock_logging, mock_completed_tasks):
        """Test returns all when no id_list provided."""
        from unmanic.libs.history import History

        mock_query = MagicMock()
        mock_query.dicts.return_value = [{"id": 1}]
        mock_completed_tasks.select.return_value = mock_query

        history = History()
        result = history.get_current_path_of_historic_tasks_by_id()

        mock_query.where.assert_not_called()


class TestGetHistoricTasksListWithSourceProbe(unittest.TestCase):
    """Tests for History.get_historic_tasks_list_with_source_probe method."""

    @patch("unmanic.libs.history.CompletedTasks")
    @patch("unmanic.libs.history.UnmanicLogging")
    @patch("unmanic.libs.history.config.Config")
    def test_filters_by_all_params(self, mock_config, mock_logging, mock_completed_tasks):
        """Test filters by all parameters."""
        from unmanic.libs.history import History

        mock_query = MagicMock()
        mock_query.where.return_value = mock_query
        mock_query.dicts.return_value = []
        mock_completed_tasks.select.return_value = mock_query

        history = History()
        result = history.get_historic_tasks_list_with_source_probe(
            id_list=[1],
            search_value="test",
            task_success=True,
            abspath="/path/to/file",
        )

        # where should be called 4 times
        self.assertEqual(mock_query.where.call_count, 4)


class TestGetHistoricTaskDataDictionary(unittest.TestCase):
    """Tests for History.get_historic_task_data_dictionary method."""

    @patch("unmanic.libs.history.CompletedTasks")
    @patch("unmanic.libs.history.UnmanicLogging")
    @patch("unmanic.libs.history.config.Config")
    def test_returns_task_dict(self, mock_config, mock_logging, mock_completed_tasks):
        """Test returns task data as dictionary."""
        from unmanic.libs.history import History

        mock_task = MagicMock()
        mock_task.model_to_dict.return_value = {"id": 1, "task_label": "test"}
        mock_completed_tasks.get_by_id.return_value = mock_task

        history = History()
        result = history.get_historic_task_data_dictionary(1)

        mock_completed_tasks.get_by_id.assert_called_once_with(1)
        self.assertEqual(result["id"], 1)
        self.assertEqual(result["task_label"], "test")

    @patch("unmanic.libs.history.CompletedTasks")
    @patch("unmanic.libs.history.UnmanicLogging")
    @patch("unmanic.libs.history.config.Config")
    def test_returns_false_on_not_found(self, mock_config, mock_logging, mock_completed_tasks):
        """Test returns False when task not found."""
        from unmanic.libs.history import History

        # Create a custom exception class for DoesNotExist
        class DoesNotExist(Exception):
            pass

        mock_completed_tasks.DoesNotExist = DoesNotExist
        mock_completed_tasks.get_by_id.side_effect = DoesNotExist("Not found")

        history = History()
        result = history.get_historic_task_data_dictionary(999)

        self.assertFalse(result)


class TestDeleteHistoricTasksRecursively(unittest.TestCase):
    """Tests for History.delete_historic_tasks_recursively method."""

    @patch("unmanic.libs.history.CompletedTasks")
    @patch("unmanic.libs.history.UnmanicLogging")
    @patch("unmanic.libs.history.config.Config")
    def test_returns_false_without_id_list(self, mock_config, mock_logging, mock_completed_tasks):
        """Test returns False when no id_list provided."""
        from unmanic.libs.history import History

        history = History()
        result = history.delete_historic_tasks_recursively()

        self.assertFalse(result)

    @patch("unmanic.libs.history.CompletedTasks")
    @patch("unmanic.libs.history.UnmanicLogging")
    @patch("unmanic.libs.history.config.Config")
    def test_returns_false_with_empty_id_list(self, mock_config, mock_logging, mock_completed_tasks):
        """Test returns False when id_list is empty."""
        from unmanic.libs.history import History

        history = History()
        result = history.delete_historic_tasks_recursively(id_list=[])

        self.assertFalse(result)

    @patch("unmanic.libs.history.CompletedTasks")
    @patch("unmanic.libs.history.UnmanicLogging")
    @patch("unmanic.libs.history.config.Config")
    def test_deletes_tasks_successfully(self, mock_config, mock_logging, mock_completed_tasks):
        """Test deletes tasks and returns True."""
        from unmanic.libs.history import History

        mock_task = MagicMock()
        mock_query = MagicMock()
        mock_query.where.return_value = [mock_task]
        mock_completed_tasks.select.return_value = mock_query

        history = History()
        result = history.delete_historic_tasks_recursively(id_list=[1])

        mock_task.delete_instance.assert_called_once_with(recursive=True)
        self.assertTrue(result)

    @patch("unmanic.libs.history.CompletedTasks")
    @patch("unmanic.libs.history.UnmanicLogging")
    @patch("unmanic.libs.history.config.Config")
    def test_returns_false_on_delete_error(self, mock_config, mock_logging, mock_completed_tasks):
        """Test returns False when delete raises exception."""
        from unmanic.libs.history import History

        mock_task = MagicMock()
        mock_task.delete_instance.side_effect = Exception("Delete error")
        mock_query = MagicMock()
        mock_query.where.return_value = [mock_task]
        mock_completed_tasks.select.return_value = mock_query

        history = History()
        result = history.delete_historic_tasks_recursively(id_list=[1])

        self.assertFalse(result)


class TestSaveTaskHistory(unittest.TestCase):
    """Tests for History.save_task_history method."""

    @patch("unmanic.libs.history.History.create_historic_task_ffmpeg_log_entry")
    @patch("unmanic.libs.history.History.create_historic_task_entry")
    @patch("unmanic.libs.history.UnmanicLogging")
    @patch("unmanic.libs.history.config.Config")
    def test_saves_task_successfully(self, mock_config, mock_logging, mock_create_entry, mock_create_log):
        """Test saves task and returns True."""
        from unmanic.libs.history import History

        mock_historic_task = MagicMock()
        mock_create_entry.return_value = mock_historic_task

        history = History()
        task_data = {"task_label": "test", "log": "ffmpeg log"}
        result = history.save_task_history(task_data)

        mock_create_entry.assert_called_once_with(task_data)
        mock_create_log.assert_called_once_with(mock_historic_task, "ffmpeg log")
        self.assertTrue(result)

    @patch("unmanic.libs.history.History.create_historic_task_entry")
    @patch("unmanic.libs.history.UnmanicLogging")
    @patch("unmanic.libs.history.config.Config")
    def test_returns_false_on_exception(self, mock_config, mock_logging, mock_create_entry):
        """Test returns False when exception occurs."""
        from unmanic.libs.history import History

        mock_create_entry.side_effect = Exception("Database error")

        history = History()
        task_data = {"task_label": "test"}
        result = history.save_task_history(task_data)

        self.assertFalse(result)


class TestCreateHistoricTaskFfmpegLogEntry(unittest.TestCase):
    """Tests for History.create_historic_task_ffmpeg_log_entry static method."""

    @patch("unmanic.libs.history.CompletedTasksCommandLogs")
    def test_creates_log_entry(self, mock_command_logs):
        """Test creates log entry with task and log."""
        from unmanic.libs.history import History

        mock_task = MagicMock()
        History.create_historic_task_ffmpeg_log_entry(mock_task, "log content")

        mock_command_logs.create.assert_called_once_with(completedtask_id=mock_task, dump="log content")


class TestCreateHistoricTaskEntry(unittest.TestCase):
    """Tests for History.create_historic_task_entry method."""

    @patch("unmanic.libs.history.CompletedTasks")
    @patch("unmanic.libs.history.UnmanicLogging")
    @patch("unmanic.libs.history.config.Config")
    def test_creates_entry_with_valid_data(self, mock_config, mock_logging, mock_completed_tasks):
        """Test creates entry with valid task data."""
        from unmanic.libs.history import History

        mock_created = MagicMock()
        mock_completed_tasks.create.return_value = mock_created

        history = History()
        task_data = {
            "task_label": "test_task",
            "abspath": "/path/to/file",
            "task_success": True,
            "start_time": 1000,
            "finish_time": 2000,
            "processed_by_worker": "worker1",
        }
        result = history.create_historic_task_entry(task_data)

        mock_completed_tasks.create.assert_called_once_with(
            task_label="test_task",
            abspath="/path/to/file",
            task_success=True,
            start_time=1000,
            finish_time=2000,
            processed_by_worker="worker1",
        )
        self.assertEqual(result, mock_created)

    @patch("unmanic.libs.history.UnmanicLogging")
    @patch("unmanic.libs.history.config.Config")
    def test_raises_on_empty_data(self, mock_config, mock_logging):
        """Test raises exception on empty task data."""
        from unmanic.libs.history import History

        history = History()

        with self.assertRaises(Exception) as ctx:
            history.create_historic_task_entry(None)

        self.assertIn("Task data param empty", str(ctx.exception))

    @patch("unmanic.libs.history.UnmanicLogging")
    @patch("unmanic.libs.history.config.Config")
    def test_raises_on_empty_dict(self, mock_config, mock_logging):
        """Test raises exception on empty dict."""
        from unmanic.libs.history import History

        history = History()

        with self.assertRaises(Exception) as ctx:
            history.create_historic_task_entry({})

        self.assertIn("Task data param empty", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()

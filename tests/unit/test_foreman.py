#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unit tests for the Foreman class in unmanic.libs.foreman.

Tests worker management, task distribution, and scheduling logic.
"""

import queue
import threading
import unittest
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch, PropertyMock


class TestForemanInit(unittest.TestCase):
    """Tests for Foreman initialization."""

    @patch("unmanic.libs.foreman.installation_link")
    @patch("unmanic.libs.foreman.UnmanicLogging")
    def test_init_creates_queues(self, mock_logging, mock_link):
        """Test that Foreman initializes with required queues."""
        from unmanic.libs.foreman import Foreman

        mock_logging.get_logger.return_value = MagicMock()

        settings = MagicMock()
        event = threading.Event()
        task_queue = MagicMock()
        data_queues = {}

        with patch.object(Foreman, "configuration_changed", return_value=False):
            foreman = Foreman(data_queues, settings, task_queue, event)

        self.assertIsInstance(foreman.workers_pending_task_queue, queue.Queue)
        self.assertIsInstance(foreman.remote_workers_pending_task_queue, queue.Queue)
        self.assertIsInstance(foreman.complete_queue, queue.Queue)
        self.assertEqual(foreman.workers_pending_task_queue.maxsize, 1)
        self.assertEqual(foreman.worker_threads, {})


class TestForemanConfigManagement(unittest.TestCase):
    """Tests for configuration management methods."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_settings = MagicMock()
        self.mock_event = threading.Event()
        self.mock_task_queue = MagicMock()

    @patch("unmanic.libs.foreman.installation_link")
    @patch("unmanic.libs.foreman.UnmanicLogging")
    def test_save_current_config_with_settings(self, mock_logging, mock_link):
        """Test save_current_config stores settings correctly."""
        from unmanic.libs.foreman import Foreman

        mock_logging.get_logger.return_value = MagicMock()

        with patch.object(Foreman, "configuration_changed", return_value=False):
            foreman = Foreman({}, self.mock_settings, self.mock_task_queue, self.mock_event)

        test_settings = {1: {"enabled_plugins": [], "plugin_flow": []}}
        foreman.save_current_config(settings=test_settings)

        self.assertEqual(foreman.current_config["settings"], test_settings)

    @patch("unmanic.libs.foreman.installation_link")
    @patch("unmanic.libs.foreman.UnmanicLogging")
    def test_save_current_config_with_hash(self, mock_logging, mock_link):
        """Test save_current_config stores hash correctly."""
        from unmanic.libs.foreman import Foreman

        mock_logging.get_logger.return_value = MagicMock()

        with patch.object(Foreman, "configuration_changed", return_value=False):
            foreman = Foreman({}, self.mock_settings, self.mock_task_queue, self.mock_event)

        test_hash = "abc123def456"
        foreman.save_current_config(settings_hash=test_hash)

        self.assertEqual(foreman.current_config["settings_hash"], test_hash)

    @patch("unmanic.libs.foreman.installation_link")
    @patch("unmanic.libs.foreman.Library")
    @patch("unmanic.libs.foreman.UnmanicLogging")
    def test_configuration_changed_returns_true_on_first_call(self, mock_logging, mock_library, mock_link):
        """Test configuration_changed returns True when hash differs."""
        from unmanic.libs.foreman import Foreman

        mock_logging.get_logger.return_value = MagicMock()
        mock_library.get_all_libraries.return_value = []

        with patch.object(Foreman, "configuration_changed", return_value=False):
            foreman = Foreman({}, self.mock_settings, self.mock_task_queue, self.mock_event)

        # Reset the hash to empty
        foreman.current_config["settings_hash"] = ""

        # Now call the real method
        with patch.object(Foreman, "get_current_library_configuration", return_value={}):
            result = Foreman.configuration_changed(foreman)

        # First call should return True (hash changed from empty)
        self.assertTrue(result)

    @patch("unmanic.libs.foreman.installation_link")
    @patch("unmanic.libs.foreman.UnmanicLogging")
    def test_configuration_changed_returns_false_when_unchanged(self, mock_logging, mock_link):
        """Test configuration_changed returns False when hash matches."""
        from unmanic.libs.foreman import Foreman
        import hashlib
        import json

        mock_logging.get_logger.return_value = MagicMock()

        with patch.object(Foreman, "configuration_changed", return_value=False):
            foreman = Foreman({}, self.mock_settings, self.mock_task_queue, self.mock_event)

        # Set up matching hash
        test_config = {"lib1": {"plugins": []}}
        json_encoded = json.dumps(test_config, sort_keys=True).encode()
        config_hash = hashlib.md5(json_encoded).hexdigest()

        foreman.current_config["settings_hash"] = config_hash

        with patch.object(Foreman, "get_current_library_configuration", return_value=test_config):
            result = Foreman.configuration_changed(foreman)

        self.assertFalse(result)


class TestForemanWorkerCount(unittest.TestCase):
    """Tests for worker count methods."""

    @patch("unmanic.libs.foreman.installation_link")
    @patch("unmanic.libs.foreman.WorkerGroup")
    @patch("unmanic.libs.foreman.UnmanicLogging")
    def test_get_total_worker_count(self, mock_logging, mock_worker_group, mock_link):
        """Test get_total_worker_count sums all worker groups."""
        from unmanic.libs.foreman import Foreman

        mock_logging.get_logger.return_value = MagicMock()
        mock_worker_group.get_all_worker_groups.return_value = [
            {"id": 1, "name": "main", "number_of_workers": 3},
            {"id": 2, "name": "secondary", "number_of_workers": 2},
        ]

        with patch.object(Foreman, "configuration_changed", return_value=False):
            foreman = Foreman({}, MagicMock(), MagicMock(), threading.Event())

        result = foreman.get_total_worker_count()
        self.assertEqual(result, 5)

    @patch("unmanic.libs.foreman.installation_link")
    @patch("unmanic.libs.foreman.WorkerGroup")
    @patch("unmanic.libs.foreman.UnmanicLogging")
    def test_get_total_worker_count_empty_groups(self, mock_logging, mock_worker_group, mock_link):
        """Test get_total_worker_count returns 0 with no groups."""
        from unmanic.libs.foreman import Foreman

        mock_logging.get_logger.return_value = MagicMock()
        mock_worker_group.get_all_worker_groups.return_value = []

        with patch.object(Foreman, "configuration_changed", return_value=False):
            foreman = Foreman({}, MagicMock(), MagicMock(), threading.Event())

        result = foreman.get_total_worker_count()
        self.assertEqual(result, 0)


class TestForemanWorkerManagement(unittest.TestCase):
    """Tests for worker thread management."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_settings = MagicMock()
        self.mock_event = threading.Event()
        self.mock_task_queue = MagicMock()

    @patch("unmanic.libs.foreman.installation_link")
    @patch("unmanic.libs.foreman.UnmanicLogging")
    def test_fetch_available_worker_ids_returns_idle_workers(self, mock_logging, mock_link):
        """Test fetch_available_worker_ids returns only idle, alive, not paused workers."""
        from unmanic.libs.foreman import Foreman

        mock_logging.get_logger.return_value = MagicMock()

        with patch.object(Foreman, "configuration_changed", return_value=False):
            foreman = Foreman({}, self.mock_settings, self.mock_task_queue, self.mock_event)

        # Create mock workers
        idle_worker = MagicMock()
        idle_worker.idle = True
        idle_worker.is_alive.return_value = True
        idle_worker.paused = False
        idle_worker.thread_id = "main-0"

        busy_worker = MagicMock()
        busy_worker.idle = False
        busy_worker.is_alive.return_value = True
        busy_worker.paused = False
        busy_worker.thread_id = "main-1"

        paused_worker = MagicMock()
        paused_worker.idle = True
        paused_worker.is_alive.return_value = True
        paused_worker.paused = True
        paused_worker.thread_id = "main-2"

        dead_worker = MagicMock()
        dead_worker.idle = True
        dead_worker.is_alive.return_value = False
        dead_worker.paused = False
        dead_worker.thread_id = "main-3"

        foreman.worker_threads = {
            "main-0": idle_worker,
            "main-1": busy_worker,
            "main-2": paused_worker,
            "main-3": dead_worker,
        }

        result = foreman.fetch_available_worker_ids()

        # Only idle_worker should be returned
        self.assertEqual(result, ["main-0"])

    @patch("unmanic.libs.foreman.installation_link")
    @patch("unmanic.libs.foreman.UnmanicLogging")
    def test_check_for_idle_workers_true(self, mock_logging, mock_link):
        """Test check_for_idle_workers returns True when idle worker exists."""
        from unmanic.libs.foreman import Foreman

        mock_logging.get_logger.return_value = MagicMock()

        with patch.object(Foreman, "configuration_changed", return_value=False):
            foreman = Foreman({}, self.mock_settings, self.mock_task_queue, self.mock_event)

        idle_worker = MagicMock()
        idle_worker.idle = True
        idle_worker.is_alive.return_value = True
        idle_worker.paused = False

        foreman.worker_threads = {"main-0": idle_worker}

        self.assertTrue(foreman.check_for_idle_workers())

    @patch("unmanic.libs.foreman.installation_link")
    @patch("unmanic.libs.foreman.UnmanicLogging")
    def test_check_for_idle_workers_false(self, mock_logging, mock_link):
        """Test check_for_idle_workers returns False when no idle workers."""
        from unmanic.libs.foreman import Foreman

        mock_logging.get_logger.return_value = MagicMock()

        with patch.object(Foreman, "configuration_changed", return_value=False):
            foreman = Foreman({}, self.mock_settings, self.mock_task_queue, self.mock_event)

        busy_worker = MagicMock()
        busy_worker.idle = False
        busy_worker.is_alive.return_value = True
        busy_worker.paused = False

        foreman.worker_threads = {"main-0": busy_worker}

        self.assertFalse(foreman.check_for_idle_workers())

    @patch("unmanic.libs.foreman.installation_link")
    @patch("unmanic.libs.foreman.UnmanicLogging")
    def test_check_for_idle_remote_workers(self, mock_logging, mock_link):
        """Test check_for_idle_remote_workers returns True when remotes available."""
        from unmanic.libs.foreman import Foreman

        mock_logging.get_logger.return_value = MagicMock()

        with patch.object(Foreman, "configuration_changed", return_value=False):
            foreman = Foreman({}, self.mock_settings, self.mock_task_queue, self.mock_event)

        foreman.available_remote_managers = {"remote-1": {"address": "http://example.com"}}

        self.assertTrue(foreman.check_for_idle_remote_workers())

        foreman.available_remote_managers = {}
        self.assertFalse(foreman.check_for_idle_remote_workers())


class TestForemanPauseResume(unittest.TestCase):
    """Tests for worker pause/resume functionality."""

    @patch("unmanic.libs.foreman.installation_link")
    @patch("unmanic.libs.foreman.UnmanicLogging")
    def test_pause_worker_thread(self, mock_logging, mock_link):
        """Test pause_worker_thread sets paused flag."""
        from unmanic.libs.foreman import Foreman

        mock_logging.get_logger.return_value = MagicMock()

        with patch.object(Foreman, "configuration_changed", return_value=False):
            foreman = Foreman({}, MagicMock(), MagicMock(), threading.Event())

        mock_worker = MagicMock()
        mock_worker.paused_flag = threading.Event()
        foreman.worker_threads = {"main-0": mock_worker}

        result = foreman.pause_worker_thread("main-0")

        self.assertTrue(result)
        self.assertTrue(mock_worker.paused_flag.is_set())

    @patch("unmanic.libs.foreman.installation_link")
    @patch("unmanic.libs.foreman.UnmanicLogging")
    def test_pause_worker_thread_not_found(self, mock_logging, mock_link):
        """Test pause_worker_thread returns False when worker not found."""
        from unmanic.libs.foreman import Foreman

        mock_logging.get_logger.return_value = MagicMock()

        with patch.object(Foreman, "configuration_changed", return_value=False):
            foreman = Foreman({}, MagicMock(), MagicMock(), threading.Event())

        foreman.worker_threads = {}

        result = foreman.pause_worker_thread("nonexistent")

        self.assertFalse(result)

    @patch("unmanic.libs.foreman.installation_link")
    @patch("unmanic.libs.foreman.UnmanicLogging")
    def test_pause_worker_thread_records_paused(self, mock_logging, mock_link):
        """Test pause_worker_thread records paused workers when requested."""
        from unmanic.libs.foreman import Foreman

        mock_logging.get_logger.return_value = MagicMock()

        with patch.object(Foreman, "configuration_changed", return_value=False):
            foreman = Foreman({}, MagicMock(), MagicMock(), threading.Event())

        mock_worker = MagicMock()
        mock_worker.paused_flag = threading.Event()
        foreman.worker_threads = {"main-0": mock_worker}

        foreman.pause_worker_thread("main-0", record_paused=True)

        self.assertIn("main-0", foreman.paused_worker_threads)


class TestForemanRemoteWorkers(unittest.TestCase):
    """Tests for remote worker management."""

    @patch("unmanic.libs.foreman.installation_link")
    @patch("unmanic.libs.foreman.UnmanicLogging")
    def test_fetch_available_remote_installation(self, mock_logging, mock_link):
        """Test fetch_available_remote_installation returns first available."""
        from unmanic.libs.foreman import Foreman

        mock_logging.get_logger.return_value = MagicMock()

        with patch.object(Foreman, "configuration_changed", return_value=False):
            foreman = Foreman({}, MagicMock(), MagicMock(), threading.Event())

        foreman.available_remote_managers = {
            "remote-1": {"address": "http://server1.local", "library_names": ["Movies"]},
            "remote-2": {"address": "http://server2.local", "library_names": ["TV"]},
        }
        foreman.remote_task_manager_threads = {}

        installation_id, installation_info = foreman.fetch_available_remote_installation()

        self.assertEqual(installation_id, "remote-1")
        self.assertEqual(installation_info["address"], "http://server1.local")

    @patch("unmanic.libs.foreman.installation_link")
    @patch("unmanic.libs.foreman.UnmanicLogging")
    def test_fetch_available_remote_installation_with_library_filter(self, mock_logging, mock_link):
        """Test fetch_available_remote_installation filters by library name."""
        from unmanic.libs.foreman import Foreman

        mock_logging.get_logger.return_value = MagicMock()

        with patch.object(Foreman, "configuration_changed", return_value=False):
            foreman = Foreman({}, MagicMock(), MagicMock(), threading.Event())

        foreman.available_remote_managers = {
            "remote-1": {"address": "http://server1.local", "library_names": ["Movies"]},
            "remote-2": {"address": "http://server2.local", "library_names": ["TV"]},
        }
        foreman.remote_task_manager_threads = {}

        installation_id, installation_info = foreman.fetch_available_remote_installation(library_name="TV")

        self.assertEqual(installation_id, "remote-2")
        self.assertEqual(installation_info["address"], "http://server2.local")

    @patch("unmanic.libs.foreman.installation_link")
    @patch("unmanic.libs.foreman.UnmanicLogging")
    def test_fetch_available_remote_installation_none_available(self, mock_logging, mock_link):
        """Test fetch_available_remote_installation returns None when none available."""
        from unmanic.libs.foreman import Foreman

        mock_logging.get_logger.return_value = MagicMock()

        with patch.object(Foreman, "configuration_changed", return_value=False):
            foreman = Foreman({}, MagicMock(), MagicMock(), threading.Event())

        foreman.available_remote_managers = {}
        foreman.remote_task_manager_threads = {}

        installation_id, installation_info = foreman.fetch_available_remote_installation()

        self.assertIsNone(installation_id)
        self.assertEqual(installation_info, {})

    @patch("unmanic.libs.foreman.installation_link")
    @patch("unmanic.libs.foreman.UnmanicLogging")
    def test_get_available_remote_library_names(self, mock_logging, mock_link):
        """Test get_available_remote_library_names returns unique names."""
        from unmanic.libs.foreman import Foreman

        mock_logging.get_logger.return_value = MagicMock()

        with patch.object(Foreman, "configuration_changed", return_value=False):
            foreman = Foreman({}, MagicMock(), MagicMock(), threading.Event())

        foreman.available_remote_managers = {
            "remote-1": {"library_names": ["Movies", "TV"]},
            "remote-2": {"library_names": ["TV", "Music"]},  # TV is duplicate
        }

        result = foreman.get_available_remote_library_names()

        self.assertEqual(sorted(result), ["Movies", "Music", "TV"])


class TestForemanPostprocessorQueue(unittest.TestCase):
    """Tests for postprocessor queue management."""

    @patch("unmanic.libs.foreman.FrontendPushMessages")
    @patch("unmanic.libs.foreman.installation_link")
    @patch("unmanic.libs.foreman.WorkerGroup")
    @patch("unmanic.libs.foreman.UnmanicLogging")
    def test_postprocessor_queue_full_returns_true(self, mock_logging, mock_worker_group, mock_link, mock_frontend):
        """Test postprocessor_queue_full returns True when over limit."""
        from unmanic.libs.foreman import Foreman

        mock_logging.get_logger.return_value = MagicMock()
        mock_worker_group.get_all_worker_groups.return_value = [{"id": 1, "number_of_workers": 2}]
        mock_frontend.return_value = MagicMock()

        mock_task_queue = MagicMock()
        # 10 items in queue, limit is workers(2) + 1 = 3
        mock_task_queue.list_processed_tasks.return_value = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

        with patch.object(Foreman, "configuration_changed", return_value=False):
            foreman = Foreman({}, MagicMock(), mock_task_queue, threading.Event())

        foreman.available_remote_managers = {}
        foreman.remote_task_manager_threads = {}

        result = foreman.postprocessor_queue_full()

        self.assertTrue(result)

    @patch("unmanic.libs.foreman.FrontendPushMessages")
    @patch("unmanic.libs.foreman.installation_link")
    @patch("unmanic.libs.foreman.WorkerGroup")
    @patch("unmanic.libs.foreman.UnmanicLogging")
    def test_postprocessor_queue_full_returns_false(self, mock_logging, mock_worker_group, mock_link, mock_frontend):
        """Test postprocessor_queue_full returns False when under limit."""
        from unmanic.libs.foreman import Foreman

        mock_logging.get_logger.return_value = MagicMock()
        mock_worker_group.get_all_worker_groups.return_value = [{"id": 1, "number_of_workers": 5}]
        mock_frontend.return_value = MagicMock()

        mock_task_queue = MagicMock()
        # 3 items in queue, limit is workers(5) + 1 = 6
        mock_task_queue.list_processed_tasks.return_value = [1, 2, 3]

        with patch.object(Foreman, "configuration_changed", return_value=False):
            foreman = Foreman({}, MagicMock(), mock_task_queue, threading.Event())

        foreman.available_remote_managers = {}
        foreman.remote_task_manager_threads = {}

        result = foreman.postprocessor_queue_full()

        self.assertFalse(result)


class TestForemanScheduling(unittest.TestCase):
    """Tests for scheduled task execution."""

    @patch("unmanic.libs.foreman.installation_link")
    @patch("unmanic.libs.foreman.UnmanicLogging")
    def test_run_task_pause(self, mock_logging, mock_link):
        """Test run_task executes pause task."""
        from unmanic.libs.foreman import Foreman

        mock_logging.get_logger.return_value = MagicMock()

        with patch.object(Foreman, "configuration_changed", return_value=False):
            foreman = Foreman({}, MagicMock(), MagicMock(), threading.Event())

        mock_worker_group = MagicMock()
        mock_worker_group.get_id.return_value = 1

        with patch.object(foreman, "pause_all_worker_threads") as mock_pause:
            foreman.run_task("12:00", "pause", 0, mock_worker_group)

            mock_pause.assert_called_once_with(worker_group_id=1)
            self.assertEqual(foreman.last_schedule_run, "12:00")

    @patch("unmanic.libs.foreman.installation_link")
    @patch("unmanic.libs.foreman.UnmanicLogging")
    def test_run_task_resume(self, mock_logging, mock_link):
        """Test run_task executes resume task."""
        from unmanic.libs.foreman import Foreman

        mock_logging.get_logger.return_value = MagicMock()

        with patch.object(Foreman, "configuration_changed", return_value=False):
            foreman = Foreman({}, MagicMock(), MagicMock(), threading.Event())

        mock_worker_group = MagicMock()
        mock_worker_group.get_id.return_value = 1

        with patch.object(foreman, "resume_all_worker_threads") as mock_resume:
            foreman.run_task("12:00", "resume", 0, mock_worker_group)

            mock_resume.assert_called_once_with(worker_group_id=1)

    @patch("unmanic.libs.foreman.installation_link")
    @patch("unmanic.libs.foreman.UnmanicLogging")
    def test_run_task_count(self, mock_logging, mock_link):
        """Test run_task executes worker count task."""
        from unmanic.libs.foreman import Foreman

        mock_logging.get_logger.return_value = MagicMock()

        with patch.object(Foreman, "configuration_changed", return_value=False):
            foreman = Foreman({}, MagicMock(), MagicMock(), threading.Event())

        mock_worker_group = MagicMock()
        mock_worker_group.get_id.return_value = 1

        foreman.run_task("12:00", "count", 5, mock_worker_group)

        mock_worker_group.set_number_of_workers.assert_called_once_with(5)
        mock_worker_group.save.assert_called_once()


class TestForemanStop(unittest.TestCase):
    """Tests for Foreman stop functionality."""

    @patch("unmanic.libs.foreman.installation_link")
    @patch("unmanic.libs.foreman.UnmanicLogging")
    def test_stop_marks_workers_redundant(self, mock_logging, mock_link):
        """Test stop marks all workers as redundant."""
        from unmanic.libs.foreman import Foreman

        mock_logging.get_logger.return_value = MagicMock()

        with patch.object(Foreman, "configuration_changed", return_value=False):
            foreman = Foreman({}, MagicMock(), MagicMock(), threading.Event())

        mock_worker = MagicMock()
        foreman.worker_threads = {"main-0": mock_worker, "main-1": mock_worker}
        foreman.remote_task_manager_threads = {}

        with patch.object(foreman, "mark_worker_thread_as_redundant") as mock_mark:
            foreman.stop()

            self.assertEqual(mock_mark.call_count, 2)
            self.assertTrue(foreman.abort_flag.is_set())


class TestForemanRemoveStaleManagers(unittest.TestCase):
    """Tests for removing stale remote managers."""

    @patch("unmanic.libs.foreman.installation_link")
    @patch("unmanic.libs.foreman.UnmanicLogging")
    def test_remove_stale_available_remote_managers(self, mock_logging, mock_link):
        """Test remove_stale_available_remote_managers removes old entries."""
        from unmanic.libs.foreman import Foreman

        mock_logging.get_logger.return_value = MagicMock()

        with patch.object(Foreman, "configuration_changed", return_value=False):
            foreman = Foreman({}, MagicMock(), MagicMock(), threading.Event())

        # Create one fresh and one stale entry
        foreman.available_remote_managers = {
            "fresh": {"created": datetime.now()},
            "stale": {"created": datetime.now() - timedelta(seconds=60)},
        }
        foreman.remote_task_manager_threads = {}

        foreman.remove_stale_available_remote_managers()

        # Only fresh should remain
        self.assertIn("fresh", foreman.available_remote_managers)
        self.assertNotIn("stale", foreman.available_remote_managers)


class TestForemanResumeWorkerThread(unittest.TestCase):
    """Tests for resume_worker_thread method."""

    @patch("unmanic.libs.foreman.installation_link")
    @patch("unmanic.libs.foreman.UnmanicLogging")
    def test_resume_worker_thread_success(self, mock_logging, mock_link):
        """Test resume_worker_thread successfully resumes a worker."""
        from unmanic.libs.foreman import Foreman

        mock_logging.get_logger.return_value = MagicMock()

        with patch.object(Foreman, "configuration_changed", return_value=False):
            foreman = Foreman({}, MagicMock(), MagicMock(), threading.Event())

        mock_worker = MagicMock()
        mock_worker.paused_flag = threading.Event()
        mock_worker.paused_flag.set()  # Worker is paused
        foreman.worker_threads = {"main-0": mock_worker}
        foreman.paused_worker_threads = ["main-0"]

        result = foreman.resume_worker_thread("main-0")

        self.assertTrue(result)
        self.assertFalse(mock_worker.paused_flag.is_set())
        self.assertNotIn("main-0", foreman.paused_worker_threads)

    @patch("unmanic.libs.foreman.installation_link")
    @patch("unmanic.libs.foreman.UnmanicLogging")
    def test_resume_worker_thread_not_found(self, mock_logging, mock_link):
        """Test resume_worker_thread returns False for unknown worker."""
        from unmanic.libs.foreman import Foreman

        mock_logging.get_logger.return_value = MagicMock()

        with patch.object(Foreman, "configuration_changed", return_value=False):
            foreman = Foreman({}, MagicMock(), MagicMock(), threading.Event())

        foreman.worker_threads = {}

        result = foreman.resume_worker_thread("nonexistent")

        self.assertFalse(result)


class TestForemanResumeAllWorkerThreads(unittest.TestCase):
    """Tests for resume_all_worker_threads method."""

    @patch("unmanic.libs.foreman.installation_link")
    @patch("unmanic.libs.foreman.UnmanicLogging")
    def test_resume_all_worker_threads(self, mock_logging, mock_link):
        """Test resume_all_worker_threads resumes all workers."""
        from unmanic.libs.foreman import Foreman

        mock_logging.get_logger.return_value = MagicMock()

        with patch.object(Foreman, "configuration_changed", return_value=False):
            foreman = Foreman({}, MagicMock(), MagicMock(), threading.Event())

        mock_worker1 = MagicMock()
        mock_worker1.paused_flag = threading.Event()
        mock_worker1.paused_flag.set()
        mock_worker1.worker_group_id = 1

        mock_worker2 = MagicMock()
        mock_worker2.paused_flag = threading.Event()
        mock_worker2.paused_flag.set()
        mock_worker2.worker_group_id = 1

        foreman.worker_threads = {"main-0": mock_worker1, "main-1": mock_worker2}
        foreman.paused_worker_threads = ["main-0", "main-1"]

        result = foreman.resume_all_worker_threads()

        self.assertTrue(result)
        self.assertFalse(mock_worker1.paused_flag.is_set())
        self.assertFalse(mock_worker2.paused_flag.is_set())

    @patch("unmanic.libs.foreman.installation_link")
    @patch("unmanic.libs.foreman.UnmanicLogging")
    def test_resume_all_worker_threads_by_group(self, mock_logging, mock_link):
        """Test resume_all_worker_threads filters by worker group."""
        from unmanic.libs.foreman import Foreman

        mock_logging.get_logger.return_value = MagicMock()

        with patch.object(Foreman, "configuration_changed", return_value=False):
            foreman = Foreman({}, MagicMock(), MagicMock(), threading.Event())

        mock_worker1 = MagicMock()
        mock_worker1.paused_flag = threading.Event()
        mock_worker1.paused_flag.set()
        mock_worker1.worker_group_id = 1

        mock_worker2 = MagicMock()
        mock_worker2.paused_flag = threading.Event()
        mock_worker2.paused_flag.set()
        mock_worker2.worker_group_id = 2

        foreman.worker_threads = {"main-0": mock_worker1, "main-1": mock_worker2}
        foreman.paused_worker_threads = ["main-0", "main-1"]

        result = foreman.resume_all_worker_threads(worker_group_id=1)

        self.assertTrue(result)
        self.assertFalse(mock_worker1.paused_flag.is_set())  # Group 1 - resumed
        self.assertTrue(mock_worker2.paused_flag.is_set())  # Group 2 - still paused

    @patch("unmanic.libs.foreman.installation_link")
    @patch("unmanic.libs.foreman.UnmanicLogging")
    def test_resume_all_worker_threads_recorded_only(self, mock_logging, mock_link):
        """Test resume_all_worker_threads with recorded_paused_only flag."""
        from unmanic.libs.foreman import Foreman

        mock_logging.get_logger.return_value = MagicMock()

        with patch.object(Foreman, "configuration_changed", return_value=False):
            foreman = Foreman({}, MagicMock(), MagicMock(), threading.Event())

        mock_worker1 = MagicMock()
        mock_worker1.paused_flag = threading.Event()
        mock_worker1.paused_flag.set()
        mock_worker1.worker_group_id = 1

        mock_worker2 = MagicMock()
        mock_worker2.paused_flag = threading.Event()
        mock_worker2.paused_flag.set()
        mock_worker2.worker_group_id = 1

        foreman.worker_threads = {"main-0": mock_worker1, "main-1": mock_worker2}
        foreman.paused_worker_threads = ["main-0"]  # Only main-0 recorded as paused

        result = foreman.resume_all_worker_threads(recorded_paused_only=True)

        self.assertTrue(result)
        self.assertFalse(mock_worker1.paused_flag.is_set())  # Recorded - resumed
        self.assertTrue(mock_worker2.paused_flag.is_set())  # Not recorded - still paused


class TestForemanTerminateWorkerThread(unittest.TestCase):
    """Tests for terminate_worker_thread method."""

    @patch("unmanic.libs.foreman.installation_link")
    @patch("unmanic.libs.foreman.UnmanicLogging")
    def test_terminate_worker_thread_success(self, mock_logging, mock_link):
        """Test terminate_worker_thread successfully terminates worker."""
        from unmanic.libs.foreman import Foreman

        mock_logging.get_logger.return_value = MagicMock()

        with patch.object(Foreman, "configuration_changed", return_value=False):
            foreman = Foreman({}, MagicMock(), MagicMock(), threading.Event())

        mock_worker = MagicMock()
        foreman.worker_threads = {"main-0": mock_worker}

        with patch.object(foreman, "mark_worker_thread_as_redundant") as mock_mark:
            result = foreman.terminate_worker_thread("main-0")

            self.assertTrue(result)
            mock_mark.assert_called_once_with("main-0")

    @patch("unmanic.libs.foreman.installation_link")
    @patch("unmanic.libs.foreman.UnmanicLogging")
    def test_terminate_worker_thread_not_found(self, mock_logging, mock_link):
        """Test terminate_worker_thread returns False for unknown worker."""
        from unmanic.libs.foreman import Foreman

        mock_logging.get_logger.return_value = MagicMock()

        with patch.object(Foreman, "configuration_changed", return_value=False):
            foreman = Foreman({}, MagicMock(), MagicMock(), threading.Event())

        foreman.worker_threads = {}

        result = foreman.terminate_worker_thread("nonexistent")

        self.assertFalse(result)


class TestForemanTerminateAllWorkerThreads(unittest.TestCase):
    """Tests for terminate_all_worker_threads method."""

    @patch("unmanic.libs.foreman.installation_link")
    @patch("unmanic.libs.foreman.UnmanicLogging")
    def test_terminate_all_worker_threads(self, mock_logging, mock_link):
        """Test terminate_all_worker_threads terminates all workers."""
        from unmanic.libs.foreman import Foreman

        mock_logging.get_logger.return_value = MagicMock()

        with patch.object(Foreman, "configuration_changed", return_value=False):
            foreman = Foreman({}, MagicMock(), MagicMock(), threading.Event())

        mock_worker1 = MagicMock()
        mock_worker2 = MagicMock()
        foreman.worker_threads = {"main-0": mock_worker1, "main-1": mock_worker2}

        with patch.object(foreman, "mark_worker_thread_as_redundant") as mock_mark:
            result = foreman.terminate_all_worker_threads()

            self.assertTrue(result)
            self.assertEqual(mock_mark.call_count, 2)


class TestForemanValidateWorkerConfig(unittest.TestCase):
    """Tests for validate_worker_config method."""

    @patch("unmanic.libs.foreman.Library")
    @patch("unmanic.libs.foreman.PluginsHandler")
    @patch("unmanic.libs.foreman.FrontendPushMessages")
    @patch("unmanic.libs.foreman.installation_link")
    @patch("unmanic.libs.foreman.UnmanicLogging")
    def test_validate_worker_config_valid(self, mock_logging, mock_link, mock_messages, mock_plugins_handler, mock_library):
        """Test validate_worker_config returns True when all validations pass."""
        from unmanic.libs.foreman import Foreman

        mock_logging.get_logger.return_value = MagicMock()
        mock_plugins_handler.return_value.get_incompatible_enabled_plugins.return_value = []
        mock_link.Links.return_value.within_enabled_link_limits.return_value = True
        mock_library.within_library_count_limits.return_value = True

        with patch.object(Foreman, "configuration_changed", return_value=False):
            foreman = Foreman({}, MagicMock(), MagicMock(), threading.Event())

        with patch.object(foreman, "configuration_changed", return_value=False):
            result = foreman.validate_worker_config()

        self.assertTrue(result)

    @patch("unmanic.libs.foreman.Library")
    @patch("unmanic.libs.foreman.PluginsHandler")
    @patch("unmanic.libs.foreman.FrontendPushMessages")
    @patch("unmanic.libs.foreman.installation_link")
    @patch("unmanic.libs.foreman.UnmanicLogging")
    def test_validate_worker_config_incompatible_plugins(
        self, mock_logging, mock_link, mock_messages, mock_plugins_handler, mock_library
    ):
        """Test validate_worker_config returns False for incompatible plugins."""
        from unmanic.libs.foreman import Foreman

        mock_logging.get_logger.return_value = MagicMock()
        mock_plugins_handler.return_value.get_incompatible_enabled_plugins.return_value = ["bad_plugin"]
        mock_link.Links.return_value.within_enabled_link_limits.return_value = True
        mock_library.within_library_count_limits.return_value = True

        with patch.object(Foreman, "configuration_changed", return_value=False):
            foreman = Foreman({}, MagicMock(), MagicMock(), threading.Event())

        with patch.object(foreman, "configuration_changed", return_value=False):
            result = foreman.validate_worker_config()

        self.assertFalse(result)

    @patch("unmanic.libs.foreman.Library")
    @patch("unmanic.libs.foreman.PluginsHandler")
    @patch("unmanic.libs.foreman.FrontendPushMessages")
    @patch("unmanic.libs.foreman.installation_link")
    @patch("unmanic.libs.foreman.UnmanicLogging")
    def test_validate_worker_config_link_limits_exceeded(
        self, mock_logging, mock_link, mock_messages, mock_plugins_handler, mock_library
    ):
        """Test validate_worker_config returns False when link limits exceeded."""
        from unmanic.libs.foreman import Foreman

        mock_logging.get_logger.return_value = MagicMock()
        mock_plugins_handler.return_value.get_incompatible_enabled_plugins.return_value = []
        mock_link.Links.return_value.within_enabled_link_limits.return_value = False
        mock_library.within_library_count_limits.return_value = True

        with patch.object(Foreman, "configuration_changed", return_value=False):
            foreman = Foreman({}, MagicMock(), MagicMock(), threading.Event())

        with patch.object(foreman, "configuration_changed", return_value=False):
            result = foreman.validate_worker_config()

        self.assertFalse(result)

    @patch("unmanic.libs.foreman.Library")
    @patch("unmanic.libs.foreman.PluginsHandler")
    @patch("unmanic.libs.foreman.FrontendPushMessages")
    @patch("unmanic.libs.foreman.installation_link")
    @patch("unmanic.libs.foreman.UnmanicLogging")
    def test_validate_worker_config_configuration_changed(
        self, mock_logging, mock_link, mock_messages, mock_plugins_handler, mock_library
    ):
        """Test validate_worker_config returns False when configuration changed."""
        from unmanic.libs.foreman import Foreman

        mock_logging.get_logger.return_value = MagicMock()
        mock_plugins_handler.return_value.get_incompatible_enabled_plugins.return_value = []
        mock_link.Links.return_value.within_enabled_link_limits.return_value = True
        mock_library.within_library_count_limits.return_value = True

        with patch.object(Foreman, "configuration_changed", return_value=False):
            foreman = Foreman({}, MagicMock(), MagicMock(), threading.Event())

        with patch.object(foreman, "configuration_changed", return_value=True):
            result = foreman.validate_worker_config()

        self.assertFalse(result)

    @patch("unmanic.libs.foreman.Library")
    @patch("unmanic.libs.foreman.PluginsHandler")
    @patch("unmanic.libs.foreman.FrontendPushMessages")
    @patch("unmanic.libs.foreman.installation_link")
    @patch("unmanic.libs.foreman.UnmanicLogging")
    def test_validate_worker_config_library_limits_exceeded(
        self, mock_logging, mock_link, mock_messages, mock_plugins_handler, mock_library
    ):
        """Test validate_worker_config returns False when library limits exceeded."""
        from unmanic.libs.foreman import Foreman

        mock_logging.get_logger.return_value = MagicMock()
        mock_plugins_handler.return_value.get_incompatible_enabled_plugins.return_value = []
        mock_link.Links.return_value.within_enabled_link_limits.return_value = True
        mock_library.within_library_count_limits.return_value = False

        with patch.object(Foreman, "configuration_changed", return_value=False):
            foreman = Foreman({}, MagicMock(), MagicMock(), threading.Event())

        with patch.object(foreman, "configuration_changed", return_value=False):
            result = foreman.validate_worker_config()

        self.assertFalse(result)


class TestForemanGetCurrentLibraryConfiguration(unittest.TestCase):
    """Tests for get_current_library_configuration method."""

    @patch("unmanic.libs.foreman.Library")
    @patch("unmanic.libs.foreman.installation_link")
    @patch("unmanic.libs.foreman.UnmanicLogging")
    def test_get_current_library_configuration_empty(self, mock_logging, mock_link, mock_library):
        """Test get_current_library_configuration with no libraries."""
        from unmanic.libs.foreman import Foreman

        mock_logging.get_logger.return_value = MagicMock()
        mock_library.get_all_libraries.return_value = []

        with patch.object(Foreman, "configuration_changed", return_value=False):
            foreman = Foreman({}, MagicMock(), MagicMock(), threading.Event())

        result = foreman.get_current_library_configuration()

        self.assertEqual(result, {})

    @patch("unmanic.libs.foreman.Library")
    @patch("unmanic.libs.foreman.installation_link")
    @patch("unmanic.libs.foreman.UnmanicLogging")
    def test_get_current_library_configuration_with_library(self, mock_logging, mock_link, mock_library):
        """Test get_current_library_configuration with a library."""
        from unmanic.libs.foreman import Foreman

        mock_logging.get_logger.return_value = MagicMock()
        mock_library.get_all_libraries.return_value = [{"id": 1}]

        mock_lib_instance = MagicMock()
        mock_lib_instance.get_enabled_plugins.return_value = [{"plugin_id": "video_encoder", "settings": {"codec": "h265"}}]
        mock_lib_instance.get_plugin_flow.return_value = [{"plugin_id": "video_encoder", "order": 1}]
        mock_library.side_effect = [mock_lib_instance]

        with patch.object(Foreman, "configuration_changed", return_value=False):
            foreman = Foreman({}, MagicMock(), MagicMock(), threading.Event())

        # Need to reset mock after __init__
        mock_library.get_all_libraries.return_value = [{"id": 1}]
        mock_library.side_effect = None
        mock_library.return_value = mock_lib_instance

        result = foreman.get_current_library_configuration()

        self.assertIn(1, result)
        self.assertEqual(len(result[1]["enabled_plugins"]), 1)
        self.assertEqual(result[1]["enabled_plugins"][0]["plugin_id"], "video_encoder")


class TestForemanPauseAllWorkerThreads(unittest.TestCase):
    """Tests for pause_all_worker_threads method."""

    @patch("unmanic.libs.foreman.installation_link")
    @patch("unmanic.libs.foreman.UnmanicLogging")
    def test_pause_all_worker_threads(self, mock_logging, mock_link):
        """Test pause_all_worker_threads pauses all workers."""
        from unmanic.libs.foreman import Foreman

        mock_logging.get_logger.return_value = MagicMock()

        with patch.object(Foreman, "configuration_changed", return_value=False):
            foreman = Foreman({}, MagicMock(), MagicMock(), threading.Event())

        mock_worker1 = MagicMock()
        mock_worker1.paused_flag = threading.Event()
        mock_worker1.worker_group_id = 1

        mock_worker2 = MagicMock()
        mock_worker2.paused_flag = threading.Event()
        mock_worker2.worker_group_id = 1

        foreman.worker_threads = {"main-0": mock_worker1, "main-1": mock_worker2}
        foreman.paused_worker_threads = []

        result = foreman.pause_all_worker_threads()

        self.assertTrue(result)
        self.assertTrue(mock_worker1.paused_flag.is_set())
        self.assertTrue(mock_worker2.paused_flag.is_set())

    @patch("unmanic.libs.foreman.installation_link")
    @patch("unmanic.libs.foreman.UnmanicLogging")
    def test_pause_all_worker_threads_by_group(self, mock_logging, mock_link):
        """Test pause_all_worker_threads filters by worker group."""
        from unmanic.libs.foreman import Foreman

        mock_logging.get_logger.return_value = MagicMock()

        with patch.object(Foreman, "configuration_changed", return_value=False):
            foreman = Foreman({}, MagicMock(), MagicMock(), threading.Event())

        mock_worker1 = MagicMock()
        mock_worker1.paused_flag = threading.Event()
        mock_worker1.worker_group_id = 1

        mock_worker2 = MagicMock()
        mock_worker2.paused_flag = threading.Event()
        mock_worker2.worker_group_id = 2

        foreman.worker_threads = {"main-0": mock_worker1, "main-1": mock_worker2}
        foreman.paused_worker_threads = []

        result = foreman.pause_all_worker_threads(worker_group_id=1)

        self.assertTrue(result)
        self.assertTrue(mock_worker1.paused_flag.is_set())  # Group 1 - paused
        self.assertFalse(mock_worker2.paused_flag.is_set())  # Group 2 - not paused

    @patch("unmanic.libs.foreman.installation_link")
    @patch("unmanic.libs.foreman.UnmanicLogging")
    def test_pause_all_worker_threads_with_record(self, mock_logging, mock_link):
        """Test pause_all_worker_threads with record_paused flag."""
        from unmanic.libs.foreman import Foreman

        mock_logging.get_logger.return_value = MagicMock()

        with patch.object(Foreman, "configuration_changed", return_value=False):
            foreman = Foreman({}, MagicMock(), MagicMock(), threading.Event())

        mock_worker = MagicMock()
        mock_worker.paused_flag = threading.Event()
        mock_worker.worker_group_id = 1

        foreman.worker_threads = {"main-0": mock_worker}
        foreman.paused_worker_threads = []

        result = foreman.pause_all_worker_threads(record_paused=True)

        self.assertTrue(result)
        self.assertIn("main-0", foreman.paused_worker_threads)


class TestForemanCheckIdleWorkers(unittest.TestCase):
    """Tests for check_for_idle_workers method."""

    @patch("unmanic.libs.foreman.installation_link")
    @patch("unmanic.libs.foreman.UnmanicLogging")
    def test_check_for_idle_workers_paused(self, mock_logging, mock_link):
        """Test check_for_idle_workers returns False when workers are paused."""
        from unmanic.libs.foreman import Foreman

        mock_logging.get_logger.return_value = MagicMock()

        with patch.object(Foreman, "configuration_changed", return_value=False):
            foreman = Foreman({}, MagicMock(), MagicMock(), threading.Event())

        mock_worker = MagicMock()
        mock_worker.idle = True
        mock_worker.paused_flag = threading.Event()
        mock_worker.paused_flag.set()  # Worker is paused

        foreman.worker_threads = {"main-0": mock_worker}

        result = foreman.check_for_idle_workers()

        self.assertFalse(result)


class TestForemanMarkRemoteTaskManagerRedundant(unittest.TestCase):
    """Tests for mark_remote_task_manager_thread_as_redundant method."""

    @patch("unmanic.libs.foreman.installation_link")
    @patch("unmanic.libs.foreman.UnmanicLogging")
    def test_mark_remote_task_manager_thread_as_redundant(self, mock_logging, mock_link):
        """Test marking remote task manager as redundant."""
        from unmanic.libs.foreman import Foreman

        mock_logging.get_logger.return_value = MagicMock()

        with patch.object(Foreman, "configuration_changed", return_value=False):
            foreman = Foreman({}, MagicMock(), MagicMock(), threading.Event())

        mock_manager = MagicMock()
        mock_manager.redundant_flag = threading.Event()
        foreman.remote_task_manager_threads = {"remote-0": mock_manager}

        foreman.mark_remote_task_manager_thread_as_redundant("remote-0")

        self.assertTrue(mock_manager.redundant_flag.is_set())


if __name__ == "__main__":
    unittest.main()

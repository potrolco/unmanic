#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unit tests for the Worker and WorkerSubprocessMonitor classes.

Tests non-threading worker logic including status management,
task handling, and subprocess monitoring.
"""

import queue
import threading
import unittest
from unittest.mock import MagicMock, patch


class TestWorkerSubprocessMonitorStats(unittest.TestCase):
    """Tests for WorkerSubprocessMonitor subprocess statistics."""

    @patch("unmanic.libs.workers.UnmanicLogging")
    def test_get_subprocess_stats_not_running(self, mock_logging):
        """Test get_subprocess_stats when no process running."""
        from unmanic.libs.workers import WorkerSubprocessMonitor

        mock_logging.get_logger.return_value = MagicMock()

        mock_parent = MagicMock()
        mock_parent.event = threading.Event()
        mock_parent.redundant_flag = threading.Event()
        mock_parent.paused_flag = threading.Event()

        monitor = WorkerSubprocessMonitor(mock_parent)
        # Default subprocess_pid is None, other stats default to 0

        stats = monitor.get_subprocess_stats()

        # Implementation converts all values to strings
        self.assertEqual(stats["pid"], "None")
        self.assertEqual(stats["percent"], "0")  # Default is 0
        # elapsed is computed via get_subprocess_elapsed()

    @patch("unmanic.libs.workers.UnmanicLogging")
    def test_get_subprocess_stats_running(self, mock_logging):
        """Test get_subprocess_stats when process is running."""
        from unmanic.libs.workers import WorkerSubprocessMonitor

        mock_logging.get_logger.return_value = MagicMock()

        mock_parent = MagicMock()
        mock_parent.event = threading.Event()
        mock_parent.redundant_flag = threading.Event()
        mock_parent.paused_flag = threading.Event()

        monitor = WorkerSubprocessMonitor(mock_parent)
        monitor.subprocess_pid = 12345
        monitor.subprocess_percent = 50
        monitor.subprocess_elapsed = 120
        monitor.subprocess_cpu_percent = 25.5
        monitor.subprocess_mem_percent = 10.2
        monitor.subprocess_rss_bytes = 1024000
        monitor.subprocess_vms_bytes = 2048000

        stats = monitor.get_subprocess_stats()

        # Implementation converts all values to strings
        self.assertEqual(stats["pid"], "12345")
        self.assertEqual(stats["percent"], "50")
        # elapsed is computed via get_subprocess_elapsed()
        self.assertEqual(stats["cpu_percent"], "25.5")
        self.assertEqual(stats["mem_percent"], "10.2")

    @patch("unmanic.libs.workers.UnmanicLogging")
    def test_set_subprocess_percent(self, mock_logging):
        """Test set_subprocess_percent updates value."""
        from unmanic.libs.workers import WorkerSubprocessMonitor

        mock_logging.get_logger.return_value = MagicMock()

        mock_parent = MagicMock()
        mock_parent.event = threading.Event()
        mock_parent.redundant_flag = threading.Event()
        mock_parent.paused_flag = threading.Event()

        monitor = WorkerSubprocessMonitor(mock_parent)
        monitor.subprocess_percent = 0

        monitor.set_subprocess_percent(75)

        self.assertEqual(monitor.subprocess_percent, 75)

    @patch("unmanic.libs.workers.UnmanicLogging")
    def test_set_subprocess_start_time(self, mock_logging):
        """Test set_subprocess_start_time updates value."""
        from unmanic.libs.workers import WorkerSubprocessMonitor

        mock_logging.get_logger.return_value = MagicMock()

        mock_parent = MagicMock()
        mock_parent.event = threading.Event()
        mock_parent.redundant_flag = threading.Event()
        mock_parent.paused_flag = threading.Event()

        monitor = WorkerSubprocessMonitor(mock_parent)

        monitor.set_subprocess_start_time(1234567890.0)

        self.assertEqual(monitor.subprocess_start_time, 1234567890.0)


class TestWorkerInit(unittest.TestCase):
    """Tests for Worker initialization."""

    @patch("unmanic.libs.workers.UnmanicLogging")
    def test_worker_init(self, mock_logging):
        """Test Worker initialization sets attributes correctly."""
        from unmanic.libs.workers import Worker

        mock_logging.get_logger.return_value = MagicMock()

        pending_queue = queue.Queue()
        complete_queue = queue.Queue()
        event = threading.Event()

        worker = Worker(
            thread_id="main-0",
            name="Worker-1",
            worker_group_id=1,
            pending_queue=pending_queue,
            complete_queue=complete_queue,
            event=event,
        )

        self.assertEqual(worker.thread_id, "main-0")
        self.assertEqual(worker.name, "Worker-1")
        self.assertEqual(worker.worker_group_id, 1)
        self.assertTrue(worker.idle)
        self.assertFalse(worker.paused)
        self.assertIsNone(worker.current_task)
        self.assertIsNone(worker.current_gpu)

    @patch("unmanic.libs.workers.UnmanicLogging")
    def test_worker_init_with_different_ids(self, mock_logging):
        """Test Worker with various thread IDs."""
        from unmanic.libs.workers import Worker

        mock_logging.get_logger.return_value = MagicMock()

        worker = Worker(
            thread_id="secondary-5",
            name="SecondaryWorker-6",
            worker_group_id=2,
            pending_queue=queue.Queue(),
            complete_queue=queue.Queue(),
            event=threading.Event(),
        )

        self.assertEqual(worker.thread_id, "secondary-5")
        self.assertEqual(worker.worker_group_id, 2)


class TestWorkerSetTask(unittest.TestCase):
    """Tests for Worker.set_task method."""

    @patch("unmanic.libs.workers.UnmanicLogging")
    def test_set_task_when_idle(self, mock_logging):
        """Test set_task assigns task when worker is idle."""
        from unmanic.libs.workers import Worker

        mock_logging.get_logger.return_value = MagicMock()

        worker = Worker(
            thread_id="main-0",
            name="Worker-1",
            worker_group_id=1,
            pending_queue=queue.Queue(),
            complete_queue=queue.Queue(),
            event=threading.Event(),
        )
        worker.current_task = None

        mock_task = MagicMock()
        worker.set_task(mock_task)

        self.assertEqual(worker.current_task, mock_task)
        self.assertFalse(worker.idle)
        self.assertEqual(worker.worker_log, [])

    @patch("unmanic.libs.workers.UnmanicLogging")
    def test_set_task_when_busy(self, mock_logging):
        """Test set_task does nothing when worker already has task."""
        from unmanic.libs.workers import Worker

        mock_logging.get_logger.return_value = MagicMock()

        worker = Worker(
            thread_id="main-0",
            name="Worker-1",
            worker_group_id=1,
            pending_queue=queue.Queue(),
            complete_queue=queue.Queue(),
            event=threading.Event(),
        )

        existing_task = MagicMock()
        worker.current_task = existing_task

        new_task = MagicMock()
        worker.set_task(new_task)

        # Should not change the current task
        self.assertEqual(worker.current_task, existing_task)


class TestWorkerGetStatus(unittest.TestCase):
    """Tests for Worker.get_status method."""

    @patch("unmanic.libs.workers.UnmanicLogging")
    def test_get_status_idle(self, mock_logging):
        """Test get_status when worker is idle."""
        from unmanic.libs.workers import Worker

        mock_logging.get_logger.return_value = MagicMock()

        worker = Worker(
            thread_id="main-0",
            name="Worker-1",
            worker_group_id=1,
            pending_queue=queue.Queue(),
            complete_queue=queue.Queue(),
            event=threading.Event(),
        )
        worker.worker_subprocess_monitor = None

        status = worker.get_status()

        self.assertEqual(status["id"], "main-0")
        self.assertEqual(status["name"], "Worker-1")
        self.assertTrue(status["idle"])
        self.assertIsNone(status["current_task"])
        self.assertEqual(status["current_file"], "")
        self.assertIsNone(status["gpu"])

    @patch("unmanic.libs.workers.UnmanicLogging")
    def test_get_status_with_task(self, mock_logging):
        """Test get_status when worker has a task."""
        from unmanic.libs.workers import Worker

        mock_logging.get_logger.return_value = MagicMock()

        worker = Worker(
            thread_id="main-0",
            name="Worker-1",
            worker_group_id=1,
            pending_queue=queue.Queue(),
            complete_queue=queue.Queue(),
            event=threading.Event(),
        )
        worker.worker_subprocess_monitor = None

        mock_task = MagicMock()
        mock_task.get_task_id.return_value = 123
        mock_task.get_source_basename.return_value = "test.mkv"
        worker.current_task = mock_task
        worker.idle = False
        worker.start_time = 1234567890.0

        status = worker.get_status()

        self.assertFalse(status["idle"])
        self.assertEqual(status["current_task"], 123)
        self.assertEqual(status["start_time"], "1234567890.0")

    @patch("unmanic.libs.workers.UnmanicLogging")
    def test_get_status_with_subprocess_monitor(self, mock_logging):
        """Test get_status includes subprocess stats."""
        from unmanic.libs.workers import Worker

        mock_logging.get_logger.return_value = MagicMock()

        worker = Worker(
            thread_id="main-0",
            name="Worker-1",
            worker_group_id=1,
            pending_queue=queue.Queue(),
            complete_queue=queue.Queue(),
            event=threading.Event(),
        )

        mock_monitor = MagicMock()
        # Implementation returns strings from get_subprocess_stats
        mock_monitor.get_subprocess_stats.return_value = {
            "pid": "12345",
            "percent": "50",
            "elapsed": "100",
        }
        worker.worker_subprocess_monitor = mock_monitor

        status = worker.get_status()

        self.assertEqual(status["subprocess"]["pid"], "12345")
        self.assertEqual(status["subprocess"]["percent"], "50")


class TestWorkerGPU(unittest.TestCase):
    """Tests for Worker GPU functionality."""

    @patch("unmanic.libs.workers.UnmanicLogging")
    def test_get_current_gpu_none(self, mock_logging):
        """Test get_current_gpu returns None when no GPU assigned."""
        from unmanic.libs.workers import Worker

        mock_logging.get_logger.return_value = MagicMock()

        worker = Worker(
            thread_id="main-0",
            name="Worker-1",
            worker_group_id=1,
            pending_queue=queue.Queue(),
            complete_queue=queue.Queue(),
            event=threading.Event(),
        )

        self.assertIsNone(worker.get_current_gpu())

    @patch("unmanic.libs.workers.UnmanicLogging")
    def test_get_current_gpu_assigned(self, mock_logging):
        """Test get_current_gpu returns assigned GPU."""
        from unmanic.libs.workers import Worker

        mock_logging.get_logger.return_value = MagicMock()

        worker = Worker(
            thread_id="main-0",
            name="Worker-1",
            worker_group_id=1,
            pending_queue=queue.Queue(),
            complete_queue=queue.Queue(),
            event=threading.Event(),
        )

        mock_gpu = MagicMock()
        mock_gpu.device_id = "0"
        worker.current_gpu = mock_gpu

        result = worker.get_current_gpu()

        self.assertEqual(result.device_id, "0")

    @patch("unmanic.libs.workers.UnmanicLogging")
    def test_get_status_includes_gpu(self, mock_logging):
        """Test get_status includes GPU info when assigned."""
        from unmanic.libs.workers import Worker

        mock_logging.get_logger.return_value = MagicMock()

        worker = Worker(
            thread_id="main-0",
            name="Worker-1",
            worker_group_id=1,
            pending_queue=queue.Queue(),
            complete_queue=queue.Queue(),
            event=threading.Event(),
        )
        worker.worker_subprocess_monitor = None

        mock_gpu = MagicMock()
        mock_gpu.to_dict.return_value = {"device_id": "0", "type": "CUDA"}
        worker.current_gpu = mock_gpu

        status = worker.get_status()

        self.assertEqual(status["gpu"]["device_id"], "0")
        self.assertEqual(status["gpu"]["type"], "CUDA")


class TestWorkerCommandError(unittest.TestCase):
    """Tests for WorkerCommandError exception."""

    def test_worker_command_error(self):
        """Test WorkerCommandError stores command."""
        from unmanic.libs.workers import WorkerCommandError

        error = WorkerCommandError("ffmpeg -i input.mkv")

        self.assertEqual(error.command, "ffmpeg -i input.mkv")
        self.assertIn("non 0 status", str(error))

    def test_worker_command_error_list(self):
        """Test WorkerCommandError with list command."""
        from unmanic.libs.workers import WorkerCommandError

        cmd = ["ffmpeg", "-i", "input.mkv", "-c", "copy", "output.mp4"]
        error = WorkerCommandError(cmd)

        self.assertEqual(error.command, cmd)


class TestWorkerPauseResume(unittest.TestCase):
    """Tests for Worker pause/resume functionality."""

    @patch("unmanic.libs.workers.UnmanicLogging")
    def test_worker_paused_flag(self, mock_logging):
        """Test Worker paused_flag starts cleared."""
        from unmanic.libs.workers import Worker

        mock_logging.get_logger.return_value = MagicMock()

        worker = Worker(
            thread_id="main-0",
            name="Worker-1",
            worker_group_id=1,
            pending_queue=queue.Queue(),
            complete_queue=queue.Queue(),
            event=threading.Event(),
        )

        self.assertFalse(worker.paused_flag.is_set())

    @patch("unmanic.libs.workers.UnmanicLogging")
    def test_worker_paused_status(self, mock_logging):
        """Test get_status reflects paused state."""
        from unmanic.libs.workers import Worker

        mock_logging.get_logger.return_value = MagicMock()

        worker = Worker(
            thread_id="main-0",
            name="Worker-1",
            worker_group_id=1,
            pending_queue=queue.Queue(),
            complete_queue=queue.Queue(),
            event=threading.Event(),
        )
        worker.worker_subprocess_monitor = None

        # Not paused
        status = worker.get_status()
        self.assertFalse(status["paused"])

        # Set paused
        worker.paused_flag.set()
        status = worker.get_status()
        self.assertTrue(status["paused"])


class TestWorkerRedundantFlag(unittest.TestCase):
    """Tests for Worker redundant_flag (termination signal)."""

    @patch("unmanic.libs.workers.UnmanicLogging")
    def test_redundant_flag_starts_cleared(self, mock_logging):
        """Test Worker redundant_flag starts cleared."""
        from unmanic.libs.workers import Worker

        mock_logging.get_logger.return_value = MagicMock()

        worker = Worker(
            thread_id="main-0",
            name="Worker-1",
            worker_group_id=1,
            pending_queue=queue.Queue(),
            complete_queue=queue.Queue(),
            event=threading.Event(),
        )

        self.assertFalse(worker.redundant_flag.is_set())

    @patch("unmanic.libs.workers.UnmanicLogging")
    def test_redundant_flag_can_be_set(self, mock_logging):
        """Test Worker redundant_flag can be set for termination."""
        from unmanic.libs.workers import Worker

        mock_logging.get_logger.return_value = MagicMock()

        worker = Worker(
            thread_id="main-0",
            name="Worker-1",
            worker_group_id=1,
            pending_queue=queue.Queue(),
            complete_queue=queue.Queue(),
            event=threading.Event(),
        )

        worker.redundant_flag.set()

        self.assertTrue(worker.redundant_flag.is_set())


if __name__ == "__main__":
    unittest.main()

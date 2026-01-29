#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    unmanic.libs.distributed_worker_monitor.py

    Monitors distributed workers for timeout and handles task recovery.
    Runs as a background thread to detect stale workers and reclaim their tasks.

    Written by:               TARS Modernization (Session 154)
    Date:                     29 Jan 2026

    Copyright:
           Copyright (C) Josh Sunnex - All Rights Reserved
           TARS Fork Modifications (C) 2026
"""

import threading
import time
from typing import List, Set

from unmanic.libs.logs import UnmanicLogging
from unmanic.libs.worker_auth import WorkerAuthManager
from unmanic.libs.taskqueue import TaskQueue


class DistributedWorkerMonitor(threading.Thread):
    """
    Background monitor for distributed workers.

    Responsibilities:
    - Detect workers that have missed heartbeats (timeout)
    - Reclaim tasks from dead/unresponsive workers
    - Clean up stale worker registrations
    - Provide worker health metrics
    """

    # Worker is considered dead after 5 minutes without heartbeat
    WORKER_TIMEOUT_SECONDS = 300

    # Task is considered abandoned after 30 minutes without status update
    TASK_TIMEOUT_SECONDS = 1800

    # Monitor runs every 60 seconds
    MONITOR_INTERVAL_SECONDS = 60

    def __init__(self, task_queue: TaskQueue):
        super(DistributedWorkerMonitor, self).__init__(name="DistributedWorkerMonitor")
        self.daemon = True
        self.task_queue = task_queue
        self.logger = UnmanicLogging.get_logger(name=self.__class__.__name__)
        self._stop_event = threading.Event()

        self.logger.info("DistributedWorkerMonitor initialized")

    def run(self) -> None:
        """Main monitor loop."""
        self.logger.info("DistributedWorkerMonitor started")

        while not self._stop_event.is_set():
            try:
                self._check_worker_timeouts()
                self._check_task_timeouts()
            except Exception as e:
                self.logger.error(f"Error in monitor loop: {str(e)}", exc_info=True)

            # Wait for next check interval (or stop event)
            self._stop_event.wait(self.MONITOR_INTERVAL_SECONDS)

        self.logger.info("DistributedWorkerMonitor stopped")

    def stop(self) -> None:
        """Stop the monitor thread."""
        self.logger.info("Stopping DistributedWorkerMonitor...")
        self._stop_event.set()

    def _check_worker_timeouts(self) -> None:
        """Check for workers that have missed heartbeats and mark them as inactive."""
        auth_manager = WorkerAuthManager()
        current_time = time.time()
        timeout_threshold = current_time - self.WORKER_TIMEOUT_SECONDS

        timed_out_workers: List[str] = []

        for worker_id, worker_info in auth_manager._workers.items():
            if not worker_info.active:
                continue  # Skip already inactive workers

            if worker_info.last_seen < timeout_threshold:
                # Worker has timed out
                worker_info.active = False
                timed_out_workers.append(worker_id)
                self.logger.warning(
                    f"Worker {worker_id} ({worker_info.name}) timed out. "
                    f"Last seen: {int(current_time - worker_info.last_seen)}s ago"
                )

        if timed_out_workers:
            # Save updated worker states
            auth_manager._save_workers()

            # Reclaim tasks from timed out workers
            self._reclaim_tasks_from_workers(timed_out_workers)

    def _check_task_timeouts(self) -> None:
        """
        Check for tasks that have been processing too long without status updates.
        This catches tasks from workers that died without proper cleanup.
        """
        # Get all in-progress tasks
        in_progress_tasks = self.task_queue.list_in_progress_tasks()
        current_time = time.time()
        timeout_threshold = current_time - self.TASK_TIMEOUT_SECONDS

        for task in in_progress_tasks:
            # Check if task has been processing for too long
            if hasattr(task, "start_time") and task.start_time:
                if task.start_time < timeout_threshold:
                    self.logger.warning(
                        f"Task {task.id} timed out after " f"{int(current_time - task.start_time)}s. Requeuing..."
                    )
                    self._requeue_task(task)

    def _reclaim_tasks_from_workers(self, worker_ids: List[str]) -> None:
        """
        Reclaim tasks that were assigned to dead workers.

        :param worker_ids: List of worker IDs that have timed out
        """
        # Get all in-progress tasks
        in_progress_tasks = self.task_queue.list_in_progress_tasks()

        for task in in_progress_tasks:
            # Check if task was assigned to a dead worker
            task_worker_id = getattr(task, "processed_by_worker", None)

            if task_worker_id in worker_ids:
                self.logger.info(f"Reclaiming task {task.id} from dead worker {task_worker_id}")
                self._requeue_task(task)

    def _requeue_task(self, task) -> None:
        """
        Requeue a task back to pending status.

        :param task: Task object to requeue
        """
        try:
            task.status = "pending"
            task.processed_by_worker = None  # Clear worker assignment
            task.start_time = None  # Clear start time
            task.save()

            self.logger.info(f"Task {task.id} requeued to pending")
        except Exception as e:
            self.logger.error(f"Failed to requeue task {task.id}: {str(e)}", exc_info=True)

    def get_active_workers_count(self) -> int:
        """Get count of currently active workers."""
        auth_manager = WorkerAuthManager()
        return sum(1 for w in auth_manager._workers.values() if w.active)

    def get_timed_out_workers(self) -> List[str]:
        """Get list of worker IDs that have timed out."""
        auth_manager = WorkerAuthManager()
        current_time = time.time()
        timeout_threshold = current_time - self.WORKER_TIMEOUT_SECONDS

        return [
            worker_id for worker_id, worker_info in auth_manager._workers.items() if worker_info.last_seen < timeout_threshold
        ]

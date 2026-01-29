#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    unmanic.webserver.api_v2.distributed_worker_api.py

    REST API for distributed worker management.
    Enables remote workers to claim tasks, report status, and manage lifecycle.

    Written by:               TARS Modernization (Session 154)
    Date:                     29 Jan 2026

    Copyright:
           Copyright (C) Josh Sunnex - All Rights Reserved
           TARS Fork Modifications (C) 2026
"""

import time
from typing import Any, Dict, List, Optional

import tornado.web

from unmanic.libs.worker_auth import (
    WorkerAuthManager,
    WorkerRole,
    require_worker_auth,
)
from unmanic.webserver.api_v2.base_api_handler import BaseApiHandler


class DistributedTaskClaimHandler(BaseApiHandler):
    """
    Handle task claiming by distributed workers.

    Endpoint: POST /api/v2/tasks/claim
    Auth: Required (WORKER role)

    Request Body:
    {
        "worker_id": "worker-uuid",
        "capabilities": ["video", "audio"],
        "max_tasks": 1
    }

    Response:
    {
        "success": true,
        "task": {
            "task_id": 123,
            "source_file": "/path/to/file.mp4",
            "cache_path": "/tmp/unmanic/cache_123",
            "settings": {...}
        }
    }
    """

    name = "distributed_task_claim"

    @require_worker_auth([WorkerRole.WORKER])
    async def post(self) -> None:
        """Claim a task for processing."""
        try:
            # Parse request body
            worker_id = self.get_json_body_item("worker_id", str, required=True)
            capabilities = self.get_json_body_item("capabilities", list, default=[])
            max_tasks = self.get_json_body_item("max_tasks", int, default=1)

            # Get foreman instance
            foreman = self.foreman
            if not foreman:
                self.build_response(
                    {
                        "success": False,
                        "error": "Foreman not available",
                    },
                    status_code=503,
                )
                return

            # Attempt to claim a task from the queue
            task_queue = foreman.task_queue
            if not task_queue:
                self.build_response(
                    {
                        "success": False,
                        "error": "Task queue not available",
                    },
                    status_code=503,
                )
                return

            # Get next pending task
            pending_tasks = task_queue.get_next_pending_tasks()
            if not pending_tasks:
                self.build_response(
                    {
                        "success": True,
                        "task": None,
                        "message": "No tasks available",
                    }
                )
                return

            # Claim the first task
            task = pending_tasks[0]

            # Mark task as claimed by this worker
            task_data = {
                "task_id": task.id,
                "source_file": task.abspath,
                "cache_path": task.cache_path,
                "settings": self._get_task_settings(task),
                "claimed_at": time.time(),
                "claimed_by": worker_id,
            }

            # Update task status to processing and assign to worker
            task.status = "processing"
            task.processed_by_worker = worker_id
            task.start_time = time.time()
            task.save()

            self.logger.info(f"Task {task.id} claimed by distributed worker {worker_id}")

            self.build_response(
                {
                    "success": True,
                    "task": task_data,
                }
            )

        except Exception as e:
            self.logger.error(f"Error claiming task: {str(e)}", exc_info=True)
            self.build_response(
                {
                    "success": False,
                    "error": str(e),
                },
                status_code=500,
            )

    def _get_task_settings(self, task) -> Dict[str, Any]:
        """Extract task-specific settings."""
        # TODO: Implement based on actual task model structure
        return {
            "library_id": getattr(task, "library_id", None),
            "priority": getattr(task, "priority", 0),
        }


class DistributedTaskStatusHandler(BaseApiHandler):
    """
    Handle task status updates from distributed workers.

    Endpoint: POST /api/v2/tasks/{task_id}/status
    Auth: Required (WORKER role)

    Request Body:
    {
        "worker_id": "worker-uuid",
        "status": "processing|completed|failed",
        "progress": 45.5,
        "message": "Processing...",
        "result": {...}  # For completed tasks
    }
    """

    name = "distributed_task_status"

    @require_worker_auth([WorkerRole.WORKER])
    async def post(self, task_id: str) -> None:
        """Update task status."""
        try:
            task_id_int = int(task_id)

            # Parse request body
            worker_id = self.get_json_body_item("worker_id", str, required=True)
            status = self.get_json_body_item("status", str, required=True)
            progress = self.get_json_body_item("progress", float, default=0.0)
            message = self.get_json_body_item("message", str, default="")
            result = self.get_json_body_item("result", dict, default=None)

            # Validate status
            valid_statuses = ["processing", "completed", "failed"]
            if status not in valid_statuses:
                self.build_response(
                    {
                        "success": False,
                        "error": f"Invalid status. Must be one of: {', '.join(valid_statuses)}",
                    },
                    status_code=400,
                )
                return

            # Get foreman and task queue
            foreman = self.foreman
            if not foreman or not foreman.task_queue:
                self.build_response(
                    {
                        "success": False,
                        "error": "Task queue not available",
                    },
                    status_code=503,
                )
                return

            # Find the task
            task = foreman.task_queue.get_task_by_id(task_id_int)
            if not task:
                self.build_response(
                    {
                        "success": False,
                        "error": f"Task {task_id} not found",
                    },
                    status_code=404,
                )
                return

            # Update task based on status
            if status == "completed":
                task.status = "complete"
                task.success = True
                if result:
                    # Store result data
                    task.finish_time = time.time()
            elif status == "failed":
                task.status = "failed"
                task.success = False
                task.error = message
            else:  # processing
                task.status = "processing"
                task.progress = progress

            task.save()

            self.logger.info(f"Task {task_id} status updated to {status} by worker {worker_id}")

            self.build_response(
                {
                    "success": True,
                    "message": f"Task {task_id} status updated to {status}",
                }
            )

        except ValueError:
            self.build_response(
                {
                    "success": False,
                    "error": "Invalid task_id",
                },
                status_code=400,
            )
        except Exception as e:
            self.logger.error(f"Error updating task status: {str(e)}", exc_info=True)
            self.build_response(
                {
                    "success": False,
                    "error": str(e),
                },
                status_code=500,
            )


class DistributedWorkerHeartbeatHandler(BaseApiHandler):
    """
    Handle worker heartbeat/health updates.

    Endpoint: POST /api/v2/workers/heartbeat
    Auth: Required (WORKER role)

    Request Body:
    {
        "worker_id": "worker-uuid",
        "status": "idle|busy|error",
        "current_tasks": [123, 456],
        "system_info": {
            "cpu_usage": 45.2,
            "memory_usage": 60.1,
            "disk_usage": 70.5
        }
    }
    """

    name = "distributed_worker_heartbeat"

    @require_worker_auth([WorkerRole.WORKER])
    async def post(self) -> None:
        """Update worker heartbeat."""
        try:
            # Parse request body
            worker_id = self.get_json_body_item("worker_id", str, required=True)
            status = self.get_json_body_item("status", str, default="idle")
            current_tasks = self.get_json_body_item("current_tasks", list, default=[])
            system_info = self.get_json_body_item("system_info", dict, default={})

            # Update worker info in auth manager
            auth_manager = WorkerAuthManager()
            worker = auth_manager.get_worker(worker_id)

            if not worker:
                self.build_response(
                    {
                        "success": False,
                        "error": f"Worker {worker_id} not registered",
                    },
                    status_code=404,
                )
                return

            # Update last_seen timestamp
            worker.last_seen = time.time()
            auth_manager._save_workers()

            self.logger.debug(f"Heartbeat received from worker {worker_id}: {status}")

            self.build_response(
                {
                    "success": True,
                    "message": "Heartbeat received",
                    "server_time": time.time(),
                }
            )

        except Exception as e:
            self.logger.error(f"Error processing heartbeat: {str(e)}", exc_info=True)
            self.build_response(
                {
                    "success": False,
                    "error": str(e),
                },
                status_code=500,
            )


# Route definitions for API router
ROUTES = [
    (r"/api/v2/tasks/claim", DistributedTaskClaimHandler),
    (r"/api/v2/tasks/([0-9]+)/status", DistributedTaskStatusHandler),
    (r"/api/v2/workers/heartbeat", DistributedWorkerHeartbeatHandler),
]

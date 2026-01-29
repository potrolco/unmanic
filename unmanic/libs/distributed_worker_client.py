#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    unmanic.libs.distributed_worker_client.py

    Python client library for distributed TARS workers.
    Handles authentication, task claiming, status reporting, and heartbeats.

    Written by:               TARS Modernization (Session 154)
    Date:                     29 Jan 2026

    Copyright:
           Copyright (C) Josh Sunnex - All Rights Reserved
           TARS Fork Modifications (C) 2026

    Usage Example:
        from unmanic.libs.distributed_worker_client import DistributedWorkerClient

        client = DistributedWorkerClient(
            server_url="http://tars-server:8888",
            worker_name="worker-01",
            worker_hostname="worker-node-01"
        )

        # Register and get token
        token = client.register()

        # Claim a task
        task = client.claim_task()
        if task:
            # Process task...
            client.update_task_status(task['task_id'], 'processing', progress=50.0)

            # Complete task
            client.update_task_status(task['task_id'], 'completed', result={...})

        # Send heartbeat
        client.heartbeat(status='idle')
"""

import logging
import time
from typing import Any, Dict, List, Optional

import requests


class DistributedWorkerClientError(Exception):
    """Base exception for worker client errors."""

    pass


class AuthenticationError(DistributedWorkerClientError):
    """Authentication failed."""

    pass


class APIError(DistributedWorkerClientError):
    """API request failed."""

    pass


class DistributedWorkerClient:
    """
    Client for distributed TARS workers.

    Provides high-level interface for:
    - Worker registration and authentication
    - Task claiming and status updates
    - Heartbeat management
    - Error handling and retries
    """

    def __init__(
        self,
        server_url: str,
        worker_name: str,
        worker_hostname: str,
        capabilities: Optional[List[str]] = None,
        logger: Optional[logging.Logger] = None,
    ):
        """
        Initialize worker client.

        :param server_url: TARS server URL (e.g., http://tars-server:8888)
        :param worker_name: Friendly name for this worker
        :param worker_hostname: Hostname where worker is running
        :param capabilities: List of worker capabilities (e.g., ['video', 'audio'])
        :param logger: Optional logger instance
        """
        self.server_url = server_url.rstrip("/")
        self.worker_name = worker_name
        self.worker_hostname = worker_hostname
        self.capabilities = capabilities or []
        self.logger = logger or logging.getLogger(__name__)

        self.worker_id: Optional[str] = None
        self.token: Optional[str] = None

        # HTTP session for connection pooling
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})

    def register(self, password: Optional[str] = None) -> str:
        """
        Register worker with TARS server and obtain JWT token.

        :param password: Optional password for registration
        :return: JWT token
        :raises AuthenticationError: If registration fails
        """
        url = f"{self.server_url}/api/v2/workers/register"
        payload = {
            "name": self.worker_name,
            "hostname": self.worker_hostname,
            "capabilities": self.capabilities,
        }

        if password:
            payload["password"] = password

        try:
            response = self.session.post(url, json=payload, timeout=30)
            response.raise_for_status()
            data = response.json()

            if not data.get("success"):
                raise AuthenticationError(f"Registration failed: {data.get('error', 'Unknown error')}")

            self.worker_id = data["worker_id"]
            self.token = data["token"]

            # Add token to session headers
            self.session.headers.update({"Authorization": f"Bearer {self.token}"})

            self.logger.info(f"Worker registered successfully: {self.worker_id}")
            return self.token

        except requests.RequestException as e:
            raise AuthenticationError(f"Registration request failed: {str(e)}")

    def claim_task(self, max_tasks: int = 1) -> Optional[Dict[str, Any]]:
        """
        Claim a task from the server queue.

        :param max_tasks: Maximum number of tasks to claim (currently only 1 supported)
        :return: Task data dict or None if no tasks available
        :raises APIError: If claim request fails
        """
        if not self.token:
            raise AuthenticationError("Not authenticated. Call register() first.")

        url = f"{self.server_url}/api/v2/tasks/claim"
        payload = {
            "worker_id": self.worker_id,
            "capabilities": self.capabilities,
            "max_tasks": max_tasks,
        }

        try:
            response = self.session.post(url, json=payload, timeout=30)
            response.raise_for_status()
            data = response.json()

            if not data.get("success"):
                raise APIError(f"Task claim failed: {data.get('error', 'Unknown error')}")

            task = data.get("task")
            if task:
                self.logger.info(f"Claimed task {task['task_id']}: {task['source_file']}")
            else:
                self.logger.debug("No tasks available")

            return task

        except requests.RequestException as e:
            raise APIError(f"Task claim request failed: {str(e)}")

    def update_task_status(
        self,
        task_id: int,
        status: str,
        progress: Optional[float] = None,
        message: Optional[str] = None,
        result: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """
        Update task status on the server.

        :param task_id: ID of the task to update
        :param status: Status ('processing', 'completed', 'failed')
        :param progress: Progress percentage (0-100)
        :param message: Optional status message
        :param result: Optional result data (for completed tasks)
        :return: True if update successful
        :raises APIError: If status update fails
        """
        if not self.token:
            raise AuthenticationError("Not authenticated. Call register() first.")

        url = f"{self.server_url}/api/v2/tasks/{task_id}/status"
        payload = {
            "worker_id": self.worker_id,
            "status": status,
        }

        if progress is not None:
            payload["progress"] = progress
        if message:
            payload["message"] = message
        if result:
            payload["result"] = result

        try:
            response = self.session.post(url, json=payload, timeout=30)
            response.raise_for_status()
            data = response.json()

            if not data.get("success"):
                raise APIError(f"Status update failed: {data.get('error', 'Unknown error')}")

            self.logger.debug(f"Task {task_id} status updated to {status}")
            return True

        except requests.RequestException as e:
            raise APIError(f"Status update request failed: {str(e)}")

    def heartbeat(
        self,
        status: str = "idle",
        current_tasks: Optional[List[int]] = None,
        system_info: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """
        Send heartbeat to server to indicate worker is alive.

        :param status: Worker status ('idle', 'busy', 'error')
        :param current_tasks: List of task IDs currently processing
        :param system_info: Optional system info (CPU, memory, disk usage)
        :return: True if heartbeat successful
        :raises APIError: If heartbeat fails
        """
        if not self.token:
            raise AuthenticationError("Not authenticated. Call register() first.")

        url = f"{self.server_url}/api/v2/workers/heartbeat"
        payload = {
            "worker_id": self.worker_id,
            "status": status,
            "current_tasks": current_tasks or [],
        }

        if system_info:
            payload["system_info"] = system_info

        try:
            response = self.session.post(url, json=payload, timeout=30)
            response.raise_for_status()
            data = response.json()

            if not data.get("success"):
                raise APIError(f"Heartbeat failed: {data.get('error', 'Unknown error')}")

            self.logger.debug(f"Heartbeat sent: {status}")
            return True

        except requests.RequestException as e:
            raise APIError(f"Heartbeat request failed: {str(e)}")

    def run_worker_loop(
        self,
        task_processor_func: callable,
        poll_interval: int = 10,
        heartbeat_interval: int = 60,
    ) -> None:
        """
        Run main worker loop: claim tasks, process, send heartbeats.

        :param task_processor_func: Callback function to process tasks
                                    Should accept task dict and return (success, result)
        :param poll_interval: Seconds between task claim attempts
        :param heartbeat_interval: Seconds between heartbeats
        """
        last_heartbeat = 0

        self.logger.info("Starting worker loop...")

        while True:
            try:
                # Send heartbeat if needed
                current_time = time.time()
                if current_time - last_heartbeat >= heartbeat_interval:
                    self.heartbeat(status="idle")
                    last_heartbeat = current_time

                # Try to claim a task
                task = self.claim_task()

                if task:
                    task_id = task["task_id"]
                    self.logger.info(f"Processing task {task_id}...")

                    try:
                        # Update status to processing
                        self.update_task_status(task_id, "processing", progress=0.0)

                        # Process task using provided function
                        success, result = task_processor_func(task)

                        # Update final status
                        if success:
                            self.update_task_status(task_id, "completed", progress=100.0, result=result)
                            self.logger.info(f"Task {task_id} completed successfully")
                        else:
                            self.update_task_status(
                                task_id,
                                "failed",
                                message=result.get("error", "Task failed"),
                            )
                            self.logger.error(f"Task {task_id} failed: {result}")

                    except Exception as e:
                        self.logger.error(f"Error processing task {task_id}: {str(e)}", exc_info=True)
                        self.update_task_status(task_id, "failed", message=f"Processing error: {str(e)}")

                else:
                    # No tasks available, wait before polling again
                    time.sleep(poll_interval)

            except KeyboardInterrupt:
                self.logger.info("Worker loop stopped by user")
                break
            except Exception as e:
                self.logger.error(f"Error in worker loop: {str(e)}", exc_info=True)
                time.sleep(poll_interval)

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
unmanic.taskqueue_factory.py

Factory for creating task queue backends based on configuration.
Supports 'sqlite' (default) and 'redis' (optional) backends.

Version: 1.0.0
Author:  JARVIS (Session 212, 2026-02-10)
"""

from unmanic.libs.logs import UnmanicLogging
from unmanic.libs.taskqueue_interface import TaskQueueInterface

logger = UnmanicLogging.get_logger("TaskQueueFactory")


def create_task_queue(data_queues, backend: str = "sqlite", **kwargs) -> TaskQueueInterface:
    """
    Create and return a task queue instance for the specified backend.

    :param data_queues: Shared data queues (passed to all backends).
    :param backend: Queue backend — 'sqlite' (default) or 'redis'.
    :param kwargs: Backend-specific configuration:
        For 'redis':
            redis_host (str): Redis hostname. Default: 'localhost'.
            redis_port (int): Redis port. Default: 6379.
            redis_db (int): Redis database number. Default: 0.
            redis_password (str|None): Redis auth password. Default: None.
            redis_max_connections (int): Connection pool size. Default: 50.
    :return: A TaskQueueInterface implementation.
    :raises ValueError: If backend is not recognized.
    :raises ImportError: If redis backend is selected but redis-py is not installed.
    """
    backend = backend.lower().strip()

    if backend == "sqlite":
        from unmanic.libs.taskqueue_sqlite import SQLiteTaskQueue

        logger.info("Initializing SQLite task queue backend")
        return SQLiteTaskQueue(data_queues)

    elif backend == "redis":
        try:
            from unmanic.libs.taskqueue_redis import RedisTaskQueue
        except ImportError as e:
            raise ImportError(
                "Redis task queue backend requires the 'redis' package. " "Install it with: pip install redis>=5.0.0"
            ) from e

        logger.info(
            "Initializing Redis task queue backend (host=%s, port=%s, db=%s)",
            kwargs.get("redis_host", "localhost"),
            kwargs.get("redis_port", 6379),
            kwargs.get("redis_db", 0),
        )
        return RedisTaskQueue(data_queues, **kwargs)

    else:
        raise ValueError(f"Unknown task queue backend: '{backend}'. " f"Supported backends: 'sqlite', 'redis'.")

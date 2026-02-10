#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    unmanic.taskqueue_interface.py

    Abstract Base Class defining the contract for all task queue backends.
    Implementations must handle task lifecycle: pending → in_progress → processed.

    The interface is intentionally backend-agnostic — no ORM types, no Redis types.
    All methods accept and return plain Python objects (dicts, lists, booleans).

    Implementations:
        - SQLiteTaskQueue  (taskqueue_sqlite.py) — default, uses Peewee ORM
        - RedisTaskQueue   (taskqueue_redis.py)  — optional, uses redis-py

    Version: 1.0.0
    Author:  JARVIS (Session 212, 2026-02-10)
    Review:  GPT-5 Adapter Pattern recommendation
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class TaskQueueInterface(ABC):
    """
    Abstract interface for task queue backends.

    All task queue implementations must subclass this and provide concrete
    implementations for every abstract method.

    Design principles:
        - Methods accept plain values (strings, ints, lists) — no ORM models.
        - Return types are dicts, lists, or booleans — no backend-specific objects.
        - The `task_item` parameter in mark_* methods is a backend-opaque handle
          returned by get_next_* methods. Each backend defines what this is internally.
    """

    # ──────────────────────────────────────────────
    # List operations
    # ──────────────────────────────────────────────

    @abstractmethod
    def list_pending_tasks(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Return a list of tasks with status 'pending'.

        :param limit: Maximum number of results. None = all.
        :return: List of task dicts sorted by priority (descending).
        """

    @abstractmethod
    def list_in_progress_tasks(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Return a list of tasks with status 'in_progress'.

        :param limit: Maximum number of results. None = all.
        :return: List of task dicts.
        """

    @abstractmethod
    def list_processed_tasks(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Return a list of tasks with status 'processed'.

        :param limit: Maximum number of results. None = all.
        :return: List of task dicts.
        """

    # ──────────────────────────────────────────────
    # Claim / fetch operations
    # ──────────────────────────────────────────────

    @abstractmethod
    def get_next_pending_tasks(
        self,
        local_only: bool = False,
        library_names: Optional[List[str]] = None,
        library_tags: Optional[List[str]] = None,
    ) -> Any:
        """
        Claim the next pending task matching the given filters.

        This is the primary task-dispatch method. The returned object is a
        backend-opaque task handle that can be passed to mark_item_in_progress()
        and mark_item_as_processed().

        :param local_only: If True, only return tasks with type='local'.
        :param library_names: Filter by library name membership.
        :param library_tags: Filter by tag membership.
        :return: A task handle, or False/None if no matching task exists.
        """

    @abstractmethod
    def get_next_processed_tasks(self) -> Any:
        """
        Claim the next task with status 'processed' for post-processing.

        :return: A task handle, or False/None if no processed task exists.
        """

    # ──────────────────────────────────────────────
    # Status mutations
    # ──────────────────────────────────────────────

    @abstractmethod
    def mark_item_in_progress(self, task_item: Any) -> Any:
        """
        Set a task's status to 'in_progress'.

        :param task_item: Task handle returned by get_next_pending_tasks().
        :return: The updated task handle.
        """

    @abstractmethod
    def mark_item_as_processed(self, task_item: Any) -> Any:
        """
        Set a task's status to 'processed'.

        :param task_item: Task handle returned by get_next_pending_tasks().
        :return: The updated task handle.
        """

    # ──────────────────────────────────────────────
    # Emptiness checks
    # ──────────────────────────────────────────────

    @abstractmethod
    def task_list_pending_is_empty(self) -> bool:
        """Return True if no pending tasks exist."""

    @abstractmethod
    def task_list_in_progress_is_empty(self) -> bool:
        """Return True if no in-progress tasks exist."""

    @abstractmethod
    def task_list_processed_is_empty(self) -> bool:
        """Return True if no processed tasks exist."""

    # ──────────────────────────────────────────────
    # Queue management
    # ──────────────────────────────────────────────

    @abstractmethod
    def requeue_tasks_at_bottom(self, task_id: int) -> bool:
        """
        Move a task to the bottom of the priority queue.

        Used when a task cannot be processed (e.g., remote worker unavailable)
        and should be retried later with lower priority.

        :param task_id: The task's database ID.
        :return: True on success.
        """

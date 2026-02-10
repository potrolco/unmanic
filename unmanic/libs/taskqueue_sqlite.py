#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
unmanic.taskqueue_sqlite.py

SQLite-backed implementation of TaskQueueInterface.
This is the default backend — preserves all existing behavior from the
original TaskQueue class using Peewee ORM.

Version: 1.0.0
Author:  JARVIS (Session 212, 2026-02-10)
"""

from typing import Any, Dict, List, Optional

from unmanic.libs import task
from unmanic.libs import common
from unmanic.libs.logs import UnmanicLogging
from unmanic.libs.taskqueue_interface import TaskQueueInterface
from unmanic.libs.unmodels import Libraries, LibraryTags, Tags
from unmanic.libs.unmodels.tasks import Tasks


class SQLiteTaskQueue(TaskQueueInterface):
    """
    SQLite-backed task queue using Peewee ORM.

    This is a direct refactor of the original TaskQueue class. All behavior
    is preserved — the only change is implementing the TaskQueueInterface ABC.
    """

    def __init__(self, data_queues):
        self.name = "SQLiteTaskQueue"
        self.data_queues = data_queues
        self.logger = UnmanicLogging.get_logger(name=self.__class__.__name__)

        # Sort fields
        self.sort_by = Tasks.priority
        self.sort_order = "desc"

    def _log(self, message, message2="", level="info"):
        message = common.format_message(message, message2)
        getattr(self.logger, level)(message)

    # ──────────────────────────────────────────────
    # Private Peewee helpers (formerly module-level)
    # ──────────────────────────────────────────────

    @staticmethod
    def _build_tasks_count_query(status: str) -> int:
        """
        Return count of tasks matching the given status.
        Limits to 1 for efficiency — we only need to know if any exist.
        """
        query = Tasks.select().where(Tasks.status == status).limit(1)
        return query.count()

    @staticmethod
    def _build_tasks_query(
        status: str,
        sort_by="id",
        sort_order: str = "asc",
        local_only: bool = False,
        library_names: Optional[List[str]] = None,
        library_tags: Optional[List[str]] = None,
    ):
        """
        Return the first task matching status with optional filters.
        Handles JOINs to Libraries and Tags tables for filtering.
        """
        query = Tasks.select().where(Tasks.status == status)

        if local_only:
            query = query.where(Tasks.type == "local")

        query = query.join(Libraries, on=(Libraries.id == Tasks.library_id))

        if library_names is not None:
            query = query.where(Libraries.name.in_(library_names))

        if library_tags is not None:
            query = query.join(LibraryTags, join_type="LEFT OUTER JOIN")
            query = query.join(Tags, join_type="LEFT OUTER JOIN")
            if library_tags:
                query = query.where(Tags.name.in_(library_tags))
            else:
                # Empty list = match only libraries with no tags
                query = query.where(Tags.name.is_null())

        query = query.limit(1)
        if sort_order == "asc":
            query = query.order_by(sort_by.asc())
        else:
            query = query.order_by(sort_by.desc())

        return query.first()

    @staticmethod
    def _build_tasks_query_full_list(
        status: str,
        sort_by="id",
        sort_order: str = "asc",
        limit: Optional[int] = None,
    ):
        """
        Return all tasks matching status, sorted and optionally limited.
        Returns query results as dicts.
        """
        query = Tasks.select(Tasks).where(Tasks.status == status)

        if sort_order == "asc":
            query = query.order_by(sort_by.asc())
        else:
            query = query.order_by(sort_by.desc())

        if limit:
            query = query.limit(limit)

        return query.dicts()

    def _fetch_next_task_filtered(
        self,
        status: str,
        sort_by=None,
        sort_order: str = "asc",
        local_only: bool = False,
        library_names: Optional[List[str]] = None,
        library_tags: Optional[List[str]] = None,
    ):
        """
        Fetch next task matching filters and return a Task wrapper object.
        Returns False if no matching task found.
        """
        if sort_by is None:
            sort_by = self.sort_by

        task_item = self._build_tasks_query(
            status,
            sort_by=sort_by,
            sort_order=sort_order,
            local_only=local_only,
            library_names=library_names,
            library_tags=library_tags,
        )
        if not task_item:
            return False

        next_task = task.Task()
        next_task.read_and_set_task_by_absolute_path(task_item.abspath)
        return next_task

    # ──────────────────────────────────────────────
    # TaskQueueInterface implementation
    # ──────────────────────────────────────────────

    def list_pending_tasks(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        results = self._build_tasks_query_full_list("pending", self.sort_by, self.sort_order, limit)
        return list(results) if results else []

    def list_in_progress_tasks(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        results = self._build_tasks_query_full_list("in_progress", self.sort_by, self.sort_order, limit)
        return list(results) if results else []

    def list_processed_tasks(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        results = self._build_tasks_query_full_list("processed", self.sort_by, self.sort_order, limit)
        return list(results) if results else []

    def get_next_pending_tasks(
        self,
        local_only: bool = False,
        library_names: Optional[List[str]] = None,
        library_tags: Optional[List[str]] = None,
    ) -> Any:
        return self._fetch_next_task_filtered(
            "pending",
            sort_by=self.sort_by,
            sort_order=self.sort_order,
            local_only=local_only,
            library_names=library_names,
            library_tags=library_tags,
        )

    def get_next_processed_tasks(self) -> Any:
        return self._fetch_next_task_filtered(
            "processed",
            sort_by=self.sort_by,
            sort_order=self.sort_order,
        )

    @staticmethod
    def mark_item_in_progress(task_item: Any) -> Any:
        task_item.set_status("in_progress")
        return task_item

    @staticmethod
    def mark_item_as_processed(task_item: Any) -> Any:
        task_item.set_status("processed")
        return task_item

    def task_list_pending_is_empty(self) -> bool:
        return self._build_tasks_count_query("pending") == 0

    def task_list_in_progress_is_empty(self) -> bool:
        return self._build_tasks_count_query("in_progress") == 0

    def task_list_processed_is_empty(self) -> bool:
        return self._build_tasks_count_query("processed") == 0

    def get_task_by_id(self, task_id: int) -> Any:
        try:
            return Tasks.get(Tasks.id == task_id)
        except Tasks.DoesNotExist:
            return None

    def requeue_tasks_at_bottom(self, task_id: int) -> bool:
        task_handler = task.Task()
        return task_handler.reorder_tasks([task_id], "bottom")

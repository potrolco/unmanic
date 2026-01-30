#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    unmanic.task.py

    Written by:               Josh.5 <jsunnex@gmail.com>
    Date:                     27 Apr 2019, (2:08 PM)

    Copyright:
           Copyright (C) Josh Sunnex - All Rights Reserved

           Permission is hereby granted, free of charge, to any person obtaining a copy
           of this software and associated documentation files (the "Software"), to deal
           in the Software without restriction, including without limitation the rights
           to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
           copies of the Software, and to permit persons to whom the Software is
           furnished to do so, subject to the following conditions:

           The above copyright notice and this permission notice shall be included in all
           copies or substantial portions of the Software.

           THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
           EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
           MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
           IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
           DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
           OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE
           OR OTHER DEALINGS IN THE SOFTWARE.

"""
import json
import os
import shutil
import threading
import time
from copy import deepcopy
from operator import attrgetter
from typing import Any, Dict, List, Optional, Union

from playhouse.shortcuts import model_to_dict

from unmanic import config
from unmanic.libs import common
from unmanic.libs.library import Library
from unmanic.libs.logs import UnmanicLogging
from peewee import IntegrityError
from unmanic.libs.unmodels.tasks import Tasks


def prepare_file_destination_data(pathname: str, file_extension: str) -> Dict[str, str]:
    """
    Prepare file destination data dictionary.

    Args:
        pathname: Original file path
        file_extension: New file extension

    Returns:
        Dictionary with 'basename' and 'abspath' keys
    """
    basename = os.path.basename(pathname)
    dirname = os.path.dirname(os.path.abspath(pathname))
    # Fetch the file's name without the file extension (this is going to be reset)
    file_name_without_extension = os.path.splitext(basename)[0]

    # Set destination dict
    basename = "{}.{}".format(file_name_without_extension, file_extension)
    abspath = os.path.join(dirname, basename)
    file_data = {"basename": basename, "abspath": abspath}

    return file_data


class Task:
    """
    Task

    Contains the stage and all data pertaining to a transcode task.
    """

    def __init__(self) -> None:
        self.name: str = "Task"
        self.task: Optional[Tasks] = None
        self.task_dict: Optional[Dict[str, Any]] = None
        self.settings = config.Config()
        self.logger = UnmanicLogging.get_logger(name=self.__class__.__name__)
        self.statistics: Dict[str, Any] = {}
        self.errors: List[str] = []

    def set_cache_path(self, cache_directory: Optional[str] = None, file_extension: Optional[str] = None) -> None:
        """Set the cache path for task output.

        IMPORTANT: If cache_path already exists and cache_directory is provided,
        this preserves the existing random suffix to prevent filename mismatch bugs.
        Only the file extension will be updated in that case.

        Bug fix: Previously, calling set_cache_path() after transcode completion would
        regenerate the random suffix, causing the post-processor to look for a different
        filename than what ffmpeg actually created, resulting in infinite retry loops.
        """
        if not self.task:
            raise Exception("Unable to set cache path. Task has not been set!")

        # Fetch the file's name without the file extension (this is going to be reset)
        split_file_name = os.path.splitext(self.get_source_basename())
        file_name_without_extension = split_file_name[0]

        if not file_extension:
            # Get file extension
            file_extension = split_file_name[1].lstrip(".")

        # FIX: If cache_path already exists and we're just updating the extension,
        # preserve the existing random suffix instead of generating a new one.
        # This prevents filename mismatch between worker output and post-processor expectation.
        if self.task.cache_path and cache_directory:
            # Extract existing filename and preserve its random suffix
            existing_basename = os.path.basename(self.task.cache_path)
            existing_name_without_ext = os.path.splitext(existing_basename)[0]
            # Update only the extension, keep the same name with random suffix
            out_file = "{}.{}".format(existing_name_without_ext, file_extension)
            self.task.cache_path = os.path.join(cache_directory, out_file)
            return

        # Generate new random string only for fresh cache paths (initial task creation)
        random_string = "{}-{}".format(common.random_string(), int(time.time()))
        out_file = "{}-{}.{}".format(file_name_without_extension, random_string, file_extension)
        if not cache_directory:
            out_folder = "unmanic_file_conversion-{}".format(random_string)
            cache_directory = os.path.join(self.settings.get_cache_path(), out_folder)

        # Set cache path class attribute
        self.task.cache_path = os.path.join(cache_directory, out_file)

    def get_cache_path(self) -> str:
        """Get the cache path for task output."""
        if not self.task:
            raise Exception("Unable to fetch cache path. Task has not been set!")
        if not self.task.cache_path:
            raise Exception("Unable to fetch cache path. Task cache path has not been set!")
        return self.task.cache_path

    def get_task_data(self) -> Dict[str, Any]:
        """Get task data as dictionary."""
        if not self.task:
            raise Exception("Unable to fetch task dictionary. Task has not been set!")
        self.task_dict = model_to_dict(self.task, backrefs=True)
        return self.task_dict

    def get_task_id(self) -> int:
        """Get task ID."""
        if not self.task:
            raise Exception("Unable to fetch task ID. Task has not been set!")
        return self.task.id

    def get_task_type(self) -> str:
        """Get task type."""
        if not self.task:
            raise Exception("Unable to fetch task type. Task has not been set!")
        return self.task.type

    def get_task_library_id(self) -> int:
        """Get task library ID."""
        if not self.task:
            raise Exception("Unable to fetch task library ID. Task has not been set!")
        return self.task.library_id

    def get_task_library_name(self) -> str:
        """Get task library name."""
        if not self.task:
            raise Exception("Unable to fetch task library ID. Task has not been set!")
        library = Library(self.task.library_id)
        return library.get_name()

    def get_task_library_priority_score(self) -> int:
        """Get task library priority score."""
        if not self.task:
            raise Exception("Unable to fetch task library ID. Task has not been set!")
        library = Library(self.task.library_id)
        return library.get_priority_score()

    def get_destination_data(self) -> Dict[str, str]:
        """Get destination file data."""
        if not self.task:
            raise Exception("Unable to fetch destination data. Task has not been set!")

        cache_path = self.get_cache_path()

        # Get the current cache path's file extension
        split_file_name = os.path.splitext(os.path.basename(cache_path))
        file_extension = split_file_name[1].lstrip(".")

        return prepare_file_destination_data(self.task.abspath, file_extension)

    def get_source_data(self) -> Dict[str, str]:
        """Get source file data."""
        if not self.task:
            raise Exception("Unable to fetch source absolute path. Task has not been set!")
        if not self.task.abspath:
            raise Exception("Unable to fetch source absolute path. Task absolute path has not been set!")
        return {
            "abspath": self.task.abspath,
            "basename": os.path.basename(self.task.abspath),
        }

    def get_source_basename(self) -> Optional[str]:
        """Get source file basename."""
        return self.get_source_data().get("basename")

    def get_source_abspath(self) -> Optional[str]:
        """Get source file absolute path."""
        return self.get_source_data().get("abspath")

    def get_task_success(self) -> bool:
        """Get task success status."""
        if not self.task:
            raise Exception("Unable to fetch task success. Task has not been set!")
        return self.task.success

    def get_start_time(self) -> float:
        """Get task start time."""
        if not self.task:
            raise Exception("Unable to fetch task start time. Task has not been set!")
        return self.task.start_time

    def get_finish_time(self) -> float:
        """Get task finish time."""
        if not self.task:
            raise Exception("Unable to fetch task finish time. Task has not been set!")
        return self.task.finish_time

    def task_dump(self) -> Dict[str, Any]:
        """Generate a copy of this task as a dictionary."""
        task_dict = {
            "task_label": self.get_source_basename(),
            "abspath": self.get_source_abspath(),
            "task_success": self.task.success,
            "start_time": self.task.start_time,
            "finish_time": self.task.finish_time,
            "processed_by_worker": self.task.processed_by_worker,
            "errors": self.errors,
            "log": self.task.log,
        }
        return task_dict

    def read_and_set_task_by_absolute_path(self, abspath: str) -> None:
        """
        Set the task by its absolute path.

        If the task already exists in the list, then return that task.
        If the task does not yet exist in the list, create it first.

        Args:
            abspath: Absolute path to the file
        """
        # Get task matching the abspath
        self.task = Tasks.get(abspath=abspath)

    def create_task_by_absolute_path(
        self,
        abspath: str,
        task_type: str = "local",
        library_id: int = 1,
        priority_score: int = 0,
    ) -> bool:
        """
        Create a task by its absolute path.

        If the task already exists in the list, then this will throw an exception
        and return False.

        Args:
            abspath: Absolute path to the file
            task_type: Type of task ('local' or 'remote')
            library_id: ID of the library
            priority_score: Priority score offset

        Returns:
            True if task created successfully, False otherwise
        """
        try:
            self.task = Tasks.create(abspath=abspath, status="creating", library_id=library_id)
            self.save()
            self.logger.debug("Created new task with ID: %s for %s", self.task, abspath)

            # Set the cache path to use during the transcoding
            self.set_cache_path()

            # Fetch the library priority score also for this task
            library_priority_score = self.get_task_library_priority_score()

            # Set the default priority to the ID of the task
            self.task.priority = int(self.task.id) + int(library_priority_score) + int(priority_score)

            # Set the task type
            self.task.type = task_type

            # Only local tasks should be progressed automatically
            # Remote tasks need to be progressed to pending by a remote trigger
            if task_type == "local":
                # Now set the status to pending. Only then will it be picked up by a worker.
                # This will also save the task.
                self.set_status("pending")
            else:
                # Save the tasks updates without settings status to pending
                self.save()

            return True
        except IntegrityError as e:
            self.logger.info("Cancel creating new task for %s - %s", abspath, e)
            return False

    def set_status(self, status: str) -> None:
        """
        Set the task status.

        Args:
            status: One of 'pending', 'in_progress', 'processed', or 'complete'

        Raises:
            Exception: If status is invalid or task not set
        """
        allowed = ["pending", "in_progress", "processed", "complete"]
        if status not in allowed:
            raise Exception('Unable to set status to "{}". Status must be one of [{}].'.format(status, ", ".join(allowed)))
        if not self.task:
            raise Exception("Unable to set status. Task has not been set!")
        self.task.status = status
        self.save()
        if status == "complete":
            TaskDataStore.clear_task(self.task.id)

    def set_success(self, success: bool) -> None:
        """
        Set the task success flag.

        Args:
            success: True for success, False for failure
        """
        if not self.task:
            raise Exception("Unable to set status. Task has not been set!")
        if success:
            self.task.success = True
        else:
            self.task.success = False
        self.save()

    def modify_path(self, new_path: str) -> None:
        """
        Modify the abspath attribute of this task.

        Args:
            new_path: New absolute path for the task
        """
        if not self.task:
            raise Exception("Unable to update abspath. Task has not been set!")
        self.task.abspath = new_path
        self.save()

    def save_command_log(self, log: List[str]) -> None:
        """
        Append to the task command log.

        Args:
            log: List of log lines to append
        """
        if not self.task:
            raise Exception("Unable to set status. Task has not been set!")
        self.task.log += "".join(log)
        self.save()

    def save(self) -> None:
        """Save the task model object to database."""
        if not self.task:
            raise Exception("Unable to save Task. Task has not been set!")
        self.task.save()

    def delete(self) -> None:
        """Delete the task model object from database."""
        if not self.task:
            raise Exception("Unable to save Task. Task has not been set!")
        TaskDataStore.clear_task(self.task.id)
        self.task.delete_instance()

    def get_total_task_list_count(self) -> int:
        """Get total count of tasks."""
        task_query = Tasks.select().order_by(Tasks.id.desc())
        return task_query.count()

    def get_task_list_filtered_and_sorted(
        self,
        order: Optional[Dict[str, str]] = None,
        start: int = 0,
        length: Optional[int] = None,
        search_value: Optional[str] = None,
        id_list: Optional[List[int]] = None,
        status: Optional[str] = None,
        task_type: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Get filtered and sorted task list.

        Args:
            order: Dict with 'column' and 'dir' keys for sorting
            start: Offset for pagination
            length: Limit for pagination
            search_value: Search string for abspath filtering
            id_list: List of task IDs to filter
            status: Status to filter by
            task_type: Task type to filter by

        Returns:
            List of task dictionaries
        """
        try:
            query = Tasks.select()

            if id_list:
                query = query.where(Tasks.id.in_(id_list))

            if search_value:
                query = query.where(Tasks.abspath.contains(search_value))

            if status:
                query = query.where(Tasks.status.in_([status]))

            if task_type:
                query = query.where(Tasks.type.in_([task_type]))

            # Get order by
            order_by = None
            if order:
                if order.get("dir") == "asc":
                    order_by = attrgetter(order.get("column"))(Tasks).asc()
                else:
                    order_by = attrgetter(order.get("column"))(Tasks).desc()

            if order_by and length:
                query = query.order_by(order_by).limit(length).offset(start)

        except Tasks.DoesNotExist:
            # No task entries exist yet
            self.logger.warning("No tasks exist yet.")
            query = []

        return query.dicts()

    def delete_tasks_recursively(self, id_list: List[int]) -> Optional[bool]:
        """
        Delete a given list of tasks based on their IDs.

        Args:
            id_list: List of task IDs to delete

        Returns:
            True if successful, False on error, None if no tasks exist
        """
        # Prevent running if no list of IDs was given
        if not id_list:
            return False

        try:
            query = Tasks.select()

            if id_list:
                query = query.where(Tasks.id.in_(id_list))

            for task_id in query:
                try:
                    # Remote tasks need to be cleaned up from the cache partition also
                    if task_id.type == "remote":
                        remote_task_dirname = task_id.abspath
                        if os.path.exists(task_id.abspath) and "unmanic_remote_pending_library" in remote_task_dirname:
                            self.logger.info("Removing remote pending library task '%s'.", remote_task_dirname)
                            shutil.rmtree(os.path.dirname(remote_task_dirname))

                    TaskDataStore.clear_task(task_id.id)
                    task_id.delete_instance(recursive=True)
                except Exception as e:
                    # Catch delete exceptions
                    self.logger.exception("An error occurred while deleting task ID: %s. %s", task_id, e)
                    return False

            return True

        except Tasks.DoesNotExist:
            # No task entries exist yet
            self.logger.warning("No tasks currently exist.")
            return None

    def reorder_tasks(self, id_list: List[int], direction: str) -> int:
        """
        Reorder tasks by adjusting their priority.

        Args:
            id_list: List of task IDs to reorder
            direction: 'top' to move to top, anything else moves to bottom

        Returns:
            Number of tasks updated
        """
        # Get the task with the highest ID
        order = {
            "column": "priority",
            "dir": "desc",
        }
        pending_task_results = self.get_task_list_filtered_and_sorted(
            order=order, start=0, length=1, search_value=None, id_list=None, status=None
        )

        task_top_priority = 1
        for pending_task_result in pending_task_results:
            task_top_priority = pending_task_result.get("priority")
            break

        # Add 500 to that number to offset it above all others.
        new_priority_offset = int(task_top_priority) + 500

        # Update the list of tasks by ID from the database adding the priority offset to their current priority
        # If the direction is to send it to the bottom, then set the priority as 0
        query = Tasks.update(priority=Tasks.priority + new_priority_offset if (direction == "top") else 0).where(
            Tasks.id.in_(id_list)
        )
        return query.execute()

    @staticmethod
    def set_tasks_status(id_list: List[int], status: str) -> int:
        """
        Update the task status for a given list of tasks by ID.

        Args:
            id_list: List of task IDs to update
            status: New status value

        Returns:
            Number of tasks updated
        """
        query = Tasks.update(status=status).where(Tasks.id.in_(id_list))
        result = query.execute()
        if status == "complete" and id_list:
            for task_id in id_list:
                TaskDataStore.clear_task(task_id)
        return result

    @staticmethod
    def set_tasks_library_id(id_list: List[int], library_id: int) -> int:
        """
        Update the task library_id for a given list of tasks by ID.

        Args:
            id_list: List of task IDs to update
            library_id: New library ID

        Returns:
            Number of tasks updated
        """
        query = Tasks.update(library_id=library_id).where(Tasks.id.in_(id_list))
        return query.execute()


class TaskDataStore:
    """
    Thread-safe in-memory store for task lifecycle data, shared across all plugins and threads.

    There are two separate stores:

    1. Runner State (immutable)
       - Stores data emitted by individual plugin runners.
       - Once a key is set under a (task_id, plugin_id, runner), it cannot be overwritten.
       - Structure:
           {
               task_id: {
                   plugin_id: {
                       runner_function_name: {
                           key: value,
                           ...
                       },
                       ...
                   },
                   ...
               },
               ...
           }
       - Example:
           {
               42: {
                   "video_file_tester": {
                       "on_worker_process": {
                           "ffprobe": {
                               "streams": [...],
                               "format": {...}
                           }
                       }
                   }
               }
           }

    2. Task State (mutable)
       - Stores arbitrary state values for a task that plugins may update freely.
       - Structure:
           {
               task_id: {
                   key: value,
                   ...
               },
               ...
           }
       - Example:
           {
               42: {
                   "progress": 0.75,
                   "status": "running"
               }
           }
    """

    _runner_state: Dict[int, Dict[str, Dict[str, Dict[str, Any]]]] = {}
    _task_state: Dict[int, Dict[str, Any]] = {}
    _lock: threading.RLock = threading.RLock()
    _ctx: threading.local = threading.local()

    @classmethod
    def clear_task(cls, task_id: int) -> None:
        """
        Remove all cached state for the given task ID.

        Args:
            task_id: Integer ID of the task to purge.
        """
        with cls._lock:
            cls._runner_state.pop(task_id, None)
            cls._task_state.pop(task_id, None)

    @classmethod
    def bind_runner_context(cls, task_id: int, plugin_id: str, runner: str) -> None:
        """
        Bind the current thread's runner context.

        Must be called before a plugin runner executes so that
        set_runner_value / get_runner_value know which (task_id, plugin_id, runner)
        to use.

        Args:
            task_id: Integer ID of the task being processed.
            plugin_id: String identifier of the plugin.
            runner: String name of the runner function.
        """
        cls._ctx.task_id = task_id
        cls._ctx.plugin_id = plugin_id
        cls._ctx.runner = runner

    @classmethod
    def clear_context(cls) -> None:
        """
        Clear the current thread's runner context.

        Should be called after the plugin runner completes.
        """
        cls._ctx.task_id = None
        cls._ctx.plugin_id = None
        cls._ctx.runner = None

    @classmethod
    def set_runner_value(cls, key: str, value: Any) -> bool:
        """
        Store an immutable value under the bound (task_id, plugin_id, runner).

        Args:
            key: String key to identify the data.
            value: Any JSON-serializable Python object to store.

        Returns:
            True if stored successfully, False if that key already exists.

        Raises:
            RuntimeError: if no runner context is bound.
        """
        tid = getattr(cls._ctx, "task_id", None)
        pid = getattr(cls._ctx, "plugin_id", None)
        run = getattr(cls._ctx, "runner", None)
        if None in (tid, pid, run):
            raise RuntimeError("Runner context not bound")
        with cls._lock:
            task_map = dict(cls._runner_state.get(tid, {}))
            plugin_map = dict(task_map.get(pid, {}))
            runner_map = dict(plugin_map.get(run, {}))
            if key in runner_map:
                return False
            runner_map[key] = deepcopy(value)
            plugin_map[run] = runner_map
            task_map[pid] = plugin_map
            cls._runner_state[tid] = task_map
            return True

    @classmethod
    def get_runner_value(
        cls,
        key: str,
        default: Any = None,
        *,
        plugin_id: Optional[str] = None,
        runner: Optional[str] = None,
    ) -> Any:
        """
        Retrieve an immutable runner value by key.

        Args:
            key: String key to retrieve.
            default: Value to return if key is not found.
            plugin_id: (optional) override plugin identifier.
            runner: (optional) override runner name.

        Returns:
            The stored value or default.

        Raises:
            RuntimeError: if context not bound and no override provided.
        """
        tid = getattr(cls._ctx, "task_id", None)
        if tid is None:
            raise RuntimeError("Runner context not bound")

        pid = plugin_id if plugin_id is not None else getattr(cls._ctx, "plugin_id", None)
        run = runner if runner is not None else getattr(cls._ctx, "runner", None)
        if None in (pid, run):
            raise RuntimeError("Runner context not fully bound and no override provided")

        with cls._lock:
            return cls._runner_state.get(tid, {}).get(pid, {}).get(run, {}).get(key, default)

    @classmethod
    def set_task_state(cls, key: str, value: Any, task_id: Optional[int] = None) -> None:
        """
        Store or overwrite a mutable value for a task.

        Args:
            key: Identifier for the state.
            value: JSON-serializable object.
            task_id: Optional task ID; if omitted, uses bound runner context.

        Raises:
            RuntimeError: if no task_id provided and no context bound.
        """
        tid = task_id if task_id is not None else getattr(cls._ctx, "task_id", None)
        if tid is None:
            raise RuntimeError("Task ID not provided or bound")
        with cls._lock:
            existing = cls._task_state.get(tid, {})
            new_t = dict(existing)
            new_t[key] = value
            cls._task_state[tid] = new_t

    @classmethod
    def get_task_state(cls, key: str, default: Any = None, task_id: Optional[int] = None) -> Any:
        """
        Retrieve a mutable task value by key.

        Args:
            key: Identifier to fetch.
            default: Returned if key missing.
            task_id: Optional task ID; if omitted, uses bound runner context.

        Returns:
            Stored value or default.

        Raises:
            RuntimeError: if no task_id provided and no context bound.
        """
        tid = task_id if task_id is not None else getattr(cls._ctx, "task_id", None)
        if tid is None:
            raise RuntimeError("Task ID not provided or bound")
        with cls._lock:
            return cls._task_state.get(tid, {}).get(key, default)

    @classmethod
    def delete_task_state(cls, key: str, task_id: Optional[int] = None) -> None:
        """
        Delete a mutable key for a given task.

        Args:
            key: Identifier to remove.
            task_id: Optional task ID; if omitted, uses bound runner context.

        Raises:
            RuntimeError: if no task_id provided and no context bound.
        """
        tid = task_id if task_id is not None else getattr(cls._ctx, "task_id", None)
        if tid is None:
            raise RuntimeError("Task ID not provided or bound")
        with cls._lock:
            t = cls._task_state.get(tid, {})
            t.pop(key, None)
            if not t:
                cls._task_state.pop(tid, None)

    @classmethod
    def export_task_state(cls, task_id: int) -> Dict[str, Any]:
        """
        Export the mutable state for a specific task as a deep-copied dict.

        Args:
            task_id: Integer ID of the task to export.

        Returns:
            Dict of key→value for that task, or {} if none.
        """
        with cls._lock:
            return deepcopy(cls._task_state.get(task_id, {}))

    @classmethod
    def export_task_state_json(cls, task_id: int, **json_kwargs: Any) -> str:
        """
        Export the mutable state for a specific task as JSON.

        Args:
            task_id: Integer ID of the task to export.
            **json_kwargs: Passed to json.dumps (e.g. indent=2).

        Returns:
            JSON string.
        """
        state = cls.export_task_state(task_id)
        return json.dumps(state, **json_kwargs)

    @classmethod
    def import_task_state(cls, task_id: int, new_state: Dict[str, Any]) -> None:
        """
        Merge a dict of new_state into existing task_state for a task.

        Only adds or updates keys; existing keys not in new_state remain untouched.

        Args:
            task_id: Integer ID of the task.
            new_state: Dict of key→value to merge in.
        """
        with cls._lock:
            t = cls._task_state.setdefault(task_id, {})
            for k, v in new_state.items():
                t[k] = v

    @classmethod
    def import_task_state_json(cls, task_id: int, json_data: str) -> None:
        """
        Parse a JSON string and import it into task_state for a given task,
        merging keys as in import_task_state.

        Args:
            task_id: Integer ID of the task.
            json_data: JSON string produced by export_task_state_json.
        """
        parsed = json.loads(json_data)
        if not isinstance(parsed, dict):
            raise ValueError("Imported JSON must be an object/dict")
        cls.import_task_state(task_id, parsed)

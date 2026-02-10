#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
unmanic.taskqueue_redis.py

Redis-backed implementation of TaskQueueInterface.
Uses sorted sets for priority queues, hashes for task data,
and Lua scripts for atomic operations.

Redis Data Structures:
    tars:tasks:pending       → Sorted Set (score = priority)
    tars:tasks:in_progress   → Sorted Set (score = start_time)
    tars:tasks:processed     → Sorted Set (score = finish_time)
    tars:task:{id}           → Hash (task fields)
    tars:task:next_id        → String (auto-increment counter)

Dependencies:
    redis>=5.0.0 (optional — install with: pip install redis>=5.0.0)

Version: 1.0.0
Author:  JARVIS (Session 212, 2026-02-10)
Review:  GPT-5 recommended Lua scripts over MULTI/EXEC for atomic claim
"""

import json
import time
from typing import Any, Dict, List, Optional

from unmanic.libs import task
from unmanic.libs import common
from unmanic.libs.logs import UnmanicLogging
from unmanic.libs.taskqueue_interface import TaskQueueInterface

# Lazy import — redis-py is optional
try:
    import redis
except ImportError:
    redis = None  # type: ignore[assignment]


# ─────────────────────────────────────────────────
# Lua Scripts for atomic Redis operations
# ─────────────────────────────────────────────────

# Atomic claim: pop highest-priority task from pending, move to in_progress
LUA_CLAIM_TASK = """
local task_id_score = redis.call('ZPOPMAX', KEYS[1], 1)
if #task_id_score == 0 then
    return nil
end
local task_id = task_id_score[1]
local score = task_id_score[2]
local now = ARGV[1]

-- Move to in_progress set with current timestamp as score
redis.call('ZADD', KEYS[2], now, task_id)

-- Update task hash status
local task_key = 'tars:task:' .. task_id
redis.call('HSET', task_key, 'status', 'in_progress', 'start_time', now)

return {task_id, score}
"""

# Atomic mark-as-processed: move from in_progress to processed
LUA_MARK_PROCESSED = """
local task_id = ARGV[1]
local now = ARGV[2]

-- Remove from in_progress
redis.call('ZREM', KEYS[1], task_id)

-- Add to processed with finish_time as score
redis.call('ZADD', KEYS[2], now, task_id)

-- Update task hash
local task_key = 'tars:task:' .. task_id
redis.call('HSET', task_key, 'status', 'processed', 'finish_time', now)

return 1
"""

# Atomic requeue: move task to bottom of pending set (lowest priority)
LUA_REQUEUE_BOTTOM = """
local task_id = ARGV[1]

-- Get current lowest score in pending
local lowest = redis.call('ZRANGE', KEYS[1], 0, 0, 'WITHSCORES')
local new_score = 0
if #lowest >= 2 then
    new_score = tonumber(lowest[2]) - 1
end

-- Remove from in_progress if present
redis.call('ZREM', KEYS[2], task_id)

-- Add to pending with lowest priority
redis.call('ZADD', KEYS[1], new_score, task_id)

-- Update status
local task_key = 'tars:task:' .. task_id
redis.call('HSET', task_key, 'status', 'pending', 'priority', new_score)

return 1
"""


class RedisTaskQueue(TaskQueueInterface):
    """
    Redis-backed task queue implementation.

    Uses sorted sets for O(log N) priority queue operations and
    Lua scripts for atomic task claim/release to prevent race conditions
    between concurrent workers.

    Task data is stored in Redis hashes with a 'tars:' key prefix to
    avoid collisions with other Redis users on the same instance.
    """

    KEY_PREFIX = "tars:"
    PENDING_KEY = "tars:tasks:pending"
    IN_PROGRESS_KEY = "tars:tasks:in_progress"
    PROCESSED_KEY = "tars:tasks:processed"
    NEXT_ID_KEY = "tars:task:next_id"

    def __init__(
        self,
        data_queues,
        redis_host: str = "localhost",
        redis_port: int = 6379,
        redis_db: int = 0,
        redis_password: Optional[str] = None,
        redis_max_connections: int = 50,
        redis_socket_timeout: int = 5,
        **kwargs,
    ):
        if redis is None:
            raise ImportError("Redis task queue requires the 'redis' package. " "Install with: pip install redis>=5.0.0")

        self.data_queues = data_queues
        self.logger = UnmanicLogging.get_logger(name=self.__class__.__name__)

        # Connection pool for thread safety
        self.pool = redis.ConnectionPool(
            host=redis_host,
            port=redis_port,
            db=redis_db,
            password=redis_password,
            max_connections=redis_max_connections,
            socket_timeout=redis_socket_timeout,
            socket_connect_timeout=redis_socket_timeout,
            decode_responses=True,
        )
        self.client = redis.Redis(connection_pool=self.pool)

        # Register Lua scripts (cached server-side after first call)
        self._claim_script = self.client.register_script(LUA_CLAIM_TASK)
        self._processed_script = self.client.register_script(LUA_MARK_PROCESSED)
        self._requeue_script = self.client.register_script(LUA_REQUEUE_BOTTOM)

        # Verify connectivity
        try:
            self.client.ping()
            self.logger.info("Redis connection established (%s:%s/%s)", redis_host, redis_port, redis_db)
        except redis.ConnectionError as e:
            self.logger.error("Failed to connect to Redis: %s", e)
            raise

    def _log(self, message, message2="", level="info"):
        message = common.format_message(message, message2)
        getattr(self.logger, level)(message)

    def _task_key(self, task_id) -> str:
        """Return the Redis hash key for a task."""
        return f"{self.KEY_PREFIX}task:{task_id}"

    # ──────────────────────────────────────────────
    # Serialization
    # ──────────────────────────────────────────────

    def _serialize_task(self, task_data: Dict[str, Any]) -> Dict[str, str]:
        """Convert task dict values to strings for Redis HSET."""
        serialized = {}
        for key, value in task_data.items():
            if value is None:
                serialized[key] = ""
            elif isinstance(value, bool):
                serialized[key] = "1" if value else "0"
            else:
                serialized[key] = str(value)
        return serialized

    def _deserialize_task(self, task_hash: Dict[str, str]) -> Dict[str, Any]:
        """Convert Redis hash strings back to appropriate Python types."""
        if not task_hash:
            return {}

        result = {}
        int_fields = {"id", "priority", "library_id"}
        bool_fields = {"success"}
        float_fields = {"start_time", "finish_time"}

        for key, value in task_hash.items():
            if value == "":
                result[key] = None
            elif key in int_fields:
                try:
                    result[key] = int(value)
                except (ValueError, TypeError):
                    result[key] = value
            elif key in bool_fields:
                result[key] = value in ("1", "True", "true")
            elif key in float_fields:
                try:
                    result[key] = float(value)
                except (ValueError, TypeError):
                    result[key] = value
            else:
                result[key] = value

        return result

    # ──────────────────────────────────────────────
    # Internal helpers
    # ──────────────────────────────────────────────

    def _get_tasks_from_set(
        self,
        set_key: str,
        limit: Optional[int] = None,
        reverse: bool = True,
    ) -> List[Dict[str, Any]]:
        """
        Fetch task dicts from a sorted set.

        :param set_key: Redis sorted set key.
        :param limit: Max results. None = all.
        :param reverse: If True, highest score first.
        :return: List of deserialized task dicts.
        """
        end = (limit - 1) if limit else -1

        if reverse:
            task_ids = self.client.zrevrange(set_key, 0, end)
        else:
            task_ids = self.client.zrange(set_key, 0, end)

        tasks = []
        pipe = self.client.pipeline(transaction=False)
        for tid in task_ids:
            pipe.hgetall(self._task_key(tid))

        results = pipe.execute()
        for task_hash in results:
            if task_hash:
                tasks.append(self._deserialize_task(task_hash))

        return tasks

    def _create_task_handle(self, task_id: str) -> Any:
        """
        Create a Task wrapper object from a Redis-stored task.

        Uses the existing Task class for compatibility with foreman/worker code
        that expects Task methods (get_task_id, get_source_abspath, etc.).
        The Task object reads from SQLite — for a full Redis-only setup,
        this would need a Redis-backed Task implementation.

        For hybrid mode (recommended by GPT review): SQLite remains the
        metadata source of truth, Redis is the fast dispatcher.
        """
        task_data = self.client.hgetall(self._task_key(task_id))
        if not task_data:
            return False

        abspath = task_data.get("abspath")
        if not abspath:
            return False

        task_handle = task.Task()
        try:
            task_handle.read_and_set_task_by_absolute_path(abspath)
            return task_handle
        except Exception as e:
            self.logger.warning("Failed to create task handle for %s: %s", task_id, e)
            return False

    def _matches_filters(
        self,
        task_data: Dict[str, str],
        local_only: bool = False,
        library_names: Optional[List[str]] = None,
        library_tags: Optional[List[str]] = None,
    ) -> bool:
        """
        Check if a task matches the given filters.

        For library_names and library_tags filtering: in hybrid mode,
        this queries SQLite for the library metadata (since Redis doesn't
        store library/tag relationships). For full Redis mode, secondary
        indexes would be needed.
        """
        if local_only and task_data.get("type") != "local":
            return False

        if library_names is not None or library_tags is not None:
            # Hybrid: query SQLite for library metadata
            library_id = task_data.get("library_id")
            if library_id:
                try:
                    from unmanic.libs.unmodels import Libraries, LibraryTags, Tags

                    lib = Libraries.get_by_id(int(library_id))

                    if library_names is not None and lib.name not in library_names:
                        return False

                    if library_tags is not None:
                        tag_query = Tags.select(Tags.name).join(LibraryTags).where(LibraryTags.library_id == int(library_id))
                        lib_tag_names = [t.name for t in tag_query]

                        if library_tags:
                            # Must have at least one matching tag
                            if not set(library_tags) & set(lib_tag_names):
                                return False
                        else:
                            # Empty list = must have no tags
                            if lib_tag_names:
                                return False

                except Exception as e:
                    self.logger.warning("Library filter check failed: %s", e)
                    return False

        return True

    # ──────────────────────────────────────────────
    # TaskQueueInterface implementation
    # ──────────────────────────────────────────────

    def list_pending_tasks(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        return self._get_tasks_from_set(self.PENDING_KEY, limit, reverse=True)

    def list_in_progress_tasks(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        return self._get_tasks_from_set(self.IN_PROGRESS_KEY, limit, reverse=True)

    def list_processed_tasks(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        return self._get_tasks_from_set(self.PROCESSED_KEY, limit, reverse=True)

    def get_next_pending_tasks(
        self,
        local_only: bool = False,
        library_names: Optional[List[str]] = None,
        library_tags: Optional[List[str]] = None,
    ) -> Any:
        """
        Atomically claim the highest-priority pending task.

        If filters are specified, tasks that don't match are put back
        and the next candidate is tried. This is a trade-off: Redis
        can't do SQL-style JOINs, so filtered claims may require
        multiple round-trips under high contention.
        """
        has_filters = local_only or library_names is not None or library_tags is not None

        if not has_filters:
            # Fast path: atomic Lua claim with no filtering
            result = self._claim_script(
                keys=[self.PENDING_KEY, self.IN_PROGRESS_KEY],
                args=[str(time.time())],
            )
            if not result:
                return False
            task_id = result[0]
            return self._create_task_handle(task_id)

        # Filtered path: peek candidates, check filters, then claim
        # We peek rather than pop to avoid unnecessary requeues
        max_candidates = 100  # Safety limit
        candidates = self.client.zrevrange(self.PENDING_KEY, 0, max_candidates - 1)

        for task_id in candidates:
            task_data = self.client.hgetall(self._task_key(task_id))
            if not task_data:
                # Orphaned entry — remove from set
                self.client.zrem(self.PENDING_KEY, task_id)
                continue

            if self._matches_filters(task_data, local_only, library_names, library_tags):
                # Atomically move this specific task to in_progress
                pipe = self.client.pipeline(transaction=True)
                pipe.zrem(self.PENDING_KEY, task_id)
                pipe.zadd(self.IN_PROGRESS_KEY, {task_id: time.time()})
                pipe.hset(
                    self._task_key(task_id),
                    mapping={
                        "status": "in_progress",
                        "start_time": str(time.time()),
                    },
                )
                pipe.execute()
                return self._create_task_handle(task_id)

        return False

    def get_next_processed_tasks(self) -> Any:
        """Claim next processed task for post-processing."""
        result = self.client.zpopmax(self.PROCESSED_KEY, 1)
        if not result:
            return False

        task_id = result[0][0]
        task_data = self.client.hgetall(self._task_key(task_id))
        if not task_data:
            return False

        abspath = task_data.get("abspath")
        if not abspath:
            return False

        task_handle = task.Task()
        try:
            task_handle.read_and_set_task_by_absolute_path(abspath)
            return task_handle
        except Exception as e:
            self.logger.warning("Failed to load processed task %s: %s", task_id, e)
            return False

    def mark_item_in_progress(self, task_item: Any) -> Any:
        """
        Set task status to 'in_progress'.

        Updates both Redis state and the SQLite-backed Task object
        (hybrid mode — SQLite remains source of truth for persistence).
        """
        task_item.set_status("in_progress")

        # Also update Redis state
        task_id = str(task_item.get_task_id())
        self.client.hset(
            self._task_key(task_id),
            mapping={
                "status": "in_progress",
                "start_time": str(time.time()),
            },
        )

        return task_item

    def mark_item_as_processed(self, task_item: Any) -> Any:
        """
        Set task status to 'processed'.

        Moves task from in_progress to processed in Redis and updates SQLite.
        """
        task_item.set_status("processed")

        # Also update Redis state
        task_id = str(task_item.get_task_id())
        self._processed_script(
            keys=[self.IN_PROGRESS_KEY, self.PROCESSED_KEY],
            args=[task_id, str(time.time())],
        )

        return task_item

    def task_list_pending_is_empty(self) -> bool:
        return self.client.zcard(self.PENDING_KEY) == 0

    def task_list_in_progress_is_empty(self) -> bool:
        return self.client.zcard(self.IN_PROGRESS_KEY) == 0

    def task_list_processed_is_empty(self) -> bool:
        return self.client.zcard(self.PROCESSED_KEY) == 0

    def get_task_by_id(self, task_id: int) -> Any:
        """Retrieve task from Redis hash. Falls back to SQLite in hybrid mode."""
        task_data = self.client.hgetall(self._task_key(str(task_id)))
        if task_data:
            return self._deserialize_task(task_data)
        # Hybrid fallback: check SQLite
        from unmanic.libs.unmodels.tasks import Tasks

        try:
            return Tasks.get(Tasks.id == task_id)
        except Tasks.DoesNotExist:
            return None

    def requeue_tasks_at_bottom(self, task_id: int) -> bool:
        """
        Move task to bottom of pending queue (lowest priority).

        Uses Lua script for atomic move + priority update.
        Also updates SQLite via Task class for hybrid consistency.
        """
        self._requeue_script(
            keys=[self.PENDING_KEY, self.IN_PROGRESS_KEY],
            args=[str(task_id)],
        )

        # Also update SQLite
        task_handler = task.Task()
        return task_handler.reorder_tasks([task_id], "bottom")

    # ──────────────────────────────────────────────
    # Redis-specific operations (not in interface)
    # ──────────────────────────────────────────────

    def enqueue_task(self, task_id: int, task_data: Dict[str, Any], priority: int = 0) -> None:
        """
        Add a task to the pending queue.

        This is called by TaskHandler when a new file is discovered.
        In hybrid mode, the task is already in SQLite — this adds it
        to Redis for fast dispatching.

        :param task_id: SQLite task ID.
        :param task_data: Task fields dict.
        :param priority: Priority score (higher = processed first).
        """
        task_data["id"] = task_id
        task_data["status"] = "pending"
        task_data["priority"] = priority

        pipe = self.client.pipeline(transaction=True)
        pipe.hset(self._task_key(task_id), mapping=self._serialize_task(task_data))
        pipe.zadd(self.PENDING_KEY, {str(task_id): priority})
        pipe.execute()

    def sync_from_sqlite(self) -> int:
        """
        Synchronize Redis queue state from SQLite (cold start / recovery).

        Reads all pending/in_progress/processed tasks from SQLite and
        populates the Redis sorted sets. Existing Redis state is cleared.

        :return: Total number of tasks synced.
        """
        from unmanic.libs.unmodels.tasks import Tasks

        # Clear existing Redis state
        pipe = self.client.pipeline(transaction=True)
        pipe.delete(self.PENDING_KEY)
        pipe.delete(self.IN_PROGRESS_KEY)
        pipe.delete(self.PROCESSED_KEY)
        pipe.execute()

        count = 0
        for task_row in Tasks.select().dicts():
            task_id = str(task_row["id"])
            task_key = self._task_key(task_id)

            self.client.hset(task_key, mapping=self._serialize_task(task_row))

            status = task_row.get("status", "pending")
            priority = task_row.get("priority", 0) or 0

            if status == "pending":
                self.client.zadd(self.PENDING_KEY, {task_id: priority})
            elif status == "in_progress":
                start_time = task_row.get("start_time")
                score = start_time.timestamp() if start_time else time.time()
                self.client.zadd(self.IN_PROGRESS_KEY, {task_id: score})
            elif status == "processed":
                finish_time = task_row.get("finish_time")
                score = finish_time.timestamp() if finish_time else time.time()
                self.client.zadd(self.PROCESSED_KEY, {task_id: score})

            count += 1

        self.logger.info("Synced %d tasks from SQLite to Redis", count)
        return count

    def health_check(self) -> Dict[str, Any]:
        """
        Return Redis health status and queue metrics.

        :return: Dict with connection status and queue sizes.
        """
        try:
            self.client.ping()
            return {
                "connected": True,
                "pending": self.client.zcard(self.PENDING_KEY),
                "in_progress": self.client.zcard(self.IN_PROGRESS_KEY),
                "processed": self.client.zcard(self.PROCESSED_KEY),
            }
        except Exception as e:
            return {
                "connected": False,
                "error": str(e),
            }

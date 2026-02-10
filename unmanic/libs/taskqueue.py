#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
unmanic.taskqueue.py

Backward-compatible entry point for the task queue system.

This module now delegates to the Adapter Pattern implementation:
    - TaskQueueInterface (ABC)     → taskqueue_interface.py
    - SQLiteTaskQueue (default)    → taskqueue_sqlite.py
    - RedisTaskQueue (optional)    → taskqueue_redis.py
    - TaskQueueFactory             → taskqueue_factory.py

The `TaskQueue` class is preserved as an alias for `SQLiteTaskQueue`
to maintain backward compatibility with existing imports:

    from unmanic.libs.taskqueue import TaskQueue  # still works

New code should use the factory:

    from unmanic.libs.taskqueue_factory import create_task_queue
    queue = create_task_queue(data_queues, backend='sqlite')

Original Author:  Josh.5 <jsunnex@gmail.com>
Refactored:       JARVIS (Session 212, 2026-02-10)

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

       THE SOFTWARE IS PROVIDED 'AS IS', WITHOUT WARRANTY OF ANY KIND,
       EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
       MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
       IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
       DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
       OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE
       OR OTHER DEALINGS IN THE SOFTWARE.

"""

# Backward compatibility: TaskQueue is now SQLiteTaskQueue
from unmanic.libs.taskqueue_sqlite import SQLiteTaskQueue as TaskQueue  # noqa: F401

# Re-export the interface and factory for new code
from unmanic.libs.taskqueue_interface import TaskQueueInterface  # noqa: F401
from unmanic.libs.taskqueue_factory import create_task_queue  # noqa: F401

# Legacy module-level functions removed — they were only used internally
# and are now private methods of SQLiteTaskQueue.

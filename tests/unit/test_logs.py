#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unit tests for the logging utilities in unmanic.libs.logs.

Tests BoundLogger and related functionality.
"""

import logging
import unittest
from unittest.mock import MagicMock, patch


class TestBoundLoggerInit(unittest.TestCase):
    """Tests for BoundLogger initialization."""

    def test_init_with_logger_only(self):
        """Test initialization with just a logger."""
        from unmanic.libs.logs import BoundLogger

        mock_logger = MagicMock()

        bound_logger = BoundLogger(mock_logger)

        self.assertEqual(bound_logger._logger, mock_logger)
        self.assertEqual(bound_logger._context, {})

    def test_init_with_context(self):
        """Test initialization with context dictionary."""
        from unmanic.libs.logs import BoundLogger

        mock_logger = MagicMock()
        context = {"worker_id": "main-0", "task_id": 123}

        bound_logger = BoundLogger(mock_logger, context)

        self.assertEqual(bound_logger._context, context)

    def test_init_with_none_context(self):
        """Test initialization with None context defaults to empty dict."""
        from unmanic.libs.logs import BoundLogger

        mock_logger = MagicMock()

        bound_logger = BoundLogger(mock_logger, None)

        self.assertEqual(bound_logger._context, {})


class TestBoundLoggerBind(unittest.TestCase):
    """Tests for BoundLogger.bind method."""

    def test_bind_returns_new_logger(self):
        """Test bind returns a new BoundLogger instance."""
        from unmanic.libs.logs import BoundLogger

        mock_logger = MagicMock()
        original = BoundLogger(mock_logger)

        result = original.bind(worker_id="main-0")

        self.assertIsNot(result, original)
        self.assertIsInstance(result, BoundLogger)

    def test_bind_adds_context(self):
        """Test bind adds context to new logger."""
        from unmanic.libs.logs import BoundLogger

        mock_logger = MagicMock()
        original = BoundLogger(mock_logger)

        result = original.bind(worker_id="main-0", task_id=123)

        self.assertEqual(result._context, {"worker_id": "main-0", "task_id": 123})

    def test_bind_preserves_existing_context(self):
        """Test bind preserves existing context."""
        from unmanic.libs.logs import BoundLogger

        mock_logger = MagicMock()
        original = BoundLogger(mock_logger, {"existing": "value"})

        result = original.bind(new_key="new_value")

        self.assertEqual(result._context, {"existing": "value", "new_key": "new_value"})

    def test_bind_does_not_modify_original(self):
        """Test bind does not modify original logger's context."""
        from unmanic.libs.logs import BoundLogger

        mock_logger = MagicMock()
        original = BoundLogger(mock_logger, {"key": "value"})

        original.bind(new_key="new_value")

        self.assertEqual(original._context, {"key": "value"})

    def test_bind_overwrites_existing_keys(self):
        """Test bind overwrites existing context keys."""
        from unmanic.libs.logs import BoundLogger

        mock_logger = MagicMock()
        original = BoundLogger(mock_logger, {"key": "old_value"})

        result = original.bind(key="new_value")

        self.assertEqual(result._context, {"key": "new_value"})


class TestBoundLoggerUnbind(unittest.TestCase):
    """Tests for BoundLogger.unbind method."""

    def test_unbind_returns_new_logger(self):
        """Test unbind returns a new BoundLogger instance."""
        from unmanic.libs.logs import BoundLogger

        mock_logger = MagicMock()
        original = BoundLogger(mock_logger, {"key": "value"})

        result = original.unbind("key")

        self.assertIsNot(result, original)
        self.assertIsInstance(result, BoundLogger)

    def test_unbind_removes_keys(self):
        """Test unbind removes specified keys."""
        from unmanic.libs.logs import BoundLogger

        mock_logger = MagicMock()
        original = BoundLogger(mock_logger, {"key1": "v1", "key2": "v2", "key3": "v3"})

        result = original.unbind("key1", "key2")

        self.assertEqual(result._context, {"key3": "v3"})

    def test_unbind_nonexistent_key(self):
        """Test unbind with non-existent key does not raise."""
        from unmanic.libs.logs import BoundLogger

        mock_logger = MagicMock()
        original = BoundLogger(mock_logger, {"key": "value"})

        result = original.unbind("nonexistent")

        self.assertEqual(result._context, {"key": "value"})

    def test_unbind_does_not_modify_original(self):
        """Test unbind does not modify original logger's context."""
        from unmanic.libs.logs import BoundLogger

        mock_logger = MagicMock()
        original = BoundLogger(mock_logger, {"key": "value"})

        original.unbind("key")

        self.assertEqual(original._context, {"key": "value"})


class TestBoundLoggerLogging(unittest.TestCase):
    """Tests for BoundLogger logging methods."""

    def test_debug_calls_logger(self):
        """Test debug method calls underlying logger."""
        from unmanic.libs.logs import BoundLogger

        mock_logger = MagicMock()
        bound_logger = BoundLogger(mock_logger, {"worker_id": "test"})

        bound_logger.debug("Test message")

        mock_logger.log.assert_called_once()
        call_args = mock_logger.log.call_args
        self.assertEqual(call_args[0][0], logging.DEBUG)
        self.assertEqual(call_args[0][1], "Test message")

    def test_info_calls_logger(self):
        """Test info method calls underlying logger."""
        from unmanic.libs.logs import BoundLogger

        mock_logger = MagicMock()
        bound_logger = BoundLogger(mock_logger)

        bound_logger.info("Info message")

        mock_logger.log.assert_called_once()
        call_args = mock_logger.log.call_args
        self.assertEqual(call_args[0][0], logging.INFO)

    def test_warning_calls_logger(self):
        """Test warning method calls underlying logger."""
        from unmanic.libs.logs import BoundLogger

        mock_logger = MagicMock()
        bound_logger = BoundLogger(mock_logger)

        bound_logger.warning("Warning message")

        mock_logger.log.assert_called_once()
        call_args = mock_logger.log.call_args
        self.assertEqual(call_args[0][0], logging.WARNING)

    def test_error_calls_logger(self):
        """Test error method calls underlying logger."""
        from unmanic.libs.logs import BoundLogger

        mock_logger = MagicMock()
        bound_logger = BoundLogger(mock_logger)

        bound_logger.error("Error message")

        mock_logger.log.assert_called_once()
        call_args = mock_logger.log.call_args
        self.assertEqual(call_args[0][0], logging.ERROR)

    def test_critical_calls_logger(self):
        """Test critical method calls underlying logger."""
        from unmanic.libs.logs import BoundLogger

        mock_logger = MagicMock()
        bound_logger = BoundLogger(mock_logger)

        bound_logger.critical("Critical message")

        mock_logger.log.assert_called_once()
        call_args = mock_logger.log.call_args
        self.assertEqual(call_args[0][0], logging.CRITICAL)

    def test_exception_includes_exc_info(self):
        """Test exception method includes exc_info=True."""
        from unmanic.libs.logs import BoundLogger

        mock_logger = MagicMock()
        bound_logger = BoundLogger(mock_logger)

        bound_logger.exception("Exception message")

        mock_logger.log.assert_called_once()
        call_args = mock_logger.log.call_args
        self.assertTrue(call_args[1]["exc_info"])

    def test_logging_includes_context_in_extra(self):
        """Test logging includes context in extra dict."""
        from unmanic.libs.logs import BoundLogger

        mock_logger = MagicMock()
        context = {"worker_id": "main-0", "task_id": 123}
        bound_logger = BoundLogger(mock_logger, context)

        bound_logger.info("Message")

        call_args = mock_logger.log.call_args
        extra = call_args[1]["extra"]
        self.assertEqual(extra["worker_id"], "main-0")
        self.assertEqual(extra["task_id"], 123)

    def test_logging_with_format_args(self):
        """Test logging with format arguments."""
        from unmanic.libs.logs import BoundLogger

        mock_logger = MagicMock()
        bound_logger = BoundLogger(mock_logger)

        bound_logger.info("Message with %s and %d", "string", 42)

        call_args = mock_logger.log.call_args
        self.assertEqual(call_args[0][1], "Message with %s and %d")
        self.assertEqual(call_args[0][2], "string")
        self.assertEqual(call_args[0][3], 42)


class TestBoundLoggerProperties(unittest.TestCase):
    """Tests for BoundLogger property methods."""

    def test_name_property(self):
        """Test name property returns underlying logger name."""
        from unmanic.libs.logs import BoundLogger

        mock_logger = MagicMock()
        mock_logger.name = "TestLogger"
        bound_logger = BoundLogger(mock_logger)

        result = bound_logger.name

        self.assertEqual(result, "TestLogger")

    def test_get_effective_level(self):
        """Test getEffectiveLevel delegates to underlying logger."""
        from unmanic.libs.logs import BoundLogger

        mock_logger = MagicMock()
        mock_logger.getEffectiveLevel.return_value = logging.DEBUG
        bound_logger = BoundLogger(mock_logger)

        result = bound_logger.getEffectiveLevel()

        self.assertEqual(result, logging.DEBUG)
        mock_logger.getEffectiveLevel.assert_called_once()

    def test_is_enabled_for(self):
        """Test isEnabledFor delegates to underlying logger."""
        from unmanic.libs.logs import BoundLogger

        mock_logger = MagicMock()
        mock_logger.isEnabledFor.return_value = True
        bound_logger = BoundLogger(mock_logger)

        result = bound_logger.isEnabledFor(logging.INFO)

        self.assertTrue(result)
        mock_logger.isEnabledFor.assert_called_once_with(logging.INFO)


class TestBoundLoggerChaining(unittest.TestCase):
    """Tests for BoundLogger method chaining."""

    def test_multiple_binds(self):
        """Test multiple bind calls accumulate context."""
        from unmanic.libs.logs import BoundLogger

        mock_logger = MagicMock()
        logger = BoundLogger(mock_logger)

        result = logger.bind(key1="v1").bind(key2="v2").bind(key3="v3")

        self.assertEqual(result._context, {"key1": "v1", "key2": "v2", "key3": "v3"})

    def test_bind_and_unbind(self):
        """Test bind followed by unbind."""
        from unmanic.libs.logs import BoundLogger

        mock_logger = MagicMock()
        logger = BoundLogger(mock_logger)

        result = logger.bind(key1="v1", key2="v2").unbind("key1")

        self.assertEqual(result._context, {"key2": "v2"})


class TestForwardJSONFormatterInit(unittest.TestCase):
    """Tests for ForwardJSONFormatter initialization."""

    def test_formatter_inherits_json_formatter(self):
        """Test ForwardJSONFormatter inherits from JSONFormatter."""
        from unmanic.libs.logs import ForwardJSONFormatter
        from json_log_formatter import JSONFormatter

        formatter = ForwardJSONFormatter()

        self.assertIsInstance(formatter, JSONFormatter)


class TestForwardJSONFormatterJsonRecord(unittest.TestCase):
    """Tests for ForwardJSONFormatter.json_record method."""

    def test_adds_levelname_to_extra(self):
        """Test json_record adds levelname to extra via real log record."""
        from unmanic.libs.logs import ForwardJSONFormatter

        formatter = ForwardJSONFormatter()

        # Create a real log record (not mock) to avoid JSONFormatter parent issues
        logger = logging.getLogger("TestLogger")
        record = logger.makeRecord(
            name="TestLogger",
            level=logging.INFO,
            fn="test.py",
            lno=1,
            msg="Test",
            args=(),
            exc_info=None,
        )

        extra = {}
        result = formatter.json_record("Test message", extra, record)

        self.assertEqual(extra["levelname"], "INFO")

    def test_includes_bound_context_fields(self):
        """Test json_record includes bound context fields."""
        from unmanic.libs.logs import ForwardJSONFormatter

        formatter = ForwardJSONFormatter()

        # Create a real log record and add bound fields
        logger = logging.getLogger("TestLogger")
        record = logger.makeRecord(
            name="TestLogger",
            level=logging.INFO,
            fn="test.py",
            lno=1,
            msg="Test",
            args=(),
            exc_info=None,
        )
        # Add bound context fields
        record.worker_id = "main-0"
        record.task_id = 123

        extra = {}
        formatter.json_record("Test message", extra, record)

        self.assertEqual(extra["worker_id"], "main-0")
        self.assertEqual(extra["task_id"], 123)

    def test_debug_mode_adds_extra_fields(self):
        """Test json_record adds extra fields in debug mode."""
        from unmanic.libs.logs import ForwardJSONFormatter

        formatter = ForwardJSONFormatter()

        # Create a real log record
        logger = logging.getLogger("TestLoggerDebug")
        logger.setLevel(logging.DEBUG)
        record = logger.makeRecord(
            name="TestLoggerDebug",
            level=logging.DEBUG,
            fn="test.py",
            lno=42,
            msg="Test",
            args=(),
            exc_info=None,
        )

        extra = {}
        formatter.json_record("Test message", extra, record)

        self.assertEqual(extra["filename"], "test.py")
        self.assertEqual(extra["lineno"], 42)


if __name__ == "__main__":
    unittest.main()

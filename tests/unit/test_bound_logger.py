#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unit tests for the BoundLogger class in unmanic.libs.logs.

Tests the structlog-like context binding functionality.
"""

import logging
import unittest
from unittest.mock import MagicMock, patch


class TestBoundLogger(unittest.TestCase):
    """Tests for the BoundLogger class."""

    def setUp(self):
        """Set up test fixtures."""
        # Import here to avoid import issues
        from unmanic.libs.logs import BoundLogger

        self.BoundLogger = BoundLogger
        self.mock_logger = MagicMock(spec=logging.Logger)
        self.mock_logger.name = "Unmanic.Test"

    def test_init_with_no_context(self):
        """Test BoundLogger initialization with no context."""
        bound = self.BoundLogger(self.mock_logger)
        self.assertEqual(bound._context, {})
        self.assertEqual(bound._logger, self.mock_logger)

    def test_init_with_context(self):
        """Test BoundLogger initialization with initial context."""
        context = {"worker_id": "main-0", "task_id": 123}
        bound = self.BoundLogger(self.mock_logger, context)
        self.assertEqual(bound._context, context)

    def test_bind_creates_new_instance(self):
        """Test that bind() creates a new logger instance."""
        bound1 = self.BoundLogger(self.mock_logger, {"worker_id": "main-0"})
        bound2 = bound1.bind(task_id=123)

        # Should be different instances
        self.assertIsNot(bound1, bound2)
        # Original should be unchanged
        self.assertEqual(bound1._context, {"worker_id": "main-0"})
        # New instance should have merged context
        self.assertEqual(bound2._context, {"worker_id": "main-0", "task_id": 123})

    def test_bind_merges_context(self):
        """Test that bind() merges context correctly."""
        bound = self.BoundLogger(self.mock_logger, {"a": 1, "b": 2})
        bound2 = bound.bind(b=3, c=4)  # b should be overwritten

        self.assertEqual(bound2._context, {"a": 1, "b": 3, "c": 4})

    def test_unbind_removes_keys(self):
        """Test that unbind() removes specified keys."""
        bound = self.BoundLogger(self.mock_logger, {"a": 1, "b": 2, "c": 3})
        bound2 = bound.unbind("a", "c")

        # Original unchanged
        self.assertEqual(bound._context, {"a": 1, "b": 2, "c": 3})
        # New instance has keys removed
        self.assertEqual(bound2._context, {"b": 2})

    def test_unbind_nonexistent_key(self):
        """Test that unbind() with nonexistent key doesn't raise."""
        bound = self.BoundLogger(self.mock_logger, {"a": 1})
        bound2 = bound.unbind("nonexistent")

        self.assertEqual(bound2._context, {"a": 1})

    def test_log_methods_inject_context(self):
        """Test that log methods inject context into extra."""
        bound = self.BoundLogger(self.mock_logger, {"worker_id": "main-0"})

        # Test debug
        bound.debug("test message")
        self.mock_logger.log.assert_called_with(logging.DEBUG, "test message", extra={"worker_id": "main-0"}, exc_info=None)
        self.mock_logger.reset_mock()

        # Test info
        bound.info("test info")
        self.mock_logger.log.assert_called_with(logging.INFO, "test info", extra={"worker_id": "main-0"}, exc_info=None)
        self.mock_logger.reset_mock()

        # Test warning
        bound.warning("test warning")
        self.mock_logger.log.assert_called_with(logging.WARNING, "test warning", extra={"worker_id": "main-0"}, exc_info=None)
        self.mock_logger.reset_mock()

        # Test error
        bound.error("test error")
        self.mock_logger.log.assert_called_with(logging.ERROR, "test error", extra={"worker_id": "main-0"}, exc_info=None)
        self.mock_logger.reset_mock()

        # Test critical
        bound.critical("test critical")
        self.mock_logger.log.assert_called_with(
            logging.CRITICAL, "test critical", extra={"worker_id": "main-0"}, exc_info=None
        )

    def test_exception_method_sets_exc_info(self):
        """Test that exception() sets exc_info=True."""
        bound = self.BoundLogger(self.mock_logger, {"worker_id": "main-0"})

        bound.exception("test exception")
        self.mock_logger.log.assert_called_with(logging.ERROR, "test exception", extra={"worker_id": "main-0"}, exc_info=True)

    def test_log_with_format_args(self):
        """Test logging with format arguments."""
        bound = self.BoundLogger(self.mock_logger, {"task_id": 123})

        bound.info("Processing file %s", "test.mkv")
        self.mock_logger.log.assert_called_with(
            logging.INFO, "Processing file %s", "test.mkv", extra={"task_id": 123}, exc_info=None
        )

    def test_log_merges_extra_kwarg(self):
        """Test that extra kwarg is merged with context."""
        bound = self.BoundLogger(self.mock_logger, {"worker_id": "main-0"})

        bound.info("test", extra={"custom_field": "value"})
        self.mock_logger.log.assert_called_with(
            logging.INFO, "test", extra={"worker_id": "main-0", "custom_field": "value"}, exc_info=None
        )

    def test_name_property(self):
        """Test the name property returns underlying logger name."""
        bound = self.BoundLogger(self.mock_logger)
        self.assertEqual(bound.name, "Unmanic.Test")

    def test_get_effective_level(self):
        """Test getEffectiveLevel delegates to underlying logger."""
        self.mock_logger.getEffectiveLevel.return_value = logging.DEBUG
        bound = self.BoundLogger(self.mock_logger)

        self.assertEqual(bound.getEffectiveLevel(), logging.DEBUG)
        self.mock_logger.getEffectiveLevel.assert_called_once()

    def test_is_enabled_for(self):
        """Test isEnabledFor delegates to underlying logger."""
        self.mock_logger.isEnabledFor.return_value = True
        bound = self.BoundLogger(self.mock_logger)

        self.assertTrue(bound.isEnabledFor(logging.DEBUG))
        self.mock_logger.isEnabledFor.assert_called_once_with(logging.DEBUG)

    def test_chained_binding(self):
        """Test chaining multiple bind() calls."""
        bound = self.BoundLogger(self.mock_logger)
        bound = bound.bind(a=1).bind(b=2).bind(c=3)

        self.assertEqual(bound._context, {"a": 1, "b": 2, "c": 3})


class TestUnmanicLoggingBoundLogger(unittest.TestCase):
    """Tests for UnmanicLogging.get_bound_logger factory method."""

    @patch("unmanic.libs.logs.UnmanicLogging.get_logger")
    def test_get_bound_logger_returns_bound_logger(self, mock_get_logger):
        """Test get_bound_logger returns a BoundLogger instance."""
        from unmanic.libs.logs import BoundLogger, UnmanicLogging

        mock_logger = MagicMock(spec=logging.Logger)
        mock_get_logger.return_value = mock_logger

        result = UnmanicLogging.get_bound_logger("Test")

        self.assertIsInstance(result, BoundLogger)
        mock_get_logger.assert_called_once_with("Test", None)

    @patch("unmanic.libs.logs.UnmanicLogging.get_logger")
    def test_get_bound_logger_with_initial_context(self, mock_get_logger):
        """Test get_bound_logger with initial context."""
        from unmanic.libs.logs import UnmanicLogging

        mock_logger = MagicMock(spec=logging.Logger)
        mock_get_logger.return_value = mock_logger

        result = UnmanicLogging.get_bound_logger("Worker", worker_id="main-0", component="transcoder")

        self.assertEqual(result._context, {"worker_id": "main-0", "component": "transcoder"})

    @patch("unmanic.libs.logs.UnmanicLogging.get_logger")
    def test_get_bound_logger_passes_settings(self, mock_get_logger):
        """Test get_bound_logger passes settings to get_logger."""
        from unmanic.libs.logs import UnmanicLogging

        mock_logger = MagicMock(spec=logging.Logger)
        mock_get_logger.return_value = mock_logger
        mock_settings = MagicMock()

        UnmanicLogging.get_bound_logger("Test", settings=mock_settings)

        mock_get_logger.assert_called_once_with("Test", mock_settings)


if __name__ == "__main__":
    unittest.main()

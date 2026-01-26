#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unit tests for the UI server utilities in unmanic.libs.uiserver.

Tests singleton classes for data queues and running threads.
"""

import unittest
from unittest.mock import MagicMock


class TestUnmanicDataQueues(unittest.TestCase):
    """Tests for UnmanicDataQueues singleton class."""

    def setUp(self):
        """Clear singleton before each test."""
        from unmanic.libs.singleton import SingletonType
        from unmanic.libs.uiserver import UnmanicDataQueues

        if UnmanicDataQueues in SingletonType._instances:
            del SingletonType._instances[UnmanicDataQueues]

    def tearDown(self):
        """Clear singleton after each test."""
        from unmanic.libs.singleton import SingletonType
        from unmanic.libs.uiserver import UnmanicDataQueues

        if UnmanicDataQueues in SingletonType._instances:
            del SingletonType._instances[UnmanicDataQueues]

    def test_init_creates_empty_dict(self):
        """Test initialization creates empty data queues dict."""
        from unmanic.libs.uiserver import UnmanicDataQueues

        udq = UnmanicDataQueues()

        self.assertEqual(udq._unmanic_data_queues, {})

    def test_set_data_queues(self):
        """Test set_unmanic_data_queues stores queues."""
        from unmanic.libs.uiserver import UnmanicDataQueues

        udq = UnmanicDataQueues()
        queues = {"queue1": MagicMock(), "queue2": MagicMock()}

        udq.set_unmanic_data_queues(queues)

        self.assertEqual(udq._unmanic_data_queues, queues)

    def test_get_data_queues(self):
        """Test get_unmanic_data_queues returns stored queues."""
        from unmanic.libs.uiserver import UnmanicDataQueues

        udq = UnmanicDataQueues()
        queues = {"queue1": MagicMock()}
        udq.set_unmanic_data_queues(queues)

        result = udq.get_unmanic_data_queues()

        self.assertEqual(result, queues)

    def test_singleton_returns_same_instance(self):
        """Test singleton returns the same instance."""
        from unmanic.libs.uiserver import UnmanicDataQueues

        udq1 = UnmanicDataQueues()
        udq2 = UnmanicDataQueues()

        self.assertIs(udq1, udq2)

    def test_data_persists_across_instances(self):
        """Test data persists across singleton instances."""
        from unmanic.libs.uiserver import UnmanicDataQueues

        udq1 = UnmanicDataQueues()
        queues = {"persistent": "data"}
        udq1.set_unmanic_data_queues(queues)

        udq2 = UnmanicDataQueues()
        result = udq2.get_unmanic_data_queues()

        self.assertEqual(result, queues)


class TestUnmanicRunningTreads(unittest.TestCase):
    """Tests for UnmanicRunningTreads singleton class."""

    def setUp(self):
        """Clear singleton before each test."""
        from unmanic.libs.singleton import SingletonType
        from unmanic.libs.uiserver import UnmanicRunningTreads

        if UnmanicRunningTreads in SingletonType._instances:
            del SingletonType._instances[UnmanicRunningTreads]

    def tearDown(self):
        """Clear singleton after each test."""
        from unmanic.libs.singleton import SingletonType
        from unmanic.libs.uiserver import UnmanicRunningTreads

        if UnmanicRunningTreads in SingletonType._instances:
            del SingletonType._instances[UnmanicRunningTreads]

    def test_init_creates_empty_dict(self):
        """Test initialization creates empty threads dict."""
        from unmanic.libs.uiserver import UnmanicRunningTreads

        urt = UnmanicRunningTreads()

        self.assertEqual(urt._unmanic_threads, {})

    def test_set_running_threads(self):
        """Test set_unmanic_running_threads stores threads."""
        from unmanic.libs.uiserver import UnmanicRunningTreads

        urt = UnmanicRunningTreads()
        threads = {"foreman": MagicMock(), "worker": MagicMock()}

        urt.set_unmanic_running_threads(threads)

        self.assertEqual(urt._unmanic_threads, threads)

    def test_get_running_thread_existing(self):
        """Test get_unmanic_running_thread returns existing thread."""
        from unmanic.libs.uiserver import UnmanicRunningTreads

        urt = UnmanicRunningTreads()
        mock_thread = MagicMock()
        urt.set_unmanic_running_threads({"foreman": mock_thread})

        result = urt.get_unmanic_running_thread("foreman")

        self.assertEqual(result, mock_thread)

    def test_get_running_thread_nonexistent(self):
        """Test get_unmanic_running_thread returns None for missing thread."""
        from unmanic.libs.uiserver import UnmanicRunningTreads

        urt = UnmanicRunningTreads()
        urt.set_unmanic_running_threads({})

        result = urt.get_unmanic_running_thread("nonexistent")

        self.assertIsNone(result)

    def test_singleton_returns_same_instance(self):
        """Test singleton returns the same instance."""
        from unmanic.libs.uiserver import UnmanicRunningTreads

        urt1 = UnmanicRunningTreads()
        urt2 = UnmanicRunningTreads()

        self.assertIs(urt1, urt2)

    def test_threads_persist_across_instances(self):
        """Test threads persist across singleton instances."""
        from unmanic.libs.uiserver import UnmanicRunningTreads

        urt1 = UnmanicRunningTreads()
        mock_thread = MagicMock()
        urt1.set_unmanic_running_threads({"test": mock_thread})

        urt2 = UnmanicRunningTreads()
        result = urt2.get_unmanic_running_thread("test")

        self.assertEqual(result, mock_thread)


class TestTornadoSettings(unittest.TestCase):
    """Tests for tornado_settings module-level configuration."""

    def test_tornado_settings_exists(self):
        """Test tornado_settings dict is defined."""
        from unmanic.libs.uiserver import tornado_settings

        self.assertIsInstance(tornado_settings, dict)

    def test_tornado_settings_has_required_keys(self):
        """Test tornado_settings has required configuration keys."""
        from unmanic.libs.uiserver import tornado_settings

        self.assertIn("template_loader", tornado_settings)
        self.assertIn("debug", tornado_settings)
        self.assertIn("autoreload", tornado_settings)

    def test_tornado_settings_static_paths(self):
        """Test tornado_settings has static file paths."""
        from unmanic.libs.uiserver import tornado_settings

        self.assertIn("static_css", tornado_settings)
        self.assertIn("static_js", tornado_settings)
        self.assertIn("static_img", tornado_settings)

    def test_autoreload_disabled(self):
        """Test autoreload is disabled by default."""
        from unmanic.libs.uiserver import tornado_settings

        self.assertFalse(tornado_settings["autoreload"])


class TestPublicDirectory(unittest.TestCase):
    """Tests for public_directory module-level variable."""

    def test_public_directory_is_absolute(self):
        """Test public_directory is an absolute path."""
        from unmanic.libs.uiserver import public_directory
        import os

        self.assertTrue(os.path.isabs(public_directory))

    def test_public_directory_contains_webserver(self):
        """Test public_directory path contains webserver."""
        from unmanic.libs.uiserver import public_directory

        self.assertIn("webserver", public_directory)
        self.assertIn("public", public_directory)


class TestUIServerInit(unittest.TestCase):
    """Tests for UIServer initialization."""

    def setUp(self):
        """Clear singletons before each test."""
        from unmanic.libs.singleton import SingletonType
        from unmanic.libs.uiserver import UnmanicDataQueues, UnmanicRunningTreads

        if UnmanicDataQueues in SingletonType._instances:
            del SingletonType._instances[UnmanicDataQueues]
        if UnmanicRunningTreads in SingletonType._instances:
            del SingletonType._instances[UnmanicRunningTreads]

    def tearDown(self):
        """Clear singletons after each test."""
        from unmanic.libs.singleton import SingletonType
        from unmanic.libs.uiserver import UnmanicDataQueues, UnmanicRunningTreads

        if UnmanicDataQueues in SingletonType._instances:
            del SingletonType._instances[UnmanicDataQueues]
        if UnmanicRunningTreads in SingletonType._instances:
            del SingletonType._instances[UnmanicRunningTreads]

    @unittest.mock.patch("unmanic.libs.uiserver.config.Config")
    @unittest.mock.patch("unmanic.libs.uiserver.UnmanicLogging")
    def test_init_sets_attributes(self, mock_logging, mock_config):
        """Test UIServer initialization sets attributes."""
        from unmanic.libs.uiserver import UIServer

        mock_logging.get_logger.return_value = MagicMock()
        mock_config_instance = MagicMock()
        mock_config_instance.get_log_path.return_value = None
        mock_config.return_value = mock_config_instance

        data_queues = {"inotifytasks": MagicMock()}
        foreman = MagicMock()

        server = UIServer(data_queues, foreman, developer=False)

        self.assertEqual(server.data_queues, data_queues)
        self.assertEqual(server.foreman, foreman)
        self.assertFalse(server.developer)
        self.assertIsNotNone(server.config)

    @unittest.mock.patch("unmanic.libs.uiserver.config.Config")
    @unittest.mock.patch("unmanic.libs.uiserver.UnmanicLogging")
    def test_init_with_developer_mode(self, mock_logging, mock_config):
        """Test UIServer initialization with developer mode."""
        from unmanic.libs.uiserver import UIServer

        mock_logging.get_logger.return_value = MagicMock()
        mock_config_instance = MagicMock()
        mock_config_instance.get_log_path.return_value = None
        mock_config.return_value = mock_config_instance

        data_queues = {"inotifytasks": MagicMock()}
        foreman = MagicMock()

        server = UIServer(data_queues, foreman, developer=True)

        self.assertTrue(server.developer)

    @unittest.mock.patch("unmanic.libs.uiserver.config.Config")
    @unittest.mock.patch("unmanic.libs.uiserver.UnmanicLogging")
    def test_init_sets_singletons(self, mock_logging, mock_config):
        """Test UIServer initialization sets singleton data."""
        from unmanic.libs.uiserver import UIServer, UnmanicDataQueues, UnmanicRunningTreads

        mock_logging.get_logger.return_value = MagicMock()
        mock_config_instance = MagicMock()
        mock_config_instance.get_log_path.return_value = None
        mock_config.return_value = mock_config_instance

        data_queues = {"inotifytasks": MagicMock()}
        foreman = MagicMock()

        UIServer(data_queues, foreman, developer=False)

        # Check singletons were set
        udq = UnmanicDataQueues()
        self.assertEqual(udq.get_unmanic_data_queues(), data_queues)

        urt = UnmanicRunningTreads()
        self.assertEqual(urt.get_unmanic_running_thread("foreman"), foreman)


class TestUIServerLog(unittest.TestCase):
    """Tests for UIServer._log method."""

    def setUp(self):
        """Clear singletons before each test."""
        from unmanic.libs.singleton import SingletonType
        from unmanic.libs.uiserver import UnmanicDataQueues, UnmanicRunningTreads

        if UnmanicDataQueues in SingletonType._instances:
            del SingletonType._instances[UnmanicDataQueues]
        if UnmanicRunningTreads in SingletonType._instances:
            del SingletonType._instances[UnmanicRunningTreads]

    def tearDown(self):
        """Clear singletons after each test."""
        from unmanic.libs.singleton import SingletonType
        from unmanic.libs.uiserver import UnmanicDataQueues, UnmanicRunningTreads

        if UnmanicDataQueues in SingletonType._instances:
            del SingletonType._instances[UnmanicDataQueues]
        if UnmanicRunningTreads in SingletonType._instances:
            del SingletonType._instances[UnmanicRunningTreads]

    @unittest.mock.patch("unmanic.libs.uiserver.common.format_message")
    @unittest.mock.patch("unmanic.libs.uiserver.config.Config")
    @unittest.mock.patch("unmanic.libs.uiserver.UnmanicLogging")
    def test_log_info_level(self, mock_logging, mock_config, mock_format):
        """Test _log with info level."""
        from unmanic.libs.uiserver import UIServer

        mock_logger = MagicMock()
        mock_logging.get_logger.return_value = mock_logger
        mock_config_instance = MagicMock()
        mock_config_instance.get_log_path.return_value = None
        mock_config.return_value = mock_config_instance
        mock_format.return_value = "formatted message"

        data_queues = {"inotifytasks": MagicMock()}
        server = UIServer(data_queues, MagicMock(), developer=False)
        server._log("test message")

        mock_logger.info.assert_called_with("formatted message")

    @unittest.mock.patch("unmanic.libs.uiserver.common.format_message")
    @unittest.mock.patch("unmanic.libs.uiserver.config.Config")
    @unittest.mock.patch("unmanic.libs.uiserver.UnmanicLogging")
    def test_log_error_level(self, mock_logging, mock_config, mock_format):
        """Test _log with error level."""
        from unmanic.libs.uiserver import UIServer

        mock_logger = MagicMock()
        mock_logging.get_logger.return_value = mock_logger
        mock_config_instance = MagicMock()
        mock_config_instance.get_log_path.return_value = None
        mock_config.return_value = mock_config_instance
        mock_format.return_value = "error message"

        data_queues = {"inotifytasks": MagicMock()}
        server = UIServer(data_queues, MagicMock(), developer=False)
        server._log("error", level="error")

        mock_logger.error.assert_called_with("error message")


class TestUIServerStop(unittest.TestCase):
    """Tests for UIServer.stop method."""

    def setUp(self):
        """Clear singletons before each test."""
        from unmanic.libs.singleton import SingletonType
        from unmanic.libs.uiserver import UnmanicDataQueues, UnmanicRunningTreads

        if UnmanicDataQueues in SingletonType._instances:
            del SingletonType._instances[UnmanicDataQueues]
        if UnmanicRunningTreads in SingletonType._instances:
            del SingletonType._instances[UnmanicRunningTreads]

    def tearDown(self):
        """Clear singletons after each test."""
        from unmanic.libs.singleton import SingletonType
        from unmanic.libs.uiserver import UnmanicDataQueues, UnmanicRunningTreads

        if UnmanicDataQueues in SingletonType._instances:
            del SingletonType._instances[UnmanicDataQueues]
        if UnmanicRunningTreads in SingletonType._instances:
            del SingletonType._instances[UnmanicRunningTreads]

    @unittest.mock.patch("unmanic.libs.uiserver.config.Config")
    @unittest.mock.patch("unmanic.libs.uiserver.UnmanicLogging")
    def test_stop_when_not_started(self, mock_logging, mock_config):
        """Test stop does nothing when not started."""
        from unmanic.libs.uiserver import UIServer

        mock_logging.get_logger.return_value = MagicMock()
        mock_config_instance = MagicMock()
        mock_config_instance.get_log_path.return_value = None
        mock_config.return_value = mock_config_instance

        data_queues = {"inotifytasks": MagicMock()}
        server = UIServer(data_queues, MagicMock(), developer=False)
        server.started = False
        server.io_loop = None

        # Should not raise
        server.stop()

        self.assertFalse(server.started)

    @unittest.mock.patch("unmanic.libs.uiserver.config.Config")
    @unittest.mock.patch("unmanic.libs.uiserver.UnmanicLogging")
    def test_stop_when_started(self, mock_logging, mock_config):
        """Test stop sets started to False."""
        from unmanic.libs.uiserver import UIServer

        mock_logging.get_logger.return_value = MagicMock()
        mock_config_instance = MagicMock()
        mock_config_instance.get_log_path.return_value = None
        mock_config.return_value = mock_config_instance

        data_queues = {"inotifytasks": MagicMock()}
        server = UIServer(data_queues, MagicMock(), developer=False)
        server.started = True
        mock_io_loop = MagicMock()
        server.io_loop = mock_io_loop

        server.stop()

        self.assertFalse(server.started)
        mock_io_loop.add_callback.assert_called()


class TestUIServerUpdateTornadoSettings(unittest.TestCase):
    """Tests for UIServer.update_tornado_settings method."""

    def setUp(self):
        """Clear singletons before each test."""
        from unmanic.libs.singleton import SingletonType
        from unmanic.libs.uiserver import UnmanicDataQueues, UnmanicRunningTreads, tornado_settings

        if UnmanicDataQueues in SingletonType._instances:
            del SingletonType._instances[UnmanicDataQueues]
        if UnmanicRunningTreads in SingletonType._instances:
            del SingletonType._instances[UnmanicRunningTreads]
        # Reset tornado_settings
        tornado_settings["autoreload"] = False
        if "serve_traceback" in tornado_settings:
            del tornado_settings["serve_traceback"]

    def tearDown(self):
        """Clear singletons after each test."""
        from unmanic.libs.singleton import SingletonType
        from unmanic.libs.uiserver import UnmanicDataQueues, UnmanicRunningTreads, tornado_settings

        if UnmanicDataQueues in SingletonType._instances:
            del SingletonType._instances[UnmanicDataQueues]
        if UnmanicRunningTreads in SingletonType._instances:
            del SingletonType._instances[UnmanicRunningTreads]
        # Reset tornado_settings
        tornado_settings["autoreload"] = False
        if "serve_traceback" in tornado_settings:
            del tornado_settings["serve_traceback"]

    @unittest.mock.patch("unmanic.libs.uiserver.config.Config")
    @unittest.mock.patch("unmanic.libs.uiserver.UnmanicLogging")
    def test_developer_mode_enables_autoreload(self, mock_logging, mock_config):
        """Test update_tornado_settings enables autoreload in developer mode."""
        from unmanic.libs.uiserver import UIServer, tornado_settings

        mock_logging.get_logger.return_value = MagicMock()
        mock_config_instance = MagicMock()
        mock_config_instance.get_log_path.return_value = None
        mock_config.return_value = mock_config_instance

        data_queues = {"inotifytasks": MagicMock()}
        server = UIServer(data_queues, MagicMock(), developer=True)

        server.update_tornado_settings()

        self.assertTrue(tornado_settings["autoreload"])
        self.assertTrue(tornado_settings["serve_traceback"])

    @unittest.mock.patch("unmanic.libs.uiserver.config.Config")
    @unittest.mock.patch("unmanic.libs.uiserver.UnmanicLogging")
    def test_non_developer_mode_keeps_defaults(self, mock_logging, mock_config):
        """Test update_tornado_settings keeps defaults in non-developer mode."""
        from unmanic.libs.uiserver import UIServer, tornado_settings

        mock_logging.get_logger.return_value = MagicMock()
        mock_config_instance = MagicMock()
        mock_config_instance.get_log_path.return_value = None
        mock_config.return_value = mock_config_instance

        data_queues = {"inotifytasks": MagicMock()}
        server = UIServer(data_queues, MagicMock(), developer=False)

        server.update_tornado_settings()

        self.assertFalse(tornado_settings["autoreload"])


class TestUIServerSetLogging(unittest.TestCase):
    """Tests for UIServer.set_logging method."""

    def setUp(self):
        """Clear singletons before each test."""
        from unmanic.libs.singleton import SingletonType
        from unmanic.libs.uiserver import UnmanicDataQueues, UnmanicRunningTreads

        if UnmanicDataQueues in SingletonType._instances:
            del SingletonType._instances[UnmanicDataQueues]
        if UnmanicRunningTreads in SingletonType._instances:
            del SingletonType._instances[UnmanicRunningTreads]

    def tearDown(self):
        """Clear singletons after each test."""
        from unmanic.libs.singleton import SingletonType
        from unmanic.libs.uiserver import UnmanicDataQueues, UnmanicRunningTreads

        if UnmanicDataQueues in SingletonType._instances:
            del SingletonType._instances[UnmanicDataQueues]
        if UnmanicRunningTreads in SingletonType._instances:
            del SingletonType._instances[UnmanicRunningTreads]

    @unittest.mock.patch("unmanic.libs.uiserver.config.Config")
    @unittest.mock.patch("unmanic.libs.uiserver.UnmanicLogging")
    def test_set_logging_skips_when_no_log_path(self, mock_logging, mock_config):
        """Test set_logging does nothing when no log path configured."""
        from unmanic.libs.uiserver import UIServer

        mock_logging.get_logger.return_value = MagicMock()
        mock_config_instance = MagicMock()
        mock_config_instance.get_log_path.return_value = None
        mock_config.return_value = mock_config_instance

        data_queues = {"inotifytasks": MagicMock()}
        server = UIServer(data_queues, MagicMock(), developer=False)

        # set_logging is called in __init__, so just verify no error occurred
        self.assertIsNotNone(server.config)

    @unittest.mock.patch("unmanic.libs.uiserver.logging.handlers.TimedRotatingFileHandler")
    @unittest.mock.patch("unmanic.libs.uiserver.logging.getLogger")
    @unittest.mock.patch("unmanic.libs.uiserver.os.makedirs")
    @unittest.mock.patch("unmanic.libs.uiserver.os.path.exists")
    @unittest.mock.patch("unmanic.libs.uiserver.config.Config")
    @unittest.mock.patch("unmanic.libs.uiserver.UnmanicLogging")
    def test_set_logging_creates_log_dir(
        self, mock_logging, mock_config, mock_exists, mock_makedirs, mock_get_logger, mock_handler
    ):
        """Test set_logging creates log directory if it doesn't exist."""
        from unmanic.libs.uiserver import UIServer

        mock_logging.get_logger.return_value = MagicMock()
        mock_config_instance = MagicMock()
        mock_config_instance.get_log_path.return_value = "/tmp/test_logs"
        mock_config.return_value = mock_config_instance
        mock_exists.return_value = False
        mock_get_logger.return_value = MagicMock()
        mock_handler.return_value = MagicMock()

        data_queues = {"inotifytasks": MagicMock()}
        UIServer(data_queues, MagicMock(), developer=False)

        mock_makedirs.assert_called_with("/tmp/test_logs")

    @unittest.mock.patch("unmanic.libs.uiserver.logging.handlers.TimedRotatingFileHandler")
    @unittest.mock.patch("unmanic.libs.uiserver.logging.getLogger")
    @unittest.mock.patch("unmanic.libs.uiserver.os.makedirs")
    @unittest.mock.patch("unmanic.libs.uiserver.os.path.exists")
    @unittest.mock.patch("unmanic.libs.uiserver.config.Config")
    @unittest.mock.patch("unmanic.libs.uiserver.UnmanicLogging")
    def test_set_logging_configures_tornado_loggers(
        self, mock_logging, mock_config, mock_exists, mock_makedirs, mock_get_logger, mock_handler
    ):
        """Test set_logging configures tornado loggers."""
        from unmanic.libs.uiserver import UIServer

        mock_logging.get_logger.return_value = MagicMock()
        mock_config_instance = MagicMock()
        mock_config_instance.get_log_path.return_value = "/tmp/test_logs"
        mock_config.return_value = mock_config_instance
        mock_exists.return_value = True
        mock_tornado_logger = MagicMock()
        mock_get_logger.return_value = mock_tornado_logger
        mock_handler.return_value = MagicMock()

        data_queues = {"inotifytasks": MagicMock()}
        UIServer(data_queues, MagicMock(), developer=False)

        # Should have called getLogger for tornado loggers
        logger_calls = [call[0][0] for call in mock_get_logger.call_args_list]
        self.assertIn("tornado.access", logger_calls)
        self.assertIn("tornado.application", logger_calls)
        self.assertIn("tornado.general", logger_calls)


if __name__ == "__main__":
    unittest.main()

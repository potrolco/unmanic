#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unit tests for the PluginsHandler class in unmanic.libs.plugins.

Tests plugin management functionality with mocked dependencies.
"""

import hashlib
import os
import unittest
from unittest.mock import MagicMock, patch


class TestPluginsHandlerInit(unittest.TestCase):
    """Tests for PluginsHandler initialization."""

    def setUp(self):
        """Clear singleton before each test."""
        from unmanic.libs.singleton import SingletonType
        from unmanic.libs.plugins import PluginsHandler

        if PluginsHandler in SingletonType._instances:
            del SingletonType._instances[PluginsHandler]

    def tearDown(self):
        """Clear singleton after each test."""
        from unmanic.libs.singleton import SingletonType
        from unmanic.libs.plugins import PluginsHandler

        if PluginsHandler in SingletonType._instances:
            del SingletonType._instances[PluginsHandler]

    @patch("unmanic.libs.plugins.UnmanicLogging")
    @patch("unmanic.libs.plugins.config.Config")
    def test_init_sets_attributes(self, mock_config, mock_logging):
        """Test initialization sets settings and logger."""
        from unmanic.libs.plugins import PluginsHandler

        mock_logging.get_logger.return_value = MagicMock()
        mock_config.return_value = MagicMock()

        handler = PluginsHandler()

        self.assertIsNotNone(handler.settings)
        self.assertIsNotNone(handler.logger)

    @patch("unmanic.libs.plugins.UnmanicLogging")
    @patch("unmanic.libs.plugins.config.Config")
    def test_version_is_set(self, mock_config, mock_logging):
        """Test version class attribute is set."""
        from unmanic.libs.plugins import PluginsHandler

        mock_logging.get_logger.return_value = MagicMock()
        mock_config.return_value = MagicMock()

        handler = PluginsHandler()

        self.assertEqual(handler.version, 2)


class TestPluginsHandlerStaticMethods(unittest.TestCase):
    """Tests for PluginsHandler static methods."""

    def test_get_plugin_repo_id_returns_int(self):
        """Test get_plugin_repo_id returns integer hash."""
        from unmanic.libs.plugins import PluginsHandler

        result = PluginsHandler.get_plugin_repo_id("test/repo/path")

        self.assertIsInstance(result, int)

    def test_get_plugin_repo_id_consistent(self):
        """Test get_plugin_repo_id returns same value for same input."""
        from unmanic.libs.plugins import PluginsHandler

        result1 = PluginsHandler.get_plugin_repo_id("test/repo")
        result2 = PluginsHandler.get_plugin_repo_id("test/repo")

        self.assertEqual(result1, result2)

    def test_get_plugin_repo_id_different_for_different_input(self):
        """Test get_plugin_repo_id returns different values for different inputs."""
        from unmanic.libs.plugins import PluginsHandler

        result1 = PluginsHandler.get_plugin_repo_id("repo1")
        result2 = PluginsHandler.get_plugin_repo_id("repo2")

        self.assertNotEqual(result1, result2)

    def test_get_plugin_repo_id_matches_md5(self):
        """Test get_plugin_repo_id uses MD5 hash."""
        from unmanic.libs.plugins import PluginsHandler

        repo_path = "test/repo"
        expected = int(hashlib.md5(repo_path.encode("utf8")).hexdigest(), 16)

        result = PluginsHandler.get_plugin_repo_id(repo_path)

        self.assertEqual(result, expected)

    def test_get_default_repo(self):
        """Test get_default_repo returns default string."""
        from unmanic.libs.plugins import PluginsHandler

        result = PluginsHandler.get_default_repo()

        self.assertEqual(result, "default")


class TestPluginsHandlerPathMethods(unittest.TestCase):
    """Tests for PluginsHandler path methods."""

    def setUp(self):
        """Clear singleton before each test."""
        from unmanic.libs.singleton import SingletonType
        from unmanic.libs.plugins import PluginsHandler

        if PluginsHandler in SingletonType._instances:
            del SingletonType._instances[PluginsHandler]

    def tearDown(self):
        """Clear singleton after each test."""
        from unmanic.libs.singleton import SingletonType
        from unmanic.libs.plugins import PluginsHandler

        if PluginsHandler in SingletonType._instances:
            del SingletonType._instances[PluginsHandler]

    @patch("unmanic.libs.plugins.os.path.exists")
    @patch("unmanic.libs.plugins.os.makedirs")
    @patch("unmanic.libs.plugins.UnmanicLogging")
    @patch("unmanic.libs.plugins.config.Config")
    def test_get_repo_cache_file_creates_directory(self, mock_config, mock_logging, mock_makedirs, mock_exists):
        """Test get_repo_cache_file creates plugins directory if needed."""
        from unmanic.libs.plugins import PluginsHandler

        mock_logging.get_logger.return_value = MagicMock()
        mock_config_instance = MagicMock()
        mock_config_instance.get_plugins_path.return_value = "/tmp/plugins"
        mock_config.return_value = mock_config_instance
        mock_exists.return_value = False

        handler = PluginsHandler()
        handler.get_repo_cache_file(12345)

        mock_makedirs.assert_called_with("/tmp/plugins")

    @patch("unmanic.libs.plugins.os.path.exists")
    @patch("unmanic.libs.plugins.UnmanicLogging")
    @patch("unmanic.libs.plugins.config.Config")
    def test_get_repo_cache_file_returns_correct_path(self, mock_config, mock_logging, mock_exists):
        """Test get_repo_cache_file returns correct file path."""
        from unmanic.libs.plugins import PluginsHandler

        mock_logging.get_logger.return_value = MagicMock()
        mock_config_instance = MagicMock()
        mock_config_instance.get_plugins_path.return_value = "/tmp/plugins"
        mock_config.return_value = mock_config_instance
        mock_exists.return_value = True

        handler = PluginsHandler()
        result = handler.get_repo_cache_file(12345)

        self.assertEqual(result, "/tmp/plugins/repo-12345.json")

    @patch("unmanic.libs.plugins.os.path.exists")
    @patch("unmanic.libs.plugins.os.makedirs")
    @patch("unmanic.libs.plugins.UnmanicLogging")
    @patch("unmanic.libs.plugins.config.Config")
    def test_get_plugin_path_creates_directory(self, mock_config, mock_logging, mock_makedirs, mock_exists):
        """Test get_plugin_path creates plugin directory if needed."""
        from unmanic.libs.plugins import PluginsHandler

        mock_logging.get_logger.return_value = MagicMock()
        mock_config_instance = MagicMock()
        mock_config_instance.get_plugins_path.return_value = "/tmp/plugins"
        mock_config.return_value = mock_config_instance
        mock_exists.return_value = False

        handler = PluginsHandler()
        handler.get_plugin_path("test_plugin")

        mock_makedirs.assert_called_with("/tmp/plugins/test_plugin")

    @patch("unmanic.libs.plugins.os.path.exists")
    @patch("unmanic.libs.plugins.UnmanicLogging")
    @patch("unmanic.libs.plugins.config.Config")
    def test_get_plugin_path_returns_correct_path(self, mock_config, mock_logging, mock_exists):
        """Test get_plugin_path returns correct directory path."""
        from unmanic.libs.plugins import PluginsHandler

        mock_logging.get_logger.return_value = MagicMock()
        mock_config_instance = MagicMock()
        mock_config_instance.get_plugins_path.return_value = "/tmp/plugins"
        mock_config.return_value = mock_config_instance
        mock_exists.return_value = True

        handler = PluginsHandler()
        result = handler.get_plugin_path("my_plugin")

        self.assertEqual(result, "/tmp/plugins/my_plugin")

    @patch("unmanic.libs.plugins.UnmanicLogging")
    @patch("unmanic.libs.plugins.config.Config")
    def test_get_plugin_download_cache_path(self, mock_config, mock_logging):
        """Test get_plugin_download_cache_path returns correct path."""
        from unmanic.libs.plugins import PluginsHandler

        mock_logging.get_logger.return_value = MagicMock()
        mock_config_instance = MagicMock()
        mock_config_instance.get_plugins_path.return_value = "/tmp/plugins"
        mock_config.return_value = mock_config_instance

        handler = PluginsHandler()
        result = handler.get_plugin_download_cache_path("test_plugin", "1.0.0")

        self.assertEqual(result, "/tmp/plugins/test_plugin-1.0.0.zip")


class TestPluginsHandlerLog(unittest.TestCase):
    """Tests for PluginsHandler._log method."""

    def setUp(self):
        """Clear singleton before each test."""
        from unmanic.libs.singleton import SingletonType
        from unmanic.libs.plugins import PluginsHandler

        if PluginsHandler in SingletonType._instances:
            del SingletonType._instances[PluginsHandler]

    def tearDown(self):
        """Clear singleton after each test."""
        from unmanic.libs.singleton import SingletonType
        from unmanic.libs.plugins import PluginsHandler

        if PluginsHandler in SingletonType._instances:
            del SingletonType._instances[PluginsHandler]

    @patch("unmanic.libs.plugins.common.format_message")
    @patch("unmanic.libs.plugins.UnmanicLogging")
    @patch("unmanic.libs.plugins.config.Config")
    def test_log_info_level(self, mock_config, mock_logging, mock_format):
        """Test _log with info level."""
        from unmanic.libs.plugins import PluginsHandler

        mock_logger = MagicMock()
        mock_logging.get_logger.return_value = mock_logger
        mock_config.return_value = MagicMock()
        mock_format.return_value = "formatted message"

        handler = PluginsHandler()
        handler._log("test message")

        mock_logger.info.assert_called_with("formatted message")

    @patch("unmanic.libs.plugins.common.format_message")
    @patch("unmanic.libs.plugins.UnmanicLogging")
    @patch("unmanic.libs.plugins.config.Config")
    def test_log_error_level(self, mock_config, mock_logging, mock_format):
        """Test _log with error level."""
        from unmanic.libs.plugins import PluginsHandler

        mock_logger = MagicMock()
        mock_logging.get_logger.return_value = mock_logger
        mock_config.return_value = MagicMock()
        mock_format.return_value = "error message"

        handler = PluginsHandler()
        handler._log("error", level="error")

        mock_logger.error.assert_called_with("error message")

    @patch("unmanic.libs.plugins.common.format_message")
    @patch("unmanic.libs.plugins.UnmanicLogging")
    @patch("unmanic.libs.plugins.config.Config")
    def test_log_with_message2(self, mock_config, mock_logging, mock_format):
        """Test _log passes message2 to format_message."""
        from unmanic.libs.plugins import PluginsHandler

        mock_logger = MagicMock()
        mock_logging.get_logger.return_value = mock_logger
        mock_config.return_value = MagicMock()
        mock_format.return_value = "formatted"

        handler = PluginsHandler()
        handler._log("msg1", "msg2")

        mock_format.assert_called_with("msg1", "msg2")


class TestPluginsHandlerSingleton(unittest.TestCase):
    """Tests for PluginsHandler singleton behavior."""

    def setUp(self):
        """Clear singleton before each test."""
        from unmanic.libs.singleton import SingletonType
        from unmanic.libs.plugins import PluginsHandler

        if PluginsHandler in SingletonType._instances:
            del SingletonType._instances[PluginsHandler]

    def tearDown(self):
        """Clear singleton after each test."""
        from unmanic.libs.singleton import SingletonType
        from unmanic.libs.plugins import PluginsHandler

        if PluginsHandler in SingletonType._instances:
            del SingletonType._instances[PluginsHandler]

    @patch("unmanic.libs.plugins.UnmanicLogging")
    @patch("unmanic.libs.plugins.config.Config")
    def test_singleton_returns_same_instance(self, mock_config, mock_logging):
        """Test singleton returns the same instance."""
        from unmanic.libs.plugins import PluginsHandler

        mock_logging.get_logger.return_value = MagicMock()
        mock_config.return_value = MagicMock()

        handler1 = PluginsHandler()
        handler2 = PluginsHandler()

        self.assertIs(handler1, handler2)


if __name__ == "__main__":
    unittest.main()

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


class TestPluginsHandlerGetPluginRepos(unittest.TestCase):
    """Tests for PluginsHandler.get_plugin_repos method."""

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

    @patch("unmanic.libs.plugins.PluginRepos")
    @patch("unmanic.libs.plugins.UnmanicLogging")
    @patch("unmanic.libs.plugins.config.Config")
    def test_get_plugin_repos_returns_default(self, mock_config, mock_logging, mock_plugin_repos):
        """Test get_plugin_repos includes default repo."""
        from unmanic.libs.plugins import PluginsHandler

        mock_logging.get_logger.return_value = MagicMock()
        mock_config.return_value = MagicMock()
        mock_plugin_repos.select.return_value.order_by.return_value = []

        handler = PluginsHandler()
        result = handler.get_plugin_repos()

        self.assertIn({"path": "default"}, result)

    @patch("unmanic.libs.plugins.PluginRepos")
    @patch("unmanic.libs.plugins.UnmanicLogging")
    @patch("unmanic.libs.plugins.config.Config")
    def test_get_plugin_repos_includes_custom_repos(self, mock_config, mock_logging, mock_plugin_repos):
        """Test get_plugin_repos includes custom repos from database."""
        from unmanic.libs.plugins import PluginsHandler

        mock_logging.get_logger.return_value = MagicMock()
        mock_config.return_value = MagicMock()

        mock_repo = MagicMock()
        mock_repo.model_to_dict.return_value = {"path": "custom/repo"}
        mock_plugin_repos.select.return_value.order_by.return_value = [mock_repo]

        handler = PluginsHandler()
        result = handler.get_plugin_repos()

        self.assertEqual(len(result), 2)
        self.assertEqual(result[1], {"path": "custom/repo"})


class TestPluginsHandlerReadRepoData(unittest.TestCase):
    """Tests for PluginsHandler.read_repo_data method."""

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

    @patch("unmanic.libs.plugins.os.makedirs")
    @patch("unmanic.libs.plugins.os.path.exists")
    @patch("unmanic.libs.plugins.UnmanicLogging")
    @patch("unmanic.libs.plugins.config.Config")
    def test_read_repo_data_returns_empty_dict_if_not_exists(self, mock_config, mock_logging, mock_exists, mock_makedirs):
        """Test read_repo_data returns empty dict if cache file doesn't exist."""
        from unmanic.libs.plugins import PluginsHandler

        mock_logging.get_logger.return_value = MagicMock()
        mock_config_instance = MagicMock()
        mock_config_instance.get_plugins_path.return_value = "/tmp/test_plugins_12345"
        mock_config.return_value = mock_config_instance
        mock_exists.return_value = False

        handler = PluginsHandler()
        result = handler.read_repo_data(12345)

        self.assertEqual(result, {})


class TestPluginsHandlerGetPluginInfo(unittest.TestCase):
    """Tests for PluginsHandler.get_plugin_info method."""

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
    @patch("unmanic.libs.plugins.UnmanicLogging")
    @patch("unmanic.libs.plugins.config.Config")
    def test_get_plugin_info_returns_empty_dict_if_no_info_file(self, mock_config, mock_logging, mock_exists):
        """Test get_plugin_info returns empty dict if info.json doesn't exist."""
        from unmanic.libs.plugins import PluginsHandler

        mock_logging.get_logger.return_value = MagicMock()
        mock_config_instance = MagicMock()
        mock_config_instance.get_plugins_path.return_value = "/tmp/plugins"
        mock_config.return_value = mock_config_instance
        mock_exists.return_value = False

        handler = PluginsHandler()
        result = handler.get_plugin_info("test_plugin")

        self.assertEqual(result, {})


class TestPluginsHandlerGetPluginsInRepoData(unittest.TestCase):
    """Tests for PluginsHandler.get_plugins_in_repo_data method."""

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
    def test_get_plugins_in_repo_data_empty_if_no_repo_key(self, mock_config, mock_logging):
        """Test get_plugins_in_repo_data returns empty list if no 'repo' key."""
        from unmanic.libs.plugins import PluginsHandler

        mock_logging.get_logger.return_value = MagicMock()
        mock_config.return_value = MagicMock()

        handler = PluginsHandler()
        result = handler.get_plugins_in_repo_data({"plugins": []})

        self.assertEqual(result, [])

    @patch("unmanic.libs.plugins.UnmanicLogging")
    @patch("unmanic.libs.plugins.config.Config")
    def test_get_plugins_in_repo_data_empty_if_no_plugins_key(self, mock_config, mock_logging):
        """Test get_plugins_in_repo_data returns empty list if no 'plugins' key."""
        from unmanic.libs.plugins import PluginsHandler

        mock_logging.get_logger.return_value = MagicMock()
        mock_config.return_value = MagicMock()

        handler = PluginsHandler()
        result = handler.get_plugins_in_repo_data({"repo": {}})

        self.assertEqual(result, [])

    @patch("unmanic.libs.plugins.UnmanicLogging")
    @patch("unmanic.libs.plugins.config.Config")
    def test_get_plugins_in_repo_data_empty_if_no_repo_data_directory(self, mock_config, mock_logging):
        """Test returns empty list if no repo_data_directory."""
        from unmanic.libs.plugins import PluginsHandler

        mock_logging.get_logger.return_value = MagicMock()
        mock_config.return_value = MagicMock()

        handler = PluginsHandler()
        result = handler.get_plugins_in_repo_data({"repo": {}, "plugins": []})

        self.assertEqual(result, [])


class TestPluginsHandlerReadRemoteChangelog(unittest.TestCase):
    """Tests for PluginsHandler.read_remote_changelog_file method."""

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

    @patch("unmanic.libs.plugins.requests.get")
    @patch("unmanic.libs.plugins.UnmanicLogging")
    @patch("unmanic.libs.plugins.config.Config")
    def test_read_remote_changelog_success(self, mock_config, mock_logging, mock_get):
        """Test read_remote_changelog_file returns content on success."""
        from unmanic.libs.plugins import PluginsHandler

        mock_logging.get_logger.return_value = MagicMock()
        mock_config.return_value = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "# Changelog\n- v1.0.0"
        mock_get.return_value = mock_response

        handler = PluginsHandler()
        result = handler.read_remote_changelog_file("https://example.com/changelog.md")

        self.assertEqual(result, "# Changelog\n- v1.0.0")

    @patch("unmanic.libs.plugins.requests.get")
    @patch("unmanic.libs.plugins.UnmanicLogging")
    @patch("unmanic.libs.plugins.config.Config")
    def test_read_remote_changelog_returns_empty_on_failure(self, mock_config, mock_logging, mock_get):
        """Test read_remote_changelog_file returns empty string on failure."""
        from unmanic.libs.plugins import PluginsHandler

        mock_logging.get_logger.return_value = MagicMock()
        mock_config.return_value = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response

        handler = PluginsHandler()
        result = handler.read_remote_changelog_file("https://example.com/changelog.md")

        self.assertEqual(result, "")


class TestPluginsHandlerWritePluginDataToDb(unittest.TestCase):
    """Tests for PluginsHandler.write_plugin_data_to_db static method."""

    @patch("unmanic.libs.plugins.Plugins")
    def test_write_plugin_data_inserts_new_plugin(self, mock_plugins):
        """Test write_plugin_data_to_db inserts new plugin."""
        from unmanic.libs.plugins import PluginsHandler

        mock_plugins.get_or_none.return_value = None
        mock_plugins.insert.return_value.execute.return_value = True

        plugin = {
            "plugin_id": "test_plugin",
            "name": "Test Plugin",
            "author": "Test Author",
            "version": "1.0.0",
            "tags": "test",
            "description": "Test description",
            "icon": "icon.png",
        }

        result = PluginsHandler.write_plugin_data_to_db(plugin, "/tmp/plugins/test_plugin")

        self.assertTrue(result)
        mock_plugins.insert.assert_called_once()

    @patch("unmanic.libs.plugins.Plugins")
    def test_write_plugin_data_updates_existing_plugin(self, mock_plugins):
        """Test write_plugin_data_to_db updates existing plugin."""
        from unmanic.libs.plugins import PluginsHandler

        mock_plugins.get_or_none.return_value = MagicMock()
        mock_plugins.update.return_value.where.return_value.execute.return_value = True

        plugin = {
            "plugin_id": "test_plugin",
            "name": "Test Plugin",
            "author": "Test Author",
            "version": "1.0.0",
            "tags": "test",
            "description": "Test description",
            "icon": "icon.png",
        }

        result = PluginsHandler.write_plugin_data_to_db(plugin, "/tmp/plugins/test_plugin")

        self.assertTrue(result)
        mock_plugins.update.assert_called_once()


class TestPluginsHandlerGetTotalPluginCount(unittest.TestCase):
    """Tests for PluginsHandler.get_total_plugin_list_count method."""

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

    @patch("unmanic.libs.plugins.Plugins")
    @patch("unmanic.libs.plugins.UnmanicLogging")
    @patch("unmanic.libs.plugins.config.Config")
    def test_get_total_plugin_list_count(self, mock_config, mock_logging, mock_plugins):
        """Test get_total_plugin_list_count returns count."""
        from unmanic.libs.plugins import PluginsHandler

        mock_logging.get_logger.return_value = MagicMock()
        mock_config.return_value = MagicMock()
        mock_plugins.select.return_value.order_by.return_value.count.return_value = 5

        handler = PluginsHandler()
        result = handler.get_total_plugin_list_count()

        self.assertEqual(result, 5)


class TestPluginsHandlerGetPluginTypesWithFlows(unittest.TestCase):
    """Tests for PluginsHandler.get_plugin_types_with_flows static method."""

    @patch("unmanic.libs.plugins.PluginExecutor")
    def test_get_plugin_types_with_flows_filters_by_has_flow(self, mock_executor):
        """Test get_plugin_types_with_flows filters by has_flow."""
        from unmanic.libs.plugins import PluginsHandler

        mock_executor_instance = MagicMock()
        mock_executor_instance.get_all_plugin_types.return_value = [
            {"id": "type1", "has_flow": True},
            {"id": "type2", "has_flow": False},
            {"id": "type3", "has_flow": True},
        ]
        mock_executor.return_value = mock_executor_instance

        result = PluginsHandler.get_plugin_types_with_flows()

        self.assertEqual(result, ["type1", "type3"])

    @patch("unmanic.libs.plugins.PluginExecutor")
    def test_get_plugin_types_with_flows_returns_empty_if_none(self, mock_executor):
        """Test get_plugin_types_with_flows returns empty list if no flows."""
        from unmanic.libs.plugins import PluginsHandler

        mock_executor_instance = MagicMock()
        mock_executor_instance.get_all_plugin_types.return_value = [
            {"id": "type1", "has_flow": False},
            {"id": "type2", "has_flow": False},
        ]
        mock_executor.return_value = mock_executor_instance

        result = PluginsHandler.get_plugin_types_with_flows()

        self.assertEqual(result, [])


class TestPluginsHandlerInstallPluginRequirements(unittest.TestCase):
    """Tests for PluginsHandler.install_plugin_requirements static method."""

    @patch("unmanic.libs.plugins.os.path.exists")
    def test_install_plugin_requirements_skips_if_no_requirements(self, mock_exists):
        """Test install_plugin_requirements skips if requirements.txt doesn't exist."""
        from unmanic.libs.plugins import PluginsHandler

        mock_exists.return_value = False

        result = PluginsHandler.install_plugin_requirements("/tmp/plugin")

        self.assertIsNone(result)

    @patch("unmanic.libs.plugins.subprocess.call")
    @patch("unmanic.libs.plugins.os.makedirs")
    @patch("unmanic.libs.plugins.shutil.rmtree")
    @patch("unmanic.libs.plugins.os.path.exists")
    def test_install_plugin_requirements_runs_pip(self, mock_exists, mock_rmtree, mock_makedirs, mock_call):
        """Test install_plugin_requirements runs pip install."""
        from unmanic.libs.plugins import PluginsHandler

        mock_exists.return_value = True

        PluginsHandler.install_plugin_requirements("/tmp/plugin")

        mock_call.assert_called_once()


class TestPluginsHandlerInstallNpmModules(unittest.TestCase):
    """Tests for PluginsHandler.install_npm_modules static method."""

    @patch("unmanic.libs.plugins.os.path.exists")
    def test_install_npm_modules_skips_if_no_package_json(self, mock_exists):
        """Test install_npm_modules skips if package.json doesn't exist."""
        from unmanic.libs.plugins import PluginsHandler

        mock_exists.return_value = False

        result = PluginsHandler.install_npm_modules("/tmp/plugin")

        self.assertIsNone(result)

    @patch("unmanic.libs.plugins.subprocess.call")
    @patch("unmanic.libs.plugins.os.path.exists")
    def test_install_npm_modules_runs_npm_install_and_build(self, mock_exists, mock_call):
        """Test install_npm_modules runs npm install and build."""
        from unmanic.libs.plugins import PluginsHandler

        mock_exists.return_value = True

        PluginsHandler.install_npm_modules("/tmp/plugin")

        self.assertEqual(mock_call.call_count, 2)


class TestPluginsHandlerSetPluginRepos(unittest.TestCase):
    """Tests for PluginsHandler.set_plugin_repos method."""

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

    @patch("unmanic.libs.plugins.PluginRepos")
    @patch("unmanic.libs.plugins.UnmanicLogging")
    @patch("unmanic.libs.plugins.config.Config")
    def test_set_plugin_repos_returns_false_if_invalid_repo(self, mock_config, mock_logging, mock_plugin_repos):
        """Test set_plugin_repos returns False if repo validation fails."""
        from unmanic.libs.plugins import PluginsHandler

        mock_logging.get_logger.return_value = MagicMock()
        mock_config.return_value = MagicMock()

        handler = PluginsHandler()
        # Patch fetch_remote_repo_data to return None (validation failure)
        handler.fetch_remote_repo_data = MagicMock(return_value=None)

        result = handler.set_plugin_repos(["invalid/repo"])

        self.assertFalse(result)

    @patch("unmanic.libs.plugins.PluginRepos")
    @patch("unmanic.libs.plugins.UnmanicLogging")
    @patch("unmanic.libs.plugins.config.Config")
    def test_set_plugin_repos_inserts_valid_repos(self, mock_config, mock_logging, mock_plugin_repos):
        """Test set_plugin_repos inserts valid repos."""
        from unmanic.libs.plugins import PluginsHandler

        mock_logging.get_logger.return_value = MagicMock()
        mock_config.return_value = MagicMock()
        mock_plugin_repos.insert_many.return_value.execute.return_value = True

        handler = PluginsHandler()
        handler.fetch_remote_repo_data = MagicMock(return_value={"success": True})

        result = handler.set_plugin_repos(["valid/repo1", "valid/repo2"])

        self.assertTrue(result)
        mock_plugin_repos.delete.return_value.execute.assert_called()
        mock_plugin_repos.insert_many.assert_called_once()


class TestPluginsHandlerFlagPluginForUpdate(unittest.TestCase):
    """Tests for PluginsHandler.flag_plugin_for_update_by_id method."""

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

    @patch("unmanic.libs.plugins.Plugins")
    @patch("unmanic.libs.plugins.UnmanicLogging")
    @patch("unmanic.libs.plugins.config.Config")
    def test_flag_plugin_for_update_updates_db(self, mock_config, mock_logging, mock_plugins):
        """Test flag_plugin_for_update_by_id updates database."""
        from unmanic.libs.plugins import PluginsHandler

        mock_logging.get_logger.return_value = MagicMock()
        mock_config.return_value = MagicMock()
        mock_plugins.update.return_value.where.return_value.execute.return_value = True

        handler = PluginsHandler()
        handler.get_plugin_list_filtered_and_sorted = MagicMock(return_value=[{"plugin_id": "test", "update_available": True}])

        result = handler.flag_plugin_for_update_by_id("test_plugin")

        self.assertTrue(result)
        mock_plugins.update.assert_called_once()

    @patch("unmanic.libs.plugins.Plugins")
    @patch("unmanic.libs.plugins.UnmanicLogging")
    @patch("unmanic.libs.plugins.config.Config")
    def test_flag_plugin_returns_false_if_flag_failed(self, mock_config, mock_logging, mock_plugins):
        """Test flag_plugin_for_update_by_id returns False if flagging failed."""
        from unmanic.libs.plugins import PluginsHandler

        mock_logging.get_logger.return_value = MagicMock()
        mock_config.return_value = MagicMock()
        mock_plugins.update.return_value.where.return_value.execute.return_value = True

        handler = PluginsHandler()
        handler.get_plugin_list_filtered_and_sorted = MagicMock(
            return_value=[{"plugin_id": "test", "update_available": False}]
        )

        result = handler.flag_plugin_for_update_by_id("test_plugin")

        self.assertFalse(result)


class TestPluginsHandlerSetPluginFlow(unittest.TestCase):
    """Tests for PluginsHandler.set_plugin_flow method."""

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

    @patch("unmanic.libs.plugins.LibraryPluginFlow")
    @patch("unmanic.libs.plugins.Plugins")
    @patch("unmanic.libs.plugins.UnmanicLogging")
    @patch("unmanic.libs.plugins.config.Config")
    def test_set_plugin_flow_deletes_existing_flow(self, mock_config, mock_logging, mock_plugins, mock_flow):
        """Test set_plugin_flow deletes existing flow first."""
        from unmanic.libs.plugins import PluginsHandler

        mock_logging.get_logger.return_value = MagicMock()
        mock_config.return_value = MagicMock()
        mock_flow.delete.return_value.where.return_value.execute.return_value = True
        mock_plugins.select.return_value.where.return_value.first.return_value = None

        handler = PluginsHandler()
        result = handler.set_plugin_flow("worker.process_item", 1, [])

        self.assertTrue(result)
        mock_flow.delete.assert_called_once()

    @patch("unmanic.libs.plugins.LibraryPluginFlow")
    @patch("unmanic.libs.plugins.Plugins")
    @patch("unmanic.libs.plugins.UnmanicLogging")
    @patch("unmanic.libs.plugins.config.Config")
    def test_set_plugin_flow_skips_nonexistent_plugins(self, mock_config, mock_logging, mock_plugins, mock_flow):
        """Test set_plugin_flow skips plugins that don't exist."""
        from unmanic.libs.plugins import PluginsHandler

        mock_logging.get_logger.return_value = MagicMock()
        mock_config.return_value = MagicMock()
        mock_flow.delete.return_value.where.return_value.execute.return_value = True
        mock_plugins.select.return_value.where.return_value.first.return_value = None

        handler = PluginsHandler()
        result = handler.set_plugin_flow("worker.process_item", 1, [{"plugin_id": "nonexistent"}])

        self.assertTrue(result)


class TestPluginsHandlerSetPluginFlowPosition(unittest.TestCase):
    """Tests for PluginsHandler.set_plugin_flow_position_for_single_plugin static method."""

    @patch("unmanic.libs.plugins.LibraryPluginFlow")
    def test_set_plugin_flow_position_creates_entry(self, mock_flow):
        """Test set_plugin_flow_position_for_single_plugin creates flow entry."""
        from unmanic.libs.plugins import PluginsHandler

        mock_plugin_info = MagicMock()
        mock_plugin_info.id = 1
        mock_plugin_info.plugin_id = "test_plugin"
        mock_flow.create.return_value = MagicMock()

        result = PluginsHandler.set_plugin_flow_position_for_single_plugin(mock_plugin_info, "worker.process_item", 1, 1)

        mock_flow.create.assert_called_once()
        self.assertIsNotNone(result)


class TestPluginsHandlerGetPluginsInRepoDataWithPlugins(unittest.TestCase):
    """Tests for PluginsHandler.get_plugins_in_repo_data with actual plugins."""

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
    def test_get_plugins_in_repo_data_filters_by_compatibility(self, mock_config, mock_logging):
        """Test get_plugins_in_repo_data filters out incompatible plugins."""
        from unmanic.libs.plugins import PluginsHandler

        mock_logging.get_logger.return_value = MagicMock()
        mock_config_instance = MagicMock()
        mock_config_instance.get_plugins_path.return_value = "/tmp/plugins"
        mock_config.return_value = mock_config_instance

        handler = PluginsHandler()
        handler.get_plugin_info = MagicMock(return_value={})

        repo_data = {
            "repo": {"name": "Test Repo", "repo_data_directory": "https://example.com/plugins"},
            "plugins": [
                {"id": "compatible", "name": "Compatible", "version": "1.0.0", "compatibility": [2]},
                {"id": "incompatible", "name": "Incompatible", "version": "1.0.0", "compatibility": [1]},
            ],
        }

        result = handler.get_plugins_in_repo_data(repo_data)

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["plugin_id"], "compatible")

    @patch("unmanic.libs.plugins.UnmanicLogging")
    @patch("unmanic.libs.plugins.config.Config")
    def test_get_plugins_in_repo_data_marks_installed_plugin(self, mock_config, mock_logging):
        """Test get_plugins_in_repo_data marks installed plugins."""
        from unmanic.libs.plugins import PluginsHandler

        mock_logging.get_logger.return_value = MagicMock()
        mock_config_instance = MagicMock()
        mock_config_instance.get_plugins_path.return_value = "/tmp/plugins"
        mock_config.return_value = mock_config_instance

        handler = PluginsHandler()
        handler.get_plugin_info = MagicMock(return_value={"version": "1.0.0"})
        handler.flag_plugin_for_update_by_id = MagicMock()

        repo_data = {
            "repo": {"name": "Test Repo", "repo_data_directory": "https://example.com/plugins"},
            "plugins": [
                {
                    "id": "installed",
                    "name": "Installed Plugin",
                    "version": "1.0.0",
                    "compatibility": [2],
                    "author": "Test",
                    "description": "Test",
                    "tags": [],
                },
            ],
        }

        result = handler.get_plugins_in_repo_data(repo_data)

        self.assertEqual(len(result), 1)
        self.assertTrue(result[0]["status"]["installed"])
        self.assertFalse(result[0]["status"]["update_available"])

    @patch("unmanic.libs.plugins.UnmanicLogging")
    @patch("unmanic.libs.plugins.config.Config")
    def test_get_plugins_in_repo_data_marks_update_available(self, mock_config, mock_logging):
        """Test get_plugins_in_repo_data marks plugins with updates available."""
        from unmanic.libs.plugins import PluginsHandler

        mock_logging.get_logger.return_value = MagicMock()
        mock_config_instance = MagicMock()
        mock_config_instance.get_plugins_path.return_value = "/tmp/plugins"
        mock_config.return_value = mock_config_instance

        handler = PluginsHandler()
        handler.get_plugin_info = MagicMock(return_value={"version": "0.9.0"})
        handler.flag_plugin_for_update_by_id = MagicMock()

        repo_data = {
            "repo": {"name": "Test Repo", "repo_data_directory": "https://example.com/plugins"},
            "plugins": [
                {
                    "id": "outdated",
                    "name": "Outdated Plugin",
                    "version": "1.0.0",
                    "compatibility": [2],
                    "author": "Test",
                    "description": "Test",
                    "tags": [],
                },
            ],
        }

        result = handler.get_plugins_in_repo_data(repo_data)

        self.assertEqual(len(result), 1)
        self.assertTrue(result[0]["status"]["installed"])
        self.assertTrue(result[0]["status"]["update_available"])
        handler.flag_plugin_for_update_by_id.assert_called_once_with("outdated")


class TestPluginsHandlerGetInstallablePluginsList(unittest.TestCase):
    """Tests for PluginsHandler.get_installable_plugins_list method."""

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
    def test_get_installable_plugins_list_aggregates_from_repos(self, mock_config, mock_logging):
        """Test get_installable_plugins_list aggregates plugins from all repos."""
        from unmanic.libs.plugins import PluginsHandler

        mock_logging.get_logger.return_value = MagicMock()
        mock_config_instance = MagicMock()
        mock_config_instance.get_plugins_path.return_value = "/tmp/plugins"
        mock_config.return_value = mock_config_instance

        handler = PluginsHandler()
        handler.get_plugin_repos = MagicMock(return_value=[{"path": "repo1"}, {"path": "repo2"}])
        handler.read_repo_data = MagicMock(return_value={})
        handler.get_plugins_in_repo_data = MagicMock(side_effect=[[{"plugin_id": "p1"}], [{"plugin_id": "p2"}]])

        result = handler.get_installable_plugins_list()

        self.assertEqual(len(result), 2)

    @patch("unmanic.libs.plugins.UnmanicLogging")
    @patch("unmanic.libs.plugins.config.Config")
    def test_get_installable_plugins_list_filters_by_repo_id(self, mock_config, mock_logging):
        """Test get_installable_plugins_list can filter by repo_id."""
        from unmanic.libs.plugins import PluginsHandler

        mock_logging.get_logger.return_value = MagicMock()
        mock_config_instance = MagicMock()
        mock_config_instance.get_plugins_path.return_value = "/tmp/plugins"
        mock_config.return_value = mock_config_instance

        handler = PluginsHandler()
        handler.get_plugin_repos = MagicMock(return_value=[{"path": "repo1"}])
        handler.read_repo_data = MagicMock(return_value={})
        handler.get_plugins_in_repo_data = MagicMock(return_value=[{"plugin_id": "p1"}])

        repo_id = PluginsHandler.get_plugin_repo_id("repo1")
        result = handler.get_installable_plugins_list(filter_repo_id=repo_id)

        self.assertEqual(len(result), 1)


class TestPluginsHandlerGetPluginListFilteredAndSorted(unittest.TestCase):
    """Tests for PluginsHandler.get_plugin_list_filtered_and_sorted method."""

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

    @patch("unmanic.libs.plugins.Plugins")
    @patch("unmanic.libs.plugins.UnmanicLogging")
    @patch("unmanic.libs.plugins.config.Config")
    def test_get_plugin_list_basic_query(self, mock_config, mock_logging, mock_plugins):
        """Test get_plugin_list_filtered_and_sorted basic query."""
        from unmanic.libs.plugins import PluginsHandler

        mock_logging.get_logger.return_value = MagicMock()
        mock_config.return_value = MagicMock()
        mock_plugins.select.return_value.dicts.return_value = [{"id": 1, "name": "Test"}]

        handler = PluginsHandler()
        result = handler.get_plugin_list_filtered_and_sorted()

        self.assertIsNotNone(result)

    @patch("unmanic.libs.plugins.UnmanicLogging")
    @patch("unmanic.libs.plugins.config.Config")
    def test_get_plugin_list_raises_on_enabled_param(self, mock_config, mock_logging):
        """Test get_plugin_list_filtered_and_sorted raises on enabled param."""
        from unmanic.libs.plugins import PluginsHandler

        mock_logging.get_logger.return_value = MagicMock()
        mock_config.return_value = MagicMock()

        handler = PluginsHandler()

        with self.assertRaises(Exception) as context:
            handler.get_plugin_list_filtered_and_sorted(enabled=True)

        self.assertIn("deprecated", str(context.exception).lower())


class TestPluginsHandlerUpdatePluginsByDbTableId(unittest.TestCase):
    """Tests for PluginsHandler.update_plugins_by_db_table_id method."""

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

    @patch("unmanic.libs.plugins.Plugins")
    @patch("unmanic.libs.plugins.UnmanicLogging")
    @patch("unmanic.libs.plugins.config.Config")
    def test_update_plugins_success(self, mock_config, mock_logging, mock_plugins):
        """Test update_plugins_by_db_table_id success path."""
        from unmanic.libs.plugins import PluginsHandler

        mock_logging.get_logger.return_value = MagicMock()
        mock_config.return_value = MagicMock()

        handler = PluginsHandler()
        handler.get_plugin_list_filtered_and_sorted = MagicMock(return_value=[{"plugin_id": "test"}])
        handler.install_plugin_by_id = MagicMock(return_value=True)

        result = handler.update_plugins_by_db_table_id([1])

        self.assertTrue(result)
        handler.install_plugin_by_id.assert_called_once_with("test")

    @patch("unmanic.libs.plugins.Plugins")
    @patch("unmanic.libs.plugins.UnmanicLogging")
    @patch("unmanic.libs.plugins.config.Config")
    def test_update_plugins_failure(self, mock_config, mock_logging, mock_plugins):
        """Test update_plugins_by_db_table_id returns False on failure."""
        from unmanic.libs.plugins import PluginsHandler

        mock_logging.get_logger.return_value = MagicMock()
        mock_config.return_value = MagicMock()

        handler = PluginsHandler()
        handler.get_plugin_list_filtered_and_sorted = MagicMock(return_value=[{"plugin_id": "test"}])
        handler.install_plugin_by_id = MagicMock(return_value=False)

        result = handler.update_plugins_by_db_table_id([1])

        self.assertFalse(result)


class TestPluginsHandlerExecPluginRunner(unittest.TestCase):
    """Tests for PluginsHandler.exec_plugin_runner method."""

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

    @patch("unmanic.libs.plugins.PluginExecutor")
    @patch("unmanic.libs.plugins.UnmanicLogging")
    @patch("unmanic.libs.plugins.config.Config")
    def test_exec_plugin_runner_delegates_to_executor(self, mock_config, mock_logging, mock_executor):
        """Test exec_plugin_runner delegates to PluginExecutor."""
        from unmanic.libs.plugins import PluginsHandler

        mock_logging.get_logger.return_value = MagicMock()
        mock_config.return_value = MagicMock()
        mock_executor_instance = MagicMock()
        mock_executor_instance.execute_plugin_runner.return_value = True
        mock_executor.return_value = mock_executor_instance

        handler = PluginsHandler()
        result = handler.exec_plugin_runner({"test": "data"}, "plugin_id", "worker.process_item")

        self.assertTrue(result)
        mock_executor_instance.execute_plugin_runner.assert_called_once()


class TestPluginsHandlerGetSettingsOfAllInstalledPlugins(unittest.TestCase):
    """Tests for PluginsHandler.get_settings_of_all_installed_plugins method."""

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

    @patch("unmanic.libs.plugins.PluginExecutor")
    @patch("unmanic.libs.plugins.UnmanicLogging")
    @patch("unmanic.libs.plugins.config.Config")
    def test_get_settings_fetches_from_executor(self, mock_config, mock_logging, mock_executor):
        """Test get_settings_of_all_installed_plugins fetches settings."""
        from unmanic.libs.plugins import PluginsHandler

        mock_logging.get_logger.return_value = MagicMock()
        mock_config.return_value = MagicMock()
        mock_executor_instance = MagicMock()
        mock_executor_instance.get_plugin_settings.return_value = ({"setting": "value"}, {})
        mock_executor.return_value = mock_executor_instance

        handler = PluginsHandler()
        handler.get_plugin_list_filtered_and_sorted = MagicMock(return_value=[{"plugin_id": "test_plugin"}])

        result = handler.get_settings_of_all_installed_plugins()

        self.assertEqual(result, {"test_plugin": {"setting": "value"}})


class TestPluginsHandlerReadRepoDataWithFile(unittest.TestCase):
    """Tests for PluginsHandler.read_repo_data when file exists."""

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

    @patch("builtins.open", create=True)
    @patch("unmanic.libs.plugins.json.load")
    @patch("unmanic.libs.plugins.os.makedirs")
    @patch("unmanic.libs.plugins.os.path.exists")
    @patch("unmanic.libs.plugins.UnmanicLogging")
    @patch("unmanic.libs.plugins.config.Config")
    def test_read_repo_data_reads_json_file(
        self, mock_config, mock_logging, mock_exists, mock_makedirs, mock_json_load, mock_open
    ):
        """Test read_repo_data reads JSON file when it exists."""
        from unmanic.libs.plugins import PluginsHandler

        mock_logging.get_logger.return_value = MagicMock()
        mock_config_instance = MagicMock()
        mock_config_instance.get_plugins_path.return_value = "/tmp/test_plugins"
        mock_config.return_value = mock_config_instance
        mock_exists.return_value = True
        mock_json_load.return_value = {"repo": "data"}
        mock_open.return_value.__enter__ = MagicMock(return_value=MagicMock())
        mock_open.return_value.__exit__ = MagicMock(return_value=False)

        handler = PluginsHandler()
        result = handler.read_repo_data(12345)

        self.assertEqual(result, {"repo": "data"})


class TestPluginsHandlerGetPluginInfoWithFile(unittest.TestCase):
    """Tests for PluginsHandler.get_plugin_info when file exists."""

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

    @patch("builtins.open", create=True)
    @patch("unmanic.libs.plugins.json.load")
    @patch("unmanic.libs.plugins.os.path.exists")
    @patch("unmanic.libs.plugins.UnmanicLogging")
    @patch("unmanic.libs.plugins.config.Config")
    def test_get_plugin_info_reads_json_file(self, mock_config, mock_logging, mock_exists, mock_json_load, mock_open):
        """Test get_plugin_info reads JSON file when it exists."""
        from unmanic.libs.plugins import PluginsHandler

        mock_logging.get_logger.return_value = MagicMock()
        mock_config_instance = MagicMock()
        mock_config_instance.get_plugins_path.return_value = "/tmp/test_plugins"
        mock_config.return_value = mock_config_instance
        mock_exists.return_value = True
        mock_json_load.return_value = {"id": "test", "version": "1.0.0"}
        mock_open.return_value.__enter__ = MagicMock(return_value=MagicMock())
        mock_open.return_value.__exit__ = MagicMock(return_value=False)

        handler = PluginsHandler()
        result = handler.get_plugin_info("test_plugin")

        self.assertEqual(result, {"id": "test", "version": "1.0.0"})


class TestPluginsHandlerGetPluginListAdvanced(unittest.TestCase):
    """Advanced tests for PluginsHandler.get_plugin_list_filtered_and_sorted method."""

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

    @patch("unmanic.libs.plugins.LibraryPluginFlow")
    @patch("unmanic.libs.plugins.Plugins")
    @patch("unmanic.libs.plugins.UnmanicLogging")
    @patch("unmanic.libs.plugins.config.Config")
    def test_get_plugin_list_with_plugin_type(self, mock_config, mock_logging, mock_plugins, mock_flow):
        """Test get_plugin_list_filtered_and_sorted with plugin_type filter."""
        from unmanic.libs.plugins import PluginsHandler

        mock_logging.get_logger.return_value = MagicMock()
        mock_config.return_value = MagicMock()
        mock_query = MagicMock()
        mock_query.dicts.return_value = [{"id": 1}]
        mock_plugins.select.return_value.join.return_value = mock_query

        handler = PluginsHandler()
        result = handler.get_plugin_list_filtered_and_sorted(plugin_type="worker.process_item")

        self.assertIsNotNone(result)
        mock_plugins.select.return_value.join.assert_called()

    @patch("unmanic.libs.plugins.LibraryPluginFlow")
    @patch("unmanic.libs.plugins.Plugins")
    @patch("unmanic.libs.plugins.UnmanicLogging")
    @patch("unmanic.libs.plugins.config.Config")
    def test_get_plugin_list_with_plugin_type_and_library_id(self, mock_config, mock_logging, mock_plugins, mock_flow):
        """Test get_plugin_list_filtered_and_sorted with plugin_type and library_id."""
        from unmanic.libs.plugins import PluginsHandler

        mock_logging.get_logger.return_value = MagicMock()
        mock_config.return_value = MagicMock()
        mock_query = MagicMock()
        mock_query.dicts.return_value = [{"id": 1}]
        mock_plugins.select.return_value.join.return_value = mock_query

        handler = PluginsHandler()
        result = handler.get_plugin_list_filtered_and_sorted(plugin_type="worker.process_item", library_id=1)

        self.assertIsNotNone(result)

    @patch("unmanic.libs.plugins.Plugins")
    @patch("unmanic.libs.plugins.UnmanicLogging")
    @patch("unmanic.libs.plugins.config.Config")
    def test_get_plugin_list_with_search_value(self, mock_config, mock_logging, mock_plugins):
        """Test get_plugin_list_filtered_and_sorted with search_value."""
        from unmanic.libs.plugins import PluginsHandler

        mock_logging.get_logger.return_value = MagicMock()
        mock_config.return_value = MagicMock()
        mock_query = MagicMock()
        mock_query.where.return_value.dicts.return_value = [{"id": 1, "name": "Test Plugin"}]
        mock_plugins.select.return_value = mock_query
        mock_plugins.name = MagicMock()
        mock_plugins.author = MagicMock()
        mock_plugins.tags = MagicMock()

        handler = PluginsHandler()
        result = handler.get_plugin_list_filtered_and_sorted(search_value="Test")

        self.assertIsNotNone(result)

    @patch("unmanic.libs.plugins.Plugins")
    @patch("unmanic.libs.plugins.UnmanicLogging")
    @patch("unmanic.libs.plugins.config.Config")
    def test_get_plugin_list_with_id_list(self, mock_config, mock_logging, mock_plugins):
        """Test get_plugin_list_filtered_and_sorted with id_list filter."""
        from unmanic.libs.plugins import PluginsHandler

        mock_logging.get_logger.return_value = MagicMock()
        mock_config.return_value = MagicMock()
        mock_query = MagicMock()
        mock_query.where.return_value.dicts.return_value = [{"id": 1}]
        mock_plugins.select.return_value = mock_query
        mock_plugins.id = MagicMock()

        handler = PluginsHandler()
        result = handler.get_plugin_list_filtered_and_sorted(id_list=[1, 2, 3])

        self.assertIsNotNone(result)

    @patch("unmanic.libs.plugins.Plugins")
    @patch("unmanic.libs.plugins.UnmanicLogging")
    @patch("unmanic.libs.plugins.config.Config")
    def test_get_plugin_list_with_plugin_id(self, mock_config, mock_logging, mock_plugins):
        """Test get_plugin_list_filtered_and_sorted with plugin_id filter."""
        from unmanic.libs.plugins import PluginsHandler

        mock_logging.get_logger.return_value = MagicMock()
        mock_config.return_value = MagicMock()
        mock_query = MagicMock()
        mock_query.where.return_value.dicts.return_value = [{"id": 1, "plugin_id": "test"}]
        mock_plugins.select.return_value = mock_query
        mock_plugins.plugin_id = MagicMock()

        handler = PluginsHandler()
        result = handler.get_plugin_list_filtered_and_sorted(plugin_id="test")

        self.assertIsNotNone(result)

    @patch("unmanic.libs.plugins.EnabledPlugins")
    @patch("unmanic.libs.plugins.Plugins")
    @patch("unmanic.libs.plugins.UnmanicLogging")
    @patch("unmanic.libs.plugins.config.Config")
    def test_get_plugin_list_with_library_id_only(self, mock_config, mock_logging, mock_plugins, mock_enabled):
        """Test get_plugin_list_filtered_and_sorted with library_id only."""
        from unmanic.libs.plugins import PluginsHandler

        mock_logging.get_logger.return_value = MagicMock()
        mock_config.return_value = MagicMock()
        mock_query = MagicMock()
        mock_query.join.return_value.where.return_value.dicts.return_value = [{"id": 1}]
        mock_plugins.select.return_value = mock_query
        mock_enabled.plugin_id = MagicMock()
        mock_enabled.library_id = MagicMock()

        handler = PluginsHandler()
        result = handler.get_plugin_list_filtered_and_sorted(library_id=1)

        self.assertIsNotNone(result)

    @patch("unmanic.libs.plugins.Plugins")
    @patch("unmanic.libs.plugins.UnmanicLogging")
    @patch("unmanic.libs.plugins.config.Config")
    def test_get_plugin_list_with_length_and_start(self, mock_config, mock_logging, mock_plugins):
        """Test get_plugin_list_filtered_and_sorted with length and start."""
        from unmanic.libs.plugins import PluginsHandler

        mock_logging.get_logger.return_value = MagicMock()
        mock_config.return_value = MagicMock()
        mock_query = MagicMock()
        mock_query.limit.return_value.offset.return_value.dicts.return_value = [{"id": 1}]
        mock_plugins.select.return_value = mock_query

        handler = PluginsHandler()
        result = handler.get_plugin_list_filtered_and_sorted(length=10, start=5)

        self.assertIsNotNone(result)
        mock_query.limit.assert_called_with(10)


class TestPluginsHandlerUninstallPlugins(unittest.TestCase):
    """Tests for PluginsHandler.uninstall_plugins_by_db_table_id method."""

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

    @patch("unmanic.libs.plugins.shutil.rmtree")
    @patch("unmanic.libs.plugins.os.remove")
    @patch("unmanic.libs.plugins.os.path.exists")
    @patch("unmanic.libs.plugins.EnabledPlugins")
    @patch("unmanic.libs.plugins.Plugins")
    @patch("unmanic.libs.plugins.PluginExecutor")
    @patch("unmanic.libs.plugins.UnmanicLogging")
    @patch("unmanic.libs.plugins.config.Config")
    def test_uninstall_plugins_success(
        self, mock_config, mock_logging, mock_executor, mock_plugins, mock_enabled, mock_exists, mock_remove, mock_rmtree
    ):
        """Test uninstall_plugins_by_db_table_id success path."""
        from unmanic.libs.plugins import PluginsHandler

        mock_logging.get_logger.return_value = MagicMock()
        mock_config_instance = MagicMock()
        mock_config_instance.get_plugins_path.return_value = "/tmp/plugins"
        mock_config.return_value = mock_config_instance
        mock_exists.return_value = True
        mock_plugins.delete.return_value.where.return_value.execute.return_value = True

        handler = PluginsHandler()
        handler.get_plugin_list_filtered_and_sorted = MagicMock(return_value=[{"plugin_id": "test"}])

        result = handler.uninstall_plugins_by_db_table_id([1])

        self.assertTrue(result)
        mock_enabled.delete.return_value.where.return_value.execute.assert_called()
        mock_plugins.delete.return_value.where.return_value.execute.assert_called()

    @patch("unmanic.libs.plugins.shutil.rmtree")
    @patch("unmanic.libs.plugins.os.remove")
    @patch("unmanic.libs.plugins.os.path.exists")
    @patch("unmanic.libs.plugins.EnabledPlugins")
    @patch("unmanic.libs.plugins.Plugins")
    @patch("unmanic.libs.plugins.PluginExecutor")
    @patch("unmanic.libs.plugins.UnmanicLogging")
    @patch("unmanic.libs.plugins.config.Config")
    def test_uninstall_plugins_returns_false_on_db_failure(
        self, mock_config, mock_logging, mock_executor, mock_plugins, mock_enabled, mock_exists, mock_remove, mock_rmtree
    ):
        """Test uninstall_plugins_by_db_table_id returns False on DB deletion failure."""
        from unmanic.libs.plugins import PluginsHandler

        mock_logging.get_logger.return_value = MagicMock()
        mock_config_instance = MagicMock()
        mock_config_instance.get_plugins_path.return_value = "/tmp/plugins"
        mock_config.return_value = mock_config_instance
        mock_exists.return_value = True
        mock_plugins.delete.return_value.where.return_value.execute.return_value = False

        handler = PluginsHandler()
        handler.get_plugin_list_filtered_and_sorted = MagicMock(return_value=[{"plugin_id": "test"}])

        result = handler.uninstall_plugins_by_db_table_id([1])

        self.assertFalse(result)


class TestPluginsHandlerFetchRemoteRepoData(unittest.TestCase):
    """Tests for PluginsHandler.fetch_remote_repo_data method."""

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

    @patch("unmanic.libs.plugins.Session")
    @patch("unmanic.libs.plugins.UnmanicLogging")
    @patch("unmanic.libs.plugins.config.Config")
    def test_fetch_remote_repo_data_success(self, mock_config, mock_logging, mock_session):
        """Test fetch_remote_repo_data success path."""
        from unmanic.libs.plugins import PluginsHandler

        mock_logging.get_logger.return_value = MagicMock()
        mock_config.return_value = MagicMock()
        mock_session_instance = MagicMock()
        mock_session_instance.get_installation_uuid.return_value = "test-uuid"
        mock_session_instance.get_supporter_level.return_value = 0
        mock_session_instance.api_get.return_value = ({"plugins": []}, 200)
        mock_session.return_value = mock_session_instance

        handler = PluginsHandler()
        result = handler.fetch_remote_repo_data("https://example.com/repo")

        self.assertEqual(result, {"plugins": []})

    @patch("unmanic.libs.plugins.Session")
    @patch("unmanic.libs.plugins.UnmanicLogging")
    @patch("unmanic.libs.plugins.config.Config")
    def test_fetch_remote_repo_data_retries_on_401(self, mock_config, mock_logging, mock_session):
        """Test fetch_remote_repo_data retries on 401 status."""
        from unmanic.libs.plugins import PluginsHandler

        mock_logging.get_logger.return_value = MagicMock()
        mock_config.return_value = MagicMock()
        mock_session_instance = MagicMock()
        mock_session_instance.get_installation_uuid.return_value = "test-uuid"
        mock_session_instance.get_supporter_level.return_value = 0
        mock_session_instance.api_get.side_effect = [
            (None, 401),
            ({"plugins": []}, 200),
        ]
        mock_session.return_value = mock_session_instance

        handler = PluginsHandler()
        result = handler.fetch_remote_repo_data("https://example.com/repo")

        mock_session_instance.register_unmanic.assert_called_once()
        self.assertEqual(mock_session_instance.api_get.call_count, 2)

    @patch("unmanic.libs.plugins.Session")
    @patch("unmanic.libs.plugins.UnmanicLogging")
    @patch("unmanic.libs.plugins.config.Config")
    def test_fetch_remote_repo_data_logs_500_error(self, mock_config, mock_logging, mock_session):
        """Test fetch_remote_repo_data logs 500 errors."""
        from unmanic.libs.plugins import PluginsHandler

        mock_logger = MagicMock()
        mock_logging.get_logger.return_value = mock_logger
        mock_config.return_value = MagicMock()
        mock_session_instance = MagicMock()
        mock_session_instance.get_installation_uuid.return_value = "test-uuid"
        mock_session_instance.get_supporter_level.return_value = 0
        mock_session_instance.api_get.return_value = (None, 500)
        mock_session.return_value = mock_session_instance

        handler = PluginsHandler()
        result = handler.fetch_remote_repo_data("https://example.com/repo")

        mock_logger.debug.assert_called()


class TestPluginsHandlerUpdatePluginRepos(unittest.TestCase):
    """Tests for PluginsHandler.update_plugin_repos method."""

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

    @patch("builtins.open", create=True)
    @patch("unmanic.libs.plugins.json.dump")
    @patch("unmanic.libs.plugins.os.makedirs")
    @patch("unmanic.libs.plugins.os.path.exists")
    @patch("unmanic.libs.plugins.UnmanicLogging")
    @patch("unmanic.libs.plugins.config.Config")
    def test_update_plugin_repos_creates_cache_files(
        self, mock_config, mock_logging, mock_exists, mock_makedirs, mock_json_dump, mock_open
    ):
        """Test update_plugin_repos creates cache files."""
        from unmanic.libs.plugins import PluginsHandler

        mock_logging.get_logger.return_value = MagicMock()
        mock_config_instance = MagicMock()
        mock_config_instance.get_plugins_path.return_value = "/tmp/plugins"
        mock_config.return_value = mock_config_instance
        mock_exists.return_value = True
        mock_open.return_value.__enter__ = MagicMock(return_value=MagicMock())
        mock_open.return_value.__exit__ = MagicMock(return_value=False)

        handler = PluginsHandler()
        handler.get_plugin_repos = MagicMock(return_value=[{"path": "repo1"}])
        handler.fetch_remote_repo_data = MagicMock(return_value={"plugins": []})

        result = handler.update_plugin_repos()

        self.assertTrue(result)
        mock_json_dump.assert_called()

    @patch("unmanic.libs.plugins.os.makedirs")
    @patch("unmanic.libs.plugins.os.path.exists")
    @patch("unmanic.libs.plugins.UnmanicLogging")
    @patch("unmanic.libs.plugins.config.Config")
    def test_update_plugin_repos_creates_directory_if_not_exists(self, mock_config, mock_logging, mock_exists, mock_makedirs):
        """Test update_plugin_repos creates plugins directory if missing."""
        from unmanic.libs.plugins import PluginsHandler

        mock_logging.get_logger.return_value = MagicMock()
        mock_config_instance = MagicMock()
        mock_config_instance.get_plugins_path.return_value = "/tmp/plugins_new"
        mock_config.return_value = mock_config_instance
        mock_exists.return_value = False

        handler = PluginsHandler()
        handler.get_plugin_repos = MagicMock(return_value=[])

        result = handler.update_plugin_repos()

        self.assertTrue(result)
        mock_makedirs.assert_called()


class TestPluginsHandlerGetEnabledPluginModules(unittest.TestCase):
    """Tests for PluginsHandler.get_enabled_plugin_modules_by_type method."""

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

    @patch("unmanic.libs.plugins.PluginExecutor")
    @patch("unmanic.libs.plugins.Session")
    @patch("unmanic.libs.plugins.UnmanicLogging")
    @patch("unmanic.libs.plugins.config.Config")
    def test_get_enabled_plugin_modules_by_type(self, mock_config, mock_logging, mock_session, mock_executor):
        """Test get_enabled_plugin_modules_by_type returns plugin data."""
        from unmanic.libs.plugins import PluginsHandler

        mock_logging.get_logger.return_value = MagicMock()
        mock_config.return_value = MagicMock()
        mock_session_instance = MagicMock()
        mock_session.return_value = mock_session_instance
        mock_executor_instance = MagicMock()
        mock_executor_instance.get_plugin_data_by_type.return_value = [{"plugin_id": "test"}]
        mock_executor.return_value = mock_executor_instance

        handler = PluginsHandler()
        handler.get_plugin_list_filtered_and_sorted = MagicMock(return_value=[{"plugin_id": "test"}])

        result = handler.get_enabled_plugin_modules_by_type("worker.process_item", library_id=1)

        self.assertEqual(result, [{"plugin_id": "test"}])
        mock_session_instance.register_unmanic.assert_called()


class TestPluginsHandlerGetIncompatiblePlugins(unittest.TestCase):
    """Tests for PluginsHandler.get_incompatible_enabled_plugins method."""

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

    @patch("unmanic.libs.plugins.Library")
    @patch("unmanic.libs.plugins.UnmanicLogging")
    @patch("unmanic.libs.plugins.config.Config")
    def test_get_incompatible_enabled_plugins_empty_when_all_compatible(self, mock_config, mock_logging, mock_library):
        """Test get_incompatible_enabled_plugins returns empty when all compatible."""
        from unmanic.libs.plugins import PluginsHandler

        mock_logging.get_logger.return_value = MagicMock()
        mock_config.return_value = MagicMock()
        mock_library.get_all_libraries.return_value = [{"id": 1}]

        handler = PluginsHandler()
        handler.get_plugin_list_filtered_and_sorted = MagicMock(return_value=[{"plugin_id": "test", "name": "Test"}])
        handler.get_plugin_info = MagicMock(return_value={"compatibility": [2]})

        result = handler.get_incompatible_enabled_plugins()

        self.assertEqual(result, [])

    @patch("unmanic.libs.plugins.Library")
    @patch("unmanic.libs.plugins.UnmanicLogging")
    @patch("unmanic.libs.plugins.config.Config")
    def test_get_incompatible_enabled_plugins_returns_incompatible(self, mock_config, mock_logging, mock_library):
        """Test get_incompatible_enabled_plugins returns incompatible plugins."""
        from unmanic.libs.plugins import PluginsHandler

        mock_logging.get_logger.return_value = MagicMock()
        mock_config.return_value = MagicMock()
        mock_library.get_all_libraries.return_value = [{"id": 1}]

        handler = PluginsHandler()
        handler.get_plugin_list_filtered_and_sorted = MagicMock(
            return_value=[{"plugin_id": "old_plugin", "name": "Old Plugin"}]
        )
        handler.get_plugin_info = MagicMock(return_value={"compatibility": [1]})

        result = handler.get_incompatible_enabled_plugins()

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["plugin_id"], "old_plugin")

    @patch("unmanic.libs.plugins.FrontendPushMessages")
    @patch("unmanic.libs.plugins.Library")
    @patch("unmanic.libs.plugins.UnmanicLogging")
    @patch("unmanic.libs.plugins.config.Config")
    def test_get_incompatible_enabled_plugins_adds_frontend_message(
        self, mock_config, mock_logging, mock_library, mock_frontend
    ):
        """Test get_incompatible_enabled_plugins adds frontend messages."""
        from unmanic.libs.plugins import PluginsHandler

        mock_logging.get_logger.return_value = MagicMock()
        mock_config.return_value = MagicMock()
        mock_library.get_all_libraries.return_value = [{"id": 1}]
        mock_frontend_instance = MagicMock()
        mock_frontend.return_value = mock_frontend_instance

        handler = PluginsHandler()
        handler.get_plugin_list_filtered_and_sorted = MagicMock(
            return_value=[{"plugin_id": "bad_plugin", "name": "Bad Plugin"}]
        )
        handler.get_plugin_info = MagicMock(return_value={"compatibility": [1]})

        result = handler.get_incompatible_enabled_plugins(frontend_messages=mock_frontend_instance)

        mock_frontend_instance.add.assert_called()


class TestPluginsHandlerNotifySite(unittest.TestCase):
    """Tests for PluginsHandler.notify_site_of_plugin_install method."""

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

    @patch("unmanic.libs.plugins.Session")
    @patch("unmanic.libs.plugins.UnmanicLogging")
    @patch("unmanic.libs.plugins.config.Config")
    def test_notify_site_posts_data(self, mock_config, mock_logging, mock_session):
        """Test notify_site_of_plugin_install posts to API."""
        from unmanic.libs.plugins import PluginsHandler

        mock_logging.get_logger.return_value = MagicMock()
        mock_config.return_value = MagicMock()
        mock_session_instance = MagicMock()
        mock_session_instance.get_installation_uuid.return_value = "test-uuid"
        mock_session_instance.get_supporter_level.return_value = 0
        mock_session_instance.api_post.return_value = ({"success": True}, 200)
        mock_session.return_value = mock_session_instance

        handler = PluginsHandler()
        plugin = {"plugin_id": "test", "author": "Test Author", "version": "1.0.0"}
        handler.notify_site_of_plugin_install(plugin)

        mock_session_instance.api_post.assert_called_once()

    @patch("unmanic.libs.plugins.Session")
    @patch("unmanic.libs.plugins.UnmanicLogging")
    @patch("unmanic.libs.plugins.config.Config")
    def test_notify_site_handles_exception(self, mock_config, mock_logging, mock_session):
        """Test notify_site_of_plugin_install handles exceptions."""
        from unmanic.libs.plugins import PluginsHandler

        mock_logger = MagicMock()
        mock_logging.get_logger.return_value = mock_logger
        mock_config.return_value = MagicMock()
        mock_session_instance = MagicMock()
        mock_session_instance.api_post.side_effect = Exception("API error")
        mock_session.return_value = mock_session_instance

        handler = PluginsHandler()
        plugin = {"plugin_id": "test", "author": "Test Author", "version": "1.0.0"}
        result = handler.notify_site_of_plugin_install(plugin)

        self.assertFalse(result)


if __name__ == "__main__":
    unittest.main()

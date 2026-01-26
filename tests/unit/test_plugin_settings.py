#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unit tests for the PluginSettings class in unmanic.libs.unplugins.settings.

Tests plugin configuration management and settings persistence.
"""

import json
import os
import tempfile
import unittest
from unittest.mock import MagicMock, patch, PropertyMock


class TestPluginSettingsInit(unittest.TestCase):
    """Tests for PluginSettings initialization."""

    def test_init_no_library_id(self):
        """Test initialization without library_id."""
        from unmanic.libs.unplugins.settings import PluginSettings

        settings = PluginSettings()
        self.assertIsNone(settings.library_id)

    def test_init_with_valid_library_id(self):
        """Test initialization with valid integer library_id."""
        from unmanic.libs.unplugins.settings import PluginSettings

        settings = PluginSettings(library_id=42)
        self.assertEqual(settings.library_id, 42)

    def test_init_with_string_library_id(self):
        """Test initialization with string library_id (gets converted to int)."""
        from unmanic.libs.unplugins.settings import PluginSettings

        settings = PluginSettings(library_id="123")
        self.assertEqual(settings.library_id, 123)

    def test_init_with_invalid_library_id(self):
        """Test initialization with non-numeric library_id raises error."""
        from unmanic.libs.unplugins.settings import PluginSettings

        with self.assertRaises(Exception) as ctx:
            PluginSettings(library_id="not_a_number")

        self.assertIn("Library ID needs to be an integer", str(ctx.exception))


class TestPluginSettingsFormSettings(unittest.TestCase):
    """Tests for form settings functionality."""

    def test_get_form_settings_empty(self):
        """Test get_form_settings returns empty dict by default."""
        from unmanic.libs.unplugins.settings import PluginSettings

        settings = PluginSettings()
        result = settings.get_form_settings()
        self.assertEqual(result, {})

    def test_get_form_settings_with_data(self):
        """Test get_form_settings returns configured form_settings."""
        from unmanic.libs.unplugins.settings import PluginSettings

        class CustomSettings(PluginSettings):
            form_settings = {
                "enable_feature": {
                    "label": "Enable Feature",
                    "input_type": "checkbox",
                }
            }

        settings = CustomSettings()
        result = settings.get_form_settings()
        self.assertIn("enable_feature", result)
        self.assertEqual(result["enable_feature"]["input_type"], "checkbox")


class TestPluginSettingsDefaultSettings(unittest.TestCase):
    """Tests for default settings functionality."""

    def test_get_default_setting_all(self):
        """Test get_default_setting returns all defaults when key is None."""
        from unmanic.libs.unplugins.settings import PluginSettings

        class CustomSettings(PluginSettings):
            settings = {"option1": "value1", "option2": 42}

        settings = CustomSettings()
        result = settings.get_default_setting()
        self.assertEqual(result, {"option1": "value1", "option2": 42})

    def test_get_default_setting_specific_key(self):
        """Test get_default_setting returns specific key value."""
        from unmanic.libs.unplugins.settings import PluginSettings

        class CustomSettings(PluginSettings):
            settings = {"option1": "value1", "option2": 42}

        settings = CustomSettings()
        result = settings.get_default_setting("option2")
        self.assertEqual(result, 42)

    def test_get_default_setting_missing_key(self):
        """Test get_default_setting returns None for missing key."""
        from unmanic.libs.unplugins.settings import PluginSettings

        class CustomSettings(PluginSettings):
            settings = {"option1": "value1"}

        settings = CustomSettings()
        result = settings.get_default_setting("nonexistent")
        self.assertIsNone(result)


class TestPluginSettingsConfigured(unittest.TestCase):
    """Tests for configured settings functionality with file I/O."""

    def setUp(self):
        """Set up test fixtures with a temporary directory."""
        self.temp_dir = tempfile.mkdtemp()
        self.profile_dir = os.path.join(self.temp_dir, "plugin_test")
        os.makedirs(self.profile_dir)

    def tearDown(self):
        """Clean up temporary directory."""
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)

    @patch("unmanic.libs.unplugins.settings.config.Config")
    def test_get_setting_returns_default_when_no_file(self, mock_config):
        """Test get_setting returns defaults when no settings file exists."""
        from unmanic.libs.unplugins.settings import PluginSettings

        mock_config.return_value.get_userdata_path.return_value = self.temp_dir

        class CustomSettings(PluginSettings):
            settings = {"feature_enabled": True}

        settings = CustomSettings()

        with patch.object(settings, "get_plugin_directory", return_value=self.profile_dir):
            result = settings.get_setting("feature_enabled")

        self.assertTrue(result)

    @patch("unmanic.libs.unplugins.settings.config.Config")
    def test_get_setting_all_returns_dict(self, mock_config):
        """Test get_setting with no key returns full dict."""
        from unmanic.libs.unplugins.settings import PluginSettings

        mock_config.return_value.get_userdata_path.return_value = self.temp_dir

        class CustomSettings(PluginSettings):
            settings = {"a": 1, "b": 2}

        settings = CustomSettings()

        with patch.object(settings, "get_plugin_directory", return_value=self.profile_dir):
            result = settings.get_setting()

        self.assertEqual(result, {"a": 1, "b": 2})

    @patch("unmanic.libs.unplugins.settings.config.Config")
    def test_set_setting_valid_key(self, mock_config):
        """Test set_setting updates and persists valid key."""
        from unmanic.libs.unplugins.settings import PluginSettings

        mock_config.return_value.get_userdata_path.return_value = self.temp_dir

        class CustomSettings(PluginSettings):
            settings = {"threshold": 50}

        settings = CustomSettings()

        with patch.object(settings, "get_plugin_directory", return_value=self.profile_dir):
            result = settings.set_setting("threshold", 100)
            new_value = settings.get_setting("threshold")

        self.assertTrue(result)
        self.assertEqual(new_value, 100)

    @patch("unmanic.libs.unplugins.settings.config.Config")
    def test_set_setting_invalid_key(self, mock_config):
        """Test set_setting returns False for non-existent key."""
        from unmanic.libs.unplugins.settings import PluginSettings

        mock_config.return_value.get_userdata_path.return_value = self.temp_dir

        class CustomSettings(PluginSettings):
            settings = {"threshold": 50}

        settings = CustomSettings()

        with patch.object(settings, "get_plugin_directory", return_value=self.profile_dir):
            result = settings.set_setting("nonexistent_key", "value")

        self.assertFalse(result)

    @patch("unmanic.libs.unplugins.settings.config.Config")
    def test_settings_persist_to_file(self, mock_config):
        """Test that settings are persisted to JSON file."""
        from unmanic.libs.unplugins.settings import PluginSettings

        mock_config.return_value.get_userdata_path.return_value = self.temp_dir

        class CustomSettings(PluginSettings):
            settings = {"mode": "default"}

        settings = CustomSettings()

        with patch.object(settings, "get_plugin_directory", return_value=self.profile_dir):
            settings.set_setting("mode", "advanced")

            # Verify file exists and contains our setting
            settings_file = os.path.join(self.profile_dir, "settings.json")
            self.assertTrue(os.path.exists(settings_file))

            with open(settings_file) as f:
                data = json.load(f)
                self.assertEqual(data["mode"], "advanced")

    @patch("unmanic.libs.unplugins.settings.config.Config")
    def test_settings_read_from_file(self, mock_config):
        """Test that settings are read from existing JSON file."""
        from unmanic.libs.unplugins.settings import PluginSettings

        mock_config.return_value.get_userdata_path.return_value = self.temp_dir

        # Pre-create settings file
        settings_file = os.path.join(self.profile_dir, "settings.json")
        with open(settings_file, "w") as f:
            json.dump({"volume": 80}, f)

        class CustomSettings(PluginSettings):
            settings = {"volume": 50}  # Default is 50

        settings = CustomSettings()

        with patch.object(settings, "get_plugin_directory", return_value=self.profile_dir):
            result = settings.get_setting("volume")

        # Should get file value (80), not default (50)
        self.assertEqual(result, 80)


class TestPluginSettingsLibrarySpecific(unittest.TestCase):
    """Tests for library-specific settings."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.profile_dir = os.path.join(self.temp_dir, "plugin_test")
        os.makedirs(self.profile_dir)

    def tearDown(self):
        """Clean up."""
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)

    @patch("unmanic.libs.unplugins.settings.config.Config")
    def test_library_specific_settings_file(self, mock_config):
        """Test that library-specific settings use separate file."""
        from unmanic.libs.unplugins.settings import PluginSettings

        mock_config.return_value.get_userdata_path.return_value = self.temp_dir

        # First create a global settings file (required as fallback)
        global_file = os.path.join(self.profile_dir, "settings.json")
        with open(global_file, "w") as f:
            json.dump({"codec": "h264"}, f)

        class CustomSettings(PluginSettings):
            settings = {"codec": "h264"}

        # Create settings for library 5
        settings = CustomSettings(library_id=5)

        with patch.object(settings, "get_plugin_directory", return_value=self.profile_dir):
            settings.set_setting("codec", "hevc")

            # Should create library-specific file
            library_file = os.path.join(self.profile_dir, "settings.5.json")
            self.assertTrue(os.path.exists(library_file))

            with open(library_file) as f:
                data = json.load(f)
                self.assertEqual(data["codec"], "hevc")


class TestPluginSettingsResetToDefaults(unittest.TestCase):
    """Tests for reset_settings_to_defaults functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.profile_dir = os.path.join(self.temp_dir, "plugin_test")
        os.makedirs(self.profile_dir)

    def tearDown(self):
        """Clean up."""
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)

    @patch("unmanic.libs.unplugins.settings.config.Config")
    def test_reset_removes_settings_file(self, mock_config):
        """Test reset_settings_to_defaults removes the settings file."""
        from unmanic.libs.unplugins.settings import PluginSettings

        mock_config.return_value.get_userdata_path.return_value = self.temp_dir

        # Create settings file
        settings_file = os.path.join(self.profile_dir, "settings.json")
        with open(settings_file, "w") as f:
            json.dump({"custom": "value"}, f)

        class CustomSettings(PluginSettings):
            settings = {"custom": "default"}

        settings = CustomSettings()

        with patch.object(settings, "get_plugin_directory", return_value=self.profile_dir):
            result = settings.reset_settings_to_defaults()

        self.assertTrue(result)
        self.assertFalse(os.path.exists(settings_file))

    @patch("unmanic.libs.unplugins.settings.config.Config")
    def test_reset_library_specific_does_not_delete_global(self, mock_config):
        """Test that resetting library config doesn't delete global config."""
        from unmanic.libs.unplugins.settings import PluginSettings

        mock_config.return_value.get_userdata_path.return_value = self.temp_dir

        # Create global settings file
        global_file = os.path.join(self.profile_dir, "settings.json")
        with open(global_file, "w") as f:
            json.dump({"global": "value"}, f)

        class CustomSettings(PluginSettings):
            settings = {"global": "default"}

        # Request reset for library 5 (no specific file exists)
        settings = CustomSettings(library_id=5)

        with patch.object(settings, "get_plugin_directory", return_value=self.profile_dir):
            result = settings.reset_settings_to_defaults()

        # Should return False (didn't delete) and global file should remain
        self.assertFalse(result)
        self.assertTrue(os.path.exists(global_file))


if __name__ == "__main__":
    unittest.main()

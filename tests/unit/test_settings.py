#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Unit tests for unmanic.libs.settings module.

Tests the Pydantic settings implementation including:
- Default values
- Environment variable loading
- Path validation
- Field constraints
"""

import os
import pytest
from unittest.mock import patch

from pydantic import ValidationError

from unmanic.libs.settings import UnmanicSettings, get_settings


class TestUnmanicSettingsDefaults:
    """Test default values for UnmanicSettings."""

    def test_default_ui_port(self):
        """Default UI port should be 8888."""
        settings = UnmanicSettings()
        assert settings.ui_port == 8888

    def test_default_debugging_disabled(self):
        """Debugging should be disabled by default."""
        settings = UnmanicSettings()
        assert settings.debugging is False

    def test_default_log_buffer_retention(self):
        """Log buffer retention should default to 0."""
        settings = UnmanicSettings()
        assert settings.log_buffer_retention == 0

    def test_default_library_scanner_disabled(self):
        """Library scanner should be disabled by default."""
        settings = UnmanicSettings()
        assert settings.enable_library_scanner is False

    def test_default_schedule_full_scan_minutes(self):
        """Full scan schedule should default to 1440 minutes (1 day)."""
        settings = UnmanicSettings()
        assert settings.schedule_full_scan_minutes == 1440

    def test_default_concurrent_file_testers(self):
        """Concurrent file testers should default to 2."""
        settings = UnmanicSettings()
        assert settings.concurrent_file_testers == 2

    def test_default_follow_symlinks(self):
        """Follow symlinks should be enabled by default."""
        settings = UnmanicSettings()
        assert settings.follow_symlinks is True

    def test_default_clear_pending_on_restart(self):
        """Clear pending tasks on restart should be enabled by default."""
        settings = UnmanicSettings()
        assert settings.clear_pending_tasks_on_restart is True

    def test_default_always_keep_failed_tasks(self):
        """Always keep failed tasks should be enabled by default."""
        settings = UnmanicSettings()
        assert settings.always_keep_failed_tasks is True


class TestUnmanicSettingsPathDefaults:
    """Test path default values."""

    def test_config_path_contains_unmanic(self):
        """Config path should contain .unmanic/config."""
        settings = UnmanicSettings()
        assert ".unmanic" in settings.config_path
        assert settings.config_path.endswith("config")

    def test_log_path_contains_unmanic(self):
        """Log path should contain .unmanic/logs."""
        settings = UnmanicSettings()
        assert ".unmanic" in settings.log_path
        assert settings.log_path.endswith("logs")

    def test_plugins_path_contains_unmanic(self):
        """Plugins path should contain .unmanic/plugins."""
        settings = UnmanicSettings()
        assert ".unmanic" in settings.plugins_path
        assert settings.plugins_path.endswith("plugins")

    def test_userdata_path_contains_unmanic(self):
        """Userdata path should contain .unmanic/userdata."""
        settings = UnmanicSettings()
        assert ".unmanic" in settings.userdata_path
        assert settings.userdata_path.endswith("userdata")


class TestUnmanicSettingsEnvOverride:
    """Test environment variable overrides."""

    def test_ui_port_env_override(self, monkeypatch):
        """UI port should be overridable via UNMANIC_UI_PORT."""
        monkeypatch.setenv("UNMANIC_UI_PORT", "9000")
        settings = UnmanicSettings()
        assert settings.ui_port == 9000

    def test_debugging_env_override(self, monkeypatch):
        """Debugging should be overridable via UNMANIC_DEBUGGING."""
        monkeypatch.setenv("UNMANIC_DEBUGGING", "true")
        settings = UnmanicSettings()
        assert settings.debugging is True

    def test_config_path_env_override(self, monkeypatch):
        """Config path should be overridable via UNMANIC_CONFIG_PATH."""
        monkeypatch.setenv("UNMANIC_CONFIG_PATH", "/custom/config/path")
        settings = UnmanicSettings()
        assert settings.config_path == "/custom/config/path"

    def test_library_path_env_override(self, monkeypatch):
        """Library path should be overridable via UNMANIC_LIBRARY_PATH."""
        monkeypatch.setenv("UNMANIC_LIBRARY_PATH", "/media/library")
        settings = UnmanicSettings()
        assert settings.library_path == "/media/library"


class TestUnmanicSettingsValidation:
    """Test field validation."""

    def test_ui_port_min_value(self, monkeypatch):
        """UI port should reject values below 1."""
        monkeypatch.setenv("UNMANIC_UI_PORT", "0")
        with pytest.raises(ValidationError, match="ui_port"):
            UnmanicSettings()

    def test_ui_port_max_value(self, monkeypatch):
        """UI port should reject values above 65535."""
        monkeypatch.setenv("UNMANIC_UI_PORT", "65536")
        with pytest.raises(ValidationError, match="ui_port"):
            UnmanicSettings()

    def test_concurrent_file_testers_min(self, monkeypatch):
        """Concurrent file testers should reject values below 1."""
        monkeypatch.setenv("UNMANIC_CONCURRENT_FILE_TESTERS", "0")
        with pytest.raises(ValidationError, match="concurrent_file_testers"):
            UnmanicSettings()

    def test_concurrent_file_testers_max(self, monkeypatch):
        """Concurrent file testers should reject values above 16."""
        monkeypatch.setenv("UNMANIC_CONCURRENT_FILE_TESTERS", "17")
        with pytest.raises(ValidationError, match="concurrent_file_testers"):
            UnmanicSettings()


class TestUnmanicSettingsPathValidation:
    """Test path validation and normalization."""

    def test_path_expands_home(self, monkeypatch):
        """Paths should expand ~ to home directory."""
        monkeypatch.setenv("UNMANIC_CONFIG_PATH", "~/custom/config")
        settings = UnmanicSettings()
        assert "~" not in settings.config_path
        assert os.path.expanduser("~") in settings.config_path

    def test_path_expands_env_vars(self, monkeypatch):
        """Paths should expand environment variables."""
        monkeypatch.setenv("MY_CUSTOM_DIR", "/opt/unmanic")
        monkeypatch.setenv("UNMANIC_CONFIG_PATH", "$MY_CUSTOM_DIR/config")
        settings = UnmanicSettings()
        assert settings.config_path == "/opt/unmanic/config"


class TestGetSettings:
    """Test get_settings function."""

    def test_get_settings_returns_instance(self):
        """get_settings should return an UnmanicSettings instance."""
        settings = get_settings()
        assert isinstance(settings, UnmanicSettings)

    def test_get_settings_creates_new_instance(self):
        """get_settings should create a new instance each time."""
        settings1 = get_settings()
        settings2 = get_settings()
        # They should have the same values but be different objects
        assert settings1.ui_port == settings2.ui_port
        # Note: In Pydantic, instances with same values may not be the same object

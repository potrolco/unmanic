#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Unit tests for unmanic.config module.

Tests the Config class including:
- Default configuration values
- Environment variable loading
- Path normalization
- Config getter/setter methods
"""

import os
import tempfile
import pytest
from unittest.mock import patch, MagicMock

# Reset singleton before importing Config to get fresh instance
from unmanic.libs.singleton import SingletonType

# Clear the singleton cache before tests
if hasattr(SingletonType, "_instances"):
    SingletonType._instances = {}

from unmanic.config import Config


class TestConfigNormalizePath:
    """Test Config._normalize_path static method."""

    def test_normalizes_absolute_path(self):
        """Should return absolute path unchanged."""
        result = Config._normalize_path("/absolute/path")
        assert result == "/absolute/path"

    def test_expands_tilde(self):
        """Should expand ~ to home directory."""
        result = Config._normalize_path("~/custom")
        assert "~" not in result
        assert result.endswith("custom")

    def test_handles_empty_path(self):
        """Should return None for empty path."""
        result = Config._normalize_path("")
        assert result is None

    def test_handles_none(self):
        """Should return None for None input."""
        result = Config._normalize_path(None)
        assert result is None

    def test_converts_relative_to_absolute(self):
        """Should convert relative path to absolute."""
        result = Config._normalize_path("relative/path")
        assert os.path.isabs(result)
        assert result.endswith("relative/path")


class TestConfigDefaults:
    """Test Config default values."""

    @pytest.fixture
    def config(self):
        """Create a fresh Config instance with temp directory."""
        # Clear singleton
        if hasattr(SingletonType, "_instances"):
            SingletonType._instances = {}

        with tempfile.TemporaryDirectory() as tmpdir:
            # Create config in temp directory
            with patch.dict(os.environ, {"HOME_DIR": tmpdir}, clear=False):
                cfg = Config(config_path=tmpdir)
                yield cfg

    def test_default_ui_port(self, config):
        """Default UI port should be 8888."""
        assert config.ui_port == 8888

    def test_default_debugging_disabled(self, config):
        """Debugging should be disabled by default."""
        assert config.debugging is False

    def test_default_library_scanner_disabled(self, config):
        """Library scanner should be disabled by default."""
        assert config.enable_library_scanner is False

    def test_default_concurrent_file_testers(self, config):
        """Concurrent file testers should default to 2."""
        assert config.concurrent_file_testers == 2

    def test_default_follow_symlinks(self, config):
        """Follow symlinks should be enabled by default."""
        assert config.follow_symlinks is True


class TestConfigGetters:
    """Test Config getter methods."""

    @pytest.fixture
    def config(self):
        """Create a fresh Config instance."""
        if hasattr(SingletonType, "_instances"):
            SingletonType._instances = {}

        with tempfile.TemporaryDirectory() as tmpdir:
            with patch.dict(os.environ, {"HOME_DIR": tmpdir}, clear=False):
                cfg = Config(config_path=tmpdir)
                yield cfg

    def test_get_ui_port(self, config):
        """get_ui_port should return ui_port value."""
        config.ui_port = 9999
        assert config.get_ui_port() == 9999

    def test_get_config_as_dict(self, config):
        """get_config_as_dict should return dict of all settings."""
        result = config.get_config_as_dict()
        assert isinstance(result, dict)
        assert "ui_port" in result
        assert "debugging" in result

    def test_get_config_keys(self, config):
        """get_config_keys should return list of config field names."""
        keys = config.get_config_keys()
        assert "ui_port" in keys
        assert "debugging" in keys
        assert "config_path" in keys


class TestConfigSetters:
    """Test Config setter methods."""

    @pytest.fixture
    def config(self):
        """Create a fresh Config instance."""
        if hasattr(SingletonType, "_instances"):
            SingletonType._instances = {}

        with tempfile.TemporaryDirectory() as tmpdir:
            with patch.dict(os.environ, {"HOME_DIR": tmpdir}, clear=False):
                cfg = Config(config_path=tmpdir)
                yield cfg

    def test_set_config_item(self, config):
        """set_config_item should set the value."""
        config.set_config_item("ui_port", 7777, save_settings=False)
        assert config.ui_port == 7777

    def test_set_config_item_ignores_unknown_key(self, config):
        """set_config_item should ignore unknown keys."""
        # This should not raise
        config.set_config_item("unknown_key_xyz", "value", save_settings=False)
        assert not hasattr(config, "unknown_key_xyz")

    def test_set_bulk_config_items(self, config):
        """set_bulk_config_items should set multiple values."""
        items = {"ui_port": 5555, "debugging": True}
        config.set_bulk_config_items(items, save_settings=False)
        assert config.ui_port == 5555
        assert config.debugging is True


class TestConfigEnvOverride:
    """Test environment variable configuration."""

    def test_respects_unmanic_path_env(self):
        """Should use UNMANIC_PATH from environment."""
        if hasattr(SingletonType, "_instances"):
            SingletonType._instances = {}

        with tempfile.TemporaryDirectory() as tmpdir:
            env = {"UNMANIC_PATH": tmpdir, "HOME_DIR": tmpdir}
            with patch.dict(os.environ, env, clear=False):
                cfg = Config()

            assert cfg.config_path == os.path.join(tmpdir, "config")
            assert cfg.log_path == os.path.join(tmpdir, "logs")
            assert cfg.plugins_path == os.path.join(tmpdir, "plugins")


class TestConfigReadVersion:
    """Test Config.read_version method."""

    def test_returns_version_string(self):
        """read_version should return version string."""
        result = Config.read_version()
        assert isinstance(result, str)
        # Should contain version number format
        assert "." in result or result


class TestConfigGetConfigItem:
    """Test Config.get_config_item method."""

    @pytest.fixture
    def config(self):
        """Create a fresh Config instance."""
        if hasattr(SingletonType, "_instances"):
            SingletonType._instances = {}

        with tempfile.TemporaryDirectory() as tmpdir:
            with patch.dict(os.environ, {"HOME_DIR": tmpdir}, clear=False):
                cfg = Config(config_path=tmpdir)
                yield cfg

    def test_get_config_item_uses_getter_method(self, config):
        """get_config_item should use get_X method if available."""
        config.ui_port = 1234
        result = config.get_config_item("ui_port")
        assert result == 1234

    def test_get_config_item_returns_none_for_no_getter(self, config):
        """get_config_item should return None for items without getter method."""
        # test attribute has no getter method
        result = config.get_config_item("test")
        assert result is None

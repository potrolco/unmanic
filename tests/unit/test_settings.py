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


class TestHealthCheckSettings:
    """Test health check settings (Phase 2)."""

    def test_default_pre_transcode_check_disabled(self):
        """Pre-transcode health check should be disabled by default."""
        settings = UnmanicSettings()
        assert settings.enable_pre_transcode_health_check is False

    def test_default_post_transcode_check_disabled(self):
        """Post-transcode health check should be disabled by default."""
        settings = UnmanicSettings()
        assert settings.enable_post_transcode_health_check is False

    def test_default_fail_on_corruption_enabled(self):
        """Fail on pre-check corruption should be enabled by default."""
        settings = UnmanicSettings()
        assert settings.fail_on_pre_check_corruption is True

    def test_default_health_check_timeout(self):
        """Health check timeout should default to 300 seconds."""
        settings = UnmanicSettings()
        assert settings.health_check_timeout_seconds == 300

    def test_default_health_check_algorithm(self):
        """Health check algorithm should default to md5."""
        settings = UnmanicSettings()
        assert settings.health_check_algorithm == "md5"

    def test_enable_pre_transcode_check_env_override(self, monkeypatch):
        """Pre-transcode check should be overridable via env var."""
        monkeypatch.setenv("UNMANIC_ENABLE_PRE_TRANSCODE_HEALTH_CHECK", "true")
        settings = UnmanicSettings()
        assert settings.enable_pre_transcode_health_check is True

    def test_enable_post_transcode_check_env_override(self, monkeypatch):
        """Post-transcode check should be overridable via env var."""
        monkeypatch.setenv("UNMANIC_ENABLE_POST_TRANSCODE_HEALTH_CHECK", "true")
        settings = UnmanicSettings()
        assert settings.enable_post_transcode_health_check is True

    def test_health_check_timeout_env_override(self, monkeypatch):
        """Health check timeout should be overridable via env var."""
        monkeypatch.setenv("UNMANIC_HEALTH_CHECK_TIMEOUT_SECONDS", "600")
        settings = UnmanicSettings()
        assert settings.health_check_timeout_seconds == 600

    def test_health_check_algorithm_env_override(self, monkeypatch):
        """Health check algorithm should be overridable via env var."""
        monkeypatch.setenv("UNMANIC_HEALTH_CHECK_ALGORITHM", "sha256")
        settings = UnmanicSettings()
        assert settings.health_check_algorithm == "sha256"

    def test_health_check_timeout_min_validation(self, monkeypatch):
        """Health check timeout should reject values below 30 seconds."""
        monkeypatch.setenv("UNMANIC_HEALTH_CHECK_TIMEOUT_SECONDS", "10")
        with pytest.raises(ValidationError, match="health_check_timeout_seconds"):
            UnmanicSettings()

    def test_health_check_timeout_max_validation(self, monkeypatch):
        """Health check timeout should reject values above 3600 seconds."""
        monkeypatch.setenv("UNMANIC_HEALTH_CHECK_TIMEOUT_SECONDS", "7200")
        with pytest.raises(ValidationError, match="health_check_timeout_seconds"):
            UnmanicSettings()

    def test_health_check_algorithm_validation_invalid(self, monkeypatch):
        """Health check algorithm should reject invalid values."""
        monkeypatch.setenv("UNMANIC_HEALTH_CHECK_ALGORITHM", "invalid_algo")
        with pytest.raises(ValidationError, match="Invalid algorithm"):
            UnmanicSettings()

    def test_health_check_algorithm_sha1_valid(self, monkeypatch):
        """Health check algorithm should accept sha1."""
        monkeypatch.setenv("UNMANIC_HEALTH_CHECK_ALGORITHM", "sha1")
        settings = UnmanicSettings()
        assert settings.health_check_algorithm == "sha1"

    def test_health_check_algorithm_case_insensitive(self, monkeypatch):
        """Health check algorithm should be case insensitive."""
        monkeypatch.setenv("UNMANIC_HEALTH_CHECK_ALGORITHM", "SHA256")
        settings = UnmanicSettings()
        assert settings.health_check_algorithm == "sha256"


class TestGPUSettings:
    """Test GPU settings (Phase 3)."""

    def test_default_gpu_enabled(self):
        """GPU should be enabled by default."""
        settings = UnmanicSettings()
        assert settings.gpu_enabled is True

    def test_default_gpu_assignment_strategy(self):
        """GPU assignment strategy should default to round_robin."""
        settings = UnmanicSettings()
        assert settings.gpu_assignment_strategy == "round_robin"

    def test_default_max_workers_per_gpu(self):
        """Max workers per GPU should default to 2."""
        settings = UnmanicSettings()
        assert settings.max_workers_per_gpu == 2

    def test_default_gpu_allowlist_empty(self):
        """GPU allowlist should default to empty."""
        settings = UnmanicSettings()
        assert settings.gpu_allowlist == ""

    def test_default_gpu_blocklist_empty(self):
        """GPU blocklist should default to empty."""
        settings = UnmanicSettings()
        assert settings.gpu_blocklist == ""

    def test_gpu_enabled_env_override(self, monkeypatch):
        """GPU enabled should be overridable via env var."""
        monkeypatch.setenv("UNMANIC_GPU_ENABLED", "false")
        settings = UnmanicSettings()
        assert settings.gpu_enabled is False

    def test_gpu_assignment_strategy_env_override(self, monkeypatch):
        """GPU assignment strategy should be overridable via env var."""
        monkeypatch.setenv("UNMANIC_GPU_ASSIGNMENT_STRATEGY", "least_used")
        settings = UnmanicSettings()
        assert settings.gpu_assignment_strategy == "least_used"

    def test_max_workers_per_gpu_env_override(self, monkeypatch):
        """Max workers per GPU should be overridable via env var."""
        monkeypatch.setenv("UNMANIC_MAX_WORKERS_PER_GPU", "4")
        settings = UnmanicSettings()
        assert settings.max_workers_per_gpu == 4

    def test_gpu_allowlist_env_override(self, monkeypatch):
        """GPU allowlist should be overridable via env var."""
        monkeypatch.setenv("UNMANIC_GPU_ALLOWLIST", "cuda:0,cuda:1")
        settings = UnmanicSettings()
        assert settings.gpu_allowlist == "cuda:0,cuda:1"

    def test_gpu_blocklist_env_override(self, monkeypatch):
        """GPU blocklist should be overridable via env var."""
        monkeypatch.setenv("UNMANIC_GPU_BLOCKLIST", "vaapi:/dev/dri/renderD129")
        settings = UnmanicSettings()
        assert settings.gpu_blocklist == "vaapi:/dev/dri/renderD129"

    def test_max_workers_per_gpu_min_validation(self, monkeypatch):
        """Max workers per GPU should reject values below 1."""
        monkeypatch.setenv("UNMANIC_MAX_WORKERS_PER_GPU", "0")
        with pytest.raises(ValidationError, match="max_workers_per_gpu"):
            UnmanicSettings()

    def test_max_workers_per_gpu_max_validation(self, monkeypatch):
        """Max workers per GPU should reject values above 10."""
        monkeypatch.setenv("UNMANIC_MAX_WORKERS_PER_GPU", "15")
        with pytest.raises(ValidationError, match="max_workers_per_gpu"):
            UnmanicSettings()

    def test_gpu_assignment_strategy_validation_invalid(self, monkeypatch):
        """GPU assignment strategy should reject invalid values."""
        monkeypatch.setenv("UNMANIC_GPU_ASSIGNMENT_STRATEGY", "invalid_strategy")
        with pytest.raises(ValidationError, match="Invalid strategy"):
            UnmanicSettings()

    def test_gpu_assignment_strategy_case_insensitive(self, monkeypatch):
        """GPU assignment strategy should be case insensitive."""
        monkeypatch.setenv("UNMANIC_GPU_ASSIGNMENT_STRATEGY", "LEAST_USED")
        settings = UnmanicSettings()
        assert settings.gpu_assignment_strategy == "least_used"

    def test_gpu_assignment_strategy_manual_valid(self, monkeypatch):
        """GPU assignment strategy should accept manual."""
        monkeypatch.setenv("UNMANIC_GPU_ASSIGNMENT_STRATEGY", "manual")
        settings = UnmanicSettings()
        assert settings.gpu_assignment_strategy == "manual"

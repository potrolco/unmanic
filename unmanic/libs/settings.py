#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    unmanic.settings.py

    Pydantic-based settings management for Unmanic.

    This module provides type-safe, validated configuration using pydantic-settings.
    It supports loading from environment variables with the UNMANIC_ prefix.

    Written by:               TARS Modernization (Phase 1)
    Date:                     26 Jan 2026

    Copyright:
           Copyright (C) Josh Sunnex - All Rights Reserved
           (TARS Fork - potrolco/unmanic)

"""

import os
from typing import List, Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from unmanic.libs import common


class UnmanicSettings(BaseSettings):
    """
    Unmanic application settings with environment variable support.

    All settings can be overridden via environment variables with the UNMANIC_ prefix.
    For example, UNMANIC_UI_PORT=9000 will override the ui_port setting.
    """

    model_config = SettingsConfigDict(
        env_prefix="UNMANIC_",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Server settings
    ui_port: int = Field(default=8888, ge=1, le=65535, description="Web UI port")
    debugging: bool = Field(default=False, description="Enable debug mode")
    log_buffer_retention: int = Field(default=0, ge=0, description="Log buffer retention in days (0 = keep all)")

    # Path settings
    config_path: str = Field(
        default_factory=lambda: os.path.join(common.get_home_dir(), ".unmanic", "config"),
        description="Configuration directory path",
    )
    log_path: str = Field(
        default_factory=lambda: os.path.join(common.get_home_dir(), ".unmanic", "logs"),
        description="Log directory path",
    )
    plugins_path: str = Field(
        default_factory=lambda: os.path.join(common.get_home_dir(), ".unmanic", "plugins"),
        description="Plugins directory path",
    )
    userdata_path: str = Field(
        default_factory=lambda: os.path.join(common.get_home_dir(), ".unmanic", "userdata"),
        description="User data directory path",
    )
    cache_path: str = Field(
        default_factory=common.get_default_cache_path,
        description="Cache directory for transcoding",
    )
    library_path: str = Field(
        default_factory=common.get_default_library_path,
        description="Default library path for scanning",
    )

    # Library scanner settings
    enable_library_scanner: bool = Field(default=False, description="Enable automatic library scanning")
    schedule_full_scan_minutes: int = Field(default=1440, ge=1, description="Minutes between full library scans")
    follow_symlinks: bool = Field(default=True, description="Follow symbolic links when scanning")
    concurrent_file_testers: int = Field(default=2, ge=1, le=16, description="Number of concurrent file testers")
    run_full_scan_on_start: bool = Field(default=False, description="Run full scan on application start")
    clear_pending_tasks_on_restart: bool = Field(default=True, description="Clear pending tasks on restart")

    # Task management settings
    auto_manage_completed_tasks: bool = Field(default=False, description="Automatically manage completed tasks")
    max_age_of_completed_tasks: int = Field(default=91, ge=1, description="Max age of completed tasks in days")
    always_keep_failed_tasks: bool = Field(default=True, description="Keep failed tasks regardless of age")

    # Installation/link settings
    installation_name: str = Field(default="", description="Name of this Unmanic installation")
    distributed_worker_count_target: int = Field(default=0, ge=0, description="Target worker count for distributed processing")

    # Feature flags
    first_run: bool = Field(default=False, description="First run flag")
    release_notes_viewed: Optional[str] = Field(default=None, description="Last viewed release notes version")

    @field_validator("config_path", "log_path", "plugins_path", "userdata_path", "cache_path", "library_path")
    @classmethod
    def validate_path(cls, v: str) -> str:
        """Normalize path strings."""
        if v:
            return os.path.expanduser(os.path.expandvars(v))
        return v


def get_settings() -> UnmanicSettings:
    """
    Get the Unmanic settings instance.

    This function creates a new settings instance each time it's called.
    For singleton behavior, use the Config class which wraps this.

    Returns:
        UnmanicSettings instance with loaded configuration
    """
    return UnmanicSettings()

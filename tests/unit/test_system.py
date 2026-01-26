#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unit tests for the System class in unmanic.libs.system.

Tests system information gathering functionality.
"""

import sys
import unittest
from unittest.mock import MagicMock, patch


class TestSystemInit(unittest.TestCase):
    """Tests for System initialization."""

    def setUp(self):
        """Clear singleton before each test."""
        from unmanic.libs.singleton import SingletonType
        from unmanic.libs.system import System

        if System in SingletonType._instances:
            del SingletonType._instances[System]

    def tearDown(self):
        """Clear singleton after each test."""
        from unmanic.libs.singleton import SingletonType
        from unmanic.libs.system import System

        if System in SingletonType._instances:
            del SingletonType._instances[System]

    @patch("unmanic.libs.system.UnmanicLogging")
    def test_init_creates_logger(self, mock_logging):
        """Test initialization creates a logger."""
        from unmanic.libs.system import System

        mock_logging.get_logger.return_value = MagicMock()

        system = System()

        mock_logging.get_logger.assert_called_once()
        self.assertIsNotNone(system.logger)

    @patch("unmanic.libs.system.UnmanicLogging")
    def test_singleton_returns_same_instance(self, mock_logging):
        """Test singleton returns the same instance."""
        from unmanic.libs.system import System

        mock_logging.get_logger.return_value = MagicMock()

        system1 = System()
        system2 = System()

        self.assertIs(system1, system2)


class TestSystemGetPythonInfo(unittest.TestCase):
    """Tests for System.__get_python_info method."""

    def setUp(self):
        """Clear singleton before each test."""
        from unmanic.libs.singleton import SingletonType
        from unmanic.libs.system import System

        if System in SingletonType._instances:
            del SingletonType._instances[System]

    def tearDown(self):
        """Clear singleton after each test."""
        from unmanic.libs.singleton import SingletonType
        from unmanic.libs.system import System

        if System in SingletonType._instances:
            del SingletonType._instances[System]

    @patch("unmanic.libs.system.UnmanicLogging")
    def test_returns_python_version_string(self, mock_logging):
        """Test returns Python version as string."""
        from unmanic.libs.system import System

        mock_logging.get_logger.return_value = MagicMock()

        system = System()
        result = system._System__get_python_info()

        self.assertIsInstance(result, str)
        # Should contain version info like "3.11.2.final.0"
        self.assertIn(".", result)

    @patch("unmanic.libs.system.UnmanicLogging")
    def test_caches_python_version(self, mock_logging):
        """Test Python version is cached after first call."""
        from unmanic.libs.system import System

        mock_logging.get_logger.return_value = MagicMock()

        system = System()
        result1 = system._System__get_python_info()
        result2 = system._System__get_python_info()

        self.assertEqual(result1, result2)
        self.assertEqual(system.python_version, result1)


class TestSystemGetPlatformInfo(unittest.TestCase):
    """Tests for System.__get_platform_info method."""

    def setUp(self):
        """Clear singleton before each test."""
        from unmanic.libs.singleton import SingletonType
        from unmanic.libs.system import System

        if System in SingletonType._instances:
            del SingletonType._instances[System]

    def tearDown(self):
        """Clear singleton after each test."""
        from unmanic.libs.singleton import SingletonType
        from unmanic.libs.system import System

        if System in SingletonType._instances:
            del SingletonType._instances[System]

    @patch("unmanic.libs.system.UnmanicLogging")
    def test_returns_platform_info(self, mock_logging):
        """Test returns platform information."""
        from unmanic.libs.system import System

        mock_logging.get_logger.return_value = MagicMock()

        system = System()
        result = system._System__get_platform_info()

        # platform.uname() returns a named tuple
        self.assertTrue(hasattr(result, "system"))
        self.assertTrue(hasattr(result, "node"))

    @patch("unmanic.libs.system.UnmanicLogging")
    def test_caches_platform_info(self, mock_logging):
        """Test platform info is cached after first call."""
        from unmanic.libs.system import System

        mock_logging.get_logger.return_value = MagicMock()

        system = System()
        result1 = system._System__get_platform_info()
        result2 = system._System__get_platform_info()

        self.assertEqual(result1, result2)


class TestSystemGetDevicesInfo(unittest.TestCase):
    """Tests for System.__get_devices_info method."""

    def setUp(self):
        """Clear singleton before each test."""
        from unmanic.libs.singleton import SingletonType
        from unmanic.libs.system import System

        if System in SingletonType._instances:
            del SingletonType._instances[System]

    def tearDown(self):
        """Clear singleton after each test."""
        from unmanic.libs.singleton import SingletonType
        from unmanic.libs.system import System

        if System in SingletonType._instances:
            del SingletonType._instances[System]

    @patch("unmanic.libs.system.UnmanicLogging")
    def test_returns_devices_dict(self, mock_logging):
        """Test returns devices dictionary."""
        from unmanic.libs.system import System

        mock_logging.get_logger.return_value = MagicMock()

        system = System()
        result = system._System__get_devices_info()

        self.assertIsInstance(result, dict)
        self.assertIn("cpu_info", result)
        self.assertIn("gpu_info", result)

    @patch("unmanic.libs.system.UnmanicLogging")
    def test_gpu_info_is_list(self, mock_logging):
        """Test gpu_info is a list."""
        from unmanic.libs.system import System

        mock_logging.get_logger.return_value = MagicMock()

        system = System()
        result = system._System__get_devices_info()

        self.assertIsInstance(result["gpu_info"], list)

    @patch("unmanic.libs.system.UnmanicLogging")
    def test_caches_devices_info(self, mock_logging):
        """Test devices info is cached after first call."""
        from unmanic.libs.system import System

        mock_logging.get_logger.return_value = MagicMock()

        system = System()
        result1 = system._System__get_devices_info()
        result2 = system._System__get_devices_info()

        self.assertIs(result1, result2)


class TestSystemInfo(unittest.TestCase):
    """Tests for System.info method."""

    def setUp(self):
        """Clear singleton before each test."""
        from unmanic.libs.singleton import SingletonType
        from unmanic.libs.system import System

        if System in SingletonType._instances:
            del SingletonType._instances[System]

    def tearDown(self):
        """Clear singleton after each test."""
        from unmanic.libs.singleton import SingletonType
        from unmanic.libs.system import System

        if System in SingletonType._instances:
            del SingletonType._instances[System]

    @patch("unmanic.libs.system.UnmanicLogging")
    def test_returns_complete_info_dict(self, mock_logging):
        """Test info() returns complete system information."""
        from unmanic.libs.system import System

        mock_logging.get_logger.return_value = MagicMock()

        system = System()
        result = system.info()

        self.assertIsInstance(result, dict)
        self.assertIn("devices", result)
        self.assertIn("platform", result)
        self.assertIn("python", result)

    @patch("unmanic.libs.system.UnmanicLogging")
    def test_info_contains_valid_python_version(self, mock_logging):
        """Test info contains valid Python version."""
        from unmanic.libs.system import System

        mock_logging.get_logger.return_value = MagicMock()

        system = System()
        result = system.info()

        python_version = result["python"]
        self.assertIsInstance(python_version, str)
        # Should match current Python version
        expected_start = f"{sys.version_info.major}.{sys.version_info.minor}"
        self.assertTrue(python_version.startswith(expected_start))

    @patch("unmanic.libs.system.UnmanicLogging")
    def test_info_contains_platform_tuple(self, mock_logging):
        """Test info contains platform named tuple."""
        from unmanic.libs.system import System

        mock_logging.get_logger.return_value = MagicMock()

        system = System()
        result = system.info()

        platform_info = result["platform"]
        self.assertTrue(hasattr(platform_info, "system"))

    @patch("unmanic.libs.system.UnmanicLogging")
    def test_info_contains_cpu_info(self, mock_logging):
        """Test info contains CPU information."""
        from unmanic.libs.system import System

        mock_logging.get_logger.return_value = MagicMock()

        system = System()
        result = system.info()

        devices = result["devices"]
        self.assertIn("cpu_info", devices)
        # cpu_info should be a dict with processor info
        self.assertIsInstance(devices["cpu_info"], dict)


if __name__ == "__main__":
    unittest.main()

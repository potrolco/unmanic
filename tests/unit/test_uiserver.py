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


if __name__ == "__main__":
    unittest.main()

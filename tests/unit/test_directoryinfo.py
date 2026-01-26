#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unit tests for UnmanicDirectoryInfo class in unmanic.libs.directoryinfo.

Tests directory info file management (.unmanic files).
"""

import json
import os
import tempfile
import unittest


class TestUnmanicDirectoryInfoException(unittest.TestCase):
    """Tests for UnmanicDirectoryInfoException class."""

    def test_init_sets_message_and_path(self):
        """Test exception initialization sets message and path."""
        from unmanic.libs.directoryinfo import UnmanicDirectoryInfoException

        exc = UnmanicDirectoryInfoException("Test error", "/test/path")

        self.assertEqual(exc.message, "Test error")
        self.assertEqual(exc.path, "/test/path")

    def test_str_returns_message(self):
        """Test str() returns the message."""
        from unmanic.libs.directoryinfo import UnmanicDirectoryInfoException

        exc = UnmanicDirectoryInfoException("Test error", "/test/path")

        self.assertEqual(str(exc), "Test error")

    def test_repr_returns_message(self):
        """Test repr() returns the message."""
        from unmanic.libs.directoryinfo import UnmanicDirectoryInfoException

        exc = UnmanicDirectoryInfoException("Test error", "/test/path")

        self.assertEqual(repr(exc), "Test error")


class TestUnmanicDirectoryInfoInit(unittest.TestCase):
    """Tests for UnmanicDirectoryInfo initialization."""

    def test_init_nonexistent_directory(self):
        """Test init with non-existent directory creates empty json_data."""
        from unmanic.libs.directoryinfo import UnmanicDirectoryInfo

        with tempfile.TemporaryDirectory() as tmpdir:
            subdir = os.path.join(tmpdir, "subdir")
            os.makedirs(subdir)
            # No .unmanic file exists

            info = UnmanicDirectoryInfo(subdir)

            self.assertEqual(info.json_data, {})
            self.assertIsNone(info.config_parser)

    def test_init_with_json_file(self):
        """Test init reads JSON .unmanic file."""
        from unmanic.libs.directoryinfo import UnmanicDirectoryInfo

        with tempfile.TemporaryDirectory() as tmpdir:
            unmanic_path = os.path.join(tmpdir, ".unmanic")
            with open(unmanic_path, "w") as f:
                json.dump({"section": {"key": "value"}}, f)

            info = UnmanicDirectoryInfo(tmpdir)

            self.assertEqual(info.json_data["section"]["key"], "value")

    def test_init_with_ini_file(self):
        """Test init reads INI .unmanic file and migrates to JSON."""
        from unmanic.libs.directoryinfo import UnmanicDirectoryInfo

        with tempfile.TemporaryDirectory() as tmpdir:
            unmanic_path = os.path.join(tmpdir, ".unmanic")
            with open(unmanic_path, "w") as f:
                f.write("[section]\n")
                f.write("key = value\n")

            info = UnmanicDirectoryInfo(tmpdir)

            self.assertIsNotNone(info.json_data)
            self.assertEqual(info.json_data["section"]["key"], "value")

    def test_init_with_invalid_file_raises(self):
        """Test init with invalid file raises exception."""
        from unmanic.libs.directoryinfo import (
            UnmanicDirectoryInfo,
            UnmanicDirectoryInfoException,
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            unmanic_path = os.path.join(tmpdir, ".unmanic")
            # Write invalid content (not JSON, not INI)
            with open(unmanic_path, "w") as f:
                f.write("this is not valid json or ini\nno sections here")

            with self.assertRaises(UnmanicDirectoryInfoException):
                UnmanicDirectoryInfo(tmpdir)


class TestUnmanicDirectoryInfoMigrations(unittest.TestCase):
    """Tests for migration functionality."""

    def test_json_keys_converted_to_lowercase(self):
        """Test JSON migration converts keys to lowercase."""
        from unmanic.libs.directoryinfo import UnmanicDirectoryInfo

        with tempfile.TemporaryDirectory() as tmpdir:
            unmanic_path = os.path.join(tmpdir, ".unmanic")
            with open(unmanic_path, "w") as f:
                json.dump({"Section": {"KEY": "value", "MixedCase": "test"}}, f)

            info = UnmanicDirectoryInfo(tmpdir)

            # Keys should be lowercase
            self.assertEqual(info.json_data["Section"]["key"], "value")
            self.assertEqual(info.json_data["Section"]["mixedcase"], "test")


class TestUnmanicDirectoryInfoSet(unittest.TestCase):
    """Tests for UnmanicDirectoryInfo.set method."""

    def test_set_creates_section_if_missing(self):
        """Test set creates section if it doesn't exist."""
        from unmanic.libs.directoryinfo import UnmanicDirectoryInfo

        with tempfile.TemporaryDirectory() as tmpdir:
            info = UnmanicDirectoryInfo(tmpdir)

            info.set("new_section", "key", "value")

            self.assertEqual(info.json_data["new_section"]["key"], "value")

    def test_set_adds_to_existing_section(self):
        """Test set adds to existing section."""
        from unmanic.libs.directoryinfo import UnmanicDirectoryInfo

        with tempfile.TemporaryDirectory() as tmpdir:
            unmanic_path = os.path.join(tmpdir, ".unmanic")
            with open(unmanic_path, "w") as f:
                json.dump({"section": {"existing": "data"}}, f)

            info = UnmanicDirectoryInfo(tmpdir)
            info.set("section", "new_key", "new_value")

            self.assertEqual(info.json_data["section"]["existing"], "data")
            self.assertEqual(info.json_data["section"]["new_key"], "new_value")

    def test_set_converts_key_to_lowercase(self):
        """Test set converts option key to lowercase."""
        from unmanic.libs.directoryinfo import UnmanicDirectoryInfo

        with tempfile.TemporaryDirectory() as tmpdir:
            info = UnmanicDirectoryInfo(tmpdir)

            info.set("section", "UPPERCASE_KEY", "value")

            self.assertEqual(info.json_data["section"]["uppercase_key"], "value")

    def test_set_with_none_value(self):
        """Test set with None value."""
        from unmanic.libs.directoryinfo import UnmanicDirectoryInfo

        with tempfile.TemporaryDirectory() as tmpdir:
            info = UnmanicDirectoryInfo(tmpdir)

            info.set("section", "key", None)

            self.assertIsNone(info.json_data["section"]["key"])


class TestUnmanicDirectoryInfoGet(unittest.TestCase):
    """Tests for UnmanicDirectoryInfo.get method."""

    def test_get_existing_value(self):
        """Test get returns existing value."""
        from unmanic.libs.directoryinfo import UnmanicDirectoryInfo

        with tempfile.TemporaryDirectory() as tmpdir:
            unmanic_path = os.path.join(tmpdir, ".unmanic")
            with open(unmanic_path, "w") as f:
                json.dump({"section": {"key": "value"}}, f)

            info = UnmanicDirectoryInfo(tmpdir)
            result = info.get("section", "key")

            self.assertEqual(result, "value")

    def test_get_missing_section(self):
        """Test get returns None for missing section."""
        from unmanic.libs.directoryinfo import UnmanicDirectoryInfo

        with tempfile.TemporaryDirectory() as tmpdir:
            info = UnmanicDirectoryInfo(tmpdir)
            result = info.get("nonexistent", "key")

            self.assertIsNone(result)

    def test_get_missing_key(self):
        """Test get returns None for missing key."""
        from unmanic.libs.directoryinfo import UnmanicDirectoryInfo

        with tempfile.TemporaryDirectory() as tmpdir:
            unmanic_path = os.path.join(tmpdir, ".unmanic")
            with open(unmanic_path, "w") as f:
                json.dump({"section": {}}, f)

            info = UnmanicDirectoryInfo(tmpdir)
            result = info.get("section", "nonexistent")

            self.assertIsNone(result)

    def test_get_converts_key_to_lowercase(self):
        """Test get converts option key to lowercase."""
        from unmanic.libs.directoryinfo import UnmanicDirectoryInfo

        with tempfile.TemporaryDirectory() as tmpdir:
            unmanic_path = os.path.join(tmpdir, ".unmanic")
            with open(unmanic_path, "w") as f:
                json.dump({"section": {"mykey": "value"}}, f)

            info = UnmanicDirectoryInfo(tmpdir)
            result = info.get("section", "MYKEY")

            self.assertEqual(result, "value")


class TestUnmanicDirectoryInfoSave(unittest.TestCase):
    """Tests for UnmanicDirectoryInfo.save method."""

    def test_save_creates_file(self):
        """Test save creates .unmanic file."""
        from unmanic.libs.directoryinfo import UnmanicDirectoryInfo

        with tempfile.TemporaryDirectory() as tmpdir:
            info = UnmanicDirectoryInfo(tmpdir)
            info.set("section", "key", "value")

            info.save()

            unmanic_path = os.path.join(tmpdir, ".unmanic")
            self.assertTrue(os.path.exists(unmanic_path))

    def test_save_writes_json(self):
        """Test save writes valid JSON."""
        from unmanic.libs.directoryinfo import UnmanicDirectoryInfo

        with tempfile.TemporaryDirectory() as tmpdir:
            info = UnmanicDirectoryInfo(tmpdir)
            info.set("section", "key", "value")

            info.save()

            unmanic_path = os.path.join(tmpdir, ".unmanic")
            with open(unmanic_path) as f:
                data = json.load(f)

            self.assertEqual(data["section"]["key"], "value")

    def test_save_roundtrip(self):
        """Test save then load preserves data."""
        from unmanic.libs.directoryinfo import UnmanicDirectoryInfo

        with tempfile.TemporaryDirectory() as tmpdir:
            # Save
            info1 = UnmanicDirectoryInfo(tmpdir)
            info1.set("section1", "key1", "value1")
            info1.set("section2", "key2", "value2")
            info1.save()

            # Load
            info2 = UnmanicDirectoryInfo(tmpdir)

            self.assertEqual(info2.get("section1", "key1"), "value1")
            self.assertEqual(info2.get("section2", "key2"), "value2")


class TestUnmanicDirectoryInfoSpecialCharacters(unittest.TestCase):
    """Tests for handling special characters."""

    def test_set_get_with_special_characters(self):
        """Test set/get with special characters in values."""
        from unmanic.libs.directoryinfo import UnmanicDirectoryInfo

        with tempfile.TemporaryDirectory() as tmpdir:
            info = UnmanicDirectoryInfo(tmpdir)
            special_value = 'value with "quotes" and \\backslashes\\ and unicode: äöü'

            info.set("section", "key", special_value)
            info.save()

            info2 = UnmanicDirectoryInfo(tmpdir)
            result = info2.get("section", "key")

            self.assertEqual(result, special_value)

    def test_section_with_special_characters(self):
        """Test section names with special characters."""
        from unmanic.libs.directoryinfo import UnmanicDirectoryInfo

        with tempfile.TemporaryDirectory() as tmpdir:
            info = UnmanicDirectoryInfo(tmpdir)

            info.set("section with spaces", "key", "value")
            info.save()

            info2 = UnmanicDirectoryInfo(tmpdir)
            result = info2.get("section with spaces", "key")

            self.assertEqual(result, "value")


if __name__ == "__main__":
    unittest.main()

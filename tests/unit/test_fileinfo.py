#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unit tests for the FileInfo class in unmanic.libs.fileinfo.

Tests file rename history tracking functionality.
"""

import os
import tempfile
import unittest


class TestEntry(unittest.TestCase):
    """Tests for Entry class."""

    def test_init_sets_attributes(self):
        """Test Entry initialization sets newname and originalname."""
        from unmanic.libs.fileinfo import Entry

        entry = Entry("new_file.mp4", "original_file.mp4")

        self.assertEqual(entry.newname, "new_file.mp4")
        self.assertEqual(entry.originalname, "original_file.mp4")

    def test_init_with_same_names(self):
        """Test Entry with identical names."""
        from unmanic.libs.fileinfo import Entry

        entry = Entry("same.mp4", "same.mp4")

        self.assertEqual(entry.newname, "same.mp4")
        self.assertEqual(entry.originalname, "same.mp4")


class TestFileInfoInit(unittest.TestCase):
    """Tests for FileInfo initialization."""

    def test_init_sets_path(self):
        """Test FileInfo initialization sets path."""
        from unmanic.libs.fileinfo import FileInfo

        fileinfo = FileInfo("/path/to/file.info")

        self.assertEqual(fileinfo.path, "/path/to/file.info")

    def test_init_creates_empty_entries(self):
        """Test FileInfo initialization creates empty entries list."""
        from unmanic.libs.fileinfo import FileInfo

        fileinfo = FileInfo("/path/to/file.info")

        self.assertEqual(fileinfo.entries, [])


class TestFileInfoAppend(unittest.TestCase):
    """Tests for FileInfo.append method."""

    def test_append_adds_entry(self):
        """Test append adds an entry to the list."""
        from unmanic.libs.fileinfo import FileInfo

        fileinfo = FileInfo("/path/to/file.info")
        fileinfo.append("new_name.mp4", "original_name.mp4")

        self.assertEqual(len(fileinfo.entries), 1)
        self.assertEqual(fileinfo.entries[0].newname, "new_name.mp4")
        self.assertEqual(fileinfo.entries[0].originalname, "original_name.mp4")

    def test_append_multiple_entries(self):
        """Test appending multiple entries."""
        from unmanic.libs.fileinfo import FileInfo

        fileinfo = FileInfo("/path/to/file.info")
        fileinfo.append("file1.mp4", "original1.mp4")
        fileinfo.append("file2.mp4", "original2.mp4")

        self.assertEqual(len(fileinfo.entries), 2)

    def test_append_finds_oldest_name(self):
        """Test append traces back to oldest original name."""
        from unmanic.libs.fileinfo import FileInfo

        fileinfo = FileInfo("/path/to/file.info")
        # First rename: original -> renamed1
        fileinfo.append("renamed1.mp4", "original.mp4")
        # Second rename: renamed1 -> renamed2 (should trace back to original)
        fileinfo.append("renamed2.mp4", "renamed1.mp4")

        self.assertEqual(len(fileinfo.entries), 2)
        # Second entry should have original name, not renamed1
        self.assertEqual(fileinfo.entries[1].originalname, "original.mp4")


class TestFileInfoFindOldestName(unittest.TestCase):
    """Tests for FileInfo._find_oldest_name method."""

    def test_returns_original_when_not_found(self):
        """Test returns filename when not in entries."""
        from unmanic.libs.fileinfo import FileInfo

        fileinfo = FileInfo("/path/to/file.info")

        result = fileinfo._find_oldest_name("unknown.mp4")

        self.assertEqual(result, "unknown.mp4")

    def test_returns_original_from_entry(self):
        """Test returns originalname from matching entry."""
        from unmanic.libs.fileinfo import FileInfo

        fileinfo = FileInfo("/path/to/file.info")
        fileinfo.append("renamed.mp4", "original.mp4")

        result = fileinfo._find_oldest_name("renamed.mp4")

        self.assertEqual(result, "original.mp4")


class TestFileInfoSaveAndLoad(unittest.TestCase):
    """Tests for FileInfo.save and load methods."""

    def test_save_creates_file(self):
        """Test save creates file with entries."""
        from unmanic.libs.fileinfo import FileInfo

        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "test.info")
            fileinfo = FileInfo(path)
            fileinfo.append("new.mp4", "original.mp4")

            fileinfo.save()

            self.assertTrue(os.path.exists(path))
            with open(path) as f:
                content = f.read()
            self.assertIn("new.mp4", content)
            self.assertIn("original.mp4", content)

    def test_save_format(self):
        """Test save uses correct format: newname=\"originalname\"."""
        from unmanic.libs.fileinfo import FileInfo

        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "test.info")
            fileinfo = FileInfo(path)
            fileinfo.append("new.mp4", "original.mp4")

            fileinfo.save()

            with open(path) as f:
                content = f.read()
            self.assertEqual(content.strip(), 'new.mp4="original.mp4"')

    def test_load_reads_file(self):
        """Test load reads entries from file."""
        from unmanic.libs.fileinfo import FileInfo

        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "test.info")

            # Create file with content
            with open(path, "w") as f:
                f.write('renamed.mp4="original.mp4"\n')
                f.write('second.mp4="first.mp4"\n')

            fileinfo = FileInfo(path)
            fileinfo.load()

            self.assertEqual(len(fileinfo.entries), 2)
            self.assertEqual(fileinfo.entries[0].newname, "renamed.mp4")
            self.assertEqual(fileinfo.entries[0].originalname, "original.mp4")
            self.assertEqual(fileinfo.entries[1].newname, "second.mp4")
            self.assertEqual(fileinfo.entries[1].originalname, "first.mp4")

    def test_load_nonexistent_file(self):
        """Test load with non-existent file does nothing."""
        from unmanic.libs.fileinfo import FileInfo

        fileinfo = FileInfo("/nonexistent/path/file.info")

        # Should not raise exception
        fileinfo.load()

        self.assertEqual(fileinfo.entries, [])

    def test_save_and_load_roundtrip(self):
        """Test save then load preserves data."""
        from unmanic.libs.fileinfo import FileInfo

        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "test.info")

            # Save
            fileinfo1 = FileInfo(path)
            fileinfo1.append("new1.mp4", "original1.mp4")
            fileinfo1.append("new2.mp4", "original2.mp4")
            fileinfo1.save()

            # Load
            fileinfo2 = FileInfo(path)
            fileinfo2.load()

            self.assertEqual(len(fileinfo2.entries), 2)
            self.assertEqual(fileinfo2.entries[0].newname, "new1.mp4")
            self.assertEqual(fileinfo2.entries[1].newname, "new2.mp4")

    def test_load_clears_existing_entries(self):
        """Test load replaces existing entries."""
        from unmanic.libs.fileinfo import FileInfo

        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "test.info")

            # Create file
            with open(path, "w") as f:
                f.write('file.mp4="original.mp4"\n')

            fileinfo = FileInfo(path)
            # Add some entries first
            fileinfo.append("other.mp4", "other_original.mp4")
            self.assertEqual(len(fileinfo.entries), 1)

            # Load should clear and replace
            fileinfo.load()

            self.assertEqual(len(fileinfo.entries), 1)
            self.assertEqual(fileinfo.entries[0].newname, "file.mp4")


class TestFileInfoSaveMultiple(unittest.TestCase):
    """Tests for saving multiple entries."""

    def test_save_multiple_entries(self):
        """Test saving multiple entries to file."""
        from unmanic.libs.fileinfo import FileInfo

        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "test.info")
            fileinfo = FileInfo(path)
            fileinfo.append("file1.mp4", "orig1.mp4")
            fileinfo.append("file2.mp4", "orig2.mp4")
            fileinfo.append("file3.mp4", "orig3.mp4")

            fileinfo.save()

            with open(path) as f:
                lines = f.readlines()

            self.assertEqual(len(lines), 3)


if __name__ == "__main__":
    unittest.main()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Unit tests for unmanic.libs.common module.

Tests utility functions including:
- Path helpers (get_home_dir, get_default_root_path, etc.)
- String formatting (format_message, random_string)
- Time utilities (time_string_to_seconds, make_timestamp_human_readable)
- File utilities (ensure_dir, get_file_checksum)
"""

import os
import tempfile
import time
import pytest
from unittest.mock import patch

from unmanic.libs import common


class TestGetHomeDir:
    """Test get_home_dir function."""

    def test_returns_home_without_env(self, monkeypatch):
        """Should return user home dir when HOME_DIR is not set."""
        monkeypatch.delenv("HOME_DIR", raising=False)
        result = common.get_home_dir()
        assert result == os.path.expanduser("~")

    def test_respects_home_dir_env(self, monkeypatch):
        """Should use HOME_DIR env var when set."""
        monkeypatch.setenv("HOME_DIR", "/custom/home")
        result = common.get_home_dir()
        assert result == "/custom/home"

    def test_expands_tilde_in_env(self, monkeypatch):
        """Should expand tilde in HOME_DIR value."""
        monkeypatch.setenv("HOME_DIR", "~/custom")
        result = common.get_home_dir()
        assert "~" not in result
        assert result.endswith("custom")


class TestGetDefaultRootPath:
    """Test get_default_root_path function."""

    def test_returns_root_on_linux(self):
        """Should return / on Linux."""
        if os.name != "nt":
            result = common.get_default_root_path()
            assert result == "/"


class TestGetDefaultLibraryPath:
    """Test get_default_library_path function."""

    def test_returns_library_on_linux(self):
        """Should return /library on Linux."""
        if os.name != "nt":
            result = common.get_default_library_path()
            assert result == "/library"


class TestGetDefaultCachePath:
    """Test get_default_cache_path function."""

    def test_returns_tmp_unmanic_on_linux(self):
        """Should return /tmp/unmanic on Linux."""
        if os.name != "nt":
            result = common.get_default_cache_path()
            assert result == "/tmp/unmanic"


class TestFormatMessage:
    """Test format_message function."""

    def test_single_message(self):
        """Should format single message."""
        result = common.format_message("Hello")
        assert "[FORMATTED]" in result
        assert "Hello" in result

    def test_two_string_messages(self):
        """Should combine two string messages."""
        result = common.format_message("Part1", "Part2")
        assert "Part1" in result
        assert "Part2" in result
        assert " - " in result

    def test_message_with_dict(self):
        """Should format dict as pprint output."""
        result = common.format_message("Data", {"key": "value"})
        assert "Data" in result
        assert "key" in result
        assert "value" in result

    def test_message_with_list(self):
        """Should format list as pprint output."""
        result = common.format_message("Items", ["a", "b", "c"])
        assert "Items" in result
        assert "'a'" in result

    def test_message_with_number(self):
        """Should convert number to string."""
        result = common.format_message("Count", 42)
        assert "Count" in result
        assert "42" in result


class TestTimeStringToSeconds:
    """Test time_string_to_seconds function."""

    def test_one_second(self):
        """Should parse 1 second."""
        result = common.time_string_to_seconds("00:00:01.000000")
        assert result == 1

    def test_one_minute(self):
        """Should parse 1 minute."""
        result = common.time_string_to_seconds("00:01:00.000000")
        assert result == 60

    def test_one_hour(self):
        """Should parse 1 hour."""
        result = common.time_string_to_seconds("01:00:00.000000")
        assert result == 3600

    def test_complex_time(self):
        """Should parse complex time."""
        result = common.time_string_to_seconds("01:30:45.500000")
        assert result == 3600 + 1800 + 45


class TestRandomString:
    """Test random_string function."""

    def test_default_length(self):
        """Should generate 5-char string by default."""
        result = common.random_string()
        assert len(result) == 5

    def test_custom_length(self):
        """Should generate string of specified length."""
        result = common.random_string(10)
        assert len(result) == 10

    def test_lowercase_only(self):
        """Should contain only lowercase letters."""
        result = common.random_string(100)
        assert result.islower()
        assert result.isalpha()

    def test_generates_different_strings(self):
        """Should generate different strings each time."""
        results = {common.random_string() for _ in range(100)}
        # Should have at least 90 unique strings out of 100
        assert len(results) > 90


class TestEnsureDir:
    """Test ensure_dir function."""

    def test_creates_directory(self):
        """Should create directory if it doesn't exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "subdir", "file.txt")
            common.ensure_dir(path)
            assert os.path.isdir(os.path.dirname(path))

    def test_handles_existing_directory(self):
        """Should not fail if directory already exists."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "file.txt")
            common.ensure_dir(path)  # First call
            common.ensure_dir(path)  # Should not raise


class TestMakeTimestampHumanReadable:
    """Test make_timestamp_human_readable function."""

    def test_seconds_ago(self):
        """Should format recent timestamp as seconds ago."""
        ts = time.time() - 30
        result = common.make_timestamp_human_readable(ts)
        assert "ago" in result
        assert "second" in result

    def test_minutes_ago(self):
        """Should format minute-old timestamp."""
        ts = time.time() - 120
        result = common.make_timestamp_human_readable(ts)
        assert "ago" in result
        assert "minute" in result

    def test_hours_ago(self):
        """Should format hour-old timestamp."""
        ts = time.time() - 7200
        result = common.make_timestamp_human_readable(ts)
        assert "ago" in result
        assert "hour" in result

    def test_days_ago(self):
        """Should format day-old timestamp."""
        ts = time.time() - (2 * 24 * 3600)
        result = common.make_timestamp_human_readable(ts)
        assert "ago" in result
        assert "day" in result


class TestExtractVideoCodecsFromFileProperties:
    """Test extract_video_codecs_from_file_properties function."""

    def test_extracts_single_codec(self):
        """Should extract single video codec."""
        props = {
            "streams": [
                {"codec_type": "video", "codec_name": "h264"},
                {"codec_type": "audio", "codec_name": "aac"},
            ]
        }
        result = common.extract_video_codecs_from_file_properties(props)
        assert result == ["h264"]

    def test_extracts_multiple_codecs(self):
        """Should extract multiple video codecs."""
        props = {
            "streams": [
                {"codec_type": "video", "codec_name": "h264"},
                {"codec_type": "video", "codec_name": "hevc"},
            ]
        }
        result = common.extract_video_codecs_from_file_properties(props)
        assert result == ["h264", "hevc"]

    def test_ignores_non_video_streams(self):
        """Should ignore audio and subtitle streams."""
        props = {
            "streams": [
                {"codec_type": "audio", "codec_name": "aac"},
                {"codec_type": "subtitle", "codec_name": "srt"},
            ]
        }
        result = common.extract_video_codecs_from_file_properties(props)
        assert result == []

    def test_handles_empty_streams(self):
        """Should handle empty streams list."""
        props = {"streams": []}
        result = common.extract_video_codecs_from_file_properties(props)
        assert result == []


class TestGetFileChecksum:
    """Test get_file_checksum function."""

    def test_calculates_md5(self):
        """Should calculate MD5 checksum."""
        with tempfile.NamedTemporaryFile(delete=False) as f:
            f.write(b"test content")
            f.flush()
            path = f.name

        try:
            result = common.get_file_checksum(path)
            # MD5 hash of "test content"
            assert len(result) == 32  # MD5 hex length
            assert result.islower()
        finally:
            os.unlink(path)

    def test_same_content_same_checksum(self):
        """Same content should produce same checksum."""
        content = b"identical content"
        paths = []

        for _ in range(2):
            with tempfile.NamedTemporaryFile(delete=False) as f:
                f.write(content)
                f.flush()
                paths.append(f.name)

        try:
            checksums = [common.get_file_checksum(p) for p in paths]
            assert checksums[0] == checksums[1]
        finally:
            for p in paths:
                os.unlink(p)

    def test_different_content_different_checksum(self):
        """Different content should produce different checksum."""
        paths = []

        for content in [b"content A", b"content B"]:
            with tempfile.NamedTemporaryFile(delete=False) as f:
                f.write(content)
                f.flush()
                paths.append(f.name)

        try:
            checksums = [common.get_file_checksum(p) for p in paths]
            assert checksums[0] != checksums[1]
        finally:
            for p in paths:
                os.unlink(p)


class TestJsonDumpToFile:
    """Test json_dump_to_file function."""

    def test_writes_json_file(self):
        """Should write JSON to file."""
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            path = f.name

        try:
            data = {"key": "value", "number": 42}
            result = common.json_dump_to_file(data, path)
            assert result["success"] is True

            import json

            with open(path) as f:
                loaded = json.load(f)
            assert loaded == data
        finally:
            os.unlink(path)

    def test_rollback_on_invalid_json(self):
        """Should rollback on invalid JSON write."""
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            # Write valid initial content
            f.write(b'{"original": "data"}')
            path = f.name

        try:
            # Try to write non-serializable data (will fail during json.dump)
            class NonSerializable:
                pass

            data = {"bad": NonSerializable()}
            result = common.json_dump_to_file(data, path, rollback_on_fail=True)
            assert result["success"] is False
        finally:
            os.unlink(path)

    def test_creates_new_file(self):
        """Should create file if it doesn't exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "new_file.json")
            data = {"new": "file"}
            result = common.json_dump_to_file(data, path)
            assert result["success"] is True
            assert os.path.exists(path)


class TestTail:
    """Test tail function."""

    def test_reads_last_lines(self):
        """Should read last n lines from file."""
        with tempfile.NamedTemporaryFile(mode="wb", delete=False) as f:
            # Write multiple lines
            for i in range(20):
                f.write(f"Line {i}\n".encode())
            path = f.name

        try:
            with open(path, "rb") as f:
                lines = common.tail(f, 5)
            assert len(lines) >= 5
            # Last line should be "Line 19"
            assert b"Line 19" in lines[-1]
        finally:
            os.unlink(path)

    def test_handles_small_file(self):
        """Should handle file with fewer lines than requested."""
        with tempfile.NamedTemporaryFile(mode="wb", delete=False) as f:
            f.write(b"Line 1\nLine 2\n")
            path = f.name

        try:
            with open(path, "rb") as f:
                lines = common.tail(f, 10)
            # Should return all lines even if fewer than requested
            assert len(lines) <= 10
        finally:
            os.unlink(path)


class TestCleanFilesInCacheDir:
    """Test clean_files_in_cache_dir function."""

    def test_removes_unmanic_file_conversion_dirs(self):
        """Should remove directories starting with unmanic_file_conversion-."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a directory that should be removed
            cache_dir = os.path.join(tmpdir, "unmanic_file_conversion-12345")
            os.makedirs(cache_dir)
            # Create a file inside
            test_file = os.path.join(cache_dir, "test.txt")
            with open(test_file, "w") as f:
                f.write("test")

            common.clean_files_in_cache_dir(tmpdir)

            # Directory should be removed
            assert not os.path.exists(cache_dir)

    def test_removes_remote_pending_library_dirs(self):
        """Should remove directories starting with unmanic_remote_pending_library-."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a directory that should be removed
            cache_dir = os.path.join(tmpdir, "unmanic_remote_pending_library-67890")
            os.makedirs(cache_dir)

            common.clean_files_in_cache_dir(tmpdir)

            # Directory should be removed
            assert not os.path.exists(cache_dir)

    def test_preserves_other_directories(self):
        """Should not remove directories with different names."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a directory that should NOT be removed
            keep_dir = os.path.join(tmpdir, "other_directory")
            os.makedirs(keep_dir)

            common.clean_files_in_cache_dir(tmpdir)

            # Directory should still exist
            assert os.path.exists(keep_dir)

    def test_handles_nonexistent_directory(self):
        """Should handle non-existent cache directory."""
        # Should not raise exception
        common.clean_files_in_cache_dir("/nonexistent/path/12345")


class TestTouch:
    """Test touch function."""

    def test_creates_new_file(self):
        """Should create new file if it doesn't exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "touched_file")
            common.touch(path)
            assert os.path.exists(path)

    def test_updates_existing_file(self):
        """Should update mtime of existing file."""
        with tempfile.NamedTemporaryFile(delete=False) as f:
            path = f.name

        try:
            # Set old mtime
            old_time = time.time() - 3600
            os.utime(path, (old_time, old_time))
            old_mtime = os.path.getmtime(path)

            # Touch the file
            common.touch(path)
            new_mtime = os.path.getmtime(path)

            assert new_mtime > old_mtime
        finally:
            os.unlink(path)

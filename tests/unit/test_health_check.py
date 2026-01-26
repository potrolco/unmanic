#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Unit tests for unmanic.libs.health_check module.

Tests video file health checking utilities.
"""

import os
import tempfile
import pytest
from unittest.mock import patch, MagicMock
import subprocess

from unmanic.libs.health_check import (
    HealthStatus,
    HealthCheckResult,
    check_file_integrity,
    get_file_checksum,
    quick_health_check,
    compare_checksums,
)


class TestHealthStatus:
    """Test HealthStatus enum."""

    def test_has_healthy_status(self):
        """Should have HEALTHY status."""
        assert HealthStatus.HEALTHY.value == "healthy"

    def test_has_corrupted_status(self):
        """Should have CORRUPTED status."""
        assert HealthStatus.CORRUPTED.value == "corrupted"

    def test_has_warning_status(self):
        """Should have WARNING status."""
        assert HealthStatus.WARNING.value == "warning"

    def test_has_error_status(self):
        """Should have ERROR status."""
        assert HealthStatus.ERROR.value == "error"


class TestHealthCheckResult:
    """Test HealthCheckResult dataclass."""

    def test_creates_result_with_defaults(self):
        """Should create result with default values."""
        result = HealthCheckResult(
            status=HealthStatus.HEALTHY,
            path="/test/file.mkv",
        )
        assert result.status == HealthStatus.HEALTHY
        assert result.path == "/test/file.mkv"
        assert result.errors == []
        assert result.warnings == []

    def test_to_dict(self):
        """Should convert to dictionary."""
        result = HealthCheckResult(
            status=HealthStatus.CORRUPTED,
            path="/test/file.mkv",
            errors=["Error 1"],
            warnings=["Warning 1"],
            checksum="abc123",
        )
        d = result.to_dict()
        assert d["status"] == "corrupted"
        assert d["path"] == "/test/file.mkv"
        assert d["errors"] == ["Error 1"]
        assert d["checksum"] == "abc123"


class TestCheckFileIntegrity:
    """Test check_file_integrity function."""

    def test_returns_error_for_missing_file(self):
        """Should return ERROR for non-existent file."""
        result = check_file_integrity("/nonexistent/file.mkv")
        assert result.status == HealthStatus.ERROR
        assert "not found" in result.errors[0].lower()

    def test_returns_healthy_for_clean_file(self):
        """Should return HEALTHY when FFmpeg finds no errors."""
        with tempfile.NamedTemporaryFile(suffix=".mkv", delete=False) as f:
            f.write(b"fake video content")
            path = f.name

        try:
            mock_result = MagicMock()
            mock_result.stderr = ""
            mock_result.returncode = 0

            with patch("subprocess.run", return_value=mock_result):
                result = check_file_integrity(path)
                assert result.status == HealthStatus.HEALTHY
                assert result.errors == []
        finally:
            os.unlink(path)

    def test_returns_corrupted_for_errors(self):
        """Should return CORRUPTED when FFmpeg finds errors."""
        with tempfile.NamedTemporaryFile(suffix=".mkv", delete=False) as f:
            f.write(b"fake video content")
            path = f.name

        try:
            mock_result = MagicMock()
            mock_result.stderr = "error: Invalid NAL unit\nerror: Corrupted frame"
            mock_result.returncode = 1

            with patch("subprocess.run", return_value=mock_result):
                result = check_file_integrity(path)
                assert result.status == HealthStatus.CORRUPTED
                assert len(result.errors) == 2
        finally:
            os.unlink(path)

    def test_returns_warning_for_warnings_only(self):
        """Should return WARNING when only warnings found."""
        with tempfile.NamedTemporaryFile(suffix=".mkv", delete=False) as f:
            f.write(b"fake video content")
            path = f.name

        try:
            mock_result = MagicMock()
            mock_result.stderr = "warning: Discarding data"
            mock_result.returncode = 0

            with patch("subprocess.run", return_value=mock_result):
                result = check_file_integrity(path)
                assert result.status == HealthStatus.WARNING
                assert len(result.warnings) == 1
        finally:
            os.unlink(path)

    def test_handles_timeout(self):
        """Should return ERROR on timeout."""
        with tempfile.NamedTemporaryFile(suffix=".mkv", delete=False) as f:
            f.write(b"fake video content")
            path = f.name

        try:
            with patch("subprocess.run", side_effect=subprocess.TimeoutExpired("cmd", 300)):
                result = check_file_integrity(path, timeout_seconds=300)
                assert result.status == HealthStatus.ERROR
                assert "timed out" in result.errors[0].lower()
        finally:
            os.unlink(path)

    def test_handles_ffmpeg_not_found(self):
        """Should return ERROR when FFmpeg not found."""
        with tempfile.NamedTemporaryFile(suffix=".mkv", delete=False) as f:
            f.write(b"fake video content")
            path = f.name

        try:
            with patch("subprocess.run", side_effect=FileNotFoundError):
                result = check_file_integrity(path, ffmpeg_path="/nonexistent/ffmpeg")
                assert result.status == HealthStatus.ERROR
                assert "not found" in result.errors[0].lower()
        finally:
            os.unlink(path)


class TestGetFileChecksum:
    """Test get_file_checksum function."""

    def test_returns_md5_by_default(self):
        """Should return MD5 checksum by default."""
        with tempfile.NamedTemporaryFile(delete=False) as f:
            f.write(b"test content")
            path = f.name

        try:
            checksum = get_file_checksum(path)
            assert checksum is not None
            assert len(checksum) == 32  # MD5 hex length
        finally:
            os.unlink(path)

    def test_returns_sha256(self):
        """Should return SHA256 checksum when requested."""
        with tempfile.NamedTemporaryFile(delete=False) as f:
            f.write(b"test content")
            path = f.name

        try:
            checksum = get_file_checksum(path, algorithm="sha256")
            assert checksum is not None
            assert len(checksum) == 64  # SHA256 hex length
        finally:
            os.unlink(path)

    def test_returns_none_for_missing_file(self):
        """Should return None for non-existent file."""
        checksum = get_file_checksum("/nonexistent/file.mkv")
        assert checksum is None

    def test_returns_none_for_unsupported_algorithm(self):
        """Should return None for unsupported algorithm."""
        with tempfile.NamedTemporaryFile(delete=False) as f:
            f.write(b"test content")
            path = f.name

        try:
            checksum = get_file_checksum(path, algorithm="unsupported")
            assert checksum is None
        finally:
            os.unlink(path)

    def test_same_content_same_checksum(self):
        """Same content should produce same checksum."""
        content = b"identical content"
        paths = []

        for _ in range(2):
            with tempfile.NamedTemporaryFile(delete=False) as f:
                f.write(content)
                paths.append(f.name)

        try:
            checksums = [get_file_checksum(p) for p in paths]
            assert checksums[0] == checksums[1]
        finally:
            for p in paths:
                os.unlink(p)


class TestQuickHealthCheck:
    """Test quick_health_check function."""

    def test_returns_true_for_healthy(self):
        """Should return True for healthy file."""
        with patch("unmanic.libs.health_check.check_file_integrity") as mock_check:
            mock_check.return_value = HealthCheckResult(status=HealthStatus.HEALTHY, path="/test.mkv")
            assert quick_health_check("/test.mkv") is True

    def test_returns_true_for_warning(self):
        """Should return True for file with warnings (still usable)."""
        with patch("unmanic.libs.health_check.check_file_integrity") as mock_check:
            mock_check.return_value = HealthCheckResult(status=HealthStatus.WARNING, path="/test.mkv")
            assert quick_health_check("/test.mkv") is True

    def test_returns_false_for_corrupted(self):
        """Should return False for corrupted file."""
        with patch("unmanic.libs.health_check.check_file_integrity") as mock_check:
            mock_check.return_value = HealthCheckResult(status=HealthStatus.CORRUPTED, path="/test.mkv")
            assert quick_health_check("/test.mkv") is False


class TestCompareChecksums:
    """Test compare_checksums function."""

    def test_compares_two_files(self):
        """Should compare checksums of two files."""
        paths = []
        for content in [b"content A", b"content B"]:
            with tempfile.NamedTemporaryFile(delete=False) as f:
                f.write(content)
                paths.append(f.name)

        try:
            result = compare_checksums(paths[0], paths[1])
            assert result["original"]["exists"] is True
            assert result["transcoded"]["exists"] is True
            assert result["checksums_differ"] is True
            assert result["algorithm"] == "md5"
        finally:
            for p in paths:
                os.unlink(p)

    def test_handles_missing_original(self):
        """Should handle missing original file."""
        with tempfile.NamedTemporaryFile(delete=False) as f:
            f.write(b"content")
            transcoded_path = f.name

        try:
            result = compare_checksums("/nonexistent.mkv", transcoded_path)
            assert result["original"]["exists"] is False
            assert result["original"]["checksum"] is None
        finally:
            os.unlink(transcoded_path)

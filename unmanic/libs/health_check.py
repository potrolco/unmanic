#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    unmanic.health_check.py

    Video file health checking utilities for detecting corruption.

    Written by:               TARS Modernization (Phase 2)
    Date:                     26 Jan 2026

    Copyright:
           Copyright (C) Josh Sunnex - All Rights Reserved
           (TARS Fork - potrolco/unmanic)

"""

import hashlib
import os
import subprocess
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional

from unmanic.libs.logs import UnmanicLogging

logger = UnmanicLogging.get_logger(name="HealthCheck")


class HealthStatus(Enum):
    """Health check result status."""

    HEALTHY = "healthy"
    CORRUPTED = "corrupted"
    WARNING = "warning"
    UNKNOWN = "unknown"
    ERROR = "error"


@dataclass
class HealthCheckResult:
    """Result of a video file health check.

    Attributes:
        status: Overall health status
        path: Path to the checked file
        errors: List of error messages found
        warnings: List of warning messages found
        checksum: File checksum (if calculated)
        duration_seconds: Time taken to perform check
        file_size_bytes: Size of the file
        checked_at: Unix timestamp of when check was performed
    """

    status: HealthStatus
    path: str
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    checksum: Optional[str] = None
    duration_seconds: float = 0.0
    file_size_bytes: int = 0
    checked_at: float = field(default_factory=time.time)

    def to_dict(self) -> dict:
        """Convert result to dictionary for JSON serialization."""
        return {
            "status": self.status.value,
            "path": self.path,
            "errors": self.errors,
            "warnings": self.warnings,
            "checksum": self.checksum,
            "duration_seconds": self.duration_seconds,
            "file_size_bytes": self.file_size_bytes,
            "checked_at": self.checked_at,
        }


def check_file_integrity(
    file_path: str,
    ffmpeg_path: str = "ffmpeg",
    timeout_seconds: int = 300,
) -> HealthCheckResult:
    """
    Check video file integrity using FFmpeg error detection.

    Runs FFmpeg with error-level logging to detect corruption, invalid
    streams, and other issues without actually transcoding.

    Args:
        file_path: Path to the video file to check
        ffmpeg_path: Path to FFmpeg executable
        timeout_seconds: Maximum time to run the check

    Returns:
        HealthCheckResult with status and any errors/warnings found
    """
    start_time = time.time()

    # Validate file exists
    if not os.path.exists(file_path):
        return HealthCheckResult(
            status=HealthStatus.ERROR,
            path=file_path,
            errors=[f"File not found: {file_path}"],
        )

    file_size = os.path.getsize(file_path)

    # Build FFmpeg command for integrity check
    # -v error: Only show errors
    # -i: Input file
    # -f null -: Output to null (no actual transcoding)
    cmd = [
        ffmpeg_path,
        "-v",
        "error",
        "-i",
        file_path,
        "-f",
        "null",
        "-",
    ]

    errors: List[str] = []
    warnings: List[str] = []

    try:
        logger.debug(f"Running integrity check on: {file_path}")

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
        )

        # Parse stderr for errors and warnings
        if result.stderr:
            for line in result.stderr.strip().split("\n"):
                line = line.strip()
                if not line:
                    continue

                # Categorize by severity
                line_lower = line.lower()
                if "error" in line_lower or "invalid" in line_lower:
                    errors.append(line)
                elif "warning" in line_lower:
                    warnings.append(line)
                else:
                    # Treat unknown messages as warnings
                    warnings.append(line)

        # Determine overall status
        if errors:
            status = HealthStatus.CORRUPTED
        elif warnings:
            status = HealthStatus.WARNING
        else:
            status = HealthStatus.HEALTHY

        duration = time.time() - start_time

        logger.info(
            f"Health check complete for {file_path}: " f"status={status.value}, errors={len(errors)}, warnings={len(warnings)}"
        )

        return HealthCheckResult(
            status=status,
            path=file_path,
            errors=errors,
            warnings=warnings,
            duration_seconds=duration,
            file_size_bytes=file_size,
        )

    except subprocess.TimeoutExpired:
        return HealthCheckResult(
            status=HealthStatus.ERROR,
            path=file_path,
            errors=[f"Health check timed out after {timeout_seconds}s"],
            duration_seconds=time.time() - start_time,
            file_size_bytes=file_size,
        )
    except FileNotFoundError:
        return HealthCheckResult(
            status=HealthStatus.ERROR,
            path=file_path,
            errors=[f"FFmpeg not found at: {ffmpeg_path}"],
            duration_seconds=time.time() - start_time,
            file_size_bytes=file_size,
        )
    except subprocess.SubprocessError as e:
        return HealthCheckResult(
            status=HealthStatus.ERROR,
            path=file_path,
            errors=[f"Subprocess error: {str(e)}"],
            duration_seconds=time.time() - start_time,
            file_size_bytes=file_size,
        )


def get_file_checksum(
    file_path: str,
    algorithm: str = "md5",
    chunk_size: int = 8192,
) -> Optional[str]:
    """
    Calculate checksum of a file.

    Args:
        file_path: Path to the file
        algorithm: Hash algorithm (md5, sha256, sha1)
        chunk_size: Size of chunks to read

    Returns:
        Hex digest of the checksum, or None on error
    """
    if not os.path.exists(file_path):
        logger.warning(f"Cannot calculate checksum - file not found: {file_path}")
        return None

    try:
        if algorithm == "md5":
            hasher = hashlib.md5()
        elif algorithm == "sha256":
            hasher = hashlib.sha256()
        elif algorithm == "sha1":
            hasher = hashlib.sha1()
        else:
            logger.error(f"Unsupported hash algorithm: {algorithm}")
            return None

        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(chunk_size), b""):
                hasher.update(chunk)

        return hasher.hexdigest()

    except OSError as e:
        logger.error(f"Error reading file for checksum: {e}")
        return None


def quick_health_check(file_path: str) -> bool:
    """
    Perform a quick health check on a file.

    This is a simplified check that returns True if the file appears
    healthy, False otherwise. Use check_file_integrity() for detailed
    results.

    Args:
        file_path: Path to the video file

    Returns:
        True if file appears healthy, False otherwise
    """
    result = check_file_integrity(file_path)
    return result.status in (HealthStatus.HEALTHY, HealthStatus.WARNING)


def compare_checksums(
    original_path: str,
    transcoded_path: str,
    algorithm: str = "md5",
) -> dict:
    """
    Compare checksums of original and transcoded files.

    Note: Checksums will ALWAYS differ after transcoding (expected).
    This is useful for detecting if the output file was written correctly.

    Args:
        original_path: Path to original file
        transcoded_path: Path to transcoded file
        algorithm: Hash algorithm to use

    Returns:
        Dictionary with checksums and comparison info
    """
    original_checksum = get_file_checksum(original_path, algorithm)
    transcoded_checksum = get_file_checksum(transcoded_path, algorithm)

    return {
        "original": {
            "path": original_path,
            "checksum": original_checksum,
            "exists": os.path.exists(original_path),
        },
        "transcoded": {
            "path": transcoded_path,
            "checksum": transcoded_checksum,
            "exists": os.path.exists(transcoded_path),
        },
        "checksums_differ": original_checksum != transcoded_checksum,
        "algorithm": algorithm,
    }

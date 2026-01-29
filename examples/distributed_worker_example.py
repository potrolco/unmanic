#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    Example distributed worker for TARS/Unmanic.

    This example demonstrates how to create a remote worker that connects
    to a TARS server, claims transcoding tasks, processes them, and reports status.

    Usage:
        python3 distributed_worker_example.py \\
            --server http://tars-server:8888 \\
            --name "Worker-01" \\
            --hostname $(hostname)

    Requirements:
        - Python 3.8+
        - requests library (pip install requests)
        - FFmpeg installed on worker machine

    Written by: TARS Modernization (Session 154)
    Date: 29 Jan 2026
"""

import argparse
import logging
import os
import subprocess
import sys
from pathlib import Path

# Add unmanic to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from unmanic.libs.distributed_worker_client import DistributedWorkerClient  # noqa: E402


def setup_logging(verbose: bool = False) -> logging.Logger:
    """Configure logging for the worker."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    return logging.getLogger("DistributedWorker")


def check_ffmpeg() -> bool:
    """Verify FFmpeg is installed and accessible."""
    try:
        result = subprocess.run(
            ["ffmpeg", "-version"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        return result.returncode == 0
    except (subprocess.SubprocessError, FileNotFoundError):
        return False


def process_transcoding_task(task: dict, logger: logging.Logger) -> tuple:
    """
    Process a transcoding task.

    This is a simplified example. In production, you would:
    - Mount source and cache directories (NFS/SMB)
    - Use proper FFmpeg command generation
    - Handle various codecs and settings
    - Monitor progress and update status
    - Handle errors gracefully

    :param task: Task dict from server
    :param logger: Logger instance
    :return: (success: bool, result: dict)
    """
    task_id = task["task_id"]
    source_file = task["source_file"]
    cache_path = task["cache_path"]

    logger.info(f"Task {task_id}: Processing {source_file}")

    # Example: Just probe the file instead of actual transcoding
    try:
        # Run ffprobe to get file info
        result = subprocess.run(
            [
                "ffprobe",
                "-v",
                "quiet",
                "-print_format",
                "json",
                "-show_format",
                "-show_streams",
                source_file,
            ],
            capture_output=True,
            text=True,
            timeout=30,
        )

        if result.returncode == 0:
            logger.info(f"Task {task_id}: File probe successful")
            return (
                True,
                {
                    "status": "success",
                    "message": "Task completed (example worker)",
                    "output_file": cache_path,
                },
            )
        else:
            logger.error(f"Task {task_id}: FFprobe failed")
            return (
                False,
                {
                    "status": "failed",
                    "error": f"FFprobe failed: {result.stderr}",
                },
            )

    except subprocess.TimeoutExpired:
        logger.error(f"Task {task_id}: FFprobe timed out")
        return (
            False,
            {
                "status": "failed",
                "error": "FFprobe timed out",
            },
        )
    except Exception as e:
        logger.error(f"Task {task_id}: Unexpected error: {str(e)}", exc_info=True)
        return (
            False,
            {
                "status": "failed",
                "error": f"Unexpected error: {str(e)}",
            },
        )


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="TARS Distributed Worker Example")
    parser.add_argument(
        "--server",
        required=True,
        help="TARS server URL (e.g., http://tars-server:8888)",
    )
    parser.add_argument(
        "--name",
        required=True,
        help="Worker name (e.g., Worker-01)",
    )
    parser.add_argument(
        "--hostname",
        required=True,
        help="Worker hostname",
    )
    parser.add_argument(
        "--capabilities",
        nargs="+",
        default=["video", "audio"],
        help="Worker capabilities (default: video audio)",
    )
    parser.add_argument(
        "--poll-interval",
        type=int,
        default=10,
        help="Seconds between task polls (default: 10)",
    )
    parser.add_argument(
        "--heartbeat-interval",
        type=int,
        default=60,
        help="Seconds between heartbeats (default: 60)",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose logging",
    )

    args = parser.parse_args()

    # Setup logging
    logger = setup_logging(args.verbose)

    # Check prerequisites
    if not check_ffmpeg():
        logger.error("FFmpeg not found. Please install FFmpeg and try again.")
        sys.exit(1)

    logger.info("=" * 60)
    logger.info("TARS Distributed Worker Example")
    logger.info("=" * 60)
    logger.info(f"Server: {args.server}")
    logger.info(f"Worker Name: {args.name}")
    logger.info(f"Hostname: {args.hostname}")
    logger.info(f"Capabilities: {', '.join(args.capabilities)}")
    logger.info("=" * 60)

    # Create worker client
    client = DistributedWorkerClient(
        server_url=args.server,
        worker_name=args.name,
        worker_hostname=args.hostname,
        capabilities=args.capabilities,
        logger=logger,
    )

    # Register worker
    try:
        logger.info("Registering worker with server...")
        client.register()
        logger.info(f"✓ Registration successful! Worker ID: {client.worker_id}")
    except Exception as e:
        logger.error(f"✗ Registration failed: {str(e)}")
        sys.exit(1)

    # Define task processor
    def task_processor(task: dict) -> tuple:
        return process_transcoding_task(task, logger)

    # Start worker loop
    logger.info("Starting worker loop...")
    logger.info("Press Ctrl+C to stop")

    try:
        client.run_worker_loop(
            task_processor_func=task_processor,
            poll_interval=args.poll_interval,
            heartbeat_interval=args.heartbeat_interval,
        )
    except KeyboardInterrupt:
        logger.info("\nShutting down worker...")
    except Exception as e:
        logger.error(f"Worker crashed: {str(e)}", exc_info=True)
        sys.exit(1)

    logger.info("Worker stopped")


if __name__ == "__main__":
    main()

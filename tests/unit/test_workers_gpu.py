#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Unit tests for GPU integration in unmanic.libs.workers module.

Tests GPU acquisition, release, and status reporting for workers (Phase 3).
"""

import queue
import threading

import pytest
from unittest.mock import MagicMock, patch

from unmanic.libs.gpu_manager import GPUType, GPUDevice, AllocationStrategy
from unmanic.libs.singleton import SingletonType


class TestWorkerGPUIntegration:
    """Test GPU integration in Worker class."""

    @pytest.fixture(autouse=True)
    def reset_singleton(self):
        """Reset singleton before each test."""
        SingletonType._instances = {}
        yield
        SingletonType._instances = {}

    @pytest.fixture
    def mock_worker_deps(self):
        """Mock worker dependencies."""
        with patch("unmanic.libs.workers.UnmanicLogging") as mock_logging, patch(
            "unmanic.libs.gpu_manager.HardwareAccelerationHandle"
        ) as mock_hw:
            mock_logging.get_logger.return_value = MagicMock()
            mock_hw.return_value.get_hwaccel_devices.return_value = []
            yield mock_logging, mock_hw

    def test_worker_has_current_gpu_attribute(self, mock_worker_deps):
        """Worker should have current_gpu attribute."""
        from unmanic.libs.workers import Worker

        pending_q = queue.Queue()
        complete_q = queue.Queue()
        event = threading.Event()

        worker = Worker(
            thread_id=0,
            name="W0",
            worker_group_id=1,
            pending_queue=pending_q,
            complete_queue=complete_q,
            event=event,
        )

        assert hasattr(worker, "current_gpu")
        assert worker.current_gpu is None

    def test_worker_status_includes_gpu_field(self, mock_worker_deps):
        """Worker status should include gpu field."""
        from unmanic.libs.workers import Worker

        pending_q = queue.Queue()
        complete_q = queue.Queue()
        event = threading.Event()

        worker = Worker(
            thread_id=0,
            name="W0",
            worker_group_id=1,
            pending_queue=pending_q,
            complete_queue=complete_q,
            event=event,
        )

        status = worker.get_status()

        assert "gpu" in status
        assert status["gpu"] is None

    def test_worker_status_includes_gpu_info_when_allocated(self, mock_worker_deps):
        """Worker status should include GPU info when GPU is allocated."""
        from unmanic.libs.workers import Worker

        pending_q = queue.Queue()
        complete_q = queue.Queue()
        event = threading.Event()

        worker = Worker(
            thread_id=0,
            name="W0",
            worker_group_id=1,
            pending_queue=pending_q,
            complete_queue=complete_q,
            event=event,
        )

        # Manually set GPU for testing
        worker.current_gpu = GPUDevice(
            device_id="cuda:0",
            gpu_type=GPUType.CUDA,
            hwaccel_device="0",
            display_name="NVIDIA GPU 0",
        )

        status = worker.get_status()

        assert status["gpu"] is not None
        assert status["gpu"]["device_id"] == "cuda:0"
        assert status["gpu"]["gpu_type"] == "cuda"

    def test_worker_get_current_gpu(self, mock_worker_deps):
        """Worker should have get_current_gpu method."""
        from unmanic.libs.workers import Worker

        pending_q = queue.Queue()
        complete_q = queue.Queue()
        event = threading.Event()

        worker = Worker(
            thread_id=0,
            name="W0",
            worker_group_id=1,
            pending_queue=pending_q,
            complete_queue=complete_q,
            event=event,
        )

        assert worker.get_current_gpu() is None

        # Set GPU
        gpu = GPUDevice(
            device_id="cuda:0",
            gpu_type=GPUType.CUDA,
            hwaccel_device="0",
        )
        worker.current_gpu = gpu

        assert worker.get_current_gpu() == gpu


class TestWorkerGPUAcquisition:
    """Test GPU acquisition and release in Worker."""

    @pytest.fixture(autouse=True)
    def reset_singleton(self):
        """Reset singleton before each test."""
        SingletonType._instances = {}
        yield
        SingletonType._instances = {}

    @pytest.fixture
    def mock_gpu_devices(self):
        """Return mock GPU devices."""
        return [
            {"hwaccel": "cuda", "hwaccel_device": "0"},
        ]

    def test_acquire_gpu_when_enabled(self, mock_gpu_devices):
        """Worker should acquire GPU when GPU is enabled."""
        from unmanic.libs.workers import Worker

        with patch("unmanic.libs.workers.UnmanicLogging") as mock_logging, patch(
            "unmanic.libs.gpu_manager.HardwareAccelerationHandle"
        ) as mock_hw, patch("unmanic.libs.workers.UnmanicSettings") as mock_settings, patch(
            "unmanic.libs.workers.get_gpu_manager"
        ) as mock_get_manager:
            mock_logging.get_logger.return_value = MagicMock()
            mock_hw.return_value.get_hwaccel_devices.return_value = mock_gpu_devices

            # Setup settings
            settings_instance = MagicMock()
            settings_instance.gpu_enabled = True
            settings_instance.max_workers_per_gpu = 2
            settings_instance.gpu_assignment_strategy = "round_robin"
            mock_settings.return_value = settings_instance

            # Setup GPU manager
            mock_gpu = GPUDevice(
                device_id="cuda:0",
                gpu_type=GPUType.CUDA,
                hwaccel_device="0",
                display_name="NVIDIA GPU 0",
            )
            mock_manager = MagicMock()
            mock_manager.allocate.return_value = mock_gpu
            mock_get_manager.return_value = mock_manager

            pending_q = queue.Queue()
            complete_q = queue.Queue()
            event = threading.Event()

            worker = Worker(
                thread_id=0,
                name="W0",
                worker_group_id=1,
                pending_queue=pending_q,
                complete_queue=complete_q,
                event=event,
            )

            # Call private acquire method
            worker._Worker__acquire_gpu()

            mock_manager.allocate.assert_called_once_with("W0")
            assert worker.current_gpu == mock_gpu

    def test_acquire_gpu_when_disabled(self, mock_gpu_devices):
        """Worker should not acquire GPU when GPU is disabled."""
        from unmanic.libs.workers import Worker

        with patch("unmanic.libs.workers.UnmanicLogging") as mock_logging, patch(
            "unmanic.libs.gpu_manager.HardwareAccelerationHandle"
        ) as mock_hw, patch("unmanic.libs.workers.UnmanicSettings") as mock_settings, patch(
            "unmanic.libs.workers.get_gpu_manager"
        ) as mock_get_manager:
            mock_logging.get_logger.return_value = MagicMock()
            mock_hw.return_value.get_hwaccel_devices.return_value = []

            # Setup settings with GPU disabled
            settings_instance = MagicMock()
            settings_instance.gpu_enabled = False
            mock_settings.return_value = settings_instance

            pending_q = queue.Queue()
            complete_q = queue.Queue()
            event = threading.Event()

            worker = Worker(
                thread_id=0,
                name="W0",
                worker_group_id=1,
                pending_queue=pending_q,
                complete_queue=complete_q,
                event=event,
            )

            worker._Worker__acquire_gpu()

            # GPU manager should not be called
            mock_get_manager.return_value.allocate.assert_not_called()
            assert worker.current_gpu is None

    def test_release_gpu(self, mock_gpu_devices):
        """Worker should release GPU when task completes."""
        from unmanic.libs.workers import Worker

        with patch("unmanic.libs.workers.UnmanicLogging") as mock_logging, patch(
            "unmanic.libs.gpu_manager.HardwareAccelerationHandle"
        ) as mock_hw, patch("unmanic.libs.workers.get_gpu_manager") as mock_get_manager:
            mock_logging.get_logger.return_value = MagicMock()
            mock_hw.return_value.get_hwaccel_devices.return_value = []

            mock_manager = MagicMock()
            mock_manager.release.return_value = True
            mock_get_manager.return_value = mock_manager

            pending_q = queue.Queue()
            complete_q = queue.Queue()
            event = threading.Event()

            worker = Worker(
                thread_id=0,
                name="W0",
                worker_group_id=1,
                pending_queue=pending_q,
                complete_queue=complete_q,
                event=event,
            )

            # Set GPU before release
            worker.current_gpu = GPUDevice(
                device_id="cuda:0",
                gpu_type=GPUType.CUDA,
                hwaccel_device="0",
            )

            worker._Worker__release_gpu()

            mock_manager.release.assert_called_once_with("W0")
            assert worker.current_gpu is None

    def test_release_gpu_when_none_allocated(self):
        """Worker should handle release when no GPU is allocated."""
        from unmanic.libs.workers import Worker

        with patch("unmanic.libs.workers.UnmanicLogging") as mock_logging, patch(
            "unmanic.libs.gpu_manager.HardwareAccelerationHandle"
        ) as mock_hw, patch("unmanic.libs.workers.get_gpu_manager") as mock_get_manager:
            mock_logging.get_logger.return_value = MagicMock()
            mock_hw.return_value.get_hwaccel_devices.return_value = []

            pending_q = queue.Queue()
            complete_q = queue.Queue()
            event = threading.Event()

            worker = Worker(
                thread_id=0,
                name="W0",
                worker_group_id=1,
                pending_queue=pending_q,
                complete_queue=complete_q,
                event=event,
            )

            # No GPU allocated
            worker.current_gpu = None

            # Should not raise exception
            worker._Worker__release_gpu()

            # Release should not be called
            mock_get_manager.return_value.release.assert_not_called()


class TestWorkerGPUUnset:
    """Test GPU cleanup when unsetting task."""

    @pytest.fixture(autouse=True)
    def reset_singleton(self):
        """Reset singleton before each test."""
        SingletonType._instances = {}
        yield
        SingletonType._instances = {}

    def test_unset_current_task_clears_gpu(self):
        """Unsetting current task should clear GPU reference."""
        from unmanic.libs.workers import Worker

        with patch("unmanic.libs.workers.UnmanicLogging") as mock_logging, patch(
            "unmanic.libs.gpu_manager.HardwareAccelerationHandle"
        ) as mock_hw:
            mock_logging.get_logger.return_value = MagicMock()
            mock_hw.return_value.get_hwaccel_devices.return_value = []

            pending_q = queue.Queue()
            complete_q = queue.Queue()
            event = threading.Event()

            worker = Worker(
                thread_id=0,
                name="W0",
                worker_group_id=1,
                pending_queue=pending_q,
                complete_queue=complete_q,
                event=event,
            )

            # Set GPU
            worker.current_gpu = GPUDevice(
                device_id="cuda:0",
                gpu_type=GPUType.CUDA,
                hwaccel_device="0",
            )

            worker._Worker__unset_current_task()

            assert worker.current_gpu is None


class TestWorkerGPUStrategyApplication:
    """Test that GPU strategy settings are applied correctly."""

    @pytest.fixture(autouse=True)
    def reset_singleton(self):
        """Reset singleton before each test."""
        SingletonType._instances = {}
        yield
        SingletonType._instances = {}

    def test_round_robin_strategy_applied(self):
        """Round robin strategy should be applied from settings."""
        from unmanic.libs.workers import Worker

        with patch("unmanic.libs.workers.UnmanicLogging") as mock_logging, patch(
            "unmanic.libs.gpu_manager.HardwareAccelerationHandle"
        ) as mock_hw, patch("unmanic.libs.workers.UnmanicSettings") as mock_settings, patch(
            "unmanic.libs.workers.get_gpu_manager"
        ) as mock_get_manager:
            mock_logging.get_logger.return_value = MagicMock()
            mock_hw.return_value.get_hwaccel_devices.return_value = []

            settings_instance = MagicMock()
            settings_instance.gpu_enabled = True
            settings_instance.max_workers_per_gpu = 2
            settings_instance.gpu_assignment_strategy = "round_robin"
            mock_settings.return_value = settings_instance

            mock_manager = MagicMock()
            mock_manager.allocate.return_value = None
            mock_get_manager.return_value = mock_manager

            pending_q = queue.Queue()
            complete_q = queue.Queue()
            event = threading.Event()

            worker = Worker(
                thread_id=0,
                name="W0",
                worker_group_id=1,
                pending_queue=pending_q,
                complete_queue=complete_q,
                event=event,
            )

            worker._Worker__acquire_gpu()

            mock_manager.set_strategy.assert_called_once_with(AllocationStrategy.ROUND_ROBIN)

    def test_least_used_strategy_applied(self):
        """Least used strategy should be applied from settings."""
        from unmanic.libs.workers import Worker

        with patch("unmanic.libs.workers.UnmanicLogging") as mock_logging, patch(
            "unmanic.libs.gpu_manager.HardwareAccelerationHandle"
        ) as mock_hw, patch("unmanic.libs.workers.UnmanicSettings") as mock_settings, patch(
            "unmanic.libs.workers.get_gpu_manager"
        ) as mock_get_manager:
            mock_logging.get_logger.return_value = MagicMock()
            mock_hw.return_value.get_hwaccel_devices.return_value = []

            settings_instance = MagicMock()
            settings_instance.gpu_enabled = True
            settings_instance.max_workers_per_gpu = 3
            settings_instance.gpu_assignment_strategy = "least_used"
            mock_settings.return_value = settings_instance

            mock_manager = MagicMock()
            mock_manager.allocate.return_value = None
            mock_get_manager.return_value = mock_manager

            pending_q = queue.Queue()
            complete_q = queue.Queue()
            event = threading.Event()

            worker = Worker(
                thread_id=0,
                name="W0",
                worker_group_id=1,
                pending_queue=pending_q,
                complete_queue=complete_q,
                event=event,
            )

            worker._Worker__acquire_gpu()

            mock_manager.set_strategy.assert_called_once_with(AllocationStrategy.LEAST_USED)
            mock_manager.set_max_workers_per_gpu.assert_called_once_with(3)

    def test_manual_strategy_applied(self):
        """Manual strategy should be applied from settings."""
        from unmanic.libs.workers import Worker

        with patch("unmanic.libs.workers.UnmanicLogging") as mock_logging, patch(
            "unmanic.libs.gpu_manager.HardwareAccelerationHandle"
        ) as mock_hw, patch("unmanic.libs.workers.UnmanicSettings") as mock_settings, patch(
            "unmanic.libs.workers.get_gpu_manager"
        ) as mock_get_manager:
            mock_logging.get_logger.return_value = MagicMock()
            mock_hw.return_value.get_hwaccel_devices.return_value = []

            settings_instance = MagicMock()
            settings_instance.gpu_enabled = True
            settings_instance.max_workers_per_gpu = 1
            settings_instance.gpu_assignment_strategy = "manual"
            mock_settings.return_value = settings_instance

            mock_manager = MagicMock()
            mock_manager.allocate.return_value = None
            mock_get_manager.return_value = mock_manager

            pending_q = queue.Queue()
            complete_q = queue.Queue()
            event = threading.Event()

            worker = Worker(
                thread_id=0,
                name="W0",
                worker_group_id=1,
                pending_queue=pending_q,
                complete_queue=complete_q,
                event=event,
            )

            worker._Worker__acquire_gpu()

            mock_manager.set_strategy.assert_called_once_with(AllocationStrategy.MANUAL)

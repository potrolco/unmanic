#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Unit tests for unmanic.libs.gpu_manager module.

Tests GPU discovery, allocation, and release for multi-GPU support.
"""

import pytest
from unittest.mock import MagicMock, patch

from unmanic.libs.gpu_manager import (
    GPUType,
    AllocationStrategy,
    GPUDevice,
    GPUAllocation,
    GPUManager,
)
from unmanic.libs.singleton import SingletonType


class TestGPUType:
    """Test GPUType enum."""

    def test_has_cuda_type(self):
        """Should have CUDA type."""
        assert GPUType.CUDA.value == "cuda"

    def test_has_vaapi_type(self):
        """Should have VAAPI type."""
        assert GPUType.VAAPI.value == "vaapi"

    def test_has_unknown_type(self):
        """Should have UNKNOWN type."""
        assert GPUType.UNKNOWN.value == "unknown"


class TestAllocationStrategy:
    """Test AllocationStrategy enum."""

    def test_has_round_robin(self):
        """Should have ROUND_ROBIN strategy."""
        assert AllocationStrategy.ROUND_ROBIN.value == "round_robin"

    def test_has_least_used(self):
        """Should have LEAST_USED strategy."""
        assert AllocationStrategy.LEAST_USED.value == "least_used"

    def test_has_manual(self):
        """Should have MANUAL strategy."""
        assert AllocationStrategy.MANUAL.value == "manual"


class TestGPUDevice:
    """Test GPUDevice dataclass."""

    def test_creates_device_with_defaults(self):
        """Should create device with default values."""
        device = GPUDevice(
            device_id="cuda:0",
            gpu_type=GPUType.CUDA,
            hwaccel_device="0",
        )
        assert device.device_id == "cuda:0"
        assert device.gpu_type == GPUType.CUDA
        assert device.current_workers == 0
        assert device.is_available is True

    def test_to_dict(self):
        """Should convert to dictionary."""
        device = GPUDevice(
            device_id="cuda:0",
            gpu_type=GPUType.CUDA,
            hwaccel_device="0",
            display_name="NVIDIA GPU 0",
            current_workers=1,
        )
        d = device.to_dict()
        assert d["device_id"] == "cuda:0"
        assert d["gpu_type"] == "cuda"
        assert d["current_workers"] == 1


class TestGPUAllocation:
    """Test GPUAllocation dataclass."""

    def test_creates_allocation(self):
        """Should create allocation with timestamp."""
        alloc = GPUAllocation(device_id="cuda:0", worker_id="W0")
        assert alloc.device_id == "cuda:0"
        assert alloc.worker_id == "W0"
        assert alloc.allocated_at > 0

    def test_to_dict(self):
        """Should convert to dictionary."""
        alloc = GPUAllocation(device_id="cuda:0", worker_id="W0")
        d = alloc.to_dict()
        assert d["device_id"] == "cuda:0"
        assert d["worker_id"] == "W0"


class TestGPUManager:
    """Test GPUManager class."""

    @pytest.fixture(autouse=True)
    def reset_singleton(self):
        """Reset singleton before each test."""
        SingletonType._instances = {}
        yield
        SingletonType._instances = {}

    @pytest.fixture
    def mock_devices(self):
        """Return mock GPU devices."""
        return [
            {"hwaccel": "cuda", "hwaccel_device": "0"},
            {"hwaccel": "cuda", "hwaccel_device": "1"},
            {"hwaccel": "vaapi", "hwaccel_device": "/dev/dri/renderD128"},
        ]

    def test_discovers_devices_on_init(self, mock_devices):
        """Should discover devices on initialization."""
        with patch("unmanic.libs.gpu_manager.HardwareAccelerationHandle") as mock_hw:
            mock_hw.return_value.get_hwaccel_devices.return_value = mock_devices

            manager = GPUManager()
            devices = manager.get_devices()

            assert len(devices) == 3

    def test_allocates_gpu_to_worker(self, mock_devices):
        """Should allocate GPU to worker."""
        with patch("unmanic.libs.gpu_manager.HardwareAccelerationHandle") as mock_hw:
            mock_hw.return_value.get_hwaccel_devices.return_value = mock_devices

            manager = GPUManager()
            device = manager.allocate("W0")

            assert device is not None
            assert device.current_workers == 1

    def test_releases_gpu_from_worker(self, mock_devices):
        """Should release GPU from worker."""
        with patch("unmanic.libs.gpu_manager.HardwareAccelerationHandle") as mock_hw:
            mock_hw.return_value.get_hwaccel_devices.return_value = mock_devices

            manager = GPUManager()
            device = manager.allocate("W0")
            initial_id = device.device_id

            released = manager.release("W0")

            assert released is True
            assert manager.get_device(initial_id).current_workers == 0

    def test_respects_max_workers_per_gpu(self, mock_devices):
        """Should respect max workers per GPU limit."""
        with patch("unmanic.libs.gpu_manager.HardwareAccelerationHandle") as mock_hw:
            # Only one GPU
            mock_hw.return_value.get_hwaccel_devices.return_value = [mock_devices[0]]

            manager = GPUManager(max_workers_per_gpu=2)

            # First two allocations succeed
            d1 = manager.allocate("W0")
            d2 = manager.allocate("W1")
            assert d1 is not None
            assert d2 is not None

            # Third allocation fails (limit reached)
            d3 = manager.allocate("W2")
            assert d3 is None

    def test_round_robin_allocation(self, mock_devices):
        """Should use round-robin allocation strategy."""
        with patch("unmanic.libs.gpu_manager.HardwareAccelerationHandle") as mock_hw:
            # Two CUDA GPUs
            mock_hw.return_value.get_hwaccel_devices.return_value = mock_devices[:2]

            manager = GPUManager(strategy=AllocationStrategy.ROUND_ROBIN, max_workers_per_gpu=5)

            d1 = manager.allocate("W0")
            d2 = manager.allocate("W1")
            d3 = manager.allocate("W2")

            # Should alternate between GPUs
            assert d1.device_id != d2.device_id
            assert d1.device_id == d3.device_id

    def test_least_used_allocation(self, mock_devices):
        """Should use least-used allocation strategy."""
        with patch("unmanic.libs.gpu_manager.HardwareAccelerationHandle") as mock_hw:
            mock_hw.return_value.get_hwaccel_devices.return_value = mock_devices[:2]

            manager = GPUManager(strategy=AllocationStrategy.LEAST_USED, max_workers_per_gpu=5)

            # Allocate to first GPU
            d1 = manager.allocate("W0")
            first_id = d1.device_id

            # Next allocation should go to least-used (the other GPU)
            d2 = manager.allocate("W1")
            assert d2.device_id != first_id

    def test_preferred_device_allocation(self, mock_devices):
        """Should honor preferred device if available."""
        with patch("unmanic.libs.gpu_manager.HardwareAccelerationHandle") as mock_hw:
            mock_hw.return_value.get_hwaccel_devices.return_value = mock_devices[:2]

            manager = GPUManager()
            devices = manager.get_devices()

            # Request specific device
            preferred_id = devices[1].device_id
            device = manager.allocate("W0", preferred_device_id=preferred_id)

            assert device.device_id == preferred_id

    def test_returns_existing_allocation(self, mock_devices):
        """Should return existing allocation for same worker."""
        with patch("unmanic.libs.gpu_manager.HardwareAccelerationHandle") as mock_hw:
            mock_hw.return_value.get_hwaccel_devices.return_value = mock_devices

            manager = GPUManager()

            d1 = manager.allocate("W0")
            d2 = manager.allocate("W0")  # Same worker

            assert d1.device_id == d2.device_id
            assert d1.current_workers == 1  # Not incremented twice

    def test_get_status(self, mock_devices):
        """Should return status dictionary."""
        with patch("unmanic.libs.gpu_manager.HardwareAccelerationHandle") as mock_hw:
            mock_hw.return_value.get_hwaccel_devices.return_value = mock_devices

            manager = GPUManager()
            manager.allocate("W0")

            status = manager.get_status()

            assert status["total_devices"] == 3
            assert status["active_allocations"] == 1
            assert "devices" in status
            assert "allocations" in status

    def test_handles_no_gpus(self):
        """Should handle system with no GPUs."""
        with patch("unmanic.libs.gpu_manager.HardwareAccelerationHandle") as mock_hw:
            mock_hw.return_value.get_hwaccel_devices.return_value = []

            manager = GPUManager()
            device = manager.allocate("W0")

            assert device is None
            assert len(manager.get_devices()) == 0

    def test_release_nonexistent_worker(self, mock_devices):
        """Should return False for releasing non-existent worker."""
        with patch("unmanic.libs.gpu_manager.HardwareAccelerationHandle") as mock_hw:
            mock_hw.return_value.get_hwaccel_devices.return_value = mock_devices

            manager = GPUManager()
            released = manager.release("nonexistent")

            assert released is False

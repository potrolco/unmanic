#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    unmanic.gpu_manager.py

    Thread-safe GPU management for multi-GPU transcoding support.

    Handles GPU discovery, allocation, and release for worker processes.
    Supports both NVIDIA CUDA and Intel VAAPI devices.

    Written by:               TARS Modernization (Phase 3)
    Date:                     26 Jan 2026

    Copyright:
           Copyright (C) Josh Sunnex - All Rights Reserved
           (TARS Fork - potrolco/unmanic)

"""

import threading
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional

from unmanic.libs.unffmpeg.hardware_acceleration_handle import HardwareAccelerationHandle
from unmanic.libs.singleton import SingletonType


class GPUType(Enum):
    """GPU hardware acceleration type."""

    CUDA = "cuda"
    VAAPI = "vaapi"
    UNKNOWN = "unknown"


class AllocationStrategy(Enum):
    """Strategy for assigning GPUs to workers."""

    ROUND_ROBIN = "round_robin"
    LEAST_USED = "least_used"
    MANUAL = "manual"


@dataclass
class GPUDevice:
    """Represents a GPU device available for transcoding."""

    device_id: str
    gpu_type: GPUType
    hwaccel_device: str
    display_name: str = ""
    current_workers: int = 0
    total_allocations: int = 0
    is_available: bool = True
    last_allocated: float = 0.0

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "device_id": self.device_id,
            "gpu_type": self.gpu_type.value,
            "hwaccel_device": self.hwaccel_device,
            "display_name": self.display_name,
            "current_workers": self.current_workers,
            "total_allocations": self.total_allocations,
            "is_available": self.is_available,
            "last_allocated": self.last_allocated,
        }


@dataclass
class GPUAllocation:
    """Represents a GPU allocation to a worker."""

    device_id: str
    worker_id: str
    allocated_at: float = field(default_factory=time.time)

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "device_id": self.device_id,
            "worker_id": self.worker_id,
            "allocated_at": self.allocated_at,
        }


class GPUManager(metaclass=SingletonType):
    """
    Thread-safe GPU manager for multi-GPU transcoding.

    Singleton class that manages GPU discovery, allocation, and release.
    Supports multiple allocation strategies and per-GPU worker limits.
    """

    def __init__(
        self,
        max_workers_per_gpu: int = 2,
        strategy: AllocationStrategy = AllocationStrategy.ROUND_ROBIN,
    ):
        """
        Initialize the GPU Manager.

        Args:
            max_workers_per_gpu: Maximum concurrent workers per GPU
            strategy: GPU allocation strategy
        """
        self._lock = threading.RLock()
        self._devices: Dict[str, GPUDevice] = {}
        self._allocations: Dict[str, GPUAllocation] = {}  # worker_id -> allocation
        self._max_workers_per_gpu = max_workers_per_gpu
        self._strategy = strategy
        self._round_robin_index = 0

        # Discover GPUs on initialization
        self.refresh_devices()

    def refresh_devices(self) -> List[GPUDevice]:
        """
        Discover and refresh the list of available GPU devices.

        Returns:
            List of discovered GPU devices
        """
        with self._lock:
            # Use existing hardware acceleration detection
            hw_handle = HardwareAccelerationHandle(None)
            raw_devices = hw_handle.get_hwaccel_devices()

            # Preserve allocation counts for existing devices
            existing_counts = {dev_id: (dev.current_workers, dev.total_allocations) for dev_id, dev in self._devices.items()}

            self._devices.clear()

            for raw_dev in raw_devices:
                hwaccel = raw_dev.get("hwaccel", "unknown")
                hwaccel_device = raw_dev.get("hwaccel_device", "")

                # Generate unique device ID
                device_id = f"{hwaccel}:{hwaccel_device}"

                # Determine GPU type
                if hwaccel == "cuda":
                    gpu_type = GPUType.CUDA
                    display_name = f"NVIDIA GPU {hwaccel_device}"
                elif hwaccel == "vaapi":
                    gpu_type = GPUType.VAAPI
                    display_name = f"VAAPI {hwaccel_device}"
                else:
                    gpu_type = GPUType.UNKNOWN
                    display_name = f"Unknown {hwaccel_device}"

                # Restore counts if device existed
                current_workers, total_allocs = existing_counts.get(device_id, (0, 0))

                device = GPUDevice(
                    device_id=device_id,
                    gpu_type=gpu_type,
                    hwaccel_device=hwaccel_device,
                    display_name=display_name,
                    current_workers=current_workers,
                    total_allocations=total_allocs,
                    is_available=current_workers < self._max_workers_per_gpu,
                )
                self._devices[device_id] = device

            return list(self._devices.values())

    def get_devices(self) -> List[GPUDevice]:
        """
        Get all known GPU devices.

        Returns:
            List of GPU devices
        """
        with self._lock:
            return list(self._devices.values())

    def get_device(self, device_id: str) -> Optional[GPUDevice]:
        """
        Get a specific GPU device by ID.

        Args:
            device_id: The device ID to look up

        Returns:
            GPUDevice if found, None otherwise
        """
        with self._lock:
            return self._devices.get(device_id)

    def get_available_devices(self) -> List[GPUDevice]:
        """
        Get all GPU devices that can accept more workers.

        Returns:
            List of available GPU devices
        """
        with self._lock:
            return [dev for dev in self._devices.values() if dev.current_workers < self._max_workers_per_gpu]

    def allocate(self, worker_id: str, preferred_device_id: Optional[str] = None) -> Optional[GPUDevice]:
        """
        Allocate a GPU to a worker.

        Args:
            worker_id: Unique identifier for the worker
            preferred_device_id: Optional specific device to allocate

        Returns:
            Allocated GPUDevice, or None if no GPU available
        """
        with self._lock:
            # Check if worker already has an allocation
            if worker_id in self._allocations:
                existing = self._allocations[worker_id]
                return self._devices.get(existing.device_id)

            # Try preferred device first
            if preferred_device_id and preferred_device_id in self._devices:
                device = self._devices[preferred_device_id]
                if device.current_workers < self._max_workers_per_gpu:
                    return self._do_allocate(worker_id, device)

            # Get available devices
            available = self.get_available_devices()
            if not available:
                return None

            # Select device based on strategy
            if self._strategy == AllocationStrategy.ROUND_ROBIN:
                device = self._select_round_robin(available)
            elif self._strategy == AllocationStrategy.LEAST_USED:
                device = self._select_least_used(available)
            else:
                # Manual strategy - return first available
                device = available[0]

            return self._do_allocate(worker_id, device)

    def _do_allocate(self, worker_id: str, device: GPUDevice) -> GPUDevice:
        """
        Perform the actual allocation.

        Args:
            worker_id: Worker identifier
            device: GPU device to allocate

        Returns:
            The allocated device
        """
        device.current_workers += 1
        device.total_allocations += 1
        device.last_allocated = time.time()
        device.is_available = device.current_workers < self._max_workers_per_gpu

        allocation = GPUAllocation(
            device_id=device.device_id,
            worker_id=worker_id,
        )
        self._allocations[worker_id] = allocation

        return device

    def _select_round_robin(self, available: List[GPUDevice]) -> GPUDevice:
        """Select next device in round-robin order."""
        self._round_robin_index = self._round_robin_index % len(available)
        device = available[self._round_robin_index]
        self._round_robin_index += 1
        return device

    def _select_least_used(self, available: List[GPUDevice]) -> GPUDevice:
        """Select device with fewest current workers."""
        return min(available, key=lambda d: d.current_workers)

    def release(self, worker_id: str) -> bool:
        """
        Release a GPU allocation for a worker.

        Args:
            worker_id: Worker identifier to release

        Returns:
            True if released, False if no allocation found
        """
        with self._lock:
            if worker_id not in self._allocations:
                return False

            allocation = self._allocations.pop(worker_id)
            device = self._devices.get(allocation.device_id)

            if device:
                device.current_workers = max(0, device.current_workers - 1)
                device.is_available = device.current_workers < self._max_workers_per_gpu

            return True

    def get_worker_allocation(self, worker_id: str) -> Optional[GPUAllocation]:
        """
        Get the current allocation for a worker.

        Args:
            worker_id: Worker identifier

        Returns:
            GPUAllocation if found, None otherwise
        """
        with self._lock:
            return self._allocations.get(worker_id)

    def get_all_allocations(self) -> List[GPUAllocation]:
        """
        Get all current allocations.

        Returns:
            List of all GPU allocations
        """
        with self._lock:
            return list(self._allocations.values())

    def get_status(self) -> dict:
        """
        Get overall GPU manager status.

        Returns:
            Dictionary with status information
        """
        with self._lock:
            return {
                "total_devices": len(self._devices),
                "available_devices": len(self.get_available_devices()),
                "active_allocations": len(self._allocations),
                "max_workers_per_gpu": self._max_workers_per_gpu,
                "strategy": self._strategy.value,
                "devices": [dev.to_dict() for dev in self._devices.values()],
                "allocations": [alloc.to_dict() for alloc in self._allocations.values()],
            }

    def set_max_workers_per_gpu(self, max_workers: int) -> None:
        """
        Update the maximum workers per GPU setting.

        Args:
            max_workers: New maximum workers per GPU
        """
        with self._lock:
            self._max_workers_per_gpu = max(1, max_workers)
            # Update availability flags
            for device in self._devices.values():
                device.is_available = device.current_workers < self._max_workers_per_gpu

    def set_strategy(self, strategy: AllocationStrategy) -> None:
        """
        Update the allocation strategy.

        Args:
            strategy: New allocation strategy
        """
        with self._lock:
            self._strategy = strategy


# Module-level convenience function
def get_gpu_manager() -> GPUManager:
    """
    Get the singleton GPU manager instance.

    Returns:
        The GPUManager singleton
    """
    return GPUManager()

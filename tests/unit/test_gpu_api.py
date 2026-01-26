#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Unit tests for GPU status API endpoint.

Tests the /health/gpu endpoint for GPU manager status (Phase 3).
"""

import asyncio
import pytest
from unittest.mock import MagicMock, patch

from unmanic.libs.gpu_manager import GPUType, GPUDevice, GPUAllocation
from unmanic.libs.singleton import SingletonType


class TestGPUStatusAPI:
    """Test GPU status API endpoint."""

    @pytest.fixture(autouse=True)
    def reset_singleton(self):
        """Reset singleton before each test."""
        SingletonType._instances = {}
        yield
        SingletonType._instances = {}

    @pytest.fixture
    def mock_handler(self):
        """Create a mock API handler."""
        from unmanic.webserver.api_v2.health_api import ApiHealthHandler

        handler = MagicMock(spec=ApiHealthHandler)
        handler.get_body_arguments = MagicMock(return_value={})
        handler.build_response = MagicMock(side_effect=lambda schema, data: data)
        handler.write_success = MagicMock()
        handler.write = MagicMock()
        handler.set_status = MagicMock()
        handler.route = {"call_method": "get_gpu_status"}
        return handler

    def test_get_gpu_status_when_disabled(self):
        """Should return disabled status when GPU is disabled."""
        with patch("unmanic.webserver.api_v2.health_api.UnmanicSettings") as mock_settings, patch(
            "unmanic.libs.gpu_manager.HardwareAccelerationHandle"
        ) as mock_hw:
            mock_hw.return_value.get_hwaccel_devices.return_value = []

            settings_instance = MagicMock()
            settings_instance.gpu_enabled = False
            settings_instance.max_workers_per_gpu = 2
            settings_instance.gpu_assignment_strategy = "round_robin"
            mock_settings.return_value = settings_instance

            from unmanic.webserver.api_v2.health_api import ApiHealthHandler

            handler = MagicMock(spec=ApiHealthHandler)
            handler.build_response = MagicMock(side_effect=lambda schema, data: data)
            handler.write_success = MagicMock()
            handler.route = {"call_method": "get_gpu_status"}

            # Create instance and call method
            api = ApiHealthHandler.__new__(ApiHealthHandler)
            api.build_response = handler.build_response
            api.write_success = handler.write_success
            api.route = handler.route

            # Run the async method
            loop = asyncio.get_event_loop()
            loop.run_until_complete(api.get_gpu_status())

            # Verify response
            handler.write_success.assert_called_once()
            response = handler.build_response.call_args[0][1]
            assert response["enabled"] is False
            assert response["total_devices"] == 0
            assert response["strategy"] == "round_robin"

    def test_get_gpu_status_when_enabled(self):
        """Should return GPU status when GPU is enabled."""
        with patch("unmanic.webserver.api_v2.health_api.UnmanicSettings") as mock_settings, patch(
            "unmanic.webserver.api_v2.health_api.get_gpu_manager"
        ) as mock_get_manager, patch("unmanic.libs.gpu_manager.HardwareAccelerationHandle") as mock_hw:
            mock_hw.return_value.get_hwaccel_devices.return_value = []

            settings_instance = MagicMock()
            settings_instance.gpu_enabled = True
            mock_settings.return_value = settings_instance

            mock_manager = MagicMock()
            mock_manager.get_status.return_value = {
                "total_devices": 2,
                "available_devices": 1,
                "active_allocations": 2,
                "max_workers_per_gpu": 2,
                "strategy": "least_used",
                "devices": [
                    {
                        "device_id": "cuda:0",
                        "gpu_type": "cuda",
                        "hwaccel_device": "0",
                        "display_name": "NVIDIA GPU 0",
                        "current_workers": 2,
                        "total_allocations": 10,
                        "is_available": False,
                    },
                    {
                        "device_id": "cuda:1",
                        "gpu_type": "cuda",
                        "hwaccel_device": "1",
                        "display_name": "NVIDIA GPU 1",
                        "current_workers": 0,
                        "total_allocations": 5,
                        "is_available": True,
                    },
                ],
                "allocations": [
                    {"device_id": "cuda:0", "worker_id": "W0", "allocated_at": 1706288400.0},
                    {"device_id": "cuda:0", "worker_id": "W1", "allocated_at": 1706288401.0},
                ],
            }
            mock_get_manager.return_value = mock_manager

            from unmanic.webserver.api_v2.health_api import ApiHealthHandler

            handler = MagicMock(spec=ApiHealthHandler)
            handler.build_response = MagicMock(side_effect=lambda schema, data: data)
            handler.write_success = MagicMock()
            handler.route = {"call_method": "get_gpu_status"}

            api = ApiHealthHandler.__new__(ApiHealthHandler)
            api.build_response = handler.build_response
            api.write_success = handler.write_success
            api.route = handler.route

            loop = asyncio.get_event_loop()
            loop.run_until_complete(api.get_gpu_status())

            handler.write_success.assert_called_once()
            response = handler.build_response.call_args[0][1]
            assert response["enabled"] is True
            assert response["total_devices"] == 2
            assert response["available_devices"] == 1
            assert response["active_allocations"] == 2
            assert response["strategy"] == "least_used"
            assert len(response["devices"]) == 2
            assert len(response["allocations"]) == 2

    def test_get_gpu_status_no_devices(self):
        """Should return empty device list when no GPUs found."""
        with patch("unmanic.webserver.api_v2.health_api.UnmanicSettings") as mock_settings, patch(
            "unmanic.webserver.api_v2.health_api.get_gpu_manager"
        ) as mock_get_manager, patch("unmanic.libs.gpu_manager.HardwareAccelerationHandle") as mock_hw:
            mock_hw.return_value.get_hwaccel_devices.return_value = []

            settings_instance = MagicMock()
            settings_instance.gpu_enabled = True
            mock_settings.return_value = settings_instance

            mock_manager = MagicMock()
            mock_manager.get_status.return_value = {
                "total_devices": 0,
                "available_devices": 0,
                "active_allocations": 0,
                "max_workers_per_gpu": 2,
                "strategy": "round_robin",
                "devices": [],
                "allocations": [],
            }
            mock_get_manager.return_value = mock_manager

            from unmanic.webserver.api_v2.health_api import ApiHealthHandler

            handler = MagicMock(spec=ApiHealthHandler)
            handler.build_response = MagicMock(side_effect=lambda schema, data: data)
            handler.write_success = MagicMock()
            handler.route = {"call_method": "get_gpu_status"}

            api = ApiHealthHandler.__new__(ApiHealthHandler)
            api.build_response = handler.build_response
            api.write_success = handler.write_success
            api.route = handler.route

            loop = asyncio.get_event_loop()
            loop.run_until_complete(api.get_gpu_status())

            handler.write_success.assert_called_once()
            response = handler.build_response.call_args[0][1]
            assert response["enabled"] is True
            assert response["total_devices"] == 0
            assert len(response["devices"]) == 0


class TestGPUStatusSchemas:
    """Test GPU status schema validation."""

    def test_gpu_device_schema_serialization(self):
        """GPUDeviceSchema should serialize correctly."""
        from unmanic.webserver.api_v2.schema.schemas import GPUDeviceSchema

        schema = GPUDeviceSchema()
        data = {
            "device_id": "cuda:0",
            "gpu_type": "cuda",
            "hwaccel_device": "0",
            "display_name": "NVIDIA GPU 0",
            "current_workers": 1,
            "total_allocations": 10,
            "is_available": True,
        }

        result = schema.load(data)
        assert result["device_id"] == "cuda:0"
        assert result["gpu_type"] == "cuda"
        assert result["is_available"] is True

    def test_gpu_allocation_schema_serialization(self):
        """GPUAllocationSchema should serialize correctly."""
        from unmanic.webserver.api_v2.schema.schemas import GPUAllocationSchema

        schema = GPUAllocationSchema()
        data = {
            "device_id": "cuda:0",
            "worker_id": "W0",
            "allocated_at": 1706288400.0,
        }

        result = schema.load(data)
        assert result["device_id"] == "cuda:0"
        assert result["worker_id"] == "W0"
        assert result["allocated_at"] == 1706288400.0

    def test_gpu_status_schema_serialization(self):
        """GPUStatusSchema should serialize correctly."""
        from unmanic.webserver.api_v2.schema.schemas import GPUStatusSchema

        schema = GPUStatusSchema()
        data = {
            "enabled": True,
            "total_devices": 2,
            "available_devices": 1,
            "active_allocations": 1,
            "max_workers_per_gpu": 2,
            "strategy": "round_robin",
            "devices": [
                {
                    "device_id": "cuda:0",
                    "gpu_type": "cuda",
                    "hwaccel_device": "0",
                    "display_name": "NVIDIA GPU 0",
                    "current_workers": 1,
                    "total_allocations": 10,
                    "is_available": True,
                }
            ],
            "allocations": [
                {
                    "device_id": "cuda:0",
                    "worker_id": "W0",
                    "allocated_at": 1706288400.0,
                }
            ],
        }

        result = schema.load(data)
        assert result["enabled"] is True
        assert result["total_devices"] == 2
        assert len(result["devices"]) == 1
        assert len(result["allocations"]) == 1

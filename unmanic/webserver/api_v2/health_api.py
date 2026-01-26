#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    unmanic.health_api.py

    Written by:               TARS Modernization (Phase 1)
    Date:                     26 Jan 2026

    Health check endpoint for monitoring and observability.
    Returns status of application components for use with:
    - Load balancers
    - Kubernetes probes
    - Monitoring systems (Prometheus, Uptime Kuma, etc.)

    Copyright:
           Copyright (C) Josh Sunnex - All Rights Reserved
           (TARS Fork - potrolco/unmanic)
"""

import os
import time

import tornado.log

from unmanic import config
from unmanic.libs import session
from unmanic.libs.gpu_manager import get_gpu_manager
from unmanic.libs.health_check import check_file_integrity, get_file_checksum
from unmanic.libs.settings import UnmanicSettings
from unmanic.libs.uiserver import UnmanicDataQueues
from unmanic.webserver.api_v2.base_api_handler import BaseApiError, BaseApiHandler
from unmanic.webserver.api_v2.schema.schemas import FileHealthCheckSchema, GPUStatusSchema, HealthCheckSchema


# Track application start time for uptime calculation
_APP_START_TIME = time.time()


class ApiHealthHandler(BaseApiHandler):
    """Health check API handler for monitoring and observability."""

    session = None
    config = None
    params = None
    unmanic_data_queues = None

    routes = [
        {
            "path_pattern": r"/health",
            "supported_methods": ["GET"],
            "call_method": "get_health",
        },
        {
            "path_pattern": r"/health/live",
            "supported_methods": ["GET"],
            "call_method": "get_liveness",
        },
        {
            "path_pattern": r"/health/ready",
            "supported_methods": ["GET"],
            "call_method": "get_readiness",
        },
        {
            "path_pattern": r"/health/file",
            "supported_methods": ["POST"],
            "call_method": "check_file_health",
        },
        {
            "path_pattern": r"/health/gpu",
            "supported_methods": ["GET"],
            "call_method": "get_gpu_status",
        },
    ]

    def initialize(self, **kwargs):
        self.session = session.Session()
        self.params = kwargs.get("params")
        udq = UnmanicDataQueues()
        self.unmanic_data_queues = udq.get_unmanic_data_queues()
        self.config = config.Config()

    async def get_health(self):
        """
        Health - full status
        ---
        description: Returns comprehensive health status of all components.
        responses:
            200:
                description: 'Health check passed'
                content:
                    application/json:
                        schema:
                            HealthCheckSchema
            503:
                description: 'Service unhealthy'
                content:
                    application/json:
                        schema:
                            HealthCheckSchema
        """
        try:
            components = {}
            overall_status = "healthy"

            # Check database
            db_status = self._check_database()
            components["database"] = db_status
            if db_status["status"] != "healthy":
                overall_status = "degraded" if overall_status == "healthy" else overall_status

            # Check config path
            config_status = self._check_config_path()
            components["config"] = config_status
            if config_status["status"] != "healthy":
                overall_status = "degraded" if overall_status == "healthy" else overall_status

            # Check cache path
            cache_status = self._check_cache_path()
            components["cache"] = cache_status
            if cache_status["status"] != "healthy":
                overall_status = "degraded" if overall_status == "healthy" else overall_status

            response = self.build_response(
                HealthCheckSchema(),
                {
                    "status": overall_status,
                    "version": self.config.read_version(),
                    "uptime_seconds": int(time.time() - _APP_START_TIME),
                    "components": components,
                },
            )

            if overall_status == "unhealthy":
                self.set_status(503)

            self.write_success(response)
            return
        except BaseApiError as bae:
            tornado.log.app_log.error("BaseApiError.{}: {}".format(self.route.get("call_method"), str(bae)))
            return
        except Exception as e:
            self.set_status(self.STATUS_ERROR_INTERNAL, reason=str(e))
            self.write_error()

    async def get_liveness(self):
        """
        Health - liveness probe
        ---
        description: Simple liveness check (is the process running?).
                     Use for Kubernetes liveness probes.
        responses:
            200:
                description: 'Process is alive'
            500:
                description: 'Process is not responding'
        """
        try:
            self.write({"status": "alive"})
            return
        except Exception as e:
            self.set_status(self.STATUS_ERROR_INTERNAL, reason=str(e))
            self.write_error()

    async def get_readiness(self):
        """
        Health - readiness probe
        ---
        description: Readiness check (can the service accept traffic?).
                     Use for Kubernetes readiness probes.
        responses:
            200:
                description: 'Service is ready'
            503:
                description: 'Service is not ready'
        """
        try:
            # Check if database is accessible
            db_status = self._check_database()
            if db_status["status"] != "healthy":
                self.set_status(503)
                self.write({"status": "not_ready", "reason": db_status.get("message", "Database unavailable")})
                return

            self.write({"status": "ready"})
            return
        except Exception as e:
            self.set_status(503)
            self.write({"status": "not_ready", "reason": str(e)})

    def _check_database(self):
        """Check database connectivity."""
        try:
            from unmanic.libs.unmodels.lib import Database

            db = Database.get_database()
            if db is None:
                return {"status": "unhealthy", "message": "Database not initialized"}

            # Try a simple query
            db.execute_sql("SELECT 1")
            return {"status": "healthy", "message": "OK"}
        except Exception as e:
            return {"status": "unhealthy", "message": str(e)}

    def _check_config_path(self):
        """Check config directory is accessible."""
        try:
            config_path = self.config.get_config_path()
            if not os.path.exists(config_path):
                return {"status": "unhealthy", "message": f"Config path not found: {config_path}"}
            if not os.access(config_path, os.R_OK | os.W_OK):
                return {"status": "degraded", "message": f"Config path not writable: {config_path}"}
            return {"status": "healthy", "message": "OK"}
        except Exception as e:
            return {"status": "unhealthy", "message": str(e)}

    def _check_cache_path(self):
        """Check cache directory is accessible."""
        try:
            cache_path = self.config.get_cache_path()
            if not os.path.exists(cache_path):
                return {"status": "degraded", "message": f"Cache path not found: {cache_path}"}
            if not os.access(cache_path, os.R_OK | os.W_OK):
                return {"status": "degraded", "message": f"Cache path not writable: {cache_path}"}
            return {"status": "healthy", "message": "OK"}
        except Exception as e:
            return {"status": "degraded", "message": str(e)}

    async def check_file_health(self):
        """
        Health - check video file integrity
        ---
        description: Check the health/integrity of a video file using FFmpeg.
        requestBody:
            required: true
            content:
                application/json:
                    schema:
                        type: object
                        required:
                            - file_path
                        properties:
                            file_path:
                                type: string
                                description: Absolute path to the video file
                            include_checksum:
                                type: boolean
                                description: Include file checksum in response
                                default: false
        responses:
            200:
                description: 'Health check completed'
                content:
                    application/json:
                        schema:
                            FileHealthCheckSchema
            400:
                description: 'Invalid request (missing file_path)'
            404:
                description: 'File not found'
        """
        try:
            # Get request body
            request_body = self.get_body_arguments()
            if not request_body:
                self.set_status(400)
                self.write({"error": "Request body required"})
                return

            file_path = request_body.get("file_path")
            if not file_path:
                self.set_status(400)
                self.write({"error": "file_path is required"})
                return

            # Check if file exists
            if not os.path.exists(file_path):
                self.set_status(404)
                self.write({"error": f"File not found: {file_path}"})
                return

            # Get settings for timeout
            settings = UnmanicSettings()

            # Run health check
            result = check_file_integrity(
                file_path,
                timeout_seconds=settings.health_check_timeout_seconds,
            )

            # Optionally include checksum
            include_checksum = request_body.get("include_checksum", False)
            if include_checksum:
                result.checksum = get_file_checksum(
                    file_path,
                    algorithm=settings.health_check_algorithm,
                )

            response = self.build_response(
                FileHealthCheckSchema(),
                result.to_dict(),
            )
            self.write_success(response)
            return

        except BaseApiError as bae:
            tornado.log.app_log.error("BaseApiError.{}: {}".format(self.route.get("call_method"), str(bae)))
            return
        except Exception as e:
            self.set_status(self.STATUS_ERROR_INTERNAL, reason=str(e))
            self.write_error()

    async def get_gpu_status(self):
        """
        Health - GPU status
        ---
        description: Get GPU manager status including available GPUs and current allocations.
        responses:
            200:
                description: 'GPU status retrieved'
                content:
                    application/json:
                        schema:
                            GPUStatusSchema
            503:
                description: 'GPU manager unavailable'
        """
        try:
            settings = UnmanicSettings()

            if not settings.gpu_enabled:
                response = self.build_response(
                    GPUStatusSchema(),
                    {
                        "enabled": False,
                        "total_devices": 0,
                        "available_devices": 0,
                        "active_allocations": 0,
                        "max_workers_per_gpu": settings.max_workers_per_gpu,
                        "strategy": settings.gpu_assignment_strategy,
                        "devices": [],
                        "allocations": [],
                    },
                )
                self.write_success(response)
                return

            gpu_manager = get_gpu_manager()
            status = gpu_manager.get_status()

            response = self.build_response(
                GPUStatusSchema(),
                {
                    "enabled": True,
                    "total_devices": status["total_devices"],
                    "available_devices": status["available_devices"],
                    "active_allocations": status["active_allocations"],
                    "max_workers_per_gpu": status["max_workers_per_gpu"],
                    "strategy": status["strategy"],
                    "devices": status["devices"],
                    "allocations": status["allocations"],
                },
            )
            self.write_success(response)
            return

        except BaseApiError as bae:
            tornado.log.app_log.error("BaseApiError.{}: {}".format(self.route.get("call_method"), str(bae)))
            return
        except Exception as e:
            self.set_status(self.STATUS_ERROR_INTERNAL, reason=str(e))
            self.write_error()

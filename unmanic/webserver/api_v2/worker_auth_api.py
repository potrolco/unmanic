#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    unmanic.webserver.api_v2.worker_auth_api.py

    API endpoints for distributed worker authentication.

    Written by:               TARS Modernization (Session 152)
    Date:                     26 Jan 2026

    Copyright:
           Copyright (C) Josh Sunnex - All Rights Reserved
           TARS Fork Modifications (C) 2026
"""

from typing import Any, Dict, List, Optional

from unmanic.libs.logs import UnmanicLogging
from unmanic.libs.worker_auth import (
    AuthError,
    TokenExpiredError,
    TokenInvalidError,
    WorkerAuthManager,
    WorkerNotRegisteredError,
    WorkerRole,
    require_worker_auth,
)
from unmanic.webserver.api_v2.base_api_handler import BaseApiHandler, BaseApiError, api_error_handler


class ApiWorkerAuthHandler(BaseApiHandler):
    """API handler for worker authentication endpoints."""

    logger = None
    auth_manager = None

    routes = [
        {
            "path_pattern": r"/workers/register",
            "supported_methods": ["POST"],
            "call_method": "register_worker",
        },
        {
            "path_pattern": r"/workers/token",
            "supported_methods": ["POST"],
            "call_method": "generate_token",
        },
        {
            "path_pattern": r"/workers/token/refresh",
            "supported_methods": ["POST"],
            "call_method": "refresh_token",
        },
        {
            "path_pattern": r"/workers/token/revoke",
            "supported_methods": ["POST"],
            "call_method": "revoke_token",
        },
        {
            "path_pattern": r"/workers/list",
            "supported_methods": ["GET"],
            "call_method": "list_workers",
        },
        {
            "path_pattern": r"/workers/(?P<worker_id>[^/]+)",
            "supported_methods": ["GET", "PUT", "DELETE"],
            "call_method": "worker_detail",
        },
        {
            "path_pattern": r"/workers/verify",
            "supported_methods": ["GET"],
            "call_method": "verify_token",
        },
    ]

    def initialize(self, **kwargs: Any) -> None:
        self.logger = UnmanicLogging.get_logger(name=self.__class__.__name__)
        self.auth_manager = WorkerAuthManager()

    @api_error_handler
    async def register_worker(self) -> None:
        """
        Workers - Register new worker
        ---
        description: Register a new distributed worker and receive a worker ID.
        requestBody:
            required: true
            content:
                application/json:
                    schema:
                        type: object
                        required:
                            - name
                            - hostname
                        properties:
                            name:
                                type: string
                                description: Human-readable worker name
                            hostname:
                                type: string
                                description: Worker's hostname
                            capabilities:
                                type: array
                                items:
                                    type: string
                                description: Worker capabilities (e.g., ["gpu", "hevc"])
        responses:
            200:
                description: Worker registered successfully
                content:
                    application/json:
                        schema:
                            type: object
                            properties:
                                worker_id:
                                    type: string
                                name:
                                    type: string
                                token:
                                    type: string
                                    description: Initial JWT token for authentication
            400:
                description: Bad request
            500:
                description: Internal error
        """
        import json

        try:
            data = json.loads(self.request.body)
        except json.JSONDecodeError:
            self.set_status(self.STATUS_ERROR_EXTERNAL, reason="Invalid JSON body")
            self.write_error()
            return

        name = data.get("name")
        hostname = data.get("hostname")
        capabilities = data.get("capabilities", [])

        if not name or not hostname:
            self.set_status(self.STATUS_ERROR_EXTERNAL, reason="name and hostname are required")
            self.write_error()
            return

        # Register the worker
        worker = self.auth_manager.register_worker(
            name=name,
            hostname=hostname,
            capabilities=set(capabilities) if capabilities else None,
        )

        # Generate initial token
        token = self.auth_manager.generate_token(worker.worker_id)

        response = {
            "success": True,
            "worker_id": worker.worker_id,
            "name": worker.name,
            "token": token,
        }
        self.write_success(response)

    @api_error_handler
    async def generate_token(self) -> None:
        """
        Workers - Generate token
        ---
        description: Generate a new JWT token for an existing worker.
        requestBody:
            required: true
            content:
                application/json:
                    schema:
                        type: object
                        required:
                            - worker_id
                        properties:
                            worker_id:
                                type: string
                                description: Worker ID
                            validity_seconds:
                                type: integer
                                description: Token validity in seconds (default 24h, max 30d)
        responses:
            200:
                description: Token generated successfully
            400:
                description: Bad request
            401:
                description: Worker not registered
            500:
                description: Internal error
        """
        import json

        try:
            data = json.loads(self.request.body)
        except json.JSONDecodeError:
            self.set_status(self.STATUS_ERROR_EXTERNAL, reason="Invalid JSON body")
            self.write_error()
            return

        worker_id = data.get("worker_id")
        validity_seconds = data.get("validity_seconds")

        if not worker_id:
            self.set_status(self.STATUS_ERROR_EXTERNAL, reason="worker_id is required")
            self.write_error()
            return

        try:
            token = self.auth_manager.generate_token(worker_id, validity_seconds)
            response = {
                "success": True,
                "token": token,
            }
            self.write_success(response)
        except WorkerNotRegisteredError as e:
            self.set_status(401, reason=str(e))
            self.write_error()

    @api_error_handler
    async def refresh_token(self) -> None:
        """
        Workers - Refresh token
        ---
        description: Refresh an existing JWT token (requires valid token in Authorization header).
        responses:
            200:
                description: Token refreshed successfully
            401:
                description: Invalid or expired token
            500:
                description: Internal error
        """
        auth_header = self.request.headers.get("Authorization", "")

        if not auth_header.startswith("Bearer "):
            self.set_status(401, reason="Missing or invalid Authorization header")
            self.write_error()
            return

        token = auth_header[7:]

        try:
            payload = self.auth_manager.validate_token(token)
            new_token = self.auth_manager.generate_token(payload.worker_id)
            response = {
                "success": True,
                "token": new_token,
            }
            self.write_success(response)
        except (TokenExpiredError, TokenInvalidError, WorkerNotRegisteredError) as e:
            self.set_status(401, reason=str(e))
            self.write_error()

    @api_error_handler
    async def revoke_token(self) -> None:
        """
        Workers - Revoke token
        ---
        description: Revoke a JWT token.
        requestBody:
            required: true
            content:
                application/json:
                    schema:
                        type: object
                        required:
                            - token
                        properties:
                            token:
                                type: string
                                description: Token to revoke
        responses:
            200:
                description: Token revoked successfully
            400:
                description: Bad request
            500:
                description: Internal error
        """
        import json

        try:
            data = json.loads(self.request.body)
        except json.JSONDecodeError:
            self.set_status(self.STATUS_ERROR_EXTERNAL, reason="Invalid JSON body")
            self.write_error()
            return

        token = data.get("token")

        if not token:
            self.set_status(self.STATUS_ERROR_EXTERNAL, reason="token is required")
            self.write_error()
            return

        self.auth_manager.revoke_token(token)
        self.write_success({"success": True, "message": "Token revoked"})

    @api_error_handler
    async def list_workers(self) -> None:
        """
        Workers - List registered workers
        ---
        description: List all registered workers.
        parameters:
            - name: active_only
              in: query
              schema:
                  type: boolean
              description: Only return active workers
        responses:
            200:
                description: List of registered workers
            500:
                description: Internal error
        """
        active_only = self.get_argument("active_only", "false").lower() == "true"

        workers = self.auth_manager.list_workers(active_only=active_only)
        response = {
            "success": True,
            "workers": [w.to_dict() for w in workers],
            "count": len(workers),
        }
        self.write_success(response)

    @api_error_handler
    async def worker_detail(self, worker_id: str) -> None:
        """
        Workers - Get/Update/Delete worker
        ---
        description: Get, update, or delete a specific worker.
        """
        if self.request.method == "GET":
            await self._get_worker(worker_id)
        elif self.request.method == "PUT":
            await self._update_worker(worker_id)
        elif self.request.method == "DELETE":
            await self._delete_worker(worker_id)

    async def _get_worker(self, worker_id: str) -> None:
        """Get worker details."""
        worker = self.auth_manager.get_worker(worker_id)
        if worker is None:
            self.set_status(404, reason="Worker not found")
            self.write_error()
            return

        response = {
            "success": True,
            "worker": worker.to_dict(),
        }
        self.write_success(response)

    async def _update_worker(self, worker_id: str) -> None:
        """Update worker details."""
        import json

        try:
            data = json.loads(self.request.body)
        except json.JSONDecodeError:
            self.set_status(self.STATUS_ERROR_EXTERNAL, reason="Invalid JSON body")
            self.write_error()
            return

        # Extract update fields
        name = data.get("name")
        capabilities = data.get("capabilities")
        active = data.get("active")
        roles = data.get("roles")

        # Convert roles to enum if provided
        role_set = None
        if roles is not None:
            try:
                role_set = {WorkerRole(r) for r in roles}
            except ValueError as e:
                self.set_status(self.STATUS_ERROR_EXTERNAL, reason=f"Invalid role: {e}")
                self.write_error()
                return

        worker = self.auth_manager.update_worker(
            worker_id=worker_id,
            name=name,
            roles=role_set,
            capabilities=set(capabilities) if capabilities else None,
            active=active,
        )

        if worker is None:
            self.set_status(404, reason="Worker not found")
            self.write_error()
            return

        response = {
            "success": True,
            "worker": worker.to_dict(),
        }
        self.write_success(response)

    async def _delete_worker(self, worker_id: str) -> None:
        """Delete (unregister) a worker."""
        if self.auth_manager.unregister_worker(worker_id):
            self.write_success({"success": True, "message": "Worker unregistered"})
        else:
            self.set_status(404, reason="Worker not found")
            self.write_error()

    @api_error_handler
    async def verify_token(self) -> None:
        """
        Workers - Verify token
        ---
        description: Verify a JWT token is valid (for testing).
        responses:
            200:
                description: Token is valid
            401:
                description: Token is invalid or expired
        """
        auth_header = self.request.headers.get("Authorization", "")

        if not auth_header.startswith("Bearer "):
            self.set_status(401, reason="Missing or invalid Authorization header")
            self.write_error()
            return

        token = auth_header[7:]

        try:
            payload = self.auth_manager.validate_token(token)
            worker = self.auth_manager.get_worker(payload.worker_id)
            response = {
                "success": True,
                "valid": True,
                "worker_id": payload.worker_id,
                "roles": payload.roles,
                "capabilities": payload.capabilities,
                "expires_at": payload.expires_at,
                "worker_name": worker.name if worker else None,
            }
            self.write_success(response)
        except (TokenExpiredError, TokenInvalidError, WorkerNotRegisteredError) as e:
            self.set_status(401, reason=str(e))
            self.write_error()

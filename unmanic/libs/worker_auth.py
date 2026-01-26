#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    unmanic.libs.worker_auth.py

    JWT-based authentication for distributed workers.
    Provides token generation, validation, and worker registration.

    Written by:               TARS Modernization (Session 152)
    Date:                     26 Jan 2026

    Copyright:
           Copyright (C) Josh Sunnex - All Rights Reserved
           TARS Fork Modifications (C) 2026

           Permission is hereby granted, free of charge, to any person obtaining a copy
           of this software and associated documentation files (the "Software"), to deal
           in the Software without restriction, including without limitation the rights
           to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
           copies of the Software, and to permit persons to whom the Software is
           furnished to do so, subject to the following conditions:

           The above copyright notice and this permission notice shall be included in all
           copies or substantial portions of the Software.

           THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
           EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
           MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
           IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
           DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
           OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE
           OR OTHER DEALINGS IN THE SOFTWARE.

"""

import hashlib
import hmac
import json
import os
import secrets
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from functools import wraps
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Set, TypeVar

import tornado.log

from unmanic import config
from unmanic.libs.logs import UnmanicLogging
from unmanic.libs.singleton import SingletonType


class WorkerRole(Enum):
    """Worker permission roles."""

    WORKER = "worker"  # Can process tasks
    ADMIN = "admin"  # Can manage workers
    READONLY = "readonly"  # Can view status only


class AuthError(Exception):
    """Base authentication error."""

    pass


class TokenExpiredError(AuthError):
    """Token has expired."""

    pass


class TokenInvalidError(AuthError):
    """Token is invalid or malformed."""

    pass


class WorkerNotRegisteredError(AuthError):
    """Worker is not registered."""

    pass


class InsufficientPermissionsError(AuthError):
    """Worker lacks required permissions."""

    pass


@dataclass
class WorkerInfo:
    """Information about a registered worker."""

    worker_id: str
    name: str
    hostname: str
    roles: Set[WorkerRole] = field(default_factory=lambda: {WorkerRole.WORKER})
    capabilities: Set[str] = field(default_factory=set)
    registered_at: float = field(default_factory=time.time)
    last_seen: float = field(default_factory=time.time)
    active: bool = True

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "worker_id": self.worker_id,
            "name": self.name,
            "hostname": self.hostname,
            "roles": [r.value for r in self.roles],
            "capabilities": list(self.capabilities),
            "registered_at": self.registered_at,
            "last_seen": self.last_seen,
            "active": self.active,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "WorkerInfo":
        """Create from dictionary."""
        return cls(
            worker_id=data["worker_id"],
            name=data["name"],
            hostname=data["hostname"],
            roles={WorkerRole(r) for r in data.get("roles", ["worker"])},
            capabilities=set(data.get("capabilities", [])),
            registered_at=data.get("registered_at", time.time()),
            last_seen=data.get("last_seen", time.time()),
            active=data.get("active", True),
        )


@dataclass
class TokenPayload:
    """JWT token payload."""

    worker_id: str
    roles: List[str]
    capabilities: List[str]
    issued_at: float
    expires_at: float
    jti: str  # JWT ID for revocation

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON encoding."""
        return {
            "sub": self.worker_id,  # Subject (standard JWT claim)
            "roles": self.roles,
            "capabilities": self.capabilities,
            "iat": self.issued_at,  # Issued at (standard JWT claim)
            "exp": self.expires_at,  # Expiration (standard JWT claim)
            "jti": self.jti,  # JWT ID (standard JWT claim)
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TokenPayload":
        """Create from dictionary."""
        return cls(
            worker_id=data["sub"],
            roles=data.get("roles", []),
            capabilities=data.get("capabilities", []),
            issued_at=data["iat"],
            expires_at=data["exp"],
            jti=data["jti"],
        )


class WorkerAuthManager(metaclass=SingletonType):
    """
    Manages JWT-based authentication for distributed workers.

    Features:
    - HMAC-SHA256 signed JWT tokens
    - Worker registration with roles and capabilities
    - Token revocation via JTI blacklist
    - Automatic secret key generation and persistence
    """

    # Default token validity: 24 hours
    DEFAULT_TOKEN_VALIDITY_SECONDS = 86400

    # Maximum token validity: 30 days
    MAX_TOKEN_VALIDITY_SECONDS = 2592000

    def __init__(self) -> None:
        self.logger = UnmanicLogging.get_logger(name=self.__class__.__name__)
        self._secret_key: Optional[bytes] = None
        self._workers: Dict[str, WorkerInfo] = {}
        self._revoked_tokens: Set[str] = set()
        self._config_dir: Optional[Path] = None

        self._load_secret_key()
        self._load_workers()
        self.logger.info("WorkerAuthManager initialized")

    def _get_config_dir(self) -> Path:
        """Get the configuration directory."""
        if self._config_dir is None:
            settings = config.Config()
            config_path = settings.get_config_path()
            self._config_dir = Path(config_path)
        return self._config_dir

    def _get_secret_key_path(self) -> Path:
        """Get path to the secret key file."""
        return self._get_config_dir() / ".worker_auth_secret"

    def _get_workers_path(self) -> Path:
        """Get path to the workers registry file."""
        return self._get_config_dir() / "registered_workers.json"

    def _load_secret_key(self) -> None:
        """Load or generate the secret key."""
        key_path = self._get_secret_key_path()

        if key_path.exists():
            try:
                with open(key_path, "rb") as f:
                    self._secret_key = f.read()
                self.logger.debug("Loaded existing secret key")
                return
            except OSError as e:
                self.logger.warning("Failed to load secret key: %s", e)

        # Generate new secret key (256 bits)
        self._secret_key = secrets.token_bytes(32)

        try:
            # Write with restrictive permissions
            key_path.parent.mkdir(parents=True, exist_ok=True)
            with open(key_path, "wb") as f:
                f.write(self._secret_key)
            os.chmod(key_path, 0o600)
            self.logger.info("Generated new secret key")
        except OSError as e:
            self.logger.error("Failed to save secret key: %s", e)

    def _load_workers(self) -> None:
        """Load registered workers from disk."""
        workers_path = self._get_workers_path()

        if not workers_path.exists():
            self.logger.debug("No registered workers file found")
            return

        try:
            with open(workers_path, "r") as f:
                data = json.load(f)
                for worker_data in data.get("workers", []):
                    worker = WorkerInfo.from_dict(worker_data)
                    self._workers[worker.worker_id] = worker
                self._revoked_tokens = set(data.get("revoked_tokens", []))
            self.logger.info("Loaded %d registered workers", len(self._workers))
        except (OSError, json.JSONDecodeError) as e:
            self.logger.error("Failed to load workers: %s", e)

    def _save_workers(self) -> None:
        """Save registered workers to disk."""
        workers_path = self._get_workers_path()

        try:
            workers_path.parent.mkdir(parents=True, exist_ok=True)
            data = {
                "workers": [w.to_dict() for w in self._workers.values()],
                "revoked_tokens": list(self._revoked_tokens),
            }
            with open(workers_path, "w") as f:
                json.dump(data, f, indent=2)
            self.logger.debug("Saved %d workers to disk", len(self._workers))
        except OSError as e:
            self.logger.error("Failed to save workers: %s", e)

    def _base64url_encode(self, data: bytes) -> str:
        """URL-safe base64 encoding without padding."""
        import base64

        return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")

    def _base64url_decode(self, data: str) -> bytes:
        """URL-safe base64 decoding with padding restoration."""
        import base64

        padding = 4 - len(data) % 4
        if padding != 4:
            data += "=" * padding
        return base64.urlsafe_b64decode(data)

    def _create_signature(self, message: str) -> str:
        """Create HMAC-SHA256 signature."""
        if self._secret_key is None:
            raise AuthError("Secret key not initialized")

        signature = hmac.new(self._secret_key, message.encode("utf-8"), hashlib.sha256).digest()
        return self._base64url_encode(signature)

    def _verify_signature(self, message: str, signature: str) -> bool:
        """Verify HMAC-SHA256 signature."""
        expected_signature = self._create_signature(message)
        return hmac.compare_digest(signature, expected_signature)

    def register_worker(
        self,
        name: str,
        hostname: str,
        roles: Optional[Set[WorkerRole]] = None,
        capabilities: Optional[Set[str]] = None,
    ) -> WorkerInfo:
        """
        Register a new worker.

        Args:
            name: Human-readable worker name
            hostname: Worker's hostname
            roles: Set of worker roles (default: {WorkerRole.WORKER})
            capabilities: Set of capabilities (e.g., {"gpu", "hevc"})

        Returns:
            WorkerInfo with generated worker_id
        """
        # Generate unique worker ID
        worker_id = secrets.token_urlsafe(16)

        worker = WorkerInfo(
            worker_id=worker_id,
            name=name,
            hostname=hostname,
            roles=roles or {WorkerRole.WORKER},
            capabilities=capabilities or set(),
        )

        self._workers[worker_id] = worker
        self._save_workers()

        self.logger.info("Registered worker: %s (%s)", name, worker_id[:8])
        return worker

    def unregister_worker(self, worker_id: str) -> bool:
        """
        Unregister a worker.

        Args:
            worker_id: Worker ID to unregister

        Returns:
            True if worker was unregistered
        """
        if worker_id not in self._workers:
            return False

        worker = self._workers.pop(worker_id)
        self._save_workers()

        self.logger.info("Unregistered worker: %s (%s)", worker.name, worker_id[:8])
        return True

    def get_worker(self, worker_id: str) -> Optional[WorkerInfo]:
        """Get worker info by ID."""
        worker = self._workers.get(worker_id)
        if worker:
            worker.last_seen = time.time()
        return worker

    def list_workers(self, active_only: bool = False) -> List[WorkerInfo]:
        """
        List all registered workers.

        Args:
            active_only: Only return active workers

        Returns:
            List of WorkerInfo objects
        """
        workers = list(self._workers.values())
        if active_only:
            workers = [w for w in workers if w.active]
        return workers

    def update_worker(
        self,
        worker_id: str,
        name: Optional[str] = None,
        roles: Optional[Set[WorkerRole]] = None,
        capabilities: Optional[Set[str]] = None,
        active: Optional[bool] = None,
    ) -> Optional[WorkerInfo]:
        """
        Update worker information.

        Args:
            worker_id: Worker ID to update
            name: New name (optional)
            roles: New roles (optional)
            capabilities: New capabilities (optional)
            active: Active status (optional)

        Returns:
            Updated WorkerInfo or None if not found
        """
        worker = self._workers.get(worker_id)
        if worker is None:
            return None

        if name is not None:
            worker.name = name
        if roles is not None:
            worker.roles = roles
        if capabilities is not None:
            worker.capabilities = capabilities
        if active is not None:
            worker.active = active

        self._save_workers()
        return worker

    def generate_token(
        self,
        worker_id: str,
        validity_seconds: Optional[int] = None,
    ) -> str:
        """
        Generate a JWT token for a worker.

        Args:
            worker_id: Worker ID to generate token for
            validity_seconds: Token validity in seconds (default: 24 hours)

        Returns:
            JWT token string

        Raises:
            WorkerNotRegisteredError: If worker is not registered
        """
        worker = self._workers.get(worker_id)
        if worker is None:
            raise WorkerNotRegisteredError(f"Worker not registered: {worker_id}")

        if not worker.active:
            raise WorkerNotRegisteredError(f"Worker is inactive: {worker_id}")

        # Determine token validity
        if validity_seconds is None:
            validity_seconds = self.DEFAULT_TOKEN_VALIDITY_SECONDS
        validity_seconds = min(validity_seconds, self.MAX_TOKEN_VALIDITY_SECONDS)

        now = time.time()
        payload = TokenPayload(
            worker_id=worker_id,
            roles=[r.value for r in worker.roles],
            capabilities=list(worker.capabilities),
            issued_at=now,
            expires_at=now + validity_seconds,
            jti=secrets.token_urlsafe(16),
        )

        # Create JWT: header.payload.signature
        header = {"alg": "HS256", "typ": "JWT"}
        header_b64 = self._base64url_encode(json.dumps(header, separators=(",", ":")).encode("utf-8"))
        payload_b64 = self._base64url_encode(json.dumps(payload.to_dict(), separators=(",", ":")).encode("utf-8"))

        message = f"{header_b64}.{payload_b64}"
        signature = self._create_signature(message)

        token = f"{message}.{signature}"
        self.logger.debug("Generated token for worker: %s", worker_id[:8])
        return token

    def validate_token(self, token: str) -> TokenPayload:
        """
        Validate a JWT token.

        Args:
            token: JWT token string

        Returns:
            TokenPayload if valid

        Raises:
            TokenInvalidError: If token is malformed or signature invalid
            TokenExpiredError: If token has expired
            WorkerNotRegisteredError: If worker is not registered
        """
        # Split token
        parts = token.split(".")
        if len(parts) != 3:
            raise TokenInvalidError("Invalid token format")

        header_b64, payload_b64, signature = parts

        # Verify signature
        message = f"{header_b64}.{payload_b64}"
        if not self._verify_signature(message, signature):
            raise TokenInvalidError("Invalid token signature")

        # Decode payload
        try:
            payload_json = self._base64url_decode(payload_b64)
            payload_data = json.loads(payload_json)
            payload = TokenPayload.from_dict(payload_data)
        except (json.JSONDecodeError, KeyError) as e:
            raise TokenInvalidError(f"Invalid token payload: {e}")

        # Check if token is revoked
        if payload.jti in self._revoked_tokens:
            raise TokenInvalidError("Token has been revoked")

        # Check expiration
        if time.time() > payload.expires_at:
            raise TokenExpiredError("Token has expired")

        # Verify worker is still registered
        worker = self._workers.get(payload.worker_id)
        if worker is None:
            raise WorkerNotRegisteredError(f"Worker not registered: {payload.worker_id}")

        if not worker.active:
            raise WorkerNotRegisteredError(f"Worker is inactive: {payload.worker_id}")

        # Update last seen
        worker.last_seen = time.time()

        return payload

    def revoke_token(self, token: str) -> bool:
        """
        Revoke a token by its JTI.

        Args:
            token: JWT token to revoke

        Returns:
            True if token was revoked
        """
        try:
            payload = self.validate_token(token)
            self._revoked_tokens.add(payload.jti)
            self._save_workers()
            self.logger.info("Revoked token: %s", payload.jti[:8])
            return True
        except AuthError:
            return False

    def revoke_all_tokens_for_worker(self, worker_id: str) -> None:
        """
        Revoke all tokens for a worker by regenerating the worker ID.

        Note: This is a soft revoke - existing tokens will fail validation
        because the worker won't be found after re-registration.
        """
        worker = self._workers.get(worker_id)
        if worker is None:
            return

        # Deactivate the worker
        worker.active = False
        self._save_workers()
        self.logger.info("Deactivated all tokens for worker: %s", worker_id[:8])

    def cleanup_expired_tokens(self) -> int:
        """
        Clean up expired revoked tokens from the blacklist.

        Returns:
            Number of tokens cleaned up
        """
        # We can't determine expiration from JTI alone, so we limit
        # the blacklist size instead
        max_blacklist_size = 10000
        if len(self._revoked_tokens) > max_blacklist_size:
            # Remove oldest entries (arbitrary - FIFO-ish)
            to_remove = len(self._revoked_tokens) - max_blacklist_size
            for _ in range(to_remove):
                self._revoked_tokens.pop()
            self._save_workers()
            return to_remove
        return 0


# Decorator for protecting API endpoints
F = TypeVar("F", bound=Callable[..., Any])


def require_worker_auth(required_roles: Optional[List[WorkerRole]] = None) -> Callable[[F], F]:
    """
    Decorator to require JWT authentication for an API handler method.

    Args:
        required_roles: List of roles, any of which grants access

    Usage:
        @require_worker_auth([WorkerRole.WORKER, WorkerRole.ADMIN])
        async def protected_endpoint(self):
            # self.worker_payload contains the validated token payload
            pass
    """

    def decorator(func: F) -> F:
        @wraps(func)
        async def wrapper(self: Any, *args: Any, **kwargs: Any) -> Any:
            # Extract token from Authorization header
            auth_header = self.request.headers.get("Authorization", "")

            if not auth_header.startswith("Bearer "):
                self.set_status(401, reason="Missing or invalid Authorization header")
                self.write_error()
                return

            token = auth_header[7:]  # Remove "Bearer " prefix

            try:
                auth_manager = WorkerAuthManager()
                payload = auth_manager.validate_token(token)

                # Check roles if required
                if required_roles:
                    worker_roles = {WorkerRole(r) for r in payload.roles}
                    if not worker_roles.intersection(set(required_roles)):
                        raise InsufficientPermissionsError("Insufficient permissions")

                # Store payload on handler for use in the method
                self.worker_payload = payload
                return await func(self, *args, **kwargs)

            except TokenExpiredError:
                self.set_status(401, reason="Token expired")
                self.write_error()
                return
            except TokenInvalidError as e:
                self.set_status(401, reason=str(e))
                self.write_error()
                return
            except WorkerNotRegisteredError as e:
                self.set_status(401, reason=str(e))
                self.write_error()
                return
            except InsufficientPermissionsError:
                self.set_status(403, reason="Insufficient permissions")
                self.write_error()
                return
            except Exception as e:
                tornado.log.app_log.error("Auth error: %s", e, exc_info=True)
                self.set_status(500, reason="Authentication error")
                self.write_error()
                return

        return wrapper  # type: ignore

    return decorator

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unit tests for the WorkerAuthManager in unmanic.libs.worker_auth.

Tests JWT token generation, validation, and worker management.
"""

import json
import time
import unittest
from unittest.mock import MagicMock, patch, mock_open


class TestWorkerRole(unittest.TestCase):
    """Tests for WorkerRole enum."""

    def test_role_values(self):
        """Test role enum values."""
        from unmanic.libs.worker_auth import WorkerRole

        self.assertEqual(WorkerRole.WORKER.value, "worker")
        self.assertEqual(WorkerRole.ADMIN.value, "admin")
        self.assertEqual(WorkerRole.READONLY.value, "readonly")


class TestWorkerInfo(unittest.TestCase):
    """Tests for WorkerInfo dataclass."""

    def test_to_dict(self):
        """Test WorkerInfo.to_dict serialization."""
        from unmanic.libs.worker_auth import WorkerInfo, WorkerRole

        worker = WorkerInfo(
            worker_id="test-id",
            name="Test Worker",
            hostname="test-host",
            roles={WorkerRole.WORKER},
            capabilities={"gpu", "hevc"},
        )

        result = worker.to_dict()

        self.assertEqual(result["worker_id"], "test-id")
        self.assertEqual(result["name"], "Test Worker")
        self.assertEqual(result["hostname"], "test-host")
        self.assertEqual(result["roles"], ["worker"])
        self.assertIn("gpu", result["capabilities"])
        self.assertIn("hevc", result["capabilities"])

    def test_from_dict(self):
        """Test WorkerInfo.from_dict deserialization."""
        from unmanic.libs.worker_auth import WorkerInfo, WorkerRole

        data = {
            "worker_id": "test-id",
            "name": "Test Worker",
            "hostname": "test-host",
            "roles": ["worker", "admin"],
            "capabilities": ["gpu"],
            "registered_at": 1234567890,
            "last_seen": 1234567891,
            "active": True,
        }

        worker = WorkerInfo.from_dict(data)

        self.assertEqual(worker.worker_id, "test-id")
        self.assertEqual(worker.name, "Test Worker")
        self.assertEqual(worker.roles, {WorkerRole.WORKER, WorkerRole.ADMIN})
        self.assertEqual(worker.capabilities, {"gpu"})


class TestTokenPayload(unittest.TestCase):
    """Tests for TokenPayload dataclass."""

    def test_to_dict(self):
        """Test TokenPayload.to_dict serialization."""
        from unmanic.libs.worker_auth import TokenPayload

        payload = TokenPayload(
            worker_id="worker-123",
            roles=["worker"],
            capabilities=["gpu"],
            issued_at=1000.0,
            expires_at=2000.0,
            jti="token-id",
        )

        result = payload.to_dict()

        self.assertEqual(result["sub"], "worker-123")
        self.assertEqual(result["roles"], ["worker"])
        self.assertEqual(result["iat"], 1000.0)
        self.assertEqual(result["exp"], 2000.0)
        self.assertEqual(result["jti"], "token-id")

    def test_from_dict(self):
        """Test TokenPayload.from_dict deserialization."""
        from unmanic.libs.worker_auth import TokenPayload

        data = {
            "sub": "worker-123",
            "roles": ["admin"],
            "capabilities": ["hevc"],
            "iat": 1000.0,
            "exp": 2000.0,
            "jti": "token-id",
        }

        payload = TokenPayload.from_dict(data)

        self.assertEqual(payload.worker_id, "worker-123")
        self.assertEqual(payload.roles, ["admin"])
        self.assertEqual(payload.expires_at, 2000.0)


class TestWorkerAuthManagerInit(unittest.TestCase):
    """Tests for WorkerAuthManager initialization."""

    @patch("unmanic.libs.worker_auth.UnmanicLogging")
    @patch("unmanic.libs.worker_auth.config.Config")
    @patch("builtins.open", mock_open())
    @patch("os.chmod")
    @patch("pathlib.Path.exists")
    @patch("pathlib.Path.mkdir")
    def test_init_generates_secret_key(self, mock_mkdir, mock_exists, mock_chmod, mock_config, mock_logging):
        """Test initialization generates secret key when none exists."""
        from unmanic.libs.worker_auth import WorkerAuthManager

        mock_logging.get_logger.return_value = MagicMock()
        mock_config_instance = MagicMock()
        mock_config_instance.get_config_path.return_value = "/tmp/test_config"
        mock_config.return_value = mock_config_instance
        mock_exists.return_value = False

        # Clear singleton
        WorkerAuthManager._instances = {}

        manager = WorkerAuthManager()

        self.assertIsNotNone(manager._secret_key)
        self.assertEqual(len(manager._secret_key), 32)


class TestWorkerAuthManagerBase64(unittest.TestCase):
    """Tests for base64 encoding/decoding."""

    @patch("unmanic.libs.worker_auth.UnmanicLogging")
    @patch("unmanic.libs.worker_auth.config.Config")
    @patch("builtins.open", mock_open())
    @patch("os.chmod")
    @patch("pathlib.Path.exists")
    @patch("pathlib.Path.mkdir")
    def test_base64url_roundtrip(self, mock_mkdir, mock_exists, mock_chmod, mock_config, mock_logging):
        """Test base64url encoding/decoding roundtrip."""
        from unmanic.libs.worker_auth import WorkerAuthManager

        mock_logging.get_logger.return_value = MagicMock()
        mock_config_instance = MagicMock()
        mock_config_instance.get_config_path.return_value = "/tmp/test_config"
        mock_config.return_value = mock_config_instance
        mock_exists.return_value = False

        WorkerAuthManager._instances = {}
        manager = WorkerAuthManager()

        test_data = b"Hello, World! This is a test."
        encoded = manager._base64url_encode(test_data)
        decoded = manager._base64url_decode(encoded)

        self.assertEqual(decoded, test_data)

    @patch("unmanic.libs.worker_auth.UnmanicLogging")
    @patch("unmanic.libs.worker_auth.config.Config")
    @patch("builtins.open", mock_open())
    @patch("os.chmod")
    @patch("pathlib.Path.exists")
    @patch("pathlib.Path.mkdir")
    def test_base64url_no_padding(self, mock_mkdir, mock_exists, mock_chmod, mock_config, mock_logging):
        """Test base64url encoding produces no padding."""
        from unmanic.libs.worker_auth import WorkerAuthManager

        mock_logging.get_logger.return_value = MagicMock()
        mock_config_instance = MagicMock()
        mock_config_instance.get_config_path.return_value = "/tmp/test_config"
        mock_config.return_value = mock_config_instance
        mock_exists.return_value = False

        WorkerAuthManager._instances = {}
        manager = WorkerAuthManager()

        test_data = b"test"
        encoded = manager._base64url_encode(test_data)

        self.assertNotIn("=", encoded)


class TestWorkerAuthManagerSignature(unittest.TestCase):
    """Tests for signature creation and verification."""

    @patch("unmanic.libs.worker_auth.UnmanicLogging")
    @patch("unmanic.libs.worker_auth.config.Config")
    @patch("builtins.open", mock_open())
    @patch("os.chmod")
    @patch("pathlib.Path.exists")
    @patch("pathlib.Path.mkdir")
    def test_signature_verification(self, mock_mkdir, mock_exists, mock_chmod, mock_config, mock_logging):
        """Test signature creation and verification."""
        from unmanic.libs.worker_auth import WorkerAuthManager

        mock_logging.get_logger.return_value = MagicMock()
        mock_config_instance = MagicMock()
        mock_config_instance.get_config_path.return_value = "/tmp/test_config"
        mock_config.return_value = mock_config_instance
        mock_exists.return_value = False

        WorkerAuthManager._instances = {}
        manager = WorkerAuthManager()

        message = "test message"
        signature = manager._create_signature(message)

        self.assertTrue(manager._verify_signature(message, signature))

    @patch("unmanic.libs.worker_auth.UnmanicLogging")
    @patch("unmanic.libs.worker_auth.config.Config")
    @patch("builtins.open", mock_open())
    @patch("os.chmod")
    @patch("pathlib.Path.exists")
    @patch("pathlib.Path.mkdir")
    def test_signature_tamper_detection(self, mock_mkdir, mock_exists, mock_chmod, mock_config, mock_logging):
        """Test signature detects tampering."""
        from unmanic.libs.worker_auth import WorkerAuthManager

        mock_logging.get_logger.return_value = MagicMock()
        mock_config_instance = MagicMock()
        mock_config_instance.get_config_path.return_value = "/tmp/test_config"
        mock_config.return_value = mock_config_instance
        mock_exists.return_value = False

        WorkerAuthManager._instances = {}
        manager = WorkerAuthManager()

        message = "test message"
        signature = manager._create_signature(message)

        # Tampered message should fail
        self.assertFalse(manager._verify_signature("tampered message", signature))


class TestWorkerRegistration(unittest.TestCase):
    """Tests for worker registration."""

    @patch("unmanic.libs.worker_auth.UnmanicLogging")
    @patch("unmanic.libs.worker_auth.config.Config")
    @patch("builtins.open", mock_open())
    @patch("os.chmod")
    @patch("pathlib.Path.exists")
    @patch("pathlib.Path.mkdir")
    def test_register_worker(self, mock_mkdir, mock_exists, mock_chmod, mock_config, mock_logging):
        """Test registering a new worker."""
        from unmanic.libs.worker_auth import WorkerAuthManager, WorkerRole

        mock_logging.get_logger.return_value = MagicMock()
        mock_config_instance = MagicMock()
        mock_config_instance.get_config_path.return_value = "/tmp/test_config"
        mock_config.return_value = mock_config_instance
        mock_exists.return_value = False

        WorkerAuthManager._instances = {}
        manager = WorkerAuthManager()

        worker = manager.register_worker(
            name="Test Worker",
            hostname="test-host",
            capabilities={"gpu", "hevc"},
        )

        self.assertIsNotNone(worker.worker_id)
        self.assertEqual(worker.name, "Test Worker")
        self.assertEqual(worker.hostname, "test-host")
        self.assertEqual(worker.capabilities, {"gpu", "hevc"})
        self.assertEqual(worker.roles, {WorkerRole.WORKER})

    @patch("unmanic.libs.worker_auth.UnmanicLogging")
    @patch("unmanic.libs.worker_auth.config.Config")
    @patch("builtins.open", mock_open())
    @patch("os.chmod")
    @patch("pathlib.Path.exists")
    @patch("pathlib.Path.mkdir")
    def test_unregister_worker(self, mock_mkdir, mock_exists, mock_chmod, mock_config, mock_logging):
        """Test unregistering a worker."""
        from unmanic.libs.worker_auth import WorkerAuthManager

        mock_logging.get_logger.return_value = MagicMock()
        mock_config_instance = MagicMock()
        mock_config_instance.get_config_path.return_value = "/tmp/test_config"
        mock_config.return_value = mock_config_instance
        mock_exists.return_value = False

        WorkerAuthManager._instances = {}
        manager = WorkerAuthManager()

        worker = manager.register_worker(name="Test", hostname="host")
        worker_id = worker.worker_id

        result = manager.unregister_worker(worker_id)

        self.assertTrue(result)
        self.assertIsNone(manager.get_worker(worker_id))

    @patch("unmanic.libs.worker_auth.UnmanicLogging")
    @patch("unmanic.libs.worker_auth.config.Config")
    @patch("builtins.open", mock_open())
    @patch("os.chmod")
    @patch("pathlib.Path.exists")
    @patch("pathlib.Path.mkdir")
    def test_unregister_nonexistent_worker(self, mock_mkdir, mock_exists, mock_chmod, mock_config, mock_logging):
        """Test unregistering a non-existent worker returns False."""
        from unmanic.libs.worker_auth import WorkerAuthManager

        mock_logging.get_logger.return_value = MagicMock()
        mock_config_instance = MagicMock()
        mock_config_instance.get_config_path.return_value = "/tmp/test_config"
        mock_config.return_value = mock_config_instance
        mock_exists.return_value = False

        WorkerAuthManager._instances = {}
        manager = WorkerAuthManager()

        result = manager.unregister_worker("nonexistent")

        self.assertFalse(result)


class TestWorkerUpdate(unittest.TestCase):
    """Tests for worker updates."""

    @patch("unmanic.libs.worker_auth.UnmanicLogging")
    @patch("unmanic.libs.worker_auth.config.Config")
    @patch("builtins.open", mock_open())
    @patch("os.chmod")
    @patch("pathlib.Path.exists")
    @patch("pathlib.Path.mkdir")
    def test_update_worker_name(self, mock_mkdir, mock_exists, mock_chmod, mock_config, mock_logging):
        """Test updating worker name."""
        from unmanic.libs.worker_auth import WorkerAuthManager

        mock_logging.get_logger.return_value = MagicMock()
        mock_config_instance = MagicMock()
        mock_config_instance.get_config_path.return_value = "/tmp/test_config"
        mock_config.return_value = mock_config_instance
        mock_exists.return_value = False

        WorkerAuthManager._instances = {}
        manager = WorkerAuthManager()

        worker = manager.register_worker(name="Old Name", hostname="host")
        updated = manager.update_worker(worker.worker_id, name="New Name")

        self.assertEqual(updated.name, "New Name")

    @patch("unmanic.libs.worker_auth.UnmanicLogging")
    @patch("unmanic.libs.worker_auth.config.Config")
    @patch("builtins.open", mock_open())
    @patch("os.chmod")
    @patch("pathlib.Path.exists")
    @patch("pathlib.Path.mkdir")
    def test_update_worker_active(self, mock_mkdir, mock_exists, mock_chmod, mock_config, mock_logging):
        """Test deactivating a worker."""
        from unmanic.libs.worker_auth import WorkerAuthManager

        mock_logging.get_logger.return_value = MagicMock()
        mock_config_instance = MagicMock()
        mock_config_instance.get_config_path.return_value = "/tmp/test_config"
        mock_config.return_value = mock_config_instance
        mock_exists.return_value = False

        WorkerAuthManager._instances = {}
        manager = WorkerAuthManager()

        worker = manager.register_worker(name="Worker", hostname="host")
        updated = manager.update_worker(worker.worker_id, active=False)

        self.assertFalse(updated.active)


class TestTokenGeneration(unittest.TestCase):
    """Tests for JWT token generation."""

    @patch("unmanic.libs.worker_auth.UnmanicLogging")
    @patch("unmanic.libs.worker_auth.config.Config")
    @patch("builtins.open", mock_open())
    @patch("os.chmod")
    @patch("pathlib.Path.exists")
    @patch("pathlib.Path.mkdir")
    def test_generate_token(self, mock_mkdir, mock_exists, mock_chmod, mock_config, mock_logging):
        """Test generating a JWT token."""
        from unmanic.libs.worker_auth import WorkerAuthManager

        mock_logging.get_logger.return_value = MagicMock()
        mock_config_instance = MagicMock()
        mock_config_instance.get_config_path.return_value = "/tmp/test_config"
        mock_config.return_value = mock_config_instance
        mock_exists.return_value = False

        WorkerAuthManager._instances = {}
        manager = WorkerAuthManager()

        worker = manager.register_worker(name="Worker", hostname="host")
        token = manager.generate_token(worker.worker_id)

        # Token should be a valid JWT format (header.payload.signature)
        parts = token.split(".")
        self.assertEqual(len(parts), 3)

    @patch("unmanic.libs.worker_auth.UnmanicLogging")
    @patch("unmanic.libs.worker_auth.config.Config")
    @patch("builtins.open", mock_open())
    @patch("os.chmod")
    @patch("pathlib.Path.exists")
    @patch("pathlib.Path.mkdir")
    def test_generate_token_unregistered_worker(self, mock_mkdir, mock_exists, mock_chmod, mock_config, mock_logging):
        """Test generating token for unregistered worker raises error."""
        from unmanic.libs.worker_auth import WorkerAuthManager, WorkerNotRegisteredError

        mock_logging.get_logger.return_value = MagicMock()
        mock_config_instance = MagicMock()
        mock_config_instance.get_config_path.return_value = "/tmp/test_config"
        mock_config.return_value = mock_config_instance
        mock_exists.return_value = False

        WorkerAuthManager._instances = {}
        manager = WorkerAuthManager()

        with self.assertRaises(WorkerNotRegisteredError):
            manager.generate_token("nonexistent")


class TestTokenValidation(unittest.TestCase):
    """Tests for JWT token validation."""

    @patch("unmanic.libs.worker_auth.UnmanicLogging")
    @patch("unmanic.libs.worker_auth.config.Config")
    @patch("builtins.open", mock_open())
    @patch("os.chmod")
    @patch("pathlib.Path.exists")
    @patch("pathlib.Path.mkdir")
    def test_validate_valid_token(self, mock_mkdir, mock_exists, mock_chmod, mock_config, mock_logging):
        """Test validating a valid token."""
        from unmanic.libs.worker_auth import WorkerAuthManager

        mock_logging.get_logger.return_value = MagicMock()
        mock_config_instance = MagicMock()
        mock_config_instance.get_config_path.return_value = "/tmp/test_config"
        mock_config.return_value = mock_config_instance
        mock_exists.return_value = False

        WorkerAuthManager._instances = {}
        manager = WorkerAuthManager()

        worker = manager.register_worker(name="Worker", hostname="host")
        token = manager.generate_token(worker.worker_id)

        payload = manager.validate_token(token)

        self.assertEqual(payload.worker_id, worker.worker_id)

    @patch("unmanic.libs.worker_auth.UnmanicLogging")
    @patch("unmanic.libs.worker_auth.config.Config")
    @patch("builtins.open", mock_open())
    @patch("os.chmod")
    @patch("pathlib.Path.exists")
    @patch("pathlib.Path.mkdir")
    def test_validate_invalid_format(self, mock_mkdir, mock_exists, mock_chmod, mock_config, mock_logging):
        """Test validating invalid token format raises error."""
        from unmanic.libs.worker_auth import WorkerAuthManager, TokenInvalidError

        mock_logging.get_logger.return_value = MagicMock()
        mock_config_instance = MagicMock()
        mock_config_instance.get_config_path.return_value = "/tmp/test_config"
        mock_config.return_value = mock_config_instance
        mock_exists.return_value = False

        WorkerAuthManager._instances = {}
        manager = WorkerAuthManager()

        with self.assertRaises(TokenInvalidError):
            manager.validate_token("not.a.valid.token.format")

    @patch("unmanic.libs.worker_auth.UnmanicLogging")
    @patch("unmanic.libs.worker_auth.config.Config")
    @patch("builtins.open", mock_open())
    @patch("os.chmod")
    @patch("pathlib.Path.exists")
    @patch("pathlib.Path.mkdir")
    def test_validate_tampered_token(self, mock_mkdir, mock_exists, mock_chmod, mock_config, mock_logging):
        """Test validating tampered token raises error."""
        from unmanic.libs.worker_auth import WorkerAuthManager, TokenInvalidError

        mock_logging.get_logger.return_value = MagicMock()
        mock_config_instance = MagicMock()
        mock_config_instance.get_config_path.return_value = "/tmp/test_config"
        mock_config.return_value = mock_config_instance
        mock_exists.return_value = False

        WorkerAuthManager._instances = {}
        manager = WorkerAuthManager()

        worker = manager.register_worker(name="Worker", hostname="host")
        token = manager.generate_token(worker.worker_id)

        # Tamper with the token
        parts = token.split(".")
        parts[1] = parts[1][:-1] + "X"  # Modify payload
        tampered = ".".join(parts)

        with self.assertRaises(TokenInvalidError):
            manager.validate_token(tampered)

    @patch("unmanic.libs.worker_auth.time.time")
    @patch("unmanic.libs.worker_auth.UnmanicLogging")
    @patch("unmanic.libs.worker_auth.config.Config")
    @patch("builtins.open", mock_open())
    @patch("os.chmod")
    @patch("pathlib.Path.exists")
    @patch("pathlib.Path.mkdir")
    def test_validate_expired_token(self, mock_mkdir, mock_exists, mock_chmod, mock_config, mock_logging, mock_time):
        """Test validating expired token raises error."""
        from unmanic.libs.worker_auth import WorkerAuthManager, TokenExpiredError

        mock_logging.get_logger.return_value = MagicMock()
        mock_config_instance = MagicMock()
        mock_config_instance.get_config_path.return_value = "/tmp/test_config"
        mock_config.return_value = mock_config_instance
        mock_exists.return_value = False

        # Set up time mock - start at t=1000
        mock_time.return_value = 1000

        WorkerAuthManager._instances = {}
        manager = WorkerAuthManager()

        worker = manager.register_worker(name="Worker", hostname="host")
        token = manager.generate_token(worker.worker_id, validity_seconds=10)

        # Fast forward past expiration
        mock_time.return_value = 1020

        with self.assertRaises(TokenExpiredError):
            manager.validate_token(token)


class TestTokenRevocation(unittest.TestCase):
    """Tests for token revocation."""

    @patch("unmanic.libs.worker_auth.UnmanicLogging")
    @patch("unmanic.libs.worker_auth.config.Config")
    @patch("builtins.open", mock_open())
    @patch("os.chmod")
    @patch("pathlib.Path.exists")
    @patch("pathlib.Path.mkdir")
    def test_revoke_token(self, mock_mkdir, mock_exists, mock_chmod, mock_config, mock_logging):
        """Test revoking a token."""
        from unmanic.libs.worker_auth import WorkerAuthManager, TokenInvalidError

        mock_logging.get_logger.return_value = MagicMock()
        mock_config_instance = MagicMock()
        mock_config_instance.get_config_path.return_value = "/tmp/test_config"
        mock_config.return_value = mock_config_instance
        mock_exists.return_value = False

        WorkerAuthManager._instances = {}
        manager = WorkerAuthManager()

        worker = manager.register_worker(name="Worker", hostname="host")
        token = manager.generate_token(worker.worker_id)

        # Revoke the token
        result = manager.revoke_token(token)
        self.assertTrue(result)

        # Token should no longer be valid
        with self.assertRaises(TokenInvalidError):
            manager.validate_token(token)


class TestListWorkers(unittest.TestCase):
    """Tests for listing workers."""

    @patch("unmanic.libs.worker_auth.UnmanicLogging")
    @patch("unmanic.libs.worker_auth.config.Config")
    @patch("builtins.open", mock_open())
    @patch("os.chmod")
    @patch("pathlib.Path.exists")
    @patch("pathlib.Path.mkdir")
    def test_list_all_workers(self, mock_mkdir, mock_exists, mock_chmod, mock_config, mock_logging):
        """Test listing all workers."""
        from unmanic.libs.worker_auth import WorkerAuthManager

        mock_logging.get_logger.return_value = MagicMock()
        mock_config_instance = MagicMock()
        mock_config_instance.get_config_path.return_value = "/tmp/test_config"
        mock_config.return_value = mock_config_instance
        mock_exists.return_value = False

        WorkerAuthManager._instances = {}
        manager = WorkerAuthManager()

        manager.register_worker(name="Worker1", hostname="host1")
        manager.register_worker(name="Worker2", hostname="host2")

        workers = manager.list_workers()

        self.assertEqual(len(workers), 2)

    @patch("unmanic.libs.worker_auth.UnmanicLogging")
    @patch("unmanic.libs.worker_auth.config.Config")
    @patch("builtins.open", mock_open())
    @patch("os.chmod")
    @patch("pathlib.Path.exists")
    @patch("pathlib.Path.mkdir")
    def test_list_active_workers_only(self, mock_mkdir, mock_exists, mock_chmod, mock_config, mock_logging):
        """Test listing only active workers."""
        from unmanic.libs.worker_auth import WorkerAuthManager

        mock_logging.get_logger.return_value = MagicMock()
        mock_config_instance = MagicMock()
        mock_config_instance.get_config_path.return_value = "/tmp/test_config"
        mock_config.return_value = mock_config_instance
        mock_exists.return_value = False

        WorkerAuthManager._instances = {}
        manager = WorkerAuthManager()

        worker1 = manager.register_worker(name="Active", hostname="host1")
        worker2 = manager.register_worker(name="Inactive", hostname="host2")

        manager.update_worker(worker2.worker_id, active=False)

        workers = manager.list_workers(active_only=True)

        self.assertEqual(len(workers), 1)
        self.assertEqual(workers[0].name, "Active")


if __name__ == "__main__":
    unittest.main()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unit tests for the Session class in unmanic.libs.session.

Tests session management functionality with mocked dependencies.
"""

import time
import unittest
from unittest.mock import MagicMock, patch


class TestRemoteApiException(unittest.TestCase):
    """Tests for RemoteApiException class."""

    def test_init_formats_message(self):
        """Test exception message includes status code."""
        from unmanic.libs.session import RemoteApiException

        exc = RemoteApiException("Test error", 404)

        self.assertIn("404", str(exc))
        self.assertIn("Test error", str(exc))
        self.assertIn("Remote API", str(exc))

    def test_init_with_different_codes(self):
        """Test with various HTTP status codes."""
        from unmanic.libs.session import RemoteApiException

        for code in [400, 401, 403, 500, 502]:
            exc = RemoteApiException("Error", code)
            self.assertIn(str(code), str(exc))


class TestSessionInit(unittest.TestCase):
    """Tests for Session initialization."""

    def setUp(self):
        """Clear singleton before each test."""
        from unmanic.libs.singleton import SingletonType
        from unmanic.libs.session import Session

        if Session in SingletonType._instances:
            del SingletonType._instances[Session]

    def tearDown(self):
        """Clear singleton after each test."""
        from unmanic.libs.singleton import SingletonType
        from unmanic.libs.session import Session

        if Session in SingletonType._instances:
            del SingletonType._instances[Session]

    @patch("unmanic.libs.session.UnmanicLogging")
    @patch("unmanic.libs.session.requests.Session")
    def test_init_sets_defaults(self, mock_requests, mock_logging):
        """Test Session initialization sets default values."""
        from unmanic.libs.session import Session

        mock_logging.get_logger.return_value = MagicMock()

        session = Session()

        self.assertEqual(session.timeout, 30)
        self.assertIsNone(session.created)
        self.assertIsNone(session.last_check)
        # TARS defaults
        self.assertEqual(session.level, 100)
        self.assertEqual(session.library_count, 999)
        self.assertEqual(session.link_count, 999)

    @patch("unmanic.libs.session.UnmanicLogging")
    @patch("unmanic.libs.session.requests.Session")
    def test_init_with_dev_api(self, mock_requests, mock_logging):
        """Test Session initialization with dev_api parameter."""
        from unmanic.libs.session import Session

        mock_logging.get_logger.return_value = MagicMock()

        session = Session(dev_api="http://localhost:8000")

        self.assertEqual(session.dev_api, "http://localhost:8000")


class TestSessionGetSiteUrl(unittest.TestCase):
    """Tests for Session.get_site_url method."""

    def setUp(self):
        """Clear singleton before each test."""
        from unmanic.libs.singleton import SingletonType
        from unmanic.libs.session import Session

        if Session in SingletonType._instances:
            del SingletonType._instances[Session]

    def tearDown(self):
        """Clear singleton after each test."""
        from unmanic.libs.singleton import SingletonType
        from unmanic.libs.session import Session

        if Session in SingletonType._instances:
            del SingletonType._instances[Session]

    @patch("unmanic.libs.session.UnmanicLogging")
    @patch("unmanic.libs.session.requests.Session")
    def test_returns_production_url(self, mock_requests, mock_logging):
        """Test returns production URL by default."""
        from unmanic.libs.session import Session

        mock_logging.get_logger.return_value = MagicMock()

        session = Session()
        url = session.get_site_url()

        self.assertEqual(url, "https://api.unmanic.app")

    @patch("unmanic.libs.session.UnmanicLogging")
    @patch("unmanic.libs.session.requests.Session")
    def test_returns_dev_url_when_set(self, mock_requests, mock_logging):
        """Test returns dev URL when dev_api is set."""
        from unmanic.libs.session import Session

        mock_logging.get_logger.return_value = MagicMock()

        session = Session(dev_api="http://dev.local")
        url = session.get_site_url()

        self.assertEqual(url, "http://dev.local")


class TestSessionSetFullApiUrl(unittest.TestCase):
    """Tests for Session.set_full_api_url method."""

    def setUp(self):
        """Clear singleton before each test."""
        from unmanic.libs.singleton import SingletonType
        from unmanic.libs.session import Session

        if Session in SingletonType._instances:
            del SingletonType._instances[Session]

    def tearDown(self):
        """Clear singleton after each test."""
        from unmanic.libs.singleton import SingletonType
        from unmanic.libs.session import Session

        if Session in SingletonType._instances:
            del SingletonType._instances[Session]

    @patch("unmanic.libs.session.UnmanicLogging")
    @patch("unmanic.libs.session.requests.Session")
    def test_builds_correct_url(self, mock_requests, mock_logging):
        """Test builds correct API URL."""
        from unmanic.libs.session import Session

        mock_logging.get_logger.return_value = MagicMock()

        session = Session()
        url = session.set_full_api_url("unmanic-api", 1, "test/endpoint")

        self.assertEqual(url, "https://api.unmanic.app/unmanic-api/v1/test/endpoint")

    @patch("unmanic.libs.session.UnmanicLogging")
    @patch("unmanic.libs.session.requests.Session")
    def test_builds_url_with_version_2(self, mock_requests, mock_logging):
        """Test builds URL with version 2."""
        from unmanic.libs.session import Session

        mock_logging.get_logger.return_value = MagicMock()

        session = Session()
        url = session.set_full_api_url("support-auth-api", 2, "user_auth/login")

        self.assertEqual(url, "https://api.unmanic.app/support-auth-api/v2/user_auth/login")


class TestSessionLoginUrls(unittest.TestCase):
    """Tests for Session login URL methods."""

    def setUp(self):
        """Clear singleton before each test."""
        from unmanic.libs.singleton import SingletonType
        from unmanic.libs.session import Session

        if Session in SingletonType._instances:
            del SingletonType._instances[Session]

    def tearDown(self):
        """Clear singleton after each test."""
        from unmanic.libs.singleton import SingletonType
        from unmanic.libs.session import Session

        if Session in SingletonType._instances:
            del SingletonType._instances[Session]

    @patch("unmanic.libs.session.UnmanicLogging")
    @patch("unmanic.libs.session.requests.Session")
    def test_get_patreon_login_url(self, mock_requests, mock_logging):
        """Test Patreon login URL."""
        from unmanic.libs.session import Session

        mock_logging.get_logger.return_value = MagicMock()

        session = Session()
        url = session.get_patreon_login_url()

        self.assertIn("support-auth-api/v1/login_patreon/login", url)

    @patch("unmanic.libs.session.UnmanicLogging")
    @patch("unmanic.libs.session.requests.Session")
    def test_get_github_login_url(self, mock_requests, mock_logging):
        """Test GitHub login URL."""
        from unmanic.libs.session import Session

        mock_logging.get_logger.return_value = MagicMock()

        session = Session()
        url = session.get_github_login_url()

        self.assertIn("support-auth-api/v1/login_github/login", url)

    @patch("unmanic.libs.session.UnmanicLogging")
    @patch("unmanic.libs.session.requests.Session")
    def test_get_discord_login_url(self, mock_requests, mock_logging):
        """Test Discord login URL."""
        from unmanic.libs.session import Session

        mock_logging.get_logger.return_value = MagicMock()

        session = Session()
        url = session.get_discord_login_url()

        self.assertIn("support-auth-api/v1/login_discord/login", url)

    @patch("unmanic.libs.session.UnmanicLogging")
    @patch("unmanic.libs.session.requests.Session")
    def test_get_sign_out_url(self, mock_requests, mock_logging):
        """Test sign out URL."""
        from unmanic.libs.session import Session

        mock_logging.get_logger.return_value = MagicMock()

        session = Session()
        url = session.get_sign_out_url()

        self.assertIn("unmanic-api/v1/installation_auth/logout", url)


class TestSessionCreatedOlderThanXDays(unittest.TestCase):
    """Tests for Session.__created_older_than_x_days private method."""

    def setUp(self):
        """Clear singleton before each test."""
        from unmanic.libs.singleton import SingletonType
        from unmanic.libs.session import Session

        if Session in SingletonType._instances:
            del SingletonType._instances[Session]

    def tearDown(self):
        """Clear singleton after each test."""
        from unmanic.libs.singleton import SingletonType
        from unmanic.libs.session import Session

        if Session in SingletonType._instances:
            del SingletonType._instances[Session]

    @patch("unmanic.libs.session.UnmanicLogging")
    @patch("unmanic.libs.session.requests.Session")
    def test_returns_false_when_no_created(self, mock_requests, mock_logging):
        """Test returns False when created is None."""
        from unmanic.libs.session import Session

        mock_logging.get_logger.return_value = MagicMock()

        session = Session()
        session.created = None

        # Access private method
        result = session._Session__created_older_than_x_days(1)

        self.assertFalse(result)

    @patch("unmanic.libs.session.UnmanicLogging")
    @patch("unmanic.libs.session.requests.Session")
    def test_returns_false_when_recent(self, mock_requests, mock_logging):
        """Test returns False when session is recent."""
        from unmanic.libs.session import Session

        mock_logging.get_logger.return_value = MagicMock()

        session = Session()
        # Set created to now
        session.created = time.time()

        result = session._Session__created_older_than_x_days(1)

        self.assertFalse(result)

    @patch("unmanic.libs.session.UnmanicLogging")
    @patch("unmanic.libs.session.requests.Session")
    def test_returns_true_when_old(self, mock_requests, mock_logging):
        """Test returns True when session is old."""
        from unmanic.libs.session import Session

        mock_logging.get_logger.return_value = MagicMock()

        session = Session()
        # Set created to 5 days ago
        session.created = time.time() - (5 * 86400)

        result = session._Session__created_older_than_x_days(1)

        self.assertTrue(result)


class TestSessionCheckSessionValid(unittest.TestCase):
    """Tests for Session.__check_session_valid private method."""

    def setUp(self):
        """Clear singleton before each test."""
        from unmanic.libs.singleton import SingletonType
        from unmanic.libs.session import Session

        if Session in SingletonType._instances:
            del SingletonType._instances[Session]

    def tearDown(self):
        """Clear singleton after each test."""
        from unmanic.libs.singleton import SingletonType
        from unmanic.libs.session import Session

        if Session in SingletonType._instances:
            del SingletonType._instances[Session]

    @patch("unmanic.libs.session.UnmanicLogging")
    @patch("unmanic.libs.session.requests.Session")
    def test_returns_false_when_never_created(self, mock_requests, mock_logging):
        """Test returns False when session was never created."""
        from unmanic.libs.session import Session

        mock_logging.get_logger.return_value = MagicMock()

        session = Session()
        session.created = None
        session.last_check = None

        result = session._Session__check_session_valid()

        self.assertFalse(result)

    @patch("unmanic.libs.session.UnmanicLogging")
    @patch("unmanic.libs.session.requests.Session")
    def test_returns_true_when_recently_created(self, mock_requests, mock_logging):
        """Test returns True when session was recently created."""
        from unmanic.libs.session import Session

        mock_logging.get_logger.return_value = MagicMock()

        session = Session()
        session.created = time.time()
        session.last_check = None

        result = session._Session__check_session_valid()

        self.assertTrue(result)


class TestSessionGetInstallationUuid(unittest.TestCase):
    """Tests for Session.get_installation_uuid method."""

    def setUp(self):
        """Clear singleton before each test."""
        from unmanic.libs.singleton import SingletonType
        from unmanic.libs.session import Session

        if Session in SingletonType._instances:
            del SingletonType._instances[Session]

    def tearDown(self):
        """Clear singleton after each test."""
        from unmanic.libs.singleton import SingletonType
        from unmanic.libs.session import Session

        if Session in SingletonType._instances:
            del SingletonType._instances[Session]

    @patch("unmanic.libs.session.UnmanicLogging")
    @patch("unmanic.libs.session.requests.Session")
    def test_returns_uuid_when_set(self, mock_requests, mock_logging):
        """Test returns UUID when already set."""
        from unmanic.libs.session import Session

        mock_logging.get_logger.return_value = MagicMock()

        session = Session()
        session.uuid = "test-uuid-12345"

        result = session.get_installation_uuid()

        self.assertEqual(result, "test-uuid-12345")

    @patch("unmanic.libs.session.Installation")
    @patch("unmanic.libs.session.UnmanicLogging")
    @patch("unmanic.libs.session.requests.Session")
    def test_fetches_uuid_when_not_set(self, mock_requests, mock_logging, mock_installation):
        """Test fetches UUID from database when not set."""
        from unmanic.libs.session import Session

        mock_logging.get_logger.return_value = MagicMock()

        # Mock installation data
        mock_install = MagicMock()
        mock_install.uuid = "db-uuid-67890"
        mock_install.level = 100
        mock_install.picture_uri = ""
        mock_install.name = ""
        mock_install.email = ""
        mock_install.created = None
        mock_install.user_access_token = None
        mock_install.application_token = ""

        mock_installation_instance = MagicMock()
        mock_installation_instance.select.return_value.order_by.return_value.limit.return_value.get.return_value = mock_install
        mock_installation.return_value = mock_installation_instance

        session = Session()
        session.uuid = None

        result = session.get_installation_uuid()

        self.assertEqual(result, "db-uuid-67890")


class TestSessionGetSupporterLevel(unittest.TestCase):
    """Tests for Session.get_supporter_level method."""

    def setUp(self):
        """Clear singleton before each test."""
        from unmanic.libs.singleton import SingletonType
        from unmanic.libs.session import Session

        if Session in SingletonType._instances:
            del SingletonType._instances[Session]

    def tearDown(self):
        """Clear singleton after each test."""
        from unmanic.libs.singleton import SingletonType
        from unmanic.libs.session import Session

        if Session in SingletonType._instances:
            del SingletonType._instances[Session]

    @patch("unmanic.libs.session.UnmanicLogging")
    @patch("unmanic.libs.session.requests.Session")
    def test_returns_level_when_set(self, mock_requests, mock_logging):
        """Test returns level when already set."""
        from unmanic.libs.session import Session

        mock_logging.get_logger.return_value = MagicMock()

        session = Session()
        # TARS default is 100
        result = session.get_supporter_level()

        self.assertEqual(result, 100)


class TestSessionUpdateSessionAuth(unittest.TestCase):
    """Tests for Session.__update_session_auth private method."""

    def setUp(self):
        """Clear singleton before each test."""
        from unmanic.libs.singleton import SingletonType
        from unmanic.libs.session import Session

        if Session in SingletonType._instances:
            del SingletonType._instances[Session]

    def tearDown(self):
        """Clear singleton after each test."""
        from unmanic.libs.singleton import SingletonType
        from unmanic.libs.session import Session

        if Session in SingletonType._instances:
            del SingletonType._instances[Session]

    @patch("unmanic.libs.session.UnmanicLogging")
    @patch("unmanic.libs.session.requests.Session")
    def test_updates_headers_with_token(self, mock_requests, mock_logging):
        """Test updates session headers with access token."""
        from unmanic.libs.session import Session

        mock_logging.get_logger.return_value = MagicMock()
        mock_requests_instance = MagicMock()
        mock_requests.return_value = mock_requests_instance

        session = Session()
        session._Session__update_session_auth(access_token="test-token-123")

        self.assertEqual(session.user_access_token, "test-token-123")
        mock_requests_instance.headers.update.assert_called()

    @patch("unmanic.libs.session.UnmanicLogging")
    @patch("unmanic.libs.session.requests.Session")
    def test_does_nothing_without_token(self, mock_requests, mock_logging):
        """Test does nothing when no token provided."""
        from unmanic.libs.session import Session

        mock_logging.get_logger.return_value = MagicMock()
        mock_requests_instance = MagicMock()
        mock_requests.return_value = mock_requests_instance

        session = Session()
        initial_token = session.user_access_token
        session._Session__update_session_auth(access_token=None)

        self.assertEqual(session.user_access_token, initial_token)


class TestSessionClearSessionAuth(unittest.TestCase):
    """Tests for Session.__clear_session_auth private method."""

    def setUp(self):
        """Clear singleton before each test."""
        from unmanic.libs.singleton import SingletonType
        from unmanic.libs.session import Session

        if Session in SingletonType._instances:
            del SingletonType._instances[Session]

    def tearDown(self):
        """Clear singleton after each test."""
        from unmanic.libs.singleton import SingletonType
        from unmanic.libs.session import Session

        if Session in SingletonType._instances:
            del SingletonType._instances[Session]

    @patch("unmanic.libs.session.UnmanicLogging")
    @patch("unmanic.libs.session.requests.Session")
    def test_clears_cookies_and_auth(self, mock_requests, mock_logging):
        """Test clears cookies and authorization header."""
        from unmanic.libs.session import Session

        mock_logging.get_logger.return_value = MagicMock()
        mock_requests_instance = MagicMock()
        mock_requests.return_value = mock_requests_instance

        session = Session()
        session._Session__clear_session_auth()

        mock_requests_instance.cookies.clear.assert_called_once()
        mock_requests_instance.headers.update.assert_called_with({"Authorization": ""})


class TestSessionSignOut(unittest.TestCase):
    """Tests for Session.sign_out method."""

    def setUp(self):
        """Clear singleton before each test."""
        from unmanic.libs.singleton import SingletonType
        from unmanic.libs.session import Session

        if Session in SingletonType._instances:
            del SingletonType._instances[Session]

    def tearDown(self):
        """Clear singleton after each test."""
        from unmanic.libs.singleton import SingletonType
        from unmanic.libs.session import Session

        if Session in SingletonType._instances:
            del SingletonType._instances[Session]

    @patch("unmanic.libs.session.Installation")
    @patch("unmanic.libs.session.UnmanicLogging")
    @patch("unmanic.libs.session.requests.Session")
    def test_sign_out_local_only(self, mock_requests, mock_logging, mock_installation):
        """Test sign out with remote=False doesn't call API."""
        from unmanic.libs.session import Session

        mock_logging.get_logger.return_value = MagicMock()
        mock_requests_instance = MagicMock()
        mock_requests.return_value = mock_requests_instance

        # Mock installation
        mock_install = MagicMock()
        mock_install.uuid = "test-uuid"
        mock_installation.get_or_none.return_value = mock_install

        session = Session()
        session.uuid = "test-uuid"
        result = session.sign_out(remote=False)

        self.assertTrue(result)
        # Verify no POST was made
        mock_requests_instance.post.assert_not_called()


if __name__ == "__main__":
    unittest.main()

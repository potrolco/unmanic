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


class TestSessionApiGet(unittest.TestCase):
    """Tests for Session.api_get method."""

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
    def test_api_get_success(self, mock_requests, mock_logging, mock_installation):
        """Test api_get returns json and status code on success."""
        from unmanic.libs.session import Session

        mock_logging.get_logger.return_value = MagicMock()

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": "test"}

        mock_requests_instance = MagicMock()
        mock_requests_instance.get.return_value = mock_response
        mock_requests.return_value = mock_requests_instance

        mock_install = MagicMock()
        mock_install.uuid = "test-uuid"
        mock_installation.get_or_none.return_value = mock_install

        session = Session()
        result, status = session.api_get("api", 1, "/test")

        self.assertEqual(result, {"data": "test"})
        self.assertEqual(status, 200)

    @patch("unmanic.libs.session.Installation")
    @patch("unmanic.libs.session.UnmanicLogging")
    @patch("unmanic.libs.session.requests.Session")
    def test_api_get_raises_on_error_status(self, mock_requests, mock_logging, mock_installation):
        """Test api_get raises RemoteApiException on status > 403."""
        from unmanic.libs.session import Session, RemoteApiException

        mock_logging.get_logger.return_value = MagicMock()

        mock_response = MagicMock()
        mock_response.status_code = 500

        mock_requests_instance = MagicMock()
        mock_requests_instance.get.return_value = mock_response
        mock_requests.return_value = mock_requests_instance

        mock_install = MagicMock()
        mock_install.uuid = "test-uuid"
        mock_installation.get_or_none.return_value = mock_install

        session = Session()

        with self.assertRaises(RemoteApiException):
            session.api_get("api", 1, "/test")


class TestSessionApiPost(unittest.TestCase):
    """Tests for Session.api_post method."""

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
    def test_api_post_success(self, mock_requests, mock_logging, mock_installation):
        """Test api_post returns json and status code on success."""
        from unmanic.libs.session import Session

        mock_logging.get_logger.return_value = MagicMock()

        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_response.json.return_value = {"created": True}

        mock_requests_instance = MagicMock()
        mock_requests_instance.post.return_value = mock_response
        mock_requests.return_value = mock_requests_instance

        mock_install = MagicMock()
        mock_install.uuid = "test-uuid"
        mock_installation.get_or_none.return_value = mock_install

        session = Session()
        result, status = session.api_post("api", 1, "/test", {"key": "value"})

        self.assertEqual(result, {"created": True})
        self.assertEqual(status, 201)
        mock_requests_instance.post.assert_called_once()

    @patch("unmanic.libs.session.Installation")
    @patch("unmanic.libs.session.UnmanicLogging")
    @patch("unmanic.libs.session.requests.Session")
    def test_api_post_raises_on_error_status(self, mock_requests, mock_logging, mock_installation):
        """Test api_post raises RemoteApiException on status > 403."""
        from unmanic.libs.session import Session, RemoteApiException

        mock_logging.get_logger.return_value = MagicMock()

        mock_response = MagicMock()
        mock_response.status_code = 500

        mock_requests_instance = MagicMock()
        mock_requests_instance.post.return_value = mock_response
        mock_requests.return_value = mock_requests_instance

        mock_install = MagicMock()
        mock_install.uuid = "test-uuid"
        mock_installation.get_or_none.return_value = mock_install

        session = Session()

        with self.assertRaises(RemoteApiException):
            session.api_post("api", 1, "/test", {})


class TestSessionGetAccessToken(unittest.TestCase):
    """Tests for Session.get_access_token method."""

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
    def test_returns_false_without_application_token(self, mock_requests, mock_logging, mock_installation):
        """Test get_access_token returns False when no application token."""
        from unmanic.libs.session import Session

        mock_logging.get_logger.return_value = MagicMock()
        mock_requests.return_value = MagicMock()

        mock_install = MagicMock()
        mock_install.uuid = "test-uuid"
        mock_installation.get_or_none.return_value = mock_install

        session = Session()
        session.application_token = None

        result = session.get_access_token()

        self.assertFalse(result)

    @patch("unmanic.libs.session.Installation")
    @patch("unmanic.libs.session.UnmanicLogging")
    @patch("unmanic.libs.session.requests.Session")
    def test_returns_true_on_success(self, mock_requests, mock_logging, mock_installation):
        """Test get_access_token returns True on successful token refresh."""
        from unmanic.libs.session import Session

        mock_logging.get_logger.return_value = MagicMock()

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"access_token": "new-token"}

        mock_requests_instance = MagicMock()
        mock_requests_instance.post.return_value = mock_response
        mock_requests.return_value = mock_requests_instance

        mock_install = MagicMock()
        mock_install.uuid = "test-uuid"
        mock_installation.get_or_none.return_value = mock_install

        session = Session()
        session.application_token = "app-token"
        session.uuid = "test-uuid"

        result = session.get_access_token()

        self.assertTrue(result)


class TestSessionUpdateCreatedTimestamp(unittest.TestCase):
    """Tests for Session.__update_created_timestamp method."""

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

    @patch("unmanic.libs.session.random.randint")
    @patch("unmanic.libs.session.time.time")
    @patch("unmanic.libs.session.Installation")
    @patch("unmanic.libs.session.UnmanicLogging")
    @patch("unmanic.libs.session.requests.Session")
    def test_sets_created_timestamp(self, mock_requests, mock_logging, mock_installation, mock_time, mock_random):
        """Test __update_created_timestamp sets created attribute."""
        from unmanic.libs.session import Session

        mock_logging.get_logger.return_value = MagicMock()
        mock_requests.return_value = MagicMock()

        mock_install = MagicMock()
        mock_install.uuid = "test-uuid"
        mock_installation.get_or_none.return_value = mock_install

        mock_time.return_value = 1000000
        mock_random.return_value = 500

        session = Session()
        session._Session__update_created_timestamp()

        # Should be time + random offset
        self.assertEqual(session.created, 1000500)


class TestSessionApiGet401Retry(unittest.TestCase):
    """Tests for Session.api_get 401 retry logic."""

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
    def test_api_get_retries_on_401(self, mock_requests, mock_logging, mock_installation):
        """Test api_get retries after 401 when token verification succeeds."""
        from unmanic.libs.session import Session

        mock_logging.get_logger.return_value = MagicMock()

        # First call returns 401, second returns 200
        mock_response_401 = MagicMock()
        mock_response_401.status_code = 401

        mock_response_200 = MagicMock()
        mock_response_200.status_code = 200
        mock_response_200.json.return_value = {"data": "success"}

        mock_requests_instance = MagicMock()
        # Need enough get responses: first 401, then 200 after retry
        mock_requests_instance.get.side_effect = [mock_response_401, mock_response_200, mock_response_200]
        # Mock verify_token to succeed (get_access_token calls post)
        mock_requests_instance.post.return_value = MagicMock(status_code=200, json=lambda: {"access_token": "new"})
        mock_requests.return_value = mock_requests_instance

        mock_install = MagicMock()
        mock_install.uuid = "test-uuid"
        mock_installation.get_or_none.return_value = mock_install

        session = Session()
        session.application_token = "app-token"
        session.uuid = "test-uuid"
        result, status = session.api_get("api", 1, "/test")

        self.assertEqual(status, 200)
        self.assertGreaterEqual(mock_requests_instance.get.call_count, 2)


class TestSessionApiPost401Retry(unittest.TestCase):
    """Tests for Session.api_post 401 retry logic."""

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
    def test_api_post_retries_on_401(self, mock_requests, mock_logging, mock_installation):
        """Test api_post retries after 401 when token verification succeeds."""
        from unmanic.libs.session import Session

        mock_logging.get_logger.return_value = MagicMock()

        # First post returns 401, verify_token post returns 200, retry post returns 201
        mock_response_401 = MagicMock()
        mock_response_401.status_code = 401

        mock_response_token = MagicMock()
        mock_response_token.status_code = 200
        mock_response_token.json.return_value = {"access_token": "new-token"}

        mock_response_201 = MagicMock()
        mock_response_201.status_code = 201
        mock_response_201.json.return_value = {"created": True}

        mock_requests_instance = MagicMock()
        mock_requests_instance.post.side_effect = [mock_response_401, mock_response_token, mock_response_201]
        mock_requests.return_value = mock_requests_instance

        mock_install = MagicMock()
        mock_install.uuid = "test-uuid"
        mock_installation.get_or_none.return_value = mock_install

        session = Session()
        session.application_token = "app-token"
        result, status = session.api_post("api", 1, "/test", {"key": "value"})

        self.assertEqual(status, 201)
        self.assertEqual(mock_requests_instance.post.call_count, 3)


class TestSessionResetInstallationData(unittest.TestCase):
    """Tests for Session.__reset_session_installation_data method."""

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

    @patch("unmanic.libs.session.time.time")
    @patch("unmanic.libs.session.Installation")
    @patch("unmanic.libs.session.UnmanicLogging")
    @patch("unmanic.libs.session.requests.Session")
    def test_resets_session_fields(self, mock_requests, mock_logging, mock_installation, mock_time):
        """Test __reset_session_installation_data clears fields."""
        from unmanic.libs.session import Session

        mock_logging.get_logger.return_value = MagicMock()
        mock_logging.enable_remote_logging = MagicMock()
        mock_logging.disable_remote_logging = MagicMock()
        mock_requests.return_value = MagicMock()
        mock_time.return_value = 12345

        mock_install = MagicMock()
        mock_install.uuid = "test-uuid"
        mock_installation.get_or_none.return_value = mock_install

        session = Session()
        session.name = "Old Name"
        session.email = "old@email.com"
        session.picture_uri = "http://old.uri"
        session.user_access_token = "old-token"

        session._Session__reset_session_installation_data()

        self.assertEqual(session.name, "")
        self.assertEqual(session.email, "")
        self.assertEqual(session.picture_uri, "")
        self.assertIsNone(session.user_access_token)
        self.assertEqual(session.level, 100)  # TARS always 100


class TestSessionGetSupporterLevelFetch(unittest.TestCase):
    """Tests for Session.get_supporter_level when fetching data."""

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
    def test_fetches_data_when_level_none(self, mock_requests, mock_logging, mock_installation):
        """Test get_supporter_level fetches installation data when level is None."""
        from unmanic.libs.session import Session

        mock_logging.get_logger.return_value = MagicMock()
        mock_requests.return_value = MagicMock()

        mock_install = MagicMock()
        mock_install.uuid = "test-uuid"
        mock_install.level = 100
        mock_installation.get_or_none.return_value = mock_install
        mock_installation.return_value.select.return_value.order_by.return_value.limit.return_value.get.return_value = (
            mock_install
        )

        session = Session()
        session.level = None

        result = session.get_supporter_level()

        # Should have fetched level (TARS always 100)
        self.assertEqual(result, 100)


class TestSessionCheckSessionValidEdgeCases(unittest.TestCase):
    """Tests for Session.__check_session_valid edge cases."""

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

    @patch("unmanic.libs.session.time.time")
    @patch("unmanic.libs.session.Installation")
    @patch("unmanic.libs.session.UnmanicLogging")
    @patch("unmanic.libs.session.requests.Session")
    def test_returns_true_when_last_check_within_window(self, mock_requests, mock_logging, mock_installation, mock_time):
        """Test __check_session_valid returns True when last check is within 2400-2700s window."""
        from unmanic.libs.session import Session

        mock_logging.get_logger.return_value = MagicMock()
        mock_requests.return_value = MagicMock()

        mock_install = MagicMock()
        mock_install.uuid = "test-uuid"
        mock_installation.get_or_none.return_value = mock_install

        # Current time is 3000, last check was at 500 (2500 seconds ago - within window)
        mock_time.return_value = 3000

        session = Session()
        session.last_check = 500
        session.created = 2000

        result = session._Session__check_session_valid()

        self.assertTrue(result)

    @patch("unmanic.libs.session.time.time")
    @patch("unmanic.libs.session.Installation")
    @patch("unmanic.libs.session.UnmanicLogging")
    @patch("unmanic.libs.session.requests.Session")
    def test_returns_false_when_session_old(self, mock_requests, mock_logging, mock_installation, mock_time):
        """Test __check_session_valid returns False when session is older than 2 days."""
        from unmanic.libs.session import Session

        mock_logging.get_logger.return_value = MagicMock()
        mock_requests.return_value = MagicMock()

        mock_install = MagicMock()
        mock_install.uuid = "test-uuid"
        mock_installation.get_or_none.return_value = mock_install

        # Current time, created 3 days ago (259200 seconds)
        current_time = 1000000
        mock_time.return_value = current_time

        session = Session()
        session.last_check = None
        session.created = current_time - 259200  # 3 days ago

        result = session._Session__check_session_valid()

        self.assertFalse(result)


class TestSessionFetchUserData(unittest.TestCase):
    """Tests for Session.fetch_user_data method."""

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
    def test_fetch_user_data_success(self, mock_requests, mock_logging, mock_installation):
        """Test fetch_user_data updates fields on success."""
        from unmanic.libs.session import Session

        mock_logging.get_logger.return_value = MagicMock()

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "success": True,
            "data": {
                "user": {
                    "name": "Test User",
                    "picture_uri": "/avatar.png",
                    "email": "test@example.com",
                }
            },
        }

        mock_requests_instance = MagicMock()
        mock_requests_instance.get.return_value = mock_response
        mock_requests.return_value = mock_requests_instance

        session = Session()
        session.fetch_user_data()

        self.assertEqual(session.name, "Test User")
        self.assertEqual(session.picture_uri, "/avatar.png")
        self.assertEqual(session.email, "test@example.com")
        self.assertEqual(session.level, 100)  # TARS always 100

    @patch("unmanic.libs.session.Installation")
    @patch("unmanic.libs.session.UnmanicLogging")
    @patch("unmanic.libs.session.requests.Session")
    def test_fetch_user_data_401_keeps_level(self, mock_requests, mock_logging, mock_installation):
        """Test fetch_user_data keeps supporter level on 401."""
        from unmanic.libs.session import Session

        mock_logging.get_logger.return_value = MagicMock()

        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_response.json.return_value = {}

        mock_requests_instance = MagicMock()
        mock_requests_instance.get.return_value = mock_response
        mock_requests.return_value = mock_requests_instance

        session = Session()
        session.fetch_user_data()

        self.assertEqual(session.level, 100)

    @patch("unmanic.libs.session.Installation")
    @patch("unmanic.libs.session.UnmanicLogging")
    @patch("unmanic.libs.session.requests.Session")
    def test_fetch_user_data_raises_on_server_error(self, mock_requests, mock_logging, mock_installation):
        """Test fetch_user_data raises exception on > 403."""
        from unmanic.libs.session import Session, RemoteApiException

        mock_logging.get_logger.return_value = MagicMock()

        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.json.return_value = {}

        mock_requests_instance = MagicMock()
        mock_requests_instance.get.return_value = mock_response
        mock_requests.return_value = mock_requests_instance

        session = Session()

        with self.assertRaises(RemoteApiException):
            session.fetch_user_data()


class TestSessionSignOutRemote(unittest.TestCase):
    """Tests for Session.sign_out with remote=True."""

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
    def test_sign_out_remote_calls_api(self, mock_requests, mock_logging, mock_installation):
        """Test sign_out with remote=True calls the API."""
        from unmanic.libs.session import Session

        mock_logging.get_logger.return_value = MagicMock()
        mock_logging.enable_remote_logging = MagicMock()
        mock_logging.disable_remote_logging = MagicMock()

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"success": True}

        mock_requests_instance = MagicMock()
        mock_requests_instance.post.return_value = mock_response
        mock_requests.return_value = mock_requests_instance

        mock_install = MagicMock()
        mock_install.uuid = "test-uuid"
        mock_installation.get_or_none.return_value = mock_install

        session = Session()
        session.uuid = "test-uuid"
        result = session.sign_out(remote=True)

        self.assertTrue(result)
        mock_requests_instance.post.assert_called()

    @patch("unmanic.libs.session.Installation")
    @patch("unmanic.libs.session.UnmanicLogging")
    @patch("unmanic.libs.session.requests.Session")
    def test_sign_out_remote_handles_api_error(self, mock_requests, mock_logging, mock_installation):
        """Test sign_out continues even if remote API fails."""
        from unmanic.libs.session import Session, RemoteApiException

        mock_logging.get_logger.return_value = MagicMock()
        mock_logging.enable_remote_logging = MagicMock()
        mock_logging.disable_remote_logging = MagicMock()

        mock_response = MagicMock()
        mock_response.status_code = 500

        mock_requests_instance = MagicMock()
        mock_requests_instance.post.return_value = mock_response
        mock_requests.return_value = mock_requests_instance

        mock_install = MagicMock()
        mock_install.uuid = "test-uuid"
        mock_installation.get_or_none.return_value = mock_install

        session = Session()
        session.uuid = "test-uuid"

        # Should not raise, should return True
        result = session.sign_out(remote=True)
        self.assertTrue(result)


class TestSessionGetPatreonSponsorPage(unittest.TestCase):
    """Tests for Session.get_patreon_sponsor_page method."""

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
    def test_returns_data_on_success(self, mock_requests, mock_logging, mock_installation):
        """Test get_patreon_sponsor_page returns data on success."""
        from unmanic.libs.session import Session

        mock_logging.get_logger.return_value = MagicMock()

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "success": True,
            "data": {"url": "https://patreon.com/unmanic"},
        }

        mock_requests_instance = MagicMock()
        mock_requests_instance.get.return_value = mock_response
        mock_requests.return_value = mock_requests_instance

        session = Session()
        result = session.get_patreon_sponsor_page()

        self.assertEqual(result, {"url": "https://patreon.com/unmanic"})

    @patch("unmanic.libs.session.Installation")
    @patch("unmanic.libs.session.UnmanicLogging")
    @patch("unmanic.libs.session.requests.Session")
    def test_returns_false_on_error(self, mock_requests, mock_logging, mock_installation):
        """Test get_patreon_sponsor_page returns False on error."""
        from unmanic.libs.session import Session

        mock_logging.get_logger.return_value = MagicMock()

        mock_requests_instance = MagicMock()
        mock_requests_instance.get.side_effect = Exception("Network error")
        mock_requests.return_value = mock_requests_instance

        session = Session()
        result = session.get_patreon_sponsor_page()

        self.assertFalse(result)


class TestSessionVerifyToken(unittest.TestCase):
    """Tests for Session.verify_token method."""

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
    def test_returns_true_when_token_valid(self, mock_requests, mock_logging, mock_installation):
        """Test verify_token returns True when access token is valid."""
        from unmanic.libs.session import Session

        mock_logging.get_logger.return_value = MagicMock()

        mock_response = MagicMock()
        mock_response.status_code = 200

        mock_requests_instance = MagicMock()
        mock_requests_instance.get.return_value = mock_response
        mock_requests.return_value = mock_requests_instance

        session = Session()
        session.user_access_token = "valid-token"

        result = session.verify_token()

        self.assertTrue(result)

    @patch("unmanic.libs.session.Installation")
    @patch("unmanic.libs.session.UnmanicLogging")
    @patch("unmanic.libs.session.requests.Session")
    def test_returns_false_when_no_tokens(self, mock_requests, mock_logging, mock_installation):
        """Test verify_token returns False when no tokens exist."""
        from unmanic.libs.session import Session

        mock_logging.get_logger.return_value = MagicMock()
        mock_requests.return_value = MagicMock()

        session = Session()
        session.user_access_token = None
        session.application_token = None

        result = session.verify_token()

        self.assertFalse(result)

    @patch("unmanic.libs.session.Installation")
    @patch("unmanic.libs.session.UnmanicLogging")
    @patch("unmanic.libs.session.requests.Session")
    def test_raises_on_server_error(self, mock_requests, mock_logging, mock_installation):
        """Test verify_token raises on server error."""
        from unmanic.libs.session import Session, RemoteApiException

        mock_logging.get_logger.return_value = MagicMock()

        mock_response = MagicMock()
        mock_response.status_code = 500

        mock_requests_instance = MagicMock()
        mock_requests_instance.get.return_value = mock_response
        mock_requests.return_value = mock_requests_instance

        session = Session()
        session.user_access_token = "valid-token"

        with self.assertRaises(RemoteApiException):
            session.verify_token()

    @patch("unmanic.libs.session.Installation")
    @patch("unmanic.libs.session.UnmanicLogging")
    @patch("unmanic.libs.session.requests.Session")
    def test_refreshes_on_invalid_token(self, mock_requests, mock_logging, mock_installation):
        """Test verify_token refreshes token when invalid."""
        from unmanic.libs.session import Session

        mock_logging.get_logger.return_value = MagicMock()

        # First verify returns 401, then get_access_token succeeds
        mock_verify_response = MagicMock()
        mock_verify_response.status_code = 401

        mock_token_response = MagicMock()
        mock_token_response.status_code = 200
        mock_token_response.json.return_value = {"data": {"accessToken": "new-token"}}

        mock_requests_instance = MagicMock()
        mock_requests_instance.get.return_value = mock_verify_response
        mock_requests_instance.post.return_value = mock_token_response
        mock_requests.return_value = mock_requests_instance

        mock_install = MagicMock()
        mock_install.uuid = "test-uuid"
        mock_installation.get_or_none.return_value = mock_install

        session = Session()
        session.user_access_token = "old-token"
        session.application_token = "app-token"
        session.uuid = "test-uuid"

        result = session.verify_token()

        self.assertTrue(result)


class TestSessionGetAccessTokenErrors(unittest.TestCase):
    """Tests for Session.get_access_token error handling."""

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
    def test_raises_on_server_error(self, mock_requests, mock_logging, mock_installation):
        """Test get_access_token raises on status > 403."""
        from unmanic.libs.session import Session, RemoteApiException

        mock_logging.get_logger.return_value = MagicMock()

        mock_response = MagicMock()
        mock_response.status_code = 500

        mock_requests_instance = MagicMock()
        mock_requests_instance.post.return_value = mock_response
        mock_requests.return_value = mock_requests_instance

        session = Session()
        session.application_token = "app-token"
        session.uuid = "test-uuid"

        with self.assertRaises(RemoteApiException):
            session.get_access_token()

    @patch("unmanic.libs.session.Installation")
    @patch("unmanic.libs.session.UnmanicLogging")
    @patch("unmanic.libs.session.requests.Session")
    def test_returns_false_on_403(self, mock_requests, mock_logging, mock_installation):
        """Test get_access_token returns False on 403."""
        from unmanic.libs.session import Session

        mock_logging.get_logger.return_value = MagicMock()

        mock_response = MagicMock()
        mock_response.status_code = 403
        mock_response.json.return_value = {"messages": ["Forbidden"]}

        mock_requests_instance = MagicMock()
        mock_requests_instance.post.return_value = mock_response
        mock_requests.return_value = mock_requests_instance

        session = Session()
        session.application_token = "app-token"
        session.uuid = "test-uuid"

        result = session.get_access_token()

        self.assertFalse(result)


class TestSessionAuthUserAccount(unittest.TestCase):
    """Tests for Session.auth_user_account method."""

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
    def test_returns_false_without_token_no_force(self, mock_requests, mock_logging, mock_installation):
        """Test auth_user_account returns False without token and not forced."""
        from unmanic.libs.session import Session

        mock_logging.get_logger.return_value = MagicMock()
        mock_requests.return_value = MagicMock()

        session = Session()
        session.user_access_token = None

        result = session.auth_user_account(force_checkin=False)

        self.assertFalse(result)

    @patch("unmanic.libs.session.Installation")
    @patch("unmanic.libs.session.UnmanicLogging")
    @patch("unmanic.libs.session.requests.Session")
    def test_returns_true_on_valid_token(self, mock_requests, mock_logging, mock_installation):
        """Test auth_user_account returns True when token is valid."""
        from unmanic.libs.session import Session

        mock_logging.get_logger.return_value = MagicMock()

        # verify_token returns 200, fetch_user_data returns 200
        mock_verify_response = MagicMock()
        mock_verify_response.status_code = 200

        mock_user_response = MagicMock()
        mock_user_response.status_code = 200
        mock_user_response.json.return_value = {
            "success": True,
            "data": {"user": {"name": "User", "email": "a@b.com", "picture_uri": ""}},
        }

        mock_requests_instance = MagicMock()
        mock_requests_instance.get.side_effect = [mock_verify_response, mock_user_response]
        mock_requests.return_value = mock_requests_instance

        session = Session()
        session.user_access_token = "valid-token"

        result = session.auth_user_account()

        self.assertTrue(result)


if __name__ == "__main__":
    unittest.main()

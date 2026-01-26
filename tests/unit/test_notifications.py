#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unit tests for the Notifications class in unmanic.libs.notifications.

Tests notification queue management for frontend messaging.
"""

import unittest
from unittest.mock import patch, MagicMock


class TestNotificationsValidateItem(unittest.TestCase):
    """Tests for Notifications.__validate_item static method."""

    def test_valid_item_returns_true(self):
        """Test valid item validation returns True."""
        from unmanic.libs.notifications import Notifications

        item = {
            "type": "info",
            "icon": "update",
            "label": "testLabel",
            "message": "Test message",
            "navigation": {"push": "/test"},
        }

        # Access the private static method
        result = Notifications._Notifications__validate_item(item)
        self.assertTrue(result)

    def test_missing_type_raises(self):
        """Test missing type key raises exception."""
        from unmanic.libs.notifications import Notifications

        item = {
            "icon": "update",
            "label": "testLabel",
            "message": "Test message",
            "navigation": {"push": "/test"},
        }

        with self.assertRaises(Exception) as ctx:
            Notifications._Notifications__validate_item(item)

        self.assertIn("Missing key: 'type'", str(ctx.exception))

    def test_missing_icon_raises(self):
        """Test missing icon key raises exception."""
        from unmanic.libs.notifications import Notifications

        item = {
            "type": "info",
            "label": "testLabel",
            "message": "Test message",
            "navigation": {"push": "/test"},
        }

        with self.assertRaises(Exception) as ctx:
            Notifications._Notifications__validate_item(item)

        self.assertIn("Missing key: 'icon'", str(ctx.exception))

    def test_missing_label_raises(self):
        """Test missing label key raises exception."""
        from unmanic.libs.notifications import Notifications

        item = {
            "type": "info",
            "icon": "update",
            "message": "Test message",
            "navigation": {"push": "/test"},
        }

        with self.assertRaises(Exception) as ctx:
            Notifications._Notifications__validate_item(item)

        self.assertIn("Missing key: 'label'", str(ctx.exception))

    def test_missing_message_raises(self):
        """Test missing message key raises exception."""
        from unmanic.libs.notifications import Notifications

        item = {
            "type": "info",
            "icon": "update",
            "label": "testLabel",
            "navigation": {"push": "/test"},
        }

        with self.assertRaises(Exception) as ctx:
            Notifications._Notifications__validate_item(item)

        self.assertIn("Missing key: 'message'", str(ctx.exception))

    def test_missing_navigation_raises(self):
        """Test missing navigation key raises exception."""
        from unmanic.libs.notifications import Notifications

        item = {
            "type": "info",
            "icon": "update",
            "label": "testLabel",
            "message": "Test message",
        }

        with self.assertRaises(Exception) as ctx:
            Notifications._Notifications__validate_item(item)

        self.assertIn("Missing key: 'navigation'", str(ctx.exception))

    def test_invalid_type_raises(self):
        """Test invalid type value raises exception."""
        from unmanic.libs.notifications import Notifications

        item = {
            "type": "invalid_type",
            "icon": "update",
            "label": "testLabel",
            "message": "Test message",
            "navigation": {"push": "/test"},
        }

        with self.assertRaises(Exception) as ctx:
            Notifications._Notifications__validate_item(item)

        self.assertIn("error", str(ctx.exception))
        self.assertIn("warning", str(ctx.exception))

    def test_valid_type_error(self):
        """Test type 'error' is valid."""
        from unmanic.libs.notifications import Notifications

        item = {
            "type": "error",
            "icon": "report",
            "label": "errorLabel",
            "message": "Error message",
            "navigation": {"push": "/error"},
        }

        result = Notifications._Notifications__validate_item(item)
        self.assertTrue(result)

    def test_valid_type_warning(self):
        """Test type 'warning' is valid."""
        from unmanic.libs.notifications import Notifications

        item = {
            "type": "warning",
            "icon": "warning",
            "label": "warningLabel",
            "message": "Warning message",
            "navigation": {"push": "/warning"},
        }

        result = Notifications._Notifications__validate_item(item)
        self.assertTrue(result)

    def test_valid_type_success(self):
        """Test type 'success' is valid."""
        from unmanic.libs.notifications import Notifications

        item = {
            "type": "success",
            "icon": "check",
            "label": "successLabel",
            "message": "Success message",
            "navigation": {"push": "/success"},
        }

        result = Notifications._Notifications__validate_item(item)
        self.assertTrue(result)


class TestNotificationsAdd(unittest.TestCase):
    """Tests for Notifications.add method."""

    def setUp(self):
        """Set up test with clean notifications instance."""
        # We need to clear the singleton for each test
        from unmanic.libs.notifications import Notifications
        from unmanic.libs.singleton import SingletonType

        # Clear singleton instance
        if Notifications in SingletonType._instances:
            del SingletonType._instances[Notifications]

    def tearDown(self):
        """Clean up after test."""
        from unmanic.libs.notifications import Notifications
        from unmanic.libs.singleton import SingletonType

        if Notifications in SingletonType._instances:
            del SingletonType._instances[Notifications]

    def test_add_valid_item(self):
        """Test adding a valid notification item."""
        from unmanic.libs.notifications import Notifications

        notifications = Notifications()

        item = {
            "uuid": "test-uuid-1",
            "type": "info",
            "icon": "update",
            "label": "testLabel",
            "message": "Test message",
            "navigation": {"push": "/test"},
        }

        notifications.add(item)

        items = notifications.read_all_items()
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]["uuid"], "test-uuid-1")

    def test_add_generates_uuid_when_missing(self):
        """Test add generates UUID when not provided."""
        from unmanic.libs.notifications import Notifications

        notifications = Notifications()

        item = {
            "type": "info",
            "icon": "update",
            "label": "testLabel",
            "message": "Test message",
            "navigation": {"push": "/test"},
        }

        notifications.add(item)

        items = notifications.read_all_items()
        self.assertEqual(len(items), 1)
        # UUID should have been generated
        self.assertIsNotNone(items[0].get("uuid"))
        self.assertTrue(len(items[0]["uuid"]) > 0)

    def test_add_duplicate_uuid_ignored(self):
        """Test adding duplicate UUID is ignored."""
        from unmanic.libs.notifications import Notifications

        notifications = Notifications()

        item = {
            "uuid": "duplicate-uuid",
            "type": "info",
            "icon": "update",
            "label": "testLabel",
            "message": "Test message",
            "navigation": {"push": "/test"},
        }

        notifications.add(item)
        notifications.add(item)

        items = notifications.read_all_items()
        self.assertEqual(len(items), 1)

    def test_add_invalid_item_raises(self):
        """Test adding invalid item raises exception."""
        from unmanic.libs.notifications import Notifications

        notifications = Notifications()

        item = {"type": "info"}  # Missing required keys

        with self.assertRaises(Exception):
            notifications.add(item)


class TestNotificationsRemove(unittest.TestCase):
    """Tests for Notifications.remove method."""

    def setUp(self):
        """Set up test with clean notifications instance."""
        from unmanic.libs.notifications import Notifications
        from unmanic.libs.singleton import SingletonType

        if Notifications in SingletonType._instances:
            del SingletonType._instances[Notifications]

    def tearDown(self):
        """Clean up after test."""
        from unmanic.libs.notifications import Notifications
        from unmanic.libs.singleton import SingletonType

        if Notifications in SingletonType._instances:
            del SingletonType._instances[Notifications]

    def test_remove_existing_item(self):
        """Test removing an existing notification."""
        from unmanic.libs.notifications import Notifications

        notifications = Notifications()

        item = {
            "uuid": "remove-test",
            "type": "info",
            "icon": "update",
            "label": "testLabel",
            "message": "Test message",
            "navigation": {"push": "/test"},
        }

        notifications.add(item)
        self.assertEqual(len(notifications.read_all_items()), 1)

        result = notifications.remove("remove-test")

        self.assertTrue(result)
        self.assertEqual(len(notifications.read_all_items()), 0)

    def test_remove_nonexistent_item(self):
        """Test removing non-existent item returns False."""
        from unmanic.libs.notifications import Notifications

        notifications = Notifications()

        result = notifications.remove("nonexistent-uuid")

        self.assertFalse(result)

    def test_remove_keeps_other_items(self):
        """Test remove only removes target item."""
        from unmanic.libs.notifications import Notifications

        notifications = Notifications()

        for i in range(3):
            item = {
                "uuid": f"item-{i}",
                "type": "info",
                "icon": "update",
                "label": "testLabel",
                "message": f"Message {i}",
                "navigation": {"push": "/test"},
            }
            notifications.add(item)

        notifications.remove("item-1")

        items = notifications.read_all_items()
        uuids = [item["uuid"] for item in items]

        self.assertEqual(len(items), 2)
        self.assertIn("item-0", uuids)
        self.assertIn("item-2", uuids)
        self.assertNotIn("item-1", uuids)


class TestNotificationsReadAllItems(unittest.TestCase):
    """Tests for Notifications.read_all_items method."""

    def setUp(self):
        """Set up test with clean notifications instance."""
        from unmanic.libs.notifications import Notifications
        from unmanic.libs.singleton import SingletonType

        if Notifications in SingletonType._instances:
            del SingletonType._instances[Notifications]

    def tearDown(self):
        """Clean up after test."""
        from unmanic.libs.notifications import Notifications
        from unmanic.libs.singleton import SingletonType

        if Notifications in SingletonType._instances:
            del SingletonType._instances[Notifications]

    def test_read_empty_returns_empty_list(self):
        """Test reading empty notifications returns empty list."""
        from unmanic.libs.notifications import Notifications

        notifications = Notifications()

        items = notifications.read_all_items()

        self.assertEqual(items, [])

    def test_read_preserves_items(self):
        """Test reading items does not remove them."""
        from unmanic.libs.notifications import Notifications

        notifications = Notifications()

        item = {
            "uuid": "read-test",
            "type": "info",
            "icon": "update",
            "label": "testLabel",
            "message": "Test message",
            "navigation": {"push": "/test"},
        }
        notifications.add(item)

        # Read twice to ensure items are preserved
        items1 = notifications.read_all_items()
        items2 = notifications.read_all_items()

        self.assertEqual(len(items1), 1)
        self.assertEqual(len(items2), 1)
        self.assertEqual(items1[0]["uuid"], items2[0]["uuid"])


class TestNotificationsUpdate(unittest.TestCase):
    """Tests for Notifications.update method."""

    def setUp(self):
        """Set up test with clean notifications instance."""
        from unmanic.libs.notifications import Notifications
        from unmanic.libs.singleton import SingletonType

        if Notifications in SingletonType._instances:
            del SingletonType._instances[Notifications]

    def tearDown(self):
        """Clean up after test."""
        from unmanic.libs.notifications import Notifications
        from unmanic.libs.singleton import SingletonType

        if Notifications in SingletonType._instances:
            del SingletonType._instances[Notifications]

    def test_update_existing_item(self):
        """Test updating an existing notification."""
        from unmanic.libs.notifications import Notifications

        notifications = Notifications()

        item = {
            "uuid": "update-test",
            "type": "info",
            "icon": "update",
            "label": "testLabel",
            "message": "Original message",
            "navigation": {"push": "/test"},
        }
        notifications.add(item)

        updated_item = {
            "uuid": "update-test",
            "type": "success",
            "icon": "check",
            "label": "updatedLabel",
            "message": "Updated message",
            "navigation": {"push": "/updated"},
        }
        notifications.update(updated_item)

        items = notifications.read_all_items()
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]["message"], "Updated message")
        self.assertEqual(items[0]["type"], "success")

    def test_update_nonexistent_adds_item(self):
        """Test updating non-existent item adds it."""
        from unmanic.libs.notifications import Notifications

        notifications = Notifications()

        item = {
            "uuid": "new-item",
            "type": "info",
            "icon": "update",
            "label": "testLabel",
            "message": "New message",
            "navigation": {"push": "/test"},
        }
        notifications.update(item)

        items = notifications.read_all_items()
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]["uuid"], "new-item")

    def test_update_generates_uuid_when_missing(self):
        """Test update generates UUID when not provided."""
        from unmanic.libs.notifications import Notifications

        notifications = Notifications()

        item = {
            "type": "info",
            "icon": "update",
            "label": "testLabel",
            "message": "Test message",
            "navigation": {"push": "/test"},
        }
        notifications.update(item)

        items = notifications.read_all_items()
        self.assertEqual(len(items), 1)
        self.assertIsNotNone(items[0].get("uuid"))

    def test_update_invalid_item_raises(self):
        """Test updating with invalid item raises exception."""
        from unmanic.libs.notifications import Notifications

        notifications = Notifications()

        item = {"type": "info"}  # Missing required keys

        with self.assertRaises(Exception):
            notifications.update(item)


class TestNotificationsInit(unittest.TestCase):
    """Tests for Notifications._init method."""

    def setUp(self):
        """Set up test with clean notifications instance."""
        from unmanic.libs.notifications import Notifications
        from unmanic.libs.singleton import SingletonType

        if Notifications in SingletonType._instances:
            del SingletonType._instances[Notifications]

    def tearDown(self):
        """Clean up after test."""
        from unmanic.libs.notifications import Notifications
        from unmanic.libs.singleton import SingletonType

        if Notifications in SingletonType._instances:
            del SingletonType._instances[Notifications]

    def test_init_creates_lock_and_set(self):
        """Test _init creates lock and all_items set."""
        from unmanic.libs.notifications import Notifications

        notifications = Notifications()

        self.assertTrue(hasattr(notifications, "_lock"))
        self.assertTrue(hasattr(notifications, "all_items"))
        self.assertIsInstance(notifications.all_items, set)


if __name__ == "__main__":
    unittest.main()

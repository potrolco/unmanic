#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unit tests for the FrontendPushMessages class in unmanic.libs.frontend_push_messages.

Tests frontend message queue management.
"""

import unittest
from unittest.mock import patch, MagicMock


class TestFrontendPushMessagesValidateItem(unittest.TestCase):
    """Tests for FrontendPushMessages.__validate_item static method."""

    def test_valid_item_returns_true(self):
        """Test valid item validation returns True."""
        from unmanic.libs.frontend_push_messages import FrontendPushMessages

        item = {
            "id": "test-id",
            "type": "info",
            "code": "testCode",
            "message": "Test message",
            "timeout": 5000,
        }

        result = FrontendPushMessages._FrontendPushMessages__validate_item(item)
        self.assertTrue(result)

    def test_missing_id_raises(self):
        """Test missing id key raises exception."""
        from unmanic.libs.frontend_push_messages import FrontendPushMessages

        item = {
            "type": "info",
            "code": "testCode",
            "message": "Test message",
            "timeout": 5000,
        }

        with self.assertRaises(Exception) as ctx:
            FrontendPushMessages._FrontendPushMessages__validate_item(item)

        self.assertIn("Missing key: 'id'", str(ctx.exception))

    def test_missing_type_raises(self):
        """Test missing type key raises exception."""
        from unmanic.libs.frontend_push_messages import FrontendPushMessages

        item = {
            "id": "test-id",
            "code": "testCode",
            "message": "Test message",
            "timeout": 5000,
        }

        with self.assertRaises(Exception) as ctx:
            FrontendPushMessages._FrontendPushMessages__validate_item(item)

        self.assertIn("Missing key: 'type'", str(ctx.exception))

    def test_missing_code_raises(self):
        """Test missing code key raises exception."""
        from unmanic.libs.frontend_push_messages import FrontendPushMessages

        item = {
            "id": "test-id",
            "type": "info",
            "message": "Test message",
            "timeout": 5000,
        }

        with self.assertRaises(Exception) as ctx:
            FrontendPushMessages._FrontendPushMessages__validate_item(item)

        self.assertIn("Missing key: 'code'", str(ctx.exception))

    def test_missing_message_raises(self):
        """Test missing message key raises exception."""
        from unmanic.libs.frontend_push_messages import FrontendPushMessages

        item = {
            "id": "test-id",
            "type": "info",
            "code": "testCode",
            "timeout": 5000,
        }

        with self.assertRaises(Exception) as ctx:
            FrontendPushMessages._FrontendPushMessages__validate_item(item)

        self.assertIn("Missing key: 'message'", str(ctx.exception))

    def test_missing_timeout_raises(self):
        """Test missing timeout key raises exception."""
        from unmanic.libs.frontend_push_messages import FrontendPushMessages

        item = {
            "id": "test-id",
            "type": "info",
            "code": "testCode",
            "message": "Test message",
        }

        with self.assertRaises(Exception) as ctx:
            FrontendPushMessages._FrontendPushMessages__validate_item(item)

        self.assertIn("Missing key: 'timeout'", str(ctx.exception))

    def test_invalid_type_raises(self):
        """Test invalid type value raises exception."""
        from unmanic.libs.frontend_push_messages import FrontendPushMessages

        item = {
            "id": "test-id",
            "type": "invalid_type",
            "code": "testCode",
            "message": "Test message",
            "timeout": 5000,
        }

        with self.assertRaises(Exception) as ctx:
            FrontendPushMessages._FrontendPushMessages__validate_item(item)

        self.assertIn("error", str(ctx.exception))
        self.assertIn("warning", str(ctx.exception))

    def test_valid_type_error(self):
        """Test type 'error' is valid."""
        from unmanic.libs.frontend_push_messages import FrontendPushMessages

        item = {
            "id": "test-id",
            "type": "error",
            "code": "errorCode",
            "message": "Error message",
            "timeout": 0,
        }

        result = FrontendPushMessages._FrontendPushMessages__validate_item(item)
        self.assertTrue(result)

    def test_valid_type_warning(self):
        """Test type 'warning' is valid."""
        from unmanic.libs.frontend_push_messages import FrontendPushMessages

        item = {
            "id": "test-id",
            "type": "warning",
            "code": "warningCode",
            "message": "Warning message",
            "timeout": 5000,
        }

        result = FrontendPushMessages._FrontendPushMessages__validate_item(item)
        self.assertTrue(result)

    def test_valid_type_success(self):
        """Test type 'success' is valid."""
        from unmanic.libs.frontend_push_messages import FrontendPushMessages

        item = {
            "id": "test-id",
            "type": "success",
            "code": "successCode",
            "message": "Success message",
            "timeout": 3000,
        }

        result = FrontendPushMessages._FrontendPushMessages__validate_item(item)
        self.assertTrue(result)

    def test_valid_type_status(self):
        """Test type 'status' is valid."""
        from unmanic.libs.frontend_push_messages import FrontendPushMessages

        item = {
            "id": "test-id",
            "type": "status",
            "code": "statusCode",
            "message": "Status message",
            "timeout": 0,
        }

        result = FrontendPushMessages._FrontendPushMessages__validate_item(item)
        self.assertTrue(result)


class TestFrontendPushMessagesAdd(unittest.TestCase):
    """Tests for FrontendPushMessages.add method."""

    def setUp(self):
        """Set up test with clean instance."""
        from unmanic.libs.frontend_push_messages import FrontendPushMessages
        from unmanic.libs.singleton import SingletonType

        if FrontendPushMessages in SingletonType._instances:
            del SingletonType._instances[FrontendPushMessages]

    def tearDown(self):
        """Clean up after test."""
        from unmanic.libs.frontend_push_messages import FrontendPushMessages
        from unmanic.libs.singleton import SingletonType

        if FrontendPushMessages in SingletonType._instances:
            del SingletonType._instances[FrontendPushMessages]

    def test_add_valid_item(self):
        """Test adding a valid message item."""
        from unmanic.libs.frontend_push_messages import FrontendPushMessages

        messages = FrontendPushMessages()

        item = {
            "id": "test-id-1",
            "type": "info",
            "code": "testCode",
            "message": "Test message",
            "timeout": 5000,
        }

        messages.add(item)

        items = messages.read_all_items()
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]["id"], "test-id-1")

    def test_add_duplicate_id_ignored(self):
        """Test adding duplicate ID is ignored."""
        from unmanic.libs.frontend_push_messages import FrontendPushMessages

        messages = FrontendPushMessages()

        item = {
            "id": "duplicate-id",
            "type": "info",
            "code": "testCode",
            "message": "Test message",
            "timeout": 5000,
        }

        messages.add(item)
        messages.add(item)

        items = messages.read_all_items()
        self.assertEqual(len(items), 1)

    def test_add_invalid_item_raises(self):
        """Test adding invalid item raises exception."""
        from unmanic.libs.frontend_push_messages import FrontendPushMessages

        messages = FrontendPushMessages()

        item = {"id": "test", "type": "info"}  # Missing required keys

        with self.assertRaises(Exception):
            messages.add(item)


class TestFrontendPushMessagesGetAllItems(unittest.TestCase):
    """Tests for FrontendPushMessages.get_all_items method."""

    def setUp(self):
        """Set up test with clean instance."""
        from unmanic.libs.frontend_push_messages import FrontendPushMessages
        from unmanic.libs.singleton import SingletonType

        if FrontendPushMessages in SingletonType._instances:
            del SingletonType._instances[FrontendPushMessages]

    def tearDown(self):
        """Clean up after test."""
        from unmanic.libs.frontend_push_messages import FrontendPushMessages
        from unmanic.libs.singleton import SingletonType

        if FrontendPushMessages in SingletonType._instances:
            del SingletonType._instances[FrontendPushMessages]

    def test_get_all_items_preserves_items(self):
        """Test get_all_items preserves items in queue."""
        from unmanic.libs.frontend_push_messages import FrontendPushMessages

        messages = FrontendPushMessages()

        item = {
            "id": "test-id",
            "type": "info",
            "code": "testCode",
            "message": "Test message",
            "timeout": 5000,
        }
        messages.add(item)

        items1 = messages.get_all_items()
        items2 = messages.get_all_items()

        self.assertEqual(len(items1), 1)
        self.assertEqual(len(items2), 1)


class TestFrontendPushMessagesRequeueItems(unittest.TestCase):
    """Tests for FrontendPushMessages.requeue_items method."""

    def setUp(self):
        """Set up test with clean instance."""
        from unmanic.libs.frontend_push_messages import FrontendPushMessages
        from unmanic.libs.singleton import SingletonType

        if FrontendPushMessages in SingletonType._instances:
            del SingletonType._instances[FrontendPushMessages]

    def tearDown(self):
        """Clean up after test."""
        from unmanic.libs.frontend_push_messages import FrontendPushMessages
        from unmanic.libs.singleton import SingletonType

        if FrontendPushMessages in SingletonType._instances:
            del SingletonType._instances[FrontendPushMessages]

    def test_requeue_items_adds_to_queue(self):
        """Test requeue_items adds items to queue."""
        from unmanic.libs.frontend_push_messages import FrontendPushMessages

        messages = FrontendPushMessages()

        items = [
            {
                "id": "requeue-1",
                "type": "info",
                "code": "code1",
                "message": "Message 1",
                "timeout": 5000,
            },
            {
                "id": "requeue-2",
                "type": "info",
                "code": "code2",
                "message": "Message 2",
                "timeout": 5000,
            },
        ]

        messages.requeue_items(items)

        result = messages.read_all_items()
        self.assertEqual(len(result), 2)


class TestFrontendPushMessagesRemoveItem(unittest.TestCase):
    """Tests for FrontendPushMessages.remove_item method."""

    def setUp(self):
        """Set up test with clean instance."""
        from unmanic.libs.frontend_push_messages import FrontendPushMessages
        from unmanic.libs.singleton import SingletonType

        if FrontendPushMessages in SingletonType._instances:
            del SingletonType._instances[FrontendPushMessages]

    def tearDown(self):
        """Clean up after test."""
        from unmanic.libs.frontend_push_messages import FrontendPushMessages
        from unmanic.libs.singleton import SingletonType

        if FrontendPushMessages in SingletonType._instances:
            del SingletonType._instances[FrontendPushMessages]

    def test_remove_existing_item(self):
        """Test removing an existing item."""
        from unmanic.libs.frontend_push_messages import FrontendPushMessages

        messages = FrontendPushMessages()

        item = {
            "id": "remove-test",
            "type": "info",
            "code": "testCode",
            "message": "Test message",
            "timeout": 5000,
        }
        messages.add(item)
        self.assertEqual(len(messages.read_all_items()), 1)

        messages.remove_item("remove-test")

        self.assertEqual(len(messages.read_all_items()), 0)

    def test_remove_keeps_other_items(self):
        """Test remove only removes target item."""
        from unmanic.libs.frontend_push_messages import FrontendPushMessages

        messages = FrontendPushMessages()

        for i in range(3):
            item = {
                "id": f"item-{i}",
                "type": "info",
                "code": "testCode",
                "message": f"Message {i}",
                "timeout": 5000,
            }
            messages.add(item)

        messages.remove_item("item-1")

        items = messages.read_all_items()
        ids = [item["id"] for item in items]

        self.assertEqual(len(items), 2)
        self.assertIn("item-0", ids)
        self.assertIn("item-2", ids)
        self.assertNotIn("item-1", ids)


class TestFrontendPushMessagesReadAllItems(unittest.TestCase):
    """Tests for FrontendPushMessages.read_all_items method."""

    def setUp(self):
        """Set up test with clean instance."""
        from unmanic.libs.frontend_push_messages import FrontendPushMessages
        from unmanic.libs.singleton import SingletonType

        if FrontendPushMessages in SingletonType._instances:
            del SingletonType._instances[FrontendPushMessages]

    def tearDown(self):
        """Clean up after test."""
        from unmanic.libs.frontend_push_messages import FrontendPushMessages
        from unmanic.libs.singleton import SingletonType

        if FrontendPushMessages in SingletonType._instances:
            del SingletonType._instances[FrontendPushMessages]

    def test_read_empty_returns_empty_list(self):
        """Test reading empty queue returns empty list."""
        from unmanic.libs.frontend_push_messages import FrontendPushMessages

        messages = FrontendPushMessages()

        items = messages.read_all_items()

        self.assertEqual(items, [])

    def test_read_preserves_items(self):
        """Test reading items does not remove them."""
        from unmanic.libs.frontend_push_messages import FrontendPushMessages

        messages = FrontendPushMessages()

        item = {
            "id": "read-test",
            "type": "info",
            "code": "testCode",
            "message": "Test message",
            "timeout": 5000,
        }
        messages.add(item)

        items1 = messages.read_all_items()
        items2 = messages.read_all_items()

        self.assertEqual(len(items1), 1)
        self.assertEqual(len(items2), 1)


class TestFrontendPushMessagesUpdate(unittest.TestCase):
    """Tests for FrontendPushMessages.update method."""

    def setUp(self):
        """Set up test with clean instance."""
        from unmanic.libs.frontend_push_messages import FrontendPushMessages
        from unmanic.libs.singleton import SingletonType

        if FrontendPushMessages in SingletonType._instances:
            del SingletonType._instances[FrontendPushMessages]

    def tearDown(self):
        """Clean up after test."""
        from unmanic.libs.frontend_push_messages import FrontendPushMessages
        from unmanic.libs.singleton import SingletonType

        if FrontendPushMessages in SingletonType._instances:
            del SingletonType._instances[FrontendPushMessages]

    def test_update_existing_item(self):
        """Test updating an existing item."""
        from unmanic.libs.frontend_push_messages import FrontendPushMessages

        messages = FrontendPushMessages()

        item = {
            "id": "update-test",
            "type": "info",
            "code": "testCode",
            "message": "Original message",
            "timeout": 5000,
        }
        messages.add(item)

        updated_item = {
            "id": "update-test",
            "type": "success",
            "code": "updatedCode",
            "message": "Updated message",
            "timeout": 3000,
        }
        messages.update(updated_item)

        items = messages.read_all_items()
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]["message"], "Updated message")
        self.assertEqual(items[0]["type"], "success")

    def test_update_nonexistent_adds_item(self):
        """Test updating non-existent item adds it."""
        from unmanic.libs.frontend_push_messages import FrontendPushMessages

        messages = FrontendPushMessages()

        item = {
            "id": "new-item",
            "type": "info",
            "code": "testCode",
            "message": "New message",
            "timeout": 5000,
        }
        messages.update(item)

        items = messages.read_all_items()
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]["id"], "new-item")

    def test_update_invalid_item_raises(self):
        """Test updating with invalid item raises exception."""
        from unmanic.libs.frontend_push_messages import FrontendPushMessages

        messages = FrontendPushMessages()

        item = {"id": "test", "type": "info"}  # Missing required keys

        with self.assertRaises(Exception):
            messages.update(item)


class TestFrontendPushMessagesInit(unittest.TestCase):
    """Tests for FrontendPushMessages._init method."""

    def setUp(self):
        """Set up test with clean instance."""
        from unmanic.libs.frontend_push_messages import FrontendPushMessages
        from unmanic.libs.singleton import SingletonType

        if FrontendPushMessages in SingletonType._instances:
            del SingletonType._instances[FrontendPushMessages]

    def tearDown(self):
        """Clean up after test."""
        from unmanic.libs.frontend_push_messages import FrontendPushMessages
        from unmanic.libs.singleton import SingletonType

        if FrontendPushMessages in SingletonType._instances:
            del SingletonType._instances[FrontendPushMessages]

    def test_init_creates_lock_and_set(self):
        """Test _init creates lock and all_items set."""
        from unmanic.libs.frontend_push_messages import FrontendPushMessages

        messages = FrontendPushMessages()

        self.assertTrue(hasattr(messages, "_lock"))
        self.assertTrue(hasattr(messages, "all_items"))
        self.assertIsInstance(messages.all_items, set)


if __name__ == "__main__":
    unittest.main()

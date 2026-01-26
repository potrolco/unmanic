#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unit tests for the Library class in unmanic.libs.library.

Tests library management functionality with mocked database models.
"""

import unittest
from unittest.mock import MagicMock, patch, PropertyMock


class TestGenerateRandomLibraryName(unittest.TestCase):
    """Tests for generate_random_library_name function."""

    def test_returns_string(self):
        """Test function returns a string."""
        from unmanic.libs.library import generate_random_library_name

        result = generate_random_library_name()

        self.assertIsInstance(result, str)

    def test_contains_the_word_library(self):
        """Test result contains 'library'."""
        from unmanic.libs.library import generate_random_library_name

        result = generate_random_library_name()

        self.assertIn("library", result)

    def test_format_matches_expected(self):
        """Test result matches 'Name, the adjective library' format."""
        from unmanic.libs.library import generate_random_library_name

        result = generate_random_library_name()

        self.assertIn(", the ", result)
        self.assertTrue(result.endswith(" library"))

    def test_generates_different_names(self):
        """Test function generates different names on multiple calls."""
        from unmanic.libs.library import generate_random_library_name

        names = {generate_random_library_name() for _ in range(50)}

        # Should have at least 30 unique names out of 50
        self.assertGreater(len(names), 30)


class TestLibraryInit(unittest.TestCase):
    """Tests for Library.__init__ method."""

    @patch("unmanic.libs.library.Libraries")
    def test_init_with_valid_id(self, mock_libraries):
        """Test init with valid library ID."""
        from unmanic.libs.library import Library

        mock_model = MagicMock()
        mock_model.id = 1
        mock_libraries.get_or_none.return_value = mock_model

        library = Library(1)

        self.assertEqual(library.model, mock_model)
        mock_libraries.get_or_none.assert_called_once_with(id=1)

    @patch("unmanic.libs.library.Libraries")
    def test_init_with_zero_id_raises(self, mock_libraries):
        """Test init with ID 0 raises exception."""
        from unmanic.libs.library import Library

        with self.assertRaises(Exception) as ctx:
            Library(0)

        self.assertIn("cannot be less than 1", str(ctx.exception))

    @patch("unmanic.libs.library.Libraries")
    def test_init_with_negative_id_raises(self, mock_libraries):
        """Test init with negative ID raises exception."""
        from unmanic.libs.library import Library

        with self.assertRaises(Exception) as ctx:
            Library(-5)

        self.assertIn("cannot be less than 1", str(ctx.exception))

    @patch("unmanic.libs.library.Libraries")
    def test_init_with_nonexistent_id_raises(self, mock_libraries):
        """Test init with non-existent library ID raises exception."""
        from unmanic.libs.library import Library

        mock_libraries.get_or_none.return_value = None

        with self.assertRaises(Exception) as ctx:
            Library(999)

        self.assertIn("Unable to fetch library", str(ctx.exception))
        self.assertIn("999", str(ctx.exception))


class TestLibraryGetters(unittest.TestCase):
    """Tests for Library getter methods."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_model = MagicMock()
        self.mock_model.id = 1
        self.mock_model.name = "Test Library"
        self.mock_model.path = "/path/to/library"
        self.mock_model.locked = False
        self.mock_model.enable_remote_only = False
        self.mock_model.enable_scanner = True
        self.mock_model.enable_inotify = False
        self.mock_model.priority_score = 100

    @patch("unmanic.libs.library.Libraries")
    def test_get_id(self, mock_libraries):
        """Test get_id returns model ID."""
        from unmanic.libs.library import Library

        mock_libraries.get_or_none.return_value = self.mock_model

        library = Library(1)
        result = library.get_id()

        self.assertEqual(result, 1)

    @patch("unmanic.libs.library.Libraries")
    def test_get_name(self, mock_libraries):
        """Test get_name returns model name."""
        from unmanic.libs.library import Library

        mock_libraries.get_or_none.return_value = self.mock_model

        library = Library(1)
        result = library.get_name()

        self.assertEqual(result, "Test Library")

    @patch("unmanic.libs.library.Libraries")
    def test_get_path(self, mock_libraries):
        """Test get_path returns model path."""
        from unmanic.libs.library import Library

        mock_libraries.get_or_none.return_value = self.mock_model

        library = Library(1)
        result = library.get_path()

        self.assertEqual(result, "/path/to/library")

    @patch("unmanic.libs.library.Libraries")
    def test_get_locked(self, mock_libraries):
        """Test get_locked returns model locked status."""
        from unmanic.libs.library import Library

        mock_libraries.get_or_none.return_value = self.mock_model

        library = Library(1)
        result = library.get_locked()

        self.assertFalse(result)

    @patch("unmanic.libs.library.Libraries")
    def test_get_enable_remote_only(self, mock_libraries):
        """Test get_enable_remote_only returns correct value."""
        from unmanic.libs.library import Library

        mock_libraries.get_or_none.return_value = self.mock_model

        library = Library(1)
        result = library.get_enable_remote_only()

        self.assertFalse(result)

    @patch("unmanic.libs.library.Libraries")
    def test_get_enable_scanner(self, mock_libraries):
        """Test get_enable_scanner returns correct value."""
        from unmanic.libs.library import Library

        mock_libraries.get_or_none.return_value = self.mock_model

        library = Library(1)
        result = library.get_enable_scanner()

        self.assertTrue(result)

    @patch("unmanic.libs.library.Libraries")
    def test_get_enable_inotify(self, mock_libraries):
        """Test get_enable_inotify returns correct value."""
        from unmanic.libs.library import Library

        mock_libraries.get_or_none.return_value = self.mock_model

        library = Library(1)
        result = library.get_enable_inotify()

        self.assertFalse(result)

    @patch("unmanic.libs.library.Libraries")
    def test_get_priority_score(self, mock_libraries):
        """Test get_priority_score returns correct value."""
        from unmanic.libs.library import Library

        mock_libraries.get_or_none.return_value = self.mock_model

        library = Library(1)
        result = library.get_priority_score()

        self.assertEqual(result, 100)


class TestLibrarySetters(unittest.TestCase):
    """Tests for Library setter methods."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_model = MagicMock()
        self.mock_model.id = 1

    @patch("unmanic.libs.library.Libraries")
    def test_set_name(self, mock_libraries):
        """Test set_name updates model name."""
        from unmanic.libs.library import Library

        mock_libraries.get_or_none.return_value = self.mock_model

        library = Library(1)
        library.set_name("New Name")

        self.assertEqual(self.mock_model.name, "New Name")

    @patch("unmanic.libs.library.Libraries")
    def test_set_path(self, mock_libraries):
        """Test set_path updates model path."""
        from unmanic.libs.library import Library

        mock_libraries.get_or_none.return_value = self.mock_model

        library = Library(1)
        library.set_path("/new/path")

        self.assertEqual(self.mock_model.path, "/new/path")

    @patch("unmanic.libs.library.Libraries")
    def test_set_locked(self, mock_libraries):
        """Test set_locked updates model locked status."""
        from unmanic.libs.library import Library

        mock_libraries.get_or_none.return_value = self.mock_model

        library = Library(1)
        library.set_locked(True)

        self.assertTrue(self.mock_model.locked)

    @patch("unmanic.libs.library.Libraries")
    def test_set_enable_remote_only(self, mock_libraries):
        """Test set_enable_remote_only updates model."""
        from unmanic.libs.library import Library

        mock_libraries.get_or_none.return_value = self.mock_model

        library = Library(1)
        library.set_enable_remote_only(True)

        self.assertTrue(self.mock_model.enable_remote_only)

    @patch("unmanic.libs.library.Libraries")
    def test_set_enable_scanner(self, mock_libraries):
        """Test set_enable_scanner updates model."""
        from unmanic.libs.library import Library

        mock_libraries.get_or_none.return_value = self.mock_model

        library = Library(1)
        library.set_enable_scanner(False)

        self.assertFalse(self.mock_model.enable_scanner)

    @patch("unmanic.libs.library.Libraries")
    def test_set_enable_inotify(self, mock_libraries):
        """Test set_enable_inotify updates model."""
        from unmanic.libs.library import Library

        mock_libraries.get_or_none.return_value = self.mock_model

        library = Library(1)
        library.set_enable_inotify(True)

        self.assertTrue(self.mock_model.enable_inotify)

    @patch("unmanic.libs.library.Libraries")
    def test_set_priority_score(self, mock_libraries):
        """Test set_priority_score updates model."""
        from unmanic.libs.library import Library

        mock_libraries.get_or_none.return_value = self.mock_model

        library = Library(1)
        library.set_priority_score(200)

        self.assertEqual(self.mock_model.priority_score, 200)


class TestLibraryWithinLimits(unittest.TestCase):
    """Tests for Library.within_library_count_limits method."""

    @patch("unmanic.libs.library.FrontendPushMessages")
    def test_always_returns_true(self, mock_push_messages):
        """Test TARS modification always returns True."""
        from unmanic.libs.library import Library

        mock_instance = MagicMock()
        mock_push_messages.return_value = mock_instance

        result = Library.within_library_count_limits()

        self.assertTrue(result)

    @patch("unmanic.libs.library.FrontendPushMessages")
    def test_removes_limit_message(self, mock_push_messages):
        """Test it removes the library limit warning message."""
        from unmanic.libs.library import Library

        mock_instance = MagicMock()
        mock_push_messages.return_value = mock_instance

        Library.within_library_count_limits()

        mock_instance.remove_item.assert_called_once_with("libraryEnabledLimits")


class TestLibraryCreate(unittest.TestCase):
    """Tests for Library.create static method."""

    @patch("unmanic.libs.library.Libraries")
    def test_create_removes_id_from_data(self, mock_libraries):
        """Test create removes 'id' from data before creating."""
        from unmanic.libs.library import Library

        mock_new_library = MagicMock()
        mock_new_library.id = 5
        mock_libraries.create.return_value = mock_new_library

        mock_model = MagicMock()
        mock_model.id = 5
        mock_libraries.get_or_none.return_value = mock_model

        data = {"id": 999, "name": "Test", "path": "/test"}
        result = Library.create(data)

        # Verify ID was removed - check that 'id' is not in call kwargs
        call_kwargs = mock_libraries.create.call_args[1]
        self.assertNotIn("id", call_kwargs)
        self.assertIn("name", call_kwargs)
        self.assertIn("path", call_kwargs)

    @patch("unmanic.libs.library.Libraries")
    def test_create_with_valid_data(self, mock_libraries):
        """Test create with valid data creates library."""
        from unmanic.libs.library import Library

        mock_new_library = MagicMock()
        mock_new_library.id = 5
        mock_libraries.create.return_value = mock_new_library

        mock_model = MagicMock()
        mock_model.id = 5
        mock_libraries.get_or_none.return_value = mock_model

        data = {"name": "Test Library", "path": "/test/path"}
        result = Library.create(data)

        mock_libraries.create.assert_called_once()
        self.assertEqual(result.model.id, 5)


class TestLibraryGetTags(unittest.TestCase):
    """Tests for Library.get_tags method."""

    @patch("unmanic.libs.library.Libraries")
    @patch("unmanic.libs.library.Tags")
    def test_get_tags_returns_list(self, mock_tags, mock_libraries):
        """Test get_tags returns list of tag names."""
        from unmanic.libs.library import Library

        mock_model = MagicMock()
        mock_model.id = 1

        # Create mock tags
        mock_tag1 = MagicMock()
        mock_tag1.name = "tag1"
        mock_tag2 = MagicMock()
        mock_tag2.name = "tag2"

        # Make tags.order_by return iterable
        mock_model.tags.order_by.return_value = [mock_tag1, mock_tag2]
        mock_libraries.get_or_none.return_value = mock_model

        library = Library(1)
        result = library.get_tags()

        self.assertEqual(result, ["tag1", "tag2"])

    @patch("unmanic.libs.library.Libraries")
    @patch("unmanic.libs.library.Tags")
    def test_get_tags_empty(self, mock_tags, mock_libraries):
        """Test get_tags returns empty list when no tags."""
        from unmanic.libs.library import Library

        mock_model = MagicMock()
        mock_model.id = 1
        mock_model.tags.order_by.return_value = []
        mock_libraries.get_or_none.return_value = mock_model

        library = Library(1)
        result = library.get_tags()

        self.assertEqual(result, [])


class TestLibrarySave(unittest.TestCase):
    """Tests for Library.save method."""

    @patch("unmanic.libs.library.Config")
    @patch("unmanic.libs.library.Libraries")
    def test_save_calls_model_save(self, mock_libraries, mock_config):
        """Test save calls model.save."""
        from unmanic.libs.library import Library

        mock_model = MagicMock()
        mock_model.id = 2  # Not default library
        mock_model.save.return_value = True
        mock_libraries.get_or_none.return_value = mock_model

        library = Library(2)
        result = library.save()

        mock_model.save.assert_called_once()
        self.assertTrue(result)

    @patch("unmanic.libs.library.Config")
    @patch("unmanic.libs.library.Libraries")
    def test_save_updates_config_for_default_library(self, mock_libraries, mock_config):
        """Test save updates Config for default library (ID=1)."""
        from unmanic.libs.library import Library

        mock_model = MagicMock()
        mock_model.id = 1
        mock_model.path = "/new/path"
        mock_model.save.return_value = True
        mock_libraries.get_or_none.return_value = mock_model

        mock_config_instance = MagicMock()
        mock_config.return_value = mock_config_instance

        library = Library(1)
        library.save()

        mock_config_instance.set_config_item.assert_called_once_with("library_path", "/new/path")


class TestLibraryDelete(unittest.TestCase):
    """Tests for Library.delete method."""

    @patch("unmanic.libs.library.Libraries")
    def test_delete_default_library_raises(self, mock_libraries):
        """Test delete of default library (ID=1) raises exception."""
        from unmanic.libs.library import Library

        mock_model = MagicMock()
        mock_model.id = 1
        mock_libraries.get_or_none.return_value = mock_model

        library = Library(1)

        with self.assertRaises(Exception) as ctx:
            library.delete()

        self.assertIn("default library", str(ctx.exception))

    @patch("unmanic.libs.library.Libraries")
    def test_delete_locked_library_raises(self, mock_libraries):
        """Test delete of locked library raises exception."""
        from unmanic.libs.library import Library

        mock_model = MagicMock()
        mock_model.id = 5
        mock_model.locked = True
        mock_libraries.get_or_none.return_value = mock_model

        library = Library(5)

        with self.assertRaises(Exception) as ctx:
            library.delete()

        self.assertIn("locked library", str(ctx.exception))

    @patch("unmanic.libs.library.EnabledPlugins")
    @patch("unmanic.libs.library.LibraryPluginFlow")
    @patch("unmanic.libs.library.Tasks")
    @patch("unmanic.libs.library.Libraries")
    def test_delete_removes_plugins_and_tasks(self, mock_libraries, mock_tasks, mock_flow, mock_enabled):
        """Test delete removes enabled plugins, plugin flows, and tasks."""
        from unmanic.libs.library import Library

        mock_model = MagicMock()
        mock_model.id = 5
        mock_model.locked = False
        mock_libraries.get_or_none.return_value = mock_model

        # Mock the delete queries
        mock_enabled_delete = MagicMock()
        mock_enabled_delete.where.return_value.execute.return_value = None
        mock_enabled.delete.return_value = mock_enabled_delete

        mock_flow_delete = MagicMock()
        mock_flow_delete.where.return_value.execute.return_value = None
        mock_flow.delete.return_value = mock_flow_delete

        # Mock tasks select for associated tasks removal
        mock_tasks.select.return_value.where.return_value = []
        mock_tasks.delete.return_value.where.return_value.execute.return_value = None

        library = Library(5)
        library.delete()

        mock_model.delete_instance.assert_called_once_with(recursive=True)


class TestLibraryGetAllLibraries(unittest.TestCase):
    """Tests for Library.get_all_libraries static method."""

    @patch("unmanic.libs.library.Libraries")
    @patch("unmanic.config.Config")
    def test_creates_default_when_empty(self, mock_config, mock_libraries):
        """Test creates default library when none exist."""
        from unmanic.libs.library import Library

        mock_config_instance = MagicMock()
        mock_config_instance.get_library_path.return_value = "/library"
        mock_config.return_value = mock_config_instance

        mock_libraries.select.return_value = []  # No libraries

        result = Library.get_all_libraries()

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["id"], 1)
        self.assertEqual(result[0]["path"], "/library")
        mock_libraries.create.assert_called_once()

    @patch("unmanic.libs.library.Libraries")
    @patch("unmanic.config.Config")
    def test_returns_existing_libraries(self, mock_config, mock_libraries):
        """Test returns existing libraries from database."""
        from unmanic.libs.library import Library

        mock_config_instance = MagicMock()
        mock_config_instance.get_library_path.return_value = "/library"
        mock_config.return_value = mock_config_instance

        # Create mock library
        mock_lib = MagicMock()
        mock_lib.id = 1
        mock_lib.name = "Test Library"
        mock_lib.path = "/library"
        mock_lib.locked = False
        mock_lib.enable_remote_only = False
        mock_lib.enable_scanner = True
        mock_lib.enable_inotify = False
        mock_lib.tags.order_by.return_value = []

        mock_libraries.select.return_value = [mock_lib]

        result = Library.get_all_libraries()

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["name"], "Test Library")

    @patch("unmanic.libs.library.common.get_default_library_path")
    @patch("unmanic.libs.library.Libraries")
    @patch("unmanic.config.Config")
    def test_uses_default_path_when_config_empty(self, mock_config, mock_libraries, mock_get_default):
        """Test uses common.get_default_library_path when config is empty."""
        from unmanic.libs.library import Library

        mock_config_instance = MagicMock()
        mock_config_instance.get_library_path.return_value = None
        mock_config.return_value = mock_config_instance

        mock_get_default.return_value = "/default/library"

        mock_libraries.select.return_value = []

        result = Library.get_all_libraries()

        mock_get_default.assert_called_once()
        self.assertEqual(result[0]["path"], "/default/library")


if __name__ == "__main__":
    unittest.main()

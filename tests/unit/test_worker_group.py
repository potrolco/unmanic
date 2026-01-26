#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unit tests for the WorkerGroup class in unmanic.libs.worker_group.

Tests worker group management including creation, modification, and deletion.
"""

import unittest
from unittest.mock import MagicMock, patch, PropertyMock


class TestGenerateRandomWorkerGroupName(unittest.TestCase):
    """Tests for generate_random_worker_group_name function."""

    def test_returns_string(self):
        """Test that function returns a string."""
        from unmanic.libs.worker_group import generate_random_worker_group_name

        result = generate_random_worker_group_name()
        self.assertIsInstance(result, str)

    def test_returns_non_empty(self):
        """Test that function returns a non-empty string."""
        from unmanic.libs.worker_group import generate_random_worker_group_name

        result = generate_random_worker_group_name()
        self.assertTrue(len(result) > 0)

    @patch("unmanic.libs.worker_group.random.choice")
    def test_uses_random_choice(self, mock_choice):
        """Test that function uses random.choice."""
        from unmanic.libs.worker_group import generate_random_worker_group_name

        mock_choice.return_value = "TestName"
        result = generate_random_worker_group_name()

        mock_choice.assert_called_once()
        self.assertEqual(result, "TestName")


class TestWorkerGroupInit(unittest.TestCase):
    """Tests for WorkerGroup initialization."""

    @patch("unmanic.libs.worker_group.WorkerGroups")
    def test_init_with_valid_id(self, mock_worker_groups):
        """Test initialization with valid group ID."""
        from unmanic.libs.worker_group import WorkerGroup

        mock_model = MagicMock()
        mock_worker_groups.get_or_none.return_value = mock_model

        worker_group = WorkerGroup(1)

        mock_worker_groups.get_or_none.assert_called_once_with(id=1)
        self.assertEqual(worker_group.model, mock_model)

    @patch("unmanic.libs.worker_group.WorkerGroups")
    def test_init_with_zero_id_raises(self, mock_worker_groups):
        """Test initialization with ID 0 raises exception."""
        from unmanic.libs.worker_group import WorkerGroup

        with self.assertRaises(Exception) as ctx:
            WorkerGroup(0)

        self.assertIn("cannot be less than 1", str(ctx.exception))

    @patch("unmanic.libs.worker_group.WorkerGroups")
    def test_init_with_negative_id_raises(self, mock_worker_groups):
        """Test initialization with negative ID raises exception."""
        from unmanic.libs.worker_group import WorkerGroup

        with self.assertRaises(Exception) as ctx:
            WorkerGroup(-5)

        self.assertIn("cannot be less than 1", str(ctx.exception))

    @patch("unmanic.libs.worker_group.WorkerGroups")
    def test_init_with_nonexistent_id_raises(self, mock_worker_groups):
        """Test initialization with non-existent ID raises exception."""
        from unmanic.libs.worker_group import WorkerGroup

        mock_worker_groups.get_or_none.return_value = None

        with self.assertRaises(Exception) as ctx:
            WorkerGroup(999)

        self.assertIn("Unable to fetch Worker group", str(ctx.exception))
        self.assertIn("999", str(ctx.exception))


class TestWorkerGroupRandomName(unittest.TestCase):
    """Tests for WorkerGroup.random_name static method."""

    @patch("unmanic.libs.worker_group.generate_random_worker_group_name")
    def test_random_name_calls_generator(self, mock_generator):
        """Test random_name calls the generator function."""
        from unmanic.libs.worker_group import WorkerGroup

        mock_generator.return_value = "RandomName"
        result = WorkerGroup.random_name()

        mock_generator.assert_called_once()
        self.assertEqual(result, "RandomName")


class TestWorkerGroupGetAllWorkerGroups(unittest.TestCase):
    """Tests for WorkerGroup.get_all_worker_groups static method."""

    @patch("unmanic.libs.worker_group.config.Config")
    @patch("unmanic.libs.worker_group.WorkerGroups")
    @patch("unmanic.libs.worker_group.generate_random_worker_group_name")
    def test_returns_empty_when_no_groups_no_legacy(self, mock_gen_name, mock_worker_groups, mock_config):
        """Test returns empty list when no groups exist and no legacy settings.

        Note: The source code falls through to iterate over empty result when
        no legacy settings exist. This is likely a bug - it should return the
        default_worker_group without requiring legacy settings.
        """
        from unmanic.libs.worker_group import WorkerGroup

        # Return empty list (not None) to avoid TypeError
        mock_worker_groups.select.return_value = []
        mock_gen_name.return_value = "DefaultName"

        # No legacy settings
        mock_settings = MagicMock()
        mock_settings.number_of_workers = None
        mock_config.return_value = mock_settings

        result = WorkerGroup.get_all_worker_groups()

        # Empty list because no legacy settings triggers return path
        self.assertEqual(result, [])

    @patch("unmanic.libs.worker_group.WorkerGroup.create")
    @patch("unmanic.libs.worker_group.config.Config")
    @patch("unmanic.libs.worker_group.WorkerGroups")
    @patch("unmanic.libs.worker_group.generate_random_worker_group_name")
    def test_migrates_legacy_settings(self, mock_gen_name, mock_worker_groups, mock_config, mock_create):
        """Test migrates legacy settings when no groups exist."""
        from unmanic.libs.worker_group import WorkerGroup

        mock_worker_groups.select.return_value = None
        mock_gen_name.return_value = "MigratedName"

        # Legacy settings present
        mock_settings = MagicMock()
        mock_settings.number_of_workers = 4
        mock_settings.worker_event_schedules = [{"test": "schedule"}]
        mock_config.return_value = mock_settings

        result = WorkerGroup.get_all_worker_groups()

        self.assertEqual(result[0]["number_of_workers"], 4)
        self.assertEqual(result[0]["worker_event_schedules"], [{"test": "schedule"}])

        # Verify legacy settings were disabled
        mock_settings.set_config_item.assert_any_call("number_of_workers", None, save_settings=True)
        mock_settings.set_config_item.assert_any_call("worker_event_schedules", None, save_settings=True)

        # Verify create was called
        mock_create.assert_called_once()

    @patch("unmanic.libs.worker_group.WorkerGroups")
    def test_returns_existing_groups(self, mock_worker_groups):
        """Test returns existing worker groups with tags and schedules."""
        from unmanic.libs.worker_group import WorkerGroup

        # Create mock group
        mock_tag = MagicMock()
        mock_tag.name = "tag1"

        mock_schedule = MagicMock()
        mock_schedule.repetition = "daily"
        mock_schedule.schedule_task = "enable"
        mock_schedule.schedule_time = "09:00"
        mock_schedule.schedule_worker_count = 2

        mock_group = MagicMock()
        mock_group.id = 1
        mock_group.locked = False
        mock_group.name = "TestGroup"
        mock_group.number_of_workers = 3
        mock_group.tags.order_by.return_value = [mock_tag]
        mock_group.worker_schedules = [mock_schedule]

        mock_worker_groups.select.return_value = [mock_group]

        result = WorkerGroup.get_all_worker_groups()

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["id"], 1)
        self.assertEqual(result[0]["name"], "TestGroup")
        self.assertEqual(result[0]["number_of_workers"], 3)
        self.assertEqual(result[0]["tags"], ["tag1"])
        self.assertEqual(len(result[0]["worker_event_schedules"]), 1)
        self.assertEqual(result[0]["worker_event_schedules"][0]["repetition"], "daily")


class TestWorkerGroupCreate(unittest.TestCase):
    """Tests for WorkerGroup.create static method."""

    @patch("unmanic.libs.worker_group.Tags")
    @patch("unmanic.libs.worker_group.WorkerSchedules")
    @patch("unmanic.libs.worker_group.WorkerGroups")
    def test_create_with_name(self, mock_worker_groups, mock_schedules, mock_tags):
        """Test create with provided name uses that name."""
        mock_created = MagicMock()
        mock_created.id = 1
        mock_worker_groups.create.return_value = mock_created

        mock_model = MagicMock()
        mock_model.id = 1
        mock_worker_groups.get_or_none.return_value = mock_model

        # Mock the schedule delete chain
        mock_delete_query = MagicMock()
        mock_schedules.delete.return_value = mock_delete_query
        mock_delete_query.where.return_value = mock_delete_query

        from unmanic.libs.worker_group import WorkerGroup

        data = {"name": "MyCustomName", "number_of_workers": 2}
        WorkerGroup.create(data)

        # Verify custom name was used
        call_args = mock_worker_groups.create.call_args
        self.assertEqual(call_args.kwargs.get("name") or call_args[1].get("name"), "MyCustomName")

    @patch("unmanic.libs.worker_group.Tags")
    @patch("unmanic.libs.worker_group.WorkerSchedules")
    @patch("unmanic.libs.worker_group.WorkerGroups")
    @patch("unmanic.libs.worker_group.generate_random_worker_group_name")
    def test_create_generates_name_when_blank(self, mock_gen_name, mock_worker_groups, mock_schedules, mock_tags):
        """Test create generates name when not provided."""
        mock_gen_name.return_value = "GeneratedName"

        mock_created = MagicMock()
        mock_created.id = 1
        mock_worker_groups.create.return_value = mock_created

        mock_model = MagicMock()
        mock_model.id = 1
        mock_worker_groups.get_or_none.return_value = mock_model

        # Mock the schedule delete chain
        mock_delete_query = MagicMock()
        mock_schedules.delete.return_value = mock_delete_query
        mock_delete_query.where.return_value = mock_delete_query

        from unmanic.libs.worker_group import WorkerGroup

        data = {"number_of_workers": 2}
        WorkerGroup.create(data)

        # Verify generated name was used
        call_args = mock_worker_groups.create.call_args
        self.assertEqual(call_args.kwargs.get("name") or call_args[1].get("name"), "GeneratedName")


class TestWorkerGroupCreateSchedules(unittest.TestCase):
    """Tests for WorkerGroup.create_schedules static method."""

    @patch("unmanic.libs.worker_group.WorkerSchedules")
    def test_create_schedules(self, mock_schedules):
        """Test creating schedules for worker group."""
        from unmanic.libs.worker_group import WorkerGroup

        schedules = [
            {
                "repetition": "daily",
                "schedule_task": "enable",
                "schedule_time": "09:00",
                "schedule_worker_count": 2,
            },
            {
                "repetition": "weekly",
                "schedule_task": "disable",
                "schedule_time": "18:00",
                "schedule_worker_count": 0,
            },
        ]

        WorkerGroup.create_schedules(1, schedules)

        self.assertEqual(mock_schedules.create.call_count, 2)

    @patch("unmanic.libs.worker_group.WorkerSchedules")
    def test_create_schedules_empty_list(self, mock_schedules):
        """Test creating schedules with empty list."""
        from unmanic.libs.worker_group import WorkerGroup

        WorkerGroup.create_schedules(1, [])

        mock_schedules.create.assert_not_called()


class TestWorkerGroupGetters(unittest.TestCase):
    """Tests for WorkerGroup getter methods."""

    @patch("unmanic.libs.worker_group.WorkerGroups")
    def test_get_id(self, mock_worker_groups):
        """Test get_id returns model ID."""
        from unmanic.libs.worker_group import WorkerGroup

        mock_model = MagicMock()
        mock_model.id = 42
        mock_worker_groups.get_or_none.return_value = mock_model

        wg = WorkerGroup(1)
        self.assertEqual(wg.get_id(), 42)

    @patch("unmanic.libs.worker_group.WorkerGroups")
    def test_get_name(self, mock_worker_groups):
        """Test get_name returns model name."""
        from unmanic.libs.worker_group import WorkerGroup

        mock_model = MagicMock()
        mock_model.name = "TestGroup"
        mock_worker_groups.get_or_none.return_value = mock_model

        wg = WorkerGroup(1)
        self.assertEqual(wg.get_name(), "TestGroup")

    @patch("unmanic.libs.worker_group.WorkerGroups")
    def test_get_locked(self, mock_worker_groups):
        """Test get_locked returns model locked status."""
        from unmanic.libs.worker_group import WorkerGroup

        mock_model = MagicMock()
        mock_model.locked = True
        mock_worker_groups.get_or_none.return_value = mock_model

        wg = WorkerGroup(1)
        self.assertTrue(wg.get_locked())

    @patch("unmanic.libs.worker_group.WorkerGroups")
    def test_get_number_of_workers(self, mock_worker_groups):
        """Test get_number_of_workers returns model value."""
        from unmanic.libs.worker_group import WorkerGroup

        mock_model = MagicMock()
        mock_model.number_of_workers = 5
        mock_worker_groups.get_or_none.return_value = mock_model

        wg = WorkerGroup(1)
        self.assertEqual(wg.get_number_of_workers(), 5)

    @patch("unmanic.libs.worker_group.Tags")
    @patch("unmanic.libs.worker_group.WorkerGroups")
    def test_get_tags(self, mock_worker_groups, mock_tags):
        """Test get_tags returns list of tag names."""
        from unmanic.libs.worker_group import WorkerGroup

        mock_tag1 = MagicMock()
        mock_tag1.name = "tag1"
        mock_tag2 = MagicMock()
        mock_tag2.name = "tag2"

        mock_model = MagicMock()
        mock_model.tags.order_by.return_value = [mock_tag1, mock_tag2]
        mock_worker_groups.get_or_none.return_value = mock_model

        wg = WorkerGroup(1)
        result = wg.get_tags()

        self.assertEqual(result, ["tag1", "tag2"])

    @patch("unmanic.libs.worker_group.WorkerGroups")
    def test_get_worker_event_schedules(self, mock_worker_groups):
        """Test get_worker_event_schedules returns schedule dicts."""
        from unmanic.libs.worker_group import WorkerGroup

        mock_schedule = MagicMock()
        mock_schedule.repetition = "daily"
        mock_schedule.schedule_task = "enable"
        mock_schedule.schedule_time = "09:00"
        mock_schedule.schedule_worker_count = 2

        mock_model = MagicMock()
        mock_model.worker_schedules = [mock_schedule]
        mock_worker_groups.get_or_none.return_value = mock_model

        wg = WorkerGroup(1)
        result = wg.get_worker_event_schedules()

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["repetition"], "daily")
        self.assertEqual(result[0]["schedule_task"], "enable")


class TestWorkerGroupSetters(unittest.TestCase):
    """Tests for WorkerGroup setter methods."""

    @patch("unmanic.libs.worker_group.WorkerGroups")
    def test_set_name(self, mock_worker_groups):
        """Test set_name updates model name."""
        from unmanic.libs.worker_group import WorkerGroup

        mock_model = MagicMock()
        mock_worker_groups.get_or_none.return_value = mock_model

        wg = WorkerGroup(1)
        wg.set_name("NewName")

        self.assertEqual(mock_model.name, "NewName")

    @patch("unmanic.libs.worker_group.WorkerGroups")
    def test_set_locked(self, mock_worker_groups):
        """Test set_locked updates model locked status."""
        from unmanic.libs.worker_group import WorkerGroup

        mock_model = MagicMock()
        mock_worker_groups.get_or_none.return_value = mock_model

        wg = WorkerGroup(1)
        wg.set_locked(True)

        self.assertTrue(mock_model.locked)

    @patch("unmanic.libs.worker_group.WorkerGroups")
    def test_set_number_of_workers(self, mock_worker_groups):
        """Test set_number_of_workers updates model value."""
        from unmanic.libs.worker_group import WorkerGroup

        mock_model = MagicMock()
        mock_worker_groups.get_or_none.return_value = mock_model

        wg = WorkerGroup(1)
        wg.set_number_of_workers(10)

        self.assertEqual(mock_model.number_of_workers, 10)

    @patch("unmanic.libs.worker_group.Tags")
    @patch("unmanic.libs.worker_group.WorkerGroups")
    def test_set_tags(self, mock_worker_groups, mock_tags):
        """Test set_tags creates tags and updates model."""
        from unmanic.libs.worker_group import WorkerGroup

        mock_model = MagicMock()
        mock_worker_groups.get_or_none.return_value = mock_model

        mock_insert = MagicMock()
        mock_tags.insert.return_value = mock_insert

        mock_select_query = MagicMock()
        mock_tags.select.return_value.where.return_value = mock_select_query

        wg = WorkerGroup(1)
        wg.set_tags(["tag1", "tag2"])

        # Verify tags were inserted
        self.assertEqual(mock_tags.insert.call_count, 2)

        # Verify model tags were updated
        mock_model.tags.add.assert_called_once()


class TestWorkerGroupSetWorkerEventSchedules(unittest.TestCase):
    """Tests for WorkerGroup.set_worker_event_schedules."""

    @patch("unmanic.libs.worker_group.WorkerGroup.create_schedules")
    @patch("unmanic.libs.worker_group.WorkerSchedules")
    @patch("unmanic.libs.worker_group.WorkerGroups")
    def test_set_worker_event_schedules(self, mock_worker_groups, mock_schedules, mock_create_schedules):
        """Test set_worker_event_schedules removes old and creates new."""
        from unmanic.libs.worker_group import WorkerGroup

        mock_model = MagicMock()
        mock_model.id = 1
        mock_worker_groups.get_or_none.return_value = mock_model

        mock_delete_query = MagicMock()
        mock_schedules.delete.return_value = mock_delete_query
        mock_delete_query.where.return_value = mock_delete_query

        wg = WorkerGroup(1)
        schedules = [{"repetition": "daily"}]
        wg.set_worker_event_schedules(schedules)

        # Verify old schedules were deleted
        mock_schedules.delete.assert_called_once()
        mock_delete_query.execute.assert_called_once()

        # Verify new schedules were created
        mock_create_schedules.assert_called_once_with(1, schedules)

    @patch("unmanic.libs.worker_group.WorkerGroup.create_schedules")
    @patch("unmanic.libs.worker_group.WorkerSchedules")
    @patch("unmanic.libs.worker_group.WorkerGroups")
    def test_set_worker_event_schedules_empty(self, mock_worker_groups, mock_schedules, mock_create_schedules):
        """Test set_worker_event_schedules with empty list only removes."""
        from unmanic.libs.worker_group import WorkerGroup

        mock_model = MagicMock()
        mock_model.id = 1
        mock_worker_groups.get_or_none.return_value = mock_model

        mock_delete_query = MagicMock()
        mock_schedules.delete.return_value = mock_delete_query
        mock_delete_query.where.return_value = mock_delete_query

        wg = WorkerGroup(1)
        wg.set_worker_event_schedules([])

        # Verify old schedules were deleted
        mock_schedules.delete.assert_called_once()

        # Verify create_schedules was not called (empty list is falsy)
        mock_create_schedules.assert_not_called()


class TestWorkerGroupSave(unittest.TestCase):
    """Tests for WorkerGroup.save method."""

    @patch("unmanic.libs.worker_group.WorkerGroups")
    def test_save_with_name(self, mock_worker_groups):
        """Test save calls model.save when name exists."""
        from unmanic.libs.worker_group import WorkerGroup

        mock_model = MagicMock()
        mock_model.name = "ExistingName"
        mock_worker_groups.get_or_none.return_value = mock_model

        wg = WorkerGroup(1)
        wg.save()

        mock_model.save.assert_called_once()

    @patch("unmanic.libs.worker_group.generate_random_worker_group_name")
    @patch("unmanic.libs.worker_group.WorkerGroups")
    def test_save_generates_name_when_blank(self, mock_worker_groups, mock_gen_name):
        """Test save generates name when blank."""
        from unmanic.libs.worker_group import WorkerGroup

        mock_model = MagicMock()
        mock_model.name = ""
        mock_worker_groups.get_or_none.return_value = mock_model
        mock_gen_name.return_value = "GeneratedName"

        wg = WorkerGroup(1)
        wg.save()

        self.assertEqual(mock_model.name, "GeneratedName")
        mock_model.save.assert_called_once()

    @patch("unmanic.libs.worker_group.generate_random_worker_group_name")
    @patch("unmanic.libs.worker_group.WorkerGroups")
    def test_save_generates_name_when_none(self, mock_worker_groups, mock_gen_name):
        """Test save generates name when None."""
        from unmanic.libs.worker_group import WorkerGroup

        mock_model = MagicMock()
        mock_model.name = None
        mock_worker_groups.get_or_none.return_value = mock_model
        mock_gen_name.return_value = "GeneratedName"

        wg = WorkerGroup(1)
        wg.save()

        self.assertEqual(mock_model.name, "GeneratedName")


class TestWorkerGroupDelete(unittest.TestCase):
    """Tests for WorkerGroup.delete method."""

    @patch("unmanic.libs.worker_group.WorkerSchedules")
    @patch("unmanic.libs.worker_group.WorkerGroups")
    def test_delete_unlocked_group(self, mock_worker_groups, mock_schedules):
        """Test delete removes unlocked group."""
        from unmanic.libs.worker_group import WorkerGroup

        mock_model = MagicMock()
        mock_model.id = 1
        mock_model.locked = False
        mock_worker_groups.get_or_none.return_value = mock_model

        mock_delete_query = MagicMock()
        mock_schedules.delete.return_value = mock_delete_query
        mock_delete_query.where.return_value = mock_delete_query

        wg = WorkerGroup(1)
        wg.delete()

        # Verify schedules were removed
        mock_schedules.delete.assert_called_once()

        # Verify model was deleted
        mock_model.delete_instance.assert_called_once_with(recursive=True)

    @patch("unmanic.libs.worker_group.WorkerGroups")
    def test_delete_locked_group_raises(self, mock_worker_groups):
        """Test delete raises exception for locked group."""
        from unmanic.libs.worker_group import WorkerGroup

        mock_model = MagicMock()
        mock_model.locked = True
        mock_worker_groups.get_or_none.return_value = mock_model

        wg = WorkerGroup(1)

        with self.assertRaises(Exception) as ctx:
            wg.delete()

        self.assertIn("locked", str(ctx.exception).lower())


class TestWorkerGroupRemoveSchedules(unittest.TestCase):
    """Tests for WorkerGroup._WorkerGroup__remove_schedules private method."""

    @patch("unmanic.libs.worker_group.WorkerSchedules")
    @patch("unmanic.libs.worker_group.WorkerGroups")
    def test_remove_schedules(self, mock_worker_groups, mock_schedules):
        """Test __remove_schedules removes all schedules for group."""
        from unmanic.libs.worker_group import WorkerGroup

        mock_model = MagicMock()
        mock_model.id = 5
        mock_worker_groups.get_or_none.return_value = mock_model

        mock_delete_query = MagicMock()
        mock_schedules.delete.return_value = mock_delete_query
        mock_delete_query.where.return_value = mock_delete_query

        wg = WorkerGroup(1)
        wg._WorkerGroup__remove_schedules()

        mock_schedules.delete.assert_called_once()
        mock_delete_query.where.assert_called_once()
        mock_delete_query.execute.assert_called_once()


if __name__ == "__main__":
    unittest.main()

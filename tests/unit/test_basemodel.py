#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unit tests for the basemodel module in unmanic.libs.unmodels.lib.basemodel.

Tests utility functions and BaseModel class methods.
"""

import unittest
from datetime import date, datetime, time
from unittest.mock import MagicMock, patch


class TestStrpdatetime(unittest.TestCase):
    """Tests for strpdatetime function."""

    def test_parses_datetime_format(self):
        """Test parsing standard datetime format."""
        from unmanic.libs.unmodels.lib.basemodel import strpdatetime

        result = strpdatetime("2024-01-15T10:30:45")

        self.assertEqual(result, datetime(2024, 1, 15, 10, 30, 45))

    def test_parses_datetime_with_microseconds(self):
        """Test parsing datetime with microseconds."""
        from unmanic.libs.unmodels.lib.basemodel import strpdatetime

        result = strpdatetime("2024-01-15T10:30:45.123456")

        self.assertEqual(result, datetime(2024, 1, 15, 10, 30, 45, 123456))

    def test_returns_none_for_none_input(self):
        """Test returns None when input is None."""
        from unmanic.libs.unmodels.lib.basemodel import strpdatetime

        result = strpdatetime(None)

        self.assertIsNone(result)


class TestStrpdate(unittest.TestCase):
    """Tests for strpdate function."""

    def test_parses_date_format(self):
        """Test parsing standard date format."""
        from unmanic.libs.unmodels.lib.basemodel import strpdate

        result = strpdate("2024-01-15")

        self.assertEqual(result, date(2024, 1, 15))

    def test_returns_none_for_none_input(self):
        """Test returns None when input is None."""
        from unmanic.libs.unmodels.lib.basemodel import strpdate

        result = strpdate(None)

        self.assertIsNone(result)


class TestStrptime(unittest.TestCase):
    """Tests for strptime function."""

    def test_parses_time_format(self):
        """Test parsing standard time format."""
        from unmanic.libs.unmodels.lib.basemodel import strptime

        result = strptime("10:30:45")

        self.assertEqual(result, time(10, 30, 45))

    def test_parses_time_with_microseconds(self):
        """Test parsing time with microseconds."""
        from unmanic.libs.unmodels.lib.basemodel import strptime

        result = strptime("10:30:45.123456")

        self.assertEqual(result, time(10, 30, 45, 123456))

    def test_returns_none_for_none_input(self):
        """Test returns None when input is None."""
        from unmanic.libs.unmodels.lib.basemodel import strptime

        result = strptime(None)

        self.assertIsNone(result)


class TestNoSuchFieldError(unittest.TestCase):
    """Tests for NoSuchFieldError exception."""

    def test_inherits_from_type_error(self):
        """Test NoSuchFieldError inherits from TypeError."""
        from unmanic.libs.unmodels.lib.basemodel import NoSuchFieldError

        self.assertTrue(issubclass(NoSuchFieldError, TypeError))

    def test_can_be_raised(self):
        """Test NoSuchFieldError can be raised and caught."""
        from unmanic.libs.unmodels.lib.basemodel import NoSuchFieldError

        with self.assertRaises(NoSuchFieldError):
            raise NoSuchFieldError("Test error")


class TestNullError(unittest.TestCase):
    """Tests for NullError exception."""

    def test_inherits_from_type_error(self):
        """Test NullError inherits from TypeError."""
        from unmanic.libs.unmodels.lib.basemodel import NullError

        self.assertTrue(issubclass(NullError, TypeError))

    def test_can_be_raised(self):
        """Test NullError can be raised and caught."""
        from unmanic.libs.unmodels.lib.basemodel import NullError

        with self.assertRaises(NullError):
            raise NullError("Test error")


class TestDatabaseConstants(unittest.TestCase):
    """Tests for module-level constants."""

    def test_date_format_constant(self):
        """Test DATE_FORMAT constant."""
        from unmanic.libs.unmodels.lib.basemodel import DATE_FORMAT

        self.assertEqual(DATE_FORMAT, "%Y-%m-%d")

    def test_time_format_constant(self):
        """Test TIME_FORMAT constant."""
        from unmanic.libs.unmodels.lib.basemodel import TIME_FORMAT

        self.assertEqual(TIME_FORMAT, "%H:%M:%S")

    def test_datetime_format_constant(self):
        """Test DATETIME_FORMAT constant."""
        from unmanic.libs.unmodels.lib.basemodel import DATETIME_FORMAT

        self.assertEqual(DATETIME_FORMAT, "%Y-%m-%dT%H:%M:%S")


class TestDatabaseProxy(unittest.TestCase):
    """Tests for database proxy."""

    def test_db_proxy_exists(self):
        """Test database proxy is defined."""
        from unmanic.libs.unmodels.lib.basemodel import db

        self.assertIsNotNone(db)


class TestBaseModelMeta(unittest.TestCase):
    """Tests for BaseModel Meta class."""

    def test_meta_uses_db_proxy(self):
        """Test BaseModel Meta uses the database proxy."""
        from unmanic.libs.unmodels.lib.basemodel import BaseModel, db

        self.assertEqual(BaseModel._meta.database, db)


class TestDatabaseSelectDatabase(unittest.TestCase):
    """Tests for Database.select_database method."""

    @patch("unmanic.libs.unmodels.lib.basemodel.db")
    @patch("unmanic.libs.unmodels.lib.basemodel.SqliteQueueDatabase")
    def test_select_database_sqlite(self, mock_sqlite_db, mock_db_proxy):
        """Test select_database creates SQLite database."""
        from unmanic.libs.unmodels.lib.basemodel import Database

        mock_database = MagicMock()
        mock_sqlite_db.return_value = mock_database

        config = {"TYPE": "SQLITE", "FILE": "/tmp/test.db"}
        result = Database.select_database(config)

        mock_sqlite_db.assert_called_once()
        mock_db_proxy.initialize.assert_called_once_with(mock_database)
        mock_db_proxy.connect.assert_called_once()

    @patch("unmanic.libs.unmodels.lib.basemodel.db")
    @patch("unmanic.libs.unmodels.lib.basemodel.SqliteQueueDatabase")
    def test_select_database_returns_db_proxy(self, mock_sqlite_db, mock_db_proxy):
        """Test select_database returns the database proxy."""
        from unmanic.libs.unmodels.lib.basemodel import Database

        mock_sqlite_db.return_value = MagicMock()

        config = {"TYPE": "SQLITE", "FILE": "/tmp/test.db"}
        result = Database.select_database(config)

        self.assertEqual(result, mock_db_proxy)

    @patch("unmanic.libs.unmodels.lib.basemodel.db")
    @patch("unmanic.libs.unmodels.lib.basemodel.SqliteQueueDatabase")
    def test_select_database_uses_wal_mode(self, mock_sqlite_db, mock_db_proxy):
        """Test select_database enables WAL mode."""
        from unmanic.libs.unmodels.lib.basemodel import Database

        mock_sqlite_db.return_value = MagicMock()

        config = {"TYPE": "SQLITE", "FILE": "/tmp/test.db"}
        Database.select_database(config)

        # Check that WAL mode is in pragmas
        call_args = mock_sqlite_db.call_args
        pragmas = call_args[1]["pragmas"]
        pragma_dict = dict(pragmas)
        self.assertEqual(pragma_dict.get("journal_mode"), "wal")


class TestDatabaseClass(unittest.TestCase):
    """Tests for Database class."""

    def test_database_class_exists(self):
        """Test Database class is defined."""
        from unmanic.libs.unmodels.lib.basemodel import Database

        self.assertTrue(hasattr(Database, "select_database"))


class TestBaseModelGetFields(unittest.TestCase):
    """Tests for BaseModel.get_fields method."""

    def test_get_fields_returns_dict(self):
        """Test get_fields returns field metadata dictionary."""
        from unmanic.libs.unmodels.lib.basemodel import BaseModel

        # Create a mock model instance
        mock_model = MagicMock(spec=BaseModel)
        mock_model._meta = MagicMock()
        mock_fields = {"id": MagicMock(), "name": MagicMock()}
        mock_model._meta.fields = mock_fields

        # Call the real method
        result = BaseModel.get_fields(mock_model)

        self.assertEqual(result, mock_fields)


class TestBaseModelGetCurrentFieldValuesDict(unittest.TestCase):
    """Tests for BaseModel.get_current_field_values_dict method."""

    def test_get_current_field_values_dict_returns_data(self):
        """Test get_current_field_values_dict returns field values."""
        from unmanic.libs.unmodels.lib.basemodel import BaseModel

        mock_model = MagicMock(spec=BaseModel)
        mock_model.__data__ = {"id": 1, "name": "test"}

        result = BaseModel.get_current_field_values_dict(mock_model)

        self.assertEqual(result, {"id": 1, "name": "test"})


class TestBaseModelParseFieldValueByType(unittest.TestCase):
    """Tests for BaseModel.parse_field_value_by_type method."""

    def test_parse_field_raises_no_such_field_error(self):
        """Test parse_field_value_by_type raises NoSuchFieldError for invalid field."""
        from unmanic.libs.unmodels.lib.basemodel import BaseModel, NoSuchFieldError

        mock_model = MagicMock(spec=BaseModel)
        mock_model._meta = MagicMock()
        mock_model._meta.fields = {}

        # Bind the method properly
        mock_model.get_fields = lambda: {}

        with self.assertRaises(NoSuchFieldError):
            BaseModel.parse_field_value_by_type(mock_model, "invalid_field", "value")

    def test_parse_field_raises_null_error_for_non_nullable(self):
        """Test parse_field_value_by_type raises NullError for non-nullable field with None value."""
        from unmanic.libs.unmodels.lib.basemodel import BaseModel, NullError
        from peewee import TextField

        mock_model = MagicMock(spec=BaseModel)
        mock_field = MagicMock(spec=TextField)
        mock_field.null = False
        mock_model._meta = MagicMock()
        mock_model._meta.fields = {"name": mock_field}

        mock_model.get_fields = lambda: {"name": mock_field}

        with self.assertRaises(NullError):
            BaseModel.parse_field_value_by_type(mock_model, "name", None)

    def test_parse_field_returns_none_for_nullable(self):
        """Test parse_field_value_by_type returns None for nullable field."""
        from unmanic.libs.unmodels.lib.basemodel import BaseModel
        from peewee import TextField

        mock_model = MagicMock(spec=BaseModel)
        mock_field = MagicMock(spec=TextField)
        mock_field.null = True
        mock_model._meta = MagicMock()
        mock_model._meta.fields = {"name": mock_field}

        mock_model.get_fields = lambda: {"name": mock_field}

        result = BaseModel.parse_field_value_by_type(mock_model, "name", None)

        self.assertIsNone(result)

    def test_parse_boolean_field_true_string(self):
        """Test parse_field_value_by_type converts true string to boolean."""
        from unmanic.libs.unmodels.lib.basemodel import BaseModel
        from peewee import BooleanField

        mock_model = MagicMock(spec=BaseModel)
        mock_field = BooleanField()
        mock_model._meta = MagicMock()
        mock_model._meta.fields = {"enabled": mock_field}

        mock_model.get_fields = lambda: {"enabled": mock_field}

        result = BaseModel.parse_field_value_by_type(mock_model, "enabled", "true")

        self.assertTrue(result)

    def test_parse_boolean_field_false_string(self):
        """Test parse_field_value_by_type converts false string to boolean."""
        from unmanic.libs.unmodels.lib.basemodel import BaseModel
        from peewee import BooleanField

        mock_model = MagicMock(spec=BaseModel)
        mock_field = BooleanField()
        mock_model._meta = MagicMock()
        mock_model._meta.fields = {"enabled": mock_field}

        mock_model.get_fields = lambda: {"enabled": mock_field}

        result = BaseModel.parse_field_value_by_type(mock_model, "enabled", "false")

        self.assertFalse(result)

    def test_parse_boolean_field_int_value(self):
        """Test parse_field_value_by_type converts int to boolean."""
        from unmanic.libs.unmodels.lib.basemodel import BaseModel
        from peewee import BooleanField

        mock_model = MagicMock(spec=BaseModel)
        mock_field = BooleanField()
        mock_model._meta = MagicMock()
        mock_model._meta.fields = {"enabled": mock_field}

        mock_model.get_fields = lambda: {"enabled": mock_field}

        result = BaseModel.parse_field_value_by_type(mock_model, "enabled", 1)

        self.assertTrue(result)

    def test_parse_boolean_field_invalid_string(self):
        """Test parse_field_value_by_type returns False for invalid boolean string."""
        from unmanic.libs.unmodels.lib.basemodel import BaseModel
        from peewee import BooleanField

        mock_model = MagicMock(spec=BaseModel)
        mock_field = BooleanField()
        mock_model._meta = MagicMock()
        mock_model._meta.fields = {"enabled": mock_field}

        mock_model.get_fields = lambda: {"enabled": mock_field}

        result = BaseModel.parse_field_value_by_type(mock_model, "enabled", "invalid")

        self.assertFalse(result)

    def test_parse_integer_field(self):
        """Test parse_field_value_by_type converts string to int."""
        from unmanic.libs.unmodels.lib.basemodel import BaseModel
        from peewee import IntegerField

        mock_model = MagicMock(spec=BaseModel)
        mock_field = IntegerField()
        mock_model._meta = MagicMock()
        mock_model._meta.fields = {"count": mock_field}

        mock_model.get_fields = lambda: {"count": mock_field}

        result = BaseModel.parse_field_value_by_type(mock_model, "count", "42")

        self.assertEqual(result, 42)

    def test_parse_float_field(self):
        """Test parse_field_value_by_type converts string to float."""
        from unmanic.libs.unmodels.lib.basemodel import BaseModel
        from peewee import FloatField

        mock_model = MagicMock(spec=BaseModel)
        mock_field = FloatField()
        mock_model._meta = MagicMock()
        mock_model._meta.fields = {"ratio": mock_field}

        mock_model.get_fields = lambda: {"ratio": mock_field}

        result = BaseModel.parse_field_value_by_type(mock_model, "ratio", "3.14")

        self.assertAlmostEqual(result, 3.14)

    def test_parse_decimal_field(self):
        """Test parse_field_value_by_type converts string to decimal (float)."""
        from unmanic.libs.unmodels.lib.basemodel import BaseModel
        from peewee import DecimalField

        mock_model = MagicMock(spec=BaseModel)
        mock_field = DecimalField()
        mock_model._meta = MagicMock()
        mock_model._meta.fields = {"price": mock_field}

        mock_model.get_fields = lambda: {"price": mock_field}

        result = BaseModel.parse_field_value_by_type(mock_model, "price", "99.99")

        self.assertAlmostEqual(result, 99.99)

    def test_parse_datetime_field(self):
        """Test parse_field_value_by_type converts string to datetime."""
        from unmanic.libs.unmodels.lib.basemodel import BaseModel
        from peewee import DateTimeField

        mock_model = MagicMock(spec=BaseModel)
        mock_field = DateTimeField()
        mock_model._meta = MagicMock()
        mock_model._meta.fields = {"created": mock_field}

        mock_model.get_fields = lambda: {"created": mock_field}

        result = BaseModel.parse_field_value_by_type(mock_model, "created", "2024-01-15T10:30:45")

        self.assertEqual(result, datetime(2024, 1, 15, 10, 30, 45))

    def test_parse_date_field(self):
        """Test parse_field_value_by_type converts string to date."""
        from unmanic.libs.unmodels.lib.basemodel import BaseModel
        from peewee import DateField

        mock_model = MagicMock(spec=BaseModel)
        mock_field = DateField()
        mock_model._meta = MagicMock()
        mock_model._meta.fields = {"birth_date": mock_field}

        mock_model.get_fields = lambda: {"birth_date": mock_field}

        result = BaseModel.parse_field_value_by_type(mock_model, "birth_date", "2024-01-15")

        self.assertEqual(result, date(2024, 1, 15))

    def test_parse_time_field(self):
        """Test parse_field_value_by_type converts string to time."""
        from unmanic.libs.unmodels.lib.basemodel import BaseModel
        from peewee import TimeField

        mock_model = MagicMock(spec=BaseModel)
        mock_field = TimeField()
        mock_model._meta = MagicMock()
        mock_model._meta.fields = {"start_time": mock_field}

        mock_model.get_fields = lambda: {"start_time": mock_field}

        result = BaseModel.parse_field_value_by_type(mock_model, "start_time", "10:30:45")

        self.assertEqual(result, time(10, 30, 45))

    def test_parse_blob_field(self):
        """Test parse_field_value_by_type converts base64 to bytes."""
        from unmanic.libs.unmodels.lib.basemodel import BaseModel
        from peewee import BlobField

        mock_model = MagicMock(spec=BaseModel)
        mock_field = BlobField()
        mock_model._meta = MagicMock()
        mock_model._meta.fields = {"data": mock_field}

        mock_model.get_fields = lambda: {"data": mock_field}

        # "dGVzdA==" is base64 for "test"
        result = BaseModel.parse_field_value_by_type(mock_model, "data", "dGVzdA==")

        self.assertEqual(result, b"test")

    def test_parse_text_field_returns_string(self):
        """Test parse_field_value_by_type returns string for text field."""
        from unmanic.libs.unmodels.lib.basemodel import BaseModel
        from peewee import TextField

        mock_model = MagicMock(spec=BaseModel)
        mock_field = TextField()
        mock_model._meta = MagicMock()
        mock_model._meta.fields = {"description": mock_field}

        mock_model.get_fields = lambda: {"description": mock_field}

        result = BaseModel.parse_field_value_by_type(mock_model, "description", "test value")

        self.assertEqual(result, "test value")


class TestBaseModelModelToDict(unittest.TestCase):
    """Tests for BaseModel.model_to_dict method."""

    @patch("unmanic.libs.unmodels.lib.basemodel.model_to_dict")
    def test_model_to_dict_calls_peewee_helper(self, mock_model_to_dict):
        """Test model_to_dict uses playhouse.shortcuts.model_to_dict."""
        from unmanic.libs.unmodels.lib.basemodel import BaseModel

        mock_model = MagicMock(spec=BaseModel)
        mock_model_to_dict.return_value = {"id": 1, "name": "test"}

        result = BaseModel.model_to_dict(mock_model)

        mock_model_to_dict.assert_called_once_with(mock_model, backrefs=True)
        self.assertEqual(result, {"id": 1, "name": "test"})


if __name__ == "__main__":
    unittest.main()

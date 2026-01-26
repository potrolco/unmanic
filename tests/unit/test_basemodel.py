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


if __name__ == "__main__":
    unittest.main()

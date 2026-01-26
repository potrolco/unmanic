#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Unit tests for unmanic.metadata module.

Tests version string reading and module metadata.
"""

import pytest
from unittest.mock import patch, mock_open
import json

from unmanic import metadata


class TestReadVersionString:
    """Test read_version_string function."""

    def test_returns_long_version_by_default(self):
        """Should return long version string."""
        result = metadata.read_version_string("long")
        assert isinstance(result, str)

    def test_returns_short_version(self):
        """Should return short version string."""
        result = metadata.read_version_string("short")
        assert isinstance(result, str)

    def test_returns_unknown_on_missing_file(self):
        """Should return UNKNOWN.VERSION when file missing."""
        with patch("builtins.open", side_effect=FileNotFoundError):
            result = metadata.read_version_string()
            assert result == "UNKNOWN.VERSION"

    def test_returns_unknown_on_invalid_json(self):
        """Should return UNKNOWN.VERSION on invalid JSON."""
        with patch("builtins.open", mock_open(read_data="not json")):
            result = metadata.read_version_string()
            assert result == "UNKNOWN.VERSION"

    def test_returns_unknown_on_missing_key(self):
        """Should return UNKNOWN.VERSION when key missing."""
        mock_data = json.dumps({"other": "data"})
        with patch("builtins.open", mock_open(read_data=mock_data)):
            result = metadata.read_version_string("missing_key")
            assert result == "UNKNOWN.VERSION"


class TestModuleMetadata:
    """Test module-level metadata attributes."""

    def test_has_version(self):
        """Should have __version__ attribute."""
        assert hasattr(metadata, "__version__")
        assert isinstance(metadata.__version__, str)

    def test_has_author(self):
        """Should have __author__ attribute."""
        assert hasattr(metadata, "__author__")
        assert "TARS" in metadata.__author__ or "Josh" in metadata.__author__

    def test_has_description(self):
        """Should have __description__ attribute."""
        assert hasattr(metadata, "__description__")
        assert isinstance(metadata.__description__, str)

    def test_has_copyright(self):
        """Should have __copyright__ attribute."""
        assert hasattr(metadata, "__copyright__")
        assert "Copyright" in metadata.__copyright__

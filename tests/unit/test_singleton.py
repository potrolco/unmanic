#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Unit tests for unmanic.libs.singleton module.

Tests the SingletonType metaclass for thread-safe singleton behavior.
"""

import threading
import pytest

from unmanic.libs.singleton import SingletonType


class TestSingletonType:
    """Test SingletonType metaclass."""

    def setup_method(self):
        """Clear singleton instances before each test."""
        SingletonType._instances = {}

    def test_returns_same_instance(self):
        """Multiple calls should return same instance."""

        class MySingleton(metaclass=SingletonType):
            pass

        instance1 = MySingleton()
        instance2 = MySingleton()

        assert instance1 is instance2

    def test_different_classes_different_instances(self):
        """Different singleton classes should have different instances."""

        class SingletonA(metaclass=SingletonType):
            pass

        class SingletonB(metaclass=SingletonType):
            pass

        instance_a = SingletonA()
        instance_b = SingletonB()

        assert instance_a is not instance_b

    def test_preserves_init_args(self):
        """First init args should be preserved."""

        class ConfigSingleton(metaclass=SingletonType):
            def __init__(self, value):
                self.value = value

        first = ConfigSingleton("first_value")
        second = ConfigSingleton("second_value")

        assert first.value == "first_value"
        assert second.value == "first_value"
        assert first is second

    def test_thread_safety(self):
        """Should be thread-safe for concurrent access."""
        instances = []
        errors = []

        class ThreadSafeSingleton(metaclass=SingletonType):
            def __init__(self):
                self.id = id(self)

        def create_instance():
            try:
                instance = ThreadSafeSingleton()
                instances.append(instance)
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=create_instance) for _ in range(50)]

        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(errors) == 0
        # All instances should be the same object
        assert all(inst is instances[0] for inst in instances)

    def test_subclass_has_own_instance(self):
        """Subclasses should have their own singleton instances."""

        class BaseSingleton(metaclass=SingletonType):
            pass

        class DerivedSingleton(BaseSingleton):
            pass

        base = BaseSingleton()
        derived = DerivedSingleton()

        assert base is not derived
        assert BaseSingleton() is base
        assert DerivedSingleton() is derived

    def test_kwargs_preserved(self):
        """Keyword arguments should be preserved on first call."""

        class KwargSingleton(metaclass=SingletonType):
            def __init__(self, name="default", value=0):
                self.name = name
                self.value = value

        first = KwargSingleton(name="custom", value=42)
        second = KwargSingleton(name="other", value=100)

        assert first.name == "custom"
        assert first.value == 42
        assert second is first

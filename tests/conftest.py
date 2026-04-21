"""
Pytest configuration and fixtures for the activities API tests
"""

import pytest
from copy import deepcopy
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def client():
    """
    Fixture that provides a TestClient and saves/restores the in-memory
    activities dict to ensure test isolation and deterministic behavior.
    """
    original = deepcopy(activities)
    test_client = TestClient(app)
    yield test_client
    activities.clear()
    activities.update(original)

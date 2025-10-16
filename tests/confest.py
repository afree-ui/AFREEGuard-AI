from fastapi.testclient import TestClient
from agent.agent import app

import pytest

@pytest.fixture
def client():
    return TestClient(app)

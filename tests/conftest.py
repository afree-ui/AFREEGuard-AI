import pytest
from fastapi.testclient import TestClient

# Import your FastAPI app
from agent.agent import app   # <- this is where you defined: app = FastAPI(...)

@pytest.fixture
def client():
    """FastAPI test client for hitting /query etc."""
    return TestClient(app)

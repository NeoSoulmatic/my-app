import pytest
from app.main import app


@pytest.fixture
def client():
    """Create a test client for the Flask app."""
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_health_returns_200(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.get_json()["status"] == "healthy"


def test_ready_returns_200(client):
    response = client.get("/ready")
    assert response.status_code == 200
    assert response.get_json()["status"] == "ready"


def test_hello_returns_200(client):
    response = client.get("/")
    assert response.status_code == 200
    data = response.get_json()
    assert data["message"] == "Hello, World!"
    assert "timestamp" in data


def test_info_returns_version(client):
    response = client.get("/info")
    assert response.status_code == 200
    data = response.get_json()
    assert data["version"] == "1.0.0"
    assert data["app"] == "my-sre-app"

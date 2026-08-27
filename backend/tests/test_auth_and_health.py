from fastapi.testclient import TestClient
from pfcompass.main import app

client = TestClient(app)


def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "PF Compass API" in data["message"]
    assert "docs" in data

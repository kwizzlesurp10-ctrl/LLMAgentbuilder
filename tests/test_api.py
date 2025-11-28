from fastapi.testclient import TestClient
from server.main import app
import os

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_generate_agent():
    payload = {
        "name": "TestApiAgent",
        "prompt": "You are a test agent.",
        "task": "Do nothing.",
        "model": "claude-3-5-sonnet-20241022"
    }
    response = client.post("/api/generate", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "TestApiAgent" in data["code"]
    assert os.path.exists(data["path"])
    
    # Cleanup
    if os.path.exists(data["path"]):
        os.remove(data["path"])

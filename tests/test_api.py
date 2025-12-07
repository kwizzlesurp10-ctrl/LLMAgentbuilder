from fastapi.testclient import TestClient
from server.main import app
import os

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_healthz_check():
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_generate_agent():
    payload = {
        "name": "TestApiAgent",
        "prompt": "You are a test agent.",
        "task": "Do nothing.",
        "model": "claude-3-5-sonnet-20241022",
        "provider": "anthropic"
    }
    response = client.post("/api/generate", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "TestApiAgent" in data["code"]
    assert "filename" in data
    assert data["filename"] == "testapiagent.py"

def test_generate_agent_huggingface():
    payload = {
        "name": "TestHfAgent",
        "prompt": "You are a test agent.",
        "task": "Do nothing.",
        "model": "meta-llama/Meta-Llama-3-8B-Instruct",
        "provider": "huggingface"
    }
    response = client.post("/api/generate", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "TestHfAgent" in data["code"]

def test_generate_agent_invalid_model():
    payload = {
        "name": "TestAgent",
        "prompt": "Test",
        "task": "Test",
        "model": "invalid-model",
        "provider": "anthropic"
    }
    response = client.post("/api/generate", json=payload)
    assert response.status_code == 422  # Validation error

def test_generate_agent_long_prompt():
    payload = {
        "name": "TestAgent",
        "prompt": "A" * 10001,  # Exceeds 10000 char limit
        "task": "Test",
        "model": "claude-3-5-sonnet-20241022",
        "provider": "anthropic"
    }
    response = client.post("/api/generate", json=payload)
    assert response.status_code == 400
    assert "exceeds maximum length" in response.json()["detail"].lower()

def test_execute_agent():
    test_code = '''
class TestAgent:
    def __init__(self, api_key):
        self.api_key = api_key
    def run(self, task):
        return f"Processed: {task}"

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--task", default="test")
    args = parser.parse_args()
    agent = TestAgent("test")
    print(agent.run(args.task))
'''
    payload = {
        "code": test_code,
        "task": "Hello World"
    }
    response = client.post("/api/execute", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "Processed: Hello World" in data["output"]

def test_execute_agent_large_code():
    payload = {
        "code": "A" * 100001,  # Exceeds 100KB limit
        "task": "Test"
    }
    response = client.post("/api/execute", json=payload)
    assert response.status_code == 400
    assert "exceeds maximum size" in response.json()["detail"].lower()


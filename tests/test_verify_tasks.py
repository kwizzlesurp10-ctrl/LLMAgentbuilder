import requests
import json

BASE_URL = "http://localhost:8000"

def test_health():
    print("Testing /healthz...")
    try:
        r = requests.get(f"{BASE_URL}/healthz")
        r.raise_for_status()
        print(f"✅ /healthz passed: {r.json()}")
    except Exception as e:
        print(f"❌ /healthz failed: {e}")

def test_metrics():
    print("\nTesting /metrics...")
    try:
        r = requests.get(f"{BASE_URL}/metrics")
        r.raise_for_status()
        if "http_requests_total" in r.text:
            print("✅ /metrics passed (found http_requests_total)")
        else:
            print("❌ /metrics passed but unexpected content")
    except Exception as e:
        print(f"❌ /metrics failed: {e}")

def test_sandbox():
    print("\nTesting /api/execute (Sandbox)...")
    payload = {
        "code": "print('Hello from Sandbox!')",
        "task": "Test Task"
    }
    try:
        r = requests.post(f"{BASE_URL}/api/execute", json=payload)
        r.raise_for_status()
        data = r.json()
        if "Hello from Sandbox!" in data["output"]:
            print(f"✅ Sandbox passed: {data}")
        else:
            print(f"❌ Sandbox ran but output unexpected: {data}")
    except Exception as e:
        print(f"❌ Sandbox failed: {e}")

if __name__ == "__main__":
    test_health()
    test_metrics()
    test_sandbox()

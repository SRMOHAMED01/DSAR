import requests
import json

API_BASE_URL = "http://localhost:5000"

def test_health():
    response = requests.get(f"{API_BASE_URL}/health")
    print("Health:", response.json())
    assert response.status_code == 200

def test_create_request():
    data = {
        "requester_name": "Test User",
        "requester_email": "test@example.com",
        "request_type": "access",
        "identifier": "alice.johnson@example.com",
        "identifier_type": "email"
    }
    response = requests.post(f"{API_BASE_URL}/api/dsar/requests", json=data)
    print("Create:", response.status_code)
    return response.json()

if __name__ == "__main__":
    test_health()
    req = test_create_request()
    print(json.dumps(req, indent=2))

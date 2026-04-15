import json
import requests

BASE_URL = "http://127.0.0.1:5000"

def test_prediction(desc, payload):
    print(f"\n--- {desc} ---")
    print("Payload:", json.dumps(payload))

    response = requests.post(f"{BASE_URL}/predict", json=payload)

    print("Status:", response.status_code)
    print("Response:", json.dumps(response.json(), indent=2))


# Test cases
test_prediction("Normal Case", {
    "traffic_level": 3,
    "time_hour": 10,
    "lat": 40.7128,
    "lon": -74.0060
})

test_prediction("High Traffic", {
    "traffic_level": 5,
    "time_hour": 18,
    "lat": 40.7128,
    "lon": -74.0060
})
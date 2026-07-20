# tests/test_api.py
from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)

def test_health():
    assert client.get("/health").status_code == 200

def test_predict_energy_reasonable_range():
    resp = client.post("/predict/energy", json={
        "organization": "OpenAI", "input_tokens": 100, "output_tokens": 300,
        "is_long_prompt": False, "is_reasoning_or_heavy": False,
    })
    assert resp.status_code == 200
    wh = resp.json()["estimated_wh"]
    assert 0.05 < wh < 5.0  # sanity bounds, not precision — catches gross errors like the log1p/expm1 mismatch

def test_predict_energy_unknown_org_rejected():
    resp = client.post("/predict/energy", json={
        "organization": "NotARealCompany", "input_tokens": 100, "output_tokens": 300,
        "is_long_prompt": False, "is_reasoning_or_heavy": False,
    })
    assert resp.status_code == 400
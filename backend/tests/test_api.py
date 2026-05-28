from fastapi.testclient import TestClient

from backend.app.main import app


client = TestClient(app)


def test_health_returns_ok():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_register_snapshot_and_get_last_snapshot():
    project = {
        "project_id": "Camera_1",
        "name": "Left camera",
        "ip": "127.0.0.1",
        "port": 8000,
        "role": "inspection_camera",
    }
    response = client.post("/api/projects/register", json=project)
    assert response.status_code == 200
    assert response.json()["project_id"] == "Camera_1"

    snapshot = {
        "project_id": "Camera_1",
        "frame_id": "Camera_1_000001",
        "context": {"result": True},
        "global_data": {},
    }
    response = client.post("/api/snapshots", json=snapshot)
    assert response.status_code == 200

    response = client.get("/api/projects/Camera_1/last-snapshot")
    assert response.status_code == 200
    assert response.json()["frame_id"] == "Camera_1_000001"


def test_evaluate_returns_deterministic_spreadsheet_context():
    payload = {
        "project_id": "Camera_1",
        "frame_id": "Camera_1_000002",
        "mode": "sync",
        "context": {"result": False},
        "global_data": {},
    }
    response = client.post("/api/evaluate", json=payload)
    assert response.status_code == 200
    body = response.json()
    assert body["ok"] is False
    assert body["context_updates"]["spreadsheet"]["outputs"]["master_result"] is False
    assert body["control"]["exit"] is False

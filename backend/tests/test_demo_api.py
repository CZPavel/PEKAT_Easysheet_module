from fastapi.testclient import TestClient

from backend.app.main import app


client = TestClient(app)


def test_demo_state_contains_cameras():
    response = client.get("/api/demo/state")
    assert response.status_code == 200
    body = response.json()
    assert body["tick_index"] >= 0
    assert len(body["cameras"]) >= 3


def test_demo_tick_generates_snapshots_and_evaluations():
    reset_response = client.post("/api/demo/reset")
    assert reset_response.status_code == 200

    response = client.post("/api/demo/tick")
    assert response.status_code == 200
    body = response.json()
    assert body["running"] is True
    assert body["tick_index"] == 1

    first_camera = body["cameras"][0]
    assert first_camera["last_snapshot"]["frame_id"].endswith("000001")
    assert first_camera["last_evaluation"]["context_updates"]["spreadsheet"]["frame_id"]


def test_projects_endpoint_lists_demo_projects():
    response = client.get("/api/projects")
    assert response.status_code == 200
    project_ids = {project["project_id"] for project in response.json()}
    assert "Camera_1" in project_ids
    assert "Coordinator" in project_ids

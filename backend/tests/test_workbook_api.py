from fastapi.testclient import TestClient

from backend.app.formula.engine import MISSING, FormulaEngine
from backend.app.main import app

client = TestClient(app)


def test_formula_engine_pv_and_pv_count():
    engine = FormulaEngine()
    contexts = {"Camera_1": {"context": {"result": True, "detectedRectangles": [{"label": "Screw"}, {"label": "Screw"}, {"label": "Defect"}]}}}
    assert engine.evaluate_formula('=PV("Camera_1.context.result")', contexts) is True
    assert engine.evaluate_formula('=PV_COUNT("Camera_1", "Screw")', contexts) == 2
    assert engine.evaluate_formula('=PV_EXISTS("Camera_1", "Defect")', contexts) is True
    assert engine.evaluate_formula('=PV("Camera_1.context.missing")', contexts) == MISSING


def test_formula_engine_logic_subset():
    engine = FormulaEngine()
    assert engine.evaluate_formula("=IF(AND(TRUE, NOT(FALSE)), 10, 0)", {}) == 10
    assert engine.evaluate_formula("=OR(FALSE, TRUE)", {}) is True
    assert engine.evaluate_formula("=ROUND(ABS(-1.234), 1)", {}) == 1.2


def test_workbook_endpoints_binding_and_output_mapping():
    binding = {"sheet_name": "Camera_1", "cell": "C10", "source_path": "Camera_1.context.measurements.diameter_mm"}
    response = client.post("/api/workbooks/default/bindings", json=binding)
    assert response.status_code == 200
    assert response.json()["sheets"][0]["cells"]["C10"]["raw"] == '=PV("Camera_1.context.measurements.diameter_mm")'

    mapping = {"sheet_name": "Camera_1", "cell": "C10", "target": "spreadsheet.diameter_mm", "target_type": "context"}
    response = client.post("/api/workbooks/default/output-mappings", json=mapping)
    assert response.status_code == 200

    payload = {"contexts": {"Camera_1": {"context": {"measurements": {"diameter_mm": 12.1}}}}}
    response = client.post("/api/workbooks/default/evaluate", json=payload)
    assert response.status_code == 200
    assert response.json()["context_updates"]["spreadsheet"]["diameter_mm"] == 12.1


def test_context_tree_endpoint_after_demo_tick():
    client.post("/api/demo/reset")
    client.post("/api/demo/tick")
    response = client.get("/api/context/Camera_1/tree")
    assert response.status_code == 200
    body = response.json()
    assert body["project_id"] == "Camera_1"
    assert "context" in body["tree"]

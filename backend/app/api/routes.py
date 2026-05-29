"""REST API routy pro MVP PEKAT Easysheet backend."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, status

from backend.app.core.evaluator import SpreadsheetEvaluator
from backend.app.core.storage import MemoryStore
from backend.app.demo.simulator import DemoSimulator
from backend.app.workbook.models import CellBinding, OutputMapping, Workbook, WorkbookEvaluateRequest, WorkbookEvaluateResponse
from backend.app.workbook.service import WorkbookService
from backend.app.models import (
    EvaluateRequest,
    EvaluateResponse,
    DemoStateResponse,
    HealthResponse,
    ProjectRecord,
    ProjectRegistration,
    SnapshotIn,
    SnapshotRecord,
)

router = APIRouter()
store = MemoryStore()
evaluator = SpreadsheetEvaluator()
demo_simulator = DemoSimulator(store=store, evaluator=evaluator)
workbook_service = WorkbookService()


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    """Rychl? kontrola, ?e backend b???."""

    return HealthResponse()


@router.post("/api/projects/register", response_model=ProjectRecord)
def register_project(payload: ProjectRegistration) -> ProjectRecord:
    """Registruje PEKAT kameru/projekt do backendu."""

    return store.register_project(payload)


@router.post("/api/snapshots", response_model=SnapshotRecord)
def save_snapshot(payload: SnapshotIn) -> SnapshotRecord:
    """Ulo?? posledn? snapshot pro dan? projekt."""

    return store.save_snapshot(payload)


@router.get("/api/projects/{project_id}/last-snapshot", response_model=SnapshotRecord)
def get_last_snapshot(project_id: str) -> SnapshotRecord:
    """Vr?t? posledn? snapshot nebo 404, pokud zat?m neexistuje."""

    snapshot = store.get_last_snapshot(project_id)
    if snapshot is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Projekt {project_id!r} zat?m nem? snapshot.",
        )
    return snapshot


@router.post("/api/evaluate", response_model=EvaluateResponse)
def evaluate(payload: EvaluateRequest) -> EvaluateResponse:
    """Ulo?? snapshot a vr?t? v?sledek workbooku pro PEKAT Code bridge."""

    store.save_snapshot(payload)
    contexts: dict[str, dict[str, object]] = {}
    for project in store.list_projects():
        snapshot = store.get_last_snapshot(project.project_id)
        if snapshot is not None:
            contexts[project.project_id] = {
                "context": snapshot.context,
                "global_data": snapshot.global_data,
            }
    contexts[payload.project_id] = {
        "context": payload.context,
        "global_data": payload.global_data,
    }
    workbook_result = workbook_service.evaluate(contexts)
    fallback = evaluator.evaluate(payload)
    context_updates = fallback.context_updates | workbook_result.context_updates
    fallback_sheet = fallback.context_updates.get("spreadsheet")
    workbook_sheet = workbook_result.context_updates.get("spreadsheet")
    if isinstance(fallback_sheet, dict) and isinstance(workbook_sheet, dict):
        context_updates["spreadsheet"] = fallback_sheet | workbook_sheet
    global_updates = fallback.global_updates | workbook_result.global_updates
    spreadsheet = context_updates.get("spreadsheet", {})
    ok = bool(spreadsheet.get("master_result", fallback.ok)) if isinstance(spreadsheet, dict) else fallback.ok
    return EvaluateResponse(
        ok=ok,
        context_updates=context_updates,
        global_updates=global_updates,
        control=workbook_result.control,
    )


@router.get("/api/projects", response_model=list[ProjectRecord])
def list_projects() -> list[ProjectRecord]:
    """Vr?t? registrovan? PEKAT/demo projekty pro UI."""

    return store.list_projects()


@router.get("/api/demo/state", response_model=DemoStateResponse)
def get_demo_state() -> dict[str, object]:
    """Vr?t? aktu?ln? stav offline PEKAT simulatoru."""

    return demo_simulator.state()


@router.post("/api/demo/tick", response_model=DemoStateResponse)
def tick_demo() -> dict[str, object]:
    """Vygeneruje dal?? demo frame pro v?echny kamery."""

    return demo_simulator.tick()


@router.post("/api/demo/reset", response_model=DemoStateResponse)
def reset_demo() -> dict[str, object]:
    """Resetuje offline demo data do v?choz?ho stavu."""

    return demo_simulator.reset()


@router.get("/api/workbooks/default", response_model=Workbook)
def get_default_workbook() -> Workbook:
    """Vr?t? default workbook pro spreadsheet UI."""
    return workbook_service.get_default()

@router.put("/api/workbooks/default", response_model=Workbook)
def put_default_workbook(payload: Workbook) -> Workbook:
    """Ulo?? default workbook konfiguraci."""
    return workbook_service.replace_default(payload)

@router.post("/api/workbooks/default/evaluate", response_model=WorkbookEvaluateResponse)
def evaluate_default_workbook(payload: WorkbookEvaluateRequest) -> WorkbookEvaluateResponse:
    """Vyhodnot? workbook nad dodan?mi PEKAT contexty."""
    return workbook_service.evaluate(payload.contexts)

@router.post("/api/workbooks/default/bindings", response_model=Workbook)
def add_workbook_binding(payload: CellBinding) -> Workbook:
    """P?id? Context?cell binding."""
    return workbook_service.add_binding(payload)

@router.post("/api/workbooks/default/output-mappings", response_model=Workbook)
def add_workbook_output_mapping(payload: OutputMapping) -> Workbook:
    """P?id? cell?Context/GlobalData mapping."""
    return workbook_service.add_output_mapping(payload)

@router.get("/api/context/{project_id}/tree")
def get_context_tree(project_id: str) -> dict[str, object]:
    """Vr?t? posledn? zn?m? demo/PEKAT Context jako strom pro drag-and-drop."""
    snapshot = store.get_last_snapshot(project_id)
    if snapshot is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Projekt {project_id!r} zat?m nem? Context snapshot.",
        )
    return {
        "project_id": project_id,
        "frame_id": snapshot.frame_id,
        "tree": {"context": snapshot.context, "global_data": snapshot.global_data},
    }

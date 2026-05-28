"""REST API routy pro MVP PEKAT Easysheet backend."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, status

from backend.app.core.evaluator import SpreadsheetEvaluator
from backend.app.core.storage import MemoryStore
from backend.app.demo.simulator import DemoSimulator
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
    """Ulo?? snapshot a vr?t? deterministick? MVP v?sledek."""

    store.save_snapshot(payload)
    return evaluator.evaluate(payload)


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

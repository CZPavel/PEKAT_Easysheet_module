"""REST API routy pro MVP PEKAT Easysheet backend."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, status

from backend.app.core.evaluator import SpreadsheetEvaluator
from backend.app.core.storage import MemoryStore
from backend.app.models import (
    EvaluateRequest,
    EvaluateResponse,
    HealthResponse,
    ProjectRecord,
    ProjectRegistration,
    SnapshotIn,
    SnapshotRecord,
)

router = APIRouter()
store = MemoryStore()
evaluator = SpreadsheetEvaluator()


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

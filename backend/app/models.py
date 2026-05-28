"""Pydantic modely pro MVP REST API.

Modely dr?? datov? kontrakty mal? a ?iteln?. V dal?? f?zi je mo?n? je
roz???it o persistenci, audit a verze workbook? bez zm?ny hlavn?ho toku.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Literal

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    """Odpov?? health endpointu pro rychlou diagnostiku backendu."""

    status: Literal["ok"] = "ok"
    service: str = "pekat-easysheet-backend"
    version: str = "0.1.0"


class ProjectRegistration(BaseModel):
    """Registrace jedn? PEKAT instance nebo logick? kamery."""

    project_id: str = Field(min_length=1, examples=["Camera_1"])
    name: str | None = Field(default=None, examples=["Left camera"])
    ip: str = Field(default="127.0.0.1")
    port: int | None = Field(default=None, ge=1, le=65535)
    role: str = Field(default="inspection_camera")


class ProjectRecord(ProjectRegistration):
    """Ulo?en? projekt dopln?n? o ?as registrace."""

    registered_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )


class SnapshotIn(BaseModel):
    """Snapshot dat z PEKAT Context/GlobalData pro jeden frame."""

    project_id: str = Field(min_length=1)
    frame_id: str = Field(min_length=1)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    context: dict[str, Any] = Field(default_factory=dict)
    global_data: dict[str, Any] = Field(default_factory=dict)


class SnapshotRecord(SnapshotIn):
    """Ulo?en? snapshot s ?asem p??jmu backendem."""

    received_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class EvaluateRequest(SnapshotIn):
    """Po?adavek na synchronn? nebo cached vyhodnocen?."""

    mode: Literal["sync", "cached"] = "sync"


class ControlResponse(BaseModel):
    """??dic? ??st odpov?di pro PEKAT Code bridge."""

    exit: bool = False
    override_result: bool | None = None


class EvaluateResponse(BaseModel):
    """V?sledek evaluace ur?en? pro z?pis do Context/GlobalData."""

    ok: bool
    context_updates: dict[str, Any] = Field(default_factory=dict)
    global_updates: dict[str, Any] = Field(default_factory=dict)
    control: ControlResponse = Field(default_factory=ControlResponse)

"""Offline PEKAT simulator pro n?hled aplikace bez PEKAT runtime.

Simulator generuje deterministick? demo data pro n?kolik kamer. Ka?d? tick
vytvo?? snapshot podobn? PEKAT Contextu, ulo?? ho p?es backend store a nech? ho
vyhodnotit stejn?m evalu?torem jako re?ln? Code bridge.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from threading import RLock
from typing import Any

from backend.app.core.evaluator import SpreadsheetEvaluator
from backend.app.core.storage import MemoryStore
from backend.app.models import EvaluateRequest, ProjectRegistration


@dataclass
class DemoCamera:
    """Stav jedn? simulovan? PEKAT kamery."""

    project_id: str
    name: str
    frame_index: int = 0
    last_snapshot: dict[str, Any] | None = None
    last_evaluation: dict[str, Any] | None = None


@dataclass
class DemoState:
    """Kompletn? stav offline demo re?imu."""

    running: bool = False
    tick_index: int = 0
    cameras: list[DemoCamera] = field(default_factory=list)


class DemoSimulator:
    """Gener?tor PEKAT-like snapshot? pro UI demo."""

    def __init__(self, store: MemoryStore, evaluator: SpreadsheetEvaluator) -> None:
        self._store = store
        self._evaluator = evaluator
        self._lock = RLock()
        self._state = self._new_state()
        self._register_demo_projects()

    def state(self) -> dict[str, Any]:
        """Vr?t? serializovateln? stav demo re?imu."""

        with self._lock:
            return self._state_to_dict()

    def reset(self) -> dict[str, Any]:
        """Vr?t? simulator do po??te?n?ho stavu."""

        with self._lock:
            self._state = self._new_state()
            self._register_demo_projects()
            return self._state_to_dict()

    def tick(self) -> dict[str, Any]:
        """Vygeneruje jeden cyklus pro v?echny demo kamery."""

        with self._lock:
            self._state.running = True
            self._state.tick_index += 1
            for camera in self._state.cameras:
                self._tick_camera(camera)
            return self._state_to_dict()

    def _new_state(self) -> DemoState:
        """Vytvo?? v?choz? sadu kamer."""

        return DemoState(
            cameras=[
                DemoCamera("Camera_1", "Left camera"),
                DemoCamera("Camera_2", "Right camera"),
                DemoCamera("Coordinator", "Coordinator sheet"),
            ]
        )

    def _register_demo_projects(self) -> None:
        """Zaregistruje demo kamery do b??n?ho backend store."""

        for camera in self._state.cameras:
            self._store.register_project(
                ProjectRegistration(
                    project_id=camera.project_id,
                    name=camera.name,
                    ip="127.0.0.1",
                    port=8000,
                    role="demo_camera"
                    if camera.project_id != "Coordinator"
                    else "coordinator",
                )
            )

    def _tick_camera(self, camera: DemoCamera) -> None:
        """Vytvo?? snapshot a evaluaci pro jednu kameru."""

        camera.frame_index += 1
        ok = self._calculate_ok(camera.project_id, camera.frame_index)
        frame_id = f"{camera.project_id}_{camera.frame_index:06d}"
        snapshot = self._build_snapshot(camera, frame_id, ok)
        request = EvaluateRequest(**snapshot)
        evaluation = self._evaluator.evaluate(request)
        self._store.save_snapshot(request)
        camera.last_snapshot = snapshot
        camera.last_evaluation = evaluation.model_dump(mode="json")

    def _calculate_ok(self, project_id: str, frame_index: int) -> bool:
        """Deterministicky st??d? OK/NG pro demo bez n?hodnosti."""

        if project_id == "Coordinator":
            return frame_index % 5 != 0
        return (frame_index + len(project_id)) % 4 != 0

    def _build_snapshot(
        self, camera: DemoCamera, frame_id: str, ok: bool
    ) -> dict[str, Any]:
        """Sestav? PEKAT-like snapshot s m??en?mi a detekcemi."""

        confidence = round(0.72 + ((camera.frame_index % 7) * 0.035), 3)
        diameter = round(12.0 + ((camera.frame_index % 5) - 2) * 0.08, 3)
        label = "Screw" if ok else "Defect"
        return {
            "project_id": camera.project_id,
            "frame_id": frame_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "mode": "sync",
            "context": {
                "result": ok,
                "completeTime": round(38.0 + camera.frame_index * 0.7, 2),
                "detectedRectangles": [
                    {
                        "label": label,
                        "confidence": confidence,
                        "x": 120 + camera.frame_index,
                        "y": 80 + camera.frame_index,
                        "w": 42,
                        "h": 36,
                        "detectedAsLast": True,
                    }
                ],
                "measurements": {
                    "diameter_mm": diameter,
                    "diameter_ok": 11.8 <= diameter <= 12.2,
                },
                "operatorInput": {"recipe_request": "A"},
            },
            "global_data": {
                "recipe": {"active_id": "A", "name": "Demo recipe A"},
                "spreadsheet": {
                    "mode": "sync",
                    "sheet_version": "0.1.0-demo",
                },
            },
        }

    def _state_to_dict(self) -> dict[str, Any]:
        """Serializuje stav pro REST API a React UI."""

        return {
            "running": self._state.running,
            "tick_index": self._state.tick_index,
            "cameras": [
                {
                    "project_id": camera.project_id,
                    "name": camera.name,
                    "frame_index": camera.frame_index,
                    "last_snapshot": camera.last_snapshot,
                    "last_evaluation": camera.last_evaluation,
                }
                for camera in self._state.cameras
            ],
        }

"""Jednoduch? in-memory ?lo?i?t? pro MVP.

T??da m? mal? metody, aby ?la pozd?ji nahradit SQLite implementac? bez zm?ny
API vrstvy. Pro produkci bude pot?eba doplnit persistenci a auditn? log.
"""

from __future__ import annotations

from threading import RLock

from backend.app.models import ProjectRecord, ProjectRegistration, SnapshotIn, SnapshotRecord


class MemoryStore:
    """Thread-safe pam??ov? ?lo?i?t? projekt? a posledn?ch snapshot?."""

    def __init__(self) -> None:
        # Lock chr?n? z?pis p?i paraleln?ch HTTP po?adavc?ch.
        self._lock = RLock()
        self._projects: dict[str, ProjectRecord] = {}
        self._last_snapshot: dict[str, SnapshotRecord] = {}

    def register_project(self, payload: ProjectRegistration) -> ProjectRecord:
        """Ulo?? nebo p?ep??e registraci PEKAT projektu."""

        record = ProjectRecord(**payload.model_dump())
        with self._lock:
            self._projects[record.project_id] = record
        return record

    def list_projects(self) -> list[ProjectRecord]:
        """Vr?t? v?echny registrovan? projekty se?azen? podle ID."""

        with self._lock:
            return [self._projects[key] for key in sorted(self._projects)]

    def get_project(self, project_id: str) -> ProjectRecord | None:
        """Vr?t? projekt, pokud byl registrov?n."""

        with self._lock:
            return self._projects.get(project_id)

    def save_snapshot(self, payload: SnapshotIn) -> SnapshotRecord:
        """Ulo?? posledn? zn?m? snapshot pro dan? projekt."""

        record = SnapshotRecord(**payload.model_dump())
        with self._lock:
            self._last_snapshot[record.project_id] = record
        return record

    def get_last_snapshot(self, project_id: str) -> SnapshotRecord | None:
        """Vr?t? posledn? ulo?en? snapshot pro projekt."""

        with self._lock:
            return self._last_snapshot.get(project_id)

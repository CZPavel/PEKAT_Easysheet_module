"""Aplika?n? evaluator pro p?evod PEKAT snapshotu na bridge odpov??."""

from __future__ import annotations

from datetime import datetime, timezone

from backend.app.formula.engine import FormulaEngine
from backend.app.models import EvaluateRequest, EvaluateResponse


class SpreadsheetEvaluator:
    """MVP evalu?tor p?ipraven? na pozd?j?? workbook/formula engine."""

    def __init__(self, formula_engine: FormulaEngine | None = None) -> None:
        self._formula_engine = formula_engine or FormulaEngine()

    def evaluate(self, payload: EvaluateRequest) -> EvaluateResponse:
        """Vyhodnot? snapshot a sestav? odpov?? pro PEKAT Code bridge."""

        master_result = self._formula_engine.evaluate_master_result(payload.context)
        updated_at = datetime.now(timezone.utc).isoformat()
        spreadsheet_state = {
            "project_id": payload.project_id,
            "frame_id": payload.frame_id,
            "mode": payload.mode,
            "last_update_ts": updated_at,
            "result": master_result,
            "reason": "MVP_MASTER_RESULT",
            "outputs": {
                "master_result": master_result,
                "allow_branch_default": master_result,
            },
        }
        return EvaluateResponse(
            ok=master_result,
            context_updates={"spreadsheet": spreadsheet_state},
            global_updates={"spreadsheet": spreadsheet_state},
        )

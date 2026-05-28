"""In-memory workbook slu?ba a vyhodnocen? mapov?n?."""
from __future__ import annotations
from copy import deepcopy
from datetime import datetime, timezone
from typing import Any
from backend.app.formula.engine import FormulaEngine, MISSING
from backend.app.workbook.models import Cell, CellBinding, OutputMapping, Recipe, Sheet, Workbook, WorkbookEvaluateResponse

class WorkbookService:
    """Spravuje default workbook pro prvn? spreadsheet mapping MVP."""
    def __init__(self, formula_engine: FormulaEngine | None = None) -> None:
        self._formula_engine = formula_engine or FormulaEngine()
        self._workbook = self._create_default_workbook()

    def get_default(self) -> Workbook:
        """Vr?t? kopii default workbooku."""
        return deepcopy(self._workbook)

    def replace_default(self, workbook: Workbook) -> Workbook:
        """Nahrad? default workbook novou konfigurac?."""
        workbook.updated_at = datetime.now(timezone.utc)
        self._workbook = deepcopy(workbook)
        return self.get_default()

    def add_binding(self, binding: CellBinding) -> Workbook:
        """P?id? nebo aktualizuje Context?cell binding."""
        formula = binding.formula or f'=PV("{binding.source_path}")'
        self._set_cell(binding.sheet_name, binding.cell, formula)
        self._workbook.bindings = [item for item in self._workbook.bindings if not (item.sheet_name == binding.sheet_name and item.cell == binding.cell)]
        self._workbook.bindings.append(binding.model_copy(update={"formula": formula}))
        self._workbook.updated_at = datetime.now(timezone.utc)
        return self.get_default()

    def add_output_mapping(self, mapping: OutputMapping) -> Workbook:
        """P?id? nebo aktualizuje cell?Context/GlobalData mapping."""
        self._workbook.output_mappings = [item for item in self._workbook.output_mappings if not (item.sheet_name == mapping.sheet_name and item.cell == mapping.cell)]
        self._workbook.output_mappings.append(mapping)
        self._workbook.updated_at = datetime.now(timezone.utc)
        return self.get_default()

    def evaluate(self, contexts: dict[str, dict[str, Any]]) -> WorkbookEvaluateResponse:
        """Vyhodnot? workbook a aplikuje output mappingy."""
        workbook = self.get_default()
        workbook_values: dict[str, dict[str, Any]] = {}
        for sheet in workbook.sheets:
            local_values: dict[str, Any] = {}
            for address in sorted(sheet.cells):
                cell = sheet.cells[address]
                try:
                    visible_values = {**local_values}
                    for name, values in workbook_values.items():
                        visible_values.update({f"{name}!{key}": value for key, value in values.items()})
                    value = self._formula_engine.evaluate_formula(cell.raw, contexts, visible_values)
                    cell.value = value
                    cell.status = "missing" if value == MISSING else "ok"
                    cell.error = None
                except Exception as exc:  # noqa: BLE001
                    cell.value = "#ERROR"
                    cell.status = "error"
                    cell.error = f"{type(exc).__name__}: {exc}"
                local_values[address] = cell.value
            workbook_values[sheet.name] = local_values
        context_updates: dict[str, Any] = {}
        global_updates: dict[str, Any] = {}
        control: dict[str, Any] = {"exit": False, "override_result": None}
        for mapping in workbook.output_mappings:
            value = workbook_values.get(mapping.sheet_name, {}).get(mapping.cell, MISSING)
            if mapping.target_type == "context":
                self._assign_path(context_updates, mapping.target, value)
            elif mapping.target_type == "global_data":
                self._assign_path(global_updates, mapping.target, value)
            else:
                control[mapping.target] = value
        return WorkbookEvaluateResponse(workbook=workbook, context_updates=context_updates, global_updates=global_updates, control=control)

    def _set_cell(self, sheet_name: str, address: str, raw: str) -> None:
        sheet = self._find_sheet(sheet_name)
        sheet.cells[address] = Cell(address=address, raw=raw)

    def _find_sheet(self, sheet_name: str) -> Sheet:
        for sheet in self._workbook.sheets:
            if sheet.name == sheet_name:
                return sheet
        sheet = Sheet(name=sheet_name)
        self._workbook.sheets.append(sheet)
        return sheet

    def _assign_path(self, root: dict[str, Any], target: str, value: Any) -> None:
        parts = target.split(".")
        current = root
        for part in parts[:-1]:
            current = current.setdefault(part, {})
        current[parts[-1]] = value

    def _create_default_workbook(self) -> Workbook:
        workbook = Workbook(
            sheets=[Sheet(name=name) for name in ["Camera_1", "Camera_2", "Coordinator", "Recipes", "Outputs"]],
            recipes=[Recipe(recipe_id="A", parameters={"min_diameter_mm": 11.8, "max_diameter_mm": 12.2})],
            bindings=[
                CellBinding(sheet_name="Camera_1", cell="B2", source_path="Camera_1.context.result", formula='=PV("Camera_1.context.result")'),
                CellBinding(sheet_name="Camera_1", cell="B3", source_path="Camera_1.context.measurements.diameter_mm", formula='=PV("Camera_1.context.measurements.diameter_mm")'),
                CellBinding(sheet_name="Camera_2", cell="B2", source_path="Camera_2.context.result", formula='=PV("Camera_2.context.result")'),
            ],
            output_mappings=[
                OutputMapping(sheet_name="Coordinator", cell="B2", target="spreadsheet.master_result", target_type="context"),
                OutputMapping(sheet_name="Coordinator", cell="B3", target="spreadsheet.allow_branch_default", target_type="context"),
                OutputMapping(sheet_name="Coordinator", cell="B4", target="spreadsheet.reject_reason", target_type="global_data"),
            ],
        )
        for sheet in workbook.sheets:
            if sheet.name == "Camera_1":
                sheet.cells = {
                    "A1": Cell(address="A1", raw="Camera_1 inputs"),
                    "A2": Cell(address="A2", raw="PEKAT result"),
                    "B2": Cell(address="B2", raw='=PV("Camera_1.context.result")'),
                    "A3": Cell(address="A3", raw="Diameter mm"),
                    "B3": Cell(address="B3", raw='=PV("Camera_1.context.measurements.diameter_mm")'),
                    "A4": Cell(address="A4", raw="Screw count"),
                    "B4": Cell(address="B4", raw='=PV_COUNT("Camera_1", "Screw")'),
                }
            elif sheet.name == "Camera_2":
                sheet.cells = {
                    "A1": Cell(address="A1", raw="Camera_2 inputs"),
                    "A2": Cell(address="A2", raw="PEKAT result"),
                    "B2": Cell(address="B2", raw='=PV("Camera_2.context.result")'),
                    "A3": Cell(address="A3", raw="Defect exists"),
                    "B3": Cell(address="B3", raw='=PV_EXISTS("Camera_2", "Defect")'),
                }
            elif sheet.name == "Coordinator":
                sheet.cells = {
                    "A1": Cell(address="A1", raw="Coordinator outputs"),
                    "A2": Cell(address="A2", raw="Master result"),
                    "B2": Cell(address="B2", raw="=AND(Camera_1!B2, Camera_2!B2)"),
                    "A3": Cell(address="A3", raw="Allow branch"),
                    "B3": Cell(address="B3", raw="=IF(B2, TRUE, FALSE)"),
                    "A4": Cell(address="A4", raw="Reject reason"),
                    "B4": Cell(address="B4", raw='=IF(B2, "OK", "MASTER_NG")'),
                }
            elif sheet.name == "Recipes":
                sheet.cells = {"A1": Cell(address="A1", raw="recipe_id"), "B1": Cell(address="B1", raw="A"), "A2": Cell(address="A2", raw="min_diameter_mm"), "B2": Cell(address="B2", raw=11.8), "A3": Cell(address="A3", raw="max_diameter_mm"), "B3": Cell(address="B3", raw=12.2)}
            elif sheet.name == "Outputs":
                sheet.cells = {"A1": Cell(address="A1", raw="cell"), "B1": Cell(address="B1", raw="target"), "A2": Cell(address="A2", raw="Coordinator!B2"), "B2": Cell(address="B2", raw="context.spreadsheet.master_result")}
        return workbook

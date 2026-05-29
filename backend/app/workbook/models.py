"""Datov? modely workbooku pro PEKAT Easysheet."""
from __future__ import annotations
from datetime import datetime, timezone
from typing import Any, Literal
from pydantic import BaseModel, Field

CellValue = str | int | float | bool | None

class Cell(BaseModel):
    """Jedna spreadsheet bu?ka s hodnotou nebo vzorcem."""
    address: str = Field(pattern=r"^[A-Z]+[1-9][0-9]*$")
    raw: str | CellValue = ""
    value: CellValue = None
    status: Literal["ok", "missing", "error"] = "ok"
    error: str | None = None

class Sheet(BaseModel):
    """Z?lo?ka workbooku odpov?daj?c? PEKAT instanci."""
    name: str
    rows: int = 50
    cols: int = 26
    cells: dict[str, Cell] = Field(default_factory=dict)

class CellBinding(BaseModel):
    """Mapov?n? hodnoty z PEKAT Context/GlobalData do bu?ky."""
    sheet_name: str
    cell: str = Field(pattern=r"^[A-Z]+[1-9][0-9]*$")
    source_path: str
    formula: str | None = None

class OutputMapping(BaseModel):
    """Mapov?n? v?sledn? bu?ky zp?t do Context nebo GlobalData."""
    sheet_name: str
    cell: str = Field(pattern=r"^[A-Z]+[1-9][0-9]*$")
    target: str
    target_type: Literal["context", "global_data", "control"] = "context"

class Recipe(BaseModel):
    """Verzovateln? receptura pou?iteln? ve spreadsheetu."""
    recipe_id: str
    version: int = 1
    parameters: dict[str, Any] = Field(default_factory=dict)

class Workbook(BaseModel):
    """Kompletn? konfigurace Easysheet workbooku."""
    workbook_id: str = "default"
    version: str = "0.2.0"
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    sheets: list[Sheet] = Field(default_factory=list)
    bindings: list[CellBinding] = Field(default_factory=list)
    output_mappings: list[OutputMapping] = Field(default_factory=list)
    recipes: list[Recipe] = Field(default_factory=list)

class WorkbookEvaluateRequest(BaseModel):
    """Po?adavek na vyhodnocen? workbooku nad contexty projekt?."""
    contexts: dict[str, dict[str, Any]] = Field(default_factory=dict)

class WorkbookEvaluateResponse(BaseModel):
    """V?sledek vyhodnocen? workbooku v?etn? write-back mapov?n?."""
    workbook: Workbook
    context_updates: dict[str, Any] = Field(default_factory=dict)
    global_updates: dict[str, Any] = Field(default_factory=dict)
    control: dict[str, Any] = Field(default_factory=dict)

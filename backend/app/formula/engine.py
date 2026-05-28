"""Bezpe?n? minim?ln? formula runtime pro MVP.

Runtime nepou??v? `eval()` ani u?ivatelsk? Python/JavaScript. Podporuje mal?
auditovateln? subset funkc? pot?ebn? pro PEKAT Context bindingy.
"""
from __future__ import annotations
import re
from typing import Any

MISSING = "#MISSING"

class FormulaError(ValueError):
    """Chyba p?i vyhodnocen? omezen? formule."""

class FormulaEngine:
    """Deterministick? evaluator pro jednoduch? spreadsheet v?razy."""
    TRUE_VALUES = {"TRUE", "OK", "PASS", "1"}
    FALSE_VALUES = {"FALSE", "NG", "FAIL", "0"}

    def evaluate_literal(self, value: Any) -> bool | int | float | str | None:
        """Vr?t? bezpe?n? interpretovanou literal hodnotu."""
        if value is None or isinstance(value, (bool, int, float)):
            return value
        if not isinstance(value, str):
            raise FormulaError(f"Nepodporovan? typ formule: {type(value).__name__}")
        normalized = value.strip()
        upper = normalized.upper()
        if upper in self.TRUE_VALUES:
            return True
        if upper in self.FALSE_VALUES:
            return False
        if (normalized.startswith('"') and normalized.endswith('"')) or (normalized.startswith("'") and normalized.endswith("'")):
            return normalized[1:-1]
        try:
            if "." in normalized:
                return float(normalized)
            return int(normalized)
        except ValueError:
            return normalized

    def evaluate_master_result(self, context: dict[str, Any]) -> bool:
        """Spo??t? deterministick? master OK/NG v?sledek z Contextu."""
        return bool(self.evaluate_literal(context.get("result", True)))

    def evaluate_formula(self, raw: Any, contexts: dict[str, dict[str, Any]], cells: dict[str, Any] | None = None) -> Any:
        """Vyhodnot? hodnotu nebo vzorec nad contexty projekt?."""
        if not isinstance(raw, str) or not raw.startswith("="):
            return self.evaluate_literal(raw)
        return self._eval_expr(raw[1:].strip(), contexts, cells or {})

    def _eval_expr(self, expr: str, contexts: dict[str, dict[str, Any]], cells: dict[str, Any]) -> Any:
        expr = expr.strip()
        sheet_ref = re.match(r"^[A-Za-z0-9_]+!([A-Z]+[1-9][0-9]*)$", expr)
        if sheet_ref:
            return cells.get(expr, cells.get(sheet_ref.group(1), MISSING))
        for operator in (">=", "<=", "!=", "=", ">", "<"):
            parts = self._split_operator(expr, operator)
            if parts is not None:
                return self._compare(self._eval_expr(parts[0], contexts, cells), self._eval_expr(parts[1], contexts, cells), operator)
        match = re.match(r"^([A-Za-z_][A-Za-z0-9_]*)\((.*)\)$", expr)
        if match:
            name = match.group(1).upper()
            args = self._split_args(match.group(2))
            values = [self._eval_expr(arg, contexts, cells) for arg in args]
            return self._call(name, values, contexts)
        if re.match(r"^[A-Z]+[1-9][0-9]*$", expr):
            return cells.get(expr, MISSING)
        return self.evaluate_literal(expr)

    def _call(self, name: str, values: list[Any], contexts: dict[str, dict[str, Any]]) -> Any:
        if name == "PV":
            return self._pv(str(values[0]), contexts) if values else MISSING
        if name == "PV_COUNT":
            return self._pv_count(str(values[0]), str(values[1]), contexts) if len(values) >= 2 else MISSING
        if name == "PV_EXISTS":
            return self._pv_count(str(values[0]), str(values[1]), contexts) > 0 if len(values) >= 2 else False
        if name == "IF":
            return values[1] if len(values) >= 2 and bool(values[0]) else (values[2] if len(values) >= 3 else False)
        if name == "AND":
            return all(bool(value) for value in values)
        if name == "OR":
            return any(bool(value) for value in values)
        if name == "NOT":
            return not bool(values[0]) if values else True
        if name == "ABS":
            return abs(float(values[0])) if values else MISSING
        if name == "ROUND":
            precision = int(values[1]) if len(values) > 1 else 0
            return round(float(values[0]), precision) if values else MISSING
        if name in {"MIN", "MAX", "SUM", "AVERAGE"}:
            nums = [float(value) for value in values if isinstance(value, (int, float))]
            if not nums:
                return MISSING
            if name == "MIN":
                return min(nums)
            if name == "MAX":
                return max(nums)
            if name == "SUM":
                return sum(nums)
            return sum(nums) / len(nums)
        raise FormulaError(f"Nepodporovan? funkce: {name}")

    def _pv(self, path: str, contexts: dict[str, dict[str, Any]]) -> Any:
        parts = path.split(".")
        if len(parts) < 2:
            return MISSING
        current: Any = contexts.get(parts[0])
        for part in parts[1:]:
            if current is None:
                return MISSING
            if isinstance(current, dict):
                current = current.get(part)
            elif isinstance(current, list) and part.isdigit():
                index = int(part)
                current = current[index] if index < len(current) else None
            else:
                return MISSING
        return current if current is not None else MISSING

    def _pv_count(self, project_id: str, label: str, contexts: dict[str, dict[str, Any]]) -> int:
        rectangles = contexts.get(project_id, {}).get("context", {}).get("detectedRectangles", [])
        if not isinstance(rectangles, list):
            return 0
        return sum(1 for item in rectangles if isinstance(item, dict) and item.get("label") == label)

    def _split_args(self, text: str) -> list[str]:
        args: list[str] = []
        current: list[str] = []
        depth = 0
        quote: str | None = None
        for char in text:
            if quote:
                current.append(char)
                if char == quote:
                    quote = None
                continue
            if char in {'"', "'"}:
                quote = char
                current.append(char)
            elif char == "(":
                depth += 1
                current.append(char)
            elif char == ")":
                depth -= 1
                current.append(char)
            elif char == "," and depth == 0:
                args.append("".join(current).strip())
                current = []
            else:
                current.append(char)
        if current or text.strip():
            args.append("".join(current).strip())
        return args

    def _split_operator(self, expr: str, operator: str) -> tuple[str, str] | None:
        depth = 0
        quote: str | None = None
        i = 0
        while i < len(expr):
            char = expr[i]
            if quote:
                if char == quote:
                    quote = None
            elif char in {'"', "'"}:
                quote = char
            elif char == "(":
                depth += 1
            elif char == ")":
                depth -= 1
            elif depth == 0 and expr.startswith(operator, i):
                return expr[:i].strip(), expr[i + len(operator):].strip()
            i += 1
        return None

    def _compare(self, left: Any, right: Any, operator: str) -> bool:
        if MISSING in {left, right}:
            return False
        if operator == "=":
            return left == right
        if operator == "!=":
            return left != right
        try:
            left_value: Any = float(left)
            right_value: Any = float(right)
        except (TypeError, ValueError):
            left_value = str(left)
            right_value = str(right)
        if operator == ">=":
            return left_value >= right_value
        if operator == "<=":
            return left_value <= right_value
        if operator == ">":
            return left_value > right_value
        if operator == "<":
            return left_value < right_value
        return False

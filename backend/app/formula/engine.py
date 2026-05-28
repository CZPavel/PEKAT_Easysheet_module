"""Bezpe?n? minim?ln? formula runtime pro MVP.

Tento modul z?m?rn? nespou?t? `eval()` ani u?ivatelsk? Python. Prvn? verze
um? pouze deterministicky p?ev?st literal hodnoty a spo??tat z?kladn? logiku,
co? je bezpe?n? z?klad pro budouc? AST/DSL parser.
"""

from __future__ import annotations

from typing import Any


class FormulaError(ValueError):
    """Chyba p?i vyhodnocen? omezen? formule."""


class FormulaEngine:
    """Mal? evaluator pro smoke testy a prvn? backend odpov??."""

    TRUE_VALUES = {"TRUE", "OK", "PASS", "1"}
    FALSE_VALUES = {"FALSE", "NG", "FAIL", "0"}

    def evaluate_literal(self, value: Any) -> bool | int | float | str | None:
        """Vr?t? bezpe?n? interpretovanou literal hodnotu.

        Vstupem m??e b?t boolean, ??slo, `None` nebo text. Textov? hodnoty typu
        `TRUE`/`FALSE` se mapuj? na boolean. ??seln? text se p?evede na ??slo.
        """

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

        try:
            if "." in normalized:
                return float(normalized)
            return int(normalized)
        except ValueError:
            return normalized

    def evaluate_master_result(self, context: dict[str, Any]) -> bool:
        """Spo??t? prvn? deterministick? master OK/NG v?sledek.

        Priorita je jednoduch?: pokud m? PEKAT context kl?? `result`, p?evezme
        se jeho boolean interpretace. Jinak je v?choz? stav bezpe?n? `True`,
        aby MVP bez dat neukon?ovalo v?tev omylem.
        """

        raw_result = context.get("result", True)
        evaluated = self.evaluate_literal(raw_result)
        return bool(evaluated)

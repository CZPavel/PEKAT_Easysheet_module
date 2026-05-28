import pytest

from backend.app.formula.engine import FormulaEngine, FormulaError


def test_formula_engine_boolean_and_number_literals():
    engine = FormulaEngine()
    assert engine.evaluate_literal("TRUE") is True
    assert engine.evaluate_literal("NG") is False
    assert engine.evaluate_literal("12") == 12
    assert engine.evaluate_literal("12.5") == 12.5


def test_formula_engine_rejects_unknown_object_type():
    engine = FormulaEngine()
    with pytest.raises(FormulaError):
        engine.evaluate_literal(object())


def test_master_result_defaults_to_true_when_context_has_no_result():
    engine = FormulaEngine()
    assert engine.evaluate_master_result({}) is True

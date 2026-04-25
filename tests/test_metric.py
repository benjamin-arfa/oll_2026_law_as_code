"""Tests for the code quality metric."""

from types import SimpleNamespace

from oll_law_as_code.metric import code_quality_metric


def _make_prediction(code: str, yaml_text: str = "", reasoning: str = "test"):
    return SimpleNamespace(openfisca_variable=code, parameter_yaml=yaml_text, reasoning=reasoning)


def _make_example(code: str = "", ref: str = "Test"):
    return SimpleNamespace(openfisca_variable=code, article_reference=ref)


GOOD_CODE = """\
from openfisca_core.model_api import *
from openfisca_switzerland.entities import Person

class test_metric_var(Variable):
    value_type = float
    entity = Person
    definition_period = MONTH
    label = "Test variable"

    def formula(person, period):
        return person("gross_monthly_salary", period) * 0.5
"""

GOOD_YAML = """\
description: Test
metadata:
  reference:
    - title: "Test"
values:
  2024-01-01:
    value: 0.5
"""

BOOL_CODE = """\
from openfisca_core.model_api import *
from openfisca_switzerland.entities import Person

class test_bool_var(Variable):
    value_type = bool
    entity = Person
    definition_period = YEAR
    label = "Test bool"

    def formula(person, period):
        return person("has_unlawful_act", period) * person("has_damage", period) > 0
"""


class TestMetricStructuralChecks:
    def test_unparseable_python_scores_low(self):
        pred = _make_prediction("class Broken(", "bad: yaml: [")
        score = code_quality_metric(_make_example(), pred)
        assert score < 0.1

    def test_good_code_scores_structural_points(self):
        pred = _make_prediction(GOOD_CODE, GOOD_YAML)
        score = code_quality_metric(_make_example(GOOD_CODE), pred)
        # Should get at least structural points: parse(0.20) + yaml(0.15) + 5 checks(0.25) = 0.60
        assert score >= 0.55

    def test_value_type_check_gives_points(self):
        code_with_type = "class X(Variable):\n    value_type = bool\n    def formula(x, p): pass\n    definition_period = YEAR"
        pred = _make_prediction(code_with_type, "x:\n  values:\n    2024-01-01:\n      value: 1")
        score = code_quality_metric(_make_example(), pred)
        assert score >= 0.25  # At least several structural checks pass

    def test_missing_formula_loses_points(self):
        code_no_formula = "class X(Variable):\n    value_type = bool\n    definition_period = YEAR"
        pred = _make_prediction(code_no_formula, GOOD_YAML)
        score_no = code_quality_metric(_make_example(), pred)

        pred_with = _make_prediction(GOOD_CODE, GOOD_YAML)
        score_with = code_quality_metric(_make_example(), pred_with)
        assert score_with > score_no


class TestMetricBooleanHandling:
    def test_bool_code_detected(self):
        pred = _make_prediction(BOOL_CODE, GOOD_YAML)
        score = code_quality_metric(_make_example(BOOL_CODE), pred)
        # Should get structural + execution points
        assert score >= 0.5


class TestMetricBootstrapMode:
    def test_trace_returns_bool(self):
        pred = _make_prediction(GOOD_CODE, GOOD_YAML)
        result = code_quality_metric(_make_example(GOOD_CODE), pred, trace="bootstrap")
        assert isinstance(result, bool)


# ── Edge case tests (TODO 9c) ────────────────────────────────────────────────

# Code that loads into TBS but fails at simulation due to referencing
# a variable that doesn't exist in the system.
LOADS_BUT_FAILS_SIMULATE = """\
from openfisca_core.model_api import *
from openfisca_switzerland.entities import Person

class test_fails_simulate_var(Variable):
    value_type = float
    entity = Person
    definition_period = MONTH
    label = "References a nonexistent variable"

    def formula(person, period):
        return person("totally_nonexistent_variable_xyz", period) * 2
"""

# Code that simulates but produces the wrong value (0.0 instead of expected).
WRONG_VALUE_CODE = """\
from openfisca_core.model_api import *
from openfisca_switzerland.entities import Person

class test_wrong_value_var(Variable):
    value_type = float
    entity = Person
    definition_period = MONTH
    label = "Always returns zero"

    def formula(person, period):
        return person("gross_monthly_salary", period) * 0
"""


class TestMetricEdgeCases:
    def test_loads_but_fails_simulate_gets_partial_score(self):
        """Code that loads into TBS but fails at calculation gets load points but not run points."""
        pred = _make_prediction(LOADS_BUT_FAILS_SIMULATE, GOOD_YAML)
        score = code_quality_metric(_make_example(), pred)
        # Should get: parse(0.20) + yaml(0.15) + structural checks + load(0.15)
        # But NOT simulation(0.10) or value(0.15)
        assert score >= 0.55  # parse + yaml + some structural + load
        assert score < 0.85  # should not get full marks

    def test_simulates_but_wrong_value_still_scores(self):
        """Code that simulates but produces wrong value still gets execution points."""
        pred = _make_prediction(WRONG_VALUE_CODE, GOOD_YAML)
        score = code_quality_metric(_make_example(WRONG_VALUE_CODE), pred)
        # Should get: parse + yaml + structural + load + simulate
        # Numeric match gives 0.15 in the current logic (since expected_code exists)
        assert score >= 0.65

    def test_bootstrap_threshold_rejects_bad_code(self):
        """Bootstrap mode returns False for code scoring below 0.7."""
        pred = _make_prediction("class Broken(", "bad: yaml: [")
        result = code_quality_metric(_make_example(), pred, trace="bootstrap")
        assert result is False

    def test_bootstrap_threshold_accepts_good_code(self):
        """Bootstrap mode returns True for code scoring at or above 0.7."""
        pred = _make_prediction(GOOD_CODE, GOOD_YAML)
        result = code_quality_metric(_make_example(GOOD_CODE), pred, trace="bootstrap")
        assert result is True

    def test_bootstrap_threshold_boundary(self):
        """Code right at the boundary: moderate structural score but no execution."""
        # Code with structural elements but that won't execute well
        borderline_code = (
            "class X(Variable):\n"
            "    value_type = float\n"
            "    definition_period = MONTH\n"
            "    def formula(p, period): return 0\n"
        )
        pred = _make_prediction(borderline_code, GOOD_YAML)
        score_raw = code_quality_metric(_make_example(), pred)
        score_boot = code_quality_metric(_make_example(), pred, trace="bootstrap")
        # Verify consistency: bootstrap result matches threshold check
        assert score_boot == (score_raw >= 0.7)

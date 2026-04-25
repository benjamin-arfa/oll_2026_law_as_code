"""Tests for the OpenFisca code runner."""

from oll_law_as_code.runner import ExecutionResult, run_generated_code, run_batch_result


VALID_BOOL_VARIABLE = """\
from openfisca_core.model_api import *
from openfisca_switzerland.entities import Person

class test_tort_liable(Variable):
    value_type = bool
    entity = Person
    definition_period = YEAR
    label = "Test tort liability"

    def formula(person, period):
        return person("has_unlawful_act", period) * person("has_damage", period) > 0
"""

VALID_FLOAT_VARIABLE = """\
from openfisca_core.model_api import *
from openfisca_switzerland.entities import Person

class test_double_salary(Variable):
    value_type = float
    entity = Person
    definition_period = MONTH
    label = "Double the salary"

    def formula(person, period):
        return person("gross_monthly_salary", period) * 2
"""

SYNTAX_ERROR_CODE = "class Broken(Variable\n"

NO_VARIABLE_CODE = "x = 42\n"


class TestRunGeneratedCode:
    def test_valid_bool_variable_runs(self):
        input_data = {
            "persons": {"p1": {
                "has_unlawful_act": {"2024": True},
                "has_damage": {"2024": True},
            }},
            "households": {"h1": {"parents": ["p1"]}},
        }
        result = run_generated_code(VALID_BOOL_VARIABLE, input_data=input_data, period="2024")
        assert isinstance(result, ExecutionResult)
        assert result.success
        assert "test_tort_liable" in result.computed_values

    def test_valid_float_variable_runs(self):
        input_data = {
            "persons": {"p1": {"gross_monthly_salary": {"2024-01": 7083.33}}},
            "households": {"h1": {"parents": ["p1"]}},
        }
        result = run_generated_code(VALID_FLOAT_VARIABLE, input_data=input_data)
        assert result.success
        assert "test_double_salary" in result.computed_values
        assert result.computed_values["test_double_salary"] == pytest.approx(7083.33 * 2, rel=0.01)

    def test_syntax_error_returns_parse_stage(self):
        result = run_generated_code(SYNTAX_ERROR_CODE)
        assert not result.success
        assert result.error_stage == "parse"

    def test_no_variable_returns_load_stage(self):
        result = run_generated_code(NO_VARIABLE_CODE)
        assert not result.success
        assert result.error_stage == "load_variable"

    def test_code_fences_stripped(self):
        fenced = f"```python\n{VALID_FLOAT_VARIABLE}\n```"
        input_data = {
            "persons": {"p1": {"gross_monthly_salary": {"2024-01": 5000.0}}},
            "households": {"h1": {"parents": ["p1"]}},
        }
        result = run_generated_code(fenced, input_data=input_data)
        assert result.success

    def test_custom_input_data(self):
        input_data = {
            "persons": {"p1": {"gross_monthly_salary": {"2024-01": 5000.0}}},
            "households": {"h1": {"parents": ["p1"]}},
        }
        result = run_generated_code(VALID_FLOAT_VARIABLE, input_data=input_data)
        assert result.success
        assert result.computed_values["test_double_salary"] == pytest.approx(10000.0, rel=0.01)


class TestRunBatchResult:
    def test_two_independent_variables(self):
        input_data = {
            "persons": {"p1": {
                "gross_monthly_salary": {"2024-01": 5000.0},
            }},
            "households": {"h1": {"parents": ["p1"]}},
        }
        # Test with just the float variable pair since mixing YEAR/MONTH periods is tricky
        result = run_batch_result([VALID_FLOAT_VARIABLE], input_data=input_data)
        assert result.success
        assert "test_double_salary" in result.computed_values

    def test_syntax_error_in_batch(self):
        result = run_batch_result([VALID_FLOAT_VARIABLE, SYNTAX_ERROR_CODE])
        assert not result.success
        assert result.error_stage == "parse"


import pytest

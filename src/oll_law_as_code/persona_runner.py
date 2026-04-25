"""Run generated OpenFisca code against the test personas."""

from __future__ import annotations

import math
from decimal import Decimal

from oll_law_as_code.personas import ALL_PERSONAS, Persona
from oll_law_as_code.runner import ExecutionResult, run_generated_code


def persona_to_openfisca_input(
    persona: Persona, period: str = "2024-01"
) -> dict:
    """Convert a Persona dataclass into an OpenFisca simulation input dict."""
    monthly_salary = float(persona.annual_income / 12) if persona.employment_status == "employed" else 0.0
    annual_self_employment = float(persona.annual_income) if persona.employment_status == "self_employed" else 0.0

    person_data: dict = {
        "gross_monthly_salary": {period: monthly_salary},
        "age": {period: persona.age},
        "has_swiss_residence": {period: True},
        "has_swiss_employment": {period: persona.employment_status in ("employed", "self_employed")},
    }

    # Only set self_employment_income for yearly periods
    year = period[:4]
    person_data["self_employment_income"] = {year: annual_self_employment}

    for var_name, period_values in persona.extra_inputs.items():
        person_data[var_name] = period_values

    return {
        "persons": {persona.name.lower(): person_data},
        "households": {"hh": {"parents": [persona.name.lower()]}},
    }


def run_persona_tests(
    code_string: str,
    yaml_string: str | None = None,
    period: str = "2024-01",
    tolerance: float = 0.01,
) -> list[dict]:
    """Run generated code against all personas and compare expected values.

    Returns a list of dicts, one per persona, with keys:
        - ``name``: persona name
        - ``passed``: whether all expected values matched
        - ``result``: the :class:`ExecutionResult`
        - ``mismatches``: dict of variable -> (expected, computed) for failures
    """
    reports = []
    for persona in ALL_PERSONAS:
        input_data = persona_to_openfisca_input(persona, period)
        result = run_generated_code(code_string, yaml_string, input_data, period)

        mismatches = {}
        if result.success:
            for var_name, expected in persona.expected_values.items():
                if isinstance(expected, (Decimal, int, float)):
                    computed = result.computed_values.get(var_name)
                    if computed is None:
                        continue  # variable not in generated code — skip
                    if not math.isclose(
                        float(expected), computed, rel_tol=tolerance
                    ):
                        mismatches[var_name] = (float(expected), computed)

        passed = result.success and len(mismatches) == 0
        reports.append(
            {
                "name": persona.name,
                "passed": passed,
                "result": result,
                "mismatches": mismatches,
            }
        )

    return reports


def compute_persona_pass_rate(
    code_string: str,
    yaml_string: str | None = None,
    period: str = "2024-01",
) -> float:
    """Fraction of personas whose expected values match the computed output."""
    reports = run_persona_tests(code_string, yaml_string, period)
    if not reports:
        return 0.0
    return sum(1 for r in reports if r["passed"]) / len(reports)

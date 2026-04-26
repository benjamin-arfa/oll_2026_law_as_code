"""Integration tests for CO personas against actual generated variable code.

For each CO persona (Francois, Giulia, Hans), loads the corresponding formula
variable code and verifies that the persona's expected_values match the
simulation output.
"""

from pathlib import Path

import yaml
import pytest

from oll_law_as_code.personas import (
    FRANCOIS, GIULIA, HANS,
    FRANCOIS_DILIGENT, GIULIA_LATE_NOTICE, HANS_NOT_SUMMONED,
    Persona,
)
from oll_law_as_code.persona_runner import persona_to_openfisca_input
from oll_law_as_code.runner import run_generated_code

DATA_DIR = Path(__file__).resolve().parents[1] / "data" / "examples"


def _load_yaml_code(filename: str) -> str:
    """Load openfisca_variable code from a YAML example file."""
    path = DATA_DIR / filename
    with open(path) as f:
        data = yaml.safe_load(f)
    return data["openfisca_variable"]


def _build_co_input(persona: Persona) -> dict:
    """Build an OpenFisca input dict for CO boolean tests.

    CO variables use definition_period = YEAR, but gross_monthly_salary is
    MONTH-based.  We set salary with a monthly period and boolean extra_inputs
    with their own (yearly) periods to avoid period-mismatch errors.
    """
    person_data: dict = {
        "gross_monthly_salary": {"2024-01": 0.0},
    }
    for var_name, period_values in persona.extra_inputs.items():
        person_data[var_name] = period_values
    return {
        "persons": {persona.name.lower(): person_data},
        "households": {"hh": {"parents": [persona.name.lower()]}},
    }


class TestFrancoisEmployerLiability:
    """Francois: employer whose employee caused a tort (CO 55)."""

    CODE = _load_yaml_code("or_art55_employer_liability.yaml")

    def test_persona_input_has_extra_inputs(self):
        inp = persona_to_openfisca_input(FRANCOIS, period="2024-01")
        person_data = inp["persons"]["francois"]
        assert person_data["is_employer_of_tortfeasor"]["2024"] is True
        assert person_data["employer_proves_diligence"]["2024"] is False

    def test_simulation_matches_expected_values(self):
        inp = _build_co_input(FRANCOIS)
        result = run_generated_code(self.CODE, input_data=inp, period="2024")
        assert result.success
        for var_name, expected in FRANCOIS.expected_values.items():
            assert var_name in result.computed_values, f"Missing variable {var_name}"
            assert result.computed_values[var_name] == pytest.approx(
                float(expected), abs=0.01
            ), f"{var_name}: expected {expected}, got {result.computed_values[var_name]}"


class TestGiuliaWarrantyClaim:
    """Giulia: buyer of defective goods (CO 197)."""

    CODE = _load_yaml_code("or_art197_warranty_claims.yaml")

    def test_persona_input_has_extra_inputs(self):
        inp = persona_to_openfisca_input(GIULIA, period="2024-01")
        person_data = inp["persons"]["giulia"]
        assert person_data["has_defect"]["2024"] is True
        assert person_data["timely_notice_of_defect"]["2024"] is True

    def test_simulation_matches_expected_values(self):
        inp = _build_co_input(GIULIA)
        result = run_generated_code(self.CODE, input_data=inp, period="2024")
        assert result.success
        for var_name, expected in GIULIA.expected_values.items():
            assert var_name in result.computed_values, f"Missing variable {var_name}"
            assert result.computed_values[var_name] == pytest.approx(
                float(expected), abs=0.01
            ), f"{var_name}: expected {expected}, got {result.computed_values[var_name]}"


class TestHansDebtorDefault:
    """Hans: contractor with overdue payment (CO 102)."""

    CODE = _load_yaml_code("or_art102_debtor_default.yaml")

    def test_persona_input_has_extra_inputs(self):
        inp = persona_to_openfisca_input(HANS, period="2024-01")
        person_data = inp["persons"]["hans"]
        assert person_data["obligation_is_due"]["2024"] is True
        assert person_data["debtor_failed_to_perform"]["2024"] is True

    def test_simulation_matches_expected_values(self):
        inp = _build_co_input(HANS)
        result = run_generated_code(self.CODE, input_data=inp, period="2024")
        assert result.success
        for var_name, expected in HANS.expected_values.items():
            assert var_name in result.computed_values, f"Missing variable {var_name}"
            assert result.computed_values[var_name] == pytest.approx(
                float(expected), abs=0.01
            ), f"{var_name}: expected {expected}, got {result.computed_values[var_name]}"


# ── Negative Personas (expected False / 0) ──────────────────────────────────


class TestFrancoisDiligentEmployerNotLiable:
    """FrancoisDiligent: employer who proves diligence — CO 55 should return False."""

    CODE = _load_yaml_code("or_art55_employer_liability.yaml")

    def test_simulation_returns_false(self):
        inp = _build_co_input(FRANCOIS_DILIGENT)
        result = run_generated_code(self.CODE, input_data=inp, period="2024")
        assert result.success
        for var_name, expected in FRANCOIS_DILIGENT.expected_values.items():
            assert var_name in result.computed_values, f"Missing variable {var_name}"
            assert result.computed_values[var_name] == pytest.approx(
                float(expected), abs=0.01
            ), f"{var_name}: expected {expected}, got {result.computed_values[var_name]}"


class TestGiuliaLateNoticeWarrantyInvalid:
    """GiuliaLateNotice: late notice of defect — CO 197 should return False."""

    CODE = _load_yaml_code("or_art197_warranty_claims.yaml")

    def test_simulation_returns_false(self):
        inp = _build_co_input(GIULIA_LATE_NOTICE)
        result = run_generated_code(self.CODE, input_data=inp, period="2024")
        assert result.success
        for var_name, expected in GIULIA_LATE_NOTICE.expected_values.items():
            assert var_name in result.computed_values, f"Missing variable {var_name}"
            assert result.computed_values[var_name] == pytest.approx(
                float(expected), abs=0.01
            ), f"{var_name}: expected {expected}, got {result.computed_values[var_name]}"


class TestHansNotSummonedNoDefault:
    """HansNotSummoned: debtor never summoned — CO 102 should return False."""

    CODE = _load_yaml_code("or_art102_debtor_default.yaml")

    def test_simulation_returns_false(self):
        inp = _build_co_input(HANS_NOT_SUMMONED)
        result = run_generated_code(self.CODE, input_data=inp, period="2024")
        assert result.success
        for var_name, expected in HANS_NOT_SUMMONED.expected_values.items():
            assert var_name in result.computed_values, f"Missing variable {var_name}"
            assert result.computed_values[var_name] == pytest.approx(
                float(expected), abs=0.01
            ), f"{var_name}: expected {expected}, got {result.computed_values[var_name]}"

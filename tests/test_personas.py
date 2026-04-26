"""Tests for persona definitions and persona runner."""

from decimal import Decimal

from oll_law_as_code.personas import (
    ALL_PERSONAS, ANNA, FRANCOIS, GIULIA, HANS,
    FRANCOIS_DILIGENT, GIULIA_LATE_NOTICE, HANS_NOT_SUMMONED,
    Persona,
)
from oll_law_as_code.persona_runner import persona_to_openfisca_input


class TestPersonaDefinitions:
    def test_all_personas_count(self):
        assert len(ALL_PERSONAS) == 11

    def test_persona_names_unique(self):
        names = [p.name for p in ALL_PERSONAS]
        assert len(names) == len(set(names))

    def test_ahvg_personas_have_expected_values(self):
        assert "ahv_employee_contribution" in ANNA.expected_values

    def test_co_personas_have_expected_values(self):
        assert "or_employer_liability" in FRANCOIS.expected_values
        assert "or_warranty_claim_valid" in GIULIA.expected_values
        assert "or_debtor_in_default" in HANS.expected_values

    def test_co_personas_have_extra_inputs(self):
        assert len(FRANCOIS.extra_inputs) > 0
        assert len(GIULIA.extra_inputs) > 0
        assert len(HANS.extra_inputs) > 0

    def test_negative_personas_expect_false(self):
        for persona in [FRANCOIS_DILIGENT, GIULIA_LATE_NOTICE, HANS_NOT_SUMMONED]:
            for var_name, val in persona.expected_values.items():
                assert val == 0, f"{persona.name}.{var_name} should expect 0 (False)"

    def test_extra_inputs_field_default(self):
        p = Persona(
            name="Test", age=30, canton="ZH",
            employment_status="employed", marital_status="single",
            annual_income=Decimal("50000"),
        )
        assert p.extra_inputs == {}


class TestPersonaToOpenfiscaInput:
    def test_basic_structure(self):
        inp = persona_to_openfisca_input(ANNA)
        assert "persons" in inp
        assert "households" in inp
        assert "anna" in inp["persons"]

    def test_employed_gets_salary(self):
        inp = persona_to_openfisca_input(ANNA)
        person_data = inp["persons"]["anna"]
        assert "gross_monthly_salary" in person_data
        salary = list(person_data["gross_monthly_salary"].values())[0]
        assert salary > 0

    def test_extra_inputs_merged(self):
        inp = persona_to_openfisca_input(FRANCOIS)
        person_data = inp["persons"]["francois"]
        assert "is_employer_of_tortfeasor" in person_data
        assert person_data["is_employer_of_tortfeasor"]["2024"] is True

    def test_self_employed_gets_zero_salary(self):
        inp = persona_to_openfisca_input(HANS)
        person_data = inp["persons"]["hans"]
        salary = list(person_data["gross_monthly_salary"].values())[0]
        assert salary == 0.0

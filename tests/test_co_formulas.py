"""Integration tests for CO formula execution.

Each test loads a CO YAML example's openfisca_variable code, adds it to the
TaxBenefitSystem, and verifies correct boolean results with appropriate inputs.
"""

from pathlib import Path

import yaml
import pytest

from oll_law_as_code.runner import run_generated_code

DATA_DIR = Path(__file__).resolve().parents[1] / "data" / "examples"


def _load_yaml_code(filename: str) -> str:
    """Load openfisca_variable code from a YAML example file."""
    path = DATA_DIR / filename
    with open(path) as f:
        data = yaml.safe_load(f)
    return data["openfisca_variable"]


# ── Art. 1 — Contract Formation ──────────────────────────────────────────────


class TestArt1ContractFormation:
    CODE = _load_yaml_code("or_art1_contract_formation.yaml")

    def test_all_conditions_true_returns_true(self):
        input_data = {
            "persons": {"p1": {
                "has_offer": {"2024": True},
                "has_acceptance": {"2024": True},
                "has_concordance": {"2024": True},
                "has_reciprocity": {"2024": True},
                "has_required_form": {"2024": True},
                "has_capacity": {"2024": True},
            }},
            "households": {"h1": {"parents": ["p1"]}},
        }
        result = run_generated_code(self.CODE, input_data=input_data, period="2024")
        assert result.success
        assert result.computed_values["or_contract_formation"] == 1.0

    def test_missing_acceptance_returns_false(self):
        input_data = {
            "persons": {"p1": {
                "has_offer": {"2024": True},
                "has_acceptance": {"2024": False},
                "has_concordance": {"2024": True},
                "has_reciprocity": {"2024": True},
                "has_required_form": {"2024": True},
                "has_capacity": {"2024": True},
            }},
            "households": {"h1": {"parents": ["p1"]}},
        }
        result = run_generated_code(self.CODE, input_data=input_data, period="2024")
        assert result.success
        assert result.computed_values["or_contract_formation"] == 0.0


# ── Art. 20 — Contract Nullity ───────────────────────────────────────────────


class TestArt20ContractNullity:
    CODE = _load_yaml_code("or_art20_contract_nullity.yaml")

    def test_illicit_object_returns_true(self):
        input_data = {
            "persons": {"p1": {
                "has_impossible_object": {"2024": False},
                "has_illicit_object": {"2024": True},
                "has_immoral_object": {"2024": False},
                "has_form_defect": {"2024": False},
            }},
            "households": {"h1": {"parents": ["p1"]}},
        }
        result = run_generated_code(self.CODE, input_data=input_data, period="2024")
        assert result.success
        assert result.computed_values["or_contract_nullity"] == 1.0

    def test_no_grounds_returns_false(self):
        input_data = {
            "persons": {"p1": {
                "has_impossible_object": {"2024": False},
                "has_illicit_object": {"2024": False},
                "has_immoral_object": {"2024": False},
                "has_form_defect": {"2024": False},
            }},
            "households": {"h1": {"parents": ["p1"]}},
        }
        result = run_generated_code(self.CODE, input_data=input_data, period="2024")
        assert result.success
        assert result.computed_values["or_contract_nullity"] == 0.0


# ── Art. 41 — Tort Liability ─────────────────────────────────────────────────


class TestArt41TortLiability:
    CODE = _load_yaml_code("or_art41_tort_liability.yaml")

    def test_al1_all_conditions_true(self):
        input_data = {
            "persons": {"p1": {
                "has_unlawful_act": {"2024": True},
                "has_damage": {"2024": True},
                "has_causation": {"2024": True},
                "has_intent": {"2024": True},
                "has_negligence": {"2024": False},
                "is_contrary_to_morals": {"2024": False},
            }},
            "households": {"h1": {"parents": ["p1"]}},
        }
        result = run_generated_code(self.CODE, input_data=input_data, period="2024")
        assert result.success
        assert result.computed_values["or_tort_liability"] == 1.0

    def test_no_damage_returns_false(self):
        input_data = {
            "persons": {"p1": {
                "has_unlawful_act": {"2024": True},
                "has_damage": {"2024": False},
                "has_causation": {"2024": True},
                "has_intent": {"2024": True},
                "has_negligence": {"2024": False},
                "is_contrary_to_morals": {"2024": False},
            }},
            "households": {"h1": {"parents": ["p1"]}},
        }
        result = run_generated_code(self.CODE, input_data=input_data, period="2024")
        assert result.success
        assert result.computed_values["or_tort_liability"] == 0.0


# ── Art. 55 — Employer Liability ─────────────────────────────────────────────


class TestArt55EmployerLiability:
    CODE = _load_yaml_code("or_art55_employer_liability.yaml")

    def test_all_conditions_no_diligence_returns_true(self):
        input_data = {
            "persons": {"p1": {
                "is_employer_of_tortfeasor": {"2024": True},
                "employee_committed_tort": {"2024": True},
                "tort_in_course_of_employment": {"2024": True},
                "has_damage": {"2024": True},
                "has_causation": {"2024": True},
                "employer_proves_diligence": {"2024": False},
            }},
            "households": {"h1": {"parents": ["p1"]}},
        }
        result = run_generated_code(self.CODE, input_data=input_data, period="2024")
        assert result.success
        assert result.computed_values["or_employer_liability"] == 1.0

    def test_employer_proves_diligence_returns_false(self):
        input_data = {
            "persons": {"p1": {
                "is_employer_of_tortfeasor": {"2024": True},
                "employee_committed_tort": {"2024": True},
                "tort_in_course_of_employment": {"2024": True},
                "has_damage": {"2024": True},
                "has_causation": {"2024": True},
                "employer_proves_diligence": {"2024": True},
            }},
            "households": {"h1": {"parents": ["p1"]}},
        }
        result = run_generated_code(self.CODE, input_data=input_data, period="2024")
        assert result.success
        assert result.computed_values["or_employer_liability"] == 0.0


# ── Art. 62 — Unjust Enrichment ──────────────────────────────────────────────


class TestArt62UnjustEnrichment:
    CODE = _load_yaml_code("or_art62_unjust_enrichment.yaml")

    def test_all_conditions_true_returns_true(self):
        input_data = {
            "persons": {"p1": {
                "has_enrichment": {"2024": True},
                "has_impoverishment": {"2024": True},
                "has_connexity": {"2024": True},
                "has_no_legal_basis": {"2024": True},
            }},
            "households": {"h1": {"parents": ["p1"]}},
        }
        result = run_generated_code(self.CODE, input_data=input_data, period="2024")
        assert result.success
        assert result.computed_values["or_unjust_enrichment"] == 1.0

    def test_missing_connexity_returns_false(self):
        input_data = {
            "persons": {"p1": {
                "has_enrichment": {"2024": True},
                "has_impoverishment": {"2024": True},
                "has_connexity": {"2024": False},
                "has_no_legal_basis": {"2024": True},
            }},
            "households": {"h1": {"parents": ["p1"]}},
        }
        result = run_generated_code(self.CODE, input_data=input_data, period="2024")
        assert result.success
        assert result.computed_values["or_unjust_enrichment"] == 0.0


# ── Art. 97 — Contractual Liability ──────────────────────────────────────────


class TestArt97ContractualLiability:
    CODE = _load_yaml_code("or_art97_contractual_liability.yaml")

    def test_all_conditions_true_returns_true(self):
        input_data = {
            "persons": {"p1": {
                "has_contractual_obligation": {"2024": True},
                "has_breach_of_obligation": {"2024": True},
                "has_contractual_damage": {"2024": True},
                "has_adequate_causation": {"2024": True},
                "has_presumed_fault": {"2024": True},
            }},
            "households": {"h1": {"parents": ["p1"]}},
        }
        result = run_generated_code(self.CODE, input_data=input_data, period="2024")
        assert result.success
        assert result.computed_values["or_contractual_liability"] == 1.0

    def test_no_breach_returns_false(self):
        input_data = {
            "persons": {"p1": {
                "has_contractual_obligation": {"2024": True},
                "has_breach_of_obligation": {"2024": False},
                "has_contractual_damage": {"2024": True},
                "has_adequate_causation": {"2024": True},
                "has_presumed_fault": {"2024": True},
            }},
            "households": {"h1": {"parents": ["p1"]}},
        }
        result = run_generated_code(self.CODE, input_data=input_data, period="2024")
        assert result.success
        assert result.computed_values["or_contractual_liability"] == 0.0


# ── Art. 102 — Debtor Default ────────────────────────────────────────────────


class TestArt102DebtorDefault:
    CODE = _load_yaml_code("or_art102_debtor_default.yaml")

    def test_all_conditions_true_returns_true(self):
        input_data = {
            "persons": {"p1": {
                "obligation_is_due": {"2024": True},
                "debtor_has_been_summoned": {"2024": True},
                "debtor_failed_to_perform": {"2024": True},
            }},
            "households": {"h1": {"parents": ["p1"]}},
        }
        result = run_generated_code(self.CODE, input_data=input_data, period="2024")
        assert result.success
        assert result.computed_values["or_debtor_in_default"] == 1.0

    def test_not_summoned_returns_false(self):
        input_data = {
            "persons": {"p1": {
                "obligation_is_due": {"2024": True},
                "debtor_has_been_summoned": {"2024": False},
                "debtor_failed_to_perform": {"2024": True},
            }},
            "households": {"h1": {"parents": ["p1"]}},
        }
        result = run_generated_code(self.CODE, input_data=input_data, period="2024")
        assert result.success
        assert result.computed_values["or_debtor_in_default"] == 0.0


# ── Art. 197 — Warranty Claims ───────────────────────────────────────────────


class TestArt197WarrantyClaims:
    CODE = _load_yaml_code("or_art197_warranty_claims.yaml")

    def test_all_conditions_true_returns_true(self):
        input_data = {
            "persons": {"p1": {
                "has_sale_or_work_contract": {"2024": True},
                "has_defect": {"2024": True},
                "defect_before_risk_transfer": {"2024": True},
                "buyer_unaware_of_defect": {"2024": True},
                "timely_notice_of_defect": {"2024": True},
            }},
            "households": {"h1": {"parents": ["p1"]}},
        }
        result = run_generated_code(self.CODE, input_data=input_data, period="2024")
        assert result.success
        assert result.computed_values["or_warranty_claim_valid"] == 1.0

    def test_no_defect_returns_false(self):
        input_data = {
            "persons": {"p1": {
                "has_sale_or_work_contract": {"2024": True},
                "has_defect": {"2024": False},
                "defect_before_risk_transfer": {"2024": True},
                "buyer_unaware_of_defect": {"2024": True},
                "timely_notice_of_defect": {"2024": True},
            }},
            "households": {"h1": {"parents": ["p1"]}},
        }
        result = run_generated_code(self.CODE, input_data=input_data, period="2024")
        assert result.success
        assert result.computed_values["or_warranty_claim_valid"] == 0.0

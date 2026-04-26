"""Tests for OpenFisca input variable definitions and system loading."""

import logging

import pytest

from openfisca_switzerland import CountryTaxBenefitSystem


@pytest.fixture(scope="module")
def tbs():
    """Build TaxBenefitSystem, suppressing openfisca metadata warning."""
    logging.disable(logging.WARNING)
    try:
        return CountryTaxBenefitSystem()
    finally:
        logging.disable(logging.NOTSET)


class TestCountryPackageLoads:
    def test_system_instantiates(self, tbs):
        assert tbs is not None

    def test_ahvg_variables_exist(self, tbs):
        for name in [
            "gross_monthly_salary",
            "self_employment_income",
            "age",
            "has_swiss_residence",
            "has_swiss_employment",
        ]:
            assert name in tbs.variables, f"Missing AHVG variable: {name}"

    def test_co_tort_variables_exist(self, tbs):
        for name in [
            "has_unlawful_act",
            "has_damage",
            "has_causation",
            "has_intent",
            "has_negligence",
            "is_contrary_to_morals",
        ]:
            assert name in tbs.variables, f"Missing CO 41 variable: {name}"

    def test_co_contract_formation_variables_exist(self, tbs):
        for name in [
            "has_offer",
            "has_acceptance",
            "has_concordance",
            "has_reciprocity",
            "has_required_form",
            "has_capacity",
        ]:
            assert name in tbs.variables, f"Missing CO 1 variable: {name}"

    def test_co_nullity_variables_exist(self, tbs):
        for name in [
            "has_impossible_object",
            "has_illicit_object",
            "has_immoral_object",
            "has_form_defect",
        ]:
            assert name in tbs.variables, f"Missing CO 20 variable: {name}"

    def test_co_contractual_liability_variables_exist(self, tbs):
        for name in [
            "has_contractual_obligation",
            "has_breach_of_obligation",
            "has_contractual_damage",
            "has_adequate_causation",
            "has_presumed_fault",
        ]:
            assert name in tbs.variables, f"Missing CO 97 variable: {name}"

    def test_co_unjust_enrichment_variables_exist(self, tbs):
        for name in [
            "has_enrichment",
            "has_impoverishment",
            "has_connexity",
            "has_no_legal_basis",
        ]:
            assert name in tbs.variables, f"Missing CO 62 variable: {name}"

    def test_co_prescription_variables_exist(self, tbs):
        for name in ["claim_age_years", "is_periodic_claim"]:
            assert name in tbs.variables, f"Missing CO 127 variable: {name}"

    def test_co_employer_liability_variables_exist(self, tbs):
        for name in [
            "is_employer_of_tortfeasor",
            "employee_committed_tort",
            "tort_in_course_of_employment",
            "employer_proves_diligence",
        ]:
            assert name in tbs.variables, f"Missing CO 55 variable: {name}"

    def test_co_debtor_default_variables_exist(self, tbs):
        for name in [
            "obligation_is_due",
            "debtor_has_been_summoned",
            "additional_delay_granted",
            "debtor_failed_to_perform",
        ]:
            assert name in tbs.variables, f"Missing CO 102 variable: {name}"

    def test_co_warranty_variables_exist(self, tbs):
        for name in [
            "has_sale_or_work_contract",
            "has_defect",
            "defect_before_risk_transfer",
            "buyer_unaware_of_defect",
            "timely_notice_of_defect",
            "defect_reduction_amount",
            "purchase_price",
        ]:
            assert name in tbs.variables, f"Missing CO 197 variable: {name}"

    def test_boolean_variables_have_correct_type(self, tbs):
        bool_vars = [
            "has_unlawful_act", "has_offer", "has_impossible_object",
            "has_contractual_obligation", "has_enrichment",
            "is_periodic_claim", "is_employer_of_tortfeasor",
            "obligation_is_due", "has_defect",
        ]
        for name in bool_vars:
            var = tbs.variables[name]
            assert var.value_type == bool, f"{name} should be bool, got {var.value_type}"

    def test_co_formula_variables_exist(self, tbs):
        """Verify CO formula variables (from co_formulas.py) are loaded into TBS."""
        for name in [
            "or_contract_formation",
            "or_contract_nullity",
            "or_tort_liability",
            "or_employer_liability",
            "or_unjust_enrichment",
            "or_contractual_liability",
            "or_debtor_in_default",
            "or_warranty_claim_valid",
        ]:
            assert name in tbs.variables, f"Missing CO formula variable: {name}"
            var = tbs.variables[name]
            assert var.value_type == bool, f"{name} should be bool"

    def test_default_values(self, tbs):
        # Variables that default to True
        for name in ["has_required_form", "has_capacity", "has_presumed_fault"]:
            var = tbs.variables[name]
            assert var.default_value is True, f"{name} should default to True"

        # Variables that default to False
        for name in ["has_unlawful_act", "has_damage", "has_offer"]:
            var = tbs.variables[name]
            assert var.default_value is False, f"{name} should default to False"

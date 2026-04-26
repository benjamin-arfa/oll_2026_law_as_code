"""Computed CO (Code of Obligations) formula variables.

Each Variable here encodes the legal conditions from a specific CO article
as a boolean formula. They reference the input variables defined in inputs.py.

This mirrors the pattern from bern_stipendium/variables/eligibility.py:
composed boolean variables using multiplication (AND), addition (OR),
and (1 - var) for negation/defense.
"""

from openfisca_core.variables import Variable
from openfisca_core.periods import YEAR

from openfisca_switzerland.entities import Person


# ===========================================================================
# CO Art. 1 — Formation du contrat (Contract Formation)
# ===========================================================================

class or_contract_formation(Variable):
    value_type = bool
    entity = Person
    definition_period = YEAR
    label = "Contract formation (Art. 1 CO)"
    reference = "CO Art. 1"
    default_value = False

    def formula(person, period, parameters):
        has_offer = person("has_offer", period)
        has_acceptance = person("has_acceptance", period)
        has_concordance = person("has_concordance", period)
        has_reciprocity = person("has_reciprocity", period)
        has_required_form = person("has_required_form", period)
        has_capacity = person("has_capacity", period)
        return has_offer * has_acceptance * has_concordance * has_reciprocity * has_required_form * has_capacity > 0


# ===========================================================================
# CO Art. 20 — Nullité du contrat (Contract Nullity)
# ===========================================================================

class or_contract_nullity(Variable):
    value_type = bool
    entity = Person
    definition_period = YEAR
    label = "Contract nullity (Art. 20 CO)"
    reference = "CO Art. 20"
    default_value = False

    def formula(person, period, parameters):
        has_impossible_object = person("has_impossible_object", period)
        has_illicit_object = person("has_illicit_object", period)
        has_immoral_object = person("has_immoral_object", period)
        has_form_defect = person("has_form_defect", period)
        return has_impossible_object + has_illicit_object + has_immoral_object + has_form_defect > 0


# ===========================================================================
# CO Art. 41 — Responsabilité délictuelle (Tort Liability)
# ===========================================================================

class or_tort_liability(Variable):
    value_type = bool
    entity = Person
    definition_period = YEAR
    label = "Tort liability (Art. 41 CO)"
    reference = "CO Art. 41"
    default_value = False

    def formula(person, period, parameters):
        has_unlawful_act = person("has_unlawful_act", period)
        has_damage = person("has_damage", period)
        has_causation = person("has_causation", period)
        has_intent = person("has_intent", period)
        has_negligence = person("has_negligence", period)
        is_contrary_to_morals = person("is_contrary_to_morals", period)
        # Al. 1: unlawful act + damage + causation + fault (intent or negligence)
        al1 = has_unlawful_act * has_damage * has_causation * (has_intent + has_negligence > 0)
        # Al. 2: intentional + contrary to morals + damage + causation
        al2 = has_intent * is_contrary_to_morals * has_damage * has_causation
        return al1 + al2 > 0


# ===========================================================================
# CO Art. 55 — Responsabilité de l'employeur (Employer Liability)
# ===========================================================================

class or_employer_liability(Variable):
    value_type = bool
    entity = Person
    definition_period = YEAR
    label = "Employer liability (Art. 55 CO)"
    reference = "CO Art. 55"
    default_value = False

    def formula(person, period, parameters):
        is_employer_of_tortfeasor = person("is_employer_of_tortfeasor", period)
        employee_committed_tort = person("employee_committed_tort", period)
        tort_in_course_of_employment = person("tort_in_course_of_employment", period)
        has_damage = person("has_damage", period)
        has_causation = person("has_causation", period)
        employer_proves_diligence = person("employer_proves_diligence", period)
        return is_employer_of_tortfeasor * employee_committed_tort * tort_in_course_of_employment * has_damage * has_causation * (1 - employer_proves_diligence) > 0


# ===========================================================================
# CO Art. 62 — Enrichissement illégitime (Unjust Enrichment)
# ===========================================================================

class or_unjust_enrichment(Variable):
    value_type = bool
    entity = Person
    definition_period = YEAR
    label = "Unjust enrichment (Art. 62 CO)"
    reference = "CO Art. 62"
    default_value = False

    def formula(person, period, parameters):
        has_enrichment = person("has_enrichment", period)
        has_impoverishment = person("has_impoverishment", period)
        has_connexity = person("has_connexity", period)
        has_no_legal_basis = person("has_no_legal_basis", period)
        return has_enrichment * has_impoverishment * has_connexity * has_no_legal_basis > 0


# ===========================================================================
# CO Art. 97 — Responsabilité contractuelle (Contractual Liability)
# ===========================================================================

class or_contractual_liability(Variable):
    value_type = bool
    entity = Person
    definition_period = YEAR
    label = "Contractual liability (Art. 97 CO)"
    reference = "CO Art. 97"
    default_value = False

    def formula(person, period, parameters):
        has_contractual_obligation = person("has_contractual_obligation", period)
        has_breach_of_obligation = person("has_breach_of_obligation", period)
        has_contractual_damage = person("has_contractual_damage", period)
        has_adequate_causation = person("has_adequate_causation", period)
        has_presumed_fault = person("has_presumed_fault", period)
        return has_contractual_obligation * has_breach_of_obligation * has_contractual_damage * has_adequate_causation * has_presumed_fault > 0


# ===========================================================================
# CO Art. 102 — Demeure du débiteur (Debtor Default)
# ===========================================================================

class or_debtor_in_default(Variable):
    value_type = bool
    entity = Person
    definition_period = YEAR
    label = "Debtor in default (Art. 102 CO)"
    reference = "CO Art. 102"
    default_value = False

    def formula(person, period, parameters):
        obligation_is_due = person("obligation_is_due", period)
        debtor_has_been_summoned = person("debtor_has_been_summoned", period)
        debtor_failed_to_perform = person("debtor_failed_to_perform", period)
        return obligation_is_due * debtor_has_been_summoned * debtor_failed_to_perform > 0


# ===========================================================================
# CO Art. 197 — Garantie pour les défauts (Warranty Claims)
# ===========================================================================

class or_warranty_claim_valid(Variable):
    value_type = bool
    entity = Person
    definition_period = YEAR
    label = "Warranty claim valid (Art. 197 CO)"
    reference = "CO Art. 197"
    default_value = False

    def formula(person, period, parameters):
        has_sale_or_work_contract = person("has_sale_or_work_contract", period)
        has_defect = person("has_defect", period)
        defect_before_risk_transfer = person("defect_before_risk_transfer", period)
        buyer_unaware_of_defect = person("buyer_unaware_of_defect", period)
        timely_notice_of_defect = person("timely_notice_of_defect", period)
        return has_sale_or_work_contract * has_defect * defect_before_risk_transfer * buyer_unaware_of_defect * timely_notice_of_defect > 0

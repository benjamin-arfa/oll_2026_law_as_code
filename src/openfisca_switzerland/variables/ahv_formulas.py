"""Computed AHV (AHVG) formula variables.

Each Variable here encodes the legal conditions from a specific AHVG article.
They reference the input variables defined in inputs.py and parameters
from the social_security/ahv parameter tree.
"""

from openfisca_core.model_api import *
from openfisca_switzerland.entities import Person


# ===========================================================================
# AHVG Art. 3 — Obligatorisch versicherte Personen (Insurance Obligation)
# ===========================================================================

class ahv_insurance_obligation(Variable):
    value_type = bool
    entity = Person
    definition_period = YEAR
    label = "AHV insurance obligation (Art. 3 AHVG)"
    reference = "AHVG Art. 3"
    default_value = False

    def formula(person, period, parameters):
        month = period.first_month
        age = person("age", month)
        has_residence = person("has_swiss_residence", month)
        has_employment = person("has_swiss_employment", month)
        return (age >= 18) * (has_residence + has_employment > 0)


# ===========================================================================
# AHVG Art. 5 — Beiträge von Einkommen aus unselbständiger Erwerbstätigkeit
# ===========================================================================

class ahv_employee_contribution(Variable):
    value_type = float
    entity = Person
    definition_period = MONTH
    label = "AHV/IV/EO employee contribution (Art. 5 AHVG)"
    reference = "AHVG Art. 5"

    def formula(person, period, parameters):
        gross_salary = person("gross_monthly_salary", period)
        rate = parameters(period).social_security.ahv.employee_rate
        return gross_salary * rate


# ===========================================================================
# AHVG Art. 10 — Beiträge der Selbständigerwerbenden
# ===========================================================================

class ahv_self_employed_contribution(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    label = "AHV/IV/EO self-employed contribution (Art. 10 AHVG)"
    reference = "AHVG Art. 10"

    def formula(person, period, parameters):
        income = person("self_employment_income", period)
        rate = parameters(period).social_security.ahv.self_employed_rate
        return income * rate


# ===========================================================================
# AHVG Art. 14 — Beiträge der Arbeitgeber (Employer Contribution)
# ===========================================================================

class ahv_employer_contribution(Variable):
    value_type = float
    entity = Person
    definition_period = MONTH
    label = "AHV/IV/EO employer contribution (Art. 14 AHVG)"
    reference = "AHVG Art. 14"

    def formula(person, period, parameters):
        employee_contribution = person("ahv_employee_contribution", period)
        return employee_contribution

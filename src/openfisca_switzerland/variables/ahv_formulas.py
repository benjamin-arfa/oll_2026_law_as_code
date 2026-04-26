"""AHV (Old-Age and Survivors' Insurance) formula variables.

Pre-written formulas encoding AHVG articles as OpenFisca variables.
These are auto-loaded by CountryTaxBenefitSystem.add_variables_from_directory().
"""

from openfisca_core.model_api import *  # noqa: F403
from openfisca_switzerland.entities import Person


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

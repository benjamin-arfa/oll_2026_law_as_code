"""Stub input variables for the Swiss OpenFisca country package."""

from openfisca_core.model_api import *
from openfisca_switzerland.entities import Person


class gross_monthly_salary(Variable):
    value_type = float
    entity = Person
    definition_period = MONTH
    label = "Gross monthly salary from employment"


class self_employment_income(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    label = "Annual net income from self-employment"


class age(Variable):
    value_type = int
    entity = Person
    definition_period = MONTH
    label = "Age of the person in years"


class has_swiss_residence(Variable):
    value_type = bool
    entity = Person
    definition_period = MONTH
    label = "Whether the person has residence in Switzerland"
    default_value = True


class has_swiss_employment(Variable):
    value_type = bool
    entity = Person
    definition_period = MONTH
    label = "Whether the person is employed in Switzerland"
    default_value = True


from openfisca_core.model_api import *
from openfisca_country_template.entities import Person


class vacation_weeks_entitlement(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    label = "Ferienanspruch in Wochen pro Kalenderjahr (altersabhaengig)"
    reference = "Art. 1 - Ferienanspruch der Angestellten"

    def formula(person, period, parameters):
        # Age reached during the calendar year = calendar year - birth year.
        # The law triggers the new tier from the *start* of the year the employee
        # turns the threshold age.
        date_of_birth = person("date_of_birth", period)
        birth_year = date_of_birth.astype("datetime64[Y]").astype(int) + 1970
        age_reached = period.start.year - birth_year

        p = parameters(period).employment.vacation

        return select(
            [
                age_reached <= p.age_threshold_youth,    # up to 20
                age_reached < p.age_threshold_middle,    # 21-49
                age_reached < p.age_threshold_senior,    # 50-59
                age_reached >= p.age_threshold_senior,   # 60+
            ],
            [
                p.weeks_youth,      # 6
                p.weeks_standard,   # 5
                p.weeks_middle,     # 6
                p.weeks_senior,     # 7
            ],
        )

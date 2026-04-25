"""Hand-crafted training examples for BootstrapFewShot optimization."""

import dspy
import textwrap


def make_examples() -> list[dspy.Example]:
    """Return 3 gold-standard examples teaching OpenFisca conventions."""
    examples = [
        # --- Example 1: AHVG Art. 5 — employee contribution (float, MONTH) ---
        dspy.Example(
            legal_article_text=textwrap.dedent("""\
                Art. 5 — Beiträge von Einkommen aus unselbständiger Erwerbstätigkeit

                1 Vom Einkommen aus unselbständiger Erwerbstätigkeit, nachfolgend massgebender \
                Lohn genannt, wird ein Beitrag von 4,35 Prozent erhoben.

                2 Als massgebender Lohn gilt jedes Entgelt für in unselbständiger Stellung auf \
                bestimmte oder unbestimmte Zeit geleistete Arbeit."""),
            article_reference="AHVG Art. 5",
            openfisca_variable=textwrap.dedent("""\
                from openfisca_core.model_api import *
                from openfisca_switzerland.entities import Person


                class ahv_employee_contribution(Variable):
                    value_type = float
                    entity = Person
                    definition_period = MONTH
                    label = "AHV/IV/EO employee contribution (Art. 5 AHVG)"

                    def formula(person, period, parameters):
                        gross_salary = person("gross_monthly_salary", period)
                        rate = parameters(period).social_security.ahv.employee_rate
                        return gross_salary * rate"""),
            parameter_yaml=textwrap.dedent("""\
                description: AHV/IV/EO employee contribution rate (Art. 5 AHVG)
                metadata:
                  unit: /1
                  reference:
                    - title: "AHVG Art. 5 — Beiträge von Einkommen aus unselbständiger Erwerbstätigkeit"
                      href: "https://www.fedlex.admin.ch/eli/cc/63/837_843_843/de#art_5"
                values:
                  2024-01-01:
                    value: 0.0435
                  2020-01-01:
                    value: 0.0425
                  1997-01-01:
                    value: 0.0415"""),
            reasoning=textwrap.dedent("""\
                1. Art. 5 para. 1 levies a contribution of 4.35% on employment income.
                2. The contribution is a monetary amount → value_type = float.
                3. It applies to individual employees → entity = Person.
                4. Salary is typically monthly → definition_period = MONTH.
                5. The formula multiplies gross_monthly_salary by the employee_rate parameter.
                6. The rate (0.0435) is stored in a YAML parameter file with historical values."""),
        ),
        # --- Example 2: AHVG Art. 10 — self-employed contribution (float, YEAR) ---
        dspy.Example(
            legal_article_text=textwrap.dedent("""\
                Art. 10 — Beiträge der Selbständigerwerbenden

                1 Vom Einkommen aus selbständiger Erwerbstätigkeit wird ein Beitrag \
                von 8,1 Prozent erhoben.

                2 Das Einkommen aus selbständiger Erwerbstätigkeit wird für die \
                Berechnung des Beitrages auf die nächsten 100 Franken abgerundet."""),
            article_reference="AHVG Art. 10",
            openfisca_variable=textwrap.dedent("""\
                from openfisca_core.model_api import *
                from openfisca_switzerland.entities import Person


                class ahv_self_employed_contribution(Variable):
                    value_type = float
                    entity = Person
                    definition_period = YEAR
                    label = "AHV/IV/EO self-employed contribution (Art. 10 AHVG)"

                    def formula(person, period, parameters):
                        income = person("self_employment_income", period)
                        rate = parameters(period).social_security.ahv.self_employed_rate
                        return income * rate"""),
            parameter_yaml=textwrap.dedent("""\
                description: AHV/IV/EO self-employed contribution rate (Art. 10 AHVG)
                metadata:
                  unit: /1
                  reference:
                    - title: "AHVG Art. 10 — Beiträge der Selbständigerwerbenden"
                      href: "https://www.fedlex.admin.ch/eli/cc/63/837_843_843/de#art_10"
                values:
                  2024-01-01:
                    value: 0.081
                  2020-01-01:
                    value: 0.079
                  1997-01-01:
                    value: 0.077"""),
            reasoning=textwrap.dedent("""\
                1. Art. 10 para. 1 levies a contribution of 8.1% on self-employment income.
                2. The contribution is a monetary amount → value_type = float.
                3. It applies to self-employed individuals → entity = Person.
                4. Self-employment income is reported annually → definition_period = YEAR.
                5. The formula multiplies self_employment_income by the self_employed_rate parameter.
                6. The rate (0.081) is stored in a YAML parameter with historical values."""),
        ),
        # --- Example 3: AHVG Art. 3 — insurance obligation (bool, YEAR) ---
        dspy.Example(
            legal_article_text=textwrap.dedent("""\
                Art. 3 — Obligatorisch versicherte Personen

                1 Obligatorisch versichert sind natürliche Personen mit Wohnsitz in \
                der Schweiz.

                2 Obligatorisch versichert sind auch natürliche Personen, die in der \
                Schweiz eine Erwerbstätigkeit ausüben.

                3 Die Versicherungspflicht beginnt am 1. Januar nach Vollendung des \
                17. Altersjahres."""),
            article_reference="AHVG Art. 3",
            openfisca_variable=textwrap.dedent("""\
                from openfisca_core.model_api import *
                from openfisca_switzerland.entities import Person


                class ahv_insurance_obligation(Variable):
                    value_type = bool
                    entity = Person
                    definition_period = YEAR
                    label = "AHV insurance obligation (Art. 3 AHVG)"
                    default_value = False

                    def formula(person, period, parameters):
                        age = person("age", period)
                        has_residence = person("has_swiss_residence", period)
                        has_employment = person("has_swiss_employment", period)
                        return (age >= 18) * (has_residence + has_employment > 0)"""),
            parameter_yaml=textwrap.dedent("""\
                description: AHV insurance obligation age threshold (Art. 3 AHVG)
                metadata:
                  reference:
                    - title: "AHVG Art. 3 — Obligatorisch versicherte Personen"
                      href: "https://www.fedlex.admin.ch/eli/cc/63/837_843_843/de#art_3"
                values:
                  1948-01-01:
                    value: 18"""),
            reasoning=textwrap.dedent("""\
                1. Art. 3 defines who is obligatorily insured under AHV.
                2. The result is a yes/no determination → value_type = bool.
                3. It applies to individual persons → entity = Person.
                4. Insurance status is assessed yearly → definition_period = YEAR.
                5. Two conditions: Swiss residence OR Swiss employment, AND age >= 18.
                6. The age threshold (18, after completing 17th year) is stored as a parameter."""),
        ),
    ]

    return [
        ex.with_inputs("legal_article_text", "article_reference")
        for ex in examples
    ]

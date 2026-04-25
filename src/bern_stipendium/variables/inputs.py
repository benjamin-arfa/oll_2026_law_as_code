"""Input variables for the Bern scholarship eligibility module.

Inputs have no formula — their values must be supplied by the simulation.
Every legal condition in ABG / ABV is ultimately reducible to a combination
of these variables.
"""

from openfisca_core.variables import Variable
from openfisca_core.periods import YEAR
from openfisca_core.indexed_enums import Enum

from bern_stipendium.entities import Person, Household
from bern_stipendium.variables.enums import (
    Staatsangehoerigkeit,
    Ausbildungstyp,
    Ausbildungsstufe,
    WohnsitzGrundlage,
)


# ---------------------------------------------------------------------------
# 2.1 Stipendienrechtlicher Wohnsitz (Art. 12 Abs. 1, Art. 13 ABG)
# ---------------------------------------------------------------------------

class wohnsitz_grundlage(Variable):
    value_type = Enum
    possible_values = WohnsitzGrundlage
    default_value = WohnsitzGrundlage.keiner
    entity = Person
    definition_period = YEAR
    label = "Grundlage des stipendienrechtlichen Wohnsitzes (Art. 13 ABG)"
    reference = "https://www.belex.sites.be.ch/data/438.31/de"


# ---------------------------------------------------------------------------
# 2.2 Persönlicher Status — Staatsangehörigkeit (Art. 12 Abs. 1 lit. b–d ABG)
# ---------------------------------------------------------------------------

class staatsangehoerigkeit(Variable):
    value_type = Enum
    possible_values = Staatsangehoerigkeit
    default_value = Staatsangehoerigkeit.andere
    entity = Person
    definition_period = YEAR
    label = "Staatsangehörigkeitsstatus der Auszubildenden"
    reference = "Art. 12 Abs. 1 lit. b–d ABG"


# ---------------------------------------------------------------------------
# 3. Förderungswürdige Ausbildung (Art. 6, 7, 8 ABG)
# ---------------------------------------------------------------------------

class ausbildungstyp(Variable):
    value_type = Enum
    possible_values = Ausbildungstyp
    default_value = Ausbildungstyp.erstausbildung
    entity = Person
    definition_period = YEAR
    label = "Typ der besuchten Ausbildung (Art. 6 / 7 ABG)"


class ausbildungsstufe(Variable):
    value_type = Enum
    possible_values = Ausbildungsstufe
    default_value = Ausbildungsstufe.sekundarstufe_ii
    entity = Person
    definition_period = YEAR
    label = "Stufe der Ausbildung (Sekundar II / Tertiär)"
    reference = "Art. 10 ABG"


class ausbildungsstaette_anerkannt(Variable):
    value_type = bool
    default_value = False
    entity = Person
    definition_period = YEAR
    label = "Besucht eine vom Kanton anerkannte Ausbildungsstätte (Art. 8 ABG)"


class private_ausbildungsstaette(Variable):
    value_type = bool
    default_value = False
    entity = Person
    definition_period = YEAR
    label = "Es handelt sich um eine private Ausbildungsstätte"


class private_ausbildungsstaette_qualitaetsgesichert(Variable):
    value_type = bool
    default_value = True  # nicht-private Stätten werden ohnehin anerkannt
    entity = Person
    definition_period = YEAR
    label = (
        "Bei privater Ausbildungsstätte: ausreichende Qualitätssicherung "
        "vorhanden (Art. 8 ABG)"
    )


# ---------------------------------------------------------------------------
# 4. Art und Umfang — Ausbildungsjahr & Dauer (Art. 10, Art. 14 ABG)
# ---------------------------------------------------------------------------

class aktuelles_ausbildungsjahr(Variable):
    value_type = int
    default_value = 1
    entity = Person
    definition_period = YEAR
    label = "Laufendes Ausbildungsjahr in der aktuellen Ausbildung (1, 2, 3, …)"


class kumulierte_ausbildungsjahre(Variable):
    value_type = int
    default_value = 0
    entity = Person
    definition_period = YEAR
    label = (
        "Kumulierte Anzahl Ausbildungsjahre, für die bereits Beiträge "
        "geleistet wurden (Art. 14 Abs. 1 ABG: max. 12 Jahre)"
    )


# ---------------------------------------------------------------------------
# 5. Wirtschaftliche Verhältnisse (Bedürftigkeit, Art. 15–16 ABG)
# ---------------------------------------------------------------------------

class anerkannte_ausbildungskosten(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    label = (
        "Vom Kanton anerkannte Ausbildungs- und Lebenshaltungskosten "
        "(Art. 16 ABG)"
    )


class eigene_anrechenbare_mittel(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    label = "Eigene anrechenbare Mittel der Auszubildenden (Einkommen + Vermögen)"


class eltern_anrechenbare_mittel(Variable):
    value_type = float
    entity = Household
    definition_period = YEAR
    label = (
        "Anrechenbare Mittel der Eltern (Einkommen + Vermögen) — "
        "Art. 15 Abs. 2 ABG"
    )


class jahre_vollerwerbstaetigkeit(Variable):
    value_type = int
    default_value = 0
    entity = Person
    definition_period = YEAR
    label = (
        "Anzahl Jahre Vollerwerbstätigkeit der Auszubildenden — "
        "relevant für Verzicht auf Anrechnung elterlicher Mittel "
        "(Art. 15 Abs. 2 ABG: ab 4 Jahren Verzicht)"
    )


# ---------------------------------------------------------------------------
# 6. Persönliche Daten — Alter & Ausnahmegründe (Art. 14 ABG)
# ---------------------------------------------------------------------------

class alter(Variable):
    value_type = int
    entity = Person
    definition_period = YEAR
    label = "Alter der antragstellenden Person in Jahren"


class beruflicher_wiedereinstieg_nach_familienphase(Variable):
    value_type = bool
    default_value = False
    entity = Person
    definition_period = YEAR
    label = (
        "Antrag im Rahmen eines beruflichen Wiedereinstiegs nach "
        "Familienphase (Ausnahme zur Altersgrenze, Art. 14 Abs. 4 ABG)"
    )


class wichtige_gruende_altersausnahme(Variable):
    value_type = bool
    default_value = False
    entity = Person
    definition_period = YEAR
    label = (
        "Wichtige Gründe für eine Ausnahme von der Altersgrenze "
        "(Art. 14 Abs. 4 ABG)"
    )

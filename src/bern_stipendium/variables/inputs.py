"""Input variables for the Bern scholarship eligibility module.

Inputs have no formula — their values must be supplied by the simulation.
Every legal condition in ABG / ABV is ultimately reducible to a combination
of these variables.

Naming convention for financial inputs follows ABV references rather than
informal labels — e.g. ``total_einkuenfte_steuerveranlagung`` (Art. 15 Abs. 2
ABV: pre-deduction "Total der Einkünfte") instead of "steuerbares Einkommen"
(post-deduction).
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
    Wohnform,
    Zivilstand,
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


class in_ausbildung(Variable):
    value_type = bool
    default_value = False
    entity = Person
    definition_period = YEAR
    label = (
        "Person befindet sich in einer (im Sinne der ABV anerkannten) "
        "Ausbildung — relevant für die Integrationszulage (Art. 21 Abs. 1 "
        "ABV) und die Saldoteilung (Art. 23 Abs. 1 ABV)."
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
# 5. Wirtschaftliche Verhältnisse (Bedürftigkeit, Art. 15–16 ABG, Art. 13–34 ABV)
#
# Decomposed inputs aligned with the StG / Steuerveranlagung as referenced by
# Art. 15 Abs. 2 ABV. Each Person carries their own values; Familien- and
# Persönliches Budget formulas aggregate them through the Household roles.
# ---------------------------------------------------------------------------

class total_einkuenfte_steuerveranlagung(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    label = (
        "Total der Einkünfte gemäss rechtskräftiger Steuerveranlagung des "
        "Vorjahres (Art. 15 Abs. 2 ABV) — *vor* Abzügen, also nicht das "
        "post-Abzug-«steuerbare Einkommen» im StG-Sinn."
    )


class steuerbares_vermoegen(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    label = (
        "Steuerbares Vermögen gemäss rechtskräftiger Steuerveranlagung "
        "(Art. 16 / Art. 27 ABV)."
    )


class erwerbseinkommen(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    label = (
        "Erwerbseinkommen der Person im aktuellen Jahr — relevant für den "
        "Freibetrag im persönlichen Budget bei Tertiärstufe "
        "(Art. 26 Abs. 3 ABV: 6'000 CHF)."
    )


class ergaenzungsleistungen(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    label = (
        "Ergänzungsleistungen, soweit nicht zweckgebunden für "
        "krankheits-/behinderungsbedingte Kosten (Art. 15 Abs. 2 ABV)."
    )


class eigenmietwert(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    label = (
        "Eigenmietwert, sofern in den Einkünften enthalten — Abzug nach "
        "Art. 15 Abs. 6 lit. a ABV."
    )


class unterhaltsleistung_an_auszubildenden(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    label = (
        "Vom Elternteil geleistete Unterhaltsbeiträge an die Auszubildenden "
        "— Abzug nach Art. 15 Abs. 6 lit. b ABV."
    )


class bvg_beitraege_selbststaendig(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    label = (
        "Beiträge an die berufliche Vorsorge (2. Säule) bei selbstständig "
        "Erwerbenden, soweit nicht in den Einkünften abgezogen — Abzug "
        "nach Art. 15 Abs. 6 lit. c ABV."
    )


class saeule_3a_ueberschiessend(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    label = (
        "Beiträge an die gebundene Selbstvorsorge (Säule 3a), soweit sie "
        "8 % des oberen BVG-Grenzbetrags übersteigen — Abzug nach "
        "Art. 15 Abs. 6 lit. d ABV."
    )


class selbststaendig(Variable):
    value_type = bool
    default_value = False
    entity = Person
    definition_period = YEAR
    label = (
        "Person ist selbstständig erwerbend — löst den Vermögensfreibetrag "
        "von 30'000 CHF aus (Art. 16 / Anhang A11.9 ABV)."
    )


class bezahlte_steuern(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    label = (
        "Im Bemessungsjahr geschuldete Steuern (Bund / Kanton / Gemeinde) "
        "als situationsbedingte Kosten (Art. 22 ABV)."
    )


class fahrkosten_arbeit(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    label = (
        "Steuerlich abziehbare Fahrkosten zwischen Wohn- und Arbeitsstätte "
        "als situationsbedingte Kosten (Art. 22 ABV)."
    )


class auswaertige_verpflegung_arbeit(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    label = (
        "Notwendige Mehrkosten für auswärtige Verpflegung im Zusammenhang "
        "mit der Erwerbstätigkeit (Art. 22 ABV)."
    )


class krankenkasse_praemienverbilligung(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    label = (
        "Vom Kanton ausgerichtete Krankenkassen-Prämienverbilligung — wird "
        "von den anerkannten Prämien angemessen abgezogen (Art. 20 ABV)."
    )


# ---------------------------------------------------------------------------
# 5b. Auszubildenden-spezifische Eingaben (Wohnform, Zivilstand, Pendelzeit, …)
# ---------------------------------------------------------------------------

class wohnform(Variable):
    value_type = Enum
    possible_values = Wohnform
    default_value = Wohnform.elterlicher_haushalt
    entity = Person
    definition_period = YEAR
    label = (
        "Wohnform der Auszubildenden — bestimmt unter anderem die "
        "WG-Reduktion im Grundbedarf (Art. 18 ABV) und ob Art. 29 oder "
        "Art. 31 ABV für Lebenshaltungskosten zur Anwendung kommt."
    )


class zivilstand(Variable):
    value_type = Enum
    possible_values = Zivilstand
    default_value = Zivilstand.ledig
    entity = Person
    definition_period = YEAR
    label = "Zivilstand (Art. 14 / Art. 32 ABV)"


class pendelzeit_zu_eltern_minuten(Variable):
    value_type = int
    default_value = 0
    entity = Person
    definition_period = YEAR
    label = (
        "Wegzeit zwischen elterlichem Wohnort und Ausbildungsstätte in "
        "Minuten (Art. 30 Abs. 2 ABV: > 90 Minuten begründet eigenen "
        "Haushalt)."
    )


class andere_zwingende_gruende_eigener_haushalt(Variable):
    value_type = bool
    default_value = False
    entity = Person
    definition_period = YEAR
    label = (
        "Sonstige zwingende Gründe für einen eigenen Haushalt nach "
        "Art. 30 Abs. 2 ABV ('insbesondere' — die VO-Aufzählung ist nicht "
        "abschliessend)."
    )


class hat_eigene_kinder(Variable):
    value_type = bool
    default_value = False
    entity = Person
    definition_period = YEAR
    label = (
        "Auszubildende(r) hat eigene Kinder — relevant für Art. 30 Abs. 2 "
        "(eigener Haushalt) und Art. 32 Abs. 2 ABV (qualifizierte "
        "faktische Lebensgemeinschaft)."
    )


class jahre_faktische_partnerschaft(Variable):
    value_type = int
    default_value = 0
    entity = Person
    definition_period = YEAR
    label = (
        "Anzahl Jahre der faktischen Lebensgemeinschaft (Art. 32 Abs. 2 "
        "ABV: ab 5 Jahren Gleichstellung mit Ehepaaren)."
    )


class mahlzeiten_auswaerts_ausbildung_pro_jahr(Variable):
    value_type = int
    default_value = 0
    entity = Person
    definition_period = YEAR
    label = (
        "Anzahl im Ausbildungsjahr auswärts eingenommener Mahlzeiten — "
        "wird mit dem Ansatz nach A11.5 (10 CHF) multipliziert "
        "(Art. 33 Abs. 2 ABV, gilt für Auszubildende im elterlichen "
        "Haushalt)."
    )


class fahrkosten_ausbildung(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    label = (
        "Tatsächliche Fahrkosten zwischen Wohnort und Ausbildungsstätte "
        "auf Basis öffentlicher Verkehrsmittel (Art. 33 Abs. 1 ABV)."
    )


class kinderbetreuungskosten(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    label = (
        "Vom AAB im Einzelfall anerkannte Kinderbetreuungskosten "
        "(Art. 33 Abs. 3 ABV)."
    )


class tatsaechliche_ausbildungskosten(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    label = (
        "Tatsächliche Ausbildungskosten (Schulgeld, Prüfungsgebühren, "
        "obligatorisches Lehrmaterial). Im persönlichen Budget gilt der "
        "Höchstansatz nach A11.4 (Art. 28 Abs. 3 ABV); bei tieferen "
        "tatsächlichen Kosten werden diese anerkannt."
    )


# ---------------------------------------------------------------------------
# 5c. Haushaltsbezogene Eingaben (Familienkonstellation, Wohnkosten, Darlehen)
# ---------------------------------------------------------------------------

class parent_a_zahlt_unterhalt(Variable):
    value_type = bool
    default_value = False
    entity = Household
    definition_period = YEAR
    label = (
        "Elternteil A leistet gerichtlich oder behördlich festgelegte "
        "Unterhaltsbeiträge an die Auszubildenden (Art. 14 Abs. 4 ABV: "
        "kein eigenes Familienbudget für diesen Elternteil)."
    )


class parent_b_zahlt_unterhalt(Variable):
    value_type = bool
    default_value = False
    entity = Household
    definition_period = YEAR
    label = "Elternteil B unterhaltspflichtig — siehe parent_a_zahlt_unterhalt."


class wohnkosten_familienbudget_tatsaechlich(Variable):
    value_type = float
    entity = Household
    definition_period = YEAR
    label = (
        "Tatsächliche Wohnkosten (Mietzins inkl. Nebenkosten oder "
        "Hypothekarzinsen) der Eltern im Familienbudget — wird durch den "
        "Höchstansatz nach A11.2 (Art. 19 ABV) gekappt."
    )


class wohnkosten_persoenlich_tatsaechlich(Variable):
    value_type = float
    entity = Household
    definition_period = YEAR
    label = (
        "Tatsächliche Wohnkosten der Auszubildenden im eigenen Haushalt — "
        "wird durch den Höchstansatz nach A11.6 (Art. 31 ABV) gekappt."
    )


class kumulierte_darlehen(Variable):
    value_type = float
    default_value = 0.0
    entity = Person
    definition_period = YEAR
    label = (
        "Bisher kumulierte Darlehen pro Person — relevant für die "
        "Höchstgrenze nach Art. 11 Abs. 1 ABG (50'000 CHF)."
    )


# ---------------------------------------------------------------------------
# 5d. Legacy aggregate inputs — werden im Verlauf der Refaktorierung durch
# die berechneten Werte aus familienbudget.py / persoenliches_budget.py
# ersetzt. Sie bleiben hier dokumentarisch, bis die neuen Formeln aktiv sind.
# Schritt 8 der Implementierung entfernt sie.
# ---------------------------------------------------------------------------

class jahre_vollerwerbstaetigkeit(Variable):
    value_type = int
    default_value = 0
    entity = Person
    definition_period = YEAR
    label = (
        "Anzahl Jahre Vollerwerbstätigkeit der Auszubildenden — relevant "
        "für die Saldoteilung mit Verzicht (Art. 15 Abs. 2 ABG i.V.m. "
        "Art. 23 Abs. 3 ABV: ab 4 Jahren)."
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

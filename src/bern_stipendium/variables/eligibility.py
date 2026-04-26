"""Computed (derived) variables encoding the legal rules of ABG / ABV.

Every condition from the Bernese 'Gesetz über die Ausbildungsbeiträge' is
modelled as a small boolean ``Variable`` with a formula. A top-level
``stipendium_anspruch`` variable then combines them.

The amount of the scholarship is computed by ``stipendium_betrag``
(Art. 10, Art. 16 ABG: deficit calculation), the amount of any
loan by ``darlehen_betrag`` (Art. 10 Abs. 2, Art. 11 Abs. 1 ABG).

The financial calculation pipeline is split across three modules:

- ``familienbudget.py`` — Art. 13–24 ABV
- ``persoenliches_budget.py`` — Art. 25–33 ABV
- ``eligibility.py`` (this file) — eligibility gates and final aggregation
"""

from openfisca_core.variables import Variable
from openfisca_core.periods import YEAR
from numpy import where, maximum as max_

from bern_stipendium.entities import Person, Household


# ===========================================================================
# 2. Persönliche Anspruchsvoraussetzungen
# ===========================================================================

class hat_stipendienrechtlichen_wohnsitz_bern(Variable):
    value_type = bool
    entity = Person
    definition_period = YEAR
    label = "Stipendienrechtlicher Wohnsitz im Kanton Bern besteht"
    reference = "Art. 12 Abs. 1, Art. 13 ABG"

    def formula(person, period):
        grundlage = person("wohnsitz_grundlage", period)
        WG = grundlage.possible_values
        # Jede der vorgesehenen Grundlagen führt zum stipendienrechtlichen Wohnsitz;
        # nur 'keiner' ist ausgeschlossen.
        return grundlage != WG.keiner


class erfuellt_persoenlichen_status(Variable):
    value_type = bool
    entity = Person
    definition_period = YEAR
    label = (
        "Erfüllt die persönlichen Voraussetzungen zum Bürgerrecht / "
        "Aufenthaltsstatus (Art. 12 Abs. 1 lit. b–d ABG)"
    )

    def formula(person, period):
        status = person("staatsangehoerigkeit", period)
        S = status.possible_values
        return (
            (status == S.schweizer)
            + (status == S.eu_efta_niederlassung)
            + (status == S.aufenthaltsbewilligung_b)
            + (status == S.fluechtling_staatenlos)
        ) > 0


# ===========================================================================
# 3. Förderungswürdige Ausbildung
# ===========================================================================

class ausbildungstyp_anerkannt(Variable):
    value_type = bool
    entity = Person
    definition_period = YEAR
    label = "Ausbildungstyp ist nach Art. 6 / 7 ABG anerkannt"
    reference = "Art. 6, Art. 7 Abs. 2 ABG"

    def formula(person, period):
        typ = person("ausbildungstyp", period)
        T = typ.possible_values
        # Anerkannt: Vorbildung, Erst-/Zweitausbildung, Höhere Berufsbildung, Umschulung
        anerkannt = (
            (typ == T.vorbildung)
            + (typ == T.erstausbildung)
            + (typ == T.zweitausbildung)
            + (typ == T.hoehere_berufsbildung)
            + (typ == T.umschulung)
        ) > 0
        # Explizit ausgeschlossen (zur Sicherheit doppelt geprüft)
        ausgeschlossen = (
            (typ == T.primarstufe)
            + (typ == T.sekundarstufe_i)
            + (typ == T.weiterbildung)
            + (typ == T.zweite_hochschulausbildung)
        ) > 0
        return anerkannt * (1 - ausgeschlossen) > 0


class ausbildungsstaette_qualifiziert(Variable):
    value_type = bool
    entity = Person
    definition_period = YEAR
    label = "Ausbildungsstätte ist anerkannt (öffentlich oder privat mit QS)"
    reference = "Art. 8 ABG"

    def formula(person, period):
        anerkannt = person("ausbildungsstaette_anerkannt", period)
        privat = person("private_ausbildungsstaette", period)
        qs = person("private_ausbildungsstaette_qualitaetsgesichert", period)
        # Bei privaten Stätten ist zusätzlich Qualitätssicherung erforderlich.
        return anerkannt * where(privat, qs, True)


# ===========================================================================
# 4. Art und Umfang — Ausschluss von Stipendien
# ===========================================================================

class ist_zweitausbildung(Variable):
    value_type = bool
    entity = Person
    definition_period = YEAR
    label = "Es handelt sich um eine Zweitausbildung"

    def formula(person, period):
        typ = person("ausbildungstyp", period)
        return typ == typ.possible_values.zweitausbildung


class stipendium_grundsaetzlich_ausgeschlossen(Variable):
    value_type = bool
    entity = Person
    definition_period = YEAR
    label = (
        "Stipendium grundsätzlich ausgeschlossen — z. B. Zweitausbildung, "
        "für die nach Art. 10 Abs. 1 ABG nur Darlehen gewährt werden"
    )
    reference = "Art. 10 Abs. 1 ABG"

    def formula(person, period):
        return person("ist_zweitausbildung", period)


# ===========================================================================
# 5. Bedürftigkeit (Fehlbetragsrechnung) — Art. 15, 16 ABG
# ===========================================================================

class verzicht_auf_anrechnung_eltern(Variable):
    value_type = bool
    entity = Person
    definition_period = YEAR
    label = (
        "Auszubildende(r) erfüllt die Voraussetzungen von Art. 15 Abs. 2 "
        "ABG — ab 25 Jahren ODER ab 4 Jahren Vollerwerbstätigkeit. Die "
        "Rechtsfolge ist die Saldoteilung nach Art. 23 Abs. 3 ABV (50 % "
        "Familienbudget-Überschuss-Anteil), nicht eine pauschale Kürzung "
        "der elterlichen Mittel."
    )
    reference = "Art. 15 Abs. 2 ABG, Art. 23 Abs. 3 ABV"

    def formula(person, period, parameters):
        p = parameters(period).stipendium
        alter = person("alter", period)
        erwerbsjahre = person("jahre_vollerwerbstaetigkeit", period)
        return (
            (alter >= p.altersgrenze_verzicht_eltern)
            + (erwerbsjahre >= p.erwerbsjahre_verzicht_eltern)
        ) > 0


class fehlbetrag(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    label = (
        "Fehlbetrag — anerkannte Kosten minus anrechenbare Mittel, "
        "ggf. pro Kopf bei verheirateten/eingetragener Partnerschaft "
        "(Art. 16 ABG, Art. 32 Abs. 1 ABV)."
    )
    reference = "Art. 16 ABG"

    def formula(person, period):
        kosten = person("anerkannte_ausbildungskosten", period)
        mittel = person("anrechenbare_mittel_total", period)
        roh = max_(kosten - mittel, 0.0)

        # Art. 32 Abs. 1 ABV: bei Verheirateten / eingetragener Partnerschaft
        # Pro-Kopf-Anteil im persönlichen Budget. ``teiler`` ist 0 für
        # Personen, die nicht die Auszubildende sind — wir teilen daher
        # durch max(teiler, 1), und der Fehlbetrag dieser Personen ist
        # dank fehlender Ausbildungskosten/Mittel ohnehin 0.
        teiler = person("persoenlich_personen_anzahl", period)
        sicherer_teiler = max_(teiler, 1)
        return where(teiler > 1, roh / sicherer_teiler, roh)


class beduerftig(Variable):
    value_type = bool
    entity = Person
    definition_period = YEAR
    label = "Bedürftigkeit liegt vor (positiver Fehlbetrag)"
    reference = "Art. 15 Abs. 1 ABG"

    def formula(person, period):
        return person("fehlbetrag", period) > 0


# ===========================================================================
# 6. Zeitliche und altersmässige Begrenzungen — Art. 14 ABG
# ===========================================================================

class maximale_beitragsdauer_eingehalten(Variable):
    value_type = bool
    entity = Person
    definition_period = YEAR
    label = "Maximale Beitragsdauer von 12 Ausbildungsjahren noch nicht erreicht"
    reference = "Art. 14 Abs. 1 ABG"

    def formula(person, period, parameters):
        p = parameters(period).stipendium
        return person("kumulierte_ausbildungsjahre", period) < p.max_beitragsdauer_jahre


class altersgrenze_eingehalten(Variable):
    value_type = bool
    entity = Person
    definition_period = YEAR
    label = (
        "Altersgrenze (35 Jahre) eingehalten — oder Ausnahme greift"
    )
    reference = "Art. 14 Abs. 4 ABG"

    def formula(person, period, parameters):
        p = parameters(period).stipendium
        alter = person("alter", period)
        unter_grenze = alter < p.altersgrenze_anspruch
        wiedereinstieg = person("beruflicher_wiedereinstieg_nach_familienphase", period)
        wichtig = person("wichtige_gruende_altersausnahme", period)
        return unter_grenze + wiedereinstieg + wichtig > 0


# ===========================================================================
# Zusammenführung: Anspruch auf ein Stipendium
# ===========================================================================

class stipendium_anspruch(Variable):
    value_type = bool
    entity = Person
    definition_period = YEAR
    label = "Anspruch auf ein Stipendium nach ABG (Kanton Bern)"
    reference = "Art. 1–3, 6–10, 12–16 ABG"

    def formula(person, period):
        # Kumulative Voraussetzungen — ALLE müssen erfüllt sein.
        return (
            person("hat_stipendienrechtlichen_wohnsitz_bern", period)
            * person("erfuellt_persoenlichen_status", period)
            * person("ausbildungstyp_anerkannt", period)
            * person("ausbildungsstaette_qualifiziert", period)
            * (1 - person("stipendium_grundsaetzlich_ausgeschlossen", period))
            * person("beduerftig", period)
            * person("maximale_beitragsdauer_eingehalten", period)
            * person("altersgrenze_eingehalten", period)
        ) > 0


# ===========================================================================
# Höhe des Stipendiums (Art. 10, Art. 16 ABG)
# ===========================================================================

class stipendium_quote(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    label = (
        "Quote des Fehlbetrags, die als Stipendium gewährt wird — "
        "100 % in den ersten Jahren, 2/3 ab dem 4. Tertiärjahr."
    )
    reference = "Art. 10 ABG"

    def formula(person, period, parameters):
        p = parameters(period).stipendium
        stufe = person("ausbildungsstufe", period)
        S = stufe.possible_values
        jahr = person("aktuelles_ausbildungsjahr", period)

        ist_tertiaer = stufe == S.tertiaerstufe
        ueber_grenze = jahr > p.tertiaer_volle_quote_jahre  # > 3

        # Sekundarstufe II: immer volle Quote
        # Tertiärstufe: erste 3 Jahre volle Quote, danach 2/3-Quote
        return where(
            ist_tertiaer * ueber_grenze,
            p.tertiaer_reduzierte_quote,  # 2/3
            1.0,
        )


class stipendium_betrag(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    label = "Höhe des gewährten Stipendiums in CHF (Art. 10, 16 ABG)"

    def formula(person, period):
        anspruch = person("stipendium_anspruch", period)
        fehlbetrag = person("fehlbetrag", period)
        quote = person("stipendium_quote", period)
        return anspruch * fehlbetrag * quote


# ===========================================================================
# Höhe des Darlehens (Art. 10 Abs. 1+2, Art. 11 Abs. 1 ABG)
# ===========================================================================

class darlehen_anspruch(Variable):
    value_type = bool
    entity = Person
    definition_period = YEAR
    label = (
        "Anspruch auf ein Darlehen — Eligibilitätsvoraussetzungen ohne "
        "Stipendien-Ausschluss (für Zweitausbildung) und ohne Bedürftigkeits-"
        "Filter, da Darlehen auch bei Stipendien-Ausschluss gewährt werden."
    )
    reference = "Art. 10 Abs. 1, Art. 10 Abs. 2 ABG"

    def formula(person, period):
        return (
            person("hat_stipendienrechtlichen_wohnsitz_bern", period)
            * person("erfuellt_persoenlichen_status", period)
            * person("ausbildungstyp_anerkannt", period)
            * person("ausbildungsstaette_qualifiziert", period)
            * person("beduerftig", period)
            * person("maximale_beitragsdauer_eingehalten", period)
            * person("altersgrenze_eingehalten", period)
        ) > 0


class darlehen_betrag(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    label = (
        "Höhe des Darlehens in CHF — bei Zweitausbildung als reines "
        "Darlehen (Art. 10 Abs. 1 ABG), in der Tertiärstufe ab dem "
        "4. Jahr 1/3 des Fehlbetrags zusätzlich zum Stipendium "
        "(Art. 10 Abs. 2 ABG). Gekappt auf den lebenslangen Höchstbetrag "
        "(Art. 11 Abs. 1 ABG)."
    )
    reference = "Art. 10, Art. 11 Abs. 1 ABG"

    def formula(person, period, parameters):
        anspruch = person("darlehen_anspruch", period)
        fehl = person("fehlbetrag", period)

        # Variante A: Zweitausbildung — gesamter Fehlbetrag als Darlehen
        zweit = person("stipendium_grundsaetzlich_ausgeschlossen", period)

        # Variante B: Tertiärstufe ab Jahr 4 — 1/3 des Fehlbetrags
        stufe = person("ausbildungsstufe", period)
        S = stufe.possible_values
        ist_tertiaer = stufe == S.tertiaerstufe
        jahr = person("aktuelles_ausbildungsjahr", period)
        p = parameters(period).stipendium
        ueber_grenze = jahr > p.tertiaer_volle_quote_jahre
        anteil_tertiaer = ist_tertiaer * ueber_grenze * (1 - zweit)

        roh = where(
            zweit,
            fehl,
            anteil_tertiaer * fehl / 3.0,
        )

        # Lebenslange Höchstgrenze (Art. 11 Abs. 1 ABG)
        max_total = parameters(period).darlehen.maximalbetrag
        kumuliert = person("kumulierte_darlehen", period)
        verbleibend = max_(max_total - kumuliert, 0.0)
        return anspruch * where(roh < verbleibend, roh, verbleibend)

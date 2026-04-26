"""Persönliches Budget — Art. 25–33 ABV.

The persönliches Budget captures the trainee's own situation (and that of
their qualifying partner). Its deficit, after possibly absorbing flows
from the Familienbudget (Art. 23 surplus or Art. 24 deficit-share), is the
final ``fehlbetrag`` consumed by ``stipendium_betrag`` and ``darlehen_betrag``.
"""

from openfisca_core.variables import Variable
from openfisca_core.periods import YEAR
from numpy import maximum as max_
from numpy import minimum as min_
from numpy import where, select

from bern_stipendium.entities import Person, Household
from bern_stipendium.variables.enums import Wohnform, Zivilstand, Ausbildungsstufe


# ===========================================================================
# Partnerschaft & eigener Haushalt
# ===========================================================================

class faktische_partnerschaft_qualifiziert(Variable):
    value_type = bool
    entity = Person
    definition_period = YEAR
    label = (
        "Eine faktische Lebensgemeinschaft wird als qualifizierte "
        "Partnerschaft anerkannt — ab 5 Jahren Dauer ODER bei gemeinsamem "
        "Kind (Art. 32 Abs. 2 ABV)."
    )

    def formula(person, period, parameters):
        zivilstand = person("zivilstand", period)
        ist_faktisch = zivilstand == zivilstand.possible_values.faktische_partnerschaft
        jahre = person("jahre_faktische_partnerschaft", period)
        kinder = person("hat_eigene_kinder", period)
        min_jahre = parameters(period).partnerschaft.min_jahre_faktische_partnerschaft
        return ist_faktisch * ((jahre >= min_jahre) + kinder > 0)


class partner_qualifiziert(Variable):
    value_type = bool
    entity = Person
    definition_period = YEAR
    label = (
        "Auszubildende(r) hat einen für das persönliche Budget zu "
        "berücksichtigenden Partner — Ehe, eingetragene Partnerschaft "
        "oder qualifizierte faktische Lebensgemeinschaft (Art. 32 ABV)."
    )

    def formula(person, period):
        zivilstand = person("zivilstand", period)
        Z = zivilstand.possible_values
        verheiratet = zivilstand == Z.verheiratet
        ep = zivilstand == Z.eingetragene_partnerschaft
        faktisch = person("faktische_partnerschaft_qualifiziert", period)
        return (verheiratet + ep + faktisch) > 0


class eigener_haushalt_anerkannt(Variable):
    value_type = bool
    entity = Person
    definition_period = YEAR
    label = (
        "Eigener Haushalt der Auszubildenden ist anerkannt — vollendetes "
        "Mindestalter ODER zwingender Grund (Art. 30 ABV)."
    )
    reference = "Art. 30 ABV"

    def formula(person, period, parameters):
        p = parameters(period).eigener_haushalt
        alter = person("alter", period)
        ueber_mindestalter = alter >= p.mindestalter
        pendelzeit = person("pendelzeit_zu_eltern_minuten", period)
        # Art. 30 Abs. 2: "mehr als" eineinhalb Stunden — strikt grösser.
        lange_pendelzeit = pendelzeit > p.min_pendelzeit_minuten
        eigene_kinder = person("hat_eigene_kinder", period)
        partner = person("partner_qualifiziert", period)
        sonstige = person("andere_zwingende_gruende_eigener_haushalt", period)
        return (
            ueber_mindestalter
            + lange_pendelzeit
            + eigene_kinder
            + partner
            + sonstige
        ) > 0


# ===========================================================================
# Anzahl Personen im persönlichen Budget (Art. 32 Abs. 1 Pro-Kopf-Divisor)
# ===========================================================================

class persoenlich_personen_anzahl(Variable):
    value_type = int
    entity = Person
    definition_period = YEAR
    label = (
        "Anzahl Personen im persönlichen Budget — Auszubildende(r) plus "
        "qualifizierte(r) Partner(in)."
    )

    def formula(person, period):
        ist_aus = person.has_role(Household.AUSZUBILDENDER).astype(int)
        partner = person("partner_qualifiziert", period).astype(int)
        return ist_aus * (1 + partner)


# ===========================================================================
# Einnahmenseite des persönlichen Budgets — Art. 26, 27 ABV
# ===========================================================================

class persoenlich_einkommen(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    label = (
        "Anrechenbares Einkommen im persönlichen Budget (Art. 26 ABV) — "
        "Auszubildende plus qualifizierte(r) Partner(in), abzüglich "
        "Erwerbseinkommens-Freibetrag (Tertiärstufe), zuzüglich Anteil "
        "Familienbudget-Überschuss (Art. 23)."
    )

    def formula(person, period, parameters):
        ist_aus = person.has_role(Household.AUSZUBILDENDER)

        eigene_einkuenfte = person("total_einkuenfte_steuerveranlagung", period)
        partner_einkommen_hh = person.household.partner(
            "total_einkuenfte_steuerveranlagung", period,
        )
        partner_qualifiziert = person("partner_qualifiziert", period)
        # Partnereinkommen (vom Haushalt projiziert) wird der Auszubildenden
        # zugerechnet.
        partner_einkommen_aus = ist_aus * partner_qualifiziert * partner_einkommen_hh

        # Erwerbseinkommens-Freibetrag bei Tertiärstufe
        stufe = person("ausbildungsstufe", period)
        ist_tertiaer = stufe == stufe.possible_values.tertiaerstufe
        erwerbseinkommen = person("erwerbseinkommen", period)
        freibetrag = parameters(period).persoenliches_budget.erwerbseinkommen_freibetrag_tertiaer
        abzug = ist_aus * ist_tertiaer * min_(erwerbseinkommen, freibetrag)

        # Anteil Familienbudget-Überschuss (Art. 23 ABV) — bereits auf
        # Personenebene berechnet und nur für die Auszubildende > 0.
        familien_anteil = person("familienbudget_ueberschuss_anteil_persoenlich", period)

        return (
            ist_aus * eigene_einkuenfte
            + partner_einkommen_aus
            - abzug
            + familien_anteil
        )


class persoenlich_vermoegensanrechnung(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    label = (
        "Vermögensanrechnung im persönlichen Budget — 15 % des steuerbaren "
        "Vermögens der Auszubildenden plus ggf. qualifizierter Partner "
        "(Art. 27 ABV)."
    )

    def formula(person, period, parameters):
        quote = parameters(period).vermoegen.anrechnung_quote
        freibetrag_ss = parameters(period).vermoegen.freibetrag_selbststaendig

        ist_aus = person.has_role(Household.AUSZUBILDENDER)
        eigenes_vermoegen = person("steuerbares_vermoegen", period)
        eigene_selbst = person("selbststaendig", period)
        eigene_basis = max_(
            eigenes_vermoegen - eigene_selbst * freibetrag_ss, 0.0,
        )

        partner_vermoegen_hh = person.household.partner("steuerbares_vermoegen", period)
        partner_selbst_hh = person.household.partner("selbststaendig", period)
        partner_basis_hh = max_(
            partner_vermoegen_hh - partner_selbst_hh * freibetrag_ss, 0.0,
        )
        partner_qualifiziert = person("partner_qualifiziert", period)
        partner_basis = ist_aus * partner_qualifiziert * partner_basis_hh

        return quote * (ist_aus * eigene_basis + partner_basis)


# ===========================================================================
# Ausgabenseite des persönlichen Budgets
# ===========================================================================

class persoenlich_ausbildungskosten(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    label = (
        "Anerkannte Ausbildungskosten im persönlichen Budget — gekappt "
        "auf den Höchstansatz nach A11.4 (Art. 28 ABV)."
    )

    def formula(person, period, parameters):
        a = parameters(period).persoenliches_budget.ausbildungskosten_max
        stufe = person("ausbildungsstufe", period)
        S = stufe.possible_values
        max_ansatz = where(
            stufe == S.tertiaerstufe,
            a.tertiaerstufe,
            a.sekundarstufe_ii,
        )
        tatsaechlich = person("tatsaechliche_ausbildungskosten", period)
        ist_aus = person.has_role(Household.AUSZUBILDENDER)
        return ist_aus * min_(tatsaechlich, max_ansatz)


class persoenlich_grundbedarf(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    label = (
        "Grundbedarf im persönlichen Budget — Auszubildende mit eigenem "
        "Haushalt erhalten den Tabellenwert nach A11.1 für ihre Personen-"
        "anzahl. Andere: 0 (über Art. 24 Pro-Kopf-Anteil abgedeckt)."
    )

    def formula(person, period, parameters):
        gb = parameters(period).familienbudget.grundbedarf
        size = person("persoenlich_personen_anzahl", period)
        per_size = select(
            [size <= 1, size == 2, size == 3, size == 4,
             size == 5, size == 6, size == 7],
            [gb.eine_person, gb.zwei_personen, gb.drei_personen,
             gb.vier_personen, gb.fuenf_personen, gb.sechs_personen,
             gb.sieben_personen],
            default=gb.sieben_personen,
        )
        zusatz = max_(size - 7, 0) * gb.zusatzperson
        wohnform = person("wohnform", period)
        Wohnform_ = wohnform.possible_values
        wg_reduktion = (
            (size == 1)
            * (wohnform == Wohnform_.gemeinschaftlicher_haushalt)
            * gb.wg_reduktion
        )
        eigener = person("eigener_haushalt_anerkannt", period)
        ist_aus = person.has_role(Household.AUSZUBILDENDER)
        return ist_aus * eigener * (per_size + zusatz - wg_reduktion)


class persoenlich_wohnkosten(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    label = (
        "Anerkannte Wohnkosten im persönlichen Budget — Min(tatsächlich, "
        "Höchstansatz nach A11.6) bei eigenem Haushalt; sonst 0 (Art. 31 ABV)."
    )

    def formula(person, period, parameters):
        wk = parameters(period).persoenliches_budget.wohnkosten_max_eigener_haushalt
        size = person("persoenlich_personen_anzahl", period)
        max_ansatz = select(
            [size <= 1, size == 2, size == 3, size == 4],
            [wk.eine_person, wk.zwei_personen, wk.drei_personen,
             wk.vier_personen],
            default=wk.fuenf_plus,
        )
        tatsaechlich_hh = person.household("wohnkosten_persoenlich_tatsaechlich", period)
        eigener = person("eigener_haushalt_anerkannt", period)
        ist_aus = person.has_role(Household.AUSZUBILDENDER)
        return ist_aus * eigener * min_(tatsaechlich_hh, max_ansatz)


class persoenlich_krankenkasse(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    label = (
        "Anerkannte Krankenkassen-Grundversicherung im persönlichen "
        "Budget bei eigenem Haushalt — Auszubildende plus ggf. "
        "qualifizierter Partner (Art. 20 ABV, A11.7)."
    )

    def formula(person, period, parameters):
        kk = parameters(period).familienbudget.krankenkasse
        ist_aus = person.has_role(Household.AUSZUBILDENDER)
        eigener = person("eigener_haushalt_anerkannt", period)

        alter_aus = person("alter", period)
        praemie_aus = select(
            [alter_aus < 19, (alter_aus >= 19) * (alter_aus < 26)],
            [kk.kinder, kk.junge_erwachsene],
            default=kk.erwachsene,
        )
        pv_aus = person("krankenkasse_praemienverbilligung", period)
        netto_aus = max_(praemie_aus - pv_aus, 0.0)

        # Partner (über Haushalt projiziert)
        alter_p = person.household.partner("alter", period)
        praemie_p = select(
            [alter_p < 19, (alter_p >= 19) * (alter_p < 26)],
            [kk.kinder, kk.junge_erwachsene],
            default=kk.erwachsene,
        )
        pv_p = person.household.partner("krankenkasse_praemienverbilligung", period)
        netto_p = max_(praemie_p - pv_p, 0.0)
        partner_q = person("partner_qualifiziert", period)

        return ist_aus * eigener * (netto_aus + partner_q * netto_p)


class persoenlich_situationsbedingte_kosten(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    label = (
        "Situationsbedingte Kosten im persönlichen Budget — Fahrkosten "
        "Wohnort↔Ausbildungsstätte (Art. 33 Abs. 1), auswärtige Verpflegung "
        "im elterlichen Haushalt (Abs. 2), Kinderbetreuung (Abs. 3)."
    )

    def formula(person, period, parameters):
        ist_aus = person.has_role(Household.AUSZUBILDENDER)
        fahrkosten = person("fahrkosten_ausbildung", period)
        mahlzeiten_n = person("mahlzeiten_auswaerts_ausbildung_pro_jahr", period)
        ansatz = parameters(period).persoenliches_budget.auswaertige_verpflegung_pro_mahlzeit
        kibe = person("kinderbetreuungskosten", period)
        return ist_aus * (fahrkosten + mahlzeiten_n * ansatz + kibe)


# ===========================================================================
# Aggregation — anerkannte Ausbildungskosten und anrechenbare Mittel
# ===========================================================================

class anerkannte_ausbildungskosten(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    label = (
        "Total anerkannte Ausbildungs- und Lebenshaltungskosten im "
        "persönlichen Budget (Art. 16 ABG, Art. 28–33 ABV)."
    )
    reference = "Art. 16 ABG"

    def formula(person, period):
        ist_aus = person.has_role(Household.AUSZUBILDENDER)
        eigener = person("eigener_haushalt_anerkannt", period)
        ausbildungskosten = person("persoenlich_ausbildungskosten", period)
        situationsbedingt = person("persoenlich_situationsbedingte_kosten", period)

        # Eigener Haushalt: Lebenshaltungskosten direkt aus persönlichem
        # Budget; sonst Pro-Kopf-Anteil aus dem Familienbudget (Art. 24
        # i.V.m. Art. 29 ABV).
        eigene_lh = (
            person("persoenlich_grundbedarf", period)
            + person("persoenlich_wohnkosten", period)
            + person("persoenlich_krankenkasse", period)
        )
        familien_anteil = person("familienbudget_fehlbetrag_pro_kopf_anteil", period)

        return ist_aus * (
            ausbildungskosten
            + situationsbedingt
            + where(eigener, eigene_lh, familien_anteil)
        )


class anrechenbare_mittel_total(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    label = (
        "Total anrechenbare Mittel der Auszubildenden — Einkommen plus "
        "Vermögensanrechnung im persönlichen Budget (Art. 15, 26, 27 ABV)."
    )
    reference = "Art. 15 ABG"

    def formula(person, period):
        return (
            person("persoenlich_einkommen", period)
            + person("persoenlich_vermoegensanrechnung", period)
        )

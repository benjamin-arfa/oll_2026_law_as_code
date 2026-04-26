"""Familienbudget — Art. 13–24 ABV.

The Familienbudget aggregates the financial situation of the parents and the
children living with them, then either flows a *Pro-Kopf-Anteil* of its
deficit into the persönliches Budget (Art. 24 — applicant in parental home)
or a *50 % share* of its surplus to applicants who satisfy Art. 15 Abs. 2
ABG (Art. 23 Abs. 3).

Modelling note on Art. 14 Abs. 3 ABV (separated parents → separate
Familienbudgets per parent): we compute *one aggregate* Familienbudget
that sums per-parent contributions, weighted by ``parent_X_zaehlt`` flags
(in household, not paying Unterhalt). For typical separated-parent cases
this is a documented simplification — strictly per-Art. 14 Abs. 3 you would
compute two budgets and aggregate their flows; in practice the aggregate is
correct when only one parent contributes (Unterhalt or absent parent)
and conservative otherwise.
"""

from openfisca_core.variables import Variable
from openfisca_core.periods import YEAR
from numpy import maximum as max_
from numpy import minimum as min_
from numpy import where, select

from bern_stipendium.entities import Person, Household
from bern_stipendium.variables.enums import Wohnform


# ===========================================================================
# Helfer: zählt ein Elternteil im Familienbudget?
# ===========================================================================

class parent_a_zaehlt_im_familienbudget(Variable):
    value_type = bool
    entity = Household
    definition_period = YEAR
    label = (
        "Elternteil A wird im Familienbudget berücksichtigt — d. h. ist im "
        "Haushalt anwesend und nicht unterhaltspflichtig (Art. 14 Abs. 4 "
        "ABV)."
    )

    def formula(household, period):
        in_haushalt = household.nb_persons(Household.PARENT_A) > 0
        zahlt_unterhalt = household("parent_a_zahlt_unterhalt", period)
        return in_haushalt * (1 - zahlt_unterhalt) > 0


class parent_b_zaehlt_im_familienbudget(Variable):
    value_type = bool
    entity = Household
    definition_period = YEAR
    label = "Siehe parent_a_zaehlt_im_familienbudget."

    def formula(household, period):
        in_haushalt = household.nb_persons(Household.PARENT_B) > 0
        zahlt_unterhalt = household("parent_b_zahlt_unterhalt", period)
        return in_haushalt * (1 - zahlt_unterhalt) > 0


# ===========================================================================
# Haushaltsgrösse für das Familienbudget — Grundlage für Grundbedarf,
# Wohnkosten, Pro-Kopf-Anteil
# ===========================================================================

class haushaltsgroesse(Variable):
    value_type = int
    entity = Household
    definition_period = YEAR
    label = (
        "Anzahl Personen im Familienbudget: zählende Eltern + Kinder im "
        "Haushalt + Auszubildende(r), falls im elterlichen Haushalt "
        "lebend (Art. 14 Abs. 1, Art. 18 ABV)."
    )

    def formula(household, period):
        pa = household("parent_a_zaehlt_im_familienbudget", period)
        pb = household("parent_b_zaehlt_im_familienbudget", period)
        kinder = household.nb_persons(Household.KIND_IM_HAUSHALT)
        wohnform_aus = household.auszubildender("wohnform", period)
        Wohnform_ = wohnform_aus.possible_values
        auszubildende_im_familienhaushalt = (
            wohnform_aus == Wohnform_.elterlicher_haushalt
        )
        return (
            pa.astype(int)
            + pb.astype(int)
            + kinder
            + auszubildende_im_familienhaushalt.astype(int)
        )


class anzahl_personen_in_ausbildung_im_haushalt(Variable):
    value_type = int
    entity = Household
    definition_period = YEAR
    label = (
        "Anzahl Personen im Familienbudget, die sich in einer anerkannten "
        "Ausbildung befinden (für die Integrationszulage, Art. 21 Abs. 1 "
        "ABV)."
    )

    def formula(household, period):
        members = household.members
        in_ausbildung = members("in_ausbildung", period).astype(int)
        # Limit to Persons whose presence is reflected in the family budget.
        is_pa = members.has_role(Household.PARENT_A).astype(int)
        is_pb = members.has_role(Household.PARENT_B).astype(int)
        is_kind = members.has_role(Household.KIND_IM_HAUSHALT).astype(int)
        is_aus = members.has_role(Household.AUSZUBILDENDER).astype(int)

        pa_zaehlt = household("parent_a_zaehlt_im_familienbudget", period).astype(int)
        pb_zaehlt = household("parent_b_zaehlt_im_familienbudget", period).astype(int)
        wohnform_aus = household.auszubildender("wohnform", period)
        aus_drin = (
            wohnform_aus == wohnform_aus.possible_values.elterlicher_haushalt
        ).astype(int)

        # Project household-level flags to the matching person rows
        flag_pa = household.project(pa_zaehlt) * is_pa
        flag_pb = household.project(pb_zaehlt) * is_pb
        flag_aus = household.project(aus_drin) * is_aus
        # Children are always counted in the family budget
        return household.sum(
            in_ausbildung * (flag_pa + flag_pb + flag_aus + is_kind)
        )


class anzahl_kinder_in_ausbildung(Variable):
    value_type = int
    entity = Household
    definition_period = YEAR
    label = (
        "Anzahl Kinder (im Sinn von Geschwistern und ggf. Auszubildenden) "
        "in anerkannter Ausbildung — Divisor für Art. 23 Abs. 1 ABV."
    )

    def formula(household, period):
        members = household.members
        in_ausbildung = members("in_ausbildung", period).astype(int)
        is_kind = members.has_role(Household.KIND_IM_HAUSHALT).astype(int)
        is_aus = members.has_role(Household.AUSZUBILDENDER).astype(int)
        return household.sum(in_ausbildung * (is_kind + is_aus))


# ===========================================================================
# Einnahmenseite des Familienbudgets — Art. 15 / Art. 16 ABV
# ===========================================================================

def _per_parent_netto_einkommen(role_proj, period):
    """Per-Elternteil-Nettoeinkommen nach Art. 15 ABV (Total der Einkünfte
    + EL − Abzüge nach Art. 15 Abs. 6 lit. a–d)."""
    einkommen = role_proj("total_einkuenfte_steuerveranlagung", period)
    el = role_proj("ergaenzungsleistungen", period)
    abzuege = (
        role_proj("eigenmietwert", period)
        + role_proj("unterhaltsleistung_an_auszubildenden", period)
        + role_proj("bvg_beitraege_selbststaendig", period)
        + role_proj("saeule_3a_ueberschiessend", period)
    )
    return einkommen + el - abzuege


class familienbudget_einkommen(Variable):
    value_type = float
    entity = Household
    definition_period = YEAR
    label = "Anrechenbares Einkommen im Familienbudget (Art. 15 ABV)"
    reference = "https://www.belex.sites.be.ch/data/438.312/de"

    def formula(household, period):
        pa_netto = _per_parent_netto_einkommen(household.parent_a, period)
        pb_netto = _per_parent_netto_einkommen(household.parent_b, period)
        pa_zaehlt = household("parent_a_zaehlt_im_familienbudget", period)
        pb_zaehlt = household("parent_b_zaehlt_im_familienbudget", period)
        return pa_netto * pa_zaehlt + pb_netto * pb_zaehlt


def _per_parent_vermoegen(role_proj, period, freibetrag_ss):
    """Anrechenbares Vermögen pro Elternteil nach Art. 16 ABV — abzüglich
    Vermögensfreibetrag bei Selbstständigerwerbenden."""
    vermoegen = role_proj("steuerbares_vermoegen", period)
    selbst = role_proj("selbststaendig", period)
    abzug = selbst * freibetrag_ss
    return max_(vermoegen - abzug, 0.0)


class familienbudget_vermoegensanrechnung(Variable):
    value_type = float
    entity = Household
    definition_period = YEAR
    label = (
        "Vermögensanrechnung im Familienbudget — 15 % des steuerbaren "
        "Vermögens (Art. 16 ABV)."
    )

    def formula(household, period, parameters):
        quote = parameters(period).vermoegen.anrechnung_quote
        freibetrag_ss = parameters(period).vermoegen.freibetrag_selbststaendig
        pa_v = _per_parent_vermoegen(household.parent_a, period, freibetrag_ss)
        pb_v = _per_parent_vermoegen(household.parent_b, period, freibetrag_ss)
        pa_zaehlt = household("parent_a_zaehlt_im_familienbudget", period)
        pb_zaehlt = household("parent_b_zaehlt_im_familienbudget", period)
        return quote * (pa_v * pa_zaehlt + pb_v * pb_zaehlt)


# ===========================================================================
# Ausgabenseite des Familienbudgets
# ===========================================================================

class familienbudget_grundbedarf(Variable):
    value_type = float
    entity = Household
    definition_period = YEAR
    label = "Grundbedarf für den Lebensunterhalt im Familienbudget (Art. 18 / A11.1 ABV)"

    def formula(household, period, parameters):
        gb = parameters(period).familienbudget.grundbedarf
        size = household("haushaltsgroesse", period)
        # Tabelle 1–7, plus Zusatzbetrag pro Person ab 8
        # Rückgabe: Stufenwert für die jeweilige Grösse.
        per_size = select(
            [size <= 1, size == 2, size == 3, size == 4,
             size == 5, size == 6, size == 7],
            [gb.eine_person, gb.zwei_personen, gb.drei_personen, gb.vier_personen,
             gb.fuenf_personen, gb.sechs_personen, gb.sieben_personen],
            default=gb.sieben_personen,  # für > 7
        )
        # Für > 7 zusätzlich: + (size − 7) × zusatzperson
        zusatz = max_(size - 7, 0) * gb.zusatzperson
        # WG-Reduktion bei Einzelperson in WG/Heim/Internat
        wohnform_aus = household.auszubildender("wohnform", period)
        Wohnform_ = wohnform_aus.possible_values
        wg_reduktion = (
            (size == 1)
            * (wohnform_aus == Wohnform_.gemeinschaftlicher_haushalt)
            * gb.wg_reduktion
        )
        return per_size + zusatz - wg_reduktion


class familienbudget_wohnkosten(Variable):
    value_type = float
    entity = Household
    definition_period = YEAR
    label = (
        "Anerkannte Wohnkosten im Familienbudget — Min(tatsächlich, "
        "Höchstansatz nach A11.2) (Art. 19 ABV)."
    )

    def formula(household, period, parameters):
        wk = parameters(period).familienbudget.wohnkosten_max
        size = household("haushaltsgroesse", period)
        max_ansatz = select(
            [size <= 1, size == 2, size == 3, size == 4],
            [wk.eine_person, wk.zwei_personen, wk.drei_personen,
             wk.vier_personen],
            default=wk.fuenf_plus,
        )
        tatsaechlich = household("wohnkosten_familienbudget_tatsaechlich", period)
        return min_(tatsaechlich, max_ansatz)


def _krankenkasse_pro_person(alter, kk):
    """Krankenkassen-Grundversicherungsprämie nach Altersbracket
    (A11.7)."""
    return select(
        [alter < 19, (alter >= 19) * (alter < 26)],
        [kk.kinder, kk.junge_erwachsene],
        default=kk.erwachsene,
    )


class familienbudget_krankenkasse(Variable):
    value_type = float
    entity = Household
    definition_period = YEAR
    label = (
        "Anerkannte Krankenkassen-Grundversicherung im Familienbudget — "
        "alle zählenden Mitglieder, abzüglich Prämienverbilligung "
        "(Art. 20 ABV)."
    )

    def formula(household, period, parameters):
        kk = parameters(period).familienbudget.krankenkasse
        members = household.members
        alter = members("alter", period)
        praemie = _krankenkasse_pro_person(alter, kk)
        praemienverbilligung = members("krankenkasse_praemienverbilligung", period)

        # Welche Personen zählen im Familienbudget?
        is_pa = members.has_role(Household.PARENT_A).astype(int)
        is_pb = members.has_role(Household.PARENT_B).astype(int)
        is_kind = members.has_role(Household.KIND_IM_HAUSHALT).astype(int)
        is_aus = members.has_role(Household.AUSZUBILDENDER).astype(int)

        pa_zaehlt = household("parent_a_zaehlt_im_familienbudget", period).astype(int)
        pb_zaehlt = household("parent_b_zaehlt_im_familienbudget", period).astype(int)
        wohnform_aus = household.auszubildender("wohnform", period)
        aus_drin = (
            wohnform_aus == wohnform_aus.possible_values.elterlicher_haushalt
        ).astype(int)

        flag = (
            household.project(pa_zaehlt) * is_pa
            + household.project(pb_zaehlt) * is_pb
            + is_kind
            + household.project(aus_drin) * is_aus
        )
        netto_pro_person = max_(praemie - praemienverbilligung, 0.0)
        return household.sum(netto_pro_person * flag)


class familienbudget_integrationszulage(Variable):
    value_type = float
    entity = Household
    definition_period = YEAR
    label = (
        "Integrationszulage pro Person in Ausbildung (Art. 21 Abs. 1, "
        "A11.3 ABV) — vor Kappung mit Einkommensfreibetrag."
    )

    def formula(household, period, parameters):
        pro_person = parameters(period).familienbudget.integrationszulage_pro_person
        n = household("anzahl_personen_in_ausbildung_im_haushalt", period)
        return n * pro_person


class familienbudget_einkommensfreibetrag(Variable):
    value_type = float
    entity = Household
    definition_period = YEAR
    label = (
        "Einkommensfreibetrag pro Familienbudget (Art. 21 Abs. 2, A11.8 "
        "ABV) — vor Kappung."
    )

    def formula(household, period, parameters):
        return parameters(period).familienbudget.einkommensfreibetrag


class familienbudget_freibetraege_total(Variable):
    value_type = float
    entity = Household
    definition_period = YEAR
    label = (
        "Summe aus Integrationszulage und Einkommensfreibetrag, gekappt "
        "auf den Höchstbetrag (Art. 21 Abs. 3 ABV)."
    )

    def formula(household, period, parameters):
        izulage = household("familienbudget_integrationszulage", period)
        efb = household("familienbudget_einkommensfreibetrag", period)
        cap = parameters(period).familienbudget.integrationszulage_einkommensfreibetrag_max
        return min_(izulage + efb, cap)


def _per_parent_situation(role_proj, period):
    return (
        role_proj("bezahlte_steuern", period)
        + role_proj("fahrkosten_arbeit", period)
        + role_proj("auswaertige_verpflegung_arbeit", period)
    )


class familienbudget_situationsbedingte_kosten(Variable):
    value_type = float
    entity = Household
    definition_period = YEAR
    label = (
        "Situationsbedingte Kosten im Familienbudget — Steuern und "
        "Berufskosten der zählenden Eltern (Art. 22 ABV)."
    )

    def formula(household, period):
        pa_zaehlt = household("parent_a_zaehlt_im_familienbudget", period)
        pb_zaehlt = household("parent_b_zaehlt_im_familienbudget", period)
        return (
            _per_parent_situation(household.parent_a, period) * pa_zaehlt
            + _per_parent_situation(household.parent_b, period) * pb_zaehlt
        )


class familienbudget_lebenshaltungskosten(Variable):
    value_type = float
    entity = Household
    definition_period = YEAR
    label = (
        "Anerkannte Lebenshaltungskosten im Familienbudget — Summe aus "
        "Grundbedarf, Wohnkosten, Krankenkasse und situationsbedingten "
        "Kosten (Art. 17 ABV)."
    )

    def formula(household, period):
        return (
            household("familienbudget_grundbedarf", period)
            + household("familienbudget_wohnkosten", period)
            + household("familienbudget_krankenkasse", period)
            + household("familienbudget_situationsbedingte_kosten", period)
        )


# ===========================================================================
# Saldo des Familienbudgets und Verteilung ins persönliche Budget
# ===========================================================================

class familienbudget_saldo(Variable):
    value_type = float
    entity = Household
    definition_period = YEAR
    label = (
        "Saldo des Familienbudgets (Einnahmen − Ausgaben − Freibeträge). "
        "Positiv = Überschuss; negativ = Fehlbetrag."
    )

    def formula(household, period):
        einnahmen = (
            household("familienbudget_einkommen", period)
            + household("familienbudget_vermoegensanrechnung", period)
        )
        ausgaben = household("familienbudget_lebenshaltungskosten", period)
        freibetraege = household("familienbudget_freibetraege_total", period)
        return einnahmen - ausgaben - freibetraege


class familienbudget_ueberschuss_anteil_persoenlich(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    label = (
        "Anteil des Familienbudget-Überschusses, der der Auszubildenden "
        "ins persönliche Budget zugerechnet wird (Art. 23 ABV). Bei "
        "Anspruch nach Art. 15 Abs. 2 ABG nur 50 %."
    )

    def formula(person, period, parameters):
        saldo = person.household("familienbudget_saldo", period)
        n_kinder = person.household("anzahl_kinder_in_ausbildung", period)
        ueberschuss = max_(saldo, 0.0)
        anteil_pro_kind = ueberschuss / max_(n_kinder, 1)
        anteil_quote = parameters(period).familienbudget.art_23_abs_3_anteil_ueberschuss
        verzicht = person("verzicht_auf_anrechnung_eltern", period)
        # Nur die Auszubildende erhält die Zuteilung — der Wert ist auf
        # Personenebene per default 0 für alle anderen Rollen.
        ist_auszubildender = person.has_role(Household.AUSZUBILDENDER)
        return ist_auszubildender * anteil_pro_kind * where(verzicht, anteil_quote, 1.0)


class familienbudget_fehlbetrag_pro_kopf_anteil(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    label = (
        "Pro-Kopf-Anteil am Familienbudget-Fehlbetrag — wird bei "
        "Auszubildenden im elterlichen Haushalt als anrechenbare "
        "Lebenshaltungskosten ins persönliche Budget übernommen "
        "(Art. 24, Art. 29 ABV)."
    )

    def formula(person, period):
        saldo = person.household("familienbudget_saldo", period)
        size = person.household("haushaltsgroesse", period)
        fehlbetrag = max_(-saldo, 0.0)
        pro_kopf = fehlbetrag / max_(size, 1)
        ist_auszubildender = person.has_role(Household.AUSZUBILDENDER)
        return ist_auszubildender * pro_kopf

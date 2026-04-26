"""Entity definitions for the Bern (Switzerland) scholarship tax-benefit system.

The scholarship ('Stipendium') is awarded to a *Person* (the Auszubildende),
but the means-test (Bedürftigkeitsprüfung per Art. 15 ABG, Art. 13–24 ABV)
requires looking at the household — specifically the income/assets of the
applicant, their partner (if any), and their parents.

The Household entity uses unique roles per family member so that Art. 14 ABV
(separate Familienbudget per parent when not cohabiting; no budget for the
parent paying court-ordered Unterhalt) can be modelled correctly.
"""

from openfisca_core.entities import build_entity


Person = build_entity(
    key="person",
    plural="persons",
    label="A natural person.",
    doc="An individual — the applicant, their partner, parents, or a child "
        "in the household.",
    is_person=True,
)

Household = build_entity(
    key="household",
    plural="households",
    label="The household used for the Bedürftigkeitsprüfung.",
    doc="Group entity grouping the applicant with their parents, partner, "
        "and children-in-household for the two-budget Fehlbetragsrechnung "
        "(Art. 13–34 ABV).",
    roles=[
        {
            "key": "auszubildender",
            "plural": "auszubildende",
            "label": "Auszubildende(r)",
            "doc": "The applicant for the scholarship.",
            "max": 1,
        },
        {
            "key": "parent_a",
            "plural": "parents_a",
            "label": "Elternteil A",
            "doc": "First legal parent. Counted in the Familienbudget per "
                   "Art. 14 ABV unless they pay Unterhalt to the applicant "
                   "(Art. 14 Abs. 4) or do not live in the same household "
                   "as parent B (Art. 14 Abs. 3 — separate budgets).",
            "max": 1,
        },
        {
            "key": "parent_b",
            "plural": "parents_b",
            "label": "Elternteil B",
            "doc": "Second legal parent. Same treatment as parent_a.",
            "max": 1,
        },
        {
            "key": "partner",
            "plural": "partners",
            "label": "Partner",
            "doc": "Spouse, registered partner, or qualifying faktischer "
                   "Lebenspartner (Art. 32 Abs. 2 ABV). Income/assets enter "
                   "the persönliches Budget (Art. 25 ABV).",
            "max": 1,
        },
        {
            "key": "kind_im_haushalt",
            "plural": "kinder_im_haushalt",
            "label": "Kind im Haushalt",
            "doc": "A child living in the household. Counted for "
                   "Haushaltsgrösse (Grundbedarf Art. 18, Pro-Kopf-Anteil "
                   "Art. 24).",
        },
    ],
)

entities = [Person, Household]

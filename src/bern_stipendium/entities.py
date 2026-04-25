"""Entity definitions for the Bern (Switzerland) scholarship tax-benefit system.

The scholarship ('Stipendium') is awarded to a *Person* (the auszubildende
person), but the means-test (Bedürftigkeitsprüfung) requires looking at the
*Household* — specifically at the parents' income and assets.
"""

from openfisca_core.entities import build_entity


Person = build_entity(
    key="person",
    plural="persons",
    label="A natural person — applicant for the scholarship.",
    doc="The individual ('Auszubildende') who applies for an "
        "Ausbildungsbeitrag (Stipendium / Darlehen).",
    is_person=True,
)

Household = build_entity(
    key="household",
    plural="households",
    label="A household — the applicant and their parents.",
    doc="Group entity used to evaluate the parental means-test "
        "(Art. 15 ABG).",
    roles=[
        {
            "key": "applicant",
            "plural": "applicants",
            "label": "Applicant",
            "doc": "The person applying for the scholarship.",
            "max": 1,
        },
        {
            "key": "parent",
            "plural": "parents",
            "label": "Parent",
            "doc": "Legal parents of the applicant — their means are "
                   "in principle taken into account (Art. 15 Abs. 2 ABG).",
            "max": 2,
        },
    ],
)

entities = [Person, Household]

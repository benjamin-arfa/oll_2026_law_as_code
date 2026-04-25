"""Entities for the Swiss OpenFisca country package."""

from openfisca_core.entities import build_entity

Person = build_entity(
    key="person",
    plural="persons",
    label="An individual subject to Swiss social security and tax law.",
    is_person=True,
)

Household = build_entity(
    key="household",
    plural="households",
    label="A household, as defined for Swiss tax and social security purposes.",
    roles=[
        {
            "key": "parent",
            "plural": "parents",
            "label": "Parent",
            "max": 2,
        },
        {
            "key": "child",
            "plural": "children",
            "label": "Child",
        },
    ],
    containing_entities=["person"],
)

ENTITIES = [Person, Household]

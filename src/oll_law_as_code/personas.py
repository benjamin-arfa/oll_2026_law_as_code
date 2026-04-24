"""Five Swiss test personas for validating generated legal code."""

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal


@dataclass
class Persona:
    """A test persona with demographic profile and expected legal outcomes."""

    name: str
    age: int
    canton: str
    employment_status: str  # "employed", "self_employed", "retired", "student"
    marital_status: str  # "single", "married", "divorced", "widowed"
    annual_income: Decimal
    description: str = ""
    expected_values: dict[str, Decimal] = field(default_factory=dict)


# --- Test Personas ---

ANNA = Persona(
    name="Anna",
    age=35,
    canton="ZH",
    employment_status="employed",
    marital_status="single",
    annual_income=Decimal("85000"),
    description="Single employed woman in Zürich, standard case",
    expected_values={
        # TODO: Fill with computed expected AHV/tax values
        "ahv_contribution_employee": Decimal("0"),
        "ahv_contribution_employer": Decimal("0"),
        "federal_income_tax": Decimal("0"),
    },
)

BEAT = Persona(
    name="Beat",
    age=45,
    canton="BE",
    employment_status="self_employed",
    marital_status="married",
    annual_income=Decimal("120000"),
    description="Married self-employed man in Bern, tests self-employed AHV rates",
    expected_values={
        "ahv_contribution_self_employed": Decimal("0"),
        "federal_income_tax": Decimal("0"),
    },
)

CLARA = Persona(
    name="Clara",
    age=68,
    canton="GE",
    employment_status="retired",
    marital_status="widowed",
    annual_income=Decimal("0"),
    description="Retired widow in Genève, tests AHV pension calculation",
    expected_values={
        "ahv_pension_monthly": Decimal("0"),
    },
)

DAVID = Persona(
    name="David",
    age=22,
    canton="BS",
    employment_status="student",
    marital_status="single",
    annual_income=Decimal("12000"),
    description="Student with part-time job in Basel, tests AHV exemption threshold",
    expected_values={
        "ahv_contribution_employee": Decimal("0"),
        "ahv_exempt": True,  # type: ignore[dict-item]
    },
)

ELENA = Persona(
    name="Elena",
    age=40,
    canton="TI",
    employment_status="employed",
    marital_status="married",
    annual_income=Decimal("95000"),
    description="Cross-border worker (Grenzgängerin) in Ticino, tests international provisions",
    expected_values={
        "ahv_contribution_employee": Decimal("0"),
        "cross_border_applicable": True,  # type: ignore[dict-item]
    },
)

ALL_PERSONAS = [ANNA, BEAT, CLARA, DAVID, ELENA]

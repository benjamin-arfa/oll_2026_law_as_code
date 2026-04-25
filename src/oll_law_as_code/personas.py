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
        # CHF 85,000 / 12 = CHF 7,083.33 × 4.35% = CHF 308.12
        "ahv_employee_contribution": Decimal("308.12"),
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
        # CHF 120,000 × 8.1% = CHF 9,720.00
        "ahv_self_employed_contribution": Decimal("9720.00"),
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
        # Pension calculation not yet covered
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
        # AHV exemption threshold not yet covered
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
        # Cross-border provisions not yet covered
    },
)

ALL_PERSONAS = [ANNA, BEAT, CLARA, DAVID, ELENA]

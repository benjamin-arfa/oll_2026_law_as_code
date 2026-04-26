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
    extra_inputs: dict[str, dict[str, bool | int | float]] = field(default_factory=dict)


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

FRANCOIS = Persona(
    name="Francois",
    age=50,
    canton="GE",
    employment_status="employed",
    marital_status="married",
    annual_income=Decimal("150000"),
    description="Employer in Geneva whose employee caused a tort — tests CO 55 employer liability",
    expected_values={
        "or_employer_liability": Decimal("1"),  # True
    },
    extra_inputs={
        "is_employer_of_tortfeasor": {"2024": True},
        "employee_committed_tort": {"2024": True},
        "tort_in_course_of_employment": {"2024": True},
        "has_damage": {"2024": True},
        "has_causation": {"2024": True},
        "employer_proves_diligence": {"2024": False},
    },
)

GIULIA = Persona(
    name="Giulia",
    age=30,
    canton="VD",
    employment_status="employed",
    marital_status="single",
    annual_income=Decimal("70000"),
    description="Buyer of defective goods in Vaud — tests CO 197 warranty claims",
    expected_values={
        "or_warranty_claim_valid": Decimal("1"),  # True
    },
    extra_inputs={
        "has_sale_or_work_contract": {"2024": True},
        "has_defect": {"2024": True},
        "defect_before_risk_transfer": {"2024": True},
        "buyer_unaware_of_defect": {"2024": True},
        "timely_notice_of_defect": {"2024": True},
    },
)

HANS = Persona(
    name="Hans",
    age=55,
    canton="ZH",
    employment_status="self_employed",
    marital_status="divorced",
    annual_income=Decimal("200000"),
    description="Contractor in Zurich with overdue payment — tests CO 102 debtor default",
    expected_values={
        "or_debtor_in_default": Decimal("1"),  # True
    },
    extra_inputs={
        "obligation_is_due": {"2024": True},
        "debtor_has_been_summoned": {"2024": True},
        "debtor_failed_to_perform": {"2024": True},
    },
)

# --- Negative CO Personas (formulas should return False) ---

FRANCOIS_DILIGENT = Persona(
    name="FrancoisDiligent",
    age=50,
    canton="GE",
    employment_status="employed",
    marital_status="married",
    annual_income=Decimal("150000"),
    description="Employer who proves diligence — CO 55 employer liability should be False",
    expected_values={
        "or_employer_liability": Decimal("0"),  # False — diligence defense succeeds
    },
    extra_inputs={
        "is_employer_of_tortfeasor": {"2024": True},
        "employee_committed_tort": {"2024": True},
        "tort_in_course_of_employment": {"2024": True},
        "has_damage": {"2024": True},
        "has_causation": {"2024": True},
        "employer_proves_diligence": {"2024": True},  # KEY: defense succeeds
    },
)

GIULIA_LATE_NOTICE = Persona(
    name="GiuliaLateNotice",
    age=30,
    canton="VD",
    employment_status="employed",
    marital_status="single",
    annual_income=Decimal("70000"),
    description="Buyer who gave late notice of defect — CO 197 warranty claim should be False",
    expected_values={
        "or_warranty_claim_valid": Decimal("0"),  # False — timely notice missing
    },
    extra_inputs={
        "has_sale_or_work_contract": {"2024": True},
        "has_defect": {"2024": True},
        "defect_before_risk_transfer": {"2024": True},
        "buyer_unaware_of_defect": {"2024": True},
        "timely_notice_of_defect": {"2024": False},  # KEY: late notice
    },
)

HANS_NOT_SUMMONED = Persona(
    name="HansNotSummoned",
    age=55,
    canton="ZH",
    employment_status="self_employed",
    marital_status="divorced",
    annual_income=Decimal("200000"),
    description="Contractor whose debtor was never summoned — CO 102 default should be False",
    expected_values={
        "or_debtor_in_default": Decimal("0"),  # False — no interpellation
    },
    extra_inputs={
        "obligation_is_due": {"2024": True},
        "debtor_has_been_summoned": {"2024": False},  # KEY: no summons
        "debtor_failed_to_perform": {"2024": True},
    },
)

ALL_PERSONAS = [ANNA, BEAT, CLARA, DAVID, ELENA, FRANCOIS, GIULIA, HANS,
                FRANCOIS_DILIGENT, GIULIA_LATE_NOTICE, HANS_NOT_SUMMONED]

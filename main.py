"""Minimal working example: transform AHVG Art. 5 into OpenFisca code via Cerebras."""

import os
from pathlib import Path

from dotenv import load_dotenv
import dspy

from oll_law_as_code.pipeline import LegalTransformer
from oll_law_as_code.runner import run_generated_code
from oll_law_as_code.tracking import setup_tracking

AHVG_ART_5 = """\
Art. 5 — Beiträge von Einkommen aus unselbständiger Erwerbstätigkeit

1 Vom Einkommen aus unselbständiger Erwerbstätigkeit, nachfolgend massgebender \
Lohn genannt, wird ein Beitrag von 4,35 Prozent erhoben.

2 Als massgebender Lohn gilt jedes Entgelt für in unselbständiger Stellung auf \
bestimmte oder unbestimmte Zeit geleistete Arbeit.\
"""


def main():
    load_dotenv()

    # --- MLflow tracking ---
    experiment = setup_tracking()
    print(f"MLflow tracking active — experiment: {experiment}")

    # --- Configure LLM provider ---
    provider = os.environ.get("LLM_PROVIDER", "cerebras")
    if provider == "openjustice":
        from oll_law_as_code.openjustice_lm import OpenJusticeLM

        lm = OpenJusticeLM(
            model=os.environ.get("OPENJUSTICE_MODEL", "gpt-5.4-nano"),
            api_key=os.environ["OPENJUSTICE_API_KEY"],
        )
    else:
        lm = dspy.LM(
            "cerebras/qwen-3-235b-a22b-instruct-2507",
            api_key=os.environ["CEREBRAS_API_KEY"],
        )
    dspy.configure(lm=lm)

    # --- Run the pipeline ---
    transformer = LegalTransformer()

    optimized_path = Path("data/optimized/legal_transformer.json")
    if optimized_path.exists():
        transformer.load(optimized_path)
        print(f"Loaded optimized program from {optimized_path}")
    else:
        print("No optimized program found — using unoptimized pipeline")

    result = transformer(
        legal_article_text=AHVG_ART_5,
        article_reference="AHVG Art. 5",
    )

    # --- Print results ---
    print("\n" + "=" * 60)
    print("OPENFISCA VARIABLE")
    print("=" * 60)
    print(result.openfisca_variable)

    print("\n" + "=" * 60)
    print("PARAMETER YAML")
    print("=" * 60)
    print(result.parameter_yaml)

    print("\n" + "=" * 60)
    print("REASONING")
    print("=" * 60)
    print(result.reasoning)

    # --- Execute generated code ---
    print("\n" + "=" * 60)
    print("EXECUTION TEST (Anna: CHF 7,083.33/month)")
    print("=" * 60)

    anna_input = {
        "persons": {
            "anna": {
                "gross_monthly_salary": {"2024-01": 7083.33},
                "age": {"2024-01": 35},
            },
        },
        "households": {"hh": {"parents": ["anna"]}},
    }

    exec_result = run_generated_code(
        result.openfisca_variable,
        result.parameter_yaml,
        input_data=anna_input,
        period="2024-01",
    )

    if exec_result.success:
        print("Status: SUCCESS")
        for var_name, value in exec_result.computed_values.items():
            print(f"  {var_name} = {value:.2f}")
    else:
        print(f"Status: FAILED at stage '{exec_result.error_stage}'")
        print(f"  Error: {exec_result.error}")


if __name__ == "__main__":
    main()

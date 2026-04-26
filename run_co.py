"""Run CO article transformation and validate."""
import os
from pathlib import Path
from dotenv import load_dotenv
import dspy

from oll_law_as_code.pipeline import LegalTransformer
from oll_law_as_code.runner import run_generated_code

OR_ART_20 = """\
Art. 20 — Nullité

1 Le contrat est nul s'il a pour objet une chose impossible, illicite ou \
contraire aux mœurs.

2 Si le contrat n'est vicié que dans certaines de ses clauses, ces clauses \
sont seules frappées de nullité, à moins qu'il n'y ait lieu d'admettre que \
le contrat n'aurait pas été conclu sans elles.\
"""


def main():
    load_dotenv()
    lm = dspy.LM(
        "cerebras/qwen-3-235b-a22b-instruct-2507",
        api_key=os.environ["CEREBRAS_API_KEY"],
    )
    dspy.configure(lm=lm)

    transformer = LegalTransformer()
    optimized_path = Path("data/optimized/legal_transformer.json")
    if optimized_path.exists():
        transformer.load(optimized_path)

    result = transformer(
        legal_article_text=OR_ART_20,
        article_reference="OR Art. 20",
        available_variables="has_impossible_object\nhas_illicit_object\nhas_immoral_object\nhas_form_defect",
    )

    print("=== Generated Code ===")
    print(result.openfisca_variable)
    print("\n=== Generated YAML ===")
    print(result.parameter_yaml)
    print("\n=== Reasoning ===")
    print(result.reasoning)

    # Test with a null contract scenario (illicit object)
    test_input = {
        "persons": {"p1": {
            "has_illicit_object": {"2024": True},
            "has_impossible_object": {"2024": False},
            "has_immoral_object": {"2024": False},
            "has_form_defect": {"2024": False},
        }},
        "households": {"h1": {"parents": ["p1"]}},
    }

    exec_result = run_generated_code(
        result.openfisca_variable,
        result.parameter_yaml,
        input_data=test_input,
        period="2024",
    )

    if exec_result.success:
        print(f"\nExecution SUCCESS: {exec_result.computed_values}")
        # Expected: or_contract_nullity = True (1.0) because has_illicit_object is True
    else:
        print(f"\nExecution FAILED at stage '{exec_result.error_stage}': {exec_result.error}")


def evaluate_co():
    """Evaluate CO vs AHVG examples separately."""
    load_dotenv()
    lm = dspy.LM(
        "cerebras/qwen-3-235b-a22b-instruct-2507",
        api_key=os.environ["CEREBRAS_API_KEY"],
    )
    dspy.configure(lm=lm)

    from oll_law_as_code.examples import make_examples
    from oll_law_as_code.metric import code_quality_metric

    transformer = LegalTransformer()
    optimized_path = Path("data/optimized/legal_transformer.json")
    if optimized_path.exists():
        transformer.load(optimized_path)

    examples = make_examples()
    ahvg = [e for e in examples if "ahvg" in e.article_reference.lower()]
    co = [e for e in examples if "or " in e.article_reference.lower()]

    print(f"AHVG examples: {len(ahvg)}, CO examples: {len(co)}")

    for label, subset in [("AHVG", ahvg), ("CO", co)]:
        scores = []
        for ex in subset:
            pred = transformer(
                legal_article_text=ex.legal_article_text,
                article_reference=ex.article_reference,
                available_variables=getattr(ex, "available_variables", ""),
            )
            s = code_quality_metric(ex, pred)
            scores.append(s)
            print(f"  {ex.article_reference}: {s:.2f}")
        if scores:
            print(f"  {label} avg: {sum(scores)/len(scores):.2f}")


if __name__ == "__main__":
    main()

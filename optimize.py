"""One-time optimization: compile LegalTransformer with BootstrapFewShot."""

import os
from pathlib import Path

from dotenv import load_dotenv
import dspy

from oll_law_as_code.examples import make_examples
from oll_law_as_code.metric import code_quality_metric
from oll_law_as_code.pipeline import LegalTransformer
from oll_law_as_code.tracking import setup_tracking

OUTPUT_PATH = Path("data/optimized/legal_transformer.json")


def main():
    load_dotenv()

    # --- MLflow tracking ---
    experiment = setup_tracking()
    print(f"MLflow tracking active — experiment: {experiment}")

    # --- Configure Cerebras via LiteLLM ---
    lm = dspy.LM(
        "cerebras/qwen-3-235b-a22b-instruct-2507",
        api_key=os.environ["CEREBRAS_API_KEY"],
    )
    dspy.configure(lm=lm)

    # --- Training examples ---
    examples = make_examples()
    print(f"Loaded {len(examples)} training examples")

    # --- Optimize with BootstrapFewShot ---
    optimizer = dspy.BootstrapFewShot(
        metric=code_quality_metric,
        max_bootstrapped_demos=2,
        max_labeled_demos=3,
        max_rounds=1,
    )

    student = LegalTransformer()
    optimized = optimizer.compile(student=student, trainset=examples)
    print("Optimization complete")

    # --- Evaluate ---
    evaluator = dspy.Evaluate(devset=examples, metric=code_quality_metric)
    score = evaluator(optimized)
    print(f"Evaluation score: {score}")

    # --- Save ---
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    optimized.save(OUTPUT_PATH)
    print(f"Saved optimized program to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()

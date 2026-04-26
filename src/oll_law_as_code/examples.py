"""Load training examples for BootstrapFewShot from YAML data files."""

from pathlib import Path

import dspy
import yaml

DATA_DIR = Path(__file__).resolve().parents[2] / "data" / "examples"


def make_examples() -> list[dspy.Example]:
    """Load gold-standard examples from data/examples/*.yaml."""
    examples = []
    for path in sorted(DATA_DIR.glob("*.yaml")):
        with open(path) as f:
            data = yaml.safe_load(f)
        ex = dspy.Example(
            legal_article_text=data["legal_article_text"].rstrip("\n"),
            article_reference=data["article_reference"],
            available_variables="\n".join(data.get("available_variables") or []),
            openfisca_variable=data["openfisca_variable"].rstrip("\n"),
            parameter_yaml=data["parameter_yaml"].rstrip("\n"),
            reasoning=data["reasoning"].rstrip("\n"),
        )
        examples.append(ex)
    return [
        ex.with_inputs("legal_article_text", "article_reference", "available_variables")
        for ex in examples
    ]

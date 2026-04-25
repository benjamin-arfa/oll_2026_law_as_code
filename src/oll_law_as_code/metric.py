"""Evaluation metric for OpenFisca code quality."""

import ast
import re

import yaml


def _strip_code_fences(text: str) -> str:
    """Remove markdown code fences (```python, ```yaml, etc.) from text."""
    text = re.sub(r"^```\w*\n?", "", text.strip())
    text = re.sub(r"\n?```$", "", text.strip())
    return text


def code_quality_metric(example, prediction, trace=None) -> float | bool:
    """Score a prediction's OpenFisca output quality.

    Scoring:
        0.4 pts — openfisca_variable parses with ast.parse()
        0.3 pts — parameter_yaml parses with yaml.safe_load()
        0.3 pts — structural checks (0.075 each):
            - class ...(Variable) present
            - def formula( present
            - definition_period present
            - YAML has a dated entry (YYYY-MM-DD)

    During bootstrap (trace is not None), returns bool(score >= 0.7).
    Otherwise returns the raw float score.
    """
    score = 0.0

    code = _strip_code_fences(prediction.openfisca_variable)
    yaml_text = _strip_code_fences(prediction.parameter_yaml)

    # --- Python parsability (0.4) ---
    try:
        ast.parse(code)
        score += 0.4
    except SyntaxError:
        pass

    # --- YAML parsability (0.3) ---
    try:
        parsed_yaml = yaml.safe_load(yaml_text)
        if parsed_yaml is not None:
            score += 0.3
    except yaml.YAMLError:
        pass

    # --- Structural checks (0.075 each, total 0.3) ---
    if re.search(r"class\s+\w+\(Variable\)", code):
        score += 0.075

    if "def formula(" in code:
        score += 0.075

    if "definition_period" in code:
        score += 0.075

    if re.search(r"\d{4}-\d{2}-\d{2}", yaml_text):
        score += 0.075

    if trace is not None:
        return score >= 0.7

    return score

"""Evaluation metric for OpenFisca code quality — static + execution scoring."""

import ast
import logging
import re

import yaml

from oll_law_as_code.runner import _strip_code_fences, run_generated_code

log = logging.getLogger(__name__)


def code_quality_metric(example, prediction, trace=None) -> float | bool:
    """Score a prediction's OpenFisca output quality.

    Tier 1 — Static analysis (max 0.6):
        0.20 pts — openfisca_variable parses with ast.parse()
        0.15 pts — parameter_yaml parses with yaml.safe_load()
        0.25 pts — structural checks (0.0625 each):
            - class ...(Variable) present
            - def formula( present
            - definition_period present
            - YAML has a dated entry (YYYY-MM-DD)

    Tier 2 — Execution (max 0.4):
        0.15 pts — generated Variable loads into TaxBenefitSystem
        0.10 pts — simulation runs without error
        0.15 pts — computed value is within 1% of expected (if available)

    During bootstrap (trace is not None), returns bool(score >= 0.7).
    Otherwise returns the raw float score.
    """
    score = 0.0

    code = _strip_code_fences(prediction.openfisca_variable)
    yaml_text = _strip_code_fences(prediction.parameter_yaml)

    # ===== Tier 1: Static analysis (0.0 – 0.6) =====

    # --- Python parsability (0.20) ---
    parses_ok = False
    try:
        ast.parse(code)
        score += 0.20
        parses_ok = True
    except SyntaxError:
        pass

    # --- YAML parsability (0.15) ---
    try:
        parsed_yaml = yaml.safe_load(yaml_text)
        if parsed_yaml is not None:
            score += 0.15
    except yaml.YAMLError:
        pass

    # --- Structural checks (0.05 each, total 0.25) ---
    if re.search(r"class\s+\w+\(Variable\)", code):
        score += 0.05

    if "def formula(" in code:
        score += 0.05

    if "definition_period" in code:
        score += 0.05

    if re.search(r"\d{4}-\d{2}-\d{2}", yaml_text):
        score += 0.05

    if re.search(r"value_type\s*=\s*(bool|float|int)", code):
        score += 0.05

    # ===== Tier 2: Execution (0.0 – 0.4) =====

    if parses_ok:
        try:
            result = run_generated_code(code, yaml_text)
        except Exception:
            log.debug("Execution scoring failed unexpectedly", exc_info=True)
            result = None

        if result is not None:
            if result.error_stage not in ("parse", "load_variable"):
                # Variable loaded into TaxBenefitSystem
                score += 0.15

            if result.success:
                # Simulation ran and produced values
                score += 0.10

                # Check if computed value matches expected (if available)
                expected_code = getattr(example, "openfisca_variable", None)
                if expected_code and result.computed_values:
                    expected_code_clean = _strip_code_fences(expected_code)
                    try:
                        expected_result = run_generated_code(expected_code_clean)
                    except Exception:
                        expected_result = None

                    if expected_result and expected_result.success and expected_result.computed_values:
                        # Build value lists for comparison (by name or by position)
                        expected_vals = list(expected_result.computed_values.values())
                        computed_vals_by_name = result.computed_values
                        computed_vals_list = list(result.computed_values.values())

                        pairs = []
                        for var_name, expected_val in expected_result.computed_values.items():
                            if var_name in computed_vals_by_name:
                                pairs.append((expected_val, computed_vals_by_name[var_name]))

                        # If no name match but both have exactly one variable, compare by position
                        if not pairs and len(expected_vals) == 1 and len(computed_vals_list) == 1:
                            pairs.append((expected_vals[0], computed_vals_list[0]))

                        if pairs:
                            is_bool = bool(re.search(r"value_type\s*=\s*bool", code))
                            all_match = True
                            for expected_val, computed_val in pairs:
                                if is_bool:
                                    if (computed_val > 0.5) != (expected_val > 0.5):
                                        all_match = False
                                else:
                                    if expected_val != 0 and abs(computed_val - expected_val) / abs(expected_val) > 0.01:
                                        all_match = False
                                    elif expected_val == 0 and abs(computed_val) > 0.01:
                                        all_match = False
                            if all_match:
                                score += 0.15
                    elif not expected_result or not expected_result.success:
                        # Can't run expected code — fall back to basic check
                        if result.computed_values:
                            score += 0.15

    if trace is not None:
        return score >= 0.7

    return score

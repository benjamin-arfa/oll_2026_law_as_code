"""Execute generated OpenFisca code against a live TaxBenefitSystem."""

from __future__ import annotations

import ast
import logging
import re
from dataclasses import dataclass, field

from openfisca_core.model_api import Variable
from openfisca_core.simulations import SimulationBuilder

from openfisca_switzerland import CountryTaxBenefitSystem

log = logging.getLogger(__name__)

_CODE_FENCE_RE = re.compile(r"^```\w*\n?|```$", re.MULTILINE)


@dataclass
class ExecutionResult:
    """Outcome of running generated OpenFisca code."""

    success: bool
    computed_values: dict[str, float] = field(default_factory=dict)
    error: str = ""
    error_stage: str = ""  # "parse", "load_variable", "simulate", "calculate"


def _strip_code_fences(text: str) -> str:
    return _CODE_FENCE_RE.sub("", text).strip()


def _extract_variable_classes(namespace: dict) -> list[type]:
    """Extract all Variable subclasses defined in the exec'd namespace."""
    classes = []
    for obj in namespace.values():
        if (
            isinstance(obj, type)
            and issubclass(obj, Variable)
            and obj is not Variable
        ):
            classes.append(obj)
    return classes


def run_generated_code(
    code_string: str,
    yaml_string: str | None = None,
    input_data: dict | None = None,
    period: str = "2024-01",
) -> ExecutionResult:
    """Execute generated OpenFisca code and return computation results.

    Args:
        code_string: Python source code defining an OpenFisca Variable subclass.
        yaml_string: Optional YAML parameter definition (currently unused — parameters
            are loaded from the country package).
        input_data: Simulation input dict matching OpenFisca's JSON API format, e.g.
            ``{"persons": {"p1": {"gross_monthly_salary": {"2024-01": 7083.33}}},
              "households": {"h1": {"parents": ["p1"]}}}``.
        period: Period string for the simulation (default ``"2024-01"``).

    Returns:
        An :class:`ExecutionResult` with computed values or error details.
    """
    code_string = _strip_code_fences(code_string)

    if input_data is None:
        input_data = {
            "persons": {
                "p1": {
                    "gross_monthly_salary": {period: 7083.33},
                    # CO boolean defaults for smoke-testing
                    "has_offer": {period: True},
                    "has_acceptance": {period: True},
                    "has_concordance": {period: True},
                    "has_reciprocity": {period: True},
                    "has_unlawful_act": {period: True},
                    "has_damage": {period: True},
                    "has_causation": {period: True},
                    "has_intent": {period: True},
                },
            },
            "households": {"h1": {"parents": ["p1"]}},
        }

    # --- Stage 1: Parse ---
    try:
        ast.parse(code_string)
    except SyntaxError as exc:
        return ExecutionResult(
            success=False,
            error=f"SyntaxError: {exc}",
            error_stage="parse",
        )

    # --- Stage 2: Execute & extract Variable classes ---
    try:
        namespace: dict = {}
        exec(code_string, namespace)  # noqa: S102
    except Exception as exc:
        return ExecutionResult(
            success=False,
            error=f"{type(exc).__name__}: {exc}",
            error_stage="load_variable",
        )

    variable_classes = _extract_variable_classes(namespace)
    if not variable_classes:
        return ExecutionResult(
            success=False,
            error="No Variable subclass found in generated code",
            error_stage="load_variable",
        )

    # --- Stage 3: Add variables to TaxBenefitSystem ---
    try:
        tbs = CountryTaxBenefitSystem()
        for var_cls in variable_classes:
            tbs.add_variable(var_cls)
    except Exception as exc:
        return ExecutionResult(
            success=False,
            error=f"{type(exc).__name__}: {exc}",
            error_stage="load_variable",
        )

    # --- Stage 4: Build simulation and calculate ---
    try:
        builder = SimulationBuilder()
        simulation = builder.build_from_dict(tbs, input_data)
    except Exception as exc:
        return ExecutionResult(
            success=False,
            error=f"{type(exc).__name__}: {exc}",
            error_stage="simulate",
        )

    computed = {}
    try:
        for var_cls in variable_classes:
            name = var_cls.__name__
            result_array = simulation.calculate(name, period)
            computed[name] = float(result_array[0])
    except Exception as exc:
        return ExecutionResult(
            success=False,
            error=f"{type(exc).__name__}: {exc}",
            error_stage="calculate",
            computed_values=computed,
        )

    return ExecutionResult(success=True, computed_values=computed)


def run_batch_result(
    code_strings: list[str],
    input_data: dict | None = None,
    period: str = "2024-01",
) -> ExecutionResult:
    """Execute multiple generated code snippets together in a single TaxBenefitSystem.

    This is needed for cross-referencing variables: e.g. ``ahv_employer_contribution``
    calls ``person("ahv_employee_contribution", period)`` so both must be loaded
    into the same system.

    Args:
        code_strings: List of Python source strings, each defining one or more
            OpenFisca Variable subclasses.
        input_data: Simulation input dict (defaults to standard test persona).
        period: Period string for the simulation.

    Returns:
        An :class:`ExecutionResult` with computed values for *all* variables.
    """
    if input_data is None:
        input_data = {
            "persons": {"p1": {"gross_monthly_salary": {period: 7083.33}}},
            "households": {"h1": {"parents": ["p1"]}},
        }

    all_variable_classes: list[type] = []

    for i, code_string in enumerate(code_strings):
        code_string = _strip_code_fences(code_string)

        # --- Parse ---
        try:
            ast.parse(code_string)
        except SyntaxError as exc:
            return ExecutionResult(
                success=False,
                error=f"SyntaxError in snippet {i}: {exc}",
                error_stage="parse",
            )

        # --- Execute & extract Variable classes ---
        try:
            namespace: dict = {}
            exec(code_string, namespace)  # noqa: S102
        except Exception as exc:
            return ExecutionResult(
                success=False,
                error=f"{type(exc).__name__} in snippet {i}: {exc}",
                error_stage="load_variable",
            )

        classes = _extract_variable_classes(namespace)
        if not classes:
            return ExecutionResult(
                success=False,
                error=f"No Variable subclass found in snippet {i}",
                error_stage="load_variable",
            )
        all_variable_classes.extend(classes)

    # --- Add all variables to a single TaxBenefitSystem ---
    try:
        tbs = CountryTaxBenefitSystem()
        for var_cls in all_variable_classes:
            tbs.add_variable(var_cls)
    except Exception as exc:
        return ExecutionResult(
            success=False,
            error=f"{type(exc).__name__}: {exc}",
            error_stage="load_variable",
        )

    # --- Build simulation and calculate ---
    try:
        builder = SimulationBuilder()
        simulation = builder.build_from_dict(tbs, input_data)
    except Exception as exc:
        return ExecutionResult(
            success=False,
            error=f"{type(exc).__name__}: {exc}",
            error_stage="simulate",
        )

    computed = {}
    try:
        for var_cls in all_variable_classes:
            name = var_cls.__name__
            result_array = simulation.calculate(name, period)
            computed[name] = float(result_array[0])
    except Exception as exc:
        return ExecutionResult(
            success=False,
            error=f"{type(exc).__name__}: {exc}",
            error_stage="calculate",
            computed_values=computed,
        )

    return ExecutionResult(success=True, computed_values=computed)

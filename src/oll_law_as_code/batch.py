"""Batch orchestrator — process multiple legal articles with cross-reference support."""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field

from oll_law_as_code.pipeline import LegalTransformer
from oll_law_as_code.references import ArticleInput, topological_sort
from oll_law_as_code.registry import VariableInfo, VariableRegistry

log = logging.getLogger(__name__)

_CLASS_NAME_RE = re.compile(r"class\s+(\w+)\s*\(\s*Variable\s*\)")
_VALUE_TYPE_RE = re.compile(r"value_type\s*=\s*(\w+)")
_ENTITY_RE = re.compile(r"entity\s*=\s*(\w+)")
_PERIOD_RE = re.compile(r"definition_period\s*=\s*(\w+)")
_LABEL_RE = re.compile(r'label\s*=\s*["\']([^"\']+)["\']')


@dataclass
class BatchArticleResult:
    """Result for a single article in a batch run."""

    article_ref: str
    openfisca_variable: str
    parameter_yaml: str
    reasoning: str
    variable_name: str = ""
    success: bool = True
    error: str = ""


@dataclass
class BatchResult:
    """Result of processing a batch of articles."""

    results: list[BatchArticleResult] = field(default_factory=list)
    registry: VariableRegistry = field(default_factory=VariableRegistry)

    @property
    def all_code(self) -> list[str]:
        return [r.openfisca_variable for r in self.results if r.success]

    @property
    def all_yaml(self) -> list[str]:
        return [r.parameter_yaml for r in self.results if r.success]


def _extract_variable_info(code: str, article_ref: str) -> VariableInfo | None:
    """Extract VariableInfo from generated OpenFisca code."""
    name_match = _CLASS_NAME_RE.search(code)
    if not name_match:
        return None

    name = name_match.group(1)
    vtype = _VALUE_TYPE_RE.search(code)
    entity = _ENTITY_RE.search(code)
    period = _PERIOD_RE.search(code)
    label = _LABEL_RE.search(code)

    return VariableInfo(
        name=name,
        article_ref=article_ref,
        value_type=vtype.group(1) if vtype else "float",
        entity=entity.group(1) if entity else "Person",
        definition_period=period.group(1) if period else "MONTH",
        label=label.group(1) if label else "",
    )


def run_batch(
    articles: list[ArticleInput],
    transformer: LegalTransformer | None = None,
    initial_registry: VariableRegistry | None = None,
) -> BatchResult:
    """Process a batch of legal articles respecting cross-reference dependencies.

    1. Topologically sort articles so dependencies come first.
    2. For each article, provide accumulated registry context to the LLM.
    3. After each successful generation, register the new variable.

    Args:
        articles: List of articles to process.
        transformer: DSPy module to use.  Creates a new ``LegalTransformer``
            if not provided.
        initial_registry: Pre-populated registry (e.g. with base input variables).

    Returns:
        A :class:`BatchResult` with per-article results and the final registry.
    """
    if transformer is None:
        transformer = LegalTransformer()

    registry = initial_registry or VariableRegistry()
    sorted_articles = topological_sort(articles)
    batch_result = BatchResult(registry=registry)

    for article in sorted_articles:
        context = registry.render()
        log.info(
            "Processing %s (registry has %d variables)",
            article.article_ref,
            len(registry),
        )

        try:
            prediction = transformer.forward(
                legal_article_text=article.legal_article_text,
                article_reference=article.article_ref,
                available_variables=context,
            )

            code = prediction.openfisca_variable
            yaml_text = prediction.parameter_yaml
            reasoning = prediction.reasoning

            # Register the new variable
            info = _extract_variable_info(code, article.article_ref)
            var_name = info.name if info else ""
            if info:
                registry.register(info)

            batch_result.results.append(BatchArticleResult(
                article_ref=article.article_ref,
                openfisca_variable=code,
                parameter_yaml=yaml_text,
                reasoning=reasoning,
                variable_name=var_name,
            ))

        except Exception as exc:
            log.error("Failed to process %s: %s", article.article_ref, exc)
            batch_result.results.append(BatchArticleResult(
                article_ref=article.article_ref,
                openfisca_variable="",
                parameter_yaml="",
                reasoning="",
                success=False,
                error=str(exc),
            ))

    return batch_result

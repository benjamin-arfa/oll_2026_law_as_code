"""Reference extraction and topological sorting for cross-referencing legal articles."""

from __future__ import annotations

import re
from collections import defaultdict
from dataclasses import dataclass, field


# Matches patterns like "Art. 5", "Artikel 5", "Art. 5 AHVG", "Art. 5 Abs. 1"
_ART_REF_RE = re.compile(
    r"(?:Art(?:ikel)?\.?\s*(\d+))"       # article number
    r"(?:\s+Abs\.?\s*\d+)?"              # optional paragraph (Absatz)
    r"(?:\s+([A-ZÄÖÜ]{2,}))?",           # optional law abbreviation (e.g. AHVG)
    re.IGNORECASE,
)


@dataclass
class ArticleInput:
    """An article to be processed by the batch pipeline."""

    article_ref: str          # e.g. "AHVG Art. 5"
    legal_article_text: str
    law: str = ""             # e.g. "AHVG" — auto-extracted if blank

    def __post_init__(self) -> None:
        if not self.law:
            self.law = _extract_law(self.article_ref)


def _extract_law(article_ref: str) -> str:
    """Extract the law abbreviation from an article reference string."""
    for part in article_ref.split():
        if part.isalpha() and part.isupper() and len(part) >= 2:
            return part
    return ""


def _extract_article_number(article_ref: str) -> str:
    """Extract the article number from a reference like 'AHVG Art. 5' → '5'."""
    m = re.search(r"(\d+)", article_ref)
    return m.group(1) if m else ""


def extract_references(text: str, own_law: str = "") -> list[str]:
    """Extract article references from legal text.

    Returns a list of normalised reference strings, e.g. ``["AHVG Art. 5"]``.
    Only returns references to *other* articles (skips self-references).
    """
    refs: list[str] = []
    for m in _ART_REF_RE.finditer(text):
        art_num = m.group(1)
        law = m.group(2) or own_law
        if law:
            ref = f"{law.upper()} Art. {art_num}"
        else:
            ref = f"Art. {art_num}"
        refs.append(ref)
    # deduplicate while preserving order
    seen: set[str] = set()
    unique: list[str] = []
    for r in refs:
        if r not in seen:
            seen.add(r)
            unique.append(r)
    return unique


def _normalise_ref(article_ref: str) -> str:
    """Normalise an article reference for comparison.

    ``"AHVG Art. 5"`` and ``"Art. 5 AHVG"`` both become ``"AHVG Art. 5"``.
    """
    law = _extract_law(article_ref)
    num = _extract_article_number(article_ref)
    if law and num:
        return f"{law} Art. {num}"
    if num:
        return f"Art. {num}"
    return article_ref


def topological_sort(articles: list[ArticleInput]) -> list[ArticleInput]:
    """Sort articles so that dependencies are processed first.

    Uses Kahn's algorithm.  If an article references another article that is
    in the batch, the referenced article comes first.  Articles not in the
    batch are ignored (they may be pre-existing variables).
    """
    # Build ref → ArticleInput index
    ref_index: dict[str, ArticleInput] = {}
    for art in articles:
        ref_index[_normalise_ref(art.article_ref)] = art

    # Build adjacency: edges from article → articles it depends on
    # In-degree: how many articles must come before this one
    in_degree: dict[str, int] = {_normalise_ref(a.article_ref): 0 for a in articles}
    dependents: dict[str, list[str]] = defaultdict(list)  # dep → list of articles that depend on it

    for art in articles:
        norm = _normalise_ref(art.article_ref)
        own_refs = extract_references(art.legal_article_text, art.law)
        # Filter out self-references
        own_refs = [r for r in own_refs if _normalise_ref(r) != norm]
        for ref in own_refs:
            ref_norm = _normalise_ref(ref)
            if ref_norm in ref_index:
                in_degree[norm] += 1
                dependents[ref_norm].append(norm)

    # Kahn's algorithm
    queue = [ref for ref, deg in in_degree.items() if deg == 0]
    result: list[ArticleInput] = []

    while queue:
        # Sort for deterministic ordering among peers
        queue.sort()
        current = queue.pop(0)
        result.append(ref_index[current])
        for dep in dependents[current]:
            in_degree[dep] -= 1
            if in_degree[dep] == 0:
                queue.append(dep)

    if len(result) != len(articles):
        # Cycle detected — return original order as fallback
        processed = {_normalise_ref(a.article_ref) for a in result}
        for art in articles:
            if _normalise_ref(art.article_ref) not in processed:
                result.append(art)

    return result

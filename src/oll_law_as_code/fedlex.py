"""Fedlex SPARQL fetcher for Swiss federal legal articles."""

from __future__ import annotations

from dataclasses import dataclass

import httpx

FEDLEX_SPARQL_ENDPOINT = "https://fedlex.data.admin.ch/sparqlendpoint"


@dataclass
class LegalArticle:
    """A single article fetched from Fedlex."""

    uri: str
    reference: str  # e.g. "AHVG Art. 5"
    title: str
    text_de: str
    text_fr: str = ""
    text_it: str = ""


def build_article_query(sr_number: str, article_number: str) -> str:
    """Build a SPARQL query to fetch a specific article from Fedlex.

    Args:
        sr_number: Systematic collection number, e.g. "831.10" for AHVG.
        article_number: Article number, e.g. "5".

    Returns:
        SPARQL query string.
    """
    # TODO: Refine query based on actual Fedlex RDF schema exploration.
    return f"""
    PREFIX jolux: <http://data.legilux.public.lu/resource/ontology/jolux#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

    SELECT ?article ?title ?text
    WHERE {{
        ?act jolux:classifiedByTaxonomyEntry ?entry .
        ?entry rdfs:label ?srLabel .
        FILTER(CONTAINS(STR(?srLabel), "{sr_number}"))
        ?act jolux:hasArticle ?article .
        ?article rdfs:label ?title .
        ?article jolux:hasText ?text .
        FILTER(CONTAINS(STR(?title), "Art. {article_number}"))
    }}
    LIMIT 5
    """


async def fetch_article(sr_number: str, article_number: str) -> LegalArticle | None:
    """Fetch a legal article from the Fedlex SPARQL endpoint.

    Args:
        sr_number: Systematic collection number (e.g. "831.10" for AHVG).
        article_number: Article number (e.g. "5").

    Returns:
        A LegalArticle if found, else None.
    """
    query = build_article_query(sr_number, article_number)

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(
            FEDLEX_SPARQL_ENDPOINT,
            params={"query": query},
            headers={"Accept": "application/sparql-results+json"},
        )
        response.raise_for_status()
        data = response.json()

    bindings = data.get("results", {}).get("bindings", [])
    if not bindings:
        return None

    row = bindings[0]
    return LegalArticle(
        uri=row.get("article", {}).get("value", ""),
        reference=f"SR {sr_number} Art. {article_number}",
        title=row.get("title", {}).get("value", ""),
        text_de=row.get("text", {}).get("value", ""),
    )

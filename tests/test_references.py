"""Tests for reference extraction and topological sorting."""

from oll_law_as_code.references import (
    ArticleInput,
    extract_references,
    topological_sort,
)


class TestExtractReferences:
    def test_standard_article_reference(self):
        refs = extract_references("See Art. 5 AHVG for details.")
        assert "AHVG Art. 5" in refs

    def test_co_shorthand(self):
        refs = extract_references("As per CO 20, the contract is null.")
        assert "OR Art. 20" in refs

    def test_or_shorthand(self):
        refs = extract_references("According to OR 41, liability applies.")
        assert "OR Art. 41" in refs

    def test_multiple_references(self):
        text = "See CO 41, CO 55, and Art. 20."
        refs = extract_references(text)
        assert "OR Art. 41" in refs
        assert "OR Art. 55" in refs

    def test_deduplication(self):
        refs = extract_references("CO 20 says... as CO 20 clarifies...")
        assert refs.count("OR Art. 20") == 1

    def test_case_insensitive(self):
        refs = extract_references("co 97 applies here")
        assert "OR Art. 97" in refs

    def test_own_law_fallback(self):
        refs = extract_references("see Art. 10", own_law="AHVG")
        assert "AHVG Art. 10" in refs

    def test_empty_text(self):
        assert extract_references("") == []

    def test_no_references(self):
        assert extract_references("This text has no legal references.") == []


class TestTopologicalSort:
    def test_independent_articles_maintain_order(self):
        articles = [
            ArticleInput("AHVG Art. 5", "Employee contributions"),
            ArticleInput("AHVG Art. 10", "Self-employed contributions"),
        ]
        result = topological_sort(articles)
        assert len(result) == 2

    def test_dependent_article_comes_after(self):
        art5 = ArticleInput("AHVG Art. 5", "Employee rate")
        art14 = ArticleInput("AHVG Art. 14", "Employer must pay Art. 5 AHVG contribution")
        result = topological_sort([art14, art5])
        refs = [a.article_ref for a in result]
        assert refs.index("AHVG Art. 5") < refs.index("AHVG Art. 14")

    def test_cycle_falls_back_gracefully(self):
        a = ArticleInput("X Art. 1", "See Art. 2 X")
        b = ArticleInput("X Art. 2", "See Art. 1 X")
        result = topological_sort([a, b])
        assert len(result) == 2

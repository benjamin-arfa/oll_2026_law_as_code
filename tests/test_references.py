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


# ── Topological sort stress tests (TODO 9d) ──────────────────────────────────


class TestTopologicalSortStress:
    def test_deep_dependency_chain_10_articles(self):
        """10+ articles forming a deep linear dependency chain."""
        # Art 1 <- Art 2 <- Art 3 <- ... <- Art 10
        # Each article references the previous one
        articles = []
        for i in range(1, 11):
            if i == 1:
                text = "Base article with no references."
            else:
                text = f"This article depends on Art. {i - 1} TEST"
            articles.append(ArticleInput(f"TEST Art. {i}", text))

        result = topological_sort(articles)
        refs = [a.article_ref for a in result]
        assert len(refs) == 10

        # Each article must come after the one it depends on
        for i in range(2, 11):
            assert refs.index(f"TEST Art. {i - 1}") < refs.index(f"TEST Art. {i}"), (
                f"Art. {i - 1} should come before Art. {i}"
            )

    def test_diamond_dependency(self):
        """Diamond: A depends on B and C, both depend on D."""
        d = ArticleInput("LAW Art. 4", "Base article D.")
        b = ArticleInput("LAW Art. 2", "Depends on Art. 4 LAW for details.")
        c = ArticleInput("LAW Art. 3", "Also depends on Art. 4 LAW.")
        a = ArticleInput("LAW Art. 1", "Depends on Art. 2 LAW and Art. 3 LAW.")

        result = topological_sort([a, b, c, d])
        refs = [r.article_ref for r in result]
        assert len(refs) == 4

        # D must come before B and C
        assert refs.index("LAW Art. 4") < refs.index("LAW Art. 2")
        assert refs.index("LAW Art. 4") < refs.index("LAW Art. 3")
        # B and C must come before A
        assert refs.index("LAW Art. 2") < refs.index("LAW Art. 1")
        assert refs.index("LAW Art. 3") < refs.index("LAW Art. 1")

    def test_external_references_ignored(self):
        """Articles referencing articles NOT in the batch are correctly ignored."""
        a = ArticleInput("TEST Art. 1", "See Art. 999 TEST for external context.")
        b = ArticleInput("TEST Art. 2", "Independent article.")

        result = topological_sort([a, b])
        refs = [r.article_ref for r in result]
        # Both articles should still be present (external ref is ignored)
        assert len(refs) == 2
        assert "TEST Art. 1" in refs
        assert "TEST Art. 2" in refs

    def test_multiple_independent_subgraphs(self):
        """Two independent subgraphs don't interfere with each other."""
        # Subgraph 1: A1 -> A2
        a1 = ArticleInput("LAW Art. 1", "Base article.")
        a2 = ArticleInput("LAW Art. 2", "Depends on Art. 1 LAW.")
        # Subgraph 2: A3 -> A4
        a3 = ArticleInput("LAW Art. 3", "Another base article.")
        a4 = ArticleInput("LAW Art. 4", "Depends on Art. 3 LAW.")

        result = topological_sort([a4, a2, a3, a1])
        refs = [r.article_ref for r in result]
        assert len(refs) == 4
        assert refs.index("LAW Art. 1") < refs.index("LAW Art. 2")
        assert refs.index("LAW Art. 3") < refs.index("LAW Art. 4")

    def test_wide_fan_out(self):
        """One base article with many dependents (fan-out)."""
        base = ArticleInput("LAW Art. 1", "Foundation article.")
        dependents = [
            ArticleInput(f"LAW Art. {i}", f"Uses Art. 1 LAW.")
            for i in range(2, 8)
        ]

        result = topological_sort(dependents + [base])
        refs = [r.article_ref for r in result]
        assert refs[0] == "LAW Art. 1"  # base must come first
        assert len(refs) == 7

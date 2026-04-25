"""Tests for training example loading and structure."""

import dspy
import yaml

from oll_law_as_code.examples import DATA_DIR, make_examples


class TestExampleLoading:
    def test_make_examples_returns_list(self):
        examples = make_examples()
        assert isinstance(examples, list)

    def test_expected_example_count(self):
        examples = make_examples()
        assert len(examples) == 13, f"Expected 13 examples (4 AHVG + 1 OR41 + 8 new CO), got {len(examples)}"

    def test_all_examples_are_dspy_examples(self):
        for ex in make_examples():
            assert isinstance(ex, dspy.Example)

    def test_required_fields_present(self):
        for ex in make_examples():
            assert hasattr(ex, "legal_article_text") and ex.legal_article_text
            assert hasattr(ex, "article_reference") and ex.article_reference
            assert hasattr(ex, "openfisca_variable") and ex.openfisca_variable
            assert hasattr(ex, "parameter_yaml") and ex.parameter_yaml
            assert hasattr(ex, "reasoning") and ex.reasoning

    def test_input_fields_set(self):
        examples = make_examples()
        for ex in examples:
            inputs = ex.inputs()
            assert "legal_article_text" in inputs
            assert "article_reference" in inputs

    def test_ahvg_examples_present(self):
        refs = [ex.article_reference for ex in make_examples()]
        ahvg_refs = [r for r in refs if "AHVG" in r.upper()]
        assert len(ahvg_refs) >= 4, f"Expected at least 4 AHVG examples, got {len(ahvg_refs)}"

    def test_co_examples_present(self):
        refs = [ex.article_reference for ex in make_examples()]
        co_refs = [r for r in refs if "OR" in r.upper()]
        assert len(co_refs) >= 9, f"Expected at least 9 CO/OR examples, got {len(co_refs)}"


class TestYamlFiles:
    def test_all_yaml_files_parse(self):
        for path in sorted(DATA_DIR.glob("*.yaml")):
            with open(path) as f:
                data = yaml.safe_load(f)
            assert isinstance(data, dict), f"{path.name} did not parse to a dict"

    def test_yaml_files_have_required_keys(self):
        required = {"legal_article_text", "article_reference", "openfisca_variable", "parameter_yaml", "reasoning"}
        for path in sorted(DATA_DIR.glob("*.yaml")):
            with open(path) as f:
                data = yaml.safe_load(f)
            missing = required - set(data.keys())
            assert not missing, f"{path.name} missing keys: {missing}"

    def test_openfisca_variable_is_valid_python(self):
        import ast
        for path in sorted(DATA_DIR.glob("*.yaml")):
            with open(path) as f:
                data = yaml.safe_load(f)
            code = data["openfisca_variable"]
            try:
                ast.parse(code)
            except SyntaxError as e:
                pytest.fail(f"{path.name}: openfisca_variable has syntax error: {e}")

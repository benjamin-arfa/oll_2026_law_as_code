"""Tests for the DSPy pipeline signatures and modules."""

import dspy

from oll_law_as_code.pipeline import LegalToCode, LegalTransformer


class TestLegalToCodeSignature:
    def test_is_dspy_signature(self):
        assert issubclass(LegalToCode, dspy.Signature)

    def test_has_input_fields(self):
        fields = LegalToCode.model_fields
        assert "legal_article_text" in fields
        assert "article_reference" in fields
        assert "available_variables" in fields

    def test_has_output_fields(self):
        fields = LegalToCode.model_fields
        assert "openfisca_variable" in fields
        assert "parameter_yaml" in fields
        assert "reasoning" in fields


class TestLegalTransformer:
    def test_is_dspy_module(self):
        transformer = LegalTransformer()
        assert isinstance(transformer, dspy.Module)

    def test_has_transform_attribute(self):
        transformer = LegalTransformer()
        assert hasattr(transformer, "transform")

"""Tests for DSPy skill signatures and skill transformer."""

import dspy

from oll_law_as_code.skills import (
    BooleanDetermination,
    CrossReferenceResolution,
    LayeredClaimAnalysis,
)
from oll_law_as_code.skill_transformer import SkillAwareTransformer, SkillRouter


class TestSkillSignatures:
    def test_boolean_determination_is_signature(self):
        assert issubclass(BooleanDetermination, dspy.Signature)

    def test_layered_claim_is_signature(self):
        assert issubclass(LayeredClaimAnalysis, dspy.Signature)

    def test_cross_reference_is_signature(self):
        assert issubclass(CrossReferenceResolution, dspy.Signature)

    def test_boolean_has_required_fields(self):
        fields = BooleanDetermination.model_fields
        assert "legal_article_text" in fields
        assert "article_reference" in fields
        assert "openfisca_variable" in fields
        assert "parameter_yaml" in fields
        assert "reasoning" in fields

    def test_layered_has_condition_fields(self):
        fields = LayeredClaimAnalysis.model_fields
        assert "conditions_summary" in fields
        assert "objections_summary" in fields
        assert "exceptions_summary" in fields

    def test_cross_ref_has_referenced_articles(self):
        fields = CrossReferenceResolution.model_fields
        assert "referenced_articles" in fields


class TestSkillRouter:
    def test_router_is_signature(self):
        assert issubclass(SkillRouter, dspy.Signature)

    def test_router_has_skill_output(self):
        fields = SkillRouter.model_fields
        assert "skill" in fields
        assert "pattern_hints" in fields


class TestSkillAwareTransformer:
    def test_transformer_is_module(self):
        transformer = SkillAwareTransformer()
        assert isinstance(transformer, dspy.Module)

    def test_transformer_has_all_skills(self):
        transformer = SkillAwareTransformer()
        assert hasattr(transformer, "router")
        assert hasattr(transformer, "general")
        assert hasattr(transformer, "boolean")
        assert hasattr(transformer, "layered")
        assert hasattr(transformer, "cross_ref")

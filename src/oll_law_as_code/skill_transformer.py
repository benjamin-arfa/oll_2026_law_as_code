"""Skill-aware DSPy module that selects the right signature for each legal pattern."""

import dspy

from oll_law_as_code.pipeline import LegalToCode
from oll_law_as_code.skills import (
    BooleanDetermination,
    LayeredClaimAnalysis,
    CrossReferenceResolution,
)


class SkillRouter(dspy.Signature):
    """Classify a legal article to determine which transformation skill to use."""
    legal_article_text: str = dspy.InputField(desc="Full text of a Swiss legal article")
    article_reference: str = dspy.InputField(desc="Article identifier")
    skill: str = dspy.OutputField(
        desc="One of: 'numeric_calculation', 'boolean_determination', 'layered_claim', 'cross_reference'"
    )
    pattern_hints: str = dspy.OutputField(
        desc="Brief description of the legal pattern detected"
    )


class SkillAwareTransformer(dspy.Module):
    """Routes legal articles to the appropriate specialized transformation skill."""

    def __init__(self):
        super().__init__()
        self.router = dspy.Predict(SkillRouter)
        self.general = dspy.ChainOfThought(LegalToCode)
        self.boolean = dspy.ChainOfThought(BooleanDetermination)
        self.layered = dspy.ChainOfThought(LayeredClaimAnalysis)
        self.cross_ref = dspy.ChainOfThought(CrossReferenceResolution)

    def forward(self, legal_article_text: str, article_reference: str,
                available_variables: str = "", **kwargs):
        route = self.router(
            legal_article_text=legal_article_text,
            article_reference=article_reference,
        )
        skill = route.skill.strip().lower()

        if skill == "boolean_determination":
            return self.boolean(
                legal_article_text=legal_article_text,
                article_reference=article_reference,
                available_variables=available_variables,
                legal_pattern=kwargs.get("legal_pattern", "conjunctive"),
            )
        elif skill == "layered_claim":
            return self.layered(
                legal_article_text=legal_article_text,
                article_reference=article_reference,
                available_variables=available_variables,
                conditions_summary=kwargs.get("conditions_summary", ""),
                objections_summary=kwargs.get("objections_summary", ""),
                exceptions_summary=kwargs.get("exceptions_summary", ""),
            )
        elif skill == "cross_reference":
            return self.cross_ref(
                legal_article_text=legal_article_text,
                article_reference=article_reference,
                available_variables=available_variables,
                referenced_articles=kwargs.get("referenced_articles", ""),
            )
        else:
            return self.general(
                legal_article_text=legal_article_text,
                article_reference=article_reference,
                available_variables=available_variables,
            )

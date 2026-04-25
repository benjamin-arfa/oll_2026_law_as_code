"""DSPy signatures and modules for legal-text-to-OpenFisca transformation."""

import dspy


class LegalToCode(dspy.Signature):
    """Transform a Swiss legal article into executable OpenFisca code.

    Given the full text of a Swiss federal legal article (e.g. from AHVG),
    produce a Python Variable class for OpenFisca and a YAML parameter snippet
    that faithfully implement the legal logic.
    """

    legal_article_text: str = dspy.InputField(
        desc="Full text of a Swiss federal legal article (German, French, or Italian)"
    )
    article_reference: str = dspy.InputField(
        desc="Article identifier, e.g. 'AHVG Art. 5' or 'DBG Art. 25'"
    )
    available_variables: str = dspy.InputField(
        desc="Already-defined OpenFisca variables that may be referenced via person(\"<name>\", period). Empty string if none.",
        default="",
    )
    openfisca_variable: str = dspy.OutputField(
        desc="Python class inheriting from Variable with a formula() method implementing the legal logic"
    )
    parameter_yaml: str = dspy.OutputField(
        desc="YAML snippet defining OpenFisca parameters (rates, thresholds) referenced by the variable"
    )
    reasoning: str = dspy.OutputField(
        desc="Step-by-step explanation of how the legal text maps to the code"
    )


class LegalTransformer(dspy.Module):
    """Chain-of-thought module that reasons through legal text before generating code."""

    def __init__(self):
        super().__init__()
        self.transform = dspy.ChainOfThought(LegalToCode)

    def forward(self, legal_article_text: str, article_reference: str, available_variables: str = ""):
        return self.transform(
            legal_article_text=legal_article_text,
            article_reference=article_reference,
            available_variables=available_variables,
        )

"""DSPy signatures and modules for legal-text-to-code transformation."""

import dspy


class LegalToCode(dspy.Signature):
    """Transform a Swiss legal article into executable Catala/OpenFisca code.

    Given the full text of a Swiss federal legal article (e.g. from DFTA or AHV),
    produce structured executable code that faithfully implements the legal logic.
    """

    legal_article_text: str = dspy.InputField(
        desc="Full text of a Swiss federal legal article (German, French, or Italian)"
    )
    article_reference: str = dspy.InputField(
        desc="Article identifier, e.g. 'AHVG Art. 5' or 'DBG Art. 25'"
    )
    code: str = dspy.OutputField(
        desc="Executable code (Catala or OpenFisca/Python) implementing the legal logic"
    )
    reasoning: str = dspy.OutputField(
        desc="Step-by-step explanation of how the legal text maps to the code"
    )


class LegalTransformer(dspy.Module):
    """Chain-of-thought module that reasons through legal text before generating code."""

    def __init__(self):
        super().__init__()
        self.transform = dspy.ChainOfThought(LegalToCode)

    def forward(self, legal_article_text: str, article_reference: str):
        return self.transform(
            legal_article_text=legal_article_text,
            article_reference=article_reference,
        )

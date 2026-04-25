"""Specialized DSPy signatures for different legal pattern types in CO."""

import dspy


class BooleanDetermination(dspy.Signature):
    """Transform a Swiss legal article into a boolean determination variable.

    The article defines conditions for a legal determination (yes/no).
    Produce a Python Variable class with value_type = bool and a formula
    that combines boolean input variables using AND/OR logic.
    """
    legal_article_text: str = dspy.InputField(
        desc="Full text of a Swiss legal article defining conditions for a legal determination"
    )
    article_reference: str = dspy.InputField(
        desc="Article identifier, e.g. 'OR Art. 20' or 'OR Art. 97'"
    )
    available_variables: str = dspy.InputField(
        desc="Already-defined OpenFisca variables that may be referenced",
        default="",
    )
    legal_pattern: str = dspy.InputField(
        desc="Type of legal pattern: 'conjunctive' (all conditions required), 'disjunctive' (any condition suffices), or 'layered' (conditions + objections + exceptions)",
        default="conjunctive",
    )
    openfisca_variable: str = dspy.OutputField(
        desc="Python class with value_type = bool implementing boolean determination logic"
    )
    parameter_yaml: str = dspy.OutputField(
        desc="YAML snippet — typically reference-only for boolean determinations"
    )
    reasoning: str = dspy.OutputField(
        desc="Step-by-step explanation mapping legal conditions to boolean algebra"
    )


class LayeredClaimAnalysis(dspy.Signature):
    """Transform a Swiss legal claim structure into executable code.

    Swiss law uses a layered analysis: CONDITIONS (all must hold) then
    OBJECTIONS (any defeats the claim) then EXCEPTIONS (any also defeats).
    The formula pattern is:
        conditions_met AND NOT any_objection AND NOT any_exception
    """
    legal_article_text: str = dspy.InputField(
        desc="Full text of the main legal article(s)"
    )
    article_reference: str = dspy.InputField(
        desc="Article identifier"
    )
    available_variables: str = dspy.InputField(
        desc="Already-defined OpenFisca variables",
        default="",
    )
    conditions_summary: str = dspy.InputField(
        desc="Summary of the positive conditions that must be met for the claim"
    )
    objections_summary: str = dspy.InputField(
        desc="Summary of objections that defeat the claim (e.g., nullity, prescription)"
    )
    exceptions_summary: str = dspy.InputField(
        desc="Summary of exceptions that defeat the claim (e.g., compensation, novation)"
    )
    openfisca_variable: str = dspy.OutputField(
        desc="Python class implementing layered claim logic: conditions * (1 - objections) * (1 - exceptions)"
    )
    parameter_yaml: str = dspy.OutputField(
        desc="YAML parameter snippet"
    )
    reasoning: str = dspy.OutputField(
        desc="Step-by-step analysis following conditions > objections > exceptions"
    )


class CrossReferenceResolution(dspy.Signature):
    """Transform a legal article that heavily references other articles.

    The article delegates part of its logic to other articles. The generated
    code should call person("other_variable", period) for each referenced
    article that has already been coded.
    """
    legal_article_text: str = dspy.InputField(
        desc="Full text of the legal article with cross-references"
    )
    article_reference: str = dspy.InputField(
        desc="Article identifier"
    )
    available_variables: str = dspy.InputField(
        desc="Already-defined OpenFisca variables that can be referenced"
    )
    referenced_articles: str = dspy.InputField(
        desc="List of referenced article identifiers and what they determine"
    )
    openfisca_variable: str = dspy.OutputField(
        desc="Python class that delegates to existing variables via person() calls"
    )
    parameter_yaml: str = dspy.OutputField(
        desc="YAML parameter snippet"
    )
    reasoning: str = dspy.OutputField(
        desc="Explanation of which references are resolved and how"
    )

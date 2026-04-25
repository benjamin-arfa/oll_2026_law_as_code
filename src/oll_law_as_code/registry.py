"""Variable registry — tracks known OpenFisca variables for cross-reference context."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class VariableInfo:
    """Metadata for a registered OpenFisca variable."""

    name: str
    article_ref: str
    value_type: str = "float"
    entity: str = "Person"
    definition_period: str = "MONTH"
    label: str = ""


class VariableRegistry:
    """Accumulates known variables and renders compact context for the LLM prompt.

    Usage::

        registry = VariableRegistry()
        registry.register(VariableInfo(
            name="ahv_employee_contribution",
            article_ref="AHVG Art. 5",
            value_type="float",
            entity="Person",
            definition_period="MONTH",
            label="AHV/IV/EO employee contribution",
        ))
        context = registry.render()
    """

    def __init__(self) -> None:
        self._variables: dict[str, VariableInfo] = {}

    def register(self, info: VariableInfo) -> None:
        """Register a variable.  Overwrites if same name already exists."""
        self._variables[info.name] = info

    def get(self, name: str) -> VariableInfo | None:
        return self._variables.get(name)

    def all_names(self) -> list[str]:
        return list(self._variables)

    def __len__(self) -> int:
        return len(self._variables)

    def render(self) -> str:
        """Render a compact summary of all registered variables for LLM context.

        Returns an empty string when no variables are registered so the
        pipeline can treat it as a no-op default.
        """
        if not self._variables:
            return ""

        lines = ["Available OpenFisca variables you may reference with person(\"<name>\", period):"]
        for info in self._variables.values():
            desc = f"  - {info.name} ({info.value_type}, {info.entity}, {info.definition_period})"
            if info.label:
                desc += f" — {info.label}"
            desc += f"  [from {info.article_ref}]"
            lines.append(desc)
        return "\n".join(lines)

"""Custom DSPy LM provider for the OpenJustice API.

OpenJustice exposes a non-standard SSE streaming endpoint at
``POST /conversations/stream`` instead of the OpenAI-compatible
``/v1/chat/completions``.  This adapter bridges the gap so that DSPy
pipelines can run against OpenJustice models (GPT-5.4-nano, Claude, …).
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from typing import Any

import httpx
import dspy

_DEFAULT_BASE = "https://api.staging.openjustice.ai"


# ---------------------------------------------------------------------------
# Lightweight containers that mimic the OpenAI response shape expected by
# ``dspy.BaseLM._process_lm_response``.
# ---------------------------------------------------------------------------

@dataclass
class _Message:
    content: str
    role: str = "assistant"


@dataclass
class _Choice:
    message: _Message
    index: int = 0


@dataclass
class _Usage:
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0

    def __iter__(self):
        yield "prompt_tokens", self.prompt_tokens
        yield "completion_tokens", self.completion_tokens
        yield "total_tokens", self.total_tokens


@dataclass
class _Response:
    choices: list[_Choice]
    model: str = ""
    usage: _Usage = field(default_factory=_Usage)


# ---------------------------------------------------------------------------
# The custom LM class
# ---------------------------------------------------------------------------

class OpenJusticeLM(dspy.BaseLM):
    """DSPy language-model adapter for the OpenJustice streaming API."""

    def __init__(
        self,
        model: str = "gpt-5.4-nano",
        api_key: str | None = None,
        api_base: str | None = None,
        **kwargs: Any,
    ):
        super().__init__(model=model, model_type="chat", **kwargs)
        self.api_key = api_key or os.environ.get("OPENJUSTICE_API_KEY", "")
        self.api_base = (api_base or _DEFAULT_BASE).rstrip("/")

    # -- core interface -----------------------------------------------------

    def forward(
        self,
        prompt: str | None = None,
        messages: list[dict[str, Any]] | None = None,
        **kwargs: Any,
    ) -> _Response:
        text = self._messages_to_prompt(prompt, messages)
        full_text = self._stream_completion(text)
        return _Response(
            choices=[_Choice(message=_Message(content=full_text))],
            model=self.model,
        )

    # -- helpers ------------------------------------------------------------

    @staticmethod
    def _messages_to_prompt(
        prompt: str | None,
        messages: list[dict[str, Any]] | None,
    ) -> str:
        """Flatten DSPy messages into a single prompt string."""
        if prompt:
            return prompt
        if not messages:
            return ""
        parts: list[str] = []
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            if role == "system":
                parts.append(f"[System]\n{content}")
            elif role == "assistant":
                parts.append(f"[Assistant]\n{content}")
            else:
                parts.append(content)
        return "\n\n".join(parts)

    def _stream_completion(self, prompt_text: str) -> str:
        """POST to ``/conversations/stream`` and collect SSE text chunks."""
        url = f"{self.api_base}/conversations/stream"
        payload = {
            "message": prompt_text,
            "model": self.model,
            "resources": [],
            "isWebSearchEnabled": False,
        }
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "text/event-stream",
        }

        chunks: list[str] = []

        with httpx.Client(timeout=300.0) as client:
            with client.stream("POST", url, json=payload, headers=headers) as resp:
                resp.raise_for_status()
                event_type = ""
                for line in resp.iter_lines():
                    if line.startswith("event:"):
                        event_type = line[len("event:"):].strip()
                        if event_type in ("done", "saved"):
                            break
                        continue

                    if line.startswith("data:"):
                        if event_type == "metadata":
                            event_type = ""
                            continue
                        raw = line[len("data:"):].strip()
                        if not raw:
                            continue
                        try:
                            data = json.loads(raw)
                        except json.JSONDecodeError:
                            continue

                        error = data.get("error")
                        if error:
                            raise RuntimeError(
                                f"OpenJustice API error (model={self.model}): {error}"
                            )

                        text = data.get("text", "")
                        if text:
                            chunks.append(text)
                        event_type = ""

        return "".join(chunks)

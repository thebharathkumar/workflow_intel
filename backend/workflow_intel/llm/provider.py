"""Provider abstraction for the optional LLM enhancement layer.

``NullProvider`` is the default and reports itself unavailable, so agents run their deterministic
path. ``AnthropicProvider`` calls ``claude-opus-4-8`` with **structured outputs** so responses
validate directly against a Pydantic schema. Any failure returns ``None`` and the caller falls
back to heuristics — the LLM layer can only add quality, never remove reliability.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Generic, Protocol, TypeVar

from pydantic import BaseModel

from workflow_intel.config import Settings

T = TypeVar("T", bound=BaseModel)


@dataclass
class LLMResult(Generic[T]):
    data: T
    input_tokens: int = 0
    output_tokens: int = 0
    model: str | None = None


class LLMProvider(Protocol):
    """A provider that can return schema-validated structured data for a prompt."""

    @property
    def available(self) -> bool: ...

    @property
    def model(self) -> str: ...

    async def structured(self, system: str, prompt: str, schema: type[T]) -> LLMResult[T] | None: ...


class NullProvider:
    """Always-unavailable provider; agents use deterministic heuristics."""

    @property
    def available(self) -> bool:
        return False

    @property
    def model(self) -> str:
        return "none"

    async def structured(self, system: str, prompt: str, schema: type[T]) -> LLMResult[T] | None:
        return None


class AnthropicProvider:
    """Anthropic-backed provider using structured outputs and adaptive thinking."""

    def __init__(self, model: str = "claude-opus-4-8") -> None:
        self._model = model
        self._client = None
        try:  # pragma: no cover - exercised only with the llm extra + key
            from anthropic import AsyncAnthropic

            self._client = AsyncAnthropic()
        except Exception:
            self._client = None

    @property
    def available(self) -> bool:
        return self._client is not None

    @property
    def model(self) -> str:
        return self._model

    async def structured(self, system: str, prompt: str, schema: type[T]) -> LLMResult[T] | None:
        if self._client is None:  # pragma: no cover
            return None
        try:  # pragma: no cover - network path
            response = await self._client.messages.parse(
                model=self._model,
                max_tokens=8000,
                thinking={"type": "adaptive"},
                system=[{"type": "text", "text": system, "cache_control": {"type": "ephemeral"}}],
                messages=[{"role": "user", "content": prompt}],
                output_format=schema,
            )
            if response.parsed_output is None:
                return None
            usage = getattr(response, "usage", None)
            return LLMResult(
                data=response.parsed_output,
                input_tokens=getattr(usage, "input_tokens", 0) or 0,
                output_tokens=getattr(usage, "output_tokens", 0) or 0,
                model=self._model,
            )
        except Exception:
            return None


def get_provider(settings: Settings) -> LLMProvider:
    """Select a provider based on configuration and dependency availability."""
    if settings.llm_enabled:
        provider = AnthropicProvider(model=settings.llm_model)
        if provider.available:
            return provider
    return NullProvider()

from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(slots=True)
class LLMConfig:
    provider: str = "mock"
    model: str = "mock-v1"
    temperature: float = 0.7
    max_tokens: int = 2048

    @classmethod
    def from_env(cls) -> "LLMConfig":
        provider = os.getenv("LLM_PROVIDER", cls.provider)
        model = os.getenv("LLM_MODEL", cls.model)
        temperature = _parse_float(os.getenv("LLM_TEMPERATURE"), cls.temperature)
        max_tokens = _parse_int(os.getenv("LLM_MAX_TOKENS"), cls.max_tokens)
        return cls(
            provider=provider,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
        )


def _parse_float(value: str | None, default: float) -> float:
    if value is None:
        return default
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _parse_int(value: str | None, default: int) -> int:
    if value is None:
        return default
    try:
        return int(value)
    except (TypeError, ValueError):
        return default

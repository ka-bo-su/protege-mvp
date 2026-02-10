"""Builder for LLM session metadata."""

from __future__ import annotations

from typing import Any

from app.config.llm_config import LLMConfig
from app.utils.prompt_hash import generate_prompt_hash


def build_llm_metadata(
    config: LLMConfig,
    system_prompt: str,
    extra: dict | None = None,
) -> dict[str, Any]:
    """Build metadata for LLM session tracking."""

    config_max_turns = getattr(config, "max_turns", None)
    metadata: dict[str, Any] = {
        "provider": config.provider,
        "model_name": config.model,
        "temperature": config.temperature,
        "system_prompt_hash": generate_prompt_hash(system_prompt),
        "config_max_turns": config_max_turns,
    }

    if extra:
        metadata.update(extra)

    if metadata.get("config_max_turns") is None and extra and "config_max_turns" in extra:
        metadata["config_max_turns"] = extra["config_max_turns"]

    metadata["provider"] = config.provider
    metadata["model_name"] = config.model
    metadata["temperature"] = config.temperature
    metadata["system_prompt_hash"] = generate_prompt_hash(system_prompt)

    if "config_max_turns" not in metadata:
        metadata["config_max_turns"] = config_max_turns

    return metadata

from __future__ import annotations

import re
from pathlib import Path

from app.prompts.prompt_registry import PROMPT_REGISTRY
from app.utils.prompt_hash import generate_prompt_hash

PROMPT_ROOT = Path(__file__).resolve().parents[2] / "prompts"
_VERSION_RE = re.compile(r"^v\d+$")


class PromptError(Exception):
    """Base error for prompt loading."""


class PromptNotFoundError(PromptError):
    """Raised when a prompt file does not exist."""


class PromptVersionError(PromptError):
    """Raised when a prompt version is invalid or missing."""


def _normalize_version(version: str) -> str:
    version_value = version.strip()
    if version_value.endswith(".txt"):
        version_value = version_value[:-4]
    return version_value


def resolve_prompt_version(phase: str, version: str | None = None) -> str:
    registry = PROMPT_REGISTRY.get(phase)
    if registry is None:
        if phase == "phase3_report":
            resolved = _normalize_version(version or "v1")
            if not _VERSION_RE.match(resolved):
                raise PromptVersionError(f"Invalid version '{resolved}' for phase '{phase}'.")
            return resolved
        raise PromptVersionError(f"Unknown phase '{phase}'.")

    resolved = version if version is not None else registry.get("default")
    if not resolved:
        raise PromptVersionError(f"No default version configured for phase '{phase}'.")

    resolved = _normalize_version(resolved)
    if not _VERSION_RE.match(resolved):
        raise PromptVersionError(f"Invalid version '{resolved}' for phase '{phase}'.")

    return resolved


def _prompt_path(phase: str, version: str) -> Path:
    return PROMPT_ROOT / phase / f"{version}.txt"


def load_prompt(phase: str, version: str | None = None) -> str:
    resolved = resolve_prompt_version(phase, version)
    prompt_path = _prompt_path(phase, resolved)
    if not prompt_path.exists():
        raise PromptNotFoundError(f"Prompt file not found: {prompt_path}")
    return prompt_path.read_text(encoding="utf-8")


def load_prompt_with_hash(phase: str, version: str | None = None) -> tuple[str, str]:
    prompt_text = load_prompt(phase, version)
    return prompt_text, generate_prompt_hash(prompt_text)

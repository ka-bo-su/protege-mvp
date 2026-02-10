from __future__ import annotations

from pathlib import Path

from app.prompts.prompt_loader import load_prompt
from app.safety.safety_rules import SAFETY_VERSION

PROMPT_ROOT = Path(__file__).resolve().parents[2] / "prompts"
SAFETY_PROMPT_PATH = PROMPT_ROOT / "safety" / f"{SAFETY_VERSION}.txt"


class SafetyPromptNotFoundError(FileNotFoundError):
    """Raised when the safety guardrails prompt is missing."""


def load_safety_prompt() -> str:
    if not SAFETY_PROMPT_PATH.exists():
        raise SafetyPromptNotFoundError(f"Safety prompt not found: {SAFETY_PROMPT_PATH}")
    return SAFETY_PROMPT_PATH.read_text(encoding="utf-8")


def prepend_safety_guardrails(prompt_text: str) -> str:
    safety_prompt = load_safety_prompt().strip()
    body = (prompt_text or "").strip()
    if not safety_prompt:
        return body
    if not body:
        return safety_prompt
    return f"{safety_prompt}\n\n{body}"


def build_system_prompt(phase: str, version: str | None = None, context: str | None = None) -> str:
    phase_prompt = load_prompt(phase, version)
    combined = prepend_safety_guardrails(phase_prompt)
    if context:
        combined = f"{combined}\n\n{context.strip()}"
    return combined

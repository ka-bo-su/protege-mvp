"""Utilities for normalizing system prompts and generating stable hashes."""

from __future__ import annotations

import hashlib
import re

_SPACE_RE = re.compile(r"[ \t\f\v]+")


def normalize_prompt(prompt: str) -> str:
    """Normalize a prompt for stable hashing.

    - Strip leading/trailing whitespace
    - Normalize newlines to LF
    - Collapse consecutive spaces/tabs into a single space
    """

    prompt_value = "" if prompt is None else str(prompt)
    normalized = prompt_value.replace("\r\n", "\n").replace("\r", "\n")
    normalized = normalized.strip()
    normalized = _SPACE_RE.sub(" ", normalized)
    return normalized


def generate_prompt_hash(prompt: str) -> str:
    """Generate a SHA256 hex digest for a normalized prompt."""

    normalized = normalize_prompt(prompt)
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()

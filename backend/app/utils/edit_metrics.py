"""Edit metrics calculation utilities."""

from __future__ import annotations

import difflib
from typing import Dict


def compute_edit_metrics(draft: str | None, final: str | None) -> Dict[str, int | float]:
    """Compute edit metrics between draft and final strings.

    Returns a dictionary with chars_added, chars_removed, and ratio.
    The ratio is normalized by max(len(draft), 1) to avoid zero division.
    """

    draft = draft or ""
    final = final or ""

    matcher = difflib.SequenceMatcher(None, draft, final)
    chars_added = 0
    chars_removed = 0

    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "insert":
            chars_added += j2 - j1
        elif tag == "delete":
            chars_removed += i2 - i1
        elif tag == "replace":
            chars_added += j2 - j1
            chars_removed += i2 - i1

    diff = chars_added + chars_removed
    base_len = max(len(draft), 1)
    ratio = diff / base_len

    return {
        "chars_added": int(chars_added),
        "chars_removed": int(chars_removed),
        "ratio": float(ratio),
    }

from __future__ import annotations

from app.safety.safety_rules import HIGH_RISK_KEYWORDS


def detect_high_risk(message: str | None) -> bool:
    if message is None:
        return False
    cleaned = message.strip()
    if not cleaned:
        return False
    return any(keyword in cleaned for keyword in HIGH_RISK_KEYWORDS)

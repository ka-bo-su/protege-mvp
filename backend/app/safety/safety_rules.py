from __future__ import annotations

SAFETY_VERSION = "guardrails_v1"

HIGH_RISK_KEYWORDS = [
    "死にたい",
    "消えたい",
    "自殺",
    "もう終わりたい",
    "生きていたくない",
    "殺してほしい",
]

ESCALATION_RESPONSE = (
    "とてもつらい状態にいるように感じます。\n\n"
    "今はあなたの安全が最優先です。\n\n"
    "可能なら、身近な人や専門家に相談してください。\n"
    "緊急の場合は、すぐに緊急通報（110/119）も検討してください。\n\n"
    "（相談窓口の案内：よりそいホットライン等）"
)

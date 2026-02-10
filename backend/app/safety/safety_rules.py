from __future__ import annotations

SAFETY_VERSION = "guardrails_v1"

HIGH_RISK_KEYWORDS = [
    "死にたい",
    "消えたい",
    "自殺",
    "もう終わりたい",
    "生きていたくない",
]

ESCALATION_RESPONSE = (
    "とてもつらい状態にいるように感じます。\n\n"
    "もし可能なら、身近な人や専門家に相談してください。\n"
    "一人で抱え込まなくて大丈夫です。\n\n"
    "（地域相談窓口の案内など）"
)

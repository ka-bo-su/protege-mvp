from __future__ import annotations

import logging

from app.config.llm_config import LLMConfig
from app.llm.base import BaseLLMClient

logger = logging.getLogger(__name__)


class MockLLMClient(BaseLLMClient):
    def __init__(self, config: LLMConfig | None = None) -> None:
        self.config = config or LLMConfig()

    async def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        **kwargs,
    ) -> str:
        try:
            logger.info("MockLLMClient system_prompt=%s", system_prompt)
            logger.info("MockLLMClient user_prompt=%s", user_prompt)
        except Exception:
            pass

        try:
            snippet = (user_prompt or "")[:200]
            return f"[MOCK RESPONSE]\nUser: {snippet}"
        except Exception:
            return "[MOCK RESPONSE]\nUser: "

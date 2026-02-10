from __future__ import annotations

import os

from app.config.llm_config import LLMConfig
from app.llm.base import BaseLLMClient
from app.llm.mock_client import MockLLMClient
from app.llm.openai_client import OpenAIClient


def get_llm_client(config: LLMConfig | None = None) -> BaseLLMClient:
    config = config or LLMConfig()
    provider = os.getenv("LLM_PROVIDER") or config.provider or "mock"
    provider = provider.lower()

    if provider == "openai":
        return OpenAIClient(config)

    return MockLLMClient(config)

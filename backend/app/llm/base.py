from __future__ import annotations

from abc import ABC, abstractmethod


class LLMClientError(Exception):
    """Base error for LLM client failures."""


class LLMTimeoutError(LLMClientError):
    """Raised when an LLM request times out."""


class BaseLLMClient(ABC):
    @abstractmethod
    async def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        **kwargs,
    ) -> str:
        """Generate a response from the LLM."""
        raise NotImplementedError

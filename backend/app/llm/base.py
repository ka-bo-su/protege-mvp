from __future__ import annotations

from abc import ABC, abstractmethod
from functools import wraps
from typing import Any, Awaitable, Callable, TypeVar

from app.config.llm_config import LLMConfig
from app.services.llm_metadata_builder import build_llm_metadata


class LLMClientError(Exception):
    """Base error for LLM client failures."""


class LLMTimeoutError(LLMClientError):
    """Raised when an LLM request times out."""


GenerateCallable = TypeVar("GenerateCallable", bound=Callable[..., Awaitable[str]])


class BaseLLMClient(ABC):
    last_meta_data: dict[str, Any] | None = None

    def __init_subclass__(cls, **kwargs: Any) -> None:
        super().__init_subclass__(**kwargs)
        original_generate = cls.__dict__.get("generate")
        if original_generate is None:
            return
        if getattr(original_generate, "_metadata_wrapped", False):
            return

        @wraps(original_generate)
        async def _wrapped_generate(self, system_prompt: str, user_prompt: str, **kwargs):
            config = getattr(self, "config", None) or LLMConfig()
            extra = kwargs.get("meta_data")
            self.last_meta_data = build_llm_metadata(config, system_prompt, extra=extra)
            return await original_generate(self, system_prompt, user_prompt, **kwargs)

        _wrapped_generate._metadata_wrapped = True  # type: ignore[attr-defined]
        cls.generate = _wrapped_generate  # type: ignore[assignment]
    @abstractmethod
    async def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        **kwargs,
    ) -> str:
        """Generate a response from the LLM."""
        raise NotImplementedError

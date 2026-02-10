from __future__ import annotations

import os

from app.config.llm_config import LLMConfig
from app.llm.base import BaseLLMClient, LLMClientError, LLMTimeoutError


class OpenAIClient(BaseLLMClient):
    def __init__(self, config: LLMConfig | None = None) -> None:
        self.config = config or LLMConfig()

    async def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        **kwargs,
    ) -> str:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise LLMClientError("OPENAI_API_KEY is not set")

        model = kwargs.get("model", self.config.model)
        temperature = kwargs.get("temperature", self.config.temperature)
        max_tokens = kwargs.get("max_tokens", self.config.max_tokens)

        try:
            from openai import OpenAI  # type: ignore[import-not-found]
        except Exception as exc:  # pragma: no cover - optional dependency
            raise LLMClientError("openai SDK is not installed") from exc

        client = OpenAI(api_key=api_key)
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        try:
            response = await _run_openai_request(
                client,
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            return (response.choices[0].message.content or "").strip()
        except TimeoutError as exc:
            raise LLMTimeoutError("OpenAI request timed out") from exc
        except Exception as exc:
            raise LLMClientError("OpenAI request failed") from exc


async def _run_openai_request(client, **kwargs):
    import asyncio

    return await asyncio.to_thread(client.chat.completions.create, **kwargs)

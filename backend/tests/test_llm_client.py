from __future__ import annotations

import asyncio
import importlib.util
import os
import sys
from contextlib import contextmanager
from pathlib import Path


def _load_module(module_name: str, relative_path: str):
    module_path = Path(__file__).resolve().parents[1] / relative_path
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Unable to load module {module_name} from {module_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


llm_base = _load_module("llm_base", "app/llm/base.py")
llm_factory = _load_module("llm_factory", "app/llm/factory.py")
llm_mock = _load_module("llm_mock", "app/llm/mock_client.py")
llm_openai = _load_module("llm_openai", "app/llm/openai_client.py")
llm_config = _load_module("llm_config", "app/config/llm_config.py")


@contextmanager
def _temp_env(**updates):
    original = os.environ.copy()
    try:
        for key, value in updates.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = str(value)
        yield
    finally:
        os.environ.clear()
        os.environ.update(original)


def test_mock_generate_success():
    client = llm_mock.MockLLMClient(llm_config.LLMConfig())
    result = asyncio.run(client.generate("system", "hello world"))
    assert "[MOCK RESPONSE]" in result
    assert "hello world" in result


def test_factory_defaults_to_mock():
    with _temp_env(LLM_PROVIDER=None):
        client = llm_factory.get_llm_client(llm_config.LLMConfig())
        assert client.__class__.__name__ == "MockLLMClient"
        assert client.__class__.__module__.endswith("llm.mock_client")


def test_factory_switches_provider():
    with _temp_env(LLM_PROVIDER="openai"):
        client = llm_factory.get_llm_client(llm_config.LLMConfig())
        assert client.__class__.__name__ == "OpenAIClient"
        assert client.__class__.__module__.endswith("llm.openai_client")


def test_config_env_override():
    with _temp_env(LLM_MODEL="mock-x", LLM_TEMPERATURE="0.25", LLM_MAX_TOKENS="512"):
        config = llm_config.LLMConfig.from_env()
        assert config.model == "mock-x"
        assert config.temperature == 0.25
        assert config.max_tokens == 512

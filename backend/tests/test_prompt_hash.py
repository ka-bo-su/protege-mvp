from __future__ import annotations

import asyncio
import importlib.util
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))


def _load_module(module_name: str, relative_path: str):
    module_path = Path(__file__).resolve().parents[1] / relative_path
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Unable to load module {module_name} from {module_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


prompt_hash = _load_module("prompt_hash", "app/utils/prompt_hash.py")
metadata_builder = _load_module("llm_metadata_builder", "app/services/llm_metadata_builder.py")
llm_config = _load_module("llm_config", "app/config/llm_config.py")
llm_mock = _load_module("llm_mock", "app/llm/mock_client.py")


def test_hash_matches_newline_variants():
    prompt_lf = "Hello\nWorld"
    prompt_crlf = "Hello\r\nWorld"
    assert prompt_hash.generate_prompt_hash(prompt_lf) == prompt_hash.generate_prompt_hash(prompt_crlf)


def test_hash_matches_space_variants():
    prompt_multi = "Hello   World"
    prompt_single = "Hello World"
    assert prompt_hash.generate_prompt_hash(prompt_multi) == prompt_hash.generate_prompt_hash(prompt_single)


def test_hash_differs_for_distinct_prompts():
    assert prompt_hash.generate_prompt_hash("Hello World") != prompt_hash.generate_prompt_hash("Hello Mars")


def test_hash_none_safe():
    assert prompt_hash.generate_prompt_hash(None) == prompt_hash.generate_prompt_hash("")


def test_build_llm_metadata_contains_hash():
    config = llm_config.LLMConfig(provider="mock", model="mock-v1", temperature=0.5, max_tokens=10)
    metadata = metadata_builder.build_llm_metadata(config, "System\nPrompt", extra={"config_max_turns": 5})
    assert metadata["provider"] == "mock"
    assert metadata["model_name"] == "mock-v1"
    assert metadata["temperature"] == 0.5
    assert metadata["config_max_turns"] == 5
    assert metadata["system_prompt_hash"] == prompt_hash.generate_prompt_hash("System\nPrompt")


def test_mock_client_builds_metadata():
    client = llm_mock.MockLLMClient(llm_config.LLMConfig())
    asyncio.run(client.generate("System Prompt", "Hello"))
    assert isinstance(client.last_meta_data, dict)
    assert client.last_meta_data["system_prompt_hash"] == prompt_hash.generate_prompt_hash("System Prompt")

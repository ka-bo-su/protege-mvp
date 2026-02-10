from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))


def _load_module(module_name: str, relative_path: str):
    module_path = BASE_DIR / relative_path
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Unable to load module {module_name} from {module_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


prompt_loader = _load_module("prompt_loader", "app/prompts/prompt_loader.py")
prompt_hash = _load_module("prompt_hash", "app/utils/prompt_hash.py")


def test_default_version_load():
    prompt_text = prompt_loader.load_prompt("phase1")
    expected = (BASE_DIR / "prompts/phase1/v1.txt").read_text(encoding="utf-8")
    assert prompt_text == expected


def test_explicit_version_load():
    prompt_text = prompt_loader.load_prompt("phase1", "v2")
    expected = (BASE_DIR / "prompts/phase1/v2.txt").read_text(encoding="utf-8")
    assert prompt_text == expected


def test_missing_file_raises():
    with pytest.raises(prompt_loader.PromptNotFoundError):
        prompt_loader.load_prompt("phase1", "v999")


def test_hash_consistent():
    prompt_text = prompt_loader.load_prompt("phase3")
    expected_text = (BASE_DIR / "prompts/phase3/v1.txt").read_text(encoding="utf-8")
    assert prompt_hash.generate_prompt_hash(prompt_text) == prompt_hash.generate_prompt_hash(expected_text)

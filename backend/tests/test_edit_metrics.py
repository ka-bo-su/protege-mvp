from __future__ import annotations

import importlib.util
from pathlib import Path


def _load_compute_edit_metrics():
    module_path = Path(__file__).resolve().parents[1] / "app" / "utils" / "edit_metrics.py"
    spec = importlib.util.spec_from_file_location("edit_metrics", module_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Unable to load edit_metrics from {module_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.compute_edit_metrics


compute_edit_metrics = _load_compute_edit_metrics()


def test_edit_metrics_same_text():
    metrics = compute_edit_metrics("abc", "abc")
    assert metrics["chars_added"] == 0
    assert metrics["chars_removed"] == 0
    assert metrics["ratio"] == 0.0


def test_edit_metrics_empty_draft_no_zero_division():
    metrics = compute_edit_metrics("", "abc")
    assert metrics["chars_added"] > 0
    assert metrics["ratio"] > 0


def test_edit_metrics_final_empty():
    metrics = compute_edit_metrics("abc", "")
    assert metrics["chars_removed"] > 0


def test_edit_metrics_none_safe():
    metrics = compute_edit_metrics(None, "abc")
    assert metrics["chars_added"] > 0

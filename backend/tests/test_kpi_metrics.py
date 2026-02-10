from __future__ import annotations

import importlib.util
from datetime import datetime, timezone
from pathlib import Path


def _load_kpi_metrics():
    module_path = Path(__file__).resolve().parents[1] / "app" / "utils" / "kpi_metrics.py"
    spec = importlib.util.spec_from_file_location("kpi_metrics", module_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Unable to load kpi_metrics from {module_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


kpi_metrics = _load_kpi_metrics()


def test_compute_completion_rate():
    sessions = [
        {"phase": 3, "report_final": "done"},
        {"phase": 3, "report_final": ""},
        {"phase": 2, "report_final": "ignored"},
    ]
    completion = kpi_metrics.compute_completion(sessions)
    assert completion["total_phase3_sessions"] == 2
    assert completion["completed_sessions"] == 1
    assert completion["completion_rate"] == 0.5


def test_compute_retention_with_fallback_date():
    sessions = [
        {"session_date": "2026-02-10", "created_at": "2026-02-10T01:00:00"},
        {"session_date": None, "created_at": "2026-02-11 02:00:00"},
        {"session_date": "2026-02-10", "created_at": "2026-02-10 03:00:00"},
    ]
    retention = kpi_metrics.compute_retention(sessions)
    assert retention["total_sessions"] == 3
    assert retention["active_days"] == 2
    assert retention["sessions_per_day"] == 1.5
    assert retention["date_list"] == ["2026-02-10", "2026-02-11"]


def test_compute_kpi_summary_includes_user():
    sessions = [
        {
            "phase": 3,
            "report_final": "done",
            "session_date": "2026-02-10",
            "created_at": datetime(2026, 2, 10, tzinfo=timezone.utc),
        }
    ]
    summary = kpi_metrics.compute_kpi_summary(1, sessions)
    assert summary["user_id"] == 1
    assert summary["completion"]["completed_sessions"] == 1
    assert summary["retention"]["active_days"] == 1
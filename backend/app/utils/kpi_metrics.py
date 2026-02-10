"""KPI metrics calculation utilities."""

from __future__ import annotations

from datetime import date, datetime
from typing import Any, Dict, Iterable, List


def _parse_date(value: Any) -> date | None:
    if value is None:
        return None
    if isinstance(value, date) and not isinstance(value, datetime):
        return value
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, str):
        value = value.strip()
        if not value:
            return None
        try:
            if "T" in value or " " in value:
                return datetime.fromisoformat(value.replace("Z", "+00:00")).date()
            return date.fromisoformat(value)
        except ValueError:
            if " " in value:
                try:
                    return date.fromisoformat(value.split(" ", 1)[0])
                except ValueError:
                    return None
    return None


def _session_date(session: Dict[str, Any]) -> date | None:
    return _parse_date(session.get("session_date")) or _parse_date(session.get("created_at"))


def compute_completion(sessions: Iterable[Dict[str, Any]]) -> Dict[str, int | float]:
    phase3_sessions = [session for session in sessions if session.get("phase") == 3]
    total_phase3_sessions = len(phase3_sessions)
    completed_sessions = sum(
        1
        for session in phase3_sessions
        if session.get("report_final") is not None
        and str(session.get("report_final")).strip() != ""
    )
    completion_rate = (
        completed_sessions / total_phase3_sessions if total_phase3_sessions > 0 else 0.0
    )
    return {
        "total_phase3_sessions": int(total_phase3_sessions),
        "completed_sessions": int(completed_sessions),
        "completion_rate": float(completion_rate),
    }


def compute_retention(sessions: Iterable[Dict[str, Any]]) -> Dict[str, Any]:
    sessions_list: List[Dict[str, Any]] = list(sessions)
    total_sessions = len(sessions_list)
    dates = [_session_date(session) for session in sessions_list]
    date_list = sorted({value.isoformat() for value in dates if value is not None})
    active_days = len(date_list)
    sessions_per_day = total_sessions / active_days if active_days > 0 else 0.0
    return {
        "active_days": int(active_days),
        "total_sessions": int(total_sessions),
        "sessions_per_day": float(sessions_per_day),
        "date_list": date_list,
    }


def compute_kpi_summary(user_id: int, sessions: Iterable[Dict[str, Any]]) -> Dict[str, Any]:
    sessions_list = list(sessions)
    return {
        "user_id": int(user_id),
        "completion": compute_completion(sessions_list),
        "retention": compute_retention(sessions_list),
    }


def compute_edit_ratio_summary(ratios: Iterable[float]) -> Dict[str, int | float | None]:
    values: List[float] = []
    for ratio in ratios:
        if ratio is None or isinstance(ratio, bool):
            continue
        try:
            values.append(float(ratio))
        except (TypeError, ValueError):
            continue

    values.sort()
    count = len(values)
    if count == 0:
        return {"count": 0, "avg": None, "median": None, "min": None, "max": None}

    avg = sum(values) / count
    if count % 2 == 1:
        median = values[count // 2]
    else:
        mid = count // 2
        median = (values[mid - 1] + values[mid]) / 2

    return {
        "count": int(count),
        "avg": float(avg),
        "median": float(median),
        "min": float(values[0]),
        "max": float(values[-1]),
    }
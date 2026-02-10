from __future__ import annotations

from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session

from app.core.db import get_session
from app.repositories import session_repository
from app.schemas.kpi_edit_ratio_schema import EditRatioItem, EditRatioResponse, EditRatioSummary
from app.utils.kpi_metrics import compute_edit_ratio_summary

router = APIRouter(prefix="/api/v1/kpi", tags=["kpi"])


def _validate_user_id(user_id: Any) -> int:
    if not isinstance(user_id, int) or isinstance(user_id, bool):
        raise HTTPException(status_code=400, detail="user_id must be an integer")
    return user_id


@router.get("/edit-ratio", response_model=EditRatioResponse)
def get_edit_ratio_kpi(
    user_id: int = Query(...),
    session: Session = Depends(get_session),
) -> EditRatioResponse:
    user_id = _validate_user_id(user_id)
    sessions = session_repository.list_phase3_sessions(session, user_id)

    items: list[EditRatioItem] = []
    ratios: list[float] = []

    for item in sessions:
        metrics: Dict[str, Any] | None = item.edit_metrics if isinstance(item.edit_metrics, dict) else None
        if not metrics:
            continue
        ratio = metrics.get("ratio")
        if ratio is None or isinstance(ratio, bool):
            continue
        try:
            ratio_value = float(ratio)
        except (TypeError, ValueError):
            continue

        chars_added = metrics.get("chars_added", 0)
        chars_removed = metrics.get("chars_removed", 0)
        items.append(
            EditRatioItem(
                session_id=item.id,
                session_date=item.session_date,
                ratio=ratio_value,
                chars_added=int(chars_added or 0),
                chars_removed=int(chars_removed or 0),
            )
        )
        ratios.append(ratio_value)

    summary_dict = compute_edit_ratio_summary(ratios)
    summary = EditRatioSummary(**summary_dict)

    return EditRatioResponse(user_id=user_id, items=items, summary=summary)

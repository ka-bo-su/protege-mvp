from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from app.core.db import get_session
from app.schemas.phase3_schema import Phase3SessionCreateRequest, Phase3SessionCreateResponse
from app.services import phase3_service

router = APIRouter(prefix="/api/v1/phase3", tags=["phase3"])


def _validate_user_id(user_id: Any) -> int:
    if not isinstance(user_id, int) or isinstance(user_id, bool):
        raise HTTPException(status_code=400, detail="user_id must be an integer")
    return user_id


@router.post("/session", response_model=Phase3SessionCreateResponse)
def create_phase3_session(
    payload: Phase3SessionCreateRequest,
    session: Session = Depends(get_session),
) -> Phase3SessionCreateResponse:
    user_id = _validate_user_id(payload.user_id)

    try:
        created_session, goal_injected = phase3_service.start_phase3_session(session, user_id)
    except phase3_service.SessionCreateError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return Phase3SessionCreateResponse(
        session_id=created_session.id,
        phase=created_session.phase,
        goal_injected=goal_injected,
        created_at=created_session.created_at,
    )

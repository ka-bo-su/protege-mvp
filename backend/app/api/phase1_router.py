from __future__ import annotations

from typing import Any

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from app.core.db import get_session
from app.schemas.phase1_chat_schema import (
    Phase1ChatTurnRequest,
    Phase1ChatTurnResponse,
)
from app.schemas.phase1_schema import (
    Phase1SessionCreateRequest,
    Phase1SessionCreateResponse,
)
from app.services import phase1_chat_service, phase1_service

router = APIRouter(prefix="/api/v1/phase1", tags=["phase1"])


def _validate_user_id(user_id: Any) -> int:
    if not isinstance(user_id, int) or isinstance(user_id, bool):
        raise HTTPException(status_code=400, detail="user_id must be an integer")
    return user_id


@router.post("/session", response_model=Phase1SessionCreateResponse)
def create_phase1_session(
    payload: Phase1SessionCreateRequest,
    session: Session = Depends(get_session),
) -> Phase1SessionCreateResponse:
    user_id = _validate_user_id(payload.user_id)

    try:
        created_session = phase1_service.start_phase1_session(session, user_id)
    except phase1_service.SessionCreateError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return Phase1SessionCreateResponse(
        session_id=created_session.id,
        phase=created_session.phase,
        created_at=created_session.created_at,
    )


@router.post("/session/{session_id}/turn", response_model=Phase1ChatTurnResponse)
async def add_phase1_chat_turn(
    session_id: UUID,
    payload: Phase1ChatTurnRequest,
    session: Session = Depends(get_session),
) -> Phase1ChatTurnResponse:
    try:
        assistant_message, turn_index = await phase1_chat_service.append_phase1_turn(
            session=session,
            session_id=session_id,
            message=payload.message,
        )
    except phase1_chat_service.InvalidMessageError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except phase1_chat_service.SessionNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except phase1_chat_service.PhaseMismatchError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except phase1_chat_service.LLMGenerateError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    except phase1_chat_service.SessionUpdateError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return Phase1ChatTurnResponse(
        session_id=session_id,
        assistant_message=assistant_message,
        turn_index=turn_index,
    )

from __future__ import annotations

from typing import Any

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from app.core.db import get_session
from app.schemas.phase3_chat_schema import (
    Phase3ChatTurnRequest,
    Phase3ChatTurnResponse,
)
from app.schemas.phase3_schema import Phase3SessionCreateRequest, Phase3SessionCreateResponse
from app.services import phase3_chat_service, phase3_report_service, phase3_service

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


@router.post("/session/{session_id}/turn", response_model=Phase3ChatTurnResponse)
async def add_phase3_chat_turn(
    session_id: UUID,
    payload: Phase3ChatTurnRequest,
    session: Session = Depends(get_session),
) -> Phase3ChatTurnResponse:
    try:
        assistant_message, turn_index = await phase3_chat_service.append_phase3_turn(
            session=session,
            session_id=session_id,
            message=payload.message,
        )
    except phase3_chat_service.InvalidMessageError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except phase3_chat_service.SessionNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except phase3_chat_service.PhaseMismatchError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except phase3_chat_service.InvalidSessionLogError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except phase3_chat_service.LLMGenerateError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    except phase3_chat_service.SessionUpdateError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return Phase3ChatTurnResponse(
        session_id=session_id,
        assistant_message=assistant_message,
        turn_index=turn_index,
    )


@router.post("/session/{session_id}/report/draft")
async def generate_phase3_report_draft(
    session_id: UUID,
    session: Session = Depends(get_session),
) -> dict[str, object]:
    try:
        report_draft = await phase3_report_service.generate_phase3_report_draft(
            session=session,
            session_id=session_id,
        )
    except phase3_report_service.SessionNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except phase3_report_service.PhaseMismatchError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except phase3_report_service.InvalidSessionLogError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except phase3_report_service.PromptLoadError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    except phase3_report_service.LLMGenerateError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    except phase3_report_service.SessionUpdateError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return {
        "session_id": str(session_id),
        "report_draft": report_draft,
        "saved": True,
    }

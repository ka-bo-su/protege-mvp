from __future__ import annotations

from datetime import date, datetime
from typing import Any

from sqlmodel import Session

from app.models.session import Session as SessionModel


def create_phase1_session(
    session: Session,
    user_id: int,
    session_date: date,
    log_json: list[dict[str, Any]],
    meta_data: dict[str, Any],
) -> SessionModel:
    new_session = SessionModel(
        user_id=user_id,
        phase=1,
        session_date=session_date,
        log_json=log_json,
        meta_data=meta_data,
        created_at=datetime.utcnow(),
    )
    session.add(new_session)
    session.flush()
    return new_session

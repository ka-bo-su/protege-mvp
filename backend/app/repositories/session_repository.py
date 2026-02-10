from __future__ import annotations

from datetime import date, datetime, timezone
from typing import Any
from uuid import UUID

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
        created_at=datetime.now(timezone.utc),
    )
    session.add(new_session)
    session.flush()
    return new_session


def create_phase3_session(
    session: Session,
    user_id: int,
    session_date: date,
    log_json: list[dict[str, Any]],
    meta_data: dict[str, Any],
) -> SessionModel:
    new_session = SessionModel(
        user_id=user_id,
        phase=3,
        session_date=session_date,
        log_json=log_json,
        meta_data=meta_data,
        created_at=datetime.now(timezone.utc),
    )
    session.add(new_session)
    session.flush()
    return new_session


def get_session_by_id(session: Session, session_id: UUID) -> SessionModel | None:
    return session.get(SessionModel, session_id)


def update_session_log(
    session: Session,
    session_id: UUID,
    log_json: list[dict[str, Any]],
) -> SessionModel | None:
    existing = session.get(SessionModel, session_id)
    if existing is None:
        return None
    existing.log_json = log_json
    session.add(existing)
    session.flush()
    return existing


def get_session(session: Session, session_id: UUID) -> SessionModel | None:
    return session.get(SessionModel, session_id)


def update_session(session: Session, session_id: UUID, **fields: Any) -> SessionModel | None:
    existing = session.get(SessionModel, session_id)
    if existing is None:
        return None
    for key, value in fields.items():
        if hasattr(existing, key):
            setattr(existing, key, value)
    session.add(existing)
    session.flush()
    return existing


def update_report_final(
    session: Session,
    session_id: UUID,
    report_final: str,
    edit_metrics: dict[str, Any],
    meta_data: dict[str, Any],
) -> SessionModel | None:
    existing = session.get(SessionModel, session_id)
    if existing is None:
        return None
    existing.report_final = report_final
    existing.edit_metrics = edit_metrics
    existing.meta_data = meta_data
    session.add(existing)
    session.flush()
    return existing

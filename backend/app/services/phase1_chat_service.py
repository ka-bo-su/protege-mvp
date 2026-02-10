from __future__ import annotations

from typing import Any
from uuid import UUID

from sqlalchemy.exc import SQLAlchemyError
from sqlmodel import Session

from app.config.llm_config import LLMConfig
from app.llm.factory import get_llm_client
from app.repositories import session_repository
from app.safety.safety_detector import detect_high_risk
from app.safety.safety_rules import ESCALATION_RESPONSE, SAFETY_VERSION
from app.utils.prompt_builder import build_system_prompt


class Phase1ChatError(RuntimeError):
    """Base error for Phase1 chat turn operations."""


class InvalidMessageError(Phase1ChatError):
    """Raised when the user message is invalid."""


class SessionNotFoundError(Phase1ChatError):
    """Raised when a session is not found."""


class PhaseMismatchError(Phase1ChatError):
    """Raised when a session phase does not match Phase1."""


class LLMGenerateError(Phase1ChatError):
    """Raised when the LLM fails to generate a response."""


class SessionUpdateError(Phase1ChatError):
    """Raised when a session update fails."""


def _normalize_log_json(log_json: Any) -> list[dict[str, Any]]:
    if isinstance(log_json, list):
        return list(log_json)
    if isinstance(log_json, dict):
        return [log_json]
    return []


async def append_phase1_turn(
    session: Session,
    session_id: UUID,
    message: str,
) -> tuple[str, int, bool]:
    cleaned = message.strip() if message is not None else ""
    if not cleaned:
        raise InvalidMessageError("message must not be empty")

    existing = session_repository.get_session_by_id(session, session_id)
    if existing is None:
        raise SessionNotFoundError("session not found")
    if existing.phase != 1:
        raise PhaseMismatchError("phase mismatch")

    if detect_high_risk(cleaned):
        updated_log = _normalize_log_json(existing.log_json)
        updated_log.append({"role": "user", "content": cleaned})
        updated_log.append({"role": "assistant", "content": ESCALATION_RESPONSE})

        meta_data = dict(existing.meta_data or {})
        meta_data.setdefault("safety_version", SAFETY_VERSION)
        meta_data["safety_triggered"] = True
        meta_data["safety_reason"] = "high_risk_keyword"

        try:
            updated = session_repository.update_session(
                session=session,
                session_id=existing.id,
                log_json=updated_log,
                meta_data=meta_data,
            )
            if updated is None:
                raise SessionNotFoundError("session not found")
            session.commit()
            session.refresh(updated)
        except SQLAlchemyError as exc:
            session.rollback()
            raise SessionUpdateError("Failed to update session log") from exc

        turn_index = len(updated_log) - 1
        return ESCALATION_RESPONSE, turn_index, True

    system_prompt = build_system_prompt("phase1")
    llm_client = get_llm_client(LLMConfig())

    try:
        assistant_response = await llm_client.generate(system_prompt, cleaned)
    except Exception as exc:  # noqa: BLE001
        raise LLMGenerateError("LLM generation failed") from exc

    updated_log = _normalize_log_json(existing.log_json)
    updated_log.append({"role": "user", "content": cleaned})
    updated_log.append({"role": "assistant", "content": assistant_response})

    try:
        updated = session_repository.update_session_log(
            session=session,
            session_id=existing.id,
            log_json=updated_log,
        )
        if updated is None:
            raise SessionNotFoundError("session not found")
        session.commit()
        session.refresh(updated)
    except SQLAlchemyError as exc:
        session.rollback()
        raise SessionUpdateError("Failed to update session log") from exc

    turn_index = len(updated_log) - 1
    return assistant_response, turn_index, False

from __future__ import annotations

from typing import Any
from uuid import UUID

from sqlalchemy.exc import SQLAlchemyError
from sqlmodel import Session

from app.config.llm_config import LLMConfig
from app.llm.factory import get_llm_client
from app.repositories import session_repository


class Phase3ChatError(RuntimeError):
    """Base error for Phase3 chat turn operations."""


class InvalidMessageError(Phase3ChatError):
    """Raised when the user message is invalid."""


class SessionNotFoundError(Phase3ChatError):
    """Raised when a session is not found."""


class PhaseMismatchError(Phase3ChatError):
    """Raised when a session phase does not match Phase3."""


class InvalidSessionLogError(Phase3ChatError):
    """Raised when session log is missing a system prompt."""


class LLMGenerateError(Phase3ChatError):
    """Raised when the LLM fails to generate a response."""


class SessionUpdateError(Phase3ChatError):
    """Raised when a session update fails."""


def _normalize_log_json(log_json: Any) -> list[dict[str, Any]]:
    if isinstance(log_json, list):
        return list(log_json)
    if isinstance(log_json, dict):
        return [log_json]
    return []


def _extract_system_prompt(log_json: list[dict[str, Any]]) -> str | None:
    if not log_json:
        return None
    first = log_json[0]
    if not isinstance(first, dict):
        return None
    if first.get("role") != "system":
        return None
    content = first.get("content")
    if not isinstance(content, str) or not content.strip():
        return None
    return content


async def append_phase3_turn(
    session: Session,
    session_id: UUID,
    message: str,
) -> tuple[str, int]:
    cleaned = message.strip() if message is not None else ""
    if not cleaned:
        raise InvalidMessageError("message must not be empty")

    existing = session_repository.get_session_by_id(session, session_id)
    if existing is None:
        raise SessionNotFoundError("session not found")
    if existing.phase != 3:
        raise PhaseMismatchError("phase mismatch")

    updated_log = _normalize_log_json(existing.log_json)
    system_prompt = _extract_system_prompt(updated_log)
    if system_prompt is None:
        raise InvalidSessionLogError("invalid session log: missing system prompt")

    llm_client = get_llm_client(LLMConfig())
    try:
        assistant_response = await llm_client.generate(system_prompt, cleaned)
    except Exception as exc:  # noqa: BLE001
        raise LLMGenerateError("LLM generation failed") from exc

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
    return assistant_response, turn_index

from __future__ import annotations

from datetime import datetime, timezone
import re
from typing import Any
from uuid import UUID

from sqlalchemy.exc import SQLAlchemyError
from sqlmodel import Session

from app.config.llm_config import LLMConfig
from app.llm.factory import get_llm_client
from app.prompts.prompt_loader import load_prompt, resolve_prompt_version
from app.repositories import goals_repository, session_repository
from app.services.phase3_service import DEFAULT_GOAL_TEXT
from app.utils.edit_metrics import compute_edit_metrics
from app.utils.prompt_hash import generate_prompt_hash

ALWAYS_ON_GOAL_PLACEHOLDER = "{{ALWAYS_ON_GOAL}}"
CHAT_LOG_PLACEHOLDER = "{{CHAT_LOG}}"
GOAL_SECTION_PATTERN = re.compile(r"Always-on Goal:\s*(.+)", re.DOTALL)


class Phase3ReportError(RuntimeError):
    """Base error for Phase3 report draft generation."""


class SessionNotFoundError(Phase3ReportError):
    """Raised when a session is not found."""


class PhaseMismatchError(Phase3ReportError):
    """Raised when a session phase does not match Phase3."""


class InvalidSessionLogError(Phase3ReportError):
    """Raised when session log is missing a system prompt."""


class LLMGenerateError(Phase3ReportError):
    """Raised when the LLM fails to generate a report."""


class SessionUpdateError(Phase3ReportError):
    """Raised when a session update fails."""


class PromptLoadError(Phase3ReportError):
    """Raised when the report prompt cannot be loaded."""


class InvalidReportFinalError(Phase3ReportError):
    """Raised when report_final is invalid."""


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


def _extract_goal_from_system_prompt(system_prompt: str) -> str | None:
    if ALWAYS_ON_GOAL_PLACEHOLDER in system_prompt:
        return None
    match = GOAL_SECTION_PATTERN.search(system_prompt)
    if not match:
        return None
    goal_text = match.group(1).strip()
    return goal_text or None


def _format_chat_log(log_json: list[dict[str, Any]]) -> str:
    lines: list[str] = []
    for entry in log_json:
        if not isinstance(entry, dict):
            continue
        role = entry.get("role")
        content = entry.get("content")
        if not isinstance(role, str) or not isinstance(content, str):
            continue
        if not role or not content:
            continue
        lines.append(f"[{role}] {content}")
    return "\n".join(lines).strip()


def _merge_report_metadata(
    existing: dict[str, Any] | None,
    prompt_phase: str,
    prompt_version: str,
    prompt_hash: str,
    model_name: str,
) -> dict[str, Any]:
    meta_data = dict(existing or {})
    meta_data["report_generation"] = {
        "prompt_phase": prompt_phase,
        "prompt_version": prompt_version,
        "prompt_hash": prompt_hash,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "model_name": model_name,
    }
    return meta_data


def _merge_report_final_metadata(
    existing: dict[str, Any] | None,
) -> dict[str, Any]:
    meta_data = dict(existing or {})
    meta_data["report_final_saved_at"] = datetime.now(timezone.utc).isoformat()
    return meta_data


async def generate_phase3_report_draft(
    session: Session,
    session_id: UUID,
) -> str:
    existing = session_repository.get_session_by_id(session, session_id)
    if existing is None:
        raise SessionNotFoundError("session not found")
    if existing.phase != 3:
        raise PhaseMismatchError("phase mismatch")

    normalized_log = _normalize_log_json(existing.log_json)
    system_prompt = _extract_system_prompt(normalized_log)
    if system_prompt is None:
        raise InvalidSessionLogError("invalid session log: missing system prompt")

    try:
        base_prompt = load_prompt("phase3_report")
        prompt_version = resolve_prompt_version("phase3_report")
    except Exception as exc:  # noqa: BLE001
        raise PromptLoadError("failed to load report prompt") from exc

    goal_text = _extract_goal_from_system_prompt(system_prompt)
    if goal_text is None:
        active_goal = goals_repository.get_active_goal(session, existing.user_id)
        goal_text = active_goal.content if active_goal is not None else DEFAULT_GOAL_TEXT

    formatted_log = _format_chat_log(normalized_log)
    report_prompt = base_prompt
    if ALWAYS_ON_GOAL_PLACEHOLDER in report_prompt:
        report_prompt = report_prompt.replace(ALWAYS_ON_GOAL_PLACEHOLDER, goal_text)
    if CHAT_LOG_PLACEHOLDER in report_prompt:
        report_prompt = report_prompt.replace(CHAT_LOG_PLACEHOLDER, formatted_log)

    prompt_hash = generate_prompt_hash(report_prompt)

    llm_config = LLMConfig()
    llm_client = get_llm_client(llm_config)
    try:
        report_draft = await llm_client.generate(report_prompt, "")
    except Exception as exc:  # noqa: BLE001
        raise LLMGenerateError("LLM generation failed") from exc

    meta_data = _merge_report_metadata(
        existing.meta_data,
        prompt_phase="phase3_report",
        prompt_version=prompt_version,
        prompt_hash=prompt_hash,
        model_name=llm_config.model,
    )

    try:
        updated = session_repository.update_session(
            session=session,
            session_id=existing.id,
            report_draft=report_draft,
            meta_data=meta_data,
        )
        if updated is None:
            raise SessionNotFoundError("session not found")
        session.commit()
        session.refresh(updated)
    except SQLAlchemyError as exc:
        session.rollback()
        raise SessionUpdateError("Failed to update session report_draft") from exc

    return report_draft


def save_phase3_report_final(
    session: Session,
    session_id: UUID,
    report_final: str,
) -> dict[str, int | float]:
    existing = session_repository.get_session_by_id(session, session_id)
    if existing is None:
        raise SessionNotFoundError("session not found")
    if existing.phase != 3:
        raise PhaseMismatchError("phase mismatch")

    if report_final is None or not report_final.strip():
        raise InvalidReportFinalError("report_final must not be empty")

    metrics = compute_edit_metrics(existing.report_draft, report_final)
    meta_data = _merge_report_final_metadata(existing.meta_data)

    try:
        updated = session_repository.update_report_final(
            session=session,
            session_id=existing.id,
            report_final=report_final,
            edit_metrics=metrics,
            meta_data=meta_data,
        )
        if updated is None:
            raise SessionNotFoundError("session not found")
        session.commit()
        session.refresh(updated)
    except SQLAlchemyError as exc:
        session.rollback()
        raise SessionUpdateError("Failed to update session report_final") from exc

    return metrics

from __future__ import annotations

from datetime import date

from sqlalchemy.exc import SQLAlchemyError
from sqlmodel import Session

from app.config.llm_config import LLMConfig
from app.prompts.prompt_loader import load_prompt, resolve_prompt_version
from app.repositories import goals_repository, session_repository
from app.services.llm_metadata_builder import build_llm_metadata
from app.utils.prompt_hash import generate_prompt_hash
from app.utils.prompt_builder import prepend_safety_guardrails
from app.safety.safety_rules import SAFETY_VERSION

ALWAYS_ON_GOAL_PLACEHOLDER = "{{ALWAYS_ON_GOAL}}"
DEFAULT_GOAL_TEXT = "（未設定）"


class SessionCreateError(RuntimeError):
    """Raised when Phase3 session creation fails."""


def _inject_goal(system_prompt: str, goal_text: str) -> str:
    if ALWAYS_ON_GOAL_PLACEHOLDER in system_prompt:
        return system_prompt.replace(ALWAYS_ON_GOAL_PLACEHOLDER, goal_text)

    suffix = f"\n\nAlways-on Goal:\n{goal_text}\n"
    return f"{system_prompt.rstrip()}{suffix}"


def start_phase3_session(session: Session, user_id: int):
    """Create a Phase3 session with injected goal, initial log, and metadata."""

    base_prompt = load_prompt("phase3")
    prompt_version = resolve_prompt_version("phase3")

    active_goal = goals_repository.get_active_goal(session, user_id)
    goal_injected = active_goal is not None
    goal_text = active_goal.content if active_goal is not None else DEFAULT_GOAL_TEXT

    injected_prompt = _inject_goal(base_prompt, goal_text)
    injected_prompt = prepend_safety_guardrails(injected_prompt)
    prompt_hash = generate_prompt_hash(injected_prompt)

    log_json = [
        {
            "role": "system",
            "content": injected_prompt,
        }
    ]

    meta_data = build_llm_metadata(
        LLMConfig(),
        injected_prompt,
        extra={
            "prompt_version": prompt_version,
            "prompt_hash": prompt_hash,
            "safety_version": SAFETY_VERSION,
            "safety_triggered": False,
        },
    )

    try:
        created_session = session_repository.create_phase3_session(
            session=session,
            user_id=user_id,
            session_date=date.today(),
            log_json=log_json,
            meta_data=meta_data,
        )
        session.commit()
        session.refresh(created_session)
        return created_session, goal_injected
    except SQLAlchemyError as exc:
        session.rollback()
        raise SessionCreateError("Failed to create Phase3 session") from exc

from __future__ import annotations

from datetime import date

from sqlalchemy.exc import SQLAlchemyError
from sqlmodel import Session

from app.config.llm_config import LLMConfig
from app.prompts.prompt_loader import load_prompt, resolve_prompt_version
from app.repositories import session_repository
from app.services.llm_metadata_builder import build_llm_metadata
from app.utils.prompt_hash import generate_prompt_hash


class SessionCreateError(RuntimeError):
    """Raised when Phase1 session creation fails."""


def start_phase1_session(session: Session, user_id: int):
    """Create a Phase1 session with initial log and metadata."""

    system_prompt = load_prompt("phase1")
    prompt_hash = generate_prompt_hash(system_prompt)
    prompt_version = resolve_prompt_version("phase1")

    log_json = [
        {
            "role": "system",
            "content": system_prompt,
        }
    ]

    meta_data = build_llm_metadata(
        LLMConfig(),
        system_prompt,
        extra={
            "prompt_version": prompt_version,
            "prompt_hash": prompt_hash,
        },
    )

    try:
        created_session = session_repository.create_phase1_session(
            session=session,
            user_id=user_id,
            session_date=date.today(),
            log_json=log_json,
            meta_data=meta_data,
        )
        session.commit()
        session.refresh(created_session)
        return created_session
    except SQLAlchemyError as exc:
        session.rollback()
        raise SessionCreateError("Failed to create Phase1 session") from exc

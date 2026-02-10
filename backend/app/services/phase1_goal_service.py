from __future__ import annotations

from uuid import UUID

from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlmodel import Session

from app.models.goal import Goal
from app.repositories import goals_repository, session_repository


class Phase1GoalConfirmError(RuntimeError):
    """Base error for Phase1 goal confirmation."""


class InvalidGoalTextError(Phase1GoalConfirmError):
    """Raised when the goal text is invalid."""


class UnsupportedModeError(Phase1GoalConfirmError):
    """Raised when the requested confirmation mode is unsupported."""


class SessionNotFoundError(Phase1GoalConfirmError):
    """Raised when a session is not found."""


class PhaseMismatchError(Phase1GoalConfirmError):
    """Raised when a session phase does not match Phase1."""


class GoalActivationConflictError(Phase1GoalConfirmError):
    """Raised when a new active goal violates the unique active-goal constraint."""

    def __init__(self, user_id: int) -> None:
        super().__init__(f"Active goal already exists for user_id={user_id}.")
        self.user_id = user_id


class GoalConfirmError(Phase1GoalConfirmError):
    """Raised when confirmation fails for unexpected reasons."""


def _resolve_goal_text(goal_text: str | None, mode: str | None) -> str:
    if mode:
        if mode != "summarize":
            raise UnsupportedModeError("Unsupported confirm mode")
        raise UnsupportedModeError("summarize mode is not supported yet")
    cleaned = goal_text.strip() if goal_text is not None else ""
    if not cleaned:
        raise InvalidGoalTextError("goal_text must not be empty")
    return cleaned


def confirm_phase1_goal(
    session: Session,
    session_id: UUID,
    goal_text: str | None,
    mode: str | None = None,
) -> Goal:
    resolved_goal = _resolve_goal_text(goal_text, mode)

    existing = session_repository.get_session(session, session_id)
    if existing is None:
        raise SessionNotFoundError("session not found")
    if existing.phase != 1:
        raise PhaseMismatchError("phase mismatch")

    try:
        transaction = session.begin_nested() if session.in_transaction() else session.begin()
        with transaction:
            goals_repository.deactivate_active_goal(session, existing.user_id)
            max_version = goals_repository.get_max_goal_version(session, existing.user_id)
            next_version = (max_version or 0) + 1
            goal = goals_repository.insert_goal(
                session=session,
                user_id=existing.user_id,
                content=resolved_goal,
                version=next_version,
                is_active=True,
            )
            updated = session_repository.update_session(
                session=session,
                session_id=existing.id,
                report_final=resolved_goal,
            )
            if updated is None:
                raise SessionNotFoundError("session not found")
        session.commit()
        session.refresh(goal)
        return goal
    except IntegrityError as exc:
        session.rollback()
        raise GoalActivationConflictError(existing.user_id) from exc
    except SQLAlchemyError as exc:
        session.rollback()
        raise GoalConfirmError("Failed to confirm Phase1 goal") from exc

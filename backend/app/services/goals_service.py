from __future__ import annotations

from sqlalchemy.exc import IntegrityError
from sqlmodel import Session

from app.models.goal import Goal
from app.repositories import goals_repo


class GoalActivationConflictError(RuntimeError):
    """Raised when a new active goal violates the unique active-goal constraint."""

    def __init__(self, user_id: int) -> None:
        super().__init__(f"Active goal already exists for user_id={user_id}.")
        self.user_id = user_id


def activate_new_goal(session: Session, user_id: int, content: str) -> Goal:
    """Deactivate existing active goals and insert a new active goal in one transaction."""
    try:
        transaction = session.begin_nested() if session.in_transaction() else session.begin()
        with transaction:
            goals_repo.deactivate_active_goals(session, user_id)
            next_version = goals_repo.get_next_goal_version(session, user_id)
            goal = Goal(
                user_id=user_id,
                content=content,
                version=next_version,
                is_active=True,
            )
            goals_repo.add_goal(session, goal)
        session.refresh(goal)
        return goal
    except IntegrityError as exc:
        session.rollback()
        raise GoalActivationConflictError(user_id) from exc

from __future__ import annotations

from typing import Any

import sqlalchemy as sa
from sqlmodel import Session, select

from app.models.goal import Goal


def deactivate_active_goals(session: Session, user_id: int) -> None:
    statement = (
        sa.update(Goal)
        .where(Goal.user_id == user_id)
        .where(Goal.is_active.is_(True))
        .values(is_active=False)
    )
    session.exec(statement)


def get_next_goal_version(session: Session, user_id: int) -> int:
    statement = select(sa.func.max(Goal.version)).where(Goal.user_id == user_id)
    result: Any = session.exec(statement).first()
    if isinstance(result, tuple):
        current_version = result[0]
    else:
        current_version = result
    return int(current_version or 0) + 1


def add_goal(session: Session, goal: Goal) -> Goal:
    session.add(goal)
    session.flush()
    return goal

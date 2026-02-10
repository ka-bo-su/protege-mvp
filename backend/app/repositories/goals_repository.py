from __future__ import annotations

from typing import Any

import sqlalchemy as sa
from sqlmodel import Session, select

from app.models.goal import Goal


def get_max_goal_version(session: Session, user_id: int) -> int | None:
    statement = select(sa.func.max(Goal.version)).where(Goal.user_id == user_id)
    result: Any = session.exec(statement).first()
    if isinstance(result, tuple):
        current_version = result[0]
    else:
        current_version = result
    if current_version is None:
        return None
    return int(current_version)


def deactivate_active_goal(session: Session, user_id: int) -> None:
    statement = (
        sa.update(Goal)
        .where(Goal.user_id == user_id)
        .where(Goal.is_active.is_(True))
        .values(is_active=False)
    )
    session.exec(statement)


def insert_goal(
    session: Session,
    user_id: int,
    content: str,
    version: int,
    is_active: bool = True,
) -> Goal:
    goal = Goal(
        user_id=user_id,
        content=content,
        version=version,
        is_active=is_active,
    )
    session.add(goal)
    session.flush()
    return goal

from __future__ import annotations

from pydantic import BaseModel, Field


class Phase1GoalConfirmRequest(BaseModel):
    goal_text: str | None = Field(default=None)
    mode: str | None = None


class Phase1GoalConfirmResponse(BaseModel):
    user_id: int
    goal_id: int
    version: int
    is_active: bool

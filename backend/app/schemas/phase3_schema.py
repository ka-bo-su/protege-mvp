from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel


class Phase3SessionCreateRequest(BaseModel):
    user_id: Any


class Phase3SessionCreateResponse(BaseModel):
    session_id: UUID
    phase: int
    goal_injected: bool
    created_at: datetime

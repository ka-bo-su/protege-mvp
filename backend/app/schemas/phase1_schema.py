from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel


class Phase1SessionCreateRequest(BaseModel):
    user_id: Any


class Phase1SessionCreateResponse(BaseModel):
    session_id: UUID
    phase: int
    created_at: datetime

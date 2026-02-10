from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel, Field


class Phase3ChatTurnRequest(BaseModel):
    message: str = Field(..., min_length=1)


class Phase3ChatTurnResponse(BaseModel):
    session_id: UUID
    assistant_message: str
    turn_index: int
    emergency: bool = False

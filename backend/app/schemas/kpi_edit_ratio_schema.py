from __future__ import annotations

from datetime import date
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class EditRatioItem(BaseModel):
    session_id: UUID
    session_date: date
    ratio: float
    chars_added: int
    chars_removed: int


class EditRatioSummary(BaseModel):
    count: int
    avg: Optional[float] = None
    median: Optional[float] = None
    min: Optional[float] = None
    max: Optional[float] = None


class EditRatioResponse(BaseModel):
    user_id: int
    items: list[EditRatioItem]
    summary: EditRatioSummary

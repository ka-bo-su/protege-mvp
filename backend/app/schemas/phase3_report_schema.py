from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel, Field


class Phase3ReportFinalSaveRequest(BaseModel):
    report_final: str = Field(..., min_length=1)


class EditMetrics(BaseModel):
    chars_added: int
    chars_removed: int
    ratio: float


class Phase3ReportFinalSaveResponse(BaseModel):
    session_id: UUID
    saved: bool
    edit_metrics: EditMetrics

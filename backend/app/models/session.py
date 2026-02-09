from __future__ import annotations

from datetime import date, datetime
from typing import Any
from uuid import UUID, uuid4

import sqlalchemy as sa
from sqlmodel import Field, SQLModel


class Session(SQLModel, table=True):
    __tablename__ = "sessions"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: int = Field(foreign_key="users.id", nullable=False)
    session_date: date
    phase: int
    log_json: dict[str, Any] = Field(
        default_factory=dict,
        sa_column=sa.Column(sa.JSON, nullable=False),
    )
    report_draft: str | None = Field(default=None)
    report_final: str | None = Field(default=None)
    edit_metrics: dict[str, Any] | None = Field(
        default=None,
        sa_column=sa.Column(sa.JSON, nullable=True),
    )
    meta_data: dict[str, Any] = Field(
        default_factory=dict,
        sa_column=sa.Column(sa.JSON, nullable=False),
    )
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

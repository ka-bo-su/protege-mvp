from __future__ import annotations

from sqlmodel import Session, create_engine

from app.core.config import DATABASE_URL

connect_args: dict[str, bool] = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(DATABASE_URL, echo=False, connect_args=connect_args)


def get_session():
    with Session(engine) as session:
        yield session

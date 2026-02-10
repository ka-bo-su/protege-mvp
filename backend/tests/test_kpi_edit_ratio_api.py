from __future__ import annotations

import sys
from datetime import date
from pathlib import Path
from uuid import uuid4

from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import SQLModel, Session as SqlSession, create_engine

BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from app.api.kpi_router import router as kpi_router
from app.core.db import get_session
from app.models.session import Session as SessionModel
from app.models.user import User


def _build_test_app():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)

    app = FastAPI()
    app.include_router(kpi_router)

    def _override_get_session():
        with SqlSession(engine) as session:
            yield session

    app.dependency_overrides[get_session] = _override_get_session
    return app, engine


def _create_user(engine) -> int:
    with SqlSession(engine) as session:
        user = User(name="Test User")
        session.add(user)
        session.commit()
        session.refresh(user)
        return int(user.id)


def test_edit_ratio_kpi_returns_summary_and_items():
    app, engine = _build_test_app()
    user_id = _create_user(engine)

    with SqlSession(engine) as session:
        session.add(
            SessionModel(
                id=uuid4(),
                user_id=user_id,
                session_date=date(2026, 2, 8),
                phase=3,
                log_json={},
                edit_metrics={"ratio": 0.1, "chars_added": 2, "chars_removed": 1},
                meta_data={},
            )
        )
        session.add(
            SessionModel(
                id=uuid4(),
                user_id=user_id,
                session_date=date(2026, 2, 9),
                phase=3,
                log_json={},
                edit_metrics={"ratio": 0.3, "chars_added": 6, "chars_removed": 3},
                meta_data={},
            )
        )
        session.add(
            SessionModel(
                id=uuid4(),
                user_id=user_id,
                session_date=date(2026, 2, 10),
                phase=3,
                log_json={},
                edit_metrics=None,
                meta_data={},
            )
        )
        session.add(
            SessionModel(
                id=uuid4(),
                user_id=user_id,
                session_date=date(2026, 2, 11),
                phase=1,
                log_json={},
                edit_metrics={"ratio": 0.9, "chars_added": 10, "chars_removed": 5},
                meta_data={},
            )
        )
        session.commit()

    client = TestClient(app)
    response = client.get(f"/api/v1/kpi/edit-ratio?user_id={user_id}")
    assert response.status_code == 200

    data = response.json()
    assert data["user_id"] == user_id
    assert data["summary"]["count"] == 2
    assert data["summary"]["avg"] == 0.2
    assert data["summary"]["median"] == 0.2
    assert data["summary"]["min"] == 0.1
    assert data["summary"]["max"] == 0.3
    assert len(data["items"]) == 2


def test_edit_ratio_kpi_empty_returns_na_summary():
    app, engine = _build_test_app()
    user_id = _create_user(engine)
    client = TestClient(app)

    response = client.get(f"/api/v1/kpi/edit-ratio?user_id={user_id}")
    assert response.status_code == 200

    data = response.json()
    assert data["summary"]["count"] == 0
    assert data["summary"]["avg"] is None
    assert data["summary"]["median"] is None
    assert data["summary"]["min"] is None
    assert data["summary"]["max"] is None

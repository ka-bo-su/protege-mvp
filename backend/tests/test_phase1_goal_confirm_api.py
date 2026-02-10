from __future__ import annotations

import sys
from datetime import date
from pathlib import Path
from uuid import UUID, uuid4

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy.exc import IntegrityError
from sqlalchemy.pool import StaticPool
from sqlmodel import SQLModel, Session as SqlSession, create_engine, select

BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from app.api.phase1_router import router as phase1_router
from app.core.db import get_session
from app.models.goal import Goal
from app.models.session import Session as SessionModel
from app.models.user import User
from app.services import phase1_goal_service, phase1_service


def _build_test_app():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)

    app = FastAPI()
    app.include_router(phase1_router)

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


def _create_phase1_session(engine, user_id: int) -> UUID:
    with SqlSession(engine) as session:
        created = phase1_service.start_phase1_session(session, user_id)
        return created.id


def test_confirm_goal_first_time_creates_version_one():
    app, engine = _build_test_app()
    user_id = _create_user(engine)
    session_id = _create_phase1_session(engine, user_id)
    client = TestClient(app)

    response = client.post(
        f"/api/v1/phase1/session/{session_id}/confirm",
        json={"goal_text": "3ヶ月で毎週1回、1on1で課題を言語化"},
    )
    assert response.status_code == 200

    data = response.json()
    assert data["user_id"] == user_id
    assert data["version"] == 1
    assert data["is_active"] is True

    with SqlSession(engine) as session:
        goals = session.exec(select(Goal).where(Goal.user_id == user_id)).all()
        assert len(goals) == 1
        goal = goals[0]
        assert goal.version == 1
        assert goal.is_active is True

        stored_session = session.get(SessionModel, session_id)
        assert stored_session is not None
        assert stored_session.report_final == "3ヶ月で毎週1回、1on1で課題を言語化"


def test_confirm_goal_second_time_switches_active_and_versions():
    app, engine = _build_test_app()
    user_id = _create_user(engine)
    session_id = _create_phase1_session(engine, user_id)
    client = TestClient(app)

    first = client.post(
        f"/api/v1/phase1/session/{session_id}/confirm",
        json={"goal_text": "初回ゴール"},
    )
    assert first.status_code == 200

    second = client.post(
        f"/api/v1/phase1/session/{session_id}/confirm",
        json={"goal_text": "2回目ゴール"},
    )
    assert second.status_code == 200
    assert second.json()["version"] == 2

    with SqlSession(engine) as session:
        goals = session.exec(select(Goal).where(Goal.user_id == user_id)).all()
        assert len(goals) == 2
        active = [goal for goal in goals if goal.is_active]
        assert len(active) == 1
        assert active[0].version == 2
        inactive_versions = [goal.version for goal in goals if not goal.is_active]
        assert inactive_versions == [1]


def test_confirm_goal_session_not_found_returns_404():
    app, _engine = _build_test_app()
    client = TestClient(app)

    response = client.post(
        f"/api/v1/phase1/session/{uuid4()}/confirm",
        json={"goal_text": "missing"},
    )
    assert response.status_code == 404


def test_confirm_goal_phase_mismatch_returns_400():
    app, engine = _build_test_app()
    user_id = _create_user(engine)

    with SqlSession(engine) as session:
        wrong_phase = SessionModel(
            id=uuid4(),
            user_id=user_id,
            session_date=date.today(),
            phase=2,
            log_json=[{"role": "system", "content": "system"}],
            meta_data={},
        )
        session.add(wrong_phase)
        session.commit()
        session.refresh(wrong_phase)
        session_id = wrong_phase.id

    client = TestClient(app)
    response = client.post(
        f"/api/v1/phase1/session/{session_id}/confirm",
        json={"goal_text": "phase error"},
    )
    assert response.status_code == 400


def test_confirm_goal_unique_violation_returns_409(monkeypatch):
    app, engine = _build_test_app()
    user_id = _create_user(engine)
    session_id = _create_phase1_session(engine, user_id)
    client = TestClient(app)

    def _raise_integrity_error(*_args, **_kwargs):
        raise IntegrityError("statement", "params", "orig")

    monkeypatch.setattr(phase1_goal_service.goals_repository, "insert_goal", _raise_integrity_error)

    response = client.post(
        f"/api/v1/phase1/session/{session_id}/confirm",
        json={"goal_text": "conflict"},
    )
    assert response.status_code == 409

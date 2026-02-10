from __future__ import annotations

import sys
from pathlib import Path
from uuid import UUID

from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import SQLModel, Session as SqlSession, create_engine

BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from app.api.phase3_router import router as phase3_router
from app.core.db import get_session
from app.models.session import Session as SessionModel
from app.models.user import User
from app.repositories import goals_repository
from app.services.phase3_service import DEFAULT_GOAL_TEXT


def _build_test_app():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)

    app = FastAPI()
    app.include_router(phase3_router)

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


def _create_active_goal(engine, user_id: int, content: str) -> None:
    with SqlSession(engine) as session:
        goals_repository.insert_goal(
            session=session,
            user_id=user_id,
            content=content,
            version=1,
            is_active=True,
        )
        session.commit()


def test_create_phase3_session_with_goal_injected():
    app, engine = _build_test_app()
    user_id = _create_user(engine)
    goal_text = "毎日5分の振り返り"
    _create_active_goal(engine, user_id, goal_text)
    client = TestClient(app)

    response = client.post("/api/v1/phase3/session", json={"user_id": user_id})
    assert response.status_code == 200

    data = response.json()
    assert data["phase"] == 3
    assert data["goal_injected"] is True
    assert data["session_id"]

    session_id = UUID(data["session_id"])
    with SqlSession(engine) as session:
        created = session.get(SessionModel, session_id)
        assert created is not None
        assert created.log_json[0]["role"] == "system"
        assert goal_text in created.log_json[0]["content"]


def test_create_phase3_session_without_goal():
    app, engine = _build_test_app()
    user_id = _create_user(engine)
    client = TestClient(app)

    response = client.post("/api/v1/phase3/session", json={"user_id": user_id})
    assert response.status_code == 200

    data = response.json()
    assert data["goal_injected"] is False

    session_id = UUID(data["session_id"])
    with SqlSession(engine) as session:
        created = session.get(SessionModel, session_id)
        assert created is not None
        assert DEFAULT_GOAL_TEXT in created.log_json[0]["content"]


def test_meta_data_contains_system_prompt_hash():
    app, engine = _build_test_app()
    user_id_with_goal = _create_user(engine)
    user_id_without_goal = _create_user(engine)
    _create_active_goal(engine, user_id_with_goal, "週次レビューを続ける")
    client = TestClient(app)

    with_goal = client.post("/api/v1/phase3/session", json={"user_id": user_id_with_goal})
    assert with_goal.status_code == 200
    without_goal = client.post("/api/v1/phase3/session", json={"user_id": user_id_without_goal})
    assert without_goal.status_code == 200

    with_goal_id = UUID(with_goal.json()["session_id"])
    without_goal_id = UUID(without_goal.json()["session_id"])

    with SqlSession(engine) as session:
        with_goal_session = session.get(SessionModel, with_goal_id)
        without_goal_session = session.get(SessionModel, without_goal_id)
        assert with_goal_session is not None
        assert without_goal_session is not None

        with_hash = with_goal_session.meta_data.get("system_prompt_hash")
        without_hash = without_goal_session.meta_data.get("system_prompt_hash")

        assert with_hash
        assert without_hash
        assert with_hash != without_hash

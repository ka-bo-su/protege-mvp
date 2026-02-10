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

from app.api.phase1_router import router as phase1_router
from app.core.db import get_session
from app.models.session import Session as SessionModel
from app.models.user import User
from app.prompts.prompt_loader import load_prompt
from app.utils.prompt_hash import generate_prompt_hash


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


def test_create_phase1_session_success():
    app, engine = _build_test_app()
    user_id = _create_user(engine)
    client = TestClient(app)

    response = client.post("/api/v1/phase1/session", json={"user_id": user_id})
    assert response.status_code == 200

    data = response.json()
    assert data["phase"] == 1
    assert data["session_id"]
    assert data["created_at"]

    prompt_text = load_prompt("phase1")
    session_id = UUID(data["session_id"])

    with SqlSession(engine) as session:
        created = session.get(SessionModel, session_id)
        assert created is not None
        assert isinstance(created.log_json, list)
        assert created.log_json[0]["role"] == "system"
        assert created.log_json[0]["content"] == prompt_text


def test_invalid_user_id_returns_400():
    app, _engine = _build_test_app()
    client = TestClient(app)

    response = client.post("/api/v1/phase1/session", json={"user_id": "abc"})
    assert response.status_code == 400


def test_meta_data_contains_prompt_hash():
    app, engine = _build_test_app()
    user_id = _create_user(engine)
    client = TestClient(app)

    response = client.post("/api/v1/phase1/session", json={"user_id": user_id})
    assert response.status_code == 200

    data = response.json()
    prompt_text = load_prompt("phase1")
    expected_hash = generate_prompt_hash(prompt_text)
    session_id = UUID(data["session_id"])

    with SqlSession(engine) as session:
        created = session.get(SessionModel, session_id)
        assert created is not None
        assert created.meta_data["prompt_hash"] == expected_hash
        assert created.meta_data["system_prompt_hash"] == expected_hash

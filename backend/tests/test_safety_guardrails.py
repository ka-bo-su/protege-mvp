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
from app.services import phase1_chat_service, phase1_service
from app.safety.safety_rules import ESCALATION_RESPONSE, SAFETY_VERSION
from app.utils import prompt_hash
from app.utils.prompt_builder import build_system_prompt, load_safety_prompt


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


def test_safety_normal_flow():
    app, engine = _build_test_app()
    user_id = _create_user(engine)
    session_id = _create_phase1_session(engine, user_id)
    client = TestClient(app)

    with SqlSession(engine) as session:
        existing = session.get(SessionModel, session_id)
        assert existing is not None
        assert existing.meta_data.get("safety_version") == SAFETY_VERSION
        assert existing.meta_data.get("safety_triggered") is False

    response = client.post(
        f"/api/v1/phase1/session/{session_id}/turn",
        json={"message": "今日はチームの振り返りをしました"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "[MOCK RESPONSE]" in data["assistant_message"]

    with SqlSession(engine) as session:
        updated = session.get(SessionModel, session_id)
        assert updated is not None
        assert updated.meta_data.get("safety_triggered") is False


def test_safety_escalation_flow(monkeypatch):
    app, engine = _build_test_app()
    user_id = _create_user(engine)
    session_id = _create_phase1_session(engine, user_id)
    client = TestClient(app)

    def _blocked_client(_config):
        raise AssertionError("LLM should not be called for high-risk input")

    monkeypatch.setattr(phase1_chat_service, "get_llm_client", _blocked_client)

    response = client.post(
        f"/api/v1/phase1/session/{session_id}/turn",
        json={"message": "もう終わりたい"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["assistant_message"] == ESCALATION_RESPONSE

    with SqlSession(engine) as session:
        updated = session.get(SessionModel, session_id)
        assert updated is not None
        assert updated.meta_data.get("safety_triggered") is True
        assert updated.log_json[-1]["content"] == ESCALATION_RESPONSE


def test_prompt_hash_includes_safety():
    base_prompt = load_prompt("phase1")
    safety_prompt = load_safety_prompt()
    system_prompt = build_system_prompt("phase1")

    assert safety_prompt.strip() in system_prompt
    assert prompt_hash.generate_prompt_hash(base_prompt) != prompt_hash.generate_prompt_hash(
        system_prompt
    )

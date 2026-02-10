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
from app.api.phase3_router import router as phase3_router
from app.core.db import get_session
from app.models.session import Session as SessionModel
from app.models.user import User
from app.safety.safety_rules import ESCALATION_RESPONSE, SAFETY_VERSION
from app.services import phase1_chat_service, phase1_service, phase3_chat_service, phase3_service


def _build_test_app():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)

    app = FastAPI()
    app.include_router(phase1_router)
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


def _create_phase1_session(engine, user_id: int) -> UUID:
    with SqlSession(engine) as session:
        created = phase1_service.start_phase1_session(session, user_id)
        return created.id


def _create_phase3_session(engine, user_id: int) -> UUID:
    with SqlSession(engine) as session:
        created, _goal_injected = phase3_service.start_phase3_session(session, user_id)
        return created.id


def test_phase1_normal_turn_calls_llm(monkeypatch):
    app, engine = _build_test_app()
    user_id = _create_user(engine)
    session_id = _create_phase1_session(engine, user_id)
    client = TestClient(app)
    called = {"count": 0}

    class _StubClient:
        async def generate(self, _system_prompt: str, _message: str) -> str:
            called["count"] += 1
            return "normal response"

    def _fake_client(_config):
        return _StubClient()

    monkeypatch.setattr(phase1_chat_service, "get_llm_client", _fake_client)

    response = client.post(
        f"/api/v1/phase1/session/{session_id}/turn",
        json={"message": "今日は穏やかな気持ちです"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["assistant_message"] == "normal response"
    assert data["emergency"] is False
    assert called["count"] == 1

    with SqlSession(engine) as session:
        updated = session.get(SessionModel, session_id)
        assert updated is not None
        assert updated.meta_data.get("safety_triggered") is False
        assert updated.log_json[-1]["content"] == "normal response"


def test_phase1_emergency_turn_skips_llm(monkeypatch):
    app, engine = _build_test_app()
    user_id = _create_user(engine)
    session_id = _create_phase1_session(engine, user_id)
    client = TestClient(app)

    def _blocked_client(_config):
        raise AssertionError("LLM should not be called for emergency input")

    monkeypatch.setattr(phase1_chat_service, "get_llm_client", _blocked_client)

    response = client.post(
        f"/api/v1/phase1/session/{session_id}/turn",
        json={"message": "もう終わりたい"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["assistant_message"] == ESCALATION_RESPONSE
    assert data["emergency"] is True

    with SqlSession(engine) as session:
        updated = session.get(SessionModel, session_id)
        assert updated is not None
        assert updated.meta_data.get("safety_version") == SAFETY_VERSION
        assert updated.meta_data.get("safety_triggered") is True
        assert updated.meta_data.get("safety_reason") == "high_risk_keyword"
        assert updated.log_json[-2]["role"] == "user"
        assert updated.log_json[-1]["content"] == ESCALATION_RESPONSE


def test_phase3_emergency_turn_skips_llm(monkeypatch):
    app, engine = _build_test_app()
    user_id = _create_user(engine)
    session_id = _create_phase3_session(engine, user_id)
    client = TestClient(app)

    def _blocked_client(_config):
        raise AssertionError("LLM should not be called for emergency input")

    monkeypatch.setattr(phase3_chat_service, "get_llm_client", _blocked_client)

    response = client.post(
        f"/api/v1/phase3/session/{session_id}/turn",
        json={"message": "死にたい"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["assistant_message"] == ESCALATION_RESPONSE
    assert data["emergency"] is True

    with SqlSession(engine) as session:
        updated = session.get(SessionModel, session_id)
        assert updated is not None
        assert updated.meta_data.get("safety_version") == SAFETY_VERSION
        assert updated.meta_data.get("safety_triggered") is True
        assert updated.meta_data.get("safety_reason") == "high_risk_keyword"
        assert updated.log_json[-2]["role"] == "user"
        assert updated.log_json[-1]["content"] == ESCALATION_RESPONSE

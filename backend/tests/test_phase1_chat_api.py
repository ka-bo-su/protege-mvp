from __future__ import annotations

import sys
from pathlib import Path
from datetime import date
from uuid import UUID, uuid4

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
from app.services import phase1_service


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


def test_append_phase1_turn_success():
    app, engine = _build_test_app()
    user_id = _create_user(engine)
    session_id = _create_phase1_session(engine, user_id)
    client = TestClient(app)

    with SqlSession(engine) as session:
        before = session.get(SessionModel, session_id)
        assert before is not None
        before_meta = dict(before.meta_data)

    response = client.post(
        f"/api/v1/phase1/session/{session_id}/turn",
        json={"message": "今日はチームの目標を整理しました"},
    )
    assert response.status_code == 200

    data = response.json()
    assert data["session_id"] == str(session_id)
    assert "[MOCK RESPONSE]" in data["assistant_message"]
    assert isinstance(data["turn_index"], int)

    with SqlSession(engine) as session:
        updated = session.get(SessionModel, session_id)
        assert updated is not None
        assert isinstance(updated.log_json, list)
        assert updated.log_json[-2]["role"] == "user"
        assert updated.log_json[-1]["role"] == "assistant"
        assert updated.meta_data == before_meta


def test_append_phase1_turn_session_not_found():
    app, _engine = _build_test_app()
    client = TestClient(app)

    response = client.post(
        f"/api/v1/phase1/session/{uuid4()}/turn",
        json={"message": "こんにちは"},
    )
    assert response.status_code == 404


def test_append_phase1_turn_phase_mismatch():
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
        f"/api/v1/phase1/session/{session_id}/turn",
        json={"message": "phase error"},
    )
    assert response.status_code == 400


def test_append_phase1_turn_log_order():
    app, engine = _build_test_app()
    user_id = _create_user(engine)
    session_id = _create_phase1_session(engine, user_id)
    client = TestClient(app)

    response = client.post(
        f"/api/v1/phase1/session/{session_id}/turn",
        json={"message": "ログ順序確認"},
    )
    assert response.status_code == 200

    with SqlSession(engine) as session:
        updated = session.get(SessionModel, session_id)
        assert updated is not None
        roles = [entry["role"] for entry in updated.log_json]
        assert roles[-3:] == ["system", "user", "assistant"]

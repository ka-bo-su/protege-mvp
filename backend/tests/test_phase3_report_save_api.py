from __future__ import annotations

import sys
from datetime import date
from pathlib import Path
from uuid import UUID, uuid4

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
from app.services import phase3_service


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


def _create_phase3_session(engine, user_id: int) -> UUID:
    with SqlSession(engine) as session:
        created, _goal_injected = phase3_service.start_phase3_session(session, user_id)
        return created.id


def test_save_phase3_report_final_success_with_draft():
    app, engine = _build_test_app()
    user_id = _create_user(engine)
    session_id = _create_phase3_session(engine, user_id)

    with SqlSession(engine) as session:
        existing = session.get(SessionModel, session_id)
        assert existing is not None
        existing.report_draft = "# draft\n- item"
        session.add(existing)
        session.commit()

    client = TestClient(app)
    response = client.put(
        f"/api/v1/phase3/session/{session_id}/report/final",
        json={"report_final": "# final\n- updated"},
    )
    assert response.status_code == 200

    data = response.json()
    assert data["session_id"] == str(session_id)
    assert data["saved"] is True
    assert "edit_metrics" in data
    assert isinstance(data["edit_metrics"]["ratio"], float)

    with SqlSession(engine) as session:
        updated = session.get(SessionModel, session_id)
        assert updated is not None
        assert updated.report_final == "# final\n- updated"
        assert updated.edit_metrics is not None
        assert isinstance(updated.edit_metrics.get("ratio"), float)


def test_save_phase3_report_final_success_without_draft():
    app, engine = _build_test_app()
    user_id = _create_user(engine)
    session_id = _create_phase3_session(engine, user_id)

    client = TestClient(app)
    response = client.put(
        f"/api/v1/phase3/session/{session_id}/report/final",
        json={"report_final": "# final\n- entry"},
    )
    assert response.status_code == 200

    data = response.json()
    assert data["saved"] is True
    assert isinstance(data["edit_metrics"]["ratio"], float)

    with SqlSession(engine) as session:
        updated = session.get(SessionModel, session_id)
        assert updated is not None
        assert updated.report_final == "# final\n- entry"
        assert updated.edit_metrics is not None


def test_save_phase3_report_final_session_not_found():
    app, _engine = _build_test_app()
    client = TestClient(app)

    response = client.put(
        f"/api/v1/phase3/session/{uuid4()}/report/final",
        json={"report_final": "# final"},
    )
    assert response.status_code == 404


def test_save_phase3_report_final_phase_mismatch():
    app, engine = _build_test_app()
    user_id = _create_user(engine)

    with SqlSession(engine) as session:
        wrong_phase = SessionModel(
            id=uuid4(),
            user_id=user_id,
            session_date=date.today(),
            phase=1,
            log_json=[{"role": "system", "content": "system"}],
            meta_data={},
        )
        session.add(wrong_phase)
        session.commit()
        session.refresh(wrong_phase)
        session_id = wrong_phase.id

    client = TestClient(app)
    response = client.put(
        f"/api/v1/phase3/session/{session_id}/report/final",
        json={"report_final": "# final"},
    )
    assert response.status_code == 400


def test_save_phase3_report_final_empty_final():
    app, engine = _build_test_app()
    user_id = _create_user(engine)
    session_id = _create_phase3_session(engine, user_id)

    client = TestClient(app)
    response = client.put(
        f"/api/v1/phase3/session/{session_id}/report/final",
        json={"report_final": "   "},
    )
    assert response.status_code == 400

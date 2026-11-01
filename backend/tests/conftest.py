import sys
from pathlib import Path

# Ensure repository root is on sys.path so tests can be run seamlessly
_repo_root = Path(__file__).resolve().parent.parent.parent
if str(_repo_root) not in sys.path:
    sys.path.insert(0, str(_repo_root))

import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.core.database import SessionLocal
from backend.app.models.user import AppUser
from backend.app.core.security import hash_password


@pytest.fixture(scope="session")
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture
def db():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def auth_headers_student_a(client):
    res = client.post("/api/auth/login", json={
        "email": "u23cs001@svnit.ac.in",
        "password": "Svnit@2026!"
    })
    token = res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def auth_headers_student_b(client):
    res = client.post("/api/auth/login", json={
        "email": "u23cs002@svnit.ac.in",
        "password": "Svnit@2026!"
    })
    token = res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def auth_headers_admin(client):
    res = client.post("/api/auth/login", json={
        "email": "admin@svnit.ac.in",
        "password": "Svnit@2026!"
    })
    token = res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

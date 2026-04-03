import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app
from app.db.session import SessionLocal
from app.models.user import User
from app.models.financial_record import FinancialRecord


@pytest.fixture(scope="session")
def client():
    return TestClient(app)


@pytest.fixture(scope="session")
def db():
    session = SessionLocal()
    yield session
    session.close()


@pytest.fixture(scope="session")
def admin_token(client):
    res = client.post("/api/v1/auth/login", json={
        "email": "admin@finance.com",
        "password": "admin123"
    })
    assert res.status_code == 200, "Admin seed user missing — run: uv run python seed.py"
    return res.json()["access_token"]


@pytest.fixture(scope="session")
def analyst_token(client, admin_token):
    client.post("/api/v1/users",
        json={"name": "Test Analyst", "email": "analyst@test.com", "password": "pass1234", "role": "ANALYST"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    res = client.post("/api/v1/auth/login", json={
        "email": "analyst@test.com",
        "password": "pass1234"
    })
    return res.json()["access_token"]


@pytest.fixture(scope="session")
def viewer_token(client):
    client.post("/api/v1/auth/register", json={
        "name": "Test Viewer",
        "email": "viewer@test.com",
        "password": "pass1234"
    })
    res = client.post("/api/v1/auth/login", json={
        "email": "viewer@test.com",
        "password": "pass1234"
    })
    return res.json()["access_token"]


@pytest.fixture(scope="session", autouse=True)
def cleanup_test_data(db: Session):
    yield
    # Runs once after all tests complete
    db.query(FinancialRecord).filter(FinancialRecord.category == "TestCategory").delete()
    db.query(User).filter(User.email.in_(["analyst@test.com", "viewer@test.com"])).delete()
    db.commit()
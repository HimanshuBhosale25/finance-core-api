def test_register_new_user(client):
    res = client.post("/api/v1/auth/register", json={
        "name": "Fresh User",
        "email": "fresh@test.com",
        "password": "pass1234"
    })
    assert res.status_code == 201
    data = res.json()
    assert data["email"] == "fresh@test.com"
    assert data["role"] == "VIEWER"
    assert data["status"] == "ACTIVE"
    assert "password_hash" not in data


def test_register_duplicate_email(client):
    res = client.post("/api/v1/auth/register", json={
        "name": "Duplicate",
        "email": "fresh@test.com",
        "password": "pass1234"
    })
    assert res.status_code == 409


def test_register_invalid_email(client):
    res = client.post("/api/v1/auth/register", json={
        "name": "Bad Email",
        "email": "not-an-email",
        "password": "pass1234"
    })
    assert res.status_code == 422


def test_register_short_password(client):
    res = client.post("/api/v1/auth/register", json={
        "name": "Short Pass",
        "email": "shortpass@test.com",
        "password": "123"
    })
    assert res.status_code == 422


def test_login_success(client):
    res = client.post("/api/v1/auth/login", json={
        "email": "admin@finance.com",
        "password": "admin123"
    })
    assert res.status_code == 200
    assert "access_token" in res.json()
    assert res.json()["token_type"] == "bearer"


def test_login_wrong_password(client):
    res = client.post("/api/v1/auth/login", json={
        "email": "admin@finance.com",
        "password": "wrongpassword"
    })
    assert res.status_code == 401


def test_login_nonexistent_user(client):
    res = client.post("/api/v1/auth/login", json={
        "email": "ghost@nowhere.com",
        "password": "pass1234"
    })
    assert res.status_code == 401


def test_me_returns_current_user(client, admin_token):
    res = client.get("/api/v1/auth/me",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert res.status_code == 200
    assert res.json()["role"] == "ADMIN"


def test_me_without_token(client):
    res = client.get("/api/v1/auth/me")
    assert res.status_code == 401


def test_logout_blacklists_token(client):
    # Get a fresh token
    res = client.post("/api/v1/auth/login", json={
        "email": "admin@finance.com",
        "password": "admin123"
    })
    token = res.json()["access_token"]

    # Logout
    logout_res = client.post("/api/v1/auth/logout",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert logout_res.status_code == 200

    # Same token should now be rejected
    me_res = client.get("/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert me_res.status_code == 401
    assert "invalidated" in me_res.json()["detail"]
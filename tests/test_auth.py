def test_register(client):
    res = client.post("/api/v1/auth/register", json={
        "email": "user@example.com",
        "password": "secret123",
        "full_name": "Test User",
    })
    assert res.status_code == 201
    body = res.json()
    assert body["email"] == "user@example.com"
    assert body["is_active"] is True


def test_register_duplicate(client):
    payload = {"email": "dup@example.com", "password": "secret123"}
    client.post("/api/v1/auth/register", json=payload)
    res = client.post("/api/v1/auth/register", json=payload)
    assert res.status_code == 409


def test_login(client):
    client.post("/api/v1/auth/register", json={"email": "u@example.com", "password": "pass1234"})
    res = client.post("/api/v1/auth/login", json={"email": "u@example.com", "password": "pass1234"})
    assert res.status_code == 200
    assert "access_token" in res.json()


def test_login_wrong_password(client):
    client.post("/api/v1/auth/register", json={"email": "u2@example.com", "password": "correct"})
    res = client.post("/api/v1/auth/login", json={"email": "u2@example.com", "password": "wrong"})
    assert res.status_code == 401

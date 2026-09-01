from app.core.security import decode_access_token


async def test_admin_login_success(client, admin_user):
    resp = await client.post(
        "/api/v1/auth/login", json={"email": admin_user.email, "password": "Admin@123"}
    )
    assert resp.status_code == 200
    body = resp.json()["data"]
    assert "access_token" in body
    payload = decode_access_token(body["access_token"])
    assert payload["sub"] == admin_user.id
    assert payload["role"] == "ADMIN"


async def test_user_login_success(client, normal_user):
    resp = await client.post(
        "/api/v1/auth/login", json={"email": normal_user.email, "password": "User@123"}
    )
    assert resp.status_code == 200
    payload = decode_access_token(resp.json()["data"]["access_token"])
    assert payload["role"] == "VOLUNTEER"


async def test_login_invalid_password(client, admin_user):
    resp = await client.post(
        "/api/v1/auth/login", json={"email": admin_user.email, "password": "wrong-password"}
    )
    assert resp.status_code == 401
    body = resp.json()
    assert body["success"] is False
    assert body["error"] == "UNAUTHORIZED"


async def test_me_with_invalid_token(client):
    resp = await client.get("/api/v1/auth/me", headers={"Authorization": "Bearer not-a-real-token"})
    assert resp.status_code == 401


async def test_me_with_expired_token_shape_rejected(client):
    # a token signed with a bogus secret is indistinguishable from expired/tampered
    resp = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJ4In0.invalidsignature"},
    )
    assert resp.status_code == 401


async def test_register_always_creates_volunteer_role(client, db_session):
    resp = await client.post(
        "/api/v1/auth/register",
        json={"name": "New Person", "email": "newperson@example.com", "password": "Passw0rd!"},
    )
    assert resp.status_code == 201
    assert resp.json()["data"]["role"] == "VOLUNTEER"


async def test_register_duplicate_email_conflict(client, normal_user):
    resp = await client.post(
        "/api/v1/auth/register",
        json={"name": "Dup", "email": normal_user.email, "password": "Passw0rd!"},
    )
    assert resp.status_code == 409
    assert resp.json()["error"] == "CONFLICT"

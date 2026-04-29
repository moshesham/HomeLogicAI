from __future__ import annotations

from httpx import AsyncClient

_USER = {
    "email": "auth_test@example.com",
    "full_name": "Auth Tester",
    "password": "SecurePass1!",
}


async def test_register_success(client: AsyncClient) -> None:
    resp = await client.post("/auth/register", json=_USER)
    assert resp.status_code == 200
    body = resp.json()
    assert "access_token" in body
    assert body.get("token_type", "bearer") == "bearer"


async def test_register_duplicate_email(client: AsyncClient) -> None:
    await client.post("/auth/register", json=_USER)
    resp = await client.post("/auth/register", json=_USER)
    assert resp.status_code == 400


async def test_login_success(client: AsyncClient) -> None:
    await client.post("/auth/register", json=_USER)
    resp = await client.post(
        "/auth/login",
        data={"username": _USER["email"], "password": _USER["password"]},
    )
    assert resp.status_code == 200
    assert "access_token" in resp.json()


async def test_login_wrong_password(client: AsyncClient) -> None:
    await client.post("/auth/register", json=_USER)
    resp = await client.post(
        "/auth/login",
        data={"username": _USER["email"], "password": "wrongpassword"},
    )
    assert resp.status_code == 401


async def test_login_unknown_user(client: AsyncClient) -> None:
    resp = await client.post(
        "/auth/login",
        data={"username": "nobody@example.com", "password": "whatever"},
    )
    assert resp.status_code == 401


async def test_get_me(client: AsyncClient) -> None:
    reg = await client.post("/auth/register", json=_USER)
    token = reg.json()["access_token"]
    resp = await client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["email"] == _USER["email"]
    assert data["full_name"] == _USER["full_name"]


async def test_get_me_invalid_token(client: AsyncClient) -> None:
    resp = await client.get(
        "/auth/me", headers={"Authorization": "Bearer invalid.token.here"}
    )
    assert resp.status_code == 401


async def test_get_me_no_token(client: AsyncClient) -> None:
    resp = await client.get("/auth/me")
    assert resp.status_code == 401

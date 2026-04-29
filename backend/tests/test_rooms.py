from __future__ import annotations

from httpx import AsyncClient


async def test_create_room(
    client: AsyncClient, auth_headers: dict, project_id: str
) -> None:
    resp = await client.post(
        f"/projects/{project_id}/rooms",
        json={"name": "Living Room", "display_order": 1},
        headers=auth_headers,
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "Living Room"
    assert data["project_id"] == project_id


async def test_list_rooms(
    client: AsyncClient, auth_headers: dict, project_id: str
) -> None:
    await client.post(
        f"/projects/{project_id}/rooms",
        json={"name": "Room A"},
        headers=auth_headers,
    )
    await client.post(
        f"/projects/{project_id}/rooms",
        json={"name": "Room B"},
        headers=auth_headers,
    )
    resp = await client.get(f"/projects/{project_id}/rooms", headers=auth_headers)
    assert resp.status_code == 200
    assert len(resp.json()) >= 2


async def test_get_room(client: AsyncClient, auth_headers: dict, room_id: str) -> None:
    resp = await client.get(f"/rooms/{room_id}", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["id"] == room_id


async def test_get_room_not_found(client: AsyncClient, auth_headers: dict) -> None:
    resp = await client.get(
        "/rooms/00000000-0000-0000-0000-000000000000", headers=auth_headers
    )
    assert resp.status_code == 404


async def test_update_room(
    client: AsyncClient, auth_headers: dict, room_id: str
) -> None:
    resp = await client.put(
        f"/rooms/{room_id}",
        json={"name": "Renovated Kitchen", "room_budget": 12000.0},
        headers=auth_headers,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["name"] == "Renovated Kitchen"
    assert data["room_budget"] == 12000.0


async def test_delete_room(
    client: AsyncClient, auth_headers: dict, project_id: str
) -> None:
    create_resp = await client.post(
        f"/projects/{project_id}/rooms",
        json={"name": "Temp Room"},
        headers=auth_headers,
    )
    rid = create_resp.json()["id"]
    del_resp = await client.delete(f"/rooms/{rid}", headers=auth_headers)
    assert del_resp.status_code == 204
    get_resp = await client.get(f"/rooms/{rid}", headers=auth_headers)
    assert get_resp.status_code == 404

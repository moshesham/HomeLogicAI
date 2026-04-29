from __future__ import annotations

from httpx import AsyncClient


async def test_create_category(
    client: AsyncClient, auth_headers: dict, room_id: str
) -> None:
    resp = await client.post(
        f"/rooms/{room_id}/categories",
        json={
            "category_slug": "ceiling-fans",
            "display_name": "Ceiling Fans",
            "display_order": 0,
        },
        headers=auth_headers,
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["category_slug"] == "ceiling-fans"
    assert data["room_id"] == room_id


async def test_create_category_unknown_slug(
    client: AsyncClient, auth_headers: dict, room_id: str
) -> None:
    resp = await client.post(
        f"/rooms/{room_id}/categories",
        json={
            "category_slug": "nonexistent-slug",
            "display_name": "Unknown",
            "display_order": 0,
        },
        headers=auth_headers,
    )
    assert resp.status_code == 404


async def test_list_categories(
    client: AsyncClient, auth_headers: dict, room_id: str
) -> None:
    await client.post(
        f"/rooms/{room_id}/categories",
        json={
            "category_slug": "ceiling-fans",
            "display_name": "Fans",
            "display_order": 0,
        },
        headers=auth_headers,
    )
    resp = await client.get(f"/rooms/{room_id}/categories", headers=auth_headers)
    assert resp.status_code == 200
    assert len(resp.json()) >= 1


async def test_get_category(
    client: AsyncClient, auth_headers: dict, category_id: str
) -> None:
    resp = await client.get(f"/categories/{category_id}", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["id"] == category_id


async def test_get_category_not_found(client: AsyncClient, auth_headers: dict) -> None:
    resp = await client.get(
        "/categories/00000000-0000-0000-0000-000000000000", headers=auth_headers
    )
    assert resp.status_code == 404


async def test_update_category(
    client: AsyncClient, auth_headers: dict, category_id: str
) -> None:
    resp = await client.put(
        f"/categories/{category_id}",
        json={"display_name": "Fans Updated", "budget_allocated": 800.0},
        headers=auth_headers,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["display_name"] == "Fans Updated"
    assert data["budget_allocated"] == 800.0


async def test_delete_category(
    client: AsyncClient, auth_headers: dict, room_id: str
) -> None:
    create_resp = await client.post(
        f"/rooms/{room_id}/categories",
        json={
            "category_slug": "toilets",
            "display_name": "Toilets",
            "display_order": 1,
        },
        headers=auth_headers,
    )
    cid = create_resp.json()["id"]
    del_resp = await client.delete(f"/categories/{cid}", headers=auth_headers)
    assert del_resp.status_code == 204
    get_resp = await client.get(f"/categories/{cid}", headers=auth_headers)
    assert get_resp.status_code == 404


async def test_buyer_guide(client: AsyncClient) -> None:
    """GET /guides/{slug} returns the raw category schema (no auth needed)."""
    resp = await client.get("/guides/ceiling-fans")
    assert resp.status_code == 200
    data = resp.json()
    assert data["slug"] == "ceiling-fans"
    assert "attributes" in data


async def test_buyer_guide_not_found(client: AsyncClient) -> None:
    resp = await client.get("/guides/not-a-real-slug")
    assert resp.status_code == 404

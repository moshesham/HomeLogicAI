from __future__ import annotations

from httpx import AsyncClient


async def test_create_product(
    client: AsyncClient, auth_headers: dict, category_id: str
) -> None:
    resp = await client.post(
        f"/categories/{category_id}/products",
        json={
            "name": "Minka Aire F844",
            "price": 299.99,
            "currency": "USD",
            "category_slug": "ceiling-fans",
            "images": [],
            "attributes": {},
            "raw_specs": {},
        },
        headers=auth_headers,
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "Minka Aire F844"
    assert data["category_id"] == category_id


async def test_list_products(
    client: AsyncClient, auth_headers: dict, category_id: str
) -> None:
    for i in range(2):
        await client.post(
            f"/categories/{category_id}/products",
            json={
                "name": f"Fan {i}",
                "category_slug": "ceiling-fans",
                "images": [],
                "attributes": {},
                "raw_specs": {},
            },
            headers=auth_headers,
        )
    resp = await client.get(f"/categories/{category_id}/products", headers=auth_headers)
    assert resp.status_code == 200
    assert len(resp.json()) >= 2


async def test_get_product(
    client: AsyncClient, auth_headers: dict, category_id: str
) -> None:
    create = await client.post(
        f"/categories/{category_id}/products",
        json={
            "name": "Test Fan",
            "category_slug": "ceiling-fans",
            "images": [],
            "attributes": {},
            "raw_specs": {},
        },
        headers=auth_headers,
    )
    pid = create.json()["id"]
    resp = await client.get(f"/products/{pid}", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["id"] == pid


async def test_update_product(
    client: AsyncClient, auth_headers: dict, category_id: str
) -> None:
    create = await client.post(
        f"/categories/{category_id}/products",
        json={
            "name": "Old Name",
            "category_slug": "ceiling-fans",
            "images": [],
            "attributes": {},
            "raw_specs": {},
        },
        headers=auth_headers,
    )
    pid = create.json()["id"]
    resp = await client.put(
        f"/products/{pid}",
        json={"name": "New Name", "user_rating": 5},
        headers=auth_headers,
    )
    assert resp.status_code == 200
    assert resp.json()["name"] == "New Name"
    assert resp.json()["user_rating"] == 5


async def test_delete_product(
    client: AsyncClient, auth_headers: dict, category_id: str
) -> None:
    create = await client.post(
        f"/categories/{category_id}/products",
        json={
            "name": "Delete Me",
            "category_slug": "ceiling-fans",
            "images": [],
            "attributes": {},
            "raw_specs": {},
        },
        headers=auth_headers,
    )
    pid = create.json()["id"]
    del_resp = await client.delete(f"/products/{pid}", headers=auth_headers)
    assert del_resp.status_code == 204
    get_resp = await client.get(f"/products/{pid}", headers=auth_headers)
    assert get_resp.status_code == 404

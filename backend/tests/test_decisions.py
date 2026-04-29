from __future__ import annotations

from httpx import AsyncClient


async def _make_product(
    client: AsyncClient, auth_headers: dict, category_id: str, name: str = "Fan"
) -> str:
    resp = await client.post(
        f"/categories/{category_id}/products",
        json={
            "name": name,
            "category_slug": "ceiling-fans",
            "images": [],
            "attributes": {},
            "raw_specs": {},
        },
        headers=auth_headers,
    )
    assert resp.status_code == 201
    return resp.json()["id"]


async def test_create_decision(
    client: AsyncClient, auth_headers: dict, category_id: str
) -> None:
    resp = await client.post(
        f"/categories/{category_id}/decisions",
        json={
            "decision_type": "selected",
            "rationale": "Best value for money",
            "source": "manual",
        },
        headers=auth_headers,
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["decision_type"] == "selected"
    assert data["category_id"] == category_id


async def test_create_decision_with_product(
    client: AsyncClient, auth_headers: dict, category_id: str
) -> None:
    product_id = await _make_product(client, auth_headers, category_id)
    resp = await client.post(
        f"/categories/{category_id}/decisions",
        json={
            "decision_type": "shortlisted",
            "rationale": "Good specs",
            "product_id": product_id,
        },
        headers=auth_headers,
    )
    assert resp.status_code == 201
    assert resp.json()["product_id"] == product_id


async def test_list_decisions(
    client: AsyncClient, auth_headers: dict, category_id: str
) -> None:
    await client.post(
        f"/categories/{category_id}/decisions",
        json={"decision_type": "rejected", "rationale": "Too expensive"},
        headers=auth_headers,
    )
    resp = await client.get(
        f"/categories/{category_id}/decisions", headers=auth_headers
    )
    assert resp.status_code == 200
    assert len(resp.json()) >= 1


async def test_delete_decision(
    client: AsyncClient, auth_headers: dict, category_id: str
) -> None:
    create = await client.post(
        f"/categories/{category_id}/decisions",
        json={"decision_type": "selected", "rationale": "Final choice"},
        headers=auth_headers,
    )
    did = create.json()["id"]
    del_resp = await client.delete(f"/decisions/{did}", headers=auth_headers)
    assert del_resp.status_code == 204

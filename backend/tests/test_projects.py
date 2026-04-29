from __future__ import annotations

from httpx import AsyncClient


async def test_create_project(client: AsyncClient, auth_headers: dict) -> None:
    resp = await client.post(
        "/projects",
        json={"name": "My Reno", "total_budget": 50000.0},
        headers=auth_headers,
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "My Reno"
    assert data["total_budget"] == 50000.0
    assert "id" in data


async def test_list_projects(client: AsyncClient, auth_headers: dict) -> None:
    await client.post("/projects", json={"name": "P1"}, headers=auth_headers)
    await client.post("/projects", json={"name": "P2"}, headers=auth_headers)
    resp = await client.get("/projects", headers=auth_headers)
    assert resp.status_code == 200
    assert len(resp.json()) >= 2


async def test_get_project(
    client: AsyncClient, auth_headers: dict, project_id: str
) -> None:
    resp = await client.get(f"/projects/{project_id}", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["id"] == project_id


async def test_get_project_not_found(client: AsyncClient, auth_headers: dict) -> None:
    resp = await client.get(
        "/projects/00000000-0000-0000-0000-000000000000", headers=auth_headers
    )
    assert resp.status_code == 404


async def test_update_project(
    client: AsyncClient, auth_headers: dict, project_id: str
) -> None:
    resp = await client.put(
        f"/projects/{project_id}",
        json={"name": "Updated Name", "status": "completed"},
        headers=auth_headers,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["name"] == "Updated Name"
    assert data["status"] == "completed"


async def test_delete_project(client: AsyncClient, auth_headers: dict) -> None:
    create_resp = await client.post(
        "/projects", json={"name": "To Delete"}, headers=auth_headers
    )
    pid = create_resp.json()["id"]
    del_resp = await client.delete(f"/projects/{pid}", headers=auth_headers)
    assert del_resp.status_code == 204
    get_resp = await client.get(f"/projects/{pid}", headers=auth_headers)
    assert get_resp.status_code == 404


async def test_project_budget_breakdown(
    client: AsyncClient,
    auth_headers: dict,
    project_id: str,
) -> None:
    resp = await client.get(f"/projects/{project_id}/budget", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert "summary" in data
    assert "rooms" in data


async def test_list_projects_unauthenticated(client: AsyncClient) -> None:
    resp = await client.get("/projects")
    assert resp.status_code == 401

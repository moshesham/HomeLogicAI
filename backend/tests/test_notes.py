from __future__ import annotations

from httpx import AsyncClient


async def test_put_and_get_notes(
    client: AsyncClient, auth_headers: dict, category_id: str
) -> None:
    content = "# Kitchen Notes\n\nRemember to check measurements."
    put_resp = await client.put(
        f"/categories/{category_id}/notes",
        json={"content": content},
        headers=auth_headers,
    )
    assert put_resp.status_code == 200
    assert put_resp.json()["content"] == content

    get_resp = await client.get(
        f"/categories/{category_id}/notes", headers=auth_headers
    )
    assert get_resp.status_code == 200
    assert get_resp.json()["content"] == content


async def test_get_notes_empty(
    client: AsyncClient, auth_headers: dict, category_id: str
) -> None:
    resp = await client.get(f"/categories/{category_id}/notes", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["content"] == ""


async def test_get_project_journal(
    client: AsyncClient, auth_headers: dict, project_id: str, category_id: str
) -> None:
    # Write notes so the journal has an entry
    await client.put(
        f"/categories/{category_id}/notes",
        json={"content": "Journal note entry"},
        headers=auth_headers,
    )
    resp = await client.get(f"/projects/{project_id}/journal", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["project_id"] == project_id
    assert "entries" in data
    assert any(e["content"] == "Journal note entry" for e in data["entries"])


async def test_project_journal_empty(
    client: AsyncClient, auth_headers: dict, project_id: str
) -> None:
    resp = await client.get(f"/projects/{project_id}/journal", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["entries"] == []

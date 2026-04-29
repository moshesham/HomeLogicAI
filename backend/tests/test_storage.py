from __future__ import annotations

from pathlib import Path

from services.storage_service import (
    read_notes,
    write_notes,
)


def test_path_helpers(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("STORAGE_PATH", str(tmp_path))
    # reload settings-dependent module
    import importlib
    import services.storage_service as svc

    importlib.reload(svc)

    proj_path = svc.get_project_path("proj-1")
    assert str(proj_path).endswith("proj-1")

    room_path = svc.get_room_path("proj-1", "room-1")
    assert "rooms" in str(room_path)

    cat_path = svc.get_category_path("proj-1", "room-1", "cat-1")
    assert "categories" in str(cat_path)


def test_write_and_read_notes(tmp_path: Path) -> None:
    cat_path = tmp_path / "categories" / "cat-1"
    write_notes(cat_path, "# Notes\n\nSome content here.")
    content = read_notes(cat_path)
    assert content == "# Notes\n\nSome content here."


def test_read_notes_nonexistent(tmp_path: Path) -> None:
    cat_path = tmp_path / "categories" / "nonexistent"
    assert read_notes(cat_path) == ""


def test_delete_project_folder(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("STORAGE_PATH", str(tmp_path))
    import importlib
    import services.storage_service as svc

    importlib.reload(svc)

    proj_path = svc.get_project_path("del-test")
    proj_path.mkdir(parents=True)
    assert proj_path.exists()
    svc.delete_project_folder("del-test")
    assert not proj_path.exists()


def test_delete_nonexistent_project_folder(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("STORAGE_PATH", str(tmp_path))
    import importlib
    import services.storage_service as svc

    importlib.reload(svc)
    # Should not raise
    svc.delete_project_folder("does-not-exist")

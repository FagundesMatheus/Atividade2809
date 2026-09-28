from pathlib import Path
from typing import Any

import pytest
from fastapi import HTTPException

from nomeProjeto.api.routers import files
from nomeProjeto.application import services
from nomeProjeto.domain.file_item import FileItem
from nomeProjeto.infrastructure.sqlite_repo import LibraryRepository


def _build_file_item(name: str, absolute_path: str) -> FileItem:
    return FileItem(id=1, name=name, absolute_path=absolute_path, extension=Path(absolute_path).suffix)


def test_add_file_routes_url_sources(
    monkeypatch: pytest.MonkeyPatch,
    repo: LibraryRepository,
    tmp_path: Path,
) -> None:
    app_dir = tmp_path / ".nomeProjeto"
    app_dir.mkdir()

    called: dict[str, Any] = {}

    def fake_add_url_as_file(*, url: str, name: str, repo: LibraryRepository, app_dir: Path) -> FileItem:
        called["url"] = url
        called["name"] = name
        called["app_dir"] = app_dir
        return _build_file_item(name=name, absolute_path=str(app_dir / "urls" / f"{name}.url"))

    monkeypatch.setattr(services, "add_url_as_file", fake_add_url_as_file)

    payload = files.FileSourcePayload(source="https://example.com", name="example")

    result = files.add_file(payload=payload, repo=repo, app_dir=app_dir)

    assert result.name == "example"
    assert called["url"] == "https://example.com"
    assert called["name"] == "example"
    assert called["app_dir"] == app_dir


def test_add_file_routes_path_sources(
    monkeypatch: pytest.MonkeyPatch,
    repo: LibraryRepository,
    tmp_path: Path,
) -> None:
    source_file = tmp_path / "document.txt"
    source_file.write_text("content")

    called: dict[str, Any] = {}

    def fake_add_file_from_path(*, path: str, repo: LibraryRepository) -> FileItem:
        called["path"] = path
        return _build_file_item(name=Path(path).name, absolute_path=path)

    monkeypatch.setattr(services, "add_file_from_path", fake_add_file_from_path)

    payload = files.FileSourcePayload(source=str(source_file))

    result = files.add_file(payload=payload, repo=repo, app_dir=tmp_path)

    assert result.absolute_path == str(source_file)
    assert called["path"] == str(source_file)


def test_add_file_rejects_unsupported_source(repo: LibraryRepository, tmp_path: Path) -> None:
    payload = files.FileSourcePayload(source="not-a-url-or-file")

    with pytest.raises(HTTPException) as exc_info:
        files.add_file(payload=payload, repo=repo, app_dir=tmp_path)

    assert exc_info.value.status_code == 400


def test_add_file_with_category_routes_url_sources(
    monkeypatch: pytest.MonkeyPatch,
    repo: LibraryRepository,
    tmp_path: Path,
) -> None:
    app_dir = tmp_path / ".nomeProjeto"
    app_dir.mkdir()

    called: dict[str, Any] = {}

    def fake_add_url_with_category_and_image(
        *,
        url: str,
        name: str,
        categoryName: str,
        imagePath: str,
        repo: LibraryRepository,
        app_dir: Path,
    ) -> FileItem:
        called["url"] = url
        called["name"] = name
        called["categoryName"] = categoryName
        called["imagePath"] = imagePath
        called["app_dir"] = app_dir
        return _build_file_item(name=name, absolute_path=str(app_dir / "urls" / f"{name}.url"))

    monkeypatch.setattr(services, "add_url_with_category_and_image", fake_add_url_with_category_and_image)

    payload = files.FileSourceWithCategoryImagePayload(
        source="https://example.com",
        name="example",
        category_name="Books",
        image_path=str(tmp_path / "cover.jpg"),
    )

    result = files.add_file_with_category_and_image(payload=payload, repo=repo, app_dir=app_dir)

    assert result.name == "example"
    assert called["url"] == "https://example.com"
    assert called["categoryName"] == "Books"
    assert called["imagePath"] == str(tmp_path / "cover.jpg")


def test_add_file_with_category_routes_path_sources(
    monkeypatch: pytest.MonkeyPatch,
    repo: LibraryRepository,
    tmp_path: Path,
) -> None:
    source_file = tmp_path / "document.txt"
    source_file.write_text("content")

    called: dict[str, Any] = {}

    def fake_add_file_with_category_and_image(
        *,
        path: str,
        categoryName: str,
        imagePath: str,
        repo: LibraryRepository,
        app_dir: Path,
    ) -> FileItem:
        called["path"] = path
        called["categoryName"] = categoryName
        called["imagePath"] = imagePath
        return _build_file_item(name=Path(path).name, absolute_path=path)

    monkeypatch.setattr(services, "add_file_with_category_and_image", fake_add_file_with_category_and_image)

    payload = files.FileSourceWithCategoryImagePayload(
        source=str(source_file),
        category_name="Books",
        image_path=str(tmp_path / "cover.jpg"),
    )

    result = files.add_file_with_category_and_image(payload=payload, repo=repo, app_dir=tmp_path)

    assert result.absolute_path == str(source_file)
    assert called["path"] == str(source_file)
    assert called["categoryName"] == "Books"


def test_add_file_with_category_rejects_unsupported_source(repo: LibraryRepository, tmp_path: Path) -> None:
    payload = files.FileSourceWithCategoryImagePayload(
        source="not-a-url-or-file",
        category_name="Books",
        image_path="cover.jpg",
    )

    with pytest.raises(HTTPException) as exc_info:
        files.add_file_with_category_and_image(payload=payload, repo=repo, app_dir=tmp_path)

    assert exc_info.value.status_code == 400

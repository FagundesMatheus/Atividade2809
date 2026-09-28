from pathlib import Path

import pytest

from nomeProjeto.api.file_source import FileSourceKind, resolve_file_source_kind


def test_resolve_file_source_kind_detects_url() -> None:
    assert resolve_file_source_kind("https://example.com/item") is FileSourceKind.URL


def test_resolve_file_source_kind_detects_existing_file_path(tmp_path: Path) -> None:
    file_path = tmp_path / "document.txt"
    file_path.write_text("content")

    assert resolve_file_source_kind(str(file_path)) is FileSourceKind.PATH


def test_resolve_file_source_kind_rejects_invalid_source() -> None:
    with pytest.raises(ValueError):
        resolve_file_source_kind("not-a-url-or-file")

from functools import lru_cache
from pathlib import Path

from ..infrastructure.sqlite_repo import LibraryRepository
from ..infrastructure.file_manager import LocalFileManager


@lru_cache(maxsize=1)
def get_app_directory() -> Path:
    return LocalFileManager.ensure_app_directory()


@lru_cache(maxsize=1)
def get_repository() -> LibraryRepository:
    db_path = get_app_directory() / "nomeProjeto.db"
    return LibraryRepository(db_path=db_path)

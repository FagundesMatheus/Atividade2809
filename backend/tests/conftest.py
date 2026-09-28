from collections.abc import Iterator

import pytest
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker

from nomeProjeto.infrastructure.sqlite_repo import LibraryRepository
from nomeProjeto.infrastructure.database.models import Base


@pytest.fixture
def in_memory_db() -> Iterator[Engine]:
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)
    engine.dispose()


@pytest.fixture
def repo(in_memory_db: Engine) -> LibraryRepository:
    repo = LibraryRepository.__new__(LibraryRepository)
    repo.engine = in_memory_db
    repo.SessionLocal = sessionmaker(bind=in_memory_db)

    return repo

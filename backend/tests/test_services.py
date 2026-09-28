from pathlib import Path

import pytest

from nomeProjeto.infrastructure.sqlite_repo import LibraryRepository

from nomeProjeto.domain.exceptions import ItemAlreadyExistsError
from nomeProjeto.application.services import (
    add_file_from_path,
    add_files_from_folder,
    add_file_with_category_and_image,
    add_category_to_files,
    add_url_with_category_and_image,
    create_category,
    create_tag,
    get_all_categories,
    get_all_file_items,
    get_all_tags,
    get_category,
    get_file_item,
    get_tag,
)


def test_add_file_from_path(repo: LibraryRepository, tmp_path: Path) -> None:
    test_file = tmp_path / "test_document.txt"
    test_file.write_text("Test")

    fileitem = add_file_from_path(str(test_file), repo)

    assert fileitem.id is not None
    result = get_file_item(fileitem.id, repo)

    assert result.id is not None
    assert result.name == "test_document.txt"
    assert result.extension == ".txt"
    assert result.absolute_path == str(test_file)


def test_add_files_from_folder(repo: LibraryRepository, tmp_path: Path) -> None:
    folder = tmp_path / "test_folder2"
    folder.mkdir()

    test = folder / "file.txt"
    test.write_text("Test")
    for i in range(10):
        test_file = tmp_path / f"test_document_{i}.txt"
        test_file.write_text(f"Test: {i}")
    add_files_from_folder(path=str(tmp_path), repo=repo)

    assert len(get_all_file_items(repo)) == 10


def test_tag(repo: LibraryRepository) -> None:

    create_tag(tagName="testTag", repo=repo)
    tag = get_all_tags(repo)[0]

    assert tag.name == "testTag"
    assert tag.id is not None
    assert get_tag(tag.id, repo) == tag


def test_category(repo: LibraryRepository) -> None:
    create_category(categoryName="testCategory", repo=repo)
    category = get_all_categories(repo)[0]

    assert category.name == "testCategory"
    assert category.id is not None
    assert get_category(category.id, repo) == category


def test_add_duplicated_file_raises_error(repo: LibraryRepository, tmp_path: Path) -> None:
    test_file = tmp_path / "test_document.txt"
    test_file.write_text("Test")

    add_file_from_path(str(test_file), repo)
    with pytest.raises(ItemAlreadyExistsError):
        add_file_from_path(str(test_file), repo)


def test_add_file_with_category_and_image_creates_missing_category(repo: LibraryRepository, tmp_path: Path) -> None:
    app_dir = tmp_path / ".nomeProjeto"
    app_dir.mkdir()
    (app_dir / "images").mkdir()

    test_file = tmp_path / "test_document.txt"
    test_file.write_text("Test")

    image = tmp_path / "image.jpg"
    image.touch()

    fileitem = add_file_with_category_and_image(
        path=str(test_file),
        categoryName="Books",
        imagePath=str(image),
        repo=repo,
        app_dir=app_dir,
    )

    assert fileitem.id is not None
    assert fileitem.category_id is not None
    assert fileitem.image_id is not None
    assert fileitem.image_name == "image.jpg"
    assert get_all_categories(repo)[0].name == "Books"


def test_add_url_with_category_and_image_reuses_existing_category(repo: LibraryRepository, tmp_path: Path) -> None:
    app_dir = tmp_path / ".nomeProjeto"
    app_dir.mkdir()
    (app_dir / "images").mkdir()
    (app_dir / "urls").mkdir()

    create_category(categoryName="Books", repo=repo)

    image = tmp_path / "image.jpg"
    image.touch()

    fileitem = add_url_with_category_and_image(
        url="https://example.com",
        name="example",
        categoryName="Books",
        imagePath=str(image),
        repo=repo,
        app_dir=app_dir,
    )

    assert fileitem.id is not None
    assert fileitem.category_id is not None
    assert len(get_all_categories(repo)) == 1
    assert fileitem.image_name == "image.jpg"


def test_add_category_to_files_creates_missing_category(repo: LibraryRepository, tmp_path: Path) -> None:
    first = tmp_path / "first.txt"
    second = tmp_path / "second.txt"
    first.write_text("A")
    second.write_text("B")

    first_file = add_file_from_path(str(first), repo)
    second_file = add_file_from_path(str(second), repo)

    assert first_file.id is not None
    assert second_file.id is not None

    updated_files = add_category_to_files(
        fileIDs=[first_file.id, second_file.id],
        categoryName="Books",
        repo=repo,
    )

    assert len(updated_files) == 2
    assert all(file_item.category_id is not None for file_item in updated_files)
    assert len(get_all_categories(repo)) == 1


def test_add_category_to_files_reuses_existing_category(repo: LibraryRepository, tmp_path: Path) -> None:
    create_category(categoryName="Books", repo=repo)

    first = tmp_path / "first.txt"
    second = tmp_path / "second.txt"
    first.write_text("A")
    second.write_text("B")

    first_file = add_file_from_path(str(first), repo)
    second_file = add_file_from_path(str(second), repo)

    assert first_file.id is not None
    assert second_file.id is not None

    updated_files = add_category_to_files(
        fileIDs=[first_file.id, second_file.id],
        categoryName="Books",
        repo=repo,
    )

    assert len(updated_files) == 2
    assert all(file_item.category_id is not None for file_item in updated_files)
    assert len(get_all_categories(repo)) == 1

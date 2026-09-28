from pathlib import Path

import pytest

from nomeProjeto.domain.exceptions import DatabaseOperationError
from nomeProjeto.infrastructure.sqlite_repo import LibraryRepository

from nomeProjeto.application.services import (
    add_files_from_folder,
    create_category,
    create_tag,
    get_all_categories,
    get_all_file_items,
    get_all_tags,
    get_category,
    get_file_item,
    get_tag,
    add_url_as_file,
    add_tag_to_file,
    add_image_to_file,
    add_category_on_file,
    remove_category_from_file,
    remove_tag_from_file,
    delete_tag,
    delete_category,
    remove_file,
)


def test_creating_everything(repo: LibraryRepository, tmp_path: Path) -> None:
    app_dir = tmp_path / ".nomeProjeto"
    image_folder = app_dir / "images"
    url_folder = app_dir / "urls"
    aux_folder = tmp_path / "aux"

    app_dir.mkdir()
    image_folder.mkdir()
    url_folder.mkdir()
    aux_folder.mkdir()

    image = aux_folder / "image.jpg"
    image.touch()

    categoryname1 = "Books"
    categoryname2 = "Games"

    tagname1 = "Action"
    tagname2 = "Fantasy"
    tagname3 = "Ongoing"

    test_file1 = tmp_path / "Book1.txt"
    test_file1.write_text("Test")

    test_file2 = tmp_path / "Book2.txt"
    test_file2.write_text("Test")

    test_file3 = tmp_path / "Game1.exe"
    test_file3.touch()

    test_url = "google.com"

    create_category(categoryName=categoryname1, repo=repo)
    create_category(categoryName=categoryname2, repo=repo)

    create_tag(tagName=tagname1, repo=repo)
    create_tag(tagName=tagname2, repo=repo)
    create_tag(tagName=tagname3, repo=repo)

    add_files_from_folder(path=str(tmp_path), repo=repo)
    add_url_as_file(url=test_url, repo=repo, name="google", app_dir=app_dir)

    tagdict = {}
    for tag in get_all_tags(repo):
        assert tag.id is not None
        tagdict[tag.name] = tag.id

    categoriesdict = {}
    for category in get_all_categories(repo):
        assert category.id is not None
        categoriesdict[category.name] = category.id

    filesdict = {}
    for file_item in get_all_file_items(repo):
        assert file_item.id is not None
        filesdict[file_item.name] = file_item.id

    add_tag_to_file(fileID=filesdict[test_file1.name], tagID=tagdict[tagname1], repo=repo)
    add_tag_to_file(fileID=filesdict[test_file1.name], tagID=tagdict[tagname2], repo=repo)
    add_tag_to_file(fileID=filesdict[test_file1.name], tagID=tagdict[tagname3], repo=repo)
    add_category_on_file(fileID=filesdict[test_file1.name], categoryID=categoriesdict[categoryname1], repo=repo)

    imageID = add_image_to_file(
        imagePath=str(image), repo=repo, fileID=filesdict[test_file1.name], app_dir=app_dir
    ).image_id

    add_tag_to_file(fileID=filesdict[test_file2.name], tagID=tagdict[tagname2], repo=repo)
    add_category_on_file(fileID=filesdict[test_file2.name], categoryID=categoriesdict[categoryname2], repo=repo)

    add_tag_to_file(fileID=filesdict[test_file3.name], tagID=tagdict[tagname1], repo=repo)
    add_category_on_file(fileID=filesdict[test_file3.name], categoryID=categoriesdict[categoryname2], repo=repo)
    add_category_on_file(fileID=filesdict[test_file3.name], categoryID=categoriesdict[categoryname1], repo=repo)

    remove_category_from_file(fileID=filesdict[test_file1.name], repo=repo)
    remove_tag_from_file(fileID=filesdict[test_file1.name], repo=repo, tagID=tagdict[tagname3])

    delete_tag(tagID=tagdict[tagname2], repo=repo)
    delete_category(categoryID=categoriesdict[categoryname2], repo=repo)

    file1 = get_file_item(fileID=filesdict[test_file1.name], repo=repo)
    assert len(file1.tags) == 1
    assert file1.tags[0].id == tagdict[tagname1]
    assert file1.category_id is None
    assert file1.image_id == imageID

    file2 = get_file_item(fileID=filesdict[test_file2.name], repo=repo)
    assert len(file2.tags) == 0
    assert file2.category_id is None

    file3 = get_file_item(fileID=filesdict[test_file3.name], repo=repo)
    assert len(file3.tags) == 1
    assert file3.tags[0].id == tagdict[tagname1]
    assert file3.category_id == categoriesdict[categoryname1]

    remove_file(fileID=filesdict[test_file1.name], repo=repo)
    with pytest.raises(DatabaseOperationError):
        get_file_item(fileID=filesdict[test_file1.name], repo=repo)

    with pytest.raises(DatabaseOperationError):
        get_tag(tagID=tagdict[tagname2], repo=repo)
    with pytest.raises(DatabaseOperationError):
        get_category(categoryID=categoriesdict[categoryname2], repo=repo)

import os
import mimetypes
import subprocess
import sys
from pathlib import Path
from urllib.error import URLError
from urllib.parse import urlparse
from urllib.request import urlopen

from ..domain.category import Category
from ..domain.exceptions import FileExecutionError, FileNotFoundDomainError
from ..domain.file_item import FileItem
from ..domain.tag import Tag
from ..infrastructure.sqlite_repo import LibraryRepository
from ..infrastructure.file_manager import LocalFileManager


def _require_id(value: int | None, item_name: str) -> int:
    if value is None:
        raise ValueError(f"{item_name} id is required")

    return value


def _is_http_url(value: str) -> bool:
    parsed_url = urlparse(value)
    return parsed_url.scheme in {"http", "https"} and bool(parsed_url.netloc)


def _download_image(url: str, destination_dir: Path, file_id: int) -> Path:
    destination_dir.mkdir(parents=True, exist_ok=True)

    try:
        with urlopen(url) as response:
            suffix = Path(urlparse(url).path).suffix
            if not suffix:
                content_type = response.headers.get_content_type()
                suffix = mimetypes.guess_extension(content_type) or ""

            destination_file = destination_dir / f"image{file_id}{suffix}"

            if destination_file.exists():
                raise FileExecutionError(
                    f"Destination file already exists and overwrite is prevented: {destination_file}"
                )

            with destination_file.open("wb") as image_file:
                while chunk := response.read(8192):
                    image_file.write(chunk)

            return destination_file
    except URLError as error:
        raise FileExecutionError(f"Failed to download image from {url}: {error}") from error


def add_file_from_path(path: str, repo: LibraryRepository) -> FileItem:
    filepath = Path(path)
    file = FileItem(name=filepath.name, extension=filepath.suffix, absolute_path=path)
    fileitem = repo.save_file_item(file)
    return fileitem


def add_files_from_folder(path: str, repo: LibraryRepository) -> list[FileItem]:
    folderpath = Path(path)

    files = []

    for file in folderpath.iterdir():
        if file.is_file():
            files.append(add_file_from_path(path=str(file.resolve()), repo=repo))

    return files


def add_url_as_file(url: str, name: str, repo: LibraryRepository, app_dir: Path | None = None) -> FileItem:
    folder_path = LocalFileManager.get_urls_directory(base_dir=app_dir)
    file_path = folder_path / f"{name}.url"

    file_path.write_text(
        f"[InternetShortcut]\nURL={url}\n",
        encoding="utf-8",
    )

    return add_file_from_path(path=str(file_path), repo=repo)


def add_image_to_file(
    imagePath: str,
    repo: LibraryRepository,
    fileID: int,
    app_dir: Path | None = None,
) -> FileItem:
    images_directory = LocalFileManager.get_images_directory(base_dir=app_dir)

    if _is_http_url(imagePath):
        imagepath = _download_image(url=imagePath, destination_dir=images_directory, file_id=fileID)
    else:
        imagepath = LocalFileManager.move_file(
            source=Path(imagePath),
            destination=images_directory,
            create_copy=True,
        )

    fileitem = repo.update_file_image(file_id=fileID, image_name=imagepath.name, image_id=imagepath.stat().st_ino)
    return fileitem


def get_or_create_category(categoryName: str, repo: LibraryRepository) -> Category:
    for category in repo.get_all_categories():
        if category.name == categoryName:
            return category

    return create_category(categoryName=categoryName, repo=repo)


def add_file_with_category_and_image(
    path: str,
    categoryName: str,
    imagePath: str,
    repo: LibraryRepository,
    app_dir: Path | None = None,
) -> FileItem:
    fileitem = add_file_from_path(path=path, repo=repo)
    file_id = _require_id(fileitem.id, "file")
    category = get_or_create_category(categoryName=categoryName, repo=repo)
    category_id = _require_id(category.id, "category")
    fileitem = add_category_on_file(fileID=file_id, categoryID=category_id, repo=repo)
    file_id = _require_id(fileitem.id, "file")
    return add_image_to_file(imagePath=imagePath, repo=repo, fileID=file_id, app_dir=app_dir)


def add_url_with_category_and_image(
    url: str,
    name: str,
    categoryName: str,
    imagePath: str,
    repo: LibraryRepository,
    app_dir: Path | None = None,
) -> FileItem:
    fileitem = add_url_as_file(url=url, name=name, repo=repo, app_dir=app_dir)
    file_id = _require_id(fileitem.id, "file")
    category = get_or_create_category(categoryName=categoryName, repo=repo)
    category_id = _require_id(category.id, "category")
    fileitem = add_category_on_file(fileID=file_id, categoryID=category_id, repo=repo)
    file_id = _require_id(fileitem.id, "file")
    return add_image_to_file(imagePath=imagePath, repo=repo, fileID=file_id, app_dir=app_dir)


def add_category_to_files(fileIDs: list[int], categoryName: str, repo: LibraryRepository) -> list[FileItem]:
    category = get_or_create_category(categoryName=categoryName, repo=repo)
    category_id = _require_id(category.id, "category")
    files = []

    for fileID in fileIDs:
        files.append(add_category_on_file(fileID=fileID, categoryID=category_id, repo=repo))

    return files


def add_tag_to_file(fileID: int, tagID: int, repo: LibraryRepository) -> FileItem:
    return repo.add_tag_to_file_item(file_id=fileID, tag_id=tagID)


def add_category_on_file(fileID: int, categoryID: int | None, repo: LibraryRepository) -> FileItem:
    return repo.set_file_category(file_id=fileID, category_id=categoryID)


def remove_tag_from_file(fileID: int, tagID: int, repo: LibraryRepository) -> FileItem:
    return repo.remove_tag_from_file_item(file_id=fileID, tag_id=tagID)


def remove_category_from_file(fileID: int, repo: LibraryRepository) -> FileItem:
    return repo.remove_file_category(file_id=fileID)


def remove_file(fileID: int, repo: LibraryRepository) -> None:
    repo.delete_file_item(fileID)


def get_file_item(fileID: int, repo: LibraryRepository) -> FileItem:
    return repo.get_file_item(file_id=fileID)


def get_all_file_items(repo: LibraryRepository) -> list[FileItem]:
    return repo.get_all_file_items()


def create_tag(tagName: str, repo: LibraryRepository) -> Tag:
    tag = repo.create_tag(tag=Tag(name=tagName))
    return tag


def get_tag(tagID: int, repo: LibraryRepository) -> Tag:
    return repo.get_tag(tag_id=tagID)


def get_all_tags(repo: LibraryRepository) -> list[Tag]:
    return repo.get_all_tags()


def delete_tag(tagID: int, repo: LibraryRepository) -> None:
    repo.delete_tag(tag_id=tagID)


def create_category(categoryName: str, repo: LibraryRepository) -> Category:
    category = repo.create_category(category=Category(name=categoryName))
    return category


def get_category(categoryID: int, repo: LibraryRepository) -> Category:
    return repo.get_category(category_id=categoryID)


def get_all_categories(repo: LibraryRepository) -> list[Category]:
    return repo.get_all_categories()


def delete_category(categoryID: int, repo: LibraryRepository) -> None:
    repo.delete_category(category_id=categoryID)


def open_file(fileID: int, repo: LibraryRepository) -> None:
    file_item = get_file_item(fileID=fileID, repo=repo)
    file_path = Path(file_item.absolute_path)

    if not file_path.exists():
        raise FileNotFoundDomainError(f"File does not exist: {file_path}")

    try:
        if sys.platform.startswith("win"):
            os.startfile(file_path)
        elif sys.platform == "darwin":
            subprocess.Popen(["open", str(file_path)])
        else:
            subprocess.Popen(["xdg-open", str(file_path)])
    except OSError as error:
        raise FileExecutionError(f"Failed to open file {file_path}: {error}") from error

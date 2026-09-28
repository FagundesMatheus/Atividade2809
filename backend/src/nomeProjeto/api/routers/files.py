from pathlib import Path as FilePath
from typing import List

from fastapi import APIRouter, Body, Depends, HTTPException, Path, status
from pydantic import BaseModel, Field

from ...domain.file_item import FileItem
from ...application import services
from ...infrastructure.sqlite_repo import LibraryRepository
from ..file_source import FileSourceKind, resolve_file_source_kind
from ..dependencies import get_app_directory, get_repository

router = APIRouter()


class FileSourcePayload(BaseModel):
    source: str = Field(..., min_length=1)
    name: str | None = None


class FileSourceWithCategoryImagePayload(FileSourcePayload):
    category_name: str = Field(..., min_length=1)
    image_path: str = Field(..., min_length=1)


@router.get("/", response_model=List[FileItem])
def list_all_items(repo: LibraryRepository = Depends(get_repository)) -> List[FileItem]:
    return services.get_all_file_items(repo=repo)


@router.get("/{file_id}", response_model=FileItem)
def get_file(file_id: int = Path(...), repo: LibraryRepository = Depends(get_repository)) -> FileItem:
    return services.get_file_item(fileID=file_id, repo=repo)


@router.post("/", response_model=FileItem)
def add_file(
    payload: FileSourcePayload = Body(...),
    repo: LibraryRepository = Depends(get_repository),
    app_dir: FilePath = Depends(get_app_directory),
) -> FileItem:
    try:
        source_kind = resolve_file_source_kind(payload.source)
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error)) from error

    if source_kind is FileSourceKind.URL:
        if payload.name is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="name is required when source is a URL",
            )

        return services.add_url_as_file(url=payload.source, name=payload.name, repo=repo, app_dir=app_dir)

    return services.add_file_from_path(path=payload.source, repo=repo)


@router.post("/category-image", response_model=FileItem)
def add_file_with_category_and_image(
    payload: FileSourceWithCategoryImagePayload = Body(...),
    repo: LibraryRepository = Depends(get_repository),
    app_dir: FilePath = Depends(get_app_directory),
) -> FileItem:
    try:
        source_kind = resolve_file_source_kind(payload.source)
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error)) from error

    if source_kind is FileSourceKind.URL:
        if payload.name is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="name is required when source is a URL",
            )

        return services.add_url_with_category_and_image(
            url=payload.source,
            name=payload.name,
            categoryName=payload.category_name,
            imagePath=payload.image_path,
            repo=repo,
            app_dir=app_dir,
        )

    return services.add_file_with_category_and_image(
        path=payload.source,
        categoryName=payload.category_name,
        imagePath=payload.image_path,
        repo=repo,
        app_dir=app_dir,
    )


@router.post("/folder", response_model=List[FileItem])
def add_files_from_folder(
    path: str = Body(..., embed=True),
    repo: LibraryRepository = Depends(get_repository),
) -> List[FileItem]:
    return services.add_files_from_folder(path=path, repo=repo)


@router.put("/{file_id}/image", response_model=FileItem)
def add_image_to_file(
    imagePath: str = Body(..., embed=True),
    file_id: int = Path(...),
    app_dir: FilePath = Depends(get_app_directory),
    repo: LibraryRepository = Depends(get_repository),
) -> FileItem:
    return services.add_image_to_file(imagePath=imagePath, repo=repo, fileID=file_id, app_dir=app_dir)


@router.post("/open/{file_id}", status_code=204)
def open_file(file_id: int = Path(...), repo: LibraryRepository = Depends(get_repository)) -> None:
    services.open_file(fileID=file_id, repo=repo)


@router.delete("/{file_id}", status_code=204)
def remove_file(file_id: int = Path(...), repo: LibraryRepository = Depends(get_repository)) -> None:
    services.remove_file(fileID=file_id, repo=repo)


@router.post("/{file_id}/tags/{tag_id}", response_model=FileItem)
def add_tag_to_file(
    file_id: int = Path(...),
    tag_id: int = Path(...),
    repo: LibraryRepository = Depends(get_repository),
) -> FileItem:
    return services.add_tag_to_file(fileID=file_id, tagID=tag_id, repo=repo)


@router.delete("/{file_id}/tags/{tag_id}", response_model=FileItem)
def remove_tag_from_file(
    file_id: int = Path(...),
    tag_id: int = Path(...),
    repo: LibraryRepository = Depends(get_repository),
) -> FileItem:
    return services.remove_tag_from_file(fileID=file_id, tagID=tag_id, repo=repo)


@router.put("/{file_id}/category", response_model=FileItem)
def add_category_to_file(
    category_id: int | None = Body(..., embed=True),
    file_id: int = Path(...),
    repo: LibraryRepository = Depends(get_repository),
) -> FileItem:
    return services.add_category_on_file(fileID=file_id, categoryID=category_id, repo=repo)


@router.put("/category", response_model=List[FileItem])
def add_category_to_files(
    item_ids: List[int] = Body(..., embed=True),
    category_name: str = Body(..., embed=True),
    repo: LibraryRepository = Depends(get_repository),
) -> List[FileItem]:
    return services.add_category_to_files(fileIDs=item_ids, categoryName=category_name, repo=repo)


@router.delete("/{file_id}/category", response_model=FileItem)
def remove_category_from_file(file_id: int = Path(...), repo: LibraryRepository = Depends(get_repository)) -> FileItem:
    return services.remove_category_from_file(fileID=file_id, repo=repo)

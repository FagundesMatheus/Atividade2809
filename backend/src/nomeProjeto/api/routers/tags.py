from fastapi import APIRouter, Body, Depends, Path
from typing import List
from ...domain.tag import Tag
from ...application import services
from ...infrastructure.sqlite_repo import LibraryRepository
from ..dependencies import get_repository

router = APIRouter()


@router.get("/", response_model=List[Tag])
def list_all_tags(repo: LibraryRepository = Depends(get_repository)) -> List[Tag]:
    return services.get_all_tags(repo=repo)


@router.get("/{tag_id}", response_model=Tag)
def get_tag(tag_id: int = Path(...), repo: LibraryRepository = Depends(get_repository)) -> Tag:
    return services.get_tag(tagID=tag_id, repo=repo)


@router.post("/", response_model=Tag)
def create_tag(name: str = Body(..., embed=True), repo: LibraryRepository = Depends(get_repository)) -> Tag:
    return services.create_tag(tagName=name, repo=repo)


@router.delete("/{tag_id}", status_code=204)
def delete_tag(tag_id: int = Path(...), repo: LibraryRepository = Depends(get_repository)) -> None:
    services.delete_tag(tagID=tag_id, repo=repo)

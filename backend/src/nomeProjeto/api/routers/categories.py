from fastapi import APIRouter, Body, Depends, Path
from typing import List
from ...domain.category import Category
from ...application import services
from ...infrastructure.sqlite_repo import LibraryRepository
from ..dependencies import get_repository

router = APIRouter()


@router.get("/", response_model=List[Category])
def list_all_categories(
    repo: LibraryRepository = Depends(get_repository),
) -> List[Category]:
    return services.get_all_categories(repo=repo)


@router.get("/{category_id}", response_model=Category)
def get_category(category_id: int = Path(...), repo: LibraryRepository = Depends(get_repository)) -> Category:
    return services.get_category(categoryID=category_id, repo=repo)


@router.post("/", response_model=Category)
def create_category(name: str = Body(..., embed=True), repo: LibraryRepository = Depends(get_repository)) -> Category:
    return services.create_category(categoryName=name, repo=repo)


@router.delete("/{category_id}", status_code=204)
def delete_category(category_id: int = Path(...), repo: LibraryRepository = Depends(get_repository)) -> None:
    services.delete_category(categoryID=category_id, repo=repo)

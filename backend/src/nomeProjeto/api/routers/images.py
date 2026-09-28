from fastapi import APIRouter, HTTPException, Path as FastApiPath
from fastapi.responses import FileResponse

from nomeProjeto.infrastructure.file_manager import LocalFileManager

router = APIRouter()

APP_DIR = LocalFileManager.ensure_app_directory()
IMAGE_DIRECTORY = APP_DIR / "images"


@router.get("/{image_name}", response_class=FileResponse)
def get_image(image_name: str = FastApiPath(...)) -> FileResponse:
    target_path = (IMAGE_DIRECTORY / image_name).resolve()

    base_path = IMAGE_DIRECTORY.resolve()

    if not str(target_path).startswith(str(base_path)):
        raise HTTPException(status_code=403, detail="Forbidden")

    if not target_path.is_file():
        raise HTTPException(status_code=404, detail="Image not found")

    return FileResponse(target_path)

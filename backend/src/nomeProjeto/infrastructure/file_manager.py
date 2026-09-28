import shutil
from pathlib import Path

from nomeProjeto.domain.exceptions import FileNotFoundDomainError, FileExecutionError


class LocalFileManager:
    @staticmethod
    def ensure_app_directory(base_dir: Path | None = None) -> Path:
        app_dir = base_dir if base_dir is not None else Path.home() / ".nomeProjeto"
        app_dir.mkdir(parents=True, exist_ok=True)

        images_dir = app_dir / "images"
        images_dir.mkdir(parents=True, exist_ok=True)

        urls_dir = app_dir / "urls"
        urls_dir.mkdir(parents=True, exist_ok=True)

        return app_dir

    @staticmethod
    def get_urls_directory(base_dir: Path | None = None) -> Path:
        return LocalFileManager.ensure_app_directory(base_dir=base_dir) / "urls"

    @staticmethod
    def get_images_directory(base_dir: Path | None = None) -> Path:
        return LocalFileManager.ensure_app_directory(base_dir=base_dir) / "images"

    @staticmethod
    def move_file(source: Path, destination: Path, create_copy: bool) -> Path:
        if not source.exists():
            raise FileNotFoundDomainError(f"Source file does not exist: {source}")

        if not source.is_file():
            raise ValueError(f"Source path must be a file, not a directory: {source}")

        try:
            destination.mkdir(parents=True, exist_ok=True)

            destination_file = destination / source.name

            if destination_file.exists():
                raise FileExecutionError(
                    f"Destination file already exists and overwrite is prevented: {destination_file}"
                )

            if create_copy:
                shutil.copy2(source, destination_file)
            else:
                source.replace(destination_file)

        except OSError as e:
            raise FileExecutionError(f"Failed to process file from {source} to {destination_file}: {e}") from e
        return destination_file

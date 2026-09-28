from enum import Enum
from pathlib import Path
from urllib.parse import urlparse


class FileSourceKind(str, Enum):
    URL = "url"
    PATH = "path"


def _is_http_url(value: str) -> bool:
    parsed_url = urlparse(value)
    return parsed_url.scheme in {"http", "https"} and bool(parsed_url.netloc)


def resolve_file_source_kind(source: str) -> FileSourceKind:
    normalized_source = source.strip()

    if not normalized_source:
        raise ValueError("source is required")

    if _is_http_url(normalized_source):
        return FileSourceKind.URL

    candidate_path = Path(normalized_source).expanduser()
    if candidate_path.exists() and candidate_path.is_file():
        return FileSourceKind.PATH

    raise ValueError("source must be a valid URL or an existing file path")

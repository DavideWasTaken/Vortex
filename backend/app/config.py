from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    env: str
    is_production: bool
    root_dir: Path
    data_dir: Path
    upload_dir: Path
    preview_dir: Path
    qdrant_path: Path
    sqlite_path: Path
    qdrant_url: str | None
    bootstrap_demo_users: bool
    bootstrap_admin_username: str | None
    bootstrap_admin_password: str | None
    bootstrap_admin_language: str
    session_cookie_name: str
    session_cookie_secure: bool
    session_cookie_samesite: str
    session_max_age_seconds: int
    login_rate_limit_window_seconds: int
    login_rate_limit_max_attempts: int
    login_rate_limit_lock_seconds: int
    max_upload_files: int
    max_upload_size_bytes: int
    allowed_upload_extensions: tuple[str, ...]
    allowed_upload_mime_types: tuple[str, ...]
    text_model: str
    clip_text_model: str
    clip_image_model: str
    max_pdf_pages_rendered: int


DEFAULT_UPLOAD_EXTENSIONS = (
    ".pdf",
    ".docx",
    ".txt",
    ".md",
    ".markdown",
    ".csv",
    ".log",
    ".png",
    ".jpg",
    ".jpeg",
    ".webp",
    ".tif",
    ".tiff",
    ".bmp",
    ".dxf",
    ".dwg",
)

DEFAULT_UPLOAD_MIME_TYPES = (
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "text/plain",
    "text/markdown",
    "text/csv",
    "image/png",
    "image/jpeg",
    "image/webp",
    "image/tiff",
    "image/bmp",
    "image/vnd.dwg",
    "image/vnd.dxf",
    "application/acad",
    "application/x-acad",
    "application/autocad_dwg",
    "application/dwg",
    "application/x-dwg",
    "drawing/dwg",
    "application/dxf",
    "application/x-dxf",
    "drawing/x-dxf",
)


def get_settings() -> Settings:
    env = os.getenv("VORTEX_ENV", "development").strip().lower() or "development"
    is_production = env == "production"
    root_dir = Path(__file__).resolve().parent
    data_dir = Path(os.getenv("VORTEX_DATA_DIR", root_dir.parent.parent / "data")).resolve()
    bootstrap_admin_password = _env_str("VORTEX_BOOTSTRAP_ADMIN_PASSWORD")
    if is_production and _is_unsafe_bootstrap_password(bootstrap_admin_password):
        bootstrap_admin_password = None

    return Settings(
        env=env,
        is_production=is_production,
        root_dir=root_dir,
        data_dir=data_dir,
        upload_dir=data_dir / "uploads",
        preview_dir=data_dir / "previews",
        qdrant_path=data_dir / "qdrant",
        sqlite_path=data_dir / "vortex.sqlite3",
        qdrant_url=os.getenv("QDRANT_URL"),
        bootstrap_demo_users=_env_bool("VORTEX_BOOTSTRAP_DEMO_USERS", not is_production),
        bootstrap_admin_username=_env_str("VORTEX_BOOTSTRAP_ADMIN_USERNAME"),
        bootstrap_admin_password=bootstrap_admin_password,
        bootstrap_admin_language=_env_choice("VORTEX_BOOTSTRAP_ADMIN_LANGUAGE", "it", {"it", "en"}),
        session_cookie_name=os.getenv("VORTEX_SESSION_COOKIE_NAME", "vortex_session"),
        session_cookie_secure=_env_bool("VORTEX_SESSION_COOKIE_SECURE", is_production),
        session_cookie_samesite=_env_choice(
            "VORTEX_SESSION_COOKIE_SAMESITE",
            "lax",
            {"lax", "strict", "none"},
        ),
        session_max_age_seconds=_env_int("VORTEX_SESSION_MAX_AGE_SECONDS", 60 * 60 * 8, minimum=300),
        login_rate_limit_window_seconds=_env_int("VORTEX_LOGIN_RATE_WINDOW_SECONDS", 15 * 60, minimum=60),
        login_rate_limit_max_attempts=_env_int("VORTEX_LOGIN_RATE_MAX_ATTEMPTS", 8, minimum=0),
        login_rate_limit_lock_seconds=_env_int("VORTEX_LOGIN_RATE_LOCK_SECONDS", 15 * 60, minimum=60),
        max_upload_files=_env_int("VORTEX_MAX_UPLOAD_FILES", 20, minimum=1),
        max_upload_size_bytes=_env_int("VORTEX_MAX_UPLOAD_SIZE_BYTES", 100 * 1024 * 1024, minimum=1024),
        allowed_upload_extensions=_env_tuple("VORTEX_ALLOWED_UPLOAD_EXTENSIONS", DEFAULT_UPLOAD_EXTENSIONS),
        allowed_upload_mime_types=_env_tuple("VORTEX_ALLOWED_UPLOAD_MIME_TYPES", DEFAULT_UPLOAD_MIME_TYPES),
        text_model=os.getenv(
            "VORTEX_TEXT_MODEL",
            "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
        ),
        clip_text_model=os.getenv("VORTEX_CLIP_TEXT_MODEL", "Qdrant/clip-ViT-B-32-text"),
        clip_image_model=os.getenv("VORTEX_CLIP_IMAGE_MODEL", "Qdrant/clip-ViT-B-32-vision"),
        max_pdf_pages_rendered=int(os.getenv("VORTEX_MAX_PDF_PAGES_RENDERED", "40")),
    )


def ensure_data_dirs(settings: Settings) -> None:
    settings.data_dir.mkdir(parents=True, exist_ok=True)
    settings.upload_dir.mkdir(parents=True, exist_ok=True)
    settings.preview_dir.mkdir(parents=True, exist_ok=True)
    settings.qdrant_path.mkdir(parents=True, exist_ok=True)


def _env_str(name: str) -> str | None:
    value = os.getenv(name)
    if value is None:
        return None
    value = value.strip()
    return value or None


def _env_bool(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _env_int(name: str, default: int, *, minimum: int) -> int:
    value = os.getenv(name)
    if value is None or not value.strip():
        return default
    try:
        parsed = int(value)
    except ValueError:
        return default
    return max(parsed, minimum)


def _env_choice(name: str, default: str, choices: set[str]) -> str:
    value = os.getenv(name, default).strip().lower()
    return value if value in choices else default


def _env_tuple(name: str, default: tuple[str, ...]) -> tuple[str, ...]:
    value = os.getenv(name)
    if value is None or not value.strip():
        return default
    return tuple(item.strip().lower() for item in value.split(",") if item.strip())


def _is_unsafe_bootstrap_password(value: str | None) -> bool:
    if value is None:
        return True
    weak_values = {
        "admin",
        "password",
        "changeme",
        "change-me",
        "change-me-with-a-long-random-password",
    }
    return len(value) < 12 or value.strip().lower() in weak_values

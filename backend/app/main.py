from __future__ import annotations

import atexit
import re
import secrets
import shutil
from contextlib import asynccontextmanager
from pathlib import Path
from time import monotonic
from uuid import uuid4

from fastapi import BackgroundTasks, Depends, FastAPI, File, Form, HTTPException, Request, Response, UploadFile
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from .config import ensure_data_dirs, get_settings
from .db import Database, verify_password
from .extraction import copy_upload, detect_content_type, validate_stored_upload
from .indexer import ProjectIndexer
from .search import VectorSearch, group_hits_by_project


settings = get_settings()
ensure_data_dirs(settings)
database = Database(
    settings.sqlite_path,
    bootstrap_demo_users=settings.bootstrap_demo_users,
    bootstrap_admin_username=settings.bootstrap_admin_username,
    bootstrap_admin_password=settings.bootstrap_admin_password,
    bootstrap_admin_language=settings.bootstrap_admin_language,
)
if settings.is_production and database.count_users() == 0:
    raise RuntimeError(
        "Production requires an initial admin. Set VORTEX_BOOTSTRAP_ADMIN_USERNAME "
        "and a non-placeholder VORTEX_BOOTSTRAP_ADMIN_PASSWORD of at least 12 characters "
        "for the first startup."
    )
if settings.is_production:
    for demo_username, demo_password in (("admin", "admin"), ("user", "user")):
        demo_user = database.get_user_by_username(demo_username)
        if demo_user and verify_password(demo_password, demo_user["password_hash"]):
            raise RuntimeError(
                f"Production cannot start with demo credentials for '{demo_username}'. "
                "Change or remove the demo account before exposing the service."
            )
vector_search = VectorSearch(settings)
indexer = ProjectIndexer(settings, database, vector_search)
atexit.register(vector_search.close)
SESSION_COOKIE = settings.session_cookie_name
login_attempts: dict[str, dict[str, float]] = {}


@asynccontextmanager
async def lifespan(_: FastAPI):
    yield
    vector_search.close()


app = FastAPI(title="Vortex", version="0.1.0", lifespan=lifespan)


class LoginRequest(BaseModel):
    username: str = Field(min_length=1, max_length=80)
    password: str = Field(min_length=1, max_length=160)


class SearchRequest(BaseModel):
    query: str = Field(min_length=2)
    limit: int = Field(default=8, ge=1, le=30)
    mode: str = Field(default="all", pattern="^(all|text|visual)$")


class ProjectUpdateRequest(BaseModel):
    title: str | None = Field(default=None, max_length=160)
    description: str | None = Field(default=None, max_length=2000)


class UserCreateRequest(BaseModel):
    username: str = Field(min_length=2, max_length=80, pattern=r"^[a-zA-Z0-9_.-]+$")
    password: str = Field(min_length=3, max_length=160)
    role: str = Field(pattern="^(admin|user)$")
    language: str = Field(default="it", pattern="^(it|en)$")


class UserUpdateRequest(BaseModel):
    role: str | None = Field(default=None, pattern="^(admin|user)$")
    active: bool | None = None
    password: str | None = Field(default=None, min_length=3, max_length=160)
    language: str | None = Field(default=None, pattern="^(it|en)$")


class MeUpdateRequest(BaseModel):
    language: str = Field(pattern="^(it|en)$")


def public_user(user: dict) -> dict:
    return {
        "id": user["id"],
        "username": user["username"],
        "role": user["role"],
        "active": bool(user["active"]),
        "language": user.get("language") or "it",
        "created_at": user["created_at"],
        "updated_at": user["updated_at"],
    }


def require_user(request: Request) -> dict:
    token = request.cookies.get(SESSION_COOKIE)
    user_id = database.get_session_user_id(token or "") if token else None
    if not user_id:
        raise HTTPException(status_code=401, detail="Authentication required")
    try:
        user = database.get_user(user_id)
    except KeyError as exc:
        raise HTTPException(status_code=401, detail="Authentication required") from exc
    if not user["active"]:
        if token:
            database.delete_session(token)
        raise HTTPException(status_code=403, detail="Account disabled")
    return user


def require_admin(user: dict = Depends(require_user)) -> dict:
    if user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin role required")
    return user


def ensure_admin_remains(user_id: str, update: UserUpdateRequest) -> None:
    try:
        target = database.get_user(user_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="User not found") from exc

    would_remove_admin = target["role"] == "admin" and (
        update.active is False or update.role == "user"
    )
    if not would_remove_admin:
        return

    active_admins = [
        user for user in database.list_users() if user["role"] == "admin" and bool(user["active"])
    ]
    if len(active_admins) <= 1:
        raise HTTPException(status_code=400, detail="At least one active admin is required")


def login_rate_key(request: Request, username: str) -> str:
    client_host = request.client.host if request.client else "unknown"
    return f"{client_host}:{username.strip().lower()}"


def ensure_login_allowed(key: str) -> None:
    if settings.login_rate_limit_max_attempts <= 0:
        return
    state = login_attempts.get(key)
    if not state:
        return
    now = monotonic()
    locked_until = state.get("locked_until", 0)
    if locked_until > now:
        raise HTTPException(status_code=429, detail="Too many failed login attempts")
    if now - state.get("window_started", now) > settings.login_rate_limit_window_seconds:
        login_attempts.pop(key, None)


def record_login_failure(key: str) -> None:
    if settings.login_rate_limit_max_attempts <= 0:
        return
    now = monotonic()
    state = login_attempts.get(key)
    if not state or now - state.get("window_started", now) > settings.login_rate_limit_window_seconds:
        state = {"failures": 0, "window_started": now, "locked_until": 0}
    state["failures"] += 1
    if state["failures"] >= settings.login_rate_limit_max_attempts:
        state["locked_until"] = now + settings.login_rate_limit_lock_seconds
    login_attempts[key] = state


def clear_login_failures(key: str) -> None:
    login_attempts.pop(key, None)


def sanitize_upload_filename(filename: str, fallback: str) -> str:
    safe_name = Path(filename or fallback).name.replace("\x00", "").strip()
    safe_name = re.sub(r"[^A-Za-z0-9._ -]+", "_", safe_name)
    safe_name = re.sub(r"\s+", " ", safe_name).strip(" .")
    return (safe_name or fallback)[:180]


def validate_upload_batch(files: list[UploadFile]) -> None:
    if len(files) > settings.max_upload_files:
        raise HTTPException(
            status_code=413,
            detail=f"Too many files. Maximum is {settings.max_upload_files}.",
        )
    for upload in files:
        validate_upload_metadata(upload)


def validate_upload_metadata(upload: UploadFile) -> None:
    filename = Path(upload.filename or "").name
    extension = Path(filename).suffix.lower()
    if extension not in settings.allowed_upload_extensions:
        raise HTTPException(status_code=400, detail=f"Unsupported file extension: {extension or 'none'}")

    content_type = (upload.content_type or "").split(";", 1)[0].strip().lower()
    if (
        settings.allowed_upload_mime_types
        and content_type
        and content_type != "application/octet-stream"
        and content_type not in settings.allowed_upload_mime_types
    ):
        raise HTTPException(status_code=400, detail=f"Unsupported file type: {content_type}")


def ensure_path_inside(path: str | Path, root: Path) -> Path:
    resolved_path = Path(path).resolve()
    resolved_root = root.resolve()
    try:
        resolved_path.relative_to(resolved_root)
    except ValueError as exc:
        raise HTTPException(status_code=403, detail="File path is outside storage") from exc
    return resolved_path


def save_project_uploads(project_id: str, files: list[UploadFile]) -> list[dict]:
    validate_upload_batch(files)
    project_dir = settings.upload_dir / project_id
    project_dir.mkdir(parents=True, exist_ok=True)
    assets = []
    copied_paths: list[Path] = []

    try:
        for upload in files:
            asset_id = str(uuid4())
            safe_filename = sanitize_upload_filename(upload.filename or "", f"{asset_id}.bin")
            destination = project_dir / f"{asset_id}-{safe_filename}"
            try:
                copy_upload(upload.file, destination, settings.max_upload_size_bytes)
            except ValueError as exc:
                destination.unlink(missing_ok=True)
                raise HTTPException(status_code=413, detail=f"File too large: {safe_filename}") from exc
            try:
                validate_stored_upload(destination)
            except Exception as exc:
                destination.unlink(missing_ok=True)
                raise HTTPException(status_code=400, detail=f"Invalid or corrupted file: {safe_filename}") from exc
            copied_paths.append(destination)
            assets.append(
                database.add_asset(
                    asset_id=asset_id,
                    project_id=project_id,
                    filename=safe_filename,
                    content_type=normalized_content_type(upload.content_type, destination),
                    stored_path=str(destination),
                )
            )
    except HTTPException:
        for asset in assets:
            try:
                database.delete_asset(asset["id"])
            except KeyError:
                pass
        for path in copied_paths:
            path.unlink(missing_ok=True)
        raise
    return assets


def normalized_content_type(content_type: str | None, path: Path) -> str:
    normalized = (content_type or "").split(";", 1)[0].strip().lower()
    if not normalized or normalized == "application/octet-stream":
        return detect_content_type(path)
    return normalized


def delete_project_files(project_id: str) -> None:
    shutil.rmtree(settings.upload_dir / project_id, ignore_errors=True)
    shutil.rmtree(settings.preview_dir / project_id, ignore_errors=True)


def search_terms(query: str) -> list[str]:
    query = query.lower()
    terms = [term for term in re.findall(r"[a-z0-9]+", query) if len(term) > 2]
    code_terms = [
        re.sub(r"[^a-z0-9]+", "", term)
        for term in re.findall(r"[a-z]+[\s_-]*\d+[a-z0-9]*|\d+[\s_-]*[a-z]+[a-z0-9]*", query)
    ]
    for term in code_terms:
        if term and term not in terms:
            terms.append(term)
    return terms


def lexical_score(
    query: str,
    project: dict,
    evidence: list[dict],
    assets: list[dict] | None = None,
) -> float:
    terms = search_terms(query)
    if not terms:
        return 0.0

    title = str(project.get("title") or "").lower()
    description = str(project.get("description") or "").lower()
    snippets = "\n".join(str(item.get("snippet") or "") for item in evidence).lower()
    evidence_filenames = "\n".join(str(item.get("filename") or "") for item in evidence)
    asset_text = "\n".join(
        "\n".join(
            [
                str(asset.get("filename") or ""),
                str(asset.get("visual_caption") or ""),
                str(asset.get("visual_tags") or ""),
            ]
        )
        for asset in (assets or [])
    )
    filenames = f"{evidence_filenames}\n{asset_text}".lower()

    title_tokens = text_tokens(title)
    description_tokens = text_tokens(description)
    filename_tokens = text_tokens(filenames)
    snippet_tokens = text_tokens(snippets)
    compact_context = compact_text(f"{title}\n{description}\n{filenames}\n{snippets}")

    score = 0.0
    normalized_query = " ".join(terms)
    if normalized_query and normalized_query in title:
        score += 2.2

    for term in terms:
        if token_match(term, title_tokens):
            score += 1.4
        if token_match(term, description_tokens):
            score += 0.45
        if token_match(term, filename_tokens):
            score += 0.55
        if token_match(term, snippet_tokens):
            score += 0.18
        if any(char.isdigit() for char in term) and term in compact_context:
            score += 2.4

    return score


def text_tokens(value: str) -> set[str]:
    return set(re.findall(r"[a-z0-9]+", value.lower()))


def compact_text(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", value.lower())


def token_match(term: str, tokens: set[str]) -> bool:
    if term in tokens:
        return True
    if len(term) < 5:
        return False
    stem = term[:-1]
    return any(token.startswith(stem) for token in tokens if len(token) >= 5)


def evidence_with_preview_flags(entries: list[dict]) -> list[dict]:
    evidence = []
    for entry in entries:
        preview_available = False
        asset_id = entry.get("asset_id")
        if asset_id:
            try:
                asset = database.get_asset(asset_id)
                preview_path = asset.get("preview_path")
                preview_available = bool(preview_path and Path(preview_path).exists())
            except KeyError:
                preview_available = False
        evidence.append({**entry, "preview_available": preview_available})
    return evidence


def ensure_visual_evidence(project_id: str, evidence: list[dict]) -> list[dict]:
    if any(item.get("kind") == "visual" for item in evidence):
        return evidence

    for asset in database.list_assets_for_project(project_id):
        preview_path = asset.get("preview_path")
        if not preview_path or not Path(preview_path).exists():
            continue
        visual_caption = asset.get("visual_caption") or f"Anteprima visuale: {asset['filename']}"
        visual_tags = [
            tag.strip()
            for tag in str(asset.get("visual_tags") or "").split(",")
            if tag.strip()
        ]
        visual_entry = {
            "kind": "visual",
            "asset_id": asset["id"],
            "filename": asset["filename"],
            "page": None,
            "section": asset["filename"],
            "snippet": (
                f"{visual_caption} Tag: {', '.join(visual_tags)}."
                if visual_tags
                else visual_caption
            ),
            "visual_caption": visual_caption,
            "visual_tags": visual_tags,
            "preview_url": f"/api/assets/{asset['id']}/preview",
            "download_url": f"/api/assets/{asset['id']}/download",
            "preview_available": True,
        }
        if len(evidence) >= 4:
            return [*evidence[:3], visual_entry]
        return [*evidence, visual_entry]
    return evidence


@app.get("/api/health")
def health() -> dict[str, str]:
    database.health_check()
    return {"status": "ok", "environment": settings.env}


@app.get("/api/health/ready")
def readiness() -> dict[str, str]:
    database.health_check()
    vector_search.health_check()
    return {"status": "ok"}


@app.post("/api/auth/login")
def login(payload: LoginRequest, request: Request, response: Response) -> dict:
    rate_key = login_rate_key(request, payload.username)
    ensure_login_allowed(rate_key)
    user = database.get_user_by_username(payload.username)
    if not user or not user["active"] or not verify_password(payload.password, user["password_hash"]):
        record_login_failure(rate_key)
        raise HTTPException(status_code=401, detail="Invalid credentials")

    clear_login_failures(rate_key)
    database.delete_expired_sessions()
    token = secrets.token_urlsafe(32)
    database.create_session(token, user["id"], settings.session_max_age_seconds)
    response.set_cookie(
        SESSION_COOKIE,
        token,
        max_age=settings.session_max_age_seconds,
        httponly=True,
        secure=settings.session_cookie_secure,
        samesite=settings.session_cookie_samesite,
    )
    return {"user": public_user(user)}


@app.post("/api/auth/logout")
def logout(request: Request, response: Response) -> dict[str, str]:
    token = request.cookies.get(SESSION_COOKIE)
    if token:
        database.delete_session(token)
    response.delete_cookie(
        SESSION_COOKIE,
        secure=settings.session_cookie_secure,
        httponly=True,
        samesite=settings.session_cookie_samesite,
    )
    return {"status": "ok"}


@app.get("/api/auth/me")
def me(user: dict = Depends(require_user)) -> dict:
    return {"user": public_user(user)}


@app.patch("/api/auth/me")
def update_me(payload: MeUpdateRequest, user: dict = Depends(require_user)) -> dict:
    updated_user = database.update_user(user["id"], language=payload.language)
    return {"user": public_user(updated_user)}


@app.get("/api/users")
def list_users(_: dict = Depends(require_admin)) -> dict[str, list[dict]]:
    return {"users": [public_user(user) for user in database.list_users()]}


@app.post("/api/users")
def create_user(payload: UserCreateRequest, _: dict = Depends(require_admin)) -> dict:
    if database.get_user_by_username(payload.username):
        raise HTTPException(status_code=409, detail="Username already exists")
    user = database.create_user(payload.username, payload.password, payload.role, payload.language)
    return {"user": public_user(user)}


@app.patch("/api/users/{user_id}")
def update_user(
    user_id: str,
    payload: UserUpdateRequest,
    _: dict = Depends(require_admin),
) -> dict:
    ensure_admin_remains(user_id, payload)
    try:
        user = database.update_user(
            user_id,
            role=payload.role,
            active=payload.active,
            password=payload.password,
            language=payload.language,
        )
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="User not found") from exc
    if payload.active is False:
        database.delete_sessions_for_user(user_id)
    return {"user": public_user(user)}


@app.delete("/api/users/{user_id}")
def delete_user(user_id: str, current: dict = Depends(require_admin)) -> dict[str, str]:
    if user_id == current["id"]:
        raise HTTPException(status_code=400, detail="You cannot delete your own account")
    try:
        target = database.get_user(user_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="User not found") from exc
    if target["role"] == "admin" and bool(target["active"]):
        active_admins = [
            user for user in database.list_users() if user["role"] == "admin" and bool(user["active"])
        ]
        if len(active_admins) <= 1:
            raise HTTPException(status_code=400, detail="At least one active admin is required")
    database.delete_sessions_for_user(user_id)
    database.delete_user(user_id)
    return {"status": "ok"}


@app.get("/api/projects")
def list_projects(_: dict = Depends(require_user)) -> dict[str, list[dict]]:
    return {"projects": database.list_projects()}


@app.get("/api/projects/{project_id}")
def get_project(project_id: str, _: dict = Depends(require_user)) -> dict:
    try:
        project = database.get_project(project_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Project not found") from exc
    project["assets"] = database.list_assets_for_project(project_id)
    return project


@app.patch("/api/projects/{project_id}")
def update_project(
    project_id: str,
    payload: ProjectUpdateRequest,
    _: dict = Depends(require_admin),
) -> dict:
    try:
        database.get_project(project_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Project not found") from exc

    updates: dict[str, str] = {}
    if payload.title is not None:
        title = payload.title.strip()
        if not title:
            raise HTTPException(status_code=400, detail="Project name is required")
        updates["title"] = title
    if payload.description is not None:
        updates["description"] = payload.description.strip()

    database.update_project(project_id, **updates)
    project = database.get_project(project_id)
    project["assets"] = database.list_assets_for_project(project_id)
    return project


@app.post("/api/projects")
async def create_project(
    background_tasks: BackgroundTasks,
    _: dict = Depends(require_admin),
    title: str = Form(...),
    description: str = Form(""),
    files: list[UploadFile] = File(...),
) -> dict:
    if not files:
        raise HTTPException(status_code=400, detail="At least one file is required")

    project_id = str(uuid4())
    database.create_project(project_id, title.strip() or "Untitled", description.strip())
    try:
        save_project_uploads(project_id, files)
    except HTTPException:
        try:
            database.delete_project(project_id)
        except KeyError:
            pass
        delete_project_files(project_id)
        raise
    background_tasks.add_task(indexer.index_project, project_id)
    project = database.get_project(project_id)
    project["assets"] = database.list_assets_for_project(project_id)
    return project


@app.post("/api/projects/{project_id}/assets")
async def add_project_assets(
    background_tasks: BackgroundTasks,
    project_id: str,
    _: dict = Depends(require_admin),
    files: list[UploadFile] = File(...),
) -> dict:
    if not files:
        raise HTTPException(status_code=400, detail="At least one file is required")

    try:
        database.get_project(project_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Project not found") from exc

    new_assets = save_project_uploads(project_id, files)
    database.update_project(project_id, status="queued", error=None)
    background_tasks.add_task(
        indexer.index_assets,
        project_id,
        [asset["id"] for asset in new_assets],
    )
    project = database.get_project(project_id)
    project["assets"] = database.list_assets_for_project(project_id)
    return project


@app.post("/api/projects/{project_id}/reindex")
async def reindex_project(
    background_tasks: BackgroundTasks,
    project_id: str,
    _: dict = Depends(require_admin),
) -> dict:
    try:
        database.get_project(project_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Project not found") from exc

    database.update_project(project_id, status="queued", error=None)
    background_tasks.add_task(indexer.reindex_project, project_id)
    project = database.get_project(project_id)
    project["assets"] = database.list_assets_for_project(project_id)
    return project


@app.delete("/api/projects/{project_id}")
def delete_project(project_id: str, _: dict = Depends(require_admin)) -> dict[str, str]:
    try:
        database.get_project(project_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Project not found") from exc

    vector_search.delete_project(project_id)
    database.delete_project(project_id)
    delete_project_files(project_id)
    return {"status": "ok"}


@app.post("/api/search")
def search(request: SearchRequest, _: dict = Depends(require_user)) -> dict:
    hits = vector_search.search(request.query, request.limit, request.mode)
    grouped = group_hits_by_project(hits, max(request.limit * 4, request.limit))

    results_by_id = {}
    for item in grouped:
        try:
            project = database.get_project(item["project_id"])
        except KeyError:
            continue
        assets = database.list_assets_for_project(project["id"])
        evidence = ensure_visual_evidence(
            project["id"],
            evidence_with_preview_flags(item.get("evidence", [])),
        )
        score = float(item.get("score") or 0.0) + lexical_score(request.query, project, evidence, assets)
        results_by_id[project["id"]] = {
            **item,
            "score": score,
            "evidence": evidence,
            "title": project["title"],
            "description": project["description"],
            "status": project["status"],
        }

    for project in database.list_projects():
        if project["id"] in results_by_id:
            continue
        assets = database.list_assets_for_project(project["id"])
        score = lexical_score(request.query, project, [], assets)
        if score <= 0:
            continue
        results_by_id[project["id"]] = {
            "project_id": project["id"],
            "score": score,
            "evidence": [],
            "title": project["title"],
            "description": project["description"],
            "status": project["status"],
        }

    results = sorted(results_by_id.values(), key=lambda item: item["score"], reverse=True)
    return {"query": request.query, "results": results[: request.limit]}


@app.get("/api/assets/{asset_id}/preview")
def preview_asset(asset_id: str, _: dict = Depends(require_user)) -> FileResponse:
    try:
        asset = database.get_asset(asset_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Asset not found") from exc

    preview_path = asset.get("preview_path")
    if not preview_path or not Path(preview_path).exists():
        raise HTTPException(status_code=404, detail="Preview not available")
    safe_preview_path = ensure_path_inside(preview_path, settings.preview_dir)
    return FileResponse(safe_preview_path, media_type="image/jpeg")


@app.get("/api/assets/{asset_id}/download")
def download_asset(asset_id: str, _: dict = Depends(require_user)) -> FileResponse:
    try:
        asset = database.get_asset(asset_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Asset not found") from exc

    stored_path = ensure_path_inside(asset["stored_path"], settings.upload_dir)
    if not stored_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(stored_path, filename=asset["filename"], media_type=asset["content_type"])


static_dir = settings.root_dir / "static"
app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")

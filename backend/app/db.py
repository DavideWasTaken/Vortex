from __future__ import annotations

import hashlib
import hmac
import secrets
import sqlite3
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any


def now_iso() -> str:
    return datetime.now(UTC).isoformat()


def hash_password(password: str) -> str:
    iterations = 210_000
    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), iterations)
    return f"pbkdf2_sha256${iterations}${salt}${digest.hex()}"


def verify_password(password: str, password_hash: str) -> bool:
    try:
        algorithm, iterations, salt, expected = password_hash.split("$", 3)
        if algorithm != "pbkdf2_sha256":
            return False
        digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), int(iterations))
        return hmac.compare_digest(digest.hex(), expected)
    except Exception:
        return False


def hash_session_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


class Database:
    def __init__(
        self,
        path: Path,
        *,
        bootstrap_demo_users: bool = True,
        bootstrap_admin_username: str | None = None,
        bootstrap_admin_password: str | None = None,
        bootstrap_admin_language: str = "it",
    ):
        self.path = path
        self.bootstrap_demo_users = bootstrap_demo_users
        self.bootstrap_admin_username = bootstrap_admin_username
        self.bootstrap_admin_password = bootstrap_admin_password
        self.bootstrap_admin_language = bootstrap_admin_language
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.init()

    def connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.path, timeout=30)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        return connection

    def init(self) -> None:
        with self.connect() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS projects (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    description TEXT NOT NULL DEFAULT '',
                    status TEXT NOT NULL DEFAULT 'queued',
                    error TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS assets (
                    id TEXT PRIMARY KEY,
                    project_id TEXT NOT NULL,
                    filename TEXT NOT NULL,
                    content_type TEXT NOT NULL,
                    stored_path TEXT NOT NULL,
                    preview_path TEXT,
                    status TEXT NOT NULL DEFAULT 'queued',
                    page_count INTEGER NOT NULL DEFAULT 0,
                    chunk_count INTEGER NOT NULL DEFAULT 0,
                    visual_count INTEGER NOT NULL DEFAULT 0,
                    error TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE
                );

                CREATE INDEX IF NOT EXISTS idx_assets_project_id ON assets(project_id);
                CREATE INDEX IF NOT EXISTS idx_projects_status ON projects(status);

                CREATE TABLE IF NOT EXISTS users (
                    id TEXT PRIMARY KEY,
                    username TEXT NOT NULL UNIQUE,
                    password_hash TEXT NOT NULL,
                    role TEXT NOT NULL CHECK(role IN ('admin', 'user')),
                    active INTEGER NOT NULL DEFAULT 1,
                    language TEXT NOT NULL DEFAULT 'it',
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );

                CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);

                CREATE TABLE IF NOT EXISTS sessions (
                    token_hash TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    expires_at TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    last_seen_at TEXT NOT NULL,
                    FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
                );

                CREATE INDEX IF NOT EXISTS idx_sessions_user_id ON sessions(user_id);
                CREATE INDEX IF NOT EXISTS idx_sessions_expires_at ON sessions(expires_at);
                """
            )
        self.ensure_user_language_column()
        self.ensure_asset_visual_columns()
        self.ensure_bootstrap_users()

    def ensure_user_language_column(self) -> None:
        with self.connect() as connection:
            rows = connection.execute("PRAGMA table_info(users)").fetchall()
            columns = {row["name"] for row in rows}
            if "language" not in columns:
                connection.execute("ALTER TABLE users ADD COLUMN language TEXT NOT NULL DEFAULT 'it'")
            connection.execute("UPDATE users SET language = 'it' WHERE language IS NULL OR language = ''")

    def ensure_asset_visual_columns(self) -> None:
        with self.connect() as connection:
            rows = connection.execute("PRAGMA table_info(assets)").fetchall()
            columns = {row["name"] for row in rows}
            if "visual_caption" not in columns:
                connection.execute("ALTER TABLE assets ADD COLUMN visual_caption TEXT")
            if "visual_tags" not in columns:
                connection.execute("ALTER TABLE assets ADD COLUMN visual_tags TEXT")

    def ensure_bootstrap_users(self) -> None:
        if self.bootstrap_admin_username and self.bootstrap_admin_password:
            if self.get_user_by_username(self.bootstrap_admin_username) is None:
                self.create_user(
                    username=self.bootstrap_admin_username,
                    password=self.bootstrap_admin_password,
                    role="admin",
                    language=self.bootstrap_admin_language,
                )

        if self.bootstrap_demo_users:
            defaults = [
                ("admin", "admin", "admin"),
                ("user", "user", "user"),
            ]
            for username, password, role in defaults:
                if self.get_user_by_username(username) is None:
                    self.create_user(username=username, password=password, role=role)

    def create_project(self, project_id: str, title: str, description: str) -> dict[str, Any]:
        timestamp = now_iso()
        with self.connect() as connection:
            connection.execute(
                """
                INSERT INTO projects (id, title, description, status, created_at, updated_at)
                VALUES (?, ?, ?, 'queued', ?, ?)
                """,
                (project_id, title, description, timestamp, timestamp),
            )
        return self.get_project(project_id)

    def add_asset(
        self,
        asset_id: str,
        project_id: str,
        filename: str,
        content_type: str,
        stored_path: str,
    ) -> dict[str, Any]:
        timestamp = now_iso()
        with self.connect() as connection:
            connection.execute(
                """
                INSERT INTO assets (
                    id, project_id, filename, content_type, stored_path, created_at, updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (asset_id, project_id, filename, content_type, stored_path, timestamp, timestamp),
            )
        return self.get_asset(asset_id)

    def update_project(self, project_id: str, **fields: Any) -> None:
        self._update("projects", project_id, fields)

    def delete_project(self, project_id: str) -> None:
        with self.connect() as connection:
            cursor = connection.execute("DELETE FROM projects WHERE id = ?", (project_id,))
            if cursor.rowcount == 0:
                raise KeyError(project_id)

    def update_asset(self, asset_id: str, **fields: Any) -> None:
        self._update("assets", asset_id, fields)

    def _update(self, table: str, row_id: str, fields: dict[str, Any]) -> None:
        if not fields:
            return
        fields["updated_at"] = now_iso()
        assignments = ", ".join(f"{key} = ?" for key in fields)
        values = list(fields.values()) + [row_id]
        with self.connect() as connection:
            connection.execute(f"UPDATE {table} SET {assignments} WHERE id = ?", values)

    def get_project(self, project_id: str) -> dict[str, Any]:
        with self.connect() as connection:
            row = connection.execute(
                """
                SELECT
                    p.*,
                    COUNT(a.id) AS files_count,
                    COALESCE(SUM(a.chunk_count), 0) AS chunk_count,
                    COALESCE(SUM(a.visual_count), 0) AS visual_count
                FROM projects p
                LEFT JOIN assets a ON a.project_id = p.id
                WHERE p.id = ?
                GROUP BY p.id
                """,
                (project_id,),
            ).fetchone()
        if row is None:
            raise KeyError(project_id)
        return dict(row)

    def list_projects(self) -> list[dict[str, Any]]:
        with self.connect() as connection:
            rows = connection.execute(
                """
                SELECT
                    p.*,
                    COUNT(a.id) AS files_count,
                    COALESCE(SUM(a.chunk_count), 0) AS chunk_count,
                    COALESCE(SUM(a.visual_count), 0) AS visual_count
                FROM projects p
                LEFT JOIN assets a ON a.project_id = p.id
                GROUP BY p.id
                ORDER BY p.created_at DESC
                """
            ).fetchall()
        return [dict(row) for row in rows]

    def get_asset(self, asset_id: str) -> dict[str, Any]:
        with self.connect() as connection:
            row = connection.execute("SELECT * FROM assets WHERE id = ?", (asset_id,)).fetchone()
        if row is None:
            raise KeyError(asset_id)
        return dict(row)

    def list_assets_for_project(self, project_id: str) -> list[dict[str, Any]]:
        with self.connect() as connection:
            rows = connection.execute(
                "SELECT * FROM assets WHERE project_id = ? ORDER BY created_at",
                (project_id,),
            ).fetchall()
        return [dict(row) for row in rows]

    def delete_assets_for_project(self, project_id: str) -> list[dict[str, Any]]:
        assets = self.list_assets_for_project(project_id)
        with self.connect() as connection:
            connection.execute("DELETE FROM assets WHERE project_id = ?", (project_id,))
        return assets

    def delete_asset(self, asset_id: str) -> None:
        with self.connect() as connection:
            cursor = connection.execute("DELETE FROM assets WHERE id = ?", (asset_id,))
            if cursor.rowcount == 0:
                raise KeyError(asset_id)

    def create_user(
        self,
        username: str,
        password: str,
        role: str,
        language: str = "it",
    ) -> dict[str, Any]:
        user_id = secrets.token_urlsafe(12)
        timestamp = now_iso()
        with self.connect() as connection:
            connection.execute(
                """
                INSERT INTO users (
                    id, username, password_hash, role, active, language, created_at, updated_at
                )
                VALUES (?, ?, ?, ?, 1, ?, ?, ?)
                """,
                (user_id, username, hash_password(password), role, language, timestamp, timestamp),
            )
        return self.get_user(user_id)

    def list_users(self) -> list[dict[str, Any]]:
        with self.connect() as connection:
            rows = connection.execute(
                """
                SELECT id, username, role, active, language, created_at, updated_at
                FROM users
                ORDER BY username
                """
            ).fetchall()
        return [dict(row) for row in rows]

    def count_users(self) -> int:
        with self.connect() as connection:
            row = connection.execute("SELECT COUNT(*) AS count FROM users").fetchone()
        return int(row["count"])

    def get_user(self, user_id: str) -> dict[str, Any]:
        with self.connect() as connection:
            row = connection.execute(
                """
                SELECT id, username, password_hash, role, active, language, created_at, updated_at
                FROM users
                WHERE id = ?
                """,
                (user_id,),
            ).fetchone()
        if row is None:
            raise KeyError(user_id)
        return dict(row)

    def get_user_by_username(self, username: str) -> dict[str, Any] | None:
        with self.connect() as connection:
            row = connection.execute(
                """
                SELECT id, username, password_hash, role, active, language, created_at, updated_at
                FROM users
                WHERE username = ?
                """,
                (username,),
            ).fetchone()
        return dict(row) if row else None

    def update_user(
        self,
        user_id: str,
        *,
        role: str | None = None,
        active: bool | None = None,
        password: str | None = None,
        language: str | None = None,
    ) -> dict[str, Any]:
        fields: dict[str, Any] = {}
        if role is not None:
            fields["role"] = role
        if active is not None:
            fields["active"] = 1 if active else 0
        if password:
            fields["password_hash"] = hash_password(password)
        if language is not None:
            fields["language"] = language
        self._update("users", user_id, fields)
        return self.get_user(user_id)

    def delete_user(self, user_id: str) -> None:
        with self.connect() as connection:
            cursor = connection.execute("DELETE FROM users WHERE id = ?", (user_id,))
            if cursor.rowcount == 0:
                raise KeyError(user_id)

    def create_session(self, token: str, user_id: str, max_age_seconds: int) -> None:
        timestamp = now_iso()
        expires_at = (datetime.now(UTC) + timedelta(seconds=max_age_seconds)).isoformat()
        with self.connect() as connection:
            connection.execute(
                """
                INSERT INTO sessions (token_hash, user_id, expires_at, created_at, last_seen_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (hash_session_token(token), user_id, expires_at, timestamp, timestamp),
            )

    def get_session_user_id(self, token: str) -> str | None:
        token_hash = hash_session_token(token)
        timestamp = now_iso()
        with self.connect() as connection:
            row = connection.execute(
                """
                SELECT user_id, expires_at
                FROM sessions
                WHERE token_hash = ?
                """,
                (token_hash,),
            ).fetchone()
            if row is None:
                return None
            if row["expires_at"] <= timestamp:
                connection.execute("DELETE FROM sessions WHERE token_hash = ?", (token_hash,))
                return None
            connection.execute(
                "UPDATE sessions SET last_seen_at = ? WHERE token_hash = ?",
                (timestamp, token_hash),
            )
        return str(row["user_id"])

    def delete_session(self, token: str) -> None:
        with self.connect() as connection:
            connection.execute("DELETE FROM sessions WHERE token_hash = ?", (hash_session_token(token),))

    def delete_sessions_for_user(self, user_id: str) -> None:
        with self.connect() as connection:
            connection.execute("DELETE FROM sessions WHERE user_id = ?", (user_id,))

    def delete_expired_sessions(self) -> None:
        with self.connect() as connection:
            connection.execute("DELETE FROM sessions WHERE expires_at <= ?", (now_iso(),))

    def health_check(self) -> None:
        with self.connect() as connection:
            connection.execute("SELECT 1").fetchone()

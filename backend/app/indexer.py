from __future__ import annotations

import threading
from pathlib import Path
from traceback import format_exc

from .config import Settings
from .db import Database
from .extraction import build_visual_items, extract_text_chunks
from .search import VectorSearch


class ProjectIndexer:
    def __init__(self, settings: Settings, database: Database, vector_search: VectorSearch):
        self.settings = settings
        self.database = database
        self.vector_search = vector_search
        self._index_lock = threading.Lock()

    def index_project(self, project_id: str) -> None:
        with self._index_lock:
            self._index_project_unlocked(project_id)

    def _index_project_unlocked(self, project_id: str) -> None:
        self.database.update_project(project_id, status="processing", error=None)
        assets = self.database.list_assets_for_project(project_id)

        try:
            for asset in assets:
                self._index_asset(asset)
            self.database.update_project(project_id, status="ready", error=None)
        except Exception:
            self.database.update_project(project_id, status="error", error=format_exc())

    def index_assets(self, project_id: str, asset_ids: list[str]) -> None:
        with self._index_lock:
            self._index_assets_unlocked(project_id, asset_ids)

    def _index_assets_unlocked(self, project_id: str, asset_ids: list[str]) -> None:
        self.database.update_project(project_id, status="processing", error=None)

        try:
            for asset_id in asset_ids:
                self._index_asset(self.database.get_asset(asset_id))
            self.database.update_project(project_id, status="ready", error=None)
        except Exception:
            self.database.update_project(project_id, status="error", error=format_exc())

    def reindex_project(self, project_id: str) -> None:
        with self._index_lock:
            self.vector_search.delete_project(project_id)
            self._index_project_unlocked(project_id)

    def _index_asset(self, asset: dict) -> None:
        asset_id = asset["id"]
        stored_path = Path(asset["stored_path"])
        project_preview_dir = self.settings.preview_dir / asset["project_id"] / asset_id

        self.database.update_asset(asset_id, status="processing", error=None)

        try:
            chunks, page_count = extract_text_chunks(stored_path, project_preview_dir)
            visuals, first_preview = build_visual_items(
                stored_path,
                project_preview_dir,
                self.settings.max_pdf_pages_rendered,
                asset["filename"],
            )

            payload_base = {
                "project_id": asset["project_id"],
                "asset_id": asset_id,
                "filename": asset["filename"],
                "content_type": asset["content_type"],
            }

            chunk_count = self.vector_search.index_text_chunks(chunks, payload_base)
            visual_count, visual_metadata = self.vector_search.index_visual_items(visuals, payload_base)
            visual_tags = _merge_visual_tags(visual_metadata)
            visual_caption = visual_metadata[0]["caption"] if visual_metadata else None

            self.database.update_asset(
                asset_id,
                status="ready",
                page_count=page_count,
                chunk_count=chunk_count,
                visual_count=visual_count,
                preview_path=str(first_preview) if first_preview else None,
                visual_caption=visual_caption,
                visual_tags=", ".join(visual_tags) if visual_tags else None,
                error=None,
            )
        except Exception:
            self.database.update_asset(asset_id, status="error", error=format_exc())
            raise


def _merge_visual_tags(metadata: list[dict]) -> list[str]:
    tags = []
    for item in metadata:
        for tag in item.get("tags", []):
            if tag not in tags:
                tags.append(tag)
    return tags[:10]

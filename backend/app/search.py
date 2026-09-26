from __future__ import annotations

import threading
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from uuid import uuid4

import numpy as np
from fastembed import ImageEmbedding, TextEmbedding
from qdrant_client import QdrantClient
from qdrant_client.http.exceptions import UnexpectedResponse
from qdrant_client.models import Distance, FieldCondition, Filter, FilterSelector, MatchValue, PointStruct, VectorParams

from .config import Settings
from .extraction import TextChunk, VisualItem


TEXT_COLLECTION = "vortex_text_chunks"
VISUAL_COLLECTION = "vortex_visual_items"


@dataclass(frozen=True)
class SearchHit:
    score: float
    payload: dict[str, Any]


@dataclass(frozen=True)
class VisualConcept:
    prompt: str
    caption: str
    tags: tuple[str, ...]


VISUAL_CONCEPTS = [
    VisualConcept(
        "architectural apartment floor plan, blueprint, rooms, terrace, technical drawing",
        "Pianta architettonica con stanze e distribuzione interna.",
        ("pianta", "planimetria", "appartamento", "stanze", "terrazzo", "disegno tecnico"),
    ),
    VisualConcept(
        "residential building facade with balconies, loggias, modular windows",
        "Facciata residenziale con balconi o logge modulari.",
        ("facciata", "residenziale", "balconi", "logge", "prospetto", "finestre"),
    ),
    VisualConcept(
        "glass car showroom with vehicles, central staircase, retail exhibition",
        "Showroom automotive con vetrata, auto esposte e scala centrale.",
        ("showroom", "automotive", "auto", "vetrata", "scala", "retail"),
    ),
    VisualConcept(
        "cosmetic skincare packaging bottles, product labels, pastel colors",
        "Packaging cosmetico con flaconi skincare ed etichette prodotto.",
        ("packaging", "cosmetica", "skincare", "flaconi", "etichette", "prodotto"),
    ),
    VisualConcept(
        "office open space with desks, phone booths, meeting rooms",
        "Ufficio operativo con open space, phone booth e sale riunioni.",
        ("ufficio", "open space", "phone booth", "scrivanie", "meeting", "acustica"),
    ),
    VisualConcept(
        "hotel spa with pool, wellness area, rooftop lounge",
        "Hotel boutique con spa, piscina e area benessere.",
        ("hotel", "spa", "piscina", "wellness", "rooftop", "ospitalita"),
    ),
    VisualConcept(
        "interactive museum exhibition with touch screens, timeline, display cases",
        "Allestimento museale con touch screen, timeline e teche.",
        ("museo", "allestimento", "touch", "timeline", "teche", "interattivo"),
    ),
    VisualConcept(
        "yacht interior lounge with light wood, leather seats, cabin layout",
        "Interni yacht con lounge, rovere chiaro e pelle nautica.",
        ("yacht", "interni", "rovere", "pelle", "lounge", "nautica"),
    ),
    VisualConcept(
        "luxury perfume retail store, marble, brass, product islands",
        "Negozio retail di lusso con isole prodotto e materiali premium.",
        ("retail", "profumeria", "lusso", "marmo", "ottone", "isole prodotto"),
    ),
    VisualConcept(
        "real estate sales sheet, technical PDF page, tables and apartment data",
        "Scheda immobiliare con dati tecnici, superfici e tabelle.",
        ("scheda vendita", "immobiliare", "superfici", "tabella", "pdf", "dati tecnici"),
    ),
]


class EmbeddingModels:
    def __init__(self, settings: Settings):
        self.settings = settings
        self._text_model: TextEmbedding | None = None
        self._clip_text_model: TextEmbedding | None = None
        self._image_model: ImageEmbedding | None = None
        self._text_dim: int | None = None
        self._clip_dim: int | None = None
        self._lock = threading.Lock()

    def text_embeddings(self, texts: list[str]) -> list[list[float]]:
        model = self._get_text_model()
        return [_as_list(vector) for vector in model.embed(texts)]

    def clip_text_embedding(self, text: str) -> list[float]:
        model = self._get_clip_text_model()
        return _as_list(next(model.embed([text])))

    def clip_text_embeddings(self, texts: list[str]) -> list[list[float]]:
        model = self._get_clip_text_model()
        return [_as_list(vector) for vector in model.embed(texts)]

    def image_embeddings(self, paths: list[Path]) -> list[list[float]]:
        model = self._get_image_model()
        return [_as_list(vector) for vector in model.embed([str(path) for path in paths])]

    def text_dim(self) -> int:
        if self._text_dim is None:
            self._text_dim = len(self.text_embeddings(["dimension probe"])[0])
        return self._text_dim

    def clip_dim(self) -> int:
        if self._clip_dim is None:
            self._clip_dim = len(self.clip_text_embedding("dimension probe"))
        return self._clip_dim

    def _get_text_model(self) -> TextEmbedding:
        with self._lock:
            if self._text_model is None:
                self._text_model = TextEmbedding(model_name=self.settings.text_model)
            return self._text_model

    def _get_clip_text_model(self) -> TextEmbedding:
        with self._lock:
            if self._clip_text_model is None:
                self._clip_text_model = TextEmbedding(model_name=self.settings.clip_text_model)
            return self._clip_text_model

    def _get_image_model(self) -> ImageEmbedding:
        with self._lock:
            if self._image_model is None:
                self._image_model = ImageEmbedding(model_name=self.settings.clip_image_model)
            return self._image_model


class VectorSearch:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.models = EmbeddingModels(settings)
        if settings.qdrant_url:
            self.client = QdrantClient(url=settings.qdrant_url)
        else:
            self.client = QdrantClient(path=str(settings.qdrant_path))
        self._collections_ready: set[str] = set()
        self._visual_concept_vectors: list[np.ndarray] | None = None
        self._lock = threading.Lock()
        self._closed = False

    def index_text_chunks(self, chunks: list[TextChunk], payload_base: dict[str, Any]) -> int:
        if not chunks:
            return 0
        self._ensure_collection(TEXT_COLLECTION, self.models.text_dim())
        vectors = self.models.text_embeddings([chunk.text for chunk in chunks])
        points = []
        for chunk, vector in zip(chunks, vectors, strict=True):
            points.append(
                PointStruct(
                    id=str(uuid4()),
                    vector=vector,
                    payload={
                        **payload_base,
                        "kind": "text",
                        "page": chunk.page,
                        "section": chunk.section,
                        "snippet": chunk.text[:700],
                    },
                )
            )
        self.client.upsert(collection_name=TEXT_COLLECTION, points=points)
        return len(points)

    def index_visual_items(self, items: list[VisualItem], payload_base: dict[str, Any]) -> tuple[int, list[dict[str, Any]]]:
        if not items:
            return 0, []
        self._ensure_collection(VISUAL_COLLECTION, self.models.clip_dim())
        vectors = self.models.image_embeddings([item.image_path for item in items])
        points = []
        metadata = []
        for item, vector in zip(items, vectors, strict=True):
            visual_metadata = self._describe_visual(vector, item.label)
            metadata.append(visual_metadata)
            points.append(
                PointStruct(
                    id=str(uuid4()),
                    vector=vector,
                    payload={
                        **payload_base,
                        "kind": "visual",
                        "page": item.page,
                        "section": item.label,
                        "preview_path": str(item.image_path),
                        "snippet": visual_metadata["snippet"],
                        "visual_caption": visual_metadata["caption"],
                        "visual_tags": visual_metadata["tags"],
                        "visual_label_score": visual_metadata["score"],
                    },
                )
            )
        self.client.upsert(collection_name=VISUAL_COLLECTION, points=points)
        return len(points), metadata

    def search(self, query: str, limit: int = 8, mode: str = "all") -> list[SearchHit]:
        hits: list[SearchHit] = []
        fetch_limit = max(limit * 4, 12)

        if mode in {"all", "text"}:
            self._ensure_collection(TEXT_COLLECTION, self.models.text_dim())
            text_vector = self.models.text_embeddings([query])[0]
            hits.extend(self._query(TEXT_COLLECTION, text_vector, fetch_limit, weight=1.0))

        if mode in {"all", "visual"}:
            self._ensure_collection(VISUAL_COLLECTION, self.models.clip_dim())
            visual_vector = self.models.clip_text_embedding(query)
            hits.extend(self._query(VISUAL_COLLECTION, visual_vector, fetch_limit, weight=0.86))

        return _dedupe_hits(hits)[: max(limit * 3, limit)]

    def delete_project(self, project_id: str) -> None:
        selector = FilterSelector(
            filter=Filter(
                must=[
                    FieldCondition(
                        key="project_id",
                        match=MatchValue(value=project_id),
                    )
                ]
            )
        )
        for collection_name in (TEXT_COLLECTION, VISUAL_COLLECTION):
            if not self.client.collection_exists(collection_name=collection_name):
                continue
            self.client.delete(collection_name=collection_name, points_selector=selector)

    def health_check(self) -> None:
        self.client.get_collections()

    def _query(
        self,
        collection_name: str,
        vector: list[float],
        limit: int,
        weight: float,
    ) -> list[SearchHit]:
        try:
            response = self.client.query_points(
                collection_name=collection_name,
                query=vector,
                limit=limit,
                with_payload=True,
            )
        except (UnexpectedResponse, ValueError):
            return []
        return [
            SearchHit(score=float(point.score or 0.0) * weight, payload=dict(point.payload or {}))
            for point in response.points
        ]

    def _ensure_collection(self, collection_name: str, dimension: int) -> None:
        with self._lock:
            if collection_name in self._collections_ready:
                return
            exists = self.client.collection_exists(collection_name=collection_name)
            if not exists:
                self.client.create_collection(
                    collection_name=collection_name,
                    vectors_config=VectorParams(size=dimension, distance=Distance.COSINE),
                )
            self._collections_ready.add(collection_name)

    def _describe_visual(self, vector: list[float], fallback_label: str) -> dict[str, Any]:
        concepts = self._visual_concepts()
        image_vector = _normalize(np.array(vector, dtype=float))
        scores = [
            (float(np.dot(image_vector, concept_vector)), concept)
            for concept_vector, concept in zip(concepts, VISUAL_CONCEPTS, strict=True)
        ]
        scores.sort(key=lambda item: item[0], reverse=True)
        top_score, top_concept = scores[0]

        selected = [top_concept]
        for score, concept in scores[1:3]:
            if score >= top_score - 0.035:
                selected.append(concept)

        tags = []
        for concept in selected:
            for tag in concept.tags:
                if tag not in tags:
                    tags.append(tag)
        caption = top_concept.caption if top_score > 0 else f"Anteprima visiva: {fallback_label}"
        snippet = f"{caption} Tag: {', '.join(tags[:8])}."
        return {
            "caption": caption,
            "tags": tags[:8],
            "score": round(top_score, 4),
            "snippet": snippet,
        }

    def _visual_concepts(self) -> list[np.ndarray]:
        if self._visual_concept_vectors is None:
            vectors = self.models.clip_text_embeddings([concept.prompt for concept in VISUAL_CONCEPTS])
            self._visual_concept_vectors = [
                _normalize(np.array(vector, dtype=float))
                for vector in vectors
            ]
        return self._visual_concept_vectors

    def close(self) -> None:
        if self._closed:
            return
        self.client.close()
        self._closed = True


def group_hits_by_project(hits: list[SearchHit], limit: int) -> list[dict[str, Any]]:
    grouped: dict[str, dict[str, Any]] = {}
    evidence_seen: dict[str, set[str]] = defaultdict(set)

    for rank, hit in enumerate(hits, start=1):
        project_id = hit.payload.get("project_id")
        if not project_id:
            continue
        group = grouped.setdefault(
            project_id,
            {
                "project_id": project_id,
                "score": 0.0,
                "evidence": [],
            },
        )
        group["score"] += hit.score / rank

        evidence_key = "|".join(
            str(hit.payload.get(key, ""))
            for key in ("asset_id", "kind", "page", "section", "snippet")
        )
        if evidence_key in evidence_seen[project_id]:
            continue
        evidence_seen[project_id].add(evidence_key)
        if len(group["evidence"]) < 4:
            group["evidence"].append(
                {
                    "kind": hit.payload.get("kind"),
                    "asset_id": hit.payload.get("asset_id"),
                    "filename": hit.payload.get("filename"),
                    "page": hit.payload.get("page"),
                    "section": hit.payload.get("section"),
                    "snippet": hit.payload.get("snippet"),
                    "visual_caption": hit.payload.get("visual_caption"),
                    "visual_tags": hit.payload.get("visual_tags") or [],
                    "preview_url": f"/api/assets/{hit.payload.get('asset_id')}/preview",
                    "download_url": f"/api/assets/{hit.payload.get('asset_id')}/download",
                }
            )

    ordered = sorted(grouped.values(), key=lambda item: item["score"], reverse=True)
    return ordered[:limit]


def _dedupe_hits(hits: list[SearchHit]) -> list[SearchHit]:
    best_by_key: dict[str, SearchHit] = {}
    for hit in hits:
        key = "|".join(
            str(hit.payload.get(part, ""))
            for part in ("asset_id", "kind", "page", "section", "snippet")
        )
        current = best_by_key.get(key)
        if current is None or hit.score > current.score:
            best_by_key[key] = hit
    return sorted(best_by_key.values(), key=lambda hit: hit.score, reverse=True)


def _as_list(vector: np.ndarray) -> list[float]:
    return vector.astype(float).tolist()


def _normalize(vector: np.ndarray) -> np.ndarray:
    norm = np.linalg.norm(vector)
    if norm == 0:
        return vector
    return vector / norm

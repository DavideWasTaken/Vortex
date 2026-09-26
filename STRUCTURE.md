# Vortex Structure

This document summarizes the technologies used by Vortex and the role of each major component in the project.

## Overview

Vortex is a local web app for archiving projects, uploading documents and images, extracting content, generating embeddings, and searching materials with natural-language queries.

The stack is composed of:

- a Python backend built with FastAPI;
- a static web interface served by the backend;
- SQLite for application data, users, and sessions;
- Qdrant for vector search;
- FastEmbed for local text and image embeddings;
- Docker Compose for containerized execution.

## Backend

The backend lives in `backend/app` and is based on:

- `FastAPI`: exposes the HTTP API and handles authentication, uploads, search, project management, and user management.
- `Uvicorn`: ASGI server used to run the application.
- `Pydantic`: validates API request payloads.
- `python-multipart`: allows FastAPI to receive files uploaded through forms.

Main entry point:

```text
backend/app/main.py
```

Local startup command:

```bash
cd backend
.venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## Frontend

The UI is a static web app served directly by FastAPI.

Main files:

```text
backend/app/static/index.html
backend/app/static/app.js
backend/app/static/styles.css
```

Technologies used:

- static HTML;
- vanilla JavaScript for state, API calls, and interactions;
- custom CSS;
- Tailwind CSS loaded through a CDN for utility classes and layout.

There is no frontend framework such as React, Vue, or Angular. The interface runs directly in the browser and communicates with the backend APIs.

## Data Persistence

Vortex uses two persistence layers:

- `SQLite`: stores users, sessions, projects, assets, and application metadata.
- `Qdrant`: stores vectors and payloads used for semantic and visual search.

Default local paths:

```text
data/vortex.sqlite3
data/qdrant/
data/uploads/
data/previews/
```

The data directory can be configured with:

```bash
VORTEX_DATA_DIR=/path/to/data
```

## Search and Local AI

Search is built on locally generated embeddings and does not require external APIs.

Main components:

- `qdrant-client`: Python client used to index and query Qdrant.
- `qdrant-client[fastembed]`: includes FastEmbed for local embeddings.
- `FastEmbed TextEmbedding`: generates text embeddings for documents and queries.
- `FastEmbed ImageEmbedding`: generates visual embeddings for images and PDF previews.
- `NumPy`: used for calculations and scoring during search.

Configurable models:

```bash
VORTEX_TEXT_MODEL=sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2
VORTEX_CLIP_TEXT_MODEL=Qdrant/clip-ViT-B-32-text
VORTEX_CLIP_IMAGE_MODEL=Qdrant/clip-ViT-B-32-vision
```

If `QDRANT_URL` is not set, the backend uses embedded Qdrant storage on disk inside `VORTEX_DATA_DIR`.

## Indexing Workflow

Project indexing is coordinated by:

```text
backend/app/indexer.py
```

The indexer processes each uploaded asset, extracts text chunks, generates visual previews, creates embeddings, and writes the resulting points to Qdrant.

Indexing is serialized with an internal `threading.Lock`. This matters for local development because embedded Qdrant uses on-disk storage and can fail on concurrent writes. The lock keeps uploads and reindex operations stable when multiple projects are queued close together.

## Document Extraction and Previews

Vortex supports documents and images through dedicated Python libraries:

- `pypdf`: extracts text from PDFs.
- `python-docx`: extracts text from DOCX files.
- `Pillow`: creates previews, normalizes images, and renders lightweight simulated 3D CAD previews.
- `pypdfium2`: renders PDF pages as images for visual search and previews.
- `ezdxf`: parses DXF drawings, extracts CAD text/layers/entities, and supports local preview generation.

Supported extensions:

```text
.pdf, .docx, .txt, .md, .markdown, .csv, .log,
.png, .jpg, .jpeg, .webp, .tif, .tiff, .bmp,
.dxf, .dwg
```

DXF files are parsed directly and rendered as simulated 3D technical previews. DWG files are accepted and handled with a best-effort fallback; when ODA File Converter, `dwgread`, or `dwg2dxf` is available locally, Vortex attempts to convert DWG files to DXF for richer extraction and previews. If no converter is available, a DWG can use a paired PDF from the same upload to generate a 3D-like preview card.

## Authentication and Roles

The app manages users and sessions locally:

- sessions persisted in SQLite;
- configurable session cookie;
- `admin` and `user` roles;
- protection against too many login attempts.

In development, demo accounts are created:

```text
admin / admin
user  / user
```

In production, the initial admin is bootstrapped through environment variables.

## Docker

The containerized stack uses Docker Compose.

Main files:

```text
docker-compose.dev.yml
docker-compose.prod.yml
backend/Dockerfile
docker/qdrant/Dockerfile
```

Development:

```bash
docker compose -f docker-compose.dev.yml up --build
```

Main services:

- `api`: FastAPI backend served by Uvicorn on port `8000`;
- `qdrant`: vector database exposed on port `6333`.

Volumes:

- `vortex_data`: application data;
- `qdrant_data`: Qdrant storage.

The backend container uses `python:3.12-slim` and installs dependencies from:

```text
backend/requirements.txt
```

## Health Checks

Available endpoints:

```text
/api/health
/api/health/ready
```

They are used both for manual checks and Docker health checks.

## Main Environment Variables

```bash
VORTEX_ENV=development
VORTEX_DATA_DIR=/data
QDRANT_URL=http://qdrant:6333

VORTEX_SESSION_COOKIE_SECURE=true
VORTEX_SESSION_COOKIE_SAMESITE=lax
VORTEX_SESSION_MAX_AGE_SECONDS=28800

VORTEX_MAX_UPLOAD_FILES=20
VORTEX_MAX_UPLOAD_SIZE_BYTES=104857600
VORTEX_MAX_PDF_PAGES_RENDERED=40
```

## Architecture Summary

```text
Browser
  |
  | static HTML/CSS/JS + API calls
  v
FastAPI / Uvicorn
  |
  |-- SQLite: users, sessions, projects, assets
  |
  |-- filesystem: uploads and previews
  |
  |-- FastEmbed: text and image embeddings
  |
  |-- Qdrant: vector indexes for semantic and visual search
```

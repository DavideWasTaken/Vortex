import importlib
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient


class OfflineTextModel:
    """Replace model downloads only; exercise the actual SQLite and Qdrant stores."""
    def text_dim(self):
        return 3

    def text_embeddings(self, texts):
        return [[1.0, 0.0, 0.0] for _ in texts]


@pytest.fixture(scope="module")
def api(tmp_path_factory):
    with patch.dict("os.environ", {
        "VORTEX_ENV": "development",
        "VORTEX_DATA_DIR": str(tmp_path_factory.mktemp("vortex")),
        "QDRANT_URL": "",
        "VORTEX_BOOTSTRAP_DEMO_USERS": "true",
        "VORTEX_BOOTSTRAP_ADMIN_USERNAME": "",
        "VORTEX_BOOTSTRAP_ADMIN_PASSWORD": "",
        "VORTEX_SESSION_COOKIE_SECURE": "true",
    }):
        module = importlib.import_module("app.main")
        module.vector_search.models = OfflineTextModel()
        with TestClient(module.app, base_url="https://testserver") as client:
            yield client


@pytest.fixture
def admin(api):
    api.cookies.clear()
    response = api.post("/api/auth/login", json={"username": "admin", "password": "admin"})
    assert response.status_code == 200
    assert "HttpOnly" in response.headers["set-cookie"]
    assert "Secure" in response.headers["set-cookie"]
    return api


@pytest.fixture
def project(admin):
    response = admin.post("/api/projects", data={"title": "Synthetic project"},
        files={"files": ("notes.txt", b"A gearbox with ceramic bearings.", "text/plain")})
    assert response.status_code == 200
    return admin.get("/api/projects/" + response.json()["id"]).json()


def test_upload_index_search_and_download(admin, project):
    assert project["status"] == "ready"
    asset = project["assets"][0]
    assert asset["status"] == "ready"
    result = admin.post("/api/search", json={"query": "ceramic bearings", "mode": "text"})
    assert result.status_code == 200
    matching = next(item for item in result.json()["results"] if item["project_id"] == project["id"])
    assert any("ceramic bearings" in entry["snippet"] for entry in matching["evidence"])
    assert admin.get(f"/api/assets/{asset['id']}/download").content == b"A gearbox with ceramic bearings."


def test_unauthenticated_users_cannot_read_documents(admin, project):
    asset = project["assets"][0]
    admin.cookies.clear()
    for endpoint in ("/api/projects", f"/api/assets/{asset['id']}/download", f"/api/assets/{asset['id']}/preview"):
        assert admin.get(endpoint).status_code == 401


def test_reader_cannot_write_or_manage_users(api):
    api.cookies.clear()
    assert api.post("/api/auth/login", json={"username": "user", "password": "user"}).status_code == 200
    assert api.get("/api/projects").status_code == 200
    assert api.get("/api/users").status_code == 403
    assert api.post("/api/projects", data={"title": "Denied"},
        files={"files": ("test.txt", b"test", "text/plain")}).status_code == 403


def test_invalid_pdf_rolls_back_project(admin):
    before = len(admin.get("/api/projects").json()["projects"])
    response = admin.post("/api/projects", data={"title": "Invalid"},
        files={"files": ("fake.pdf", b"this is not a PDF", "application/pdf")})
    assert response.status_code == 400
    assert len(admin.get("/api/projects").json()["projects"]) == before


def test_unsupported_upload_is_rejected(admin):
    response = admin.post("/api/projects", data={"title": "Invalid"},
        files={"files": ("run.exe", b"not executable", "application/octet-stream")})
    assert response.status_code == 400


def test_logout_invalidates_session(admin):
    assert admin.get("/api/auth/me").status_code == 200
    cookies = dict(admin.cookies)
    assert admin.post("/api/auth/logout").status_code == 200
    admin.cookies.update(cookies)
    assert admin.get("/api/auth/me").status_code == 401


def test_delete_removes_assets_and_search_results(admin, project):
    project_id = project["id"]
    asset_id = project["assets"][0]["id"]
    assert admin.delete(f"/api/projects/{project_id}").status_code == 200
    assert admin.get(f"/api/assets/{asset_id}/download").status_code == 404
    result = admin.post("/api/search", json={"query": "ceramic bearings", "mode": "text"})
    assert all(item["project_id"] != project_id for item in result.json()["results"])

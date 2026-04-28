from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.codegen.templated import TemplatedGenerator, _route
from app.main import create_app
from app.models import IdeaSpec


@pytest.fixture()
def client() -> TestClient:
    return TestClient(create_app())


@pytest.mark.parametrize(
    ("idea", "expected"),
    [
        ("a notes app", "notes"),
        ("simple calculator", "calculator"),
        ("flashlight please", "flashlight"),
        ("siswati english translator", "translator"),
        ("a community scheduler for moMo agents", "default"),
    ],
)
def test_archetype_routing(idea: str, expected: str) -> None:
    assert _route(idea) == expected


def test_templated_generator_produces_required_files() -> None:
    files = TemplatedGenerator().generate(IdeaSpec(idea="a notes app"))
    paths = {f.path for f in files.files}
    assert "pubspec.yaml" in paths
    assert "lib/main.dart" in paths
    assert "README.md" in paths
    assert files.archetype == "notes"


def test_pubspec_has_required_fields() -> None:
    files = TemplatedGenerator().generate(IdeaSpec(idea="hello"))
    pubspec = next(f.content for f in files.files if f.path == "pubspec.yaml")
    for required in ("name:", "description:", "environment:", "dependencies:", "flutter:"):
        assert required in pubspec


def test_health_endpoint(client: TestClient) -> None:
    r = client.get("/health")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "ok"
    assert body["codegen_provider"] in {"templated", "anthropic"}
    assert body["builder_provider"] in {"stub", "docker", "codemagic"}


def test_generate_endpoint_creates_project(client: TestClient) -> None:
    r = client.post(
        "/generate",
        json={"idea": "a notes app", "architectures": ["arm64-v8a"]},
    )
    assert r.status_code == 200, r.text
    body = r.json()
    project_id = body["project"]["project_id"]
    assert body["project"]["archetype"] == "notes"
    assert "lib/main.dart" in body["file_tree"]

    # Project metadata
    r2 = client.get(f"/projects/{project_id}")
    assert r2.status_code == 200

    # Single file fetch
    r3 = client.get(f"/projects/{project_id}/files/lib/main.dart")
    assert r3.status_code == 200
    assert "MaterialApp" in r3.json()["content"]

    # Zip download
    r4 = client.get(f"/projects/{project_id}/zip")
    assert r4.status_code == 200
    assert r4.headers["content-type"] == "application/zip"
    assert len(r4.content) > 0


def test_build_stub_succeeds(client: TestClient) -> None:
    r = client.post("/generate", json={"idea": "a calculator"})
    project_id = r.json()["project"]["project_id"]

    r2 = client.post("/build", json={"project_id": project_id})
    assert r2.status_code == 200, r2.text
    job_id = r2.json()["job_id"]

    # Stub builder runs synchronously inline via BackgroundTasks once
    # TestClient finishes the request; poll until done.
    for _ in range(50):
        s = client.get(f"/status/{job_id}").json()
        if s["state"] in {"succeeded", "failed"}:
            break
    assert s["state"] == "succeeded", s

    r3 = client.get(f"/download/{job_id}")
    assert r3.status_code == 200
    assert r3.content.startswith(b"AUTOAI_STUB_APK_v1")


def test_build_unknown_project(client: TestClient) -> None:
    r = client.post("/build", json={"project_id": "nope"})
    assert r.status_code == 404

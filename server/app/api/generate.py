from __future__ import annotations

from fastapi import APIRouter, HTTPException

from .. import storage
from ..codegen import get_generator
from ..models import GenerateResponse, IdeaSpec, ProjectMeta
from ..settings import settings

router = APIRouter()


@router.post("/generate", response_model=GenerateResponse)
def generate(spec: IdeaSpec) -> GenerateResponse:
    provider = settings.resolve_codegen()
    generator = get_generator(provider)
    files = generator.generate(spec)

    project_id = storage.new_project_id()
    app_name = spec.app_name or _derive_app_name(spec.idea)
    meta = storage.save_project(
        project_id=project_id,
        idea=spec.idea,
        app_name=app_name,
        architectures=list(spec.architectures),
        files=files,
    )
    return GenerateResponse(
        project=meta,
        file_tree=storage.list_project_files(project_id),
    )


@router.get("/projects/{project_id}", response_model=GenerateResponse)
def get_project(project_id: str) -> GenerateResponse:
    meta = storage.load_project_meta(project_id)
    if meta is None:
        raise HTTPException(status_code=404, detail="project not found")
    return GenerateResponse(
        project=meta,
        file_tree=storage.list_project_files(project_id),
    )


@router.get("/projects/{project_id}/files/{path:path}")
def get_project_file(project_id: str, path: str) -> dict[str, str]:
    if storage.load_project_meta(project_id) is None:
        raise HTTPException(status_code=404, detail="project not found")
    content = storage.read_project_file(project_id, path)
    if content is None:
        raise HTTPException(status_code=404, detail="file not found")
    return {"path": path, "content": content}


def _derive_app_name(idea: str) -> str:
    head = idea.strip().split("\n", 1)[0]
    return head[:40] or "MyApp"


# Late-imported to avoid circulars; exposed so main.py has a single mount.
__all__ = ["router"]


# Project meta type re-export for FastAPI schema.
_ = ProjectMeta

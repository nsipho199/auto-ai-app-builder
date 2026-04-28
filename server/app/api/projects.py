from __future__ import annotations

from fastapi import APIRouter, HTTPException
from fastapi.responses import Response

from .. import storage

router = APIRouter()


@router.get("/projects/{project_id}/zip")
def download_zip(project_id: str) -> Response:
    meta = storage.load_project_meta(project_id)
    if meta is None:
        raise HTTPException(status_code=404, detail="project not found")
    payload = storage.project_zip_bytes(project_id)
    if payload is None:
        raise HTTPException(status_code=404, detail="project files missing")
    filename = f"{meta.app_name.replace(' ', '_') or 'project'}.zip"
    return Response(
        content=payload,
        media_type="application/zip",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )

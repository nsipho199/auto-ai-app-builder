from __future__ import annotations

from fastapi import APIRouter, BackgroundTasks, HTTPException
from fastapi.responses import FileResponse

from .. import storage
from ..builder import get_builder
from ..models import Architecture, BuildJob, BuildRequest
from ..settings import settings

router = APIRouter()


@router.post("/build", response_model=BuildJob)
def start_build(req: BuildRequest, background: BackgroundTasks) -> BuildJob:
    meta = storage.load_project_meta(req.project_id)
    if meta is None:
        raise HTTPException(status_code=404, detail="project not found")

    archs: list[Architecture] = list(req.architectures or meta.architectures)
    builder = get_builder(settings.builder_provider)
    job = storage.create_job(
        project_id=req.project_id,
        builder=builder.name,
        architectures=list(archs),
    )
    background.add_task(builder.build, req.project_id, job.job_id, archs)
    return job


@router.get("/status/{job_id}", response_model=BuildJob)
def get_status(job_id: str) -> BuildJob:
    job = storage.load_job(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="job not found")
    return job


@router.get("/status/{job_id}/log")
def get_log(job_id: str) -> dict[str, str]:
    job = storage.load_job(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="job not found")
    return {"job_id": job_id, "log": storage.read_job_log(job_id)}


@router.get("/download/{job_id}")
def download(job_id: str) -> FileResponse:
    job = storage.load_job(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="job not found")
    artifact = storage.job_artifact_path(job_id)
    if artifact is None or not artifact.exists():
        raise HTTPException(status_code=404, detail="artifact not ready")
    return FileResponse(
        artifact,
        media_type="application/vnd.android.package-archive",
        filename=f"{job.project_id}.apk",
    )

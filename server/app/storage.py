"""Filesystem-backed storage for generated projects and build jobs.

Designed so the storage layer can be swapped for S3 + Postgres without
touching the API routes — every read/write goes through this module.
"""

from __future__ import annotations

import io
import shutil
import zipfile
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from .models import (
    BuildJob,
    BuildState,
    GeneratedFile,
    ProjectFiles,
    ProjectMeta,
)
from .settings import settings


def _now() -> datetime:
    return datetime.now(UTC)


def _projects_dir() -> Path:
    p = settings.data_dir / "projects"
    p.mkdir(parents=True, exist_ok=True)
    return p


def _jobs_dir() -> Path:
    p = settings.data_dir / "jobs"
    p.mkdir(parents=True, exist_ok=True)
    return p


# ---------------------------------------------------------------------------
# Projects
# ---------------------------------------------------------------------------


def new_project_id() -> str:
    return uuid4().hex[:12]


def save_project(
    project_id: str,
    idea: str,
    app_name: str,
    architectures: list[str],
    files: ProjectFiles,
) -> ProjectMeta:
    project_dir = _projects_dir() / project_id
    files_dir = project_dir / "files"
    if project_dir.exists():
        shutil.rmtree(project_dir)
    files_dir.mkdir(parents=True)

    for f in files.files:
        target = files_dir / f.path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(f.content, encoding="utf-8")

    meta = ProjectMeta(
        project_id=project_id,
        archetype=files.archetype,
        idea=idea,
        app_name=app_name,
        architectures=architectures,  # type: ignore[arg-type]
        created_at=_now(),
        file_count=len(files.files),
    )
    (project_dir / "meta.json").write_text(meta.model_dump_json(indent=2))
    return meta


def load_project_meta(project_id: str) -> ProjectMeta | None:
    meta_path = _projects_dir() / project_id / "meta.json"
    if not meta_path.exists():
        return None
    return ProjectMeta.model_validate_json(meta_path.read_text())


def list_project_files(project_id: str) -> list[str]:
    files_dir = _projects_dir() / project_id / "files"
    if not files_dir.exists():
        return []
    return sorted(
        str(p.relative_to(files_dir)) for p in files_dir.rglob("*") if p.is_file()
    )


def read_project_file(project_id: str, path: str) -> str | None:
    files_dir = _projects_dir() / project_id / "files"
    target = (files_dir / path).resolve()
    try:
        target.relative_to(files_dir.resolve())
    except ValueError:
        return None
    if not target.is_file():
        return None
    return target.read_text(encoding="utf-8")


def project_files_path(project_id: str) -> Path:
    return _projects_dir() / project_id / "files"


def project_zip_bytes(project_id: str) -> bytes | None:
    files_dir = project_files_path(project_id)
    if not files_dir.exists():
        return None
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for f in files_dir.rglob("*"):
            if f.is_file():
                zf.write(f, arcname=str(f.relative_to(files_dir)))
    return buf.getvalue()


def load_project_files(project_id: str) -> list[GeneratedFile]:
    files_dir = project_files_path(project_id)
    out: list[GeneratedFile] = []
    if not files_dir.exists():
        return out
    for f in files_dir.rglob("*"):
        if f.is_file():
            out.append(
                GeneratedFile(
                    path=str(f.relative_to(files_dir)),
                    content=f.read_text(encoding="utf-8"),
                )
            )
    return out


# ---------------------------------------------------------------------------
# Build jobs
# ---------------------------------------------------------------------------


def new_job_id() -> str:
    return uuid4().hex[:12]


def create_job(project_id: str, builder: str, architectures: list[str]) -> BuildJob:
    job_id = new_job_id()
    now = _now()
    job = BuildJob(
        job_id=job_id,
        project_id=project_id,
        state=BuildState.queued,
        builder=builder,
        architectures=architectures,  # type: ignore[arg-type]
        created_at=now,
        updated_at=now,
    )
    job_dir = _jobs_dir() / job_id
    job_dir.mkdir(parents=True)
    _write_job(job)
    (job_dir / "log.txt").write_text("")
    return job


def _job_dir(job_id: str) -> Path:
    return _jobs_dir() / job_id


def _write_job(job: BuildJob) -> None:
    job_dir = _job_dir(job.job_id)
    job_dir.mkdir(parents=True, exist_ok=True)
    (job_dir / "meta.json").write_text(job.model_dump_json(indent=2))


def load_job(job_id: str) -> BuildJob | None:
    meta = _job_dir(job_id) / "meta.json"
    if not meta.exists():
        return None
    return BuildJob.model_validate_json(meta.read_text())


def update_job(
    job_id: str,
    *,
    state: BuildState | None = None,
    artifact_url: str | None = None,
    error: str | None = None,
    log_excerpt: str | None = None,
) -> BuildJob | None:
    job = load_job(job_id)
    if job is None:
        return None
    if state is not None:
        job.state = state
    if artifact_url is not None:
        job.artifact_url = artifact_url
    if error is not None:
        job.error = error
    if log_excerpt is not None:
        job.log_excerpt = log_excerpt
    job.updated_at = _now()
    _write_job(job)
    return job


def append_job_log(job_id: str, line: str) -> None:
    log_path = _job_dir(job_id) / "log.txt"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("a", encoding="utf-8") as f:
        f.write(line.rstrip() + "\n")
    # Keep a short excerpt on the job for convenience.
    excerpt = log_path.read_text(encoding="utf-8").splitlines()[-20:]
    update_job(job_id, log_excerpt="\n".join(excerpt))


def read_job_log(job_id: str) -> str:
    log_path = _job_dir(job_id) / "log.txt"
    if not log_path.exists():
        return ""
    return log_path.read_text(encoding="utf-8")


def write_job_artifact(job_id: str, content: bytes, filename: str = "artifact.apk") -> Path:
    job_dir = _job_dir(job_id)
    job_dir.mkdir(parents=True, exist_ok=True)
    path = job_dir / filename
    path.write_bytes(content)
    return path


def job_artifact_path(job_id: str) -> Path | None:
    job_dir = _job_dir(job_id)
    if not job_dir.exists():
        return None
    for candidate in job_dir.glob("artifact*"):
        return candidate
    return None

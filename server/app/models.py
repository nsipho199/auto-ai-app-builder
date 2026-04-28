from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, Field

Architecture = Literal["arm64-v8a", "x86_64", "armeabi-v7a"]


class IdeaSpec(BaseModel):
    """A user's app idea, plus structured options."""

    idea: str = Field(min_length=1, max_length=4000)
    app_name: str | None = Field(default=None, max_length=80)
    architectures: list[Architecture] = Field(
        default_factory=lambda: ["arm64-v8a", "x86_64"],  # type: ignore[arg-type]
    )
    primary_color: str | None = Field(default=None, pattern=r"^#?[0-9A-Fa-f]{6}$")


class GeneratedFile(BaseModel):
    path: str
    content: str


class ProjectFiles(BaseModel):
    """A complete generated project: a list of file paths + contents."""

    archetype: str
    files: list[GeneratedFile]


class ProjectMeta(BaseModel):
    project_id: str
    archetype: str
    idea: str
    app_name: str
    architectures: list[Architecture]
    created_at: datetime
    file_count: int


class GenerateResponse(BaseModel):
    project: ProjectMeta
    file_tree: list[str]


class BuildRequest(BaseModel):
    project_id: str
    architectures: list[Architecture] | None = None


class BuildState(StrEnum):
    queued = "queued"
    running = "running"
    succeeded = "succeeded"
    failed = "failed"


class BuildJob(BaseModel):
    job_id: str
    project_id: str
    state: BuildState
    builder: str
    architectures: list[Architecture]
    created_at: datetime
    updated_at: datetime
    artifact_url: str | None = None
    log_excerpt: str = ""
    error: str | None = None


class HealthResponse(BaseModel):
    status: Literal["ok"] = "ok"
    codegen_provider: str
    builder_provider: str

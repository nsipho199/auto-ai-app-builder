from __future__ import annotations

from abc import ABC, abstractmethod

from ..models import Architecture


class Builder(ABC):
    """Strategy interface for turning a generated project into an APK.

    Implementations are expected to be **synchronous** (run inside an executor).
    They must:
      - read project files via `app.storage.project_files_path(project_id)`,
      - stream log lines via `app.storage.append_job_log(job_id, line)`,
      - write the final APK via `app.storage.write_job_artifact(...)`,
      - update the job state to `succeeded` / `failed`.
    """

    name: str = "base"

    @abstractmethod
    def build(self, project_id: str, job_id: str, architectures: list[Architecture]) -> None: ...

"""Stub builder.

Produces a fake `.apk` that's actually the project zip with an `.apk` extension
plus a sentinel header. Lets the end-to-end UI flow be exercised without a 3GB
Android toolchain. The UI labels these clearly as "stub builds".
"""

from __future__ import annotations

import time

from ..models import Architecture, BuildState
from ..storage import (
    append_job_log,
    project_zip_bytes,
    update_job,
    write_job_artifact,
)
from .base import Builder


class StubBuilder(Builder):
    name = "stub"

    def build(self, project_id: str, job_id: str, architectures: list[Architecture]) -> None:
        update_job(job_id, state=BuildState.running)
        append_job_log(job_id, f"[stub] starting build for project {project_id}")
        append_job_log(job_id, f"[stub] target architectures: {', '.join(architectures)}")

        # Simulate a few build phases for nicer UX.
        for phase in ("flutter pub get", "compile dart -> kernel", "package APK"):
            append_job_log(job_id, f"[stub] {phase}…")
            time.sleep(0.2)

        zip_bytes = project_zip_bytes(project_id)
        if zip_bytes is None:
            update_job(job_id, state=BuildState.failed, error="project not found")
            append_job_log(job_id, "[stub] ERROR: project not found")
            return

        # Marker bytes so consumers can tell this is a stub build, not a real APK.
        marker = b"AUTOAI_STUB_APK_v1\n"
        write_job_artifact(job_id, marker + zip_bytes, filename="artifact.apk")
        append_job_log(job_id, f"[stub] artifact ready ({len(zip_bytes)} bytes payload)")
        update_job(
            job_id,
            state=BuildState.succeeded,
            artifact_url=f"/download/{job_id}",
        )

"""Docker-based Flutter builder.

Runs `cirrusci/flutter:stable` against the generated project to produce a
real `app-release.apk`. Streams logs back into the job store.
"""

from __future__ import annotations

import shutil
import subprocess
import time

from ..models import Architecture, BuildState
from ..settings import settings
from ..storage import (
    append_job_log,
    job_artifact_path,
    project_files_path,
    update_job,
    write_job_artifact,
)
from .base import Builder


class DockerFlutterBuilder(Builder):
    name = "docker"

    def build(self, project_id: str, job_id: str, architectures: list[Architecture]) -> None:
        if shutil.which("docker") is None:
            update_job(
                job_id,
                state=BuildState.failed,
                error="docker not available on host",
            )
            append_job_log(job_id, "[docker] ERROR: docker binary not found on host")
            return

        files_dir = project_files_path(project_id).resolve()
        if not files_dir.exists():
            update_job(job_id, state=BuildState.failed, error="project not found")
            append_job_log(job_id, "[docker] ERROR: project directory missing")
            return

        update_job(job_id, state=BuildState.running)
        append_job_log(job_id, f"[docker] building {project_id} for {', '.join(architectures)}")

        target_platform = ",".join(_arch_to_flutter(a) for a in architectures)
        script = (
            "set -eux; cd /app; "
            "flutter pub get; "
            f"flutter build apk --release --target-platform {target_platform}"
        )
        cmd = [
            "docker", "run", "--rm",
            "-v", f"{files_dir}:/app",
            "-w", "/app",
            settings.docker_flutter_image,
            "bash", "-lc", script,
        ]
        append_job_log(job_id, f"[docker] $ {' '.join(cmd)}")
        timeout = settings.docker_build_timeout_seconds
        deadline = time.monotonic() + timeout
        try:
            proc = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
            )
            assert proc.stdout is not None
            for line in proc.stdout:
                append_job_log(job_id, line.rstrip())
                if time.monotonic() > deadline:
                    proc.kill()
                    proc.wait()
                    update_job(
                        job_id,
                        state=BuildState.failed,
                        error=f"build exceeded {timeout}s timeout",
                    )
                    append_job_log(
                        job_id,
                        f"[docker] ERROR: build exceeded {timeout}s timeout, killed",
                    )
                    return
            rc = proc.wait()
            if rc != 0:
                update_job(
                    job_id,
                    state=BuildState.failed,
                    error=f"flutter build returned {rc}",
                )
                return
        except Exception as e:  # pragma: no cover - defensive
            update_job(job_id, state=BuildState.failed, error=str(e))
            append_job_log(job_id, f"[docker] EXCEPTION: {e}")
            return

        apk = files_dir / "build" / "app" / "outputs" / "flutter-apk" / "app-release.apk"
        if not apk.exists():
            update_job(
                job_id,
                state=BuildState.failed,
                error="apk not produced",
            )
            append_job_log(job_id, f"[docker] ERROR: expected apk at {apk}")
            return

        write_job_artifact(job_id, apk.read_bytes(), filename="artifact.apk")
        # Sanity-check the artifact landed.
        produced = job_artifact_path(job_id)
        size = produced.stat().st_size if produced else 0
        append_job_log(job_id, f"[docker] artifact ready ({size} bytes)")
        update_job(
            job_id,
            state=BuildState.succeeded,
            artifact_url=f"/download/{job_id}",
        )


def _arch_to_flutter(arch: Architecture) -> str:
    # Flutter's --target-platform uses "android-arm", "android-arm64", "android-x64".
    return {
        "armeabi-v7a": "android-arm",
        "arm64-v8a": "android-arm64",
        "x86_64": "android-x64",
    }[arch]

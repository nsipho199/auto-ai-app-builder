"use client";

import { useCallback, useEffect, useState } from "react";

import BuildStatus from "@/components/BuildStatus";
import CodePreview from "@/components/CodePreview";
import DownloadCard from "@/components/DownloadCard";
import IdeaForm from "@/components/IdeaForm";
import { api, type BuildJob, type GenerateResponse, type HealthResponse, type IdeaSpec } from "@/lib/api";

export default function Page() {
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [project, setProject] = useState<GenerateResponse | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [jobId, setJobId] = useState<string | null>(null);
  const [job, setJob] = useState<BuildJob | null>(null);

  useEffect(() => {
    api.health().then(setHealth).catch(() => setHealth(null));
  }, []);

  const generate = useCallback(async (spec: IdeaSpec) => {
    setBusy(true);
    setError(null);
    setJobId(null);
    setJob(null);
    try {
      const r = await api.generate(spec);
      setProject(r);
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(false);
    }
  }, []);

  const startBuild = useCallback(async () => {
    if (!project) return;
    setError(null);
    setJob(null);
    try {
      const j = await api.startBuild(project.project.project_id, project.project.architectures);
      setJobId(j.job_id);
    } catch (e) {
      setError((e as Error).message);
    }
  }, [project]);

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
      <div className="space-y-6">
        <p className="text-sm text-slate-600 dark:text-slate-400">
          Describe the app you want and we&apos;ll generate a runnable Flutter
          project. Tick the architectures you need; the build worker will
          target them when packaging the APK.
        </p>
        <IdeaForm busy={busy} onSubmit={generate} />
        {error ? (
          <div className="border border-red-300 bg-red-50 dark:bg-red-950/40 text-red-800 dark:text-red-200 text-sm rounded-md p-3">
            {error}
          </div>
        ) : null}
        {health ? (
          <p className="text-xs text-slate-500">
            backend ok · codegen=<code>{health.codegen_provider}</code> · builder=<code>{health.builder_provider}</code>
          </p>
        ) : (
          <p className="text-xs text-amber-600">backend unreachable</p>
        )}
      </div>

      <div className="space-y-6">
        {project ? (
          <>
            <CodePreview project={project.project} fileTree={project.file_tree} />
            <div className="flex items-center gap-3">
              <button
                type="button"
                onClick={startBuild}
                disabled={!!jobId && (job?.state === "queued" || job?.state === "running")}
                className="px-4 py-2 rounded-md bg-emerald-600 text-white text-sm font-medium hover:bg-emerald-700 disabled:opacity-60"
              >
                Build APK
              </button>
              <span className="text-xs text-slate-500">
                project <code>{project.project.project_id}</code>
              </span>
            </div>
            {jobId ? (
              <BuildStatus jobId={jobId} onTerminal={setJob} />
            ) : null}
            <DownloadCard project={project.project} job={job} />
          </>
        ) : (
          <div className="border border-dashed border-slate-300 dark:border-slate-700 rounded-md p-8 text-center text-sm text-slate-500">
            Your generated project will appear here.
          </div>
        )}
      </div>
    </div>
  );
}

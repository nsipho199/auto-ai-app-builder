"use client";

import { useEffect, useRef, useState } from "react";

import { api, type BuildJob } from "@/lib/api";

interface Props {
  jobId: string;
  onTerminal?: (job: BuildJob) => void;
}

export default function BuildStatus({ jobId, onTerminal }: Props) {
  const [job, setJob] = useState<BuildJob | null>(null);
  const [log, setLog] = useState<string>("");
  const calledTerminalFor = useRef<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    let timer: ReturnType<typeof setTimeout> | undefined;

    const tick = async () => {
      try {
        const j = await api.getStatus(jobId);
        if (cancelled) return;
        setJob(j);
        const l = await api.getLog(jobId);
        if (!cancelled) setLog(l.log);
        if (j.state === "succeeded" || j.state === "failed") {
          if (onTerminal && calledTerminalFor.current !== jobId) {
            calledTerminalFor.current = jobId;
            onTerminal(j);
          }
          return;
        }
      } catch (e) {
        if (!cancelled) setLog((prev) => `${prev}\n[client] poll error: ${(e as Error).message}`);
      }
      timer = setTimeout(tick, 800);
    };
    tick();

    return () => {
      cancelled = true;
      if (timer) clearTimeout(timer);
    };
  }, [jobId, onTerminal]);

  if (!job) return <p className="text-sm text-slate-500">Starting build…</p>;

  return (
    <section className="space-y-2">
      <div className="flex items-center gap-3">
        <StateBadge state={job.state} />
        <span className="text-xs text-slate-500">
          builder: <code>{job.builder}</code> · job <code>{job.job_id}</code>
        </span>
      </div>
      <pre className="code-pre max-h-72">{log || "(no log yet)"}</pre>
      {job.error ? (
        <p className="text-sm text-red-600">Error: {job.error}</p>
      ) : null}
    </section>
  );
}

function StateBadge({ state }: { state: BuildJob["state"] }) {
  const cls =
    state === "succeeded"
      ? "bg-green-100 text-green-800 dark:bg-green-900/40 dark:text-green-200"
      : state === "failed"
      ? "bg-red-100 text-red-800 dark:bg-red-900/40 dark:text-red-200"
      : state === "running"
      ? "bg-amber-100 text-amber-800 dark:bg-amber-900/40 dark:text-amber-200"
      : "bg-slate-100 text-slate-800 dark:bg-slate-800 dark:text-slate-200";
  return (
    <span className={`inline-flex px-2 py-0.5 text-xs font-medium rounded-full ${cls}`}>
      {state}
    </span>
  );
}

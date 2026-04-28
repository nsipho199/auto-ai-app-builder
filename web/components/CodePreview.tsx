"use client";

import { useEffect, useState } from "react";

import { api, type ProjectMeta } from "@/lib/api";

interface Props {
  project: ProjectMeta;
  fileTree: string[];
}

export default function CodePreview({ project, fileTree }: Props) {
  const [selected, setSelected] = useState<string>(
    fileTree.find((p) => p === "lib/main.dart") ?? fileTree[0] ?? "",
  );
  const [content, setContent] = useState<string>("");
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!selected) return;
    let cancelled = false;
    api
      .getFile(project.project_id, selected)
      .then((r) => {
        if (!cancelled) setContent(r.content);
      })
      .catch((e: unknown) => {
        if (!cancelled) setError((e as Error).message);
      });
    return () => {
      cancelled = true;
    };
  }, [project.project_id, selected]);

  return (
    <section className="space-y-2">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold">Generated project</h3>
        <span className="text-xs text-slate-500">
          archetype: <code>{project.archetype}</code> · {project.file_count} files
        </span>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-[220px_minmax(0,1fr)] gap-3">
        <ul className="border border-slate-200 dark:border-slate-800 rounded-md p-2 max-h-72 overflow-auto text-xs">
          {fileTree.map((p) => (
            <li key={p}>
              <button
                type="button"
                onClick={() => setSelected(p)}
                className={`w-full text-left px-2 py-1 rounded ${
                  p === selected ? "bg-blue-100 dark:bg-blue-900/40" : "hover:bg-slate-100 dark:hover:bg-slate-800"
                }`}
              >
                {p}
              </button>
            </li>
          ))}
        </ul>
        <pre className="code-pre min-h-[18rem] max-h-[28rem]">
          {error ? `error: ${error}` : content || "loading…"}
        </pre>
      </div>
    </section>
  );
}

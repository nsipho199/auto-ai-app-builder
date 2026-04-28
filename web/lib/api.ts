// Thin client around the FastAPI backend, accessed via the Next.js proxy
// route at /api/proxy/* (so we don't need CORS in dev).

export const API_BASE = "/api/proxy";

export type Architecture = "arm64-v8a" | "x86_64" | "armeabi-v7a";

export interface IdeaSpec {
  idea: string;
  app_name?: string | null;
  architectures: Architecture[];
  primary_color?: string | null;
}

export interface ProjectMeta {
  project_id: string;
  archetype: string;
  idea: string;
  app_name: string;
  architectures: Architecture[];
  created_at: string;
  file_count: number;
}

export interface GenerateResponse {
  project: ProjectMeta;
  file_tree: string[];
}

export type BuildState = "queued" | "running" | "succeeded" | "failed";

export interface BuildJob {
  job_id: string;
  project_id: string;
  state: BuildState;
  builder: string;
  architectures: Architecture[];
  created_at: string;
  updated_at: string;
  artifact_url: string | null;
  log_excerpt: string;
  error: string | null;
}

export interface HealthResponse {
  status: "ok";
  codegen_provider: string;
  builder_provider: string;
}

async function jfetch<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers ?? {}),
    },
    cache: "no-store",
  });
  if (!res.ok) {
    const body = await res.text();
    throw new Error(`${res.status} ${res.statusText}: ${body}`);
  }
  return (await res.json()) as T;
}

export const api = {
  health: () => jfetch<HealthResponse>("/health"),
  generate: (spec: IdeaSpec) =>
    jfetch<GenerateResponse>("/generate", {
      method: "POST",
      body: JSON.stringify(spec),
    }),
  getProject: (id: string) => jfetch<GenerateResponse>(`/projects/${id}`),
  getFile: (id: string, path: string) =>
    jfetch<{ path: string; content: string }>(
      `/projects/${id}/files/${path.split("/").map(encodeURIComponent).join("/")}`,
    ),
  zipUrl: (id: string) => `${API_BASE}/projects/${id}/zip`,
  startBuild: (project_id: string, architectures?: Architecture[]) =>
    jfetch<BuildJob>("/build", {
      method: "POST",
      body: JSON.stringify({ project_id, architectures }),
    }),
  getStatus: (job_id: string) => jfetch<BuildJob>(`/status/${job_id}`),
  getLog: (job_id: string) =>
    jfetch<{ job_id: string; log: string }>(`/status/${job_id}/log`),
  downloadUrl: (job_id: string) => `${API_BASE}/download/${job_id}`,
};

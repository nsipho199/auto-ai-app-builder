# Architecture

## Components

### Frontend (`web/`)
- Next.js 14 App Router, TypeScript, Tailwind CSS.
- Single page (`app/page.tsx`) renders:
  - `<IdeaForm>` — textarea + voice-input stub.
  - `<ArchitectureCheckboxes>` — `arm64-v8a`, `x86_64`, `armeabi-v7a`.
  - `<CodePreview>` — file tree + monaco-style viewer for generated files.
  - `<BuildStatus>` — polled build job state with log lines.
  - `<DownloadCard>` — APK download link, QR code, and project-zip download.
- Talks to the backend via the proxy route at `/api/proxy/*`, which forwards
  to `process.env.BACKEND_URL` (default `http://localhost:8000`). This keeps
  CORS simple in dev and lets the backend stay private behind the web tier in
  prod.

### Backend (`server/`)
- FastAPI app with a thin layered structure:
  - `app/api/` — HTTP routes.
  - `app/codegen/` — code generation strategies behind a `CodeGenerator` ABC.
  - `app/builder/` — APK build strategies behind a `Builder` ABC.
  - `app/storage.py` — filesystem-backed project + job store. Designed so the
    backing store can be swapped for S3/Postgres without touching routes.
- Endpoints:

  | Method | Path                          | Purpose                                  |
  |--------|-------------------------------|------------------------------------------|
  | POST   | `/generate`                   | Generate a Flutter project from an idea  |
  | GET    | `/projects/{project_id}`      | Project metadata + file tree             |
  | GET    | `/projects/{project_id}/files/{path}` | Read a single file from the project |
  | GET    | `/projects/{project_id}/zip`  | Download the whole project as a zip      |
  | POST   | `/build`                      | Kick off an APK build for a project      |
  | GET    | `/status/{job_id}`            | Build job status + log lines             |
  | GET    | `/download/{job_id}`          | Download the produced APK                |
  | GET    | `/health`                     | Liveness                                 |

### Code generation
`CodeGenerator.generate(IdeaSpec) -> ProjectFiles`.

- **`TemplatedGenerator`** — keyword-routes the idea text into one of a small
  set of archetypes (`default`, `notes`, `translator`, `calculator`) and fills
  in placeholders (app name, primary color, sample data). Always available;
  zero external dependencies.
- **`AnthropicGenerator`** — sends a structured prompt to Claude and parses
  back a `ProjectFiles` JSON. Activated when `ANTHROPIC_API_KEY` is set or
  `CODEGEN_PROVIDER=anthropic`. Falls back to templated on any error.

Both generators emit a complete Flutter project rooted at the project id, so
downstream builders don't care which one ran.

### APK build
`Builder.build(ProjectFiles, BuildSpec) -> BuildJob` (async, with status
streaming via the job store).

- **`StubBuilder`** — writes a placeholder `.apk` file containing the project
  zip with an `.apk` extension. Lets the end-to-end flow be exercised without
  a 3GB Android toolchain; clearly labelled in the UI as "stub build".
- **`DockerFlutterBuilder`** — runs `cirrusci/flutter:stable` against the
  generated project (`flutter pub get && flutter build apk --release
  --target-platform <archs>`). Streams logs back into the job store. Requires
  Docker on the host; auto-detected at startup.
- **`CodemagicBuilder`** *(planned)* — pushes the generated project to a
  branch, triggers a Codemagic build via the
  [Codemagic API](https://docs.codemagic.io/rest-api/), returns the artifact
  URL. The repo's existing `codemagic.yaml` is the reference workflow.

## Data flow

1. User submits idea + archs → `POST /generate`.
2. Server picks a `CodeGenerator`, materialises files into
   `${DATA_DIR}/projects/{project_id}/`, returns metadata.
3. UI renders the file tree and offers **Download zip** /
   **Build APK**.
4. **Build APK** → `POST /build` → server enqueues a job, picks a `Builder`,
   streams status to `${DATA_DIR}/jobs/{job_id}/status.json` + `log.txt`.
5. UI polls `GET /status/{job_id}`; on success it renders the download card
   pointing at `GET /download/{job_id}`.

## Persistence

For the MVP, everything is on local disk under `DATA_DIR` (default
`server/_data/`). The directory layout is:

```
_data/
├── projects/
│   └── <project_id>/
│       ├── meta.json
│       └── files/...        (full Flutter project)
└── jobs/
    └── <job_id>/
        ├── meta.json
        ├── status.json
        ├── log.txt
        └── artifact.apk     (when done)
```

This is intentionally trivial to swap for an object store + database in
production — every read/write goes through `app/storage.py`.

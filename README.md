# Auto AI App Builder

Cloud-powered AI app builder that transforms a written idea into a downloadable
Flutter project (and, optionally, a built Android APK). This repo contains the
MVP of the system described in the project vision: a web UI, a code-generation
backend, a build worker, and a starter Flutter template that the existing
[Codemagic](./codemagic.yaml) pipeline can compile.

> **Status:** MVP. The core idea-to-project path works end-to-end with templated
> code generation. LLM-driven generation (Claude) and Docker-based local APK
> builds are wired in as optional, swappable backends.

## Architecture

```
┌─────────────┐   idea text +   ┌─────────────┐   project files    ┌──────────────┐
│  web (UI)   │ ───arch flags─▶ │  server     │ ───zip / commit──▶ │ build worker │
│  Next.js    │                 │  FastAPI    │                    │ docker/      │
│             │ ◀──artifacts─── │             │ ◀────APK / logs─── │ codemagic    │
└─────────────┘                 └─────────────┘                    └──────────────┘
                                       │
                                       ▼
                                ┌──────────────┐
                                │  CodeGenerator │
                                │  (templated /  │
                                │   anthropic)   │
                                └──────────────┘
```

- **`web/`** — Next.js 14 app with the idea input form, architecture
  checkboxes, generated-code preview, build log stream, and APK download / QR
  share card.
- **`server/`** — FastAPI service exposing `/generate`, `/projects/{id}`,
  `/build`, `/status/{job_id}`, and `/download/{job_id}` (see
  [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md)).
- **`server/app/codegen/`** — `CodeGenerator` interface plus a
  `TemplatedGenerator` (default, no API keys required) and an
  `AnthropicGenerator` (used automatically when `ANTHROPIC_API_KEY` is set).
- **`server/app/builder/`** — Pluggable builders. `StubBuilder` produces a
  placeholder artifact for fast iteration; `DockerFlutterBuilder` runs Flutter
  inside `cirrusci/flutter:stable` to produce a real APK.
- **Root Flutter starter** (`pubspec.yaml`, `lib/`, `codemagic.yaml`) — kept as
  the default template that the generator forks per idea, and as the reference
  Codemagic workflow for production builds.

## Quick start (development)

Requirements: Python 3.11+, Node 20+, Docker (only for real APK builds).

```bash
# 1. Backend
cd server
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
uvicorn app.main:app --reload --port 8000

# 2. Frontend (separate shell)
cd web
npm install
npm run dev   # http://localhost:3000
```

Open http://localhost:3000, type an idea ("a Siswati ↔ English translator"),
tick the architectures you want APKs for, hit **Generate**. You'll see the
generated Flutter project, can download it as a zip, and trigger an APK build.

## Configuration

Environment variables (see `server/app/settings.py`):

| Variable                | Purpose                                                  | Default      |
|-------------------------|----------------------------------------------------------|--------------|
| `ANTHROPIC_API_KEY`     | If set, Claude is used for code generation.              | unset        |
| `CODEGEN_PROVIDER`      | Force a provider: `templated` \| `anthropic`.            | auto-detect  |
| `BUILDER_PROVIDER`      | `stub` \| `docker` \| `codemagic`.                        | `stub`       |
| `DATA_DIR`              | Where generated projects + APKs are stored.              | `./_data`    |

## Roadmap

See [`docs/ROADMAP.md`](docs/ROADMAP.md) for what's deferred from the original
vision (real-time multi-user collab, voice input, marketplace, GDPR tooling,
auto-updates) and how the MVP is structured to absorb them.

## License

See [LICENSE](LICENSE) (TBD).

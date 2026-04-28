# Roadmap

The MVP intentionally ships a small slice of the original vision. This file
tracks what is **done**, **in-progress**, and **deferred**, plus where each
piece slots into the current architecture.

## Done (MVP)

- [x] Idea-to-project pipeline with a pluggable `CodeGenerator` interface.
- [x] `TemplatedGenerator` with archetypes: `default`, `notes`, `translator`,
      `calculator`.
- [x] `AnthropicGenerator` (Claude) — used automatically when
      `ANTHROPIC_API_KEY` is set.
- [x] FastAPI backend (`/generate`, `/projects`, `/build`, `/status`,
      `/download`).
- [x] Next.js frontend with idea input, architecture checkboxes, file
      preview, build status, and APK / zip download.
- [x] `StubBuilder` (no Android toolchain required) and
      `DockerFlutterBuilder` (real APK via `cirrusci/flutter:stable`).
- [x] End-to-end download of generated project as a zip.
- [x] Architecture targeting (`arm64-v8a`, `x86_64`, `armeabi-v7a`) plumbed
      through to `flutter build apk --target-platform`.
- [x] CI: lint + typecheck + tests on every PR.

## In progress

- [ ] `CodemagicBuilder` — push generated project to a branch and trigger a
      Codemagic build via the REST API. Will reuse the existing
      `codemagic.yaml` workflow.
- [ ] More archetypes: flashlight, MoMo agent system, community scheduler.
- [ ] Better archetype routing (intent classifier instead of keyword regex).

## Deferred (intentionally out of MVP)

The original vision lists these — they are valuable but each is a multi-week
project on its own. Each item below has a clean extension point in the
current architecture.

- **Real-time multi-user collaboration.** Where it slots in: a Yjs/Liveblocks
  document layered over the project file tree, plus a websocket route on the
  server. The `/projects/{id}` endpoints already model the project as the
  unit of collaboration.
- **Voice input.** A `<VoiceInput>` component that hits OpenAI Whisper or
  browser `SpeechRecognition` and feeds the transcript into `<IdeaForm>`. No
  backend changes needed.
- **Marketplace / template sharing.** A `templates` resource alongside
  `projects`, plus a "Publish to GitHub/GitLab" action that uses an OAuth
  token to fork the project into the user's account.
- **Multi-language / localisation.** The archetype templates already include
  Siswati, Zulu, and Swahili strings as a starting point. Production
  localisation would feed the generated `lib/l10n/` ARB files through a
  translation provider.
- **Security & compliance (GDPR/CCPA).** Per-project data retention policies,
  audit logs, and a "delete my data" endpoint. The storage layer is the
  natural place to enforce this — every read/write already goes through
  `app/storage.py`.
- **AI-optimized performance refinement & auto-updates.** A post-generation
  pass that runs `dart fix` / `flutter analyze` and surfaces suggestions, plus
  a periodic job that bumps SDK versions in the archetype templates.
- **Auto-updates of generated apps.** Out of scope until distribution is
  solved (GitHub releases / Firebase App Distribution / Play Internal
  Testing).

## Non-goals (for the foreseeable future)

- iOS builds. The repo and the original vision are Android-first.
- Hosting user-uploaded build artifacts long-term — APKs are short-lived
  artifacts in the MVP and will be GC'd.

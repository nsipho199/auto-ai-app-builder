# Codemagic integration

The repo ships a minimal [`codemagic.yaml`](../codemagic.yaml) at the root.
It is the reference Flutter-APK workflow that the future
`CodemagicBuilder` (see [ROADMAP.md](ROADMAP.md)) will trigger per generated
project.

## How it currently works

The default workflow runs on every push to `main`:

```yaml
workflows:
  default-workflow:
    name: Default Workflow
    environment:
      flutter: stable
    scripts:
      - name: Build APK
        script: |
          flutter pub get
          flutter build apk --release
    artifacts:
      - build/app/outputs/flutter-apk/app-release.apk
```

This builds the **root** Flutter starter (the `lib/main.dart` placeholder).

## How the production flow will work

1. User generates a project in the web UI → server materialises it under
   `_data/projects/{id}/`.
2. Server commits the project to a branch named `gen/{id}` on this repo.
3. Server calls Codemagic's [Build REST API][build-api] with that branch and a
   workflow id, optionally overriding `--target-platform` based on the
   architecture checkboxes the user ticked.
4. Server polls Codemagic's build status; on success, downloads the APK
   artifact and exposes it via `GET /download/{job_id}`.

[build-api]: https://docs.codemagic.io/rest-api/builds/

## Why we keep the local docker builder too

`DockerFlutterBuilder` exists so the project is fully usable without any
Codemagic credentials — it just needs Docker. Codemagic is the production
path; Docker is the dev-loop path.

"""Anthropic Claude-backed code generator.

Activated when ANTHROPIC_API_KEY is set or CODEGEN_PROVIDER=anthropic. Asks
Claude for a JSON list of files for a Flutter project, validates it, and
falls back to the templated generator on any error.
"""

from __future__ import annotations

import json
import logging

from ..models import GeneratedFile, IdeaSpec, ProjectFiles
from ..settings import settings
from .base import CodeGenerator
from .templated import TemplatedGenerator

log = logging.getLogger(__name__)

_PROMPT = """You are a senior Flutter engineer. Given an app idea, produce a small,
runnable Flutter project (Flutter SDK >=3.0).

Hard rules:
- Output ONLY a JSON object matching this schema, no prose, no code fences:
  {{"archetype": "<short-id>", "files": [{{"path": "...", "content": "..."}}]}}
- Required files: pubspec.yaml, lib/main.dart, README.md, .gitignore.
- pubspec.yaml MUST declare: name, description, environment.sdk, dependencies.flutter, dev_dependencies.flutter_test.
- The app must compile with `flutter pub get && flutter build apk --release`.
- Use only packages from the Flutter SDK + cupertino_icons + flutter_lints.
- Keep total source <= 400 lines.

App idea:
{idea}

App name (optional): {app_name}
Primary color (hex, optional): {primary_color}
"""


class AnthropicGenerator(CodeGenerator):
    name = "anthropic"

    def __init__(self) -> None:
        if not settings.anthropic_api_key:
            raise RuntimeError("ANTHROPIC_API_KEY is not set")
        try:
            import anthropic  # noqa: F401  -- imported lazily to avoid hard dep
        except ImportError as e:
            raise RuntimeError(
                "anthropic package not installed; install with `pip install anthropic`"
            ) from e
        self._fallback = TemplatedGenerator()

    def generate(self, spec: IdeaSpec) -> ProjectFiles:
        try:
            return self._generate_inner(spec)
        except Exception as e:
            log.warning("AnthropicGenerator failed, falling back to templated: %s", e)
            return self._fallback.generate(spec)

    def _generate_inner(self, spec: IdeaSpec) -> ProjectFiles:
        # Imports are lazy because anthropic is an optional dependency.
        import anthropic
        from anthropic.types import TextBlock

        client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
        prompt = _PROMPT.format(
            idea=spec.idea,
            app_name=spec.app_name or "(unset)",
            primary_color=spec.primary_color or "(unset)",
        )
        msg = client.messages.create(
            model=settings.anthropic_model,
            max_tokens=4000,
            messages=[{"role": "user", "content": prompt}],
        )
        text = "".join(
            block.text for block in msg.content if isinstance(block, TextBlock)
        )
        # Strip code fences if Claude added them despite the instructions.
        text = text.strip()
        if text.startswith("```"):
            text = text.strip("`")
            if text.lower().startswith("json"):
                text = text[4:]
            text = text.strip()
        data = json.loads(text)
        files = [
            GeneratedFile(path=f["path"], content=f["content"])
            for f in data.get("files", [])
        ]
        if not files:
            raise ValueError("Claude returned no files")
        archetype = str(data.get("archetype") or "anthropic")
        return ProjectFiles(archetype=archetype, files=files)

from __future__ import annotations

from pathlib import Path
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

CodegenProvider = Literal["auto", "templated", "anthropic"]
BuilderProvider = Literal["stub", "docker", "codemagic"]


class Settings(BaseSettings):
    """Process-wide settings, populated from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    data_dir: Path = Field(default=Path("./_data"))
    codegen_provider: CodegenProvider = Field(default="auto")
    builder_provider: BuilderProvider = Field(default="stub")

    anthropic_api_key: str | None = Field(default=None)
    anthropic_model: str = Field(default="claude-3-5-sonnet-latest")

    docker_flutter_image: str = Field(default="cirrusci/flutter:stable")

    cors_allow_origins: list[str] = Field(default_factory=lambda: ["*"])

    def resolve_codegen(self) -> Literal["templated", "anthropic"]:
        """Pick a concrete codegen provider given current config."""
        if self.codegen_provider == "anthropic":
            return "anthropic"
        if self.codegen_provider == "templated":
            return "templated"
        return "anthropic" if self.anthropic_api_key else "templated"


settings = Settings()

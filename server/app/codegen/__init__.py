from .anthropic import AnthropicGenerator
from .base import CodeGenerator
from .templated import TemplatedGenerator

__all__ = ["CodeGenerator", "TemplatedGenerator", "AnthropicGenerator", "get_generator"]


def get_generator(provider: str) -> CodeGenerator:
    """Return a concrete generator. Falls back to templated on any error."""
    if provider == "anthropic":
        try:
            return AnthropicGenerator()
        except Exception:  # pragma: no cover - defensive
            return TemplatedGenerator()
    return TemplatedGenerator()

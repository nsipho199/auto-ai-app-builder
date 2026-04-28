from .base import Builder
from .docker_flutter import DockerFlutterBuilder
from .stub import StubBuilder

__all__ = ["Builder", "StubBuilder", "DockerFlutterBuilder", "get_builder"]


def get_builder(provider: str) -> Builder:
    if provider == "docker":
        return DockerFlutterBuilder()
    return StubBuilder()

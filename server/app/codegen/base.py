from __future__ import annotations

from abc import ABC, abstractmethod

from ..models import IdeaSpec, ProjectFiles


class CodeGenerator(ABC):
    """Strategy interface for turning an IdeaSpec into a Flutter ProjectFiles."""

    name: str = "base"

    @abstractmethod
    def generate(self, spec: IdeaSpec) -> ProjectFiles: ...

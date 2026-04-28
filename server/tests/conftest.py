from __future__ import annotations

import os
import tempfile
from collections.abc import Iterator
from pathlib import Path

import pytest

# Use a fresh DATA_DIR per test session so we don't pollute the dev tree.
_TMP = Path(tempfile.mkdtemp(prefix="autoai-test-"))
os.environ["DATA_DIR"] = str(_TMP)
os.environ.setdefault("CODEGEN_PROVIDER", "templated")
os.environ.setdefault("BUILDER_PROVIDER", "stub")


@pytest.fixture(scope="session")
def data_dir() -> Iterator[Path]:
    yield _TMP

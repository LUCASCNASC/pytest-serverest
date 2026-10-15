import ast
import json
import os
from collections.abc import Iterator
from pathlib import Path
from typing import Any

import pytest
import requests


@pytest.fixture(scope="session")
def base_url() -> str:
    return os.getenv("SERVEREST_BASE_URL", "https://serverest.dev").rstrip("/")


@pytest.fixture
def api() -> Iterator[requests.Session]:
    session = requests.Session()
    session.headers.update({"Accept": "application/json"})
    yield session
    session.close()


@pytest.fixture(scope="session")
def openapi_spec() -> dict[str, Any]:
    spec_path = Path(__file__).resolve().parents[1] / "serverest.json"
    return json.loads(spec_path.read_text(encoding="utf-8"))


@pytest.fixture(scope="session")
def api_route_coverage() -> set[tuple[str, str, int]]:
    tests_dir = Path(__file__).resolve().parent
    coverage: set[tuple[str, str, int]] = set()
    for test_file in tests_dir.glob("test_*.py"):
        module = ast.parse(test_file.read_text(encoding="utf-8"))
        for node in ast.walk(module):
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            if not node.name.startswith("test_"):
                continue
            for decorator in node.decorator_list:
                if not isinstance(decorator, ast.Call):
                    continue
                if ast.unparse(decorator.func) != "pytest.mark.api_coverage":
                    continue
                marker = {
                    keyword.arg: ast.literal_eval(keyword.value)
                    for keyword in decorator.keywords
                    if keyword.arg is not None
                }
                coverage.update(
                    (marker["method"].upper(), marker["path"], int(status))
                    for status in marker["statuses"]
                )
    return coverage

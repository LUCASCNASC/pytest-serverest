import os
from collections.abc import Iterator

import pytest
import requests


@pytest.fixture(scope="session")
def base_url() -> str:
    return os.getenv("SERVEREST_BASE_URL", "https://serverest.dev").rstrip("/")


@pytest.fixture
def api(base_url: str) -> Iterator[requests.Session]:
    session = requests.Session()
    session.headers.update({"Accept": "application/json"})
    yield session
    session.close()

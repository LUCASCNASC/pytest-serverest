import json
from pathlib import Path
from typing import Any


SPEC_PATH = Path(__file__).resolve().parents[1] / "serverest.json"


def load_spec() -> dict[str, Any]:
    return json.loads(SPEC_PATH.read_text(encoding="utf-8"))


def test_openapi_document_has_expected_identity() -> None:
    spec = load_spec()

    assert spec["openapi"].startswith("3.")
    assert spec["info"]["title"] == "ServeRest"
    assert spec["info"]["version"]
    assert spec["servers"][0]["url"] == "https://serverest.dev"


def test_all_local_references_resolve() -> None:
    spec = load_spec()
    references: list[str] = []

    def collect_references(value: Any) -> None:
        if isinstance(value, dict):
            if "$ref" in value:
                references.append(value["$ref"])
            for nested_value in value.values():
                collect_references(nested_value)
        elif isinstance(value, list):
            for nested_value in value:
                collect_references(nested_value)

    collect_references(spec)
    assert references

    for reference in references:
        assert reference.startswith("#/"), f"Unsupported external ref: {reference}"
        target: Any = spec
        for part in reference[2:].split("/"):
            part = part.replace("~1", "/").replace("~0", "~")
            target = target[int(part)] if isinstance(target, list) else target[part]


def test_spec_documents_core_routes_and_operations() -> None:
    paths = load_spec()["paths"]
    expected = {
        "/login": {"post"},
        "/usuarios": {"get", "post"},
        "/usuarios/{_id}": {"get", "put", "delete"},
        "/produtos": {"get", "post"},
        "/produtos/{_id}": {"get", "put", "delete"},
        "/carrinhos": {"get", "post"},
        "/carrinhos/{_id}": {"get"},
        "/carrinhos/concluir-compra": {"delete"},
        "/carrinhos/cancelar-compra": {"delete"},
    }

    for path, operations in expected.items():
        assert operations <= set(paths[path])

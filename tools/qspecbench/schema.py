"""Load and expose the QSpecBench JSON schema."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

from jsonschema import Draft202012Validator
from referencing import Registry, Resource

REPO_ROOT = Path(__file__).resolve().parents[2]
SCHEMA_DIR = REPO_ROOT / "schema"
SCHEMA_PATH = SCHEMA_DIR / "qspecbench.schema.json"
SEMANTIC_BRIDGE_SCHEMA_PATH = SCHEMA_DIR / "semantic_bridge.schema.json"


def _schema_resource(uri: str) -> Resource:
    name = uri.rsplit("/", 1)[-1]
    path = SCHEMA_DIR / name
    if not path.is_file():
        raise FileNotFoundError(f"schema resource not found: {uri}")
    return Resource.from_contents(json.loads(path.read_text(encoding="utf-8")))


@lru_cache(maxsize=1)
def _schema_registry() -> Registry:
    return (
        Registry()
        .with_resource(
            "https://qspecbench.org/schema/qspecbench.schema.json",
            _schema_resource("https://qspecbench.org/schema/qspecbench.schema.json"),
        )
        .with_resource(
            "https://qspecbench.org/schema/semantic_bridge.schema.json",
            _schema_resource("https://qspecbench.org/schema/semantic_bridge.schema.json"),
        )
    )


@lru_cache(maxsize=1)
def load_schema() -> dict:
    with SCHEMA_PATH.open(encoding="utf-8") as f:
        return json.load(f)


@lru_cache(maxsize=1)
def load_semantic_bridge_schema() -> dict:
    with SEMANTIC_BRIDGE_SCHEMA_PATH.open(encoding="utf-8") as f:
        return json.load(f)


@lru_cache(maxsize=1)
def spec_validator() -> Draft202012Validator:
    return Draft202012Validator(load_schema(), registry=_schema_registry())


def validate_spec_schema(spec: dict) -> None:
    """Validate a spec dict against qspecbench.schema.json (resolves external $ref)."""
    spec_validator().validate(spec)


def schema_path() -> Path:
    return SCHEMA_PATH

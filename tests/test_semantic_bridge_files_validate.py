"""Validate optional semantic bridge JSON artifacts."""

import json
from pathlib import Path

import jsonschema

REPO = Path(__file__).resolve().parents[1]
BRIDGE_SCHEMA = json.loads(
    (REPO / "schema" / "semantic_bridge.schema.json").read_text(encoding="utf-8")
)


def test_semantic_bridge_schema_loads():
    assert BRIDGE_SCHEMA["required"]


def test_semantic_bridge_files_validate():
    bridges = list((REPO / "benchmarks").rglob("expected/semantic_bridge.json"))
    for path in bridges:
        data = json.loads(path.read_text(encoding="utf-8"))
        jsonschema.validate(data, BRIDGE_SCHEMA)

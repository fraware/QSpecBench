"""Repository-level semantic-profile registry integrity checks."""

from __future__ import annotations

from pathlib import Path

import yaml

from qspecbench.schema import REPO_ROOT
from qspecbench.semantic_profiles import all_registered_profile_ids, load_registered_profile


def _graph_profile_id(graph_path: Path) -> str | None:
    payload = yaml.safe_load(graph_path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        return None
    value = ((payload.get("semantic_profile") or {}).get("id") or "").strip()
    return value or None


def test_registered_profile_filenames_and_ids_are_bijective() -> None:
    ids = all_registered_profile_ids()
    assert ids
    for profile_id in ids:
        profile = load_registered_profile(profile_id)
        assert profile["id"] == profile_id


def test_all_corpus_semantic_profile_identifiers_resolve() -> None:
    benchmark_root = REPO_ROOT / "benchmarks"
    resolved: set[str] = set()

    for spec_path in benchmark_root.rglob("spec.yaml"):
        spec = yaml.safe_load(spec_path.read_text(encoding="utf-8"))
        if not isinstance(spec, dict):
            continue
        profile_id = spec.get("openqasm_profile")
        if profile_id:
            load_registered_profile(str(profile_id))
            resolved.add(str(profile_id))

        graph_path = spec_path.parent / "assurance_graph.yaml"
        if graph_path.is_file():
            graph_profile_id = _graph_profile_id(graph_path)
            if graph_profile_id:
                load_registered_profile(graph_profile_id)
                resolved.add(graph_profile_id)

    assert resolved, "expected at least one semantic-profile identifier in benchmark corpus"

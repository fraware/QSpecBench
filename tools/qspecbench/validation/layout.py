"""Layout, id, track, README, and specification-shape checks."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from qspecbench.artifacts import (
    claim_path_escape_error,
    resolve_claim_path,
    track_for_claim,
)

SNAKE_CASE = re.compile(r"^[a-z][a-z0-9_]*$")


def validate_layout_rules(
    spec: dict[str, Any], claim_dir: Path, benchmarks_root: Path
) -> list[str]:
    errors: list[str] = []
    claim_id = spec.get("id", "")
    if not SNAKE_CASE.match(claim_id):
        errors.append(f"id must be lowercase snake_case: {claim_id}")
    if claim_dir.name != claim_id:
        errors.append(f"id {claim_id} must match directory name {claim_dir.name}")

    track = track_for_claim(claim_dir, benchmarks_root)
    track_map = {
        "algorithms": "algorithm",
        "equivalence": "equivalence",
        "qec": "qec",
        "hamiltonian": "hamiltonian",
        "ai_formalization": "ai_formalization",
    }
    expected_track = track_map.get(track)
    if expected_track and spec.get("track") != expected_track:
        errors.append(f"track {spec.get('track')} must match parent directory {track}")

    if not (claim_dir / "README.md").is_file():
        errors.append("missing README.md claim card")

    spec_block = spec.get("specification", {})
    pre = spec_block.get("preconditions", [])
    post = spec_block.get("postconditions", [])
    if not pre and not post:
        errors.append("must declare at least one precondition or postcondition")

    mode = spec_block.get("mode")
    approx = spec_block.get("approximation", {})
    if mode == "approximate" and not approx.get("enabled"):
        errors.append("approximate mode requires approximation.enabled true")
    if approx.get("enabled"):
        if not approx.get("metric"):
            errors.append("approximation.enabled requires metric")
        if not approx.get("bound"):
            errors.append("approximation.enabled requires bound")

    resources = spec_block.get("resources", {})
    if resources.get("enabled"):
        keys = ("qubits", "gates", "depth", "t_count", "t_depth", "ancilla", "measurements")
        if not any(resources.get(k) for k in keys) and not resources.get("other"):
            errors.append("resources.enabled requires at least one resource field")

    for obj in spec.get("objects", []):
        path = obj.get("path")
        if not path:
            continue
        escape_err = claim_path_escape_error(claim_dir, path)
        if escape_err:
            errors.append(escape_err)
        elif not resolve_claim_path(claim_dir, path).is_file():
            errors.append(f"missing object file: {path}")

    if spec.get("status", {}).get("maturity") == "deprecated":
        readme = (
            (claim_dir / "README.md").read_text(encoding="utf-8")
            if (claim_dir / "README.md").is_file()
            else ""
        )
        if "deprecat" not in readme.lower():
            errors.append("deprecated benchmark README must explain deprecation")
    return errors

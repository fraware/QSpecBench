"""Semantic bridge verification: QASM matrix vs OpenQASM3 denotation model."""

from __future__ import annotations

import json
from fractions import Fraction
from pathlib import Path
from typing import Any

from qspecbench.denotate import matrices_equal, ops_from_qasm_matrix
from qspecbench.qasm_matrix import extract_matrix


def _find_qasm_artifact(claim_dir: Path, bridge: dict[str, Any] | None = None) -> Path | None:
    if bridge:
        bridge_rel = bridge.get("qasm_artifact")
        if bridge_rel:
            candidate = claim_dir / bridge_rel
            if candidate.is_file():
                return candidate
    spec = _load_spec(claim_dir)
    for obj in spec.get("objects", []):
        if obj.get("format") == "qasm3" and obj.get("role") == "source" and obj.get("path"):
            candidate = claim_dir / obj["path"]
            if candidate.is_file():
                return candidate
    for obj in spec.get("objects", []):
        if obj.get("format") == "qasm3" and obj.get("path"):
            candidate = claim_dir / obj["path"]
            if candidate.is_file():
                return candidate
    artifacts = claim_dir / "artifacts"
    if artifacts.is_dir():
        for name in ("source.qasm", "circuit.qasm", "teleportation.qasm"):
            p = artifacts / name
            if p.is_file():
                return p
    return None


def _load_spec(claim_dir: Path) -> dict[str, Any]:
    import yaml

    return yaml.safe_load((claim_dir / "spec.yaml").read_text(encoding="utf-8"))


def _load_bridge(claim_dir: Path) -> dict[str, Any]:
    bridge_path = claim_dir / "expected" / "semantic_bridge.json"
    if not bridge_path.is_file():
        raise FileNotFoundError(f"missing semantic bridge: {bridge_path}")
    return json.loads(bridge_path.read_text(encoding="utf-8"))


def verify_bridge(claim_dir: Path) -> dict[str, Any]:
    claim_dir = claim_dir.resolve()
    bridge = _load_bridge(claim_dir)
    qasm = _find_qasm_artifact(claim_dir, bridge)
    if qasm is None:
        return {
            "ok": False,
            "claim": claim_dir.name,
            "claimed_link": bridge.get("claimed_link"),
            "errors": ["no qasm3 artifact found"],
        }

    qasm_data = extract_matrix(qasm)
    n = qasm_data["n_qubits"]
    ops = ops_from_qasm_matrix(qasm_data)
    from qspecbench.denotate import denotate_ops

    denoted = denotate_ops(n, ops)
    qasm_mat = [
        [Fraction(cell[0], cell[1]) for cell in row] for row in qasm_data["matrix"]
    ]
    match = matrices_equal(qasm_mat, denoted)

    result = {
        "ok": match,
        "claim": claim_dir.name,
        "claimed_link": bridge.get("claimed_link"),
        "lean_module": bridge.get("lean_module"),
        "lean_theorem": bridge.get("lean_theorem"),
        "qasm": str(qasm),
        "n_qubits": n,
        "gates": len(ops),
        "matrix_match": match,
        "errors": [] if match else ["QASM matrix differs from OpenQASM3 denotation model"],
    }
    return result


def write_bridge_result(claim_dir: Path, out_path: Path | None = None) -> dict[str, Any]:
    result = verify_bridge(claim_dir)
    if out_path is None:
        out_path = claim_dir / "evidence" / "bridge_verify.result.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    return result

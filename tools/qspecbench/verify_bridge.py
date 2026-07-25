"""Semantic bridge verification: QASM matrix vs OpenQASM3 denotation model."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from qspecbench.bridge_codegen import is_dynamic_ast_checked_link
from qspecbench.denotate import (
    denotate_ops,
    matrix_from_qasm_json,
    ops_from_qasm_matrix,
)
from qspecbench.qasm_matrix import _line_skip_category, extract_matrix, matrices_equal


def _qasm_has_measure_or_classical_control(qasm_path: Path) -> bool:
    """True when on-disk QASM contains measure / if / while that matrix codegen drops."""
    text = qasm_path.read_text(encoding="utf-8")
    for raw in text.splitlines():
        cat = _line_skip_category(raw)
        if cat in {"measurement", "classical_control", "reset"}:
            return True
    return False


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
    spec = _load_spec(claim_dir)
    extraction = spec.get("qasm_extraction")
    claimed = bridge.get("claimed_link")
    qasm = _find_qasm_artifact(claim_dir, bridge)
    if qasm is None:
        return {
            "ok": False,
            "claim": claim_dir.name,
            "claimed_link": claimed,
            "errors": ["no qasm3 artifact found"],
        }

    # Fail-closed: matrix KERNEL_BRIDGE must not silently drop measure/if/reset.
    if _qasm_has_measure_or_classical_control(qasm) and not is_dynamic_ast_checked_link(
        claimed
    ):
        return {
            "ok": False,
            "claim": claim_dir.name,
            "claimed_link": claimed,
            "qasm": str(qasm),
            "matrix_match": False,
            "errors": [
                "matrix KERNEL_BRIDGE path refuses measure/if/reset QASM "
                "(would drop dynamics); use kernel_checked_dynamic_ast_semantics "
                "or kernel_checked_dynamic_denotation"
            ],
        }

    qasm_data = extract_matrix(qasm, extraction=extraction)
    n = qasm_data["n_qubits"]
    ops = ops_from_qasm_matrix(qasm_data)
    denoted = denotate_ops(n, ops)
    qasm_mat = matrix_from_qasm_json(qasm_data)
    match = matrices_equal(qasm_mat, denoted)

    result = {
        "ok": match,
        "claim": claim_dir.name,
        "claimed_link": claimed,
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

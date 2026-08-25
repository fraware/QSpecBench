#!/usr/bin/env python3
"""Qiskit Optimize1qGates compiler-provenance adapter."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

from qspecbench.qiskit_compiler import QiskitCompilerError, compile_hxx_with_optimize_1q_gates


def _claim_dir(provenance_path: Path) -> Path:
    """Provenance JSON lives at ``<claim>/artifacts/compiler_provenance.json``."""
    return provenance_path.resolve().parent.parent


def _resolve_qasm(provenance_path: Path, declared: object | None, default_name: str) -> Path:
    """Resolve claim-relative QASM paths against the claim root, not process cwd."""
    claim = _claim_dir(provenance_path)
    if declared:
        candidate = Path(str(declared))
        if candidate.is_absolute():
            return candidate
        return (claim / candidate).resolve()
    return (provenance_path.resolve().parent / default_name).resolve()


def main() -> int:
    if len(sys.argv) != 2:
        print(json.dumps({"ok": False, "error": "usage: parse_result.py <provenance.json>"}))
        return 1
    path = Path(sys.argv[1])
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}))
        return 1

    source = _resolve_qasm(path, payload.get("source_path"), "source.qasm")
    target = _resolve_qasm(path, payload.get("target_path"), "target.qasm")
    if not source.is_file() or not target.is_file():
        print(json.dumps({"ok": False, "error": "source/target QASM missing"}))
        return 1

    def digest(p: Path) -> str:
        return hashlib.sha256(p.read_bytes()).hexdigest()

    source_sha = digest(source)
    target_sha = digest(target)
    if source_sha != payload.get("source_sha256") or target_sha != payload.get("target_sha256"):
        print(json.dumps({"ok": False, "error": "committed QASM hashes do not match provenance"}))
        return 1

    regen = None
    try:
        regen = compile_hxx_with_optimize_1q_gates(source.read_text(encoding="utf-8"))
    except QiskitCompilerError:
        regen = None
    if regen is not None and regen.target_sha256 != target_sha:
        print(json.dumps({"ok": False, "error": "qiskit regeneration does not match committed target"}))
        return 1
    print(
        json.dumps(
            {
                "ok": True,
                "skipped": False,
                "adapter_id": "qspecbench.qiskit.optimize_1q_gates.v1",
                "compiler_id": payload.get("compiler_id"),
                "qiskit_version": payload.get("qiskit_version"),
                "regenerated": regen is not None,
                "target_sha256": target_sha,
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

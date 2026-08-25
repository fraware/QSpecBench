#!/usr/bin/env python3
"""Qiskit Optimize1qGates compiler-provenance adapter."""

from __future__ import annotations

import json
import sys
from pathlib import Path

from qspecbench.qiskit_compiler import QiskitCompilerError, compile_hxx_with_optimize_1q_gates


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

    source = Path(payload.get("source_path") or path.parent.parent / "artifacts" / "source.qasm")
    target = Path(payload.get("target_path") or path.parent.parent / "artifacts" / "target.qasm")
    if not source.is_file() or not target.is_file():
        print(json.dumps({"ok": False, "error": "source/target QASM missing"}))
        return 1
    import hashlib

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

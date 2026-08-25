#!/usr/bin/env python3
"""Re-run the reference compiler and byte-compare its output with the declared target."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

from qspecbench.reference_compiler import (
    COMPILER_ID,
    COMPILER_VERSION,
    ReferenceCompilerError,
    compile_qasm,
)

ADAPTER_ID = "qspecbench.compiler.peephole.v1"


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> int:
    if len(sys.argv) != 3:
        print(json.dumps({"ok": False, "error": "usage: parse_result.py <source.qasm> <target.qasm>"}))
        return 1
    source_path = Path(sys.argv[1]).resolve()
    target_path = Path(sys.argv[2]).resolve()
    if not source_path.is_file() or not target_path.is_file():
        print(json.dumps({"ok": False, "error": "source or target artifact missing"}))
        return 1

    source_bytes = source_path.read_bytes()
    target_bytes = target_path.read_bytes()
    try:
        source = source_bytes.decode("utf-8")
        target_bytes.decode("utf-8")
    except UnicodeDecodeError as exc:
        print(json.dumps({"ok": False, "error": f"artifacts must be UTF-8: {exc}"}))
        return 1

    try:
        result = compile_qasm(source)
    except ReferenceCompilerError as exc:
        print(json.dumps({"ok": False, "error": str(exc), "adapter_id": ADAPTER_ID}))
        return 1

    emitted = result.output.encode("utf-8")
    ok = emitted == target_bytes
    payload = {
        "ok": ok,
        "adapter_id": ADAPTER_ID,
        "adapter_version": "1.0.0",
        "compiler_id": COMPILER_ID,
        "compiler_version": COMPILER_VERSION,
        "source_sha256": _sha256(source_bytes),
        "declared_target_sha256": _sha256(target_bytes),
        "emitted_target_sha256": _sha256(emitted),
        "transformations": list(result.transformations),
        "supported_obligations": ["compiler_transformation_reproduced"],
        "not_supported_obligations": ["source_target_semantic_equivalence"],
    }
    if not ok:
        payload["error"] = "compiler-emitted bytes differ from declared target"
    print(json.dumps(payload, sort_keys=True))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())

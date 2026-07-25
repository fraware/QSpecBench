"""Extract bridge/qec functions from staged validate impl into validation modules."""

from __future__ import annotations

import ast
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SRC = REPO / "tools/qspecbench/validation/_impl.py"


def main() -> None:
    src = SRC.read_text(encoding="utf-8")
    tree = ast.parse(src)
    funcs = {n.name: n for n in tree.body if isinstance(n, ast.FunctionDef)}

    bridge_names = [
        "_load_semantic_bridge",
        "_has_qasm_objects",
        "_has_lean_evidence",
        "_has_passing_bridge_verify",
        "_validate_kernel_bridge_authority_warnings",
        "validate_semantic_bridge_rules",
        "_validate_artifact_bound_reference_claim",
        "_validate_wire_order",
        "_validate_reference_claim_bridge",
    ]
    qec_names = [
        "_infer_qec_witness_claim_kind",
        "_validate_qec_witness_file",
        "_validate_qec_claim_scope",
    ]

    def slice_func(name: str) -> str:
        return ast.get_source_segment(src, funcs[name]) or ""

    header_bridges = '''"""Semantic bridge and artifact-bound claim validation."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from qspecbench.bridge_codegen import (
    KERNEL_BRIDGE_IDS,
    KERNEL_CHECKED_LINK,
    LEGACY_KERNEL_CHECKED_LINK,
    AST_AUTHORITY_FIELD,
    AST_AUTHORITY_LEAN_MIRROR,
    is_kernel_checked_link,
    read_theorem_source_hash,
    theorem_source_statement_hash,
    verify_kernel_artifact_semantics_bridge,
    _elaborator_exported_types,
)
from qspecbench.bridge_manifest import validate_kernel_checked_bridge, validate_manifest_bridge
from qspecbench.models import ALL_REFERENCE_LEVELS, REFERENCE_CLAIM_LEVEL
from qspecbench.schema import REPO_ROOT
from qspecbench.verify_bridge import verify_bridge
from qspecbench.validation.qec import validate_qec_claim_scope

ARTIFACT_BOUND_LEVEL = "artifact_bound_reference_claim"

'''

    header_qec = '''"""QEC witness and claim-scope validation."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

'''

    # Fix bridges to call qec.validate_qec_claim_scope instead of _validate_qec_claim_scope
    bridge_body = "\n\n".join(slice_func(n) for n in bridge_names)
    bridge_body = bridge_body.replace(
        "errors.extend(_validate_qec_claim_scope(spec, claim_dir))",
        "errors.extend(validate_qec_claim_scope(spec, claim_dir))",
    )

    qec_body = "\n\n".join(slice_func(n) for n in qec_names)
    qec_body += """

infer_qec_witness_claim_kind = _infer_qec_witness_claim_kind
validate_qec_witness_file = _validate_qec_witness_file
validate_qec_claim_scope = _validate_qec_claim_scope
"""

    (REPO / "tools/qspecbench/validation/bridges.py").write_text(
        header_bridges + bridge_body + "\n", encoding="utf-8"
    )
    (REPO / "tools/qspecbench/validation/qec.py").write_text(
        header_qec + qec_body + "\n", encoding="utf-8"
    )
    print("ok")


if __name__ == "__main__":
    main()

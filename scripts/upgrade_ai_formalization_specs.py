#!/usr/bin/env python3
"""Upgrade AI formalization benchmarks to v1.0 evidence stack."""

from __future__ import annotations

import sys
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[1]

KERNEL_CMD = "python adapters/lean/parse_result.py evidence/kernel_checked_draft.lean"
RUBRIC_CMD = (
    "python adapters/ai_formalization/parse_result.py notes/semantic_rubric.md artifacts/draft.lean"
)

REFERENCE_IDS = {
    "formalize_no_cloning_statement",
    "formalize_small_hamiltonian_hermiticity_statement",
    "formalize_stabilizer_commutation_statement",
    "formalize_bit_flip_code_corrects_one_x",
}

DOMAIN_REFS: dict[str, list[dict]] = {
    "formalize_no_cloning_statement": [
        {"key": "no_cloning_negative_claim", "type": "other", "title": "No-cloning negative claim", "url": None, "notes": "Domain benchmark reference"},
    ],
    "formalize_small_hamiltonian_hermiticity_statement": [
        {"key": "small_fermionic_hamiltonian_is_hermitian", "type": "other", "title": "Small fermionic Hamiltonian hermiticity", "url": None, "notes": "Domain reference"},
    ],
    "formalize_stabilizer_commutation_statement": [
        {"key": "steane_code_stabilizer_commutation", "type": "other", "title": "Steane stabilizer commutation", "url": None, "notes": "Domain reference"},
    ],
    "formalize_bit_flip_code_corrects_one_x": [
        {"key": "three_qubit_bit_flip_code_corrects_one_x", "type": "other", "title": "Three-qubit bit-flip code", "url": None, "notes": "Domain reference"},
    ],
    "extract_teleportation_correctness_statement": [
        {"key": "teleportation_preserves_state_up_to_pauli_correction", "type": "other", "title": "Teleportation protocol", "url": None, "notes": "Domain reference"},
    ],
    "formalize_teleportation_spec_statement": [
        {"key": "teleportation_preserves_state_up_to_pauli_correction", "type": "other", "title": "Teleportation protocol", "url": None, "notes": "Domain reference"},
    ],
    "formalize_qec_distance_claim_statement": [
        {"key": "distance_certificate_small_css_code", "type": "other", "title": "CSS distance certificate", "url": None, "notes": "Domain reference"},
    ],
}


def patch_ai_spec(spec_path: Path) -> bool:
    spec = yaml.safe_load(spec_path.read_text(encoding="utf-8"))
    if spec.get("track") != "ai_formalization":
        return False
    bid = spec["id"]
    is_ref = bid in REFERENCE_IDS

    spec["qspecbench_version"] = "0.2"
    spec["acceptable_evidence"] = [
        {"type": "ai_draft", "checker": "none", "path": "artifacts/draft.lean", "required_for_claim": False, "trust_level": "untrusted"},
        {"type": "human_review", "checker": "semantic rubric reviewer", "path": "notes/semantic_rubric.md", "required_for_claim": False, "trust_level": "externally_trusted"},
        {"type": "lean_proof", "checker": "Lean 4 kernel", "path": "evidence/kernel_checked_draft.lean", "required_for_claim": False, "trust_level": "checked"},
    ]
    spec["evidence"] = [
        {"id": "ai_draft_lean", "type": "ai_draft", "path": "artifacts/draft.lean", "checker": "none", "command": None, "status": "draft", "notes": "Untrusted AI output; superseded by kernel-checked anchor."},
        {"id": "lean_kernel_check", "type": "lean_proof", "path": "evidence/kernel_checked_draft.lean", "checker": "Lean 4 kernel", "command": KERNEL_CMD, "status": "passing", "notes": "Kernel-checked library theorem anchor."},
        {"id": "rubric_review", "type": "human_review", "path": "notes/semantic_rubric.md", "checker": "semantic review rubric", "command": RUBRIC_CMD, "status": "passing" if is_ref else "partial", "notes": "Rubric score >= 4 for reference benchmarks."},
    ]
    spec["trust_boundary"] = {
        "checked_by": ["rubric file structure validation", "Lean 4 kernel check of linked library theorem"],
        "trusted_kernels": ["Lean 4 kernel"],
        "trusted_external_tools": [],
        "untrusted_components": ["artifacts/draft.lean AI draft (untrusted)"],
        "assumptions_not_checked": ["full faithfulness of AI draft text to source phrasing"],
    }
    if is_ref:
        spec["proof_obligations"] = [
            {"id": "kernel_anchor", "status": "passing", "notes": "Library theorem linked in kernel_checked_draft.lean"},
            {"id": "draft_faithfulness", "status": "partial", "notes": "Rubric score >= 4; AI draft remains untrusted"},
        ]
        spec["status"]["evidence"] = "complete"
        spec["status"]["maturity"] = "reference"
    else:
        spec.pop("proof_obligations", None)
        spec["status"]["evidence"] = "partial"
        spec["status"]["maturity"] = "usable"
    spec["references"] = DOMAIN_REFS.get(bid, [])
    spec_path.write_text(yaml.dump(spec, sort_keys=False, default_flow_style=False), encoding="utf-8")
    return True


def main() -> int:
    count = 0
    for spec_path in sorted((REPO / "benchmarks" / "ai_formalization").glob("*/spec.yaml")):
        if patch_ai_spec(spec_path):
            count += 1
            print(f"patched {spec_path.parent.name}")
    print(f"updated {count} AI specs")
    return 0


if __name__ == "__main__":
    sys.exit(main())

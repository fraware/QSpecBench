#!/usr/bin/env python3
"""One-shot P0 corpus migration: bridge taxonomy, Lean anchors, QEC scope, qasm_extraction."""

from __future__ import annotations

import json
import re
from pathlib import Path

import yaml

from qspecbench.bridge_manifest import compute_bridge_hashes, format_evidence_anchor, full_theorem_name

REPO = Path(__file__).resolve().parents[1]
BENCHMARKS = REPO / "benchmarks"

BRIDGE_LINK_MAP = {
    "kernel_checked": "manifest_checked_theorem_binding",
    "python_consistency_checked": "python_denotation_consistency",
}

MANIFEST_IDS = {
    "cnot_self_inverse_cancellation",
    "hadamard_conjugates_x_to_z",
    "single_qubit_gate_cancellation",
    "qft_inverse_qft_small_instance",
    "swap_from_three_cx",
    "toffoli_decomposition_equivalence",
    "circuit_identity_after_layout",
    "source_optimized_qasm_equivalence_small_instance",
    "bell_state_preparation",
    "clifford_simplification_preserves_unitary",
    "phase_polynomial_equivalence_small_instance",
}

REFERENCE_CLAIM_HEADLINE = {
    "checked_under": [
        "qspecbench.openqasm3.int_scaffold.v0",
        "finite_matrix_model",
    ],
    "not_checked_under": [
        "full_openqasm3",
        "hardware_semantics",
        "general_n_qubit_rule",
    ],
}

REFERENCE_CLAIM_COMPLEX = {
    "checked_under": [
        "qspecbench.openqasm3.complex_scaffold.v0",
        "finite_matrix_model",
    ],
    "not_checked_under": [
        "full_openqasm3",
        "hardware_semantics",
        "general_n_qubit_rule",
    ],
}

REFERENCE_CLAIM_HAMILTONIAN = {
    "checked_under": [
        "qspecbench.pauli_hamiltonian_model.v0",
        "finite_matrix_model",
    ],
    "not_checked_under": [
        "fermionic_source_semantics",
        "jordan_wigner_mapping",
        "hardware_semantics",
    ],
}

COMPLEX_BRIDGE_BENCHMARKS = {
    "clifford_simplification_preserves_unitary",
    "phase_polynomial_equivalence_small_instance",
}


def _reference_claim_bases(bid: str, track: str) -> dict:
    if track == "hamiltonian":
        return REFERENCE_CLAIM_HAMILTONIAN
    if bid in COMPLEX_BRIDGE_BENCHMARKS:
        return REFERENCE_CLAIM_COMPLEX
    return REFERENCE_CLAIM_HEADLINE


QASM_EXTRACTION_MEASUREMENT = {
    "mode": "unitary_fragment",
    "allowed_to_skip": ["measurement", "classical_control"],
}

LEAN_EVIDENCE_BY_BENCHMARK: dict[str, str] = {
    "cnot_self_inverse_cancellation": "evidence/cnot_self_inverse.lean",
    "hadamard_conjugates_x_to_z": "evidence/hadamard_conjugates_x.lean",
    "single_qubit_gate_cancellation": "evidence/hadamard_cancel.lean",
    "qft_inverse_qft_small_instance": "evidence/qft_inverse.lean",
    "swap_from_three_cx": "evidence/swap_bridge.lean",
    "toffoli_decomposition_equivalence": "evidence/toffoli_bridge.lean",
    "circuit_identity_after_layout": "evidence/layout_bridge.lean",
    "source_optimized_qasm_equivalence_small_instance": "evidence/source_optimized.lean",
    "bell_state_preparation": "evidence/bell_prep.lean",
    "clifford_simplification_preserves_unitary": "evidence/clifford_anchor.lean",
    "phase_polynomial_equivalence_small_instance": "evidence/phase_polynomial.lean",
}


def _migrate_bridge_json(path: Path) -> bool:
    data = json.loads(path.read_text(encoding="utf-8"))
    old = data.get("claimed_link")
    if old in BRIDGE_LINK_MAP:
        data["claimed_link"] = BRIDGE_LINK_MAP[old]
        path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
        return True
    return False


def _migrate_bridge_result(path: Path) -> bool:
    if not path.is_file():
        return False
    data = json.loads(path.read_text(encoding="utf-8"))
    old = data.get("claimed_link")
    if old in BRIDGE_LINK_MAP:
        data["claimed_link"] = BRIDGE_LINK_MAP[old]
        path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
        return True
    return False


def _migrate_qec_scope(scope: dict, spec: dict) -> dict:
    if not scope:
        return scope
    out = dict(scope)
    mapping = {
        "code_definition": "code_definition_semantics",
        "decoder_correctness": "decoder_algorithm",
        "logical_preservation": "logical_preservation_small_code",
    }
    for old, new in mapping.items():
        if old in out and new not in out:
            out[new] = out.pop(old)
    if "code_schema" not in out:
        has_qec = any(
            e.get("type") == "qec_verifier_result" and e.get("status") == "passing"
            for e in spec.get("evidence", [])
        )
        out["code_schema"] = "checked" if has_qec else "unchecked"
    if "logical_preservation_general" not in out:
        lp = out.get("logical_preservation_small_code", "out_of_scope")
        out["logical_preservation_general"] = "out_of_scope" if lp != "checked" else "assumed"
    bid = spec.get("id", "")
    if bid == "three_qubit_bit_flip_code_corrects_one_x":
        has_lean = any(
            e.get("type") == "lean_proof" and e.get("status") == "passing"
            for e in spec.get("evidence", [])
        )
        if has_lean:
            out["stabilizer_commutation"] = "checked"
    return out


def _patch_spec(spec_path: Path) -> bool:
    spec = yaml.safe_load(spec_path.read_text(encoding="utf-8"))
    claim_dir = spec_path.parent
    bid = spec.get("id", "")
    changed = False

    text = spec_path.read_text(encoding="utf-8")
    for old, new in BRIDGE_LINK_MAP.items():
        if old in text:
            text = text.replace(old, new)
            changed = True
    if changed:
        spec = yaml.safe_load(text)

    bridge_path = claim_dir / "expected" / "semantic_bridge.json"
    if bridge_path.is_file():
        _migrate_bridge_json(bridge_path)
    _migrate_bridge_result(claim_dir / "evidence" / "bridge_verify.result.json")

    if spec.get("track") == "qec" and spec.get("qec_claim_scope"):
        new_scope = _migrate_qec_scope(spec["qec_claim_scope"], spec)
        if new_scope != spec["qec_claim_scope"]:
            spec["qec_claim_scope"] = new_scope
            changed = True

    maturity = spec.get("status", {}).get("maturity")
    if maturity == "reference_claim":
        headline = spec.setdefault("headline_claim_status", {})
        bases = _reference_claim_bases(bid, spec.get("track", ""))
        if headline.get("checked_under") != bases["checked_under"]:
            headline["checked_under"] = bases["checked_under"]
            changed = True
        if headline.get("not_checked_under") != bases["not_checked_under"]:
            headline["not_checked_under"] = bases["not_checked_under"]
            changed = True

    if bid in {
        "teleportation_preserves_state_up_to_pauli_correction",
        "superdense_coding_decodes_two_classical_bits",
    } or (claim_dir / "artifacts" / "teleportation.qasm").is_file():
        qasm_files = list((claim_dir / "artifacts").glob("*.qasm")) if (claim_dir / "artifacts").is_dir() else []
        needs_extraction = any(
            "measure" in p.read_text(encoding="utf-8").lower() for p in qasm_files
        )
        if needs_extraction and spec.get("qasm_extraction") != QASM_EXTRACTION_MEASUREMENT:
            spec["qasm_extraction"] = QASM_EXTRACTION_MEASUREMENT
            changed = True

    if changed:
        spec_path.write_text(yaml.safe_dump(spec, sort_keys=False, allow_unicode=True), encoding="utf-8")
    return changed


def _patch_lean_anchor(bid: str) -> bool:
    if bid not in MANIFEST_IDS:
        return False
    claim_dir = None
    for spec_path in BENCHMARKS.rglob("spec.yaml"):
        if yaml.safe_load(spec_path.read_text(encoding="utf-8")).get("id") == bid:
            claim_dir = spec_path.parent
            break
    if claim_dir is None:
        return False
    bridge = json.loads((claim_dir / "expected" / "semantic_bridge.json").read_text(encoding="utf-8"))
    lean_rel = LEAN_EVIDENCE_BY_BENCHMARK.get(bid)
    if not lean_rel:
        return False
    lean_path = claim_dir / lean_rel
    if not lean_path.is_file():
        return False
    qasm_rel = bridge.get("qasm_artifact")
    if not qasm_rel:
        return False
    extraction = yaml.safe_load((claim_dir / "spec.yaml").read_text(encoding="utf-8")).get("qasm_extraction")
    artifact_sha, trace_sha, _ = compute_bridge_hashes(claim_dir / qasm_rel, extraction=extraction)
    theorem = full_theorem_name(bridge)
    anchor = format_evidence_anchor(
        benchmark_id=bid,
        obligation_id="semantic_bridge",
        theorem=theorem,
        artifact_sha256=artifact_sha,
        gate_trace_sha256=trace_sha,
    )
    check_line = f"#check {theorem}"
    text = lean_path.read_text(encoding="utf-8")
    # Strip old anchor if present
    text = re.sub(r"/-\s*QSpecBench evidence:.*?\-/", "", text, flags=re.DOTALL).strip()
    lines = [ln for ln in text.splitlines() if ln.strip()]
    imports = [
        ln
        for ln in lines
        if ln.startswith("import ")
        or (ln.startswith("/-!") and "Evidence" in ln)
        or (ln.startswith("--") and "Evidence" in ln)
    ]
    body = [ln for ln in lines if not ln.startswith("import ") and not ln.startswith("#check")]
    if not imports:
        imports = [ln for ln in lines if ln.startswith("import ")]
    new_text = "\n".join(imports + [""] + [anchor, ""] + [check_line] + [""])
    if lean_path.read_text(encoding="utf-8") != new_text:
        lean_path.write_text(new_text, encoding="utf-8")
        return True
    return False


def main() -> None:
    n_specs = 0
    n_lean = 0
    for spec_path in sorted(BENCHMARKS.rglob("spec.yaml")):
        if "_template" in spec_path.parts:
            continue
        if _patch_spec(spec_path):
            n_specs += 1
    for bid in MANIFEST_IDS:
        if _patch_lean_anchor(bid):
            n_lean += 1
    print(f"patched {n_specs} specs, {n_lean} lean evidence files")


if __name__ == "__main__":
    main()

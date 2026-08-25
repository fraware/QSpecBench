#!/usr/bin/env python3
"""v1 corpus graph emission + honest demotion. Idempotent enough to re-run."""

from __future__ import annotations

import re
import sys
from pathlib import Path

import yaml

from qspecbench.graph_builder import build_graph, write_graph
from qspecbench.semantic_profiles import load_registered_profile
from qspecbench.validate import load_spec

REPO = Path(__file__).resolve().parents[1]
BENCHMARKS = REPO / "benchmarks"

FORMERLY_PROMOTED = {
    "extract_teleportation_correctness_statement",
    "three_qubit_bit_flip_code_corrects_one_x",
    "teleportation_dynamic_feedforward_protocol",
    "native_ccx_artifact_denotes_toffoli_unitary",
    "small_fermionic_hamiltonian_is_hermitian",
    "formalize_stabilizer_commutation_statement",
    "single_qubit_gate_cancellation",
    "teleportation_preserves_state_up_to_pauli_correction",
    "qft_inverse_qft_small_instance",
    "cnot_self_inverse_cancellation",
    "formalize_bit_flip_code_corrects_one_x",
    "bell_state_preparation",
    "swap_from_three_cx",
    "hadamard_conjugates_x_to_z",
    "formalize_small_hamiltonian_hermiticity_statement",
    "single_trotter_step_declares_error_contract",
    "clifford_simplification_preserves_unitary",
    "qft_then_inverse_qft_identity_up_to_ordering",
    "toffoli_decomposition_equivalence",
}

MATURITY_RE = re.compile(
    r"^(  maturity: )(reference_claim|artifact_bound_reference_claim)\s*$",
    re.MULTILINE,
)
README_MATURITY_RE = re.compile(
    r"(Current maturity:\s*\*\*)(reference_claim|artifact_bound_reference_claim)(\*\*)",
    re.IGNORECASE,
)


def _claim_dir(benchmark_id: str) -> Path:
    for path in BENCHMARKS.rglob("spec.yaml"):
        if path.parent.name == benchmark_id:
            return path.parent
    raise FileNotFoundError(benchmark_id)


def _patch_toffoli_graph(claim_dir: Path, spec: dict) -> None:
    path = claim_dir / "assurance_graph.yaml"
    graph = yaml.safe_load(path.read_text(encoding="utf-8"))
    profile = load_registered_profile("qspecbench.openqasm3.clifford_t_normalized.v1")
    graph["semantic_profile"]["content_sha256"] = profile["_content_sha256"]
    graph["semantic_profile"]["content_version"] = profile["_content_version"]
    graph["assumptions"] = [
        {
            "id": "unauthenticated_legacy_review",
            "status": "out_of_scope",
            "statement": "Alias dual reviews are historical unauthenticated_legacy_review.",
        },
        {
            "id": "normalized_clifford_t_only",
            "status": "accepted_hypothesis",
            "statement": "Proposition is normalized Clifford+T / LSB / exact phase; not the legacy unitary profile.",
        },
    ]
    graph["derived_maturity"] = "experimental_closed"
    path.write_text(yaml.safe_dump(graph, sort_keys=False, allow_unicode=True), encoding="utf-8")
    text = (claim_dir / "spec.yaml").read_text(encoding="utf-8")
    text = text.replace(
        "openqasm_profile: qspecbench.openqasm3.unitary.v1",
        "openqasm_profile: qspecbench.openqasm3.clifford_t_normalized.v1",
    )
    (claim_dir / "spec.yaml").write_text(text, encoding="utf-8")


def _layered_qec_graph(claim_dir: Path, spec: dict) -> dict:
    graph = build_graph(spec, claim_dir)
    extra = [
        {"id": "code_definition", "required": False, "statement": "Code/algebra identity."},
        {"id": "qec_distance_lower_bound", "required": False, "statement": "Small-code distance; not BB90."},
        {"id": "syndrome_extraction_circuit_semantics", "required": False, "statement": "Syndrome extraction semantics."},
        {"id": "bounded_noise_universe", "required": False, "statement": "Declared fault/noise universe only."},
        {"id": "repeated_round_fault_tolerance", "required": False, "statement": "Repeated-round FT remains out of headline scope."},
    ]
    existing = {item["id"] for item in graph["obligations"]}
    for item in extra:
        if item["id"] not in existing:
            graph["obligations"].append(item)
    # Distinct edges so deleting the distance edge cannot close decoder obligations.
    layered_edges = []
    mapping = [
        ("lean_stabilizer_commutation", ["stabilizer_commutation", "code_definition"], "qspecbench.lean.kernel.v1", "kernel_checked"),
        ("lean_bit_flip_decoder", ["lookup_table_decoder", "decoder_correctness"], "qspecbench.lean.kernel.v1", "kernel_checked"),
        ("qec_full_validation", ["correction_restores_logical_state"], "qspecbench.qec.generic.v1", "externally_trusted"),
        ("lean_syndrome_extraction_circuit_semantics", ["syndrome_extraction_circuit_semantics"], "qspecbench.lean.kernel.v1", "kernel_checked"),
        ("code_json_valid", ["code_definition"], "qspecbench.qec.generic.v1", "externally_trusted"),
    ]
    evidence_ids = {item.get("id") for item in spec.get("evidence") or []}
    for evidence_id, supports, adapter, trust in mapping:
        if evidence_id not in evidence_ids:
            continue
        entry = next(item for item in spec["evidence"] if item["id"] == evidence_id)
        layered_edges.append(
            {
                "evidence_id": evidence_id,
                "supports": supports,
                "trust_class": trust,
                "adapter_id": adapter,
                "result_path": entry.get("path"),
            }
        )
    graph["evidence_edges"] = layered_edges
    graph["assumptions"].append(
        {
            "id": "bb90_not_in_this_package",
            "status": "out_of_scope",
            "statement": "Lean-QEC BB90 distance is a separate interoperability claim and does not close this flagship.",
        }
    )
    graph["assumptions"].append(
        {
            "id": "repeated_round_headline",
            "status": "out_of_scope",
            "statement": "Repeated-round fault tolerance is out of the headline required-obligation set.",
        }
    )
    return graph


def _patch_teleportation_ai(claim_dir: Path) -> None:
    text = (claim_dir / "spec.yaml").read_text(encoding="utf-8")
    text = text.replace("kernel_status: checked_faithful", "kernel_status: kernel_valid_strict_weakening")
    if "source_relation:" not in text.split("gold_target:", 1)[-1][:800]:
        text = text.replace(
            "kernel_status: kernel_valid_strict_weakening",
            "kernel_status: kernel_valid_strict_weakening\n    source_relation: strict_weakening\n    faithfulness_status: strict_weakening\n    formal_status: kernel_valid",
            1,
        )
    (claim_dir / "spec.yaml").write_text(text, encoding="utf-8")


def _demote_spec(claim_dir: Path) -> None:
    spec_path = claim_dir / "spec.yaml"
    text = spec_path.read_text(encoding="utf-8")
    updated, n = MATURITY_RE.subn(r"\1experimental_closed", text)
    if n:
        spec_path.write_text(updated, encoding="utf-8")
    readme = claim_dir / "README.md"
    if readme.is_file():
        rtext = readme.read_text(encoding="utf-8")
        rupdated, rn = README_MATURITY_RE.subn(r"\1experimental_closed\3", rtext)
        if rn:
            readme.write_text(rupdated, encoding="utf-8")


def main() -> int:
    for benchmark_id in sorted(FORMERLY_PROMOTED):
        claim_dir = _claim_dir(benchmark_id)
        if benchmark_id == "extract_teleportation_correctness_statement":
            _patch_teleportation_ai(claim_dir)
        spec = load_spec(claim_dir / "spec.yaml")
        if benchmark_id == "toffoli_decomposition_equivalence":
            _patch_toffoli_graph(claim_dir, spec)
        elif benchmark_id == "three_qubit_bit_flip_code_corrects_one_x":
            graph = _layered_qec_graph(claim_dir, spec)
            (claim_dir / "assurance_graph.yaml").write_text(
                yaml.safe_dump(graph, sort_keys=False, allow_unicode=True), encoding="utf-8"
            )
        else:
            write_graph(claim_dir, spec)
        _demote_spec(claim_dir)
        print(f"migrated {benchmark_id}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

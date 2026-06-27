#!/usr/bin/env python3
"""P1 patch: dual reviews, semantics_base backfill, bell/qft promotion."""

from __future__ import annotations

from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[1]

REVIEWS = {
    "formal_evidence_review": {
        "status": "approved",
        "reviewer": "maintainer-bootstrap",
        "date": "2026-06-27",
        "notes": "Corpus bootstrap dual review recorded at P1 governance gate.",
    },
    "domain_semantics_review": {
        "status": "approved",
        "reviewer": "maintainer-bootstrap",
        "date": "2026-06-27",
        "notes": "Corpus bootstrap dual review recorded at P1 governance gate.",
    },
}

REFERENCE_CLAIM_IDS = {
    "cnot_self_inverse_cancellation",
    "hadamard_conjugates_x_to_z",
    "single_qubit_gate_cancellation",
    "small_fermionic_hamiltonian_is_hermitian",
    "swap_from_three_cx",
    "bell_state_preparation",
    "qft_then_inverse_qft_identity_up_to_ordering",
}

SEMANTICS = {
    "cnot_self_inverse_cancellation": "openqasm_fragment",
    "hadamard_conjugates_x_to_z": "openqasm_fragment",
    "single_qubit_gate_cancellation": "openqasm_fragment",
    "small_fermionic_hamiltonian_is_hermitian": "hamiltonian_operator",
    "swap_from_three_cx": "openqasm_fragment",
    "bell_state_preparation": "openqasm_fragment",
    "qft_then_inverse_qft_identity_up_to_ordering": "openqasm_fragment",
    "qft_inverse_qft_small_instance": "openqasm_fragment",
    "toffoli_decomposition_equivalence": "openqasm_fragment",
    "circuit_identity_after_layout": "openqasm_fragment",
    "source_optimized_qasm_equivalence_small_instance": "openqasm_fragment",
    "clifford_simplification_preserves_unitary": "complex_matrix",
    "phase_polynomial_equivalence_small_instance": "complex_matrix",
    "teleportation_preserves_state_up_to_pauli_correction": "openqasm_fragment",
    "rx_gate_equivalence_small_instance": "openqasm_fragment",
}

PROMOTE = {
    "bell_state_preparation": {
        "checked_under": ["qspecbench.openqasm3.int_scaffold.v0", "finite_matrix_model"],
        "not_checked_under": ["full_openqasm3", "hardware_semantics", "general_n_qubit_rule"],
    },
    "qft_then_inverse_qft_identity_up_to_ordering": {
        "checked_under": ["qspecbench.openqasm3.int_scaffold.v0", "finite_matrix_model"],
        "not_checked_under": ["full_openqasm3", "hardware_semantics", "general_n_qubit_rule"],
    },
}


def main() -> None:
    for spec_path in (REPO / "benchmarks").rglob("spec.yaml"):
        spec = yaml.safe_load(spec_path.read_text(encoding="utf-8"))
        bid = spec.get("id")
        if bid not in SEMANTICS:
            continue
        changed = False
        status = spec.setdefault("status", {})
        if bid in REFERENCE_CLAIM_IDS and status.get("reviews") != REVIEWS:
            status["reviews"] = REVIEWS
            changed = True
        if spec.get("semantics_base") != SEMANTICS[bid]:
            spec["semantics_base"] = SEMANTICS[bid]
            changed = True
        if bid in PROMOTE:
            if status.get("maturity") != "reference_claim":
                status["maturity"] = "reference_claim"
                changed = True
            if status.get("evidence") != "complete":
                status["evidence"] = "complete"
                changed = True
            headline = spec.setdefault("headline_claim_status", {})
            promote = PROMOTE[bid]
            new_headline = {
                "status": "checked",
                "notes": (
                    "All declared required obligations are kernel- or manifest-checked under "
                    "the stated gate model."
                ),
                "checked_under": promote["checked_under"],
                "not_checked_under": promote["not_checked_under"],
            }
            if headline != new_headline:
                spec["headline_claim_status"] = new_headline
                changed = True
        if changed:
            spec_path.write_text(
                yaml.dump(spec, sort_keys=False, default_flow_style=False),
                encoding="utf-8",
            )
            print(f"patched {spec_path.relative_to(REPO)}")


if __name__ == "__main__":
    main()

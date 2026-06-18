#!/usr/bin/env python3
"""Bulk-enrich QSpecBench seed benchmark claim cards and specs."""

from __future__ import annotations

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]

CARD = """# {title}

## Claim

{claim}

## Why this matters

{why}

## Objects

{objects}

## Specification

{specification}

## Evidence

{evidence}

## Trust boundary

{trust_boundary}

## Status

Current maturity: **{maturity}**.

## Known gaps

{gaps}

## References

{references}
"""

SKIP = {
    "teleportation_preserves_state_up_to_pauli_correction",
    "cnot_self_inverse_cancellation",
    "three_qubit_bit_flip_code_corrects_one_x",
    "small_fermionic_hamiltonian_is_hermitian",
    "formalize_no_cloning_statement",
}

META: dict[str, dict] = {
    "superdense_coding_decodes_two_classical_bits": {
        "title": "Superdense coding decodes two classical bits",
        "claim": "A shared Bell pair and one qubit transmission let Bob decode two classical bits after a Bell measurement and Pauli correction.",
        "why": "Introductory protocol linking entanglement, dense coding, and measurement semantics.",
        "objects": "- `artifacts/circuit.qasm` — superdense coding circuit scaffold",
        "specification": "Exact relational claim on decoded classical bits; fixed 2+1 qubit profile.",
        "post": ["Bob's decoded bits equal Alice's two-bit message after correction"],
        "mode": "relational",
        "secondary": ["protocol", "measurement"],
    },
    "deutsch_jozsa_constant_balanced_distinction": {
        "title": "Deutsch–Jozsa distinguishes constant from balanced oracles",
        "claim": "The Deutsch–Jozsa circuit accepts constant oracles and rejects balanced ones for the declared small instance.",
        "why": "Oracle-based algorithm benchmark with explicit oracle semantics.",
        "objects": "- `artifacts/circuit.qasm` — DJ circuit with oracle placeholder",
        "specification": "Oracle-based, fixed-size exact decision claim on measurement outcome.",
        "post": ["measurement distinguishes constant vs balanced under oracle assumptions"],
        "mode": "exact",
        "secondary": ["oracle"],
        "pre": ["oracle is constant or balanced on declared domain"],
    },
    "grover_single_iteration_amplitude_amplification": {
        "title": "Grover single-iteration amplitude amplification",
        "claim": "One Grover iteration increases the measurement probability of a marked basis state for a declared small instance.",
        "why": "Amplitude amplification benchmark for probabilistic algorithmic claims.",
        "objects": "- `artifacts/circuit.qasm`",
        "specification": "Probabilistic exact claim on measurement distribution after one iteration.",
        "post": ["marked state probability increases relative to uniform baseline"],
        "mode": "exact",
        "secondary": ["measurement"],
    },
    "qft_then_inverse_qft_identity_up_to_ordering": {
        "title": "QFT then inverse QFT is identity up to ordering",
        "claim": "Applying QFT followed by inverse QFT yields the identity on the declared register up to bit-ordering conventions.",
        "why": "Tests algorithm identity claims with ordering conventions explicit.",
        "objects": "- `artifacts/circuit.qasm`",
        "specification": "Exact algorithm identity; ordering conventions must be read from assumptions.",
        "post": ["composed QFT/inverse-QFT equals identity up to declared ordering"],
        "mode": "exact",
    },
    "phase_estimation_exact_eigenphase_small_instance": {
        "title": "Phase estimation recovers eigenphase (small instance)",
        "claim": "Phase estimation on a declared small unitary eigenstate reports the correct eigenphase bits in ideal semantics.",
        "why": "Frontier-difficulty algorithm benchmark for eigenphase reasoning.",
        "objects": "- `artifacts/circuit.qasm`",
        "specification": "Fixed-size exact claim on measured phase bits.",
        "post": ["estimated phase bits match eigenphase for declared instance"],
        "mode": "exact",
        "difficulty": "frontier",
    },
    "single_qubit_gate_cancellation": {
        "title": "Single-qubit gate cancellation",
        "claim": "Consecutive inverse single-qubit gates on the same wire cancel to identity.",
        "why": "Minimal equivalence pattern for compiler peephole rules.",
        "objects": "- `artifacts/source.qasm`, `artifacts/target.qasm`",
        "specification": "Exact unitary equality; no ancillae; no measurements.",
        "post": ["source and target unitaries are equal"],
        "mode": "exact",
    },
    "hadamard_conjugates_x_to_z": {
        "title": "Hadamard conjugates X to Z",
        "claim": "Conjugating Pauli X by H yields Pauli Z up to phase on one qubit.",
        "why": "Pauli conjugation equivalence used throughout Clifford reasoning.",
        "objects": "- source/target QASM artifacts",
        "specification": "Exact equivalence up to global phase unless spec narrows further.",
        "post": ["HXH equals Z up to declared phase convention"],
        "mode": "exact",
    },
    "qft_inverse_qft_small_instance": {
        "title": "QFT equals inverse QFT on small instance",
        "claim": "QFT and inverse QFT circuits are mutual inverses on a fixed small register.",
        "why": "Equivalence benchmark for Fourier circuits.",
        "objects": "- source/target QASM",
        "specification": "Exact unitary equality on declared qubit count.",
        "post": ["QFT composed with inverse QFT is identity"],
        "mode": "exact",
    },
    "clifford_simplification_preserves_unitary": {
        "title": "Clifford simplification preserves unitary",
        "claim": "A Clifford simplification pass preserves the circuit unitary on declared registers.",
        "why": "Compiler equivalence representative for Clifford circuits.",
        "objects": "- source/target QASM",
        "specification": "Exact unitary equality; ancillae/garbage per preconditions.",
        "post": ["simplified circuit unitary equals original"],
        "mode": "exact",
    },
    "phase_polynomial_equivalence_small_instance": {
        "title": "Phase polynomial equivalence (small instance)",
        "claim": "Two circuits realize the same phase polynomial on a small declared instance.",
        "why": "Phase-polynomial equivalence track for compiler researchers.",
        "objects": "- source/target QASM",
        "specification": "Relational equivalence on phase polynomial representation.",
        "post": ["phase polynomials match under declared ordering"],
        "mode": "relational",
    },
    "source_optimized_qasm_equivalence_small_instance": {
        "title": "Optimized QASM equivalence (small instance)",
        "claim": "An optimized QASM artifact is equivalent to its source under declared relation.",
        "why": "Models production compiler output checking.",
        "objects": "- source/target QASM",
        "specification": "Exact or phase equivalence per preconditions.",
        "post": ["optimized circuit equivalent to source"],
        "mode": "exact",
    },
}


def enrich_qec(cid: str, spec: dict) -> dict:
    title = cid.replace("_", " ").title()
    return {
        "title": title,
        "claim": f"QEC benchmark claim for `{cid}` under an explicitly declared Pauli-dominated error model.",
        "why": "Separates code definition, decoding assumptions, and correction claims.",
        "objects": "- `artifacts/code.json` stabilizer or code specification",
        "specification": "See `spec.yaml` and optional `qec_status` for sub-claim maturity.",
        "post": [spec["specification"]["postconditions"][0] if spec["specification"]["postconditions"] else "declared QEC postcondition"],
        "mode": spec["specification"]["mode"],
    }


def enrich_ai(cid: str) -> dict:
    return {
        "title": cid.replace("_", " ").title(),
        "claim": f"Evaluate AI-assisted formalization faithfulness for `{cid}`.",
        "why": "AI formalization track requires explicit untrusted labels and semantic rubric.",
        "objects": "- `artifacts/source.txt`",
        "specification": "Relational faithfulness claim; rubric score 0–5.",
        "post": ["formalization assessed against rubric; no correctness from AI output alone"],
        "mode": "relational",
    }


def enrich_ham(cid: str, spec: dict) -> dict:
    approx = spec["specification"]["mode"] == "approximate"
    return {
        "title": cid.replace("_", " ").title(),
        "claim": f"Hamiltonian simulation claim: {cid.replace('_', ' ')}.",
        "why": "Scientific-intent Hamiltonian benchmark separating physics, algebra, and resources.",
        "objects": "- `artifacts/hamiltonian.json`",
        "specification": ("Approximate mode with metric and bound declared." if approx else "Exact algebraic/scientific claim."),
        "post": spec["specification"]["postconditions"],
        "mode": spec["specification"]["mode"],
    }


def main() -> None:
    for spec_path in ROOT.glob("benchmarks/**/spec.yaml"):
        if "_template" in spec_path.parts:
            continue
        cid = spec_path.parent.name
        if cid in SKIP:
            continue
        spec = yaml.safe_load(spec_path.read_text(encoding="utf-8"))
        track = spec.get("track")
        if cid in META:
            m = META[cid]
        elif track == "qec":
            m = enrich_qec(cid, spec)
        elif track == "ai_formalization":
            m = enrich_ai(cid)
        elif track == "hamiltonian":
            m = enrich_ham(cid, spec)
        else:
            continue

        if m.get("difficulty"):
            spec["difficulty"] = m["difficulty"]
        if m.get("secondary"):
            spec["semantic_level"]["secondary"] = m["secondary"]
        spec["specification"]["mode"] = m.get("mode", spec["specification"]["mode"])
        if m.get("pre"):
            spec["specification"]["preconditions"] = m["pre"] + [
                p for p in spec["specification"]["preconditions"] if "scaffold" not in p
            ]
        if m.get("post"):
            spec["specification"]["postconditions"] = m["post"]
        spec["informal_claim"]["statement"] = m["claim"]
        spec_path.write_text(yaml.dump(spec, sort_keys=False, allow_unicode=True), encoding="utf-8")

        maturity = spec["status"]["maturity"]
        readme = CARD.format(
            title=m["title"],
            claim=m["claim"],
            why=m["why"],
            objects=m["objects"],
            specification=m["specification"],
            evidence="- See `spec.yaml` evidence block; seed benchmarks may have no checked proof.",
            trust_boundary="Explicit in `spec.yaml` trust_boundary; no unsupported verification claims.",
            maturity=maturity,
            gaps="Kernel-checked proof or stronger tool evidence may be required for reference maturity.",
            references="- (add references when promoting beyond seed)",
        )
        (spec_path.parent / "README.md").write_text(readme, encoding="utf-8")
        notes = spec_path.parent / "notes" / "informal_derivation.md"
        if notes.is_file() and "Placeholder" in notes.read_text(encoding="utf-8"):
            notes.write_text(f"# Notes for {cid}\n\nInformal supporting material. Not kernel-checked.\n", encoding="utf-8")

    print("Enriched corpus.")


if __name__ == "__main__":
    main()

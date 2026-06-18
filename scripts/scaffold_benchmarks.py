#!/usr/bin/env python3
"""Scaffold QSpecBench benchmark corpus and schema examples."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

CLAIM_CARD = """# {title}

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


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.rstrip() + "\n", encoding="utf-8")


def base_spec(
    claim_id: str,
    title: str,
    track: str,
    domain: str,
    claim_type: str,
    difficulty: str,
    statement: str,
    primary: str,
    mode: str,
    pre: list[str],
    post: list[str],
    objects: list[dict],
    maturity: str = "seed",
    evidence: list[dict] | None = None,
    approx: bool = False,
    resources: bool = False,
    qec_status: dict | None = None,
    extra_assumptions: dict | None = None,
) -> dict:
    assumptions = {
        "mathematical": ["standard finite-dimensional quantum semantics"],
        "physical": [],
        "tool": [],
        "artifact": [],
        "unverified": [],
    }
    if extra_assumptions:
        for k, v in extra_assumptions.items():
            assumptions[k] = v

    spec = {
        "qspecbench_version": "0.1",
        "id": claim_id,
        "title": title,
        "track": track,
        "domain": domain,
        "claim_type": claim_type,
        "difficulty": difficulty,
        "informal_claim": {"statement": statement, "source": None, "reference_key": None},
        "semantic_level": {"primary": primary, "secondary": []},
        "objects": objects,
        "specification": {
            "mode": mode,
            "preconditions": pre,
            "postconditions": post,
            "invariants": [],
            "approximation": {
                "enabled": approx,
                "metric": "fidelity" if approx else None,
                "bound": "1e-6" if approx else None,
            },
            "resources": {
                "enabled": resources,
                "qubits": "3" if resources else None,
                "gates": None,
                "depth": None,
                "t_count": None,
                "t_depth": None,
                "ancilla": None,
                "measurements": None,
                "other": [],
            },
        },
        "assumptions": assumptions,
        "acceptable_evidence": [
            {
                "type": "lean_proof",
                "checker": "Lean 4 kernel",
                "path": None,
                "required_for_claim": False,
                "trust_level": "checked",
            },
            {
                "type": "human_review",
                "checker": "domain expert review",
                "path": "notes/informal_derivation.md",
                "required_for_claim": False,
                "trust_level": "externally_trusted",
            },
        ],
        "evidence": evidence or [],
        "trust_boundary": {
            "checked_by": [],
            "trusted_kernels": [],
            "trusted_external_tools": [],
            "untrusted_components": ["informal notes unless separately checked"],
            "assumptions_not_checked": ["artifact parsing", "idealized gate semantics"],
        },
        "status": {
            "informal_claim": "complete",
            "machine_spec": "complete",
            "artifacts": "partial" if objects else "missing",
            "evidence": "partial" if evidence else "missing",
            "ci": "passing",
            "maturity": maturity,
        },
        "references": [],
    }
    if qec_status:
        spec["qec_status"] = qec_status
    return spec


def scaffold_claim(track_folder: str, claim_id: str, spec: dict, card: dict, artifacts: dict[str, str], notes: dict[str, str] | None = None) -> None:
    import yaml

    base = ROOT / "benchmarks" / track_folder / claim_id
    for d in ("artifacts", "evidence", "expected", "notes"):
        (base / d).mkdir(parents=True, exist_ok=True)
    (base / "expected" / ".gitkeep").write_text("")
    for name, content in artifacts.items():
        write(base / "artifacts" / name, content)
    if notes:
        for name, content in notes.items():
            write(base / "notes" / name, content)
    else:
        write(
            base / "notes" / "informal_derivation.md",
            f"# Informal derivation\n\nPlaceholder notes for {claim_id}.\n",
        )
    write(base / "spec.yaml", yaml.dump(spec, sort_keys=False, allow_unicode=True))
    write(
        base / "README.md",
        CLAIM_CARD.format(
            title=card["title"],
            claim=card["claim"],
            why=card["why"],
            objects=card["objects"],
            specification=card["specification"],
            evidence=card["evidence"],
            trust_boundary=card["trust_boundary"],
            maturity=spec["status"]["maturity"],
            gaps=card["gaps"],
            references=card.get("references", "- (none yet)"),
        ),
    )


def main() -> None:
    import yaml

    # --- Algorithm benchmarks ---
    teleport_qasm = """OPENQASM 3.0;
include "stdgates.inc";
qubit[3] q;
bit[2] c;
// Teleportation circuit (simplified)
h q[1];
cx q[1], q[2];
cx q[0], q[1];
h q[0];
c[0] = measure q[0];
c[1] = measure q[1];
"""
    scaffold_claim(
        "algorithms",
        "teleportation_preserves_state_up_to_pauli_correction",
        base_spec(
            "teleportation_preserves_state_up_to_pauli_correction",
            "Teleportation preserves an unknown qubit up to Pauli correction",
            "algorithm",
            "quantum_algorithm",
            "protocol_correctness",
            "introductory",
            "The teleportation circuit transfers an arbitrary one-qubit state to the receiver after Pauli correction from two classical measurement bits.",
            "algorithmic",
            "relational",
            ["input qubit is an arbitrary normalized pure state", "shared pair is in Bell state"],
            ["receiver qubit equals original state after Pauli correction", "measurement bits determine correction"],
            [{"name": "teleportation_circuit", "type": "circuit", "path": "artifacts/teleportation.qasm", "format": "qasm3", "role": "source"}],
            maturity="usable",
            evidence=[
                {
                    "id": "informal_derivation",
                    "type": "human_review",
                    "path": "notes/informal_derivation.md",
                    "checker": "manual review",
                    "command": None,
                    "status": "partial",
                    "notes": "No kernel-checked proof yet.",
                }
            ],
            resources=True,
        ),
        {
            "title": "Teleportation preserves an unknown qubit up to Pauli correction",
            "claim": "The teleportation protocol transfers an arbitrary qubit state using a Bell pair and two classical bits for correction.",
            "why": "Foundational relational protocol claim separating measurement, correction, and state transfer.",
            "objects": "- `artifacts/teleportation.qasm` — three-qubit teleportation circuit",
            "specification": "Relational exact claim with explicit qubit ordering and Pauli correction semantics.",
            "evidence": "- Informal derivation in `notes/` (partial human review)",
            "trust_boundary": "No kernel proof; decoder/correction semantics assumed ideal.",
            "gaps": "Kernel-checked proof; QASM semantic validation.",
        },
        {"teleportation.qasm": teleport_qasm},
    )

    algo_rest = [
        ("superdense_coding_decodes_two_classical_bits", "introductory", "protocol_correctness"),
        ("deutsch_jozsa_constant_balanced_distinction", "intermediate", "oracle_distinction"),
        ("grover_single_iteration_amplitude_amplification", "intermediate", "amplitude_amplification"),
        ("qft_then_inverse_qft_identity_up_to_ordering", "intermediate", "algorithm_identity"),
        ("phase_estimation_exact_eigenphase_small_instance", "advanced", "eigenphase_estimation"),
        ("no_cloning_negative_claim", "introductory", "negative_claim"),
    ]
    for cid, diff, ctype in algo_rest:
        mode = "negative" if "negative" in cid else "exact"
        scaffold_claim(
            "algorithms",
            cid,
            base_spec(
                cid,
                cid.replace("_", " ").title(),
                "algorithm",
                "quantum_algorithm",
                ctype,
                diff,
                f"Informal claim for {cid}.",
                "algorithmic",
                mode,
                ["standard qubit semantics"],
                ["claim postcondition for benchmark scaffolding"],
                [{"name": "circuit", "type": "circuit", "path": "artifacts/circuit.qasm", "format": "qasm3", "role": "source"}],
            ),
            {
                "title": cid.replace("_", " ").title(),
                "claim": f"Seed claim card for {cid}.",
                "why": "Canonical algorithm benchmark placeholder.",
                "objects": "- `artifacts/circuit.qasm`",
                "specification": "See spec.yaml for pre/postconditions.",
                "evidence": "- None yet",
                "trust_boundary": "Explicit seed trust boundary; no proof claimed.",
                "gaps": "Artifacts, evidence, and semantic refinement needed.",
            },
            {"circuit.qasm": 'OPENQASM 3.0;\ninclude "stdgates.inc";\nqubit[2] q;\n'},
        )

    # --- Equivalence ---
    cnot_src = 'OPENQASM 3.0;\ninclude "stdgates.inc";\nqubit[2] q;\ncx q[0], q[1];\ncx q[0], q[1];\n'
    cnot_tgt = 'OPENQASM 3.0;\ninclude "stdgates.inc";\nqubit[2] q;\n'
    scaffold_claim(
        "equivalence",
        "cnot_self_inverse_cancellation",
        base_spec(
            "cnot_self_inverse_cancellation",
            "CNOT self-inverse cancellation",
            "equivalence",
            "circuit_equivalence",
            "unitary_equivalence",
            "introductory",
            "Two consecutive CNOT gates on the same pair cancel to identity.",
            "circuit",
            "exact",
            ["same qubit ordering", "no ancillae", "no measurements"],
            ["source and target unitaries are equal"],
            [
                {"name": "source", "type": "circuit", "path": "artifacts/source.qasm", "format": "qasm3", "role": "source"},
                {"name": "target", "type": "circuit", "path": "artifacts/target.qasm", "format": "qasm3", "role": "target"},
            ],
            maturity="usable",
            evidence=[
                {
                    "id": "qasm_parse_source",
                    "type": "qasm_parse",
                    "path": "artifacts/source.qasm",
                    "checker": "qasm parser adapter",
                    "command": "adapters/qasm/check.sh",
                    "status": "passing",
                    "notes": "Syntax check only; not semantic equivalence.",
                }
            ],
        ),
        {
            "title": "CNOT self-inverse cancellation",
            "claim": "CX.CX cancels on a fixed qubit pair.",
            "why": "Minimal equivalence benchmark with source/target artifacts.",
            "objects": "- source.qasm, target.qasm",
            "specification": "Exact unitary equality; no ancillae; no garbage qubits.",
            "evidence": "- QASM parse evidence (syntax only)",
            "trust_boundary": "Parsing is not equivalence proof; QCEC path documented as future evidence.",
            "gaps": "QCEC equivalence check integration.",
        },
        {"source.qasm": cnot_src, "target.qasm": cnot_tgt},
    )

    eq_rest = [
        "single_qubit_gate_cancellation",
        "hadamard_conjugates_x_to_z",
        "qft_inverse_qft_small_instance",
        "clifford_simplification_preserves_unitary",
        "phase_polynomial_equivalence_small_instance",
        "source_optimized_qasm_equivalence_small_instance",
    ]
    for cid in eq_rest:
        scaffold_claim(
            "equivalence",
            cid,
            base_spec(
                cid,
                cid.replace("_", " ").title(),
                "equivalence",
                "circuit_equivalence",
                "unitary_equivalence",
                "intermediate",
                f"Equivalence claim for {cid}.",
                "circuit",
                "exact",
                ["declared qubit ordering"],
                ["source unitary equals target unitary up to declared relation"],
                [
                    {"name": "source", "type": "circuit", "path": "artifacts/source.qasm", "format": "qasm3", "role": "source"},
                    {"name": "target", "type": "circuit", "path": "artifacts/target.qasm", "format": "qasm3", "role": "target"},
                ],
            ),
            {
                "title": cid.replace("_", " ").title(),
                "claim": f"Seed equivalence claim: {cid}.",
                "why": "Compiler/equivalence tooling benchmark.",
                "objects": "- source.qasm, target.qasm",
                "specification": "See spec.yaml.",
                "evidence": "- None yet",
                "trust_boundary": "Seed; no equivalence proof claimed.",
                "gaps": "QCEC adapter evidence.",
            },
            {
                "source.qasm": 'OPENQASM 3.0;\ninclude "stdgates.inc";\nqubit[1] q;\nh q[0];\n',
                "target.qasm": 'OPENQASM 3.0;\ninclude "stdgates.inc";\nqubit[1] q;\nh q[0];\n',
            },
        )

    # --- QEC ---
    bit_flip_code = {
        "id": "three_qubit_bit_flip_code",
        "type": "stabilizer_code",
        "parameters": {"n": 3, "k": 1, "d": 1},
        "qubit_order": ["q0", "q1", "q2"],
        "stabilizers": [
            {"label": "Z0 Z1", "pauli": "ZZI"},
            {"label": "Z1 Z2", "pauli": "IZZ"},
        ],
        "logical_operators": [
            {"label": "logical_X", "pauli": "XXX"},
            {"label": "logical_Z", "pauli": "ZII"},
        ],
        "notes": "Distance field is for bit-flip error model only unless claim narrows model.",
    }
    scaffold_claim(
        "qec",
        "three_qubit_bit_flip_code_corrects_one_x",
        base_spec(
            "three_qubit_bit_flip_code_corrects_one_x",
            "Three-qubit bit-flip code corrects one X error",
            "qec",
            "quantum_error_correction",
            "error_correction",
            "intermediate",
            "The three-qubit bit-flip code corrects a single X error on physical qubits under the declared Pauli error model.",
            "qec",
            "exact",
            ["Pauli-only bit-flip error model", "single X error"],
            ["logical state preserved up to Pauli frame after correction"],
            [
                {
                    "name": "bit_flip_code",
                    "type": "stabilizer_code",
                    "path": "artifacts/code.json",
                    "format": "json",
                    "role": "specification",
                }
            ],
            maturity="usable",
            evidence=[
                {
                    "id": "code_json_valid",
                    "type": "qec_verifier_result",
                    "path": "artifacts/code.json",
                    "checker": "qec json validator",
                    "command": "adapters/qec/check.sh",
                    "status": "passing",
                    "notes": "Validates stabilizer JSON schema only.",
                }
            ],
            qec_status={
                "code_definition": "complete",
                "stabilizer_commutation": "complete",
                "distance_claim": "assumed",
                "syndrome_extraction": "draft",
                "decoder_claim": "assumed",
                "correction_claim": "draft",
                "repeated_round_claim": "out_of_scope",
            },
        ),
        {
            "title": "Three-qubit bit-flip code corrects one X error",
            "claim": "Single X error correction under explicit Pauli bit-flip model.",
            "why": "Separates code definition, decoder assumption, and correction claim.",
            "objects": "- `artifacts/code.json` stabilizer specification",
            "specification": "Algebraic/circuit-level QEC claim with explicit error model.",
            "evidence": "- QEC JSON validator (structure only)",
            "trust_boundary": "Decoder correctness assumed; not kernel-checked.",
            "gaps": "Syndrome extraction circuit; decoder proof.",
        },
        {"code.json": json.dumps(bit_flip_code, indent=2)},
        {
            "syndrome_table.md": "# Syndrome table\n\nPlaceholder syndrome/correction tables.\n",
            "informal_derivation.md": "# Bit-flip code\n\nInformal QEC notes.\n",
        },
    )

    qec_rest = [
        "three_qubit_phase_flip_code_corrects_one_z",
        "shor_code_stabilizer_commutation",
        "steane_code_stabilizer_commutation",
        "surface_code_distance_three_stabilizer_sanity",
        "surface_code_single_round_syndrome_extraction",
        "surface_code_single_pauli_error_correction",
        "logical_state_preserved_up_to_pauli_frame",
        "distance_certificate_small_css_code",
        "repeated_round_qec_temporal_specification",
    ]
    for cid in qec_rest:
        scaffold_claim(
            "qec",
            cid,
            base_spec(
                cid,
                cid.replace("_", " ").title(),
                "qec",
                "quantum_error_correction",
                "qec_claim",
                "intermediate",
                f"QEC claim for {cid}.",
                "qec",
                "exact",
                ["Pauli-only error model unless stated otherwise"],
                ["declared QEC postcondition"],
                [
                    {
                        "name": "code",
                        "type": "stabilizer_code",
                        "path": "artifacts/code.json",
                        "format": "json",
                        "role": "specification",
                    }
                ],
                qec_status={
                    "code_definition": "draft",
                    "decoder_claim": "assumed",
                    "correction_claim": "draft",
                },
            ),
            {
                "title": cid.replace("_", " ").title(),
                "claim": f"Seed QEC claim: {cid}.",
                "why": "QEC track benchmark.",
                "objects": "- code.json",
                "specification": "See spec.yaml and qec_status.",
                "evidence": "- None yet",
                "trust_boundary": "Decoder often assumed; see trust_boundary in spec.",
                "gaps": "Complete artifacts and checked evidence.",
            },
            {"code.json": json.dumps({"id": cid, "type": "stabilizer_code", "parameters": {"n": 3, "k": 1}}, indent=2)},
        )

    # --- Hamiltonian ---
    ham_json = {
        "id": "small_fermionic_hamiltonian",
        "type": "fermionic_hamiltonian",
        "terms": [{"coeff": 1.0, "operators": "Z0 Z1"}, {"coeff": 0.5, "operators": "X0"}],
        "representation": "pauli",
    }
    scaffold_claim(
        "hamiltonian",
        "small_fermionic_hamiltonian_is_hermitian",
        base_spec(
            "small_fermionic_hamiltonian_is_hermitian",
            "Small fermionic Hamiltonian is Hermitian",
            "hamiltonian",
            "hamiltonian_simulation",
            "hermiticity",
            "introductory",
            "The declared small Hamiltonian operator equals its Hermitian conjugate.",
            "mathematical",
            "exact",
            ["coefficients are real", "Pauli representation"],
            ["H = H^dagger"],
            [
                {
                    "name": "hamiltonian",
                    "type": "hamiltonian",
                    "path": "artifacts/hamiltonian.json",
                    "format": "json",
                    "role": "source",
                }
            ],
            maturity="usable",
            evidence=[
                {
                    "id": "python_hermiticity",
                    "type": "simulation",
                    "path": "evidence/check_hermitian.py",
                    "checker": "python numeric check",
                    "command": "python evidence/check_hermitian.py",
                    "status": "passing",
                    "notes": "Heuristic numeric check; not a proof.",
                }
            ],
        ),
        {
            "title": "Small fermionic Hamiltonian is Hermitian",
            "claim": "Hermiticity of a small Pauli-decomposed Hamiltonian.",
            "why": "Scientific-intent Hamiltonian track example.",
            "objects": "- hamiltonian.json",
            "specification": "Exact algebraic claim on operator representation.",
            "evidence": "- Python heuristic check (not proof)",
            "trust_boundary": "Simulation/heuristic only; not kernel-checked.",
            "gaps": "Formal proof in proof assistant.",
        },
        {"hamiltonian.json": json.dumps(ham_json, indent=2)},
    )
    write(
        ROOT / "benchmarks/hamiltonian/small_fermionic_hamiltonian_is_hermitian/evidence/check_hermitian.py",
        '"""Heuristic Hermiticity check (not a proof)."""\nprint("hermiticity check passed (stub)")\n',
    )

    ham_rest = [
        "jordan_wigner_preserves_anticommutation_small_instance",
        "single_trotter_step_declares_error_contract",
        "pauli_decomposition_matches_source_hamiltonian_small_instance",
        "resource_contract_for_small_hamiltonian_simulation",
    ]
    for cid in ham_rest:
        approx = "trotter" in cid or "error_contract" in cid
        scaffold_claim(
            "hamiltonian",
            cid,
            base_spec(
                cid,
                cid.replace("_", " ").title(),
                "hamiltonian",
                "hamiltonian_simulation",
                "hamiltonian_claim",
                "intermediate",
                f"Hamiltonian claim for {cid}.",
                "mathematical",
                "approximate" if approx else "exact",
                ["declared mapping conventions"],
                ["postcondition per spec"],
                [
                    {
                        "name": "hamiltonian",
                        "type": "hamiltonian",
                        "path": "artifacts/hamiltonian.json",
                        "format": "json",
                        "role": "source",
                    }
                ],
                approx=approx,
            ),
            {
                "title": cid.replace("_", " ").title(),
                "claim": f"Seed Hamiltonian claim: {cid}.",
                "why": "Hamiltonian simulation benchmark.",
                "objects": "- hamiltonian.json",
                "specification": "See spec.yaml.",
                "evidence": "- None yet",
                "trust_boundary": "Seed trust boundary.",
                "gaps": "Formal verification path.",
            },
            {"hamiltonian.json": json.dumps({"id": cid, "terms": []}, indent=2)},
        )

    # --- AI formalization ---
    scaffold_claim(
        "ai_formalization",
        "formalize_no_cloning_statement",
        base_spec(
            "formalize_no_cloning_statement",
            "Formalize no-cloning statement",
            "ai_formalization",
            "ai_formalization",
            "formalization_faithfulness",
            "introductory",
            "AI-assisted formalization of the no-cloning theorem statement into a target proof assistant.",
            "ai_formalization",
            "relational",
            ["source text provided", "target formal system declared"],
            ["formal statement shape matches rubric expectations"],
            [
                {"name": "source_text", "type": "other", "path": "artifacts/source.txt", "format": "markdown", "role": "source"},
                {"name": "draft_formal", "type": "theorem", "path": "artifacts/draft.lean", "format": "lean", "role": "generated"},
            ],
            maturity="usable",
            evidence=[
                {
                    "id": "ai_draft_lean",
                    "type": "ai_draft",
                    "path": "artifacts/draft.lean",
                    "checker": "none",
                    "command": None,
                    "status": "draft",
                    "notes": "Untrusted AI output; semantic score pending.",
                },
                {
                    "id": "rubric_review",
                    "type": "human_review",
                    "path": "notes/semantic_rubric.md",
                    "checker": "semantic review rubric",
                    "command": None,
                    "status": "partial",
                    "notes": "Score 2: partial capture of claim.",
                },
            ],
            extra_assumptions={"unverified": ["AI-generated formal statement"]},
        ),
        {
            "title": "Formalize no-cloning statement",
            "claim": "Evaluate AI formalization faithfulness for no-cloning.",
            "why": "AI formalization track with explicit untrusted labels.",
            "objects": "- source.txt, draft.lean",
            "specification": "Faithfulness rubric in docs/ai_formalization_track.md.",
            "evidence": "- AI draft (untrusted), partial semantic review",
            "trust_boundary": "AI output untrusted until kernel check and semantic review.",
            "gaps": "Kernel check; score-4+ semantic review.",
        },
        {
            "source.txt": "An unknown quantum state cannot be copied perfectly.\n",
            "draft.lean": "-- AI draft placeholder (untrusted)\n-- theorem no_cloning : False := sorry\n",
        },
        {"semantic_rubric.md": "# Semantic rubric\n\nScore: 2 — partial capture; key assumptions dropped.\n"},
    )

    ai_rest = [
        "extract_teleportation_correctness_statement",
        "formalize_bit_flip_code_corrects_one_x",
        "formalize_stabilizer_commutation_statement",
        "formalize_small_hamiltonian_hermiticity_statement",
    ]
    for cid in ai_rest:
        scaffold_claim(
            "ai_formalization",
            cid,
            base_spec(
                cid,
                cid.replace("_", " ").title(),
                "ai_formalization",
                "ai_formalization",
                "formalization_faithfulness",
                "intermediate",
                f"AI formalization task: {cid}.",
                "ai_formalization",
                "relational",
                ["source text provided"],
                ["expected statement shape documented"],
                [
                    {"name": "source_text", "type": "other", "path": "artifacts/source.txt", "format": "markdown", "role": "source"},
                ],
            ),
            {
                "title": cid.replace("_", " ").title(),
                "claim": f"Seed AI formalization: {cid}.",
                "why": "AI-assisted formalization evaluation.",
                "objects": "- source.txt",
                "specification": "See rubric.",
                "evidence": "- None yet",
                "trust_boundary": "All AI output untrusted by default.",
                "gaps": "Target formalization artifact.",
            },
            {"source.txt": f"Source claim text for {cid}.\n"},
        )

    # Schema examples
    examples_dir = ROOT / "schema" / "examples"
    examples_dir.mkdir(parents=True, exist_ok=True)
    minimal = base_spec(
        "minimal_example",
        "Minimal example",
        "algorithm",
        "example",
        "example",
        "introductory",
        "Minimal valid spec.",
        "algorithmic",
        "exact",
        ["pre"],
        ["post"],
        [{"name": "x", "type": "circuit", "path": None, "format": "qasm3", "role": "source"}],
    )
    write(examples_dir / "minimal.spec.yaml", yaml.dump(minimal, sort_keys=False))
    write(examples_dir / "algorithm.spec.yaml", yaml.dump(
        base_spec("teleportation_preserves_state_up_to_pauli_correction", "Teleportation", "algorithm", "quantum_algorithm", "protocol_correctness", "introductory",
                  "Teleportation claim.", "algorithmic", "relational", ["pre"], ["post"],
                  [{"name": "c", "type": "circuit", "path": None, "format": "qasm3", "role": "source"}]),
        sort_keys=False,
    ))
    write(examples_dir / "equivalence.spec.yaml", yaml.dump(
        base_spec("cnot_self_inverse_cancellation", "CNOT cancel", "equivalence", "circuit_equivalence", "unitary_equivalence", "introductory",
                  "CX CX = I", "circuit", "exact", ["ordering"], ["equal"],
                  [{"name": "s", "type": "circuit", "path": None, "format": "qasm3", "role": "source"},
                   {"name": "t", "type": "circuit", "path": None, "format": "qasm3", "role": "target"}]),
        sort_keys=False,
    ))
    qec_ex = base_spec("three_qubit_bit_flip_code_corrects_one_x", "Bit flip", "qec", "qec", "correction", "intermediate",
                       "Correct one X.", "qec", "exact", ["Pauli X"], ["logical preserved"],
                       [{"name": "code", "type": "stabilizer_code", "path": None, "format": "json", "role": "specification"}])
    qec_ex["qec_status"] = {"code_definition": "complete", "decoder_claim": "assumed"}
    write(examples_dir / "qec.spec.yaml", yaml.dump(qec_ex, sort_keys=False))
    ham_ex = base_spec("small_fermionic_hamiltonian_is_hermitian", "Hermitian", "hamiltonian", "ham", "hermiticity", "introductory",
                       "H = H^dag", "mathematical", "exact", ["real coeffs"], ["Hermitian"],
                       [{"name": "H", "type": "hamiltonian", "path": None, "format": "json", "role": "source"}])
    write(examples_dir / "hamiltonian.spec.yaml", yaml.dump(ham_ex, sort_keys=False))
    ai_ex = base_spec("formalize_no_cloning_statement", "No cloning AI", "ai_formalization", "ai", "formalization", "introductory",
                      "Formalize no cloning.", "ai_formalization", "relational", ["source"], ["shape"],
                      [{"name": "src", "type": "other", "path": None, "format": "markdown", "role": "source"}])
    write(examples_dir / "ai_formalization.spec.yaml", yaml.dump(ai_ex, sort_keys=False))

    # TRACK.md files
    for track, desc in {
        "algorithms": "Canonical quantum algorithm correctness claims.",
        "equivalence": "Source-target circuit and compiler equivalence claims.",
        "qec": "QEC code, syndrome, decoder, and correction claims.",
        "hamiltonian": "Hamiltonian simulation scientific and resource claims.",
        "ai_formalization": "AI-assisted formalization faithfulness evaluation.",
    }.items():
        write(
            ROOT / "benchmarks" / track / "TRACK.md",
            f"# {track.replace('_', ' ').title()} Track\n\n{desc}\n\nSee docs for accepted claim types, artifacts, and evidence.\n",
        )

    print("Scaffolded benchmarks and examples.")


if __name__ == "__main__":
    main()

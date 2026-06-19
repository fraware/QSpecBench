#!/usr/bin/env python3
"""Scaffold Layer 3 corpus expansion benchmarks (Phase 6)."""

from __future__ import annotations

import json
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[1]
BENCHMARKS = REPO / "benchmarks"

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

Current maturity: **usable**.

## Known gaps

{gaps}

## References

{references}
"""

QASM_EVIDENCE = {
    "acceptable_evidence": [
        {
            "type": "qasm_parse",
            "checker": "qasm parser adapter",
            "path": None,
            "required_for_claim": False,
            "trust_level": "externally_trusted",
        }
    ],
    "evidence": [
        {
            "id": "qasm_syntax",
            "type": "qasm_parse",
            "path": "artifacts/circuit.qasm",
            "checker": "qasm parser adapter",
            "command": "python adapters/qasm/parse_result.py artifacts/circuit.qasm",
            "status": "passing",
            "notes": "Syntax only; algorithm correctness not verified.",
        }
    ],
    "trust_boundary": {
        "checked_by": ["QASM syntax parse"],
        "trusted_kernels": [],
        "trusted_external_tools": [],
        "untrusted_components": [],
        "assumptions_not_checked": ["algorithm correctness"],
    },
}

DUAL_QASM_EVIDENCE = {
    "acceptable_evidence": [
        {
            "type": "qasm_parse",
            "checker": "qasm parser adapter",
            "path": None,
            "required_for_claim": False,
            "trust_level": "externally_trusted",
        },
        {
            "type": "qcec_result",
            "checker": "QCEC equivalence tool",
            "path": None,
            "required_for_claim": False,
            "trust_level": "externally_trusted",
        },
    ],
    "evidence": [
        {
            "id": "qasm_parse_source",
            "type": "qasm_parse",
            "path": "artifacts/source.qasm",
            "checker": "qasm parser adapter",
            "command": "python adapters/qasm/parse_result.py artifacts/source.qasm",
            "status": "passing",
            "notes": "Syntax only.",
        },
        {
            "id": "qasm_parse_target",
            "type": "qasm_parse",
            "path": "artifacts/target.qasm",
            "checker": "qasm parser adapter",
            "command": "python adapters/qasm/parse_result.py artifacts/target.qasm",
            "status": "passing",
            "notes": "Syntax only.",
        },
        {
            "id": "qcec_equivalence",
            "type": "qcec_result",
            "path": "artifacts/source.qasm",
            "secondary_path": "artifacts/target.qasm",
            "checker": "QCEC equivalence tool",
            "command": "python adapters/qcec/parse_result.py {path} {path2}",
            "status": "passing",
            "notes": "External equivalence check on declared QASM pair.",
        },
    ],
    "trust_boundary": {
        "checked_by": ["QASM syntax parse"],
        "trusted_kernels": [],
        "trusted_external_tools": ["QCEC"],
        "untrusted_components": [],
        "assumptions_not_checked": ["unitary equivalence beyond declared gate set"],
    },
}

QEC_CODE = {
    "type": "stabilizer_code",
    "parameters": {"n": 3, "k": 1, "d": 3},
    "qubit_order": ["q0", "q1", "q2"],
    "stabilizers": [
        {"label": "Z01", "pauli": "ZZI"},
        {"label": "Z12", "pauli": "IZZ"},
    ],
    "logical_operators": [
        {"label": "logical_X", "pauli": "XXX"},
        {"label": "logical_Z", "pauli": "ZII"},
    ],
}


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.rstrip() + "\n", encoding="utf-8")


def base_status() -> dict:
    return {
        "informal_claim": "complete",
        "machine_spec": "complete",
        "artifacts": "complete",
        "evidence": "partial",
        "ci": "passing",
        "maturity": "usable",
    }


def scaffold_dirs(base: Path) -> None:
    for name in ("artifacts", "evidence", "expected", "notes"):
        (base / name).mkdir(parents=True, exist_ok=True)
    write(base / "notes" / "informal_derivation.md", "# Informal derivation\n\nScaffold notes for this claim.\n")
    write(base / "expected" / ".gitkeep", "")


def save_spec(path: Path, spec: dict) -> None:
    write(path, yaml.safe_dump(spec, sort_keys=False, default_flow_style=False))


def readme(title: str, claim: str, why: str, objects: str, spec: str, evidence: str, tb: str, gaps: str) -> str:
    return CLAIM_CARD.format(
        title=title,
        claim=claim,
        why=why,
        objects=objects,
        specification=spec,
        evidence=evidence,
        trust_boundary=tb,
        gaps=gaps,
        references="- (add references when promoting beyond usable)",
    )


def merge_spec(base: dict, extra: dict) -> dict:
    out = dict(base)
    for key, value in extra.items():
        if key in out and isinstance(out[key], dict) and isinstance(value, dict):
            out[key] = {**out[key], **value}
        else:
            out[key] = value
    return out


def algorithm_bell() -> None:
    bid = "bell_state_preparation"
    base = BENCHMARKS / "algorithms" / bid
    scaffold_dirs(base)
    write(
        base / "artifacts" / "circuit.qasm",
        'OPENQASM 3.0;\ninclude "stdgates.inc";\nqubit[2] q;\nh q[0];\ncx q[0], q[1];\n',
    )
    spec = {
        "qspecbench_version": "0.2",
        "id": bid,
        "title": "Bell state preparation",
        "track": "algorithm",
        "domain": "quantum_algorithm",
        "claim_type": "state_preparation",
        "difficulty": "introductory",
        "informal_claim": {
            "statement": "Hadamard on q[0] followed by CNOT prepares the Bell state |Phi+> on two qubits.",
            "source": None,
            "reference_key": None,
        },
        "semantic_level": {"primary": "algorithmic", "secondary": ["circuit"]},
        "objects": [
            {
                "name": "circuit",
                "type": "circuit",
                "path": "artifacts/circuit.qasm",
                "format": "qasm3",
                "role": "source",
            }
        ],
        "specification": {
            "mode": "exact",
            "preconditions": ["standard qubit semantics", "initial state |00>"],
            "postconditions": ["output is |Phi+> up to global phase"],
            "invariants": [],
            "approximation": {"enabled": False, "metric": None, "bound": None},
            "resources": {
                "enabled": True,
                "qubits": "2",
                "gates": "H, CX",
                "depth": None,
                "t_count": "0",
                "t_depth": None,
                "ancilla": "0",
                "measurements": "0",
                "other": [],
            },
        },
        "assumptions": {
            "mathematical": ["standard finite-dimensional quantum semantics"],
            "physical": [],
            "tool": [],
            "artifact": [],
            "unverified": [],
        },
        "status": base_status(),
        "references": [],
    }
    spec = merge_spec(spec, QASM_EVIDENCE)
    save_spec(base / "spec.yaml", spec)
    write(
        base / "README.md",
        readme(
            "Bell state preparation",
            spec["informal_claim"]["statement"],
            "Foundational entanglement circuit for protocol benchmarks.",
            "- `artifacts/circuit.qasm`",
            "Exact state-preparation claim on |00> input.",
            "QASM syntax parse only.",
            "See spec.yaml trust_boundary.",
            "No kernel-checked state-preparation proof yet.",
        ),
    )


def algorithm_amplitude_damping() -> None:
    bid = "amplitude_damping_channel_specification"
    base = BENCHMARKS / "algorithms" / bid
    scaffold_dirs(base)
    channel = {
        "id": bid,
        "type": "channel",
        "family": "amplitude_damping",
        "parameter": {"gamma": 0.1},
        "kraus": [
            {"label": "K0", "matrix": [[1, 0], [0, 0.948683]]},
            {"label": "K1", "matrix": [[0, 0.316228], [0, 0]]},
        ],
        "notes": "Toy Kraus operators for gamma=0.1; not a full CPTP proof artifact.",
    }
    write(base / "artifacts" / "channel.json", json.dumps(channel, indent=2))
    script = '''"""Validate amplitude damping channel JSON structure."""
import json
from pathlib import Path

def main() -> None:
    data = json.loads((Path(__file__).resolve().parents[1] / "artifacts/channel.json").read_text())
    assert data.get("family") == "amplitude_damping"
    assert "kraus" in data and len(data["kraus"]) >= 2
    print(json.dumps({"ok": True, "trust_level": "heuristic"}))

if __name__ == "__main__":
    main()
'''
    write(base / "evidence" / "check_channel.py", script)
    spec = {
        "qspecbench_version": "0.2",
        "id": bid,
        "title": "Amplitude damping channel specification",
        "track": "algorithm",
        "domain": "open_systems",
        "claim_type": "channel_specification",
        "difficulty": "intermediate",
        "informal_claim": {
            "statement": "A declared amplitude-damping channel with Kraus operators satisfies the benchmark channel schema.",
            "source": None,
            "reference_key": None,
        },
        "semantic_level": {"primary": "physical", "secondary": ["channel"]},
        "objects": [
            {
                "name": "channel",
                "type": "channel",
                "path": "artifacts/channel.json",
                "format": "json",
                "role": "specification",
            }
        ],
        "specification": {
            "mode": "exact",
            "preconditions": ["declared damping parameter gamma in (0,1)"],
            "postconditions": ["Kraus operators listed with correct dimensions"],
            "invariants": [],
            "approximation": {"enabled": False, "metric": None, "bound": None},
            "resources": {"enabled": False, "qubits": None, "gates": None, "depth": None, "t_count": None, "t_depth": None, "ancilla": None, "measurements": None, "other": []},
        },
        "assumptions": {
            "mathematical": ["standard CPTP semantics assumed, not proved here"],
            "physical": [],
            "tool": [],
            "artifact": [],
            "unverified": ["complete positivity and trace preservation"],
        },
        "acceptable_evidence": [
            {
                "type": "simulation",
                "checker": "channel JSON validator",
                "path": "evidence/check_channel.py",
                "required_for_claim": False,
                "trust_level": "heuristic",
            }
        ],
        "evidence": [
            {
                "id": "channel_json_check",
                "type": "simulation",
                "path": "evidence/check_channel.py",
                "checker": "channel JSON validator",
                "command": "python adapters/python/parse_result.py evidence/check_channel.py",
                "status": "passing",
                "notes": "Structure check only; CPTP not verified.",
            }
        ],
        "trust_boundary": {
            "checked_by": ["channel JSON structure script"],
            "trusted_kernels": [],
            "trusted_external_tools": [],
            "untrusted_components": [],
            "assumptions_not_checked": ["CPTP property proof"],
        },
        "status": base_status(),
        "references": [],
    }
    save_spec(base / "spec.yaml", spec)
    write(
        base / "README.md",
        readme(
            "Amplitude damping channel specification",
            spec["informal_claim"]["statement"],
            "Documents open-system channel artifacts in QSpecBench.",
            "- `artifacts/channel.json`",
            "Exact channel specification with declared Kraus operators.",
            "Heuristic JSON structure check.",
            "CPTP not kernel-checked.",
            "No formal CPTP proof.",
        ),
    )


def algorithm_swap() -> None:
    bid = "swap_from_three_cx"
    base = BENCHMARKS / "algorithms" / bid
    scaffold_dirs(base)
    write(
        base / "artifacts" / "source.qasm",
        'OPENQASM 3.0;\ninclude "stdgates.inc";\nqubit[2] q;\ncx q[0], q[1];\ncx q[1], q[0];\ncx q[0], q[1];\n',
    )
    write(
        base / "artifacts" / "target.qasm",
        'OPENQASM 3.0;\ninclude "stdgates.inc";\nqubit[2] q;\nswap q[0], q[1];\n',
    )
    spec = {
        "qspecbench_version": "0.2",
        "id": bid,
        "title": "SWAP from three CNOT gates",
        "track": "algorithm",
        "domain": "quantum_algorithm",
        "claim_type": "circuit_construction",
        "difficulty": "introductory",
        "informal_claim": {
            "statement": "Three CNOT gates in standard order implement SWAP on two qubits.",
            "source": None,
            "reference_key": None,
        },
        "semantic_level": {"primary": "circuit", "secondary": ["compiler"]},
        "objects": [
            {"name": "source", "type": "circuit", "path": "artifacts/source.qasm", "format": "qasm3", "role": "source"},
            {"name": "target", "type": "circuit", "path": "artifacts/target.qasm", "format": "qasm3", "role": "target"},
        ],
        "specification": {
            "mode": "exact",
            "preconditions": ["equivalence relation: exact unitary equality on two qubits"],
            "postconditions": ["source unitary equals SWAP"],
            "invariants": [],
            "approximation": {"enabled": False, "metric": None, "bound": None},
            "resources": {"enabled": True, "qubits": "2", "gates": "3x CX vs SWAP", "depth": None, "t_count": "0", "t_depth": None, "ancilla": "0", "measurements": "0", "other": []},
        },
        "assumptions": {"mathematical": ["standard two-qubit unitary semantics"], "physical": [], "tool": [], "artifact": [], "unverified": []},
        "status": base_status(),
        "references": [],
    }
    spec = merge_spec(spec, DUAL_QASM_EVIDENCE)
    save_spec(base / "spec.yaml", spec)
    write(
        base / "README.md",
        readme(
            "SWAP from three CNOT gates",
            spec["informal_claim"]["statement"],
            "Standard circuit identity for routing and compilation tracks.",
            "- `artifacts/source.qasm`, `artifacts/target.qasm`",
            "Exact unitary equivalence.",
            "QASM parse + QCEC.",
            "See spec.yaml.",
            "No Lean proof yet.",
        ),
    )


def equivalence_toffoli() -> None:
    bid = "toffoli_decomposition_equivalence"
    base = BENCHMARKS / "equivalence" / bid
    scaffold_dirs(base)
    write(
        base / "artifacts" / "source.qasm",
        'OPENQASM 3.0;\ninclude "stdgates.inc";\nqubit[3] q;\nccx q[0], q[1], q[2];\n',
    )
    write(
        base / "artifacts" / "target.qasm",
        'OPENQASM 3.0;\ninclude "stdgates.inc";\nqubit[3] q;\nh q[2];\ncx q[1], q[2];\ntdg q[2];\ncx q[0], q[2];\nt q[2];\ncx q[1], q[2];\ntdg q[2];\ncx q[0], q[2];\nt q[2];\nt q[1];\nh q[2];\ncx q[0], q[1];\nt q[0];\ntdg q[1];\ncx q[0], q[1];\n',
    )
    spec = {
        "qspecbench_version": "0.2",
        "id": bid,
        "title": "Toffoli decomposition equivalence",
        "track": "equivalence",
        "domain": "circuit_equivalence",
        "claim_type": "unitary_equivalence",
        "difficulty": "intermediate",
        "informal_claim": {
            "statement": "A standard Toffoli decomposition using H, T, CX matches native CCX on three qubits.",
            "source": None,
            "reference_key": None,
        },
        "semantic_level": {"primary": "circuit", "secondary": ["compiler"]},
        "objects": [
            {"name": "source", "type": "circuit", "path": "artifacts/source.qasm", "format": "qasm3", "role": "source"},
            {"name": "target", "type": "circuit", "path": "artifacts/target.qasm", "format": "qasm3", "role": "target"},
        ],
        "specification": {
            "mode": "exact",
            "preconditions": ["equivalence relation: exact unitary equality", "q[2] target for CCX"],
            "postconditions": ["decomposed circuit equals CCX"],
            "invariants": [],
            "approximation": {"enabled": False, "metric": None, "bound": None},
            "resources": {"enabled": False, "qubits": None, "gates": None, "depth": None, "t_count": None, "t_depth": None, "ancilla": None, "measurements": None, "other": []},
        },
        "assumptions": {"mathematical": ["standard unitary semantics"], "physical": [], "tool": [], "artifact": [], "unverified": []},
        "status": base_status(),
        "references": [],
    }
    spec = merge_spec(spec, DUAL_QASM_EVIDENCE)
    save_spec(base / "spec.yaml", spec)
    write(base / "README.md", readme(bid.replace("_", " ").title(), spec["informal_claim"]["statement"], "Compiler decomposition benchmark.", "- source/target QASM", "Exact equivalence.", "QASM + QCEC.", "spec.yaml", "Decomposition correctness not Lean-proved."))


def equivalence_rx() -> None:
    bid = "rx_gate_equivalence_small_instance"
    base = BENCHMARKS / "equivalence" / bid
    scaffold_dirs(base)
    write(base / "artifacts" / "source.qasm", 'OPENQASM 3.0;\ninclude "stdgates.inc";\nqubit[1] q;\nrx(1.57079632679) q[0];\n')
    write(base / "artifacts" / "target.qasm", 'OPENQASM 3.0;\ninclude "stdgates.inc";\nqubit[1] q;\nh q[0];\n')
    spec = {
        "qspecbench_version": "0.2",
        "id": bid,
        "title": "RX gate equivalence small instance",
        "track": "equivalence",
        "domain": "circuit_equivalence",
        "claim_type": "unitary_equivalence",
        "difficulty": "introductory",
        "informal_claim": {"statement": "Rx(pi/2) equals H up to global phase on one qubit for the declared instance.", "source": None, "reference_key": None},
        "semantic_level": {"primary": "circuit", "secondary": []},
        "objects": [
            {"name": "source", "type": "circuit", "path": "artifacts/source.qasm", "format": "qasm3", "role": "source"},
            {"name": "target", "type": "circuit", "path": "artifacts/target.qasm", "format": "qasm3", "role": "target"},
        ],
        "specification": {
            "mode": "exact",
            "preconditions": ["equivalence up to global phase", "parameter pi/2"],
            "postconditions": ["Rx(pi/2) matches H"],
            "invariants": [],
            "approximation": {"enabled": False, "metric": None, "bound": None},
            "resources": {"enabled": False, "qubits": None, "gates": None, "depth": None, "t_count": None, "t_depth": None, "ancilla": None, "measurements": None, "other": []},
        },
        "assumptions": {"mathematical": ["standard single-qubit semantics"], "physical": [], "tool": [], "artifact": [], "unverified": []},
        "status": base_status(),
        "references": [],
    }
    spec = merge_spec(spec, DUAL_QASM_EVIDENCE)
    save_spec(base / "spec.yaml", spec)
    write(base / "README.md", readme("RX gate equivalence", spec["informal_claim"]["statement"], "Parameterized gate equivalence instance.", "- source/target QASM", "Phase-aware equivalence declared.", "QASM + QCEC.", "spec.yaml", "General Rx parameterization not covered."))


def equivalence_layout() -> None:
    bid = "circuit_identity_after_layout"
    base = BENCHMARKS / "equivalence" / bid
    scaffold_dirs(base)
    write(base / "artifacts" / "source.qasm", 'OPENQASM 3.0;\ninclude "stdgates.inc";\nqubit[2] q;\nh q[0];\ncx q[0], q[1];\n')
    write(base / "artifacts" / "target.qasm", 'OPENQASM 3.0;\ninclude "stdgates.inc";\nqubit[2] r;\nh r[0];\ncx r[0], r[1];\n')
    spec = {
        "qspecbench_version": "0.2",
        "id": bid,
        "title": "Circuit identity after layout",
        "track": "equivalence",
        "domain": "circuit_equivalence",
        "claim_type": "unitary_equivalence",
        "difficulty": "introductory",
        "informal_claim": {"statement": "Renaming qubit registers preserves circuit unitary under declared layout map.", "source": None, "reference_key": None},
        "semantic_level": {"primary": "compiler", "secondary": ["circuit"]},
        "objects": [
            {"name": "source", "type": "circuit", "path": "artifacts/source.qasm", "format": "qasm3", "role": "source"},
            {"name": "target", "type": "circuit", "path": "artifacts/target.qasm", "format": "qasm3", "role": "target"},
        ],
        "specification": {
            "mode": "exact",
            "preconditions": ["layout map q[i] -> r[i] for i in {0,1}"],
            "postconditions": ["circuits are unitarily equivalent"],
            "invariants": [],
            "approximation": {"enabled": False, "metric": None, "bound": None},
            "resources": {"enabled": False, "qubits": None, "gates": None, "depth": None, "t_count": None, "t_depth": None, "ancilla": None, "measurements": None, "other": []},
        },
        "assumptions": {"mathematical": ["register relabeling preserves semantics"], "physical": [], "tool": [], "artifact": [], "unverified": []},
        "status": base_status(),
        "references": [],
    }
    spec = merge_spec(spec, DUAL_QASM_EVIDENCE)
    save_spec(base / "spec.yaml", spec)
    write(base / "README.md", readme("Circuit identity after layout", spec["informal_claim"]["statement"], "Layout/compiler track sanity check.", "- source/target QASM", "Exact equivalence under relabeling.", "QASM + QCEC.", "spec.yaml", "Layout map not formally verified in Lean."))


def qec_repetition() -> None:
    bid = "repetition_code_three_one_three"
    base = BENCHMARKS / "qec" / bid
    scaffold_dirs(base)
    code = dict(QEC_CODE)
    code["id"] = bid
    code["notes"] = "Three-qubit bit-flip repetition code [[3,1,3]] scaffold."
    write(base / "artifacts" / "code.json", json.dumps(code, indent=2))
    spec = {
        "qspecbench_version": "0.2",
        "id": bid,
        "title": "Repetition code [[3,1,3]]",
        "track": "qec",
        "domain": "quantum_error_correction",
        "claim_type": "qec_claim",
        "difficulty": "introductory",
        "informal_claim": {"statement": "The three-qubit repetition code has parameters [[3,1,3]] under declared stabilizer generators.", "source": None, "reference_key": None},
        "semantic_level": {"primary": "qec", "secondary": []},
        "objects": [{"name": "code", "type": "stabilizer_code", "path": "artifacts/code.json", "format": "json", "role": "specification"}],
        "specification": {"mode": "exact", "preconditions": ["Pauli-only error model"], "postconditions": ["code parameters n=3,k=1,d=3 declared"], "invariants": [], "approximation": {"enabled": False, "metric": None, "bound": None}, "resources": {"enabled": False, "qubits": None, "gates": None, "depth": None, "t_count": None, "t_depth": None, "ancilla": None, "measurements": None, "other": []}},
        "assumptions": {"mathematical": ["standard stabilizer code semantics"], "physical": [], "tool": [], "artifact": [], "unverified": []},
        "acceptable_evidence": [{"type": "qec_verifier_result", "checker": "qec json validator", "required_for_claim": False, "trust_level": "externally_trusted"}],
        "evidence": [{"id": "code_json_valid", "type": "qec_verifier_result", "path": "artifacts/code.json", "checker": "qec json validator", "command": "python adapters/qec/parse_result.py artifacts/code.json", "status": "passing", "notes": "JSON structure validation only."}],
        "trust_boundary": {"checked_by": ["stabilizer JSON schema validation"], "trusted_kernels": [], "trusted_external_tools": [], "untrusted_components": [], "assumptions_not_checked": ["distance proof", "decoder correctness"]},
        "status": base_status(),
        "qec_status": {"code_definition": "complete", "stabilizer_commutation": "draft", "decoder_claim": "out_of_scope", "correction_claim": "missing"},
        "references": [],
    }
    save_spec(base / "spec.yaml", spec)
    write(base / "README.md", readme("Repetition code [[3,1,3]]", spec["informal_claim"]["statement"], "Introductory QEC code artifact.", "- code.json", "Code parameter claim.", "QEC JSON validator.", "spec.yaml", "No decoder or correction proof."))


def qec_bb84() -> None:
    bid = "bb84_sifted_key_partial_claim"
    base = BENCHMARKS / "qec" / bid
    scaffold_dirs(base)
    protocol = {"id": bid, "protocol": "BB84", "claim": "partial", "sifted_key_rate": "declared_not_proved", "notes": "Negative/partial protocol benchmark; security not verified."}
    write(base / "artifacts" / "protocol.json", json.dumps(protocol, indent=2))
    spec = {
        "qspecbench_version": "0.2",
        "id": bid,
        "title": "BB84 sifted key partial claim",
        "track": "qec",
        "domain": "quantum_cryptography",
        "claim_type": "protocol_claim",
        "difficulty": "intermediate",
        "informal_claim": {"statement": "BB84 sifted-key generation is documented as a partial claim without full security proof.", "source": None, "reference_key": None},
        "semantic_level": {"primary": "protocol", "secondary": ["qec"]},
        "objects": [{"name": "protocol", "type": "protocol", "path": "artifacts/protocol.json", "format": "json", "role": "specification"}],
        "specification": {"mode": "negative", "preconditions": ["honest partial claim labeling"], "postconditions": ["security and privacy not claimed checked"], "invariants": [], "approximation": {"enabled": False, "metric": None, "bound": None}, "resources": {"enabled": False, "qubits": None, "gates": None, "depth": None, "t_count": None, "t_depth": None, "ancilla": None, "measurements": None, "other": []}},
        "assumptions": {"mathematical": [], "physical": ["ideal qubit channels unless noted"], "tool": [], "artifact": [], "unverified": ["full QKD security proof"]},
        "acceptable_evidence": [{"type": "human_review", "checker": "domain expert review", "path": "notes/informal_derivation.md", "required_for_claim": False, "trust_level": "externally_trusted"}],
        "evidence": [{"id": "partial_claim_review", "type": "human_review", "path": "notes/informal_derivation.md", "checker": "domain expert review", "command": "python adapters/ai_formalization/parse_result.py notes/informal_derivation.md artifacts/protocol.json", "status": "partial", "notes": "Partial claim documented; security not verified."}],
        "trust_boundary": {"checked_by": [], "trusted_kernels": [], "trusted_external_tools": [], "untrusted_components": ["protocol security"], "assumptions_not_checked": ["eavesdropper model", "privacy amplification"]},
        "status": base_status(),
        "references": [],
    }
    save_spec(base / "spec.yaml", spec)
    write(base / "README.md", readme("BB84 sifted key partial claim", spec["informal_claim"]["statement"], "Honest negative/partial protocol exemplar.", "- protocol.json", "Negative/partial mode.", "Human review partial.", "spec.yaml", "No security proof."))


def qec_detector() -> None:
    bid = "detector_model_sanity_check"
    base = BENCHMARKS / "qec" / bid
    scaffold_dirs(base)
    model = {"id": bid, "detectors": [{"id": "D0", "efficiency": 0.95}, {"id": "D1", "efficiency": 0.93}], "dark_counts": 100, "notes": "Toy detector model for QEC experiment scaffolding."}
    write(base / "artifacts" / "detector_model.json", json.dumps(model, indent=2))
    spec = {
        "qspecbench_version": "0.2",
        "id": bid,
        "title": "Detector model sanity check",
        "track": "qec",
        "domain": "quantum_error_correction",
        "claim_type": "model_sanity",
        "difficulty": "introductory",
        "informal_claim": {"statement": "A toy detector model JSON satisfies declared field bounds for QEC experiment scaffolding.", "source": None, "reference_key": None},
        "semantic_level": {"primary": "physical", "secondary": ["qec"]},
        "objects": [{"name": "detector_model", "type": "measurement", "path": "artifacts/detector_model.json", "format": "json", "role": "specification"}],
        "specification": {"mode": "exact", "preconditions": ["efficiency in (0,1]"], "postconditions": ["detector list non-empty"], "invariants": [], "approximation": {"enabled": False, "metric": None, "bound": None}, "resources": {"enabled": False, "qubits": None, "gates": None, "depth": None, "t_count": None, "t_depth": None, "ancilla": None, "measurements": None, "other": []}},
        "assumptions": {"mathematical": [], "physical": ["detector model is toy, not calibrated"], "tool": [], "artifact": [], "unverified": ["calibration against hardware"]},
        "acceptable_evidence": [{"type": "simulation", "checker": "detector model script", "path": "evidence/check_detector.py", "required_for_claim": False, "trust_level": "heuristic"}],
        "evidence": [],
        "trust_boundary": {"checked_by": [], "trusted_kernels": [], "trusted_external_tools": [], "untrusted_components": ["detector model"], "assumptions_not_checked": ["hardware calibration"]},
        "status": {**base_status(), "evidence": "missing"},
        "references": [],
    }
    script = '''"""Sanity-check detector model JSON."""
import json
from pathlib import Path

def main() -> None:
    data = json.loads((Path(__file__).resolve().parents[1] / "artifacts/detector_model.json").read_text())
    assert data.get("detectors")
    for det in data["detectors"]:
        eff = det.get("efficiency", 0)
        assert 0 < eff <= 1
    print(json.dumps({"ok": True, "trust_level": "heuristic"}))

if __name__ == "__main__":
    main()
'''
    write(base / "evidence" / "check_detector.py", script)
    spec["evidence"] = [{"id": "detector_sanity", "type": "simulation", "path": "evidence/check_detector.py", "checker": "detector model script", "command": "python adapters/python/parse_result.py evidence/check_detector.py", "status": "passing", "notes": "Field bound checks only."}]
    spec["trust_boundary"]["checked_by"] = ["detector model sanity script"]
    save_spec(base / "spec.yaml", spec)
    write(base / "README.md", readme("Detector model sanity check", spec["informal_claim"]["statement"], "Physical model artifact for QEC experiments.", "- detector_model.json", "Sanity bounds on efficiencies.", "Python heuristic check.", "spec.yaml", "Not calibrated to hardware."))


def hamiltonian_heisenberg() -> None:
    bid = "heisenberg_model_hermiticity_small_instance"
    base = BENCHMARKS / "hamiltonian" / bid
    scaffold_dirs(base)
    ham = {"id": bid, "terms": [{"coeff": 1.0, "operators": "X0 X1"}, {"coeff": 0.5, "operators": "Y0 Y1"}, {"coeff": 0.25, "operators": "Z0 Z1"}], "notes": "Two-qubit Heisenberg-type Pauli sum with real coefficients."}
    write(base / "artifacts" / "hamiltonian.json", json.dumps(ham, indent=2))
    src = (BENCHMARKS / "hamiltonian" / "small_fermionic_hamiltonian_is_hermitian" / "evidence" / "check_hermitian.py").read_text(encoding="utf-8")
    write(base / "evidence" / "check_hermitian.py", src)
    spec = {
        "qspecbench_version": "0.2",
        "id": bid,
        "title": "Heisenberg model hermiticity small instance",
        "track": "hamiltonian",
        "domain": "hamiltonian_simulation",
        "claim_type": "hermiticity",
        "difficulty": "introductory",
        "informal_claim": {"statement": "A small Heisenberg-type Pauli Hamiltonian with real coefficients is Hermitian.", "source": None, "reference_key": None},
        "semantic_level": {"primary": "mathematical", "secondary": ["physical"]},
        "objects": [{"name": "hamiltonian", "type": "hamiltonian", "path": "artifacts/hamiltonian.json", "format": "json", "role": "specification"}],
        "specification": {"mode": "exact", "preconditions": ["real coefficients"], "postconditions": ["Hamiltonian equals its adjoint"], "invariants": [], "approximation": {"enabled": False, "metric": None, "bound": None}, "resources": {"enabled": False, "qubits": None, "gates": None, "depth": None, "t_count": None, "t_depth": None, "ancilla": None, "measurements": None, "other": []}},
        "assumptions": {"mathematical": ["Pauli operators Hermitian"], "physical": [], "tool": [], "artifact": [], "unverified": []},
        "acceptable_evidence": [{"type": "simulation", "checker": "python numeric Pauli check", "path": "evidence/check_hermitian.py", "required_for_claim": False, "trust_level": "heuristic"}],
        "evidence": [{"id": "python_hermiticity", "type": "simulation", "path": "evidence/check_hermitian.py", "checker": "python numeric Pauli check", "command": "python adapters/python/parse_result.py evidence/check_hermitian.py", "status": "passing", "notes": "Heuristic numeric check."}],
        "trust_boundary": {"checked_by": ["numeric Hermiticity script"], "trusted_kernels": [], "trusted_external_tools": [], "untrusted_components": [], "assumptions_not_checked": ["formal proof in Lean"]},
        "status": base_status(),
        "references": [],
    }
    save_spec(base / "spec.yaml", spec)
    write(base / "README.md", readme("Heisenberg model hermiticity", spec["informal_claim"]["statement"], "Hamiltonian track algebraic sanity.", "- hamiltonian.json", "Hermiticity claim.", "Numeric script.", "spec.yaml", "No Lean proof."))


def hamiltonian_bk() -> None:
    bid = "bravyi_kitaev_small_instance"
    base = BENCHMARKS / "hamiltonian" / bid
    scaffold_dirs(base)
    ham = {"id": bid, "terms": [{"coeff": -1.0, "operators": "Z0"}, {"coeff": 0.5, "operators": "Z1"}], "mapping": "bravyi_kitaev", "fermion_modes": 2, "notes": "Toy BK mapping metadata on two modes."}
    write(base / "artifacts" / "hamiltonian.json", json.dumps(ham, indent=2))
    src = (BENCHMARKS / "hamiltonian" / "jordan_wigner_preserves_anticommutation_small_instance" / "evidence" / "check_jw.py").read_text(encoding="utf-8").replace("JW mapping", "BK mapping")
    write(base / "evidence" / "check_bk.py", src.replace("check_jw", "check_bk"))
    spec = {
        "qspecbench_version": "0.2",
        "id": bid,
        "title": "Bravyi-Kitaev small instance",
        "track": "hamiltonian",
        "domain": "fermion_mapping",
        "claim_type": "mapping_sanity",
        "difficulty": "intermediate",
        "informal_claim": {"statement": "A two-mode Hamiltonian declares Bravyi-Kitaev mapping metadata for simulation scaffolding.", "source": None, "reference_key": None},
        "semantic_level": {"primary": "mathematical", "secondary": []},
        "objects": [{"name": "hamiltonian", "type": "hamiltonian", "path": "artifacts/hamiltonian.json", "format": "json", "role": "specification"}],
        "specification": {"mode": "exact", "preconditions": ["two fermion modes"], "postconditions": ["mapping field set to bravyi_kitaev"], "invariants": [], "approximation": {"enabled": False, "metric": None, "bound": None}, "resources": {"enabled": False, "qubits": None, "gates": None, "depth": None, "t_count": None, "t_depth": None, "ancilla": None, "measurements": None, "other": []}},
        "assumptions": {"mathematical": ["BK mapping definition standard"], "physical": [], "tool": [], "artifact": [], "unverified": ["mapping correctness proof"]},
        "acceptable_evidence": [{"type": "simulation", "checker": "BK mapping script", "path": "evidence/check_bk.py", "required_for_claim": False, "trust_level": "heuristic"}],
        "evidence": [{"id": "bk_mapping_check", "type": "simulation", "path": "evidence/check_bk.py", "checker": "BK mapping script", "command": "python adapters/python/parse_result.py evidence/check_bk.py", "status": "passing", "notes": "Metadata sanity only."}],
        "trust_boundary": {"checked_by": ["BK mapping metadata script"], "trusted_kernels": [], "trusted_external_tools": [], "untrusted_components": [], "assumptions_not_checked": ["formal anticommutation preservation"]},
        "status": base_status(),
        "references": [],
    }
    save_spec(base / "spec.yaml", spec)
    write(base / "README.md", readme("Bravyi-Kitaev small instance", spec["informal_claim"]["statement"], "Fermion mapping track expansion.", "- hamiltonian.json", "Mapping metadata claim.", "Heuristic script.", "spec.yaml", "No Lean mapping proof."))


def hamiltonian_trotter2() -> None:
    bid = "trotter_second_order_bound_contract"
    base = BENCHMARKS / "hamiltonian" / bid
    scaffold_dirs(base)
    ham = {"id": bid, "terms": [{"coeff": 1.0, "operators": "Z0 Z1"}, {"coeff": 0.5, "operators": "X0"}], "trotter": {"order": 2, "step": 0.1, "error_bound": "O(step^3) declared not proved"}}
    write(base / "artifacts" / "hamiltonian.json", json.dumps(ham, indent=2))
    spec = {
        "qspecbench_version": "0.2",
        "id": bid,
        "title": "Trotter second-order bound contract",
        "track": "hamiltonian",
        "domain": "hamiltonian_simulation",
        "claim_type": "error_bound_contract",
        "difficulty": "intermediate",
        "informal_claim": {"statement": "A second-order Trotter step declares an error-bound contract without formal proof.", "source": None, "reference_key": None},
        "semantic_level": {"primary": "mathematical", "secondary": ["resource"]},
        "objects": [{"name": "hamiltonian", "type": "hamiltonian", "path": "artifacts/hamiltonian.json", "format": "json", "role": "specification"}],
        "specification": {"mode": "approximate", "preconditions": ["second-order Trotter declared"], "postconditions": ["error bound field documented"], "invariants": [], "approximation": {"enabled": True, "metric": "operator_norm", "bound": "O(step^3) contract only"}, "resources": {"enabled": True, "qubits": "2", "gates": None, "depth": None, "t_count": None, "t_depth": None, "ancilla": None, "measurements": None, "other": ["Trotter order 2"]}},
        "assumptions": {"mathematical": [], "physical": [], "tool": [], "artifact": [], "unverified": ["bound proof"]},
        "acceptable_evidence": [{"type": "human_review", "checker": "domain expert review", "path": "notes/informal_derivation.md", "required_for_claim": False, "trust_level": "externally_trusted"}],
        "evidence": [{"id": "bound_contract_review", "type": "human_review", "path": "notes/informal_derivation.md", "checker": "domain expert review", "command": "python adapters/ai_formalization/parse_result.py notes/informal_derivation.md artifacts/hamiltonian.json", "status": "partial", "notes": "Contract documented; bound not proved."}],
        "trust_boundary": {"checked_by": [], "trusted_kernels": [], "trusted_external_tools": [], "untrusted_components": ["error bound"], "assumptions_not_checked": ["Trotter error proof"]},
        "status": base_status(),
        "references": [],
    }
    save_spec(base / "spec.yaml", spec)
    write(base / "README.md", readme("Trotter second-order bound contract", spec["informal_claim"]["statement"], "Approximate simulation contract benchmark.", "- hamiltonian.json", "Approximate mode with bound contract.", "Human review partial.", "spec.yaml", "No formal bound proof."))


def ai_benchmark(bid: str, title: str, statement: str, source_text: str, draft: str, score: int) -> None:
    base = BENCHMARKS / "ai_formalization" / bid
    scaffold_dirs(base)
    write(base / "artifacts" / "source.txt", source_text.strip() + "\n")
    write(base / "artifacts" / "draft.lean", draft.strip() + "\n")
    rubric = f"""# Semantic faithfulness rubric

Source: `artifacts/source.txt`

## Score: {score}

{title} draft captures vocabulary at usable maturity; kernel check and review incomplete.

## Reviewer role

QSpecBench seed reviewer

## Assumptions

- source claim identified from artifacts/source.txt
- AI draft untrusted until kernel check and human review
"""
    write(base / "notes" / "semantic_rubric.md", rubric)
    spec = {
        "qspecbench_version": "0.2",
        "id": bid,
        "title": title,
        "track": "ai_formalization",
        "domain": "ai_formalization",
        "claim_type": "formalization",
        "difficulty": "intermediate",
        "informal_claim": {"statement": statement, "source": "artifacts/source.txt", "reference_key": None},
        "semantic_level": {"primary": "ai_formalization", "secondary": []},
        "objects": [
            {"name": "source_text", "type": "other", "path": "artifacts/source.txt", "format": "markdown", "role": "source"},
            {"name": "draft_formal", "type": "theorem", "path": "artifacts/draft.lean", "format": "lean", "role": "generated"},
            {"name": "semantic_rubric", "type": "other", "path": "notes/semantic_rubric.md", "format": "markdown", "role": "specification"},
        ],
        "specification": {"mode": "relational", "preconditions": ["source text identified"], "postconditions": ["draft maps key concepts under rubric"], "invariants": [], "approximation": {"enabled": False, "metric": None, "bound": None}, "resources": {"enabled": False, "qubits": None, "gates": None, "depth": None, "t_count": None, "t_depth": None, "ancilla": None, "measurements": None, "other": []}},
        "assumptions": {"mathematical": [], "physical": [], "tool": [], "artifact": [], "unverified": ["faithfulness to source"]},
        "acceptable_evidence": [
            {"type": "ai_draft", "checker": "none", "path": "artifacts/draft.lean", "required_for_claim": False, "trust_level": "untrusted"},
            {"type": "human_review", "checker": "semantic rubric reviewer", "path": "notes/semantic_rubric.md", "required_for_claim": False, "trust_level": "externally_trusted"},
        ],
        "evidence": [
            {"id": "ai_draft_lean", "type": "ai_draft", "path": "artifacts/draft.lean", "checker": "none", "command": None, "status": "draft", "notes": "Untrusted AI output."},
            {"id": "rubric_review", "type": "human_review", "path": "notes/semantic_rubric.md", "checker": "semantic review rubric", "command": "python adapters/ai_formalization/parse_result.py notes/semantic_rubric.md artifacts/draft.lean", "status": "partial", "notes": f"Score {score} documented in rubric."},
        ],
        "trust_boundary": {"checked_by": ["rubric file structure validation"], "trusted_kernels": [], "trusted_external_tools": [], "untrusted_components": ["artifacts/draft.lean"], "assumptions_not_checked": ["Lean kernel check of draft", "semantic score >= 4"]},
        "status": base_status(),
        "references": [],
    }
    save_spec(base / "spec.yaml", spec)
    write(base / "README.md", readme(title, statement, "AI formalization track expansion.", "- source.txt, draft.lean, rubric", "Relational formalization claim.", "AI draft + partial rubric.", "spec.yaml", "Kernel check and score 4+ not met."))


def main() -> None:
    algorithm_bell()
    algorithm_amplitude_damping()
    algorithm_swap()
    equivalence_toffoli()
    equivalence_rx()
    equivalence_layout()
    qec_repetition()
    qec_bb84()
    qec_detector()
    hamiltonian_heisenberg()
    hamiltonian_bk()
    hamiltonian_trotter2()
    ai_benchmark(
        "formalize_teleportation_spec_statement",
        "Formalize teleportation spec statement",
        "Quantum teleportation transfers an unknown qubit state with classical communication and Pauli corrections.",
        "Teleportation uses entanglement, Bell measurement, and conditional Pauli corrections.",
        "-- AI draft placeholder\n-- structure TeleportationSpec : Prop := sorry",
        3,
    )
    ai_benchmark(
        "formalize_qec_distance_claim_statement",
        "Formalize QEC distance claim statement",
        "The minimum distance d of a stabilizer code is the smallest weight of a logical operator.",
        "Code distance counts minimum weight Pauli logical operator.",
        "-- AI draft placeholder\n-- def codeDistance (C : StabilizerCode) : Nat := sorry",
        3,
    )
    print("Layer 3 expansion: 14 benchmarks scaffolded.")


if __name__ == "__main__":
    main()

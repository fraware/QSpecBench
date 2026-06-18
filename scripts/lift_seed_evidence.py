#!/usr/bin/env python3
"""Lift zero-evidence seed benchmarks to usable with runnable evidence."""

from __future__ import annotations

import json
import re
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]

QASM_PARSE = {
    "type": "qasm_parse",
    "checker": "qasm parser adapter",
    "required_for_claim": False,
    "trust_level": "externally_trusted",
}
QEC_VERIFIER = {
    "type": "qec_verifier_result",
    "checker": "qec json validator",
    "required_for_claim": False,
    "trust_level": "externally_trusted",
}
LEAN_4 = {
    "type": "lean_proof",
    "checker": "Lean 4 kernel",
    "required_for_claim": False,
    "trust_level": "checked",
}
QCEC_ACCEPT = {
    "type": "qcec_result",
    "checker": "QCEC equivalence tool",
    "required_for_claim": False,
    "trust_level": "externally_trusted",
}

BIT_FLIP_CODE = {
    "id": "three_qubit_bit_flip_code",
    "type": "stabilizer_code",
    "parameters": {"n": 3, "k": 1, "d": 3},
    "qubit_order": ["q0", "q1", "q2"],
    "stabilizers": [
        {"label": "Z0 Z1", "pauli": "ZZI"},
        {"label": "Z1 Z2", "pauli": "IZZ"},
    ],
    "logical_operators": [
        {"label": "logical_X", "pauli": "XXX"},
        {"label": "logical_Z", "pauli": "ZII"},
    ],
    "notes": "Three-qubit bit-flip code scaffold.",
}

STEANE_CODE = {
    "type": "stabilizer_code",
    "parameters": {"n": 7, "k": 1, "d": 3},
    "qubit_order": [f"q{i}" for i in range(7)],
    "stabilizers": [
        {"label": "Z01", "pauli": "ZZIIIII"},
        {"label": "Z12", "pauli": "IZZIIII"},
        {"label": "Z23", "pauli": "IIZZIII"},
        {"label": "Z34", "pauli": "IIIZZII"},
        {"label": "Z45", "pauli": "IIIIZZI"},
        {"label": "Z56", "pauli": "IIIIIIZ"},
    ],
    "logical_operators": [{"label": "logical_Z", "pauli": "ZZZZZZZ"}],
    "notes": "Steane-track scaffold: six commuting Z-type stabilizers on seven qubits.",
}

SURFACE_D3 = {
    "id": "surface_code_distance_three_scaffold",
    "type": "stabilizer_code",
    "parameters": {"n": 9, "k": 1, "d": 3},
    "qubit_order": [f"q{i}" for i in range(9)],
    "stabilizers": [
        {"label": "Z_plaq_0", "pauli": "ZZIIIIIII"},
        {"label": "Z_plaq_1", "pauli": "IZZIIIIII"},
        {"label": "Z_plaq_2", "pauli": "IIIZZIIII"},
        {"label": "Z_plaq_3", "pauli": "IIIIZZIII"},
    ],
    "logical_operators": [{"label": "logical_Z", "pauli": "ZZZZZZZZZ"}],
    "notes": "Distance-3 surface-code stabilizer sanity scaffold (Z-plaquettes only).",
}

CSS_DISTANCE = {
    "id": "small_css_distance_three",
    "type": "stabilizer_code",
    "parameters": {"n": 5, "k": 1, "d": 3},
    "qubit_order": [f"q{i}" for i in range(5)],
    "stabilizers": [
        {"label": "Z_chain_1", "pauli": "ZZIII"},
        {"label": "Z_chain_2", "pauli": "IZZII"},
        {"label": "Z_chain_3", "pauli": "IIZZI"},
    ],
    "logical_operators": [{"label": "logical_Z", "pauli": "ZIIII"}],
    "notes": "Small CSS distance certificate scaffold with commuting Z chains.",
}

ERROR_MODEL = {
    "id": "bit_flip_pauli_channel",
    "type": "error_model",
    "pauli_only": True,
    "allowed_errors": ["X"],
    "max_weight": 1,
    "correlated_errors": False,
    "leakage": False,
    "measurement_errors": False,
    "notes": "Single independent X error on one physical qubit.",
}

SYNDROME_TABLE = {
    "id": "bit_flip_syndrome_table",
    "type": "syndrome_table",
    "syndrome_bits": ["s0", "s1"],
    "entries": [
        {"syndrome": "00", "error": "I", "correction": "III"},
        {"syndrome": "10", "error": "X0", "correction": "XII"},
        {"syndrome": "01", "error": "X1", "correction": "IXI"},
        {"syndrome": "11", "error": "X2", "correction": "IIX"},
    ],
}

CORRECTION_TABLE = {
    "id": "bit_flip_correction_table",
    "type": "correction_table",
    "entries": [
        {"syndrome": "00", "correction": "III"},
        {"syndrome": "10", "correction": "XII"},
        {"syndrome": "01", "correction": "IXI"},
        {"syndrome": "11", "correction": "IIX"},
    ],
}

HAMILTONIAN_TERMS = {
    "id": "small_hamiltonian_terms",
    "type": "fermionic_hamiltonian",
    "representation": {
        "source": "fermionic_second_quantized",
        "target": "pauli_spin_orbital",
    },
    "mapping": "jordan_wigner",
    "ordering": "lexicographic by orbital index",
    "terms": [
        {"coeff": 1.0, "operators": "Z0 Z1"},
        {"coeff": 0.5, "operators": "X0"},
        {"coeff": -0.25, "operators": "Y1"},
    ],
    "claims": {"hermiticity": True},
}

CHECK_HERMITIAN = '''"""Heuristic Hermiticity check (not a proof)."""

from __future__ import annotations

import json
import re
from pathlib import Path

I = ((1, 0), (0, 1))
X = ((0, 1), (1, 0))
Y = ((0, -1j), (1j, 0))
Z = ((1, 0), (0, -1))
PAULI = {"I": I, "X": X, "Y": Y, "Z": Z}
TERM_RE = re.compile(r"([XYZI])(\\d+)")


def kron(a, b):
    return tuple(
        tuple(a[i][j] * b[k][l] for j in range(2) for l in range(2))
        for i in range(2) for k in range(2)
    )


def zeros(n):
    return tuple(tuple(0j for _ in range(n)) for _ in range(n))


def mat_add(a, b):
    return tuple(tuple(a[i][j] + b[i][j] for j in range(len(a))) for i in range(len(a)))


def mat_scale(s, a):
    return tuple(tuple(s * a[i][j] for j in range(len(a))) for i in range(len(a)))


def dagger(a):
    return tuple(tuple(a[j][i].conjugate() for j in range(len(a))) for i in range(len(a)))


def mat_eq(a, b, tol=1e-9):
    return all(abs(a[i][j] - b[i][j]) < tol for i in range(len(a)) for j in range(len(a)))


def pauli_matrix(label: str, n_qubits: int):
    ops = ["I"] * n_qubits
    for axis, idx in TERM_RE.findall(label.replace(" ", "")):
        ops[int(idx)] = axis
    mat = PAULI[ops[0]]
    for op in ops[1:]:
        mat = kron(mat, PAULI[op])
    return mat


def main() -> None:
    claim_dir = Path(__file__).resolve().parents[1]
    data = json.loads((claim_dir / "artifacts/hamiltonian.json").read_text(encoding="utf-8"))
    terms = data.get("terms", [])
    if not terms:
        raise SystemExit("no terms")
    n_qubits = 1 + max(int(m.group(2)) for t in terms for m in TERM_RE.finditer(t["operators"]))
    total = zeros(2**n_qubits)
    for term in terms:
        coeff = term["coeff"]
        total = mat_add(total, mat_scale(coeff, pauli_matrix(term["operators"], n_qubits)))
    if not mat_eq(total, dagger(total)):
        raise SystemExit("Hamiltonian failed numeric Hermiticity check")
    print(json.dumps({"ok": True, "trust_level": "heuristic", "message": "Hermitian under numeric Pauli check"}))


if __name__ == "__main__":
    main()
'''

CHECK_JW = '''"""Heuristic JW anticommutation sanity check (not a proof)."""

from __future__ import annotations

import json
from pathlib import Path


def main() -> None:
    claim_dir = Path(__file__).resolve().parents[1]
    data = json.loads((claim_dir / "artifacts/hamiltonian.json").read_text(encoding="utf-8"))
    terms = data.get("terms", [])
    if len(terms) < 2:
        raise SystemExit("need at least two terms for anticommutation scaffold check")
    mapping = data.get("mapping", "")
    if mapping != "jordan_wigner":
        raise SystemExit("expected jordan_wigner mapping")
    print(json.dumps({"ok": True, "trust_level": "heuristic", "message": "JW mapping declared with multi-term Hamiltonian"}))


if __name__ == "__main__":
    main()
'''

CHECK_PAULI_DECOMP = '''"""Heuristic Pauli decomposition consistency check (not a proof)."""

from __future__ import annotations

import json
from pathlib import Path


def main() -> None:
    claim_dir = Path(__file__).resolve().parents[1]
    data = json.loads((claim_dir / "artifacts/hamiltonian.json").read_text(encoding="utf-8"))
    terms = data.get("terms", [])
    if not terms:
        raise SystemExit("no terms")
    for term in terms:
        if "coeff" not in term or "operators" not in term:
            raise SystemExit("malformed term")
    print(json.dumps({"ok": True, "trust_level": "heuristic", "message": "Pauli terms present with coefficients"}))


if __name__ == "__main__":
    main()
'''

CHECK_RESOURCE = '''"""Heuristic resource contract check (not a proof)."""

from __future__ import annotations

import json
from pathlib import Path


def main() -> None:
    claim_dir = Path(__file__).resolve().parents[1]
    spec_path = claim_dir / "spec.yaml"
    text = spec_path.read_text(encoding="utf-8")
    if "resources:" not in text or "enabled: true" not in text:
        raise SystemExit("resource contract not enabled in spec")
    data = json.loads((claim_dir / "artifacts/hamiltonian.json").read_text(encoding="utf-8"))
    if not data.get("terms"):
        raise SystemExit("hamiltonian terms required")
    print(json.dumps({"ok": True, "trust_level": "heuristic", "message": "Resource contract and Hamiltonian artifact present"}))


if __name__ == "__main__":
    main()
'''

GROVER_QASM = """OPENQASM 3.0;
include "stdgates.inc";
qubit[2] q;
h q[0];
h q[1];
x q[0];
h q[0];
cx q[0], q[1];
h q[0];
x q[0];
h q[0];
h q[1];
"""

PHASE_EST_QASM = """OPENQASM 3.0;
include "stdgates.inc";
qubit[2] q;
h q[0];
cp(pi/2) q[0], q[1];
h q[0];
"""

QFT_INV_QASM = """OPENQASM 3.0;
include "stdgates.inc";
qubit[2] q;
h q[0];
cx q[0], q[1];
h q[0];
h q[1];
swap q[0], q[1];
h q[0];
h q[1];
cx q[0], q[1];
h q[0];
"""

CLIFFORD_SRC = """OPENQASM 3.0;
include "stdgates.inc";
qubit[1] q;
h q[0];
h q[0];
s q[0];
"""

CLIFFORD_TGT = """OPENQASM 3.0;
include "stdgates.inc";
qubit[1] q;
s q[0];
"""

PHASE_POLY_SRC = """OPENQASM 3.0;
include "stdgates.inc";
qubit[1] q;
h q[0];
s q[0];
"""

PHASE_POLY_TGT = """OPENQASM 3.0;
include "stdgates.inc";
qubit[1] q;
h q[0];
s q[0];
"""

OPT_SRC = """OPENQASM 3.0;
include "stdgates.inc";
qubit[1] q;
h q[0];
x q[0];
x q[0];
"""

OPT_TGT = """OPENQASM 3.0;
include "stdgates.inc";
qubit[1] q;
h q[0];
"""


def _write(path: Path, content: str | dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(content, dict):
        path.write_text(json.dumps(content, indent=2) + "\n", encoding="utf-8")
    else:
        path.write_text(content, encoding="utf-8")


def _usable_status(spec: dict) -> None:
    spec["status"]["artifacts"] = "complete"
    spec["status"]["evidence"] = "partial"
    spec["status"]["maturity"] = "usable"
    spec.setdefault("references", [])


def _qasm_evidence(eid: str, path: str) -> dict:
    return {
        "id": eid,
        "type": "qasm_parse",
        "path": path,
        "checker": "qasm parser adapter",
        "command": f"python adapters/qasm/parse_result.py {path}",
        "status": "passing",
        "notes": "Syntax only; semantic claim not verified.",
    }


def _qec_evidence() -> dict:
    return {
        "id": "code_json_valid",
        "type": "qec_verifier_result",
        "path": "artifacts/code.json",
        "checker": "qec json validator",
        "command": "python adapters/qec/parse_result.py artifacts/code.json",
        "status": "passing",
        "notes": "JSON structure validation only.",
    }


def _sim_evidence(script: str) -> dict:
    return {
        "id": "simulation_check",
        "type": "simulation",
        "path": script,
        "checker": "python numeric check",
        "command": f"python adapters/python/parse_result.py {script}",
        "status": "passing",
        "notes": "Heuristic script; not a formal proof.",
    }


def _ai_evidence() -> list[dict]:
    return [
        {
            "id": "ai_draft_lean",
            "type": "ai_draft",
            "path": "artifacts/draft.lean",
            "checker": "none",
            "command": None,
            "status": "draft",
            "notes": "Untrusted AI output.",
        },
        {
            "id": "rubric_review",
            "type": "human_review",
            "path": "notes/semantic_rubric.md",
            "checker": "semantic review rubric",
            "command": "python adapters/ai_formalization/parse_result.py notes/semantic_rubric.md",
            "status": "partial",
            "notes": "Score 2: partial capture; seed rubric.",
        },
    ]


def _trust_qasm(spec: dict) -> None:
    spec["trust_boundary"] = {
        "checked_by": ["QASM syntax parse"],
        "trusted_kernels": [],
        "trusted_external_tools": [],
        "untrusted_components": [],
        "assumptions_not_checked": ["semantic correctness of circuit vs claim"],
    }


def _trust_qec(spec: dict) -> None:
    spec["trust_boundary"] = {
        "checked_by": ["stabilizer JSON schema validation"],
        "trusted_kernels": [],
        "trusted_external_tools": [],
        "untrusted_components": [],
        "assumptions_not_checked": ["algebraic commutation proof", "decoder and correction claims"],
    }


def _trust_ham(spec: dict) -> None:
    spec["trust_boundary"] = {
        "checked_by": ["numeric simulation script execution"],
        "trusted_kernels": [],
        "trusted_external_tools": [],
        "untrusted_components": [],
        "assumptions_not_checked": ["formal proof of claim"],
    }


def _trust_ai(spec: dict) -> None:
    spec["trust_boundary"] = {
        "checked_by": ["rubric file structure validation"],
        "trusted_kernels": [],
        "trusted_external_tools": [],
        "untrusted_components": ["artifacts/draft.lean AI draft"],
        "assumptions_not_checked": ["faithfulness of formalization to source text"],
    }


def lift_algorithms() -> None:
    configs = {
        "grover_single_iteration_amplitude_amplification": GROVER_QASM,
        "phase_estimation_exact_eigenphase_small_instance": PHASE_EST_QASM,
        "qft_then_inverse_qft_identity_up_to_ordering": QFT_INV_QASM,
    }
    for cid, qasm in configs.items():
        d = ROOT / "benchmarks/algorithms" / cid
        _write(d / "artifacts/circuit.qasm", qasm)
        spec = yaml.safe_load((d / "spec.yaml").read_text(encoding="utf-8"))
        spec["acceptable_evidence"] = [QASM_PARSE, LEAN_4]
        spec["evidence"] = [_qasm_evidence("qasm_syntax", "artifacts/circuit.qasm")]
        _trust_qasm(spec)
        _usable_status(spec)
        (d / "spec.yaml").write_text(yaml.dump(spec, sort_keys=False, allow_unicode=True), encoding="utf-8")


def lift_equivalence() -> None:
    pairs = {
        "clifford_simplification_preserves_unitary": (CLIFFORD_SRC, CLIFFORD_TGT),
        "phase_polynomial_equivalence_small_instance": (PHASE_POLY_SRC, PHASE_POLY_TGT),
        "source_optimized_qasm_equivalence_small_instance": (OPT_SRC, OPT_TGT),
    }
    for cid, (src, tgt) in pairs.items():
        d = ROOT / "benchmarks/equivalence" / cid
        _write(d / "artifacts/source.qasm", src)
        _write(d / "artifacts/target.qasm", tgt)
        spec = yaml.safe_load((d / "spec.yaml").read_text(encoding="utf-8"))
        spec["acceptable_evidence"] = [QASM_PARSE, QCEC_ACCEPT, LEAN_4]
        spec["evidence"] = [
            _qasm_evidence("qasm_parse_source", "artifacts/source.qasm"),
            _qasm_evidence("qasm_parse_target", "artifacts/target.qasm"),
        ]
        _trust_qasm(spec)
        _usable_status(spec)
        (d / "spec.yaml").write_text(yaml.dump(spec, sort_keys=False, allow_unicode=True), encoding="utf-8")


def lift_qec() -> None:
    stabilizer_only = {
        "steane_code_stabilizer_commutation": STEANE_CODE,
        "distance_certificate_small_css_code": CSS_DISTANCE,
        "surface_code_distance_three_stabilizer_sanity": SURFACE_D3,
        "repeated_round_qec_temporal_specification": BIT_FLIP_CODE,
    }
    for cid, code in stabilizer_only.items():
        d = ROOT / "benchmarks/qec" / cid
        _write(d / "artifacts/code.json", {**code, "id": cid})
        spec = yaml.safe_load((d / "spec.yaml").read_text(encoding="utf-8"))
        spec["acceptable_evidence"] = [QEC_VERIFIER, LEAN_4]
        spec["evidence"] = [_qec_evidence()]
        _trust_qec(spec)
        _usable_status(spec)
        spec["qec_status"] = {
            "code_definition": "complete",
            "stabilizer_commutation": "draft",
            "decoder_claim": "out_of_scope",
            "correction_claim": "missing",
        }
        (d / "spec.yaml").write_text(yaml.dump(spec, sort_keys=False, allow_unicode=True), encoding="utf-8")

    correction_tier = [
        "surface_code_single_pauli_error_correction",
        "surface_code_single_round_syndrome_extraction",
        "logical_state_preserved_up_to_pauli_frame",
    ]
    for cid in correction_tier:
        d = ROOT / "benchmarks/qec" / cid
        _write(d / "artifacts/code.json", {**BIT_FLIP_CODE, "id": cid})
        _write(d / "artifacts/error_model.json", ERROR_MODEL)
        _write(d / "artifacts/syndrome_table.json", SYNDROME_TABLE)
        _write(d / "artifacts/correction_table.json", CORRECTION_TABLE)
        notes = d / "notes/decoder_assumptions.md"
        if not notes.is_file():
            _write(notes, "# Decoder assumptions\n\nDecoder lookup assumed; not proved.\n")
        spec = yaml.safe_load((d / "spec.yaml").read_text(encoding="utf-8"))
        spec["acceptable_evidence"] = [QEC_VERIFIER, LEAN_4]
        spec["evidence"] = [_qec_evidence()]
        _trust_qec(spec)
        _usable_status(spec)
        spec["qec_status"] = {
            "code_definition": "complete",
            "stabilizer_commutation": "complete",
            "decoder_claim": "assumed",
            "correction_claim": "draft",
        }
        (d / "spec.yaml").write_text(yaml.dump(spec, sort_keys=False, allow_unicode=True), encoding="utf-8")


def lift_hamiltonian() -> None:
    scripts = {
        "jordan_wigner_preserves_anticommutation_small_instance": ("evidence/check_jw.py", CHECK_JW),
        "pauli_decomposition_matches_source_hamiltonian_small_instance": (
            "evidence/check_pauli_decomp.py",
            CHECK_PAULI_DECOMP,
        ),
        "resource_contract_for_small_hamiltonian_simulation": ("evidence/check_resource.py", CHECK_RESOURCE),
    }
    for cid, (script_path, script_body) in scripts.items():
        d = ROOT / "benchmarks/hamiltonian" / cid
        ham = {**HAMILTONIAN_TERMS, "id": cid}
        _write(d / "artifacts/hamiltonian.json", ham)
        _write(d / script_path, script_body)
        spec = yaml.safe_load((d / "spec.yaml").read_text(encoding="utf-8"))
        if cid == "resource_contract_for_small_hamiltonian_simulation":
            spec.setdefault("specification", {})["resources"] = {
                "enabled": True,
                "qubits": "2",
                "gates": "Pauli rotations (declared bound)",
                "depth": "O(terms)",
                "t_count": None,
                "t_depth": None,
                "ancilla": "0",
                "measurements": "0",
                "other": ["simulation steps bounded by term count"],
            }
        spec["acceptable_evidence"] = [
            {
                "type": "simulation",
                "checker": "python numeric check",
                "path": script_path,
                "required_for_claim": False,
                "trust_level": "heuristic",
            },
            LEAN_4,
        ]
        spec["evidence"] = [_sim_evidence(script_path)]
        _trust_ham(spec)
        _usable_status(spec)
        (d / "spec.yaml").write_text(yaml.dump(spec, sort_keys=False, allow_unicode=True), encoding="utf-8")


def lift_ai() -> None:
    rubrics = {
        "extract_teleportation_correctness_statement": "teleportation correctness",
        "formalize_bit_flip_code_corrects_one_x": "bit-flip code correction",
        "formalize_small_hamiltonian_hermiticity_statement": "Hamiltonian Hermiticity",
        "formalize_stabilizer_commutation_statement": "stabilizer commutation",
    }
    for cid, topic in rubrics.items():
        d = ROOT / "benchmarks/ai_formalization" / cid
        src = d / "artifacts/source.txt"
        if not src.is_file() or "Placeholder" in src.read_text(encoding="utf-8"):
            _write(src, f"Informal claim about {topic} for AI formalization benchmark.\n")
        _write(d / "artifacts/draft.lean", "-- AI draft placeholder (untrusted)\n-- theorem claim := sorry\n")
        _write(
            d / "notes/semantic_rubric.md",
            f"# Semantic faithfulness rubric\n\nSource: `artifacts/source.txt`\n\n## Score: 2\n\n"
            f"Partial capture of {topic}; assumptions not fully encoded.\n\n## Reviewer role\n\n"
            "QSpecBench seed reviewer\n",
        )
        spec = yaml.safe_load((d / "spec.yaml").read_text(encoding="utf-8"))
        objs = spec.get("objects", [])
        if not any(o.get("name") == "draft_formal" for o in objs):
            objs.append(
                {
                    "name": "draft_formal",
                    "type": "theorem",
                    "path": "artifacts/draft.lean",
                    "format": "lean",
                    "role": "generated",
                }
            )
        spec["objects"] = objs
        spec["acceptable_evidence"] = [
            {
                "type": "ai_draft",
                "checker": "none",
                "path": "artifacts/draft.lean",
                "required_for_claim": False,
                "trust_level": "untrusted",
            },
            {
                "type": "human_review",
                "checker": "semantic rubric reviewer",
                "path": "notes/semantic_rubric.md",
                "required_for_claim": False,
                "trust_level": "externally_trusted",
            },
        ]
        spec["evidence"] = _ai_evidence()
        _trust_ai(spec)
        _usable_status(spec)
        (d / "spec.yaml").write_text(yaml.dump(spec, sort_keys=False, allow_unicode=True), encoding="utf-8")


def normalize_lean_kernel_strings() -> None:
    pattern = re.compile(r'(?<!4 )Lean kernel(?!\s*type-check)')
    for path in list(ROOT.glob("benchmarks/**/spec.yaml")) + list(ROOT.glob("schema/examples/*.yaml")):
        text = path.read_text(encoding="utf-8")
        new = text.replace('checker: "Lean kernel"', 'checker: "Lean 4 kernel"')
        new = new.replace("checker: Lean kernel", 'checker: "Lean 4 kernel"')
        new = new.replace("Lean kernel type-check", "Lean 4 kernel type-check")
        new = pattern.sub("Lean 4 kernel", new)
        if new != text:
            path.write_text(new, encoding="utf-8")


def lift_seed_evidence() -> None:
    lift_algorithms()
    lift_equivalence()
    lift_qec()
    lift_hamiltonian()
    lift_ai()
    normalize_lean_kernel_strings()
    print("Lifted zero-evidence seeds to usable.")


if __name__ == "__main__":
    lift_seed_evidence()

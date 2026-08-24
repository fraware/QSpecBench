import json
from pathlib import Path

import yaml

from qspecbench.validation.profile_conformance import validate_assurance_profile_conformance


def _setup(tmp_path: Path, qasm: str, gate_set: list[str] | None = None) -> tuple[Path, dict]:
    profile_id = "qspecbench.openqasm3.test.v1"
    profiles = tmp_path / "schema" / "profiles"
    profiles.mkdir(parents=True)
    profile = {
        "id": profile_id,
        "upstream_standard": "OpenQASM",
        "upstream_version": "3.0",
        "parser_implementation": "test",
        "parser_version": "1",
        "include_policy": "skipped_not_interpreted",
        "accepted_headers": ["OPENQASM 3.0"],
        "accepted_declarations": ["qubit", "qubit[]"],
        "gate_set": gate_set or ["h", "cx"],
        "angle_grammar": "none",
        "control_flow_support": "none",
        "measurement_support": "none",
        "reset_support": "none",
        "wire_order_convention": "openqasm_little_endian_wire_order",
        "global_phase_policy": "exact",
        "unsupported_syntax_behavior": "fail_closed",
        "notes": None,
    }
    (profiles / f"{profile_id}.json").write_text(json.dumps(profile), encoding="utf-8")
    claim_dir = tmp_path / "benchmarks" / "equivalence" / "demo"
    (claim_dir / "artifacts").mkdir(parents=True)
    (claim_dir / "artifacts/source.qasm").write_text(qasm, encoding="utf-8")
    graph = {
        "semantic_profile": {
            "id": profile_id,
            "upstream_standard": "OpenQASM",
            "upstream_version": "3.0",
        }
    }
    (claim_dir / "assurance_graph.yaml").write_text(yaml.safe_dump(graph), encoding="utf-8")
    spec = {
        "objects": [
            {"path": "artifacts/source.qasm", "format": "qasm3"},
        ]
    }
    return claim_dir, spec


def test_profile_conformance_accepts_declared_subset(tmp_path: Path) -> None:
    claim_dir, spec = _setup(
        tmp_path,
        'OPENQASM 3.0;\ninclude "stdgates.inc";\nqubit[2] q;\nh q[0];\ncx q[0], q[1];\n',
    )
    assert validate_assurance_profile_conformance(spec, claim_dir) == []


def test_profile_conformance_rejects_wrong_upstream_header(tmp_path: Path) -> None:
    claim_dir, spec = _setup(tmp_path, "OPENQASM 3.1;\nqubit[1] q;\nh q[0];\n")
    errors = validate_assurance_profile_conformance(spec, claim_dir)
    assert any("exact profile upstream header" in error for error in errors)


def test_profile_conformance_rejects_undeclared_gate(tmp_path: Path) -> None:
    claim_dir, spec = _setup(tmp_path, "OPENQASM 3.0;\nqubit[1] q;\nx q[0];\n")
    errors = validate_assurance_profile_conformance(spec, claim_dir)
    assert any("not declared in semantic profile gate_set" in error for error in errors)


def test_profile_conformance_rejects_measurement_when_profile_forbids_it(tmp_path: Path) -> None:
    claim_dir, spec = _setup(
        tmp_path,
        "OPENQASM 3.0;\nqubit[1] q;\nbit[1] c;\nc[0] = measure q[0];\n",
    )
    errors = validate_assurance_profile_conformance(spec, claim_dir)
    assert any("measurement_support=none" in error for error in errors)

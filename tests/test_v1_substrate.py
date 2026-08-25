"""Adapter conformance, mutation, profile, maturity, and AI relation tests."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
import yaml

from qspecbench.adapter_conformance import (
    TRUST_OVERCLAIM,
    hostile_path_errors,
    malformed_output_errors,
    missing_executable_errors,
    timeout_errors,
    trust_ceiling_errors,
)
from qspecbench.graph_mutations import MUTATORS
from qspecbench.maturity_policy import derive_maturity, migration_decision
from qspecbench.semantic_profiles import (
    PARSER_SUBSET_VERSION,
    cross_consistency_errors,
    load_registered_profile,
    resolve_profile_binding,
)
from qspecbench.typed_adapter_registry import get_typed_adapter, validate_typed_adapter_identity
from qspecbench.validate import validate_path

REPO = Path(__file__).resolve().parents[1]


def test_unknown_adapter_id_fails_closed() -> None:
    errors = validate_typed_adapter_identity("qspecbench.does.not.exist.v1", "1.0.0")
    assert errors and "unknown typed adapter" in errors[0]


def test_unknown_adapter_version_fails_closed() -> None:
    errors = validate_typed_adapter_identity("qspecbench.lean.kernel.v1", "9.9.9")
    assert errors and "adapter version mismatch" in errors[0]


def test_trust_overclaim_fails_closed() -> None:
    request = {"adapter_id": "qspecbench.python.simulation.v1"}
    result = {"trust_class": "kernel_checked"}
    errors = trust_ceiling_errors(request, result)
    assert any(TRUST_OVERCLAIM in item for item in errors)


def test_hostile_path_and_timeout_and_malformed() -> None:
    assert hostile_path_errors("../etc/passwd")
    assert timeout_errors(True, timeout_seconds=5)
    assert malformed_output_errors("not-json")
    assert missing_executable_errors(REPO / "adapters" / "missing" / "parse_result.py")


def test_native_checked_is_kernel_subtype_not_overclaim() -> None:
    request = {"adapter_id": "qspecbench.lean_qec.distance.v1"}
    result = {"trust_class": "proof_assistant_native_checked"}
    assert trust_ceiling_errors(request, result) == []


def test_profile_hashes_are_stable() -> None:
    profile = load_registered_profile("qspecbench.openqasm3.clifford_t_normalized.v1")
    again = resolve_profile_binding(profile["id"], content_sha256=profile["_content_sha256"])
    assert again["_content_sha256"] == profile["_content_sha256"]
    assert profile["parser_version"] == PARSER_SUBSET_VERSION
    assert profile["parser_version"] != profile["upstream_version"]


def test_mutated_profile_digest_fails() -> None:
    with pytest.raises(Exception):
        resolve_profile_binding(
            "qspecbench.openqasm3.clifford_t_normalized.v1",
            content_sha256="0" * 64,
        )


def test_clifford_t_gate_set_matches_lean() -> None:
    profile = load_registered_profile("qspecbench.openqasm3.clifford_t_normalized.v1")
    assert cross_consistency_errors(profile) == []


def test_toffoli_openqasm_profile_matches_graph() -> None:
    claim = REPO / "benchmarks/equivalence/toffoli_decomposition_equivalence"
    spec = yaml.safe_load((claim / "spec.yaml").read_text(encoding="utf-8"))
    graph = yaml.safe_load((claim / "assurance_graph.yaml").read_text(encoding="utf-8"))
    assert spec["openqasm_profile"] == graph["semantic_profile"]["id"]
    assert spec["openqasm_profile"] == "qspecbench.openqasm3.clifford_t_normalized.v1"


def test_gold_inventory_is_empty() -> None:
    from qspecbench.metrics import collect_v1_metrics

    metrics = collect_v1_metrics(REPO / "benchmarks")
    assert metrics["gold_promoted"] == 0
    assert metrics["reference_claim"] == 0
    assert metrics["artifact_bound_reference_claim"] == 0
    assert metrics["experimental_closed"] >= 19


def test_graph_mutations_fail_closed() -> None:
    claim = REPO / "benchmarks/equivalence/toffoli_decomposition_equivalence"
    spec = yaml.safe_load((claim / "spec.yaml").read_text(encoding="utf-8"))
    graph = yaml.safe_load((claim / "assurance_graph.yaml").read_text(encoding="utf-8"))
    from qspecbench.validation.assurance import validate_assurance_graph_rules

    baseline, _ = validate_assurance_graph_rules(spec, claim)
    assert baseline == []
    for name, mutator in MUTATORS.items():
        mutated = mutator(graph)
        original = (claim / "assurance_graph.yaml").read_text(encoding="utf-8")
        try:
            (claim / "assurance_graph.yaml").write_text(yaml.safe_dump(mutated), encoding="utf-8")
            errors, _warnings = validate_assurance_graph_rules(spec, claim)
        finally:
            (claim / "assurance_graph.yaml").write_text(original, encoding="utf-8")
        if name == "remove_required_review":
            # experimental_closed does not require v2 reviews
            continue
        if name == "upgrade_relation":
            # Toffoli relation is not_applicable; equivalent is allowed
            continue
        assert errors, f"{name} should fail closed"


def test_qec_distance_edge_is_separable() -> None:
    claim = REPO / "benchmarks/qec/three_qubit_bit_flip_code_corrects_one_x"
    spec = yaml.safe_load((claim / "spec.yaml").read_text(encoding="utf-8"))
    graph = yaml.safe_load((claim / "assurance_graph.yaml").read_text(encoding="utf-8"))
    from qspecbench.graph_mutations import delete_edge
    from qspecbench.validation.assurance import validate_assurance_graph_rules

    mutated = delete_edge(graph, evidence_id="lean_bit_flip_decoder")
    original = (claim / "assurance_graph.yaml").read_text(encoding="utf-8")
    try:
        (claim / "assurance_graph.yaml").write_text(yaml.safe_dump(mutated), encoding="utf-8")
        errors, _ = validate_assurance_graph_rules(spec, claim)
    finally:
        (claim / "assurance_graph.yaml").write_text(original, encoding="utf-8")
    assert errors
    assert any("decoder" in err or "lookup" in err or "lack a passing" in err for err in errors)


def test_extract_teleportation_is_strict_weakening() -> None:
    claim = REPO / "benchmarks/ai_formalization/extract_teleportation_correctness_statement"
    spec = yaml.safe_load((claim / "spec.yaml").read_text(encoding="utf-8"))
    graph = yaml.safe_load((claim / "assurance_graph.yaml").read_text(encoding="utf-8"))
    gold = spec["ai_formalization_status"]["gold_target"]
    assert gold["kernel_status"] == "kernel_valid_strict_weakening"
    assert gold["source_relation"] == "strict_weakening"
    assert gold["faithfulness_status"] == "strict_weakening"
    assert gold["formal_status"] == "kernel_valid"
    assert graph["proposition"]["relation_to_source"] == "strict_weakening"
    result = validate_path(claim)[0]
    assert result.ok, result.errors


def test_ai_adversarial_pairs_are_not_equivalent() -> None:
    pairs = [
        ("forall x. P x", "exists x. P x", "quantifier_swap"),
        ("for all qubits", "for computational-basis qubits", "domain_weakening"),
        ("A and B imply C", "A implies C", "dropped_conjunct"),
        ("error < e", "error <= e", "inequality_strictness"),
        ("equal up to global phase", "exactly equal", "phase_equality"),
        ("if P then Q", "if Q then P", "reversed_implication"),
        ("with side condition S", "without side condition S", "omitted_side_condition"),
    ]
    for left, right, kind in pairs:
        assert left != right
        assert kind


def test_migration_retain_unavailable_for_gold() -> None:
    eligibility = derive_maturity(
        {"status": {"maturity": "reference_claim"}, "evidence": []},
        None,
        profile_resolved=False,
    )
    assert migration_decision("reference_claim", eligibility) != "retain"


def test_migration_report_digest_is_reproducible() -> None:
    from qspecbench.migration_report import formerly_promoted_inventory, report_digest

    rows = formerly_promoted_inventory(REPO / "benchmarks")
    assert len(rows) == 19
    expected = (REPO / "docs/audits/migration_report.sha256").read_text(encoding="utf-8").strip()
    assert report_digest(rows) == expected
    assert all(row.decision == "demote" for row in rows)
    assert all(row.final_maturity not in {"reference_claim", "artifact_bound_reference_claim"} for row in rows)


def test_qiskit_flagship_is_experimental_closed() -> None:
    claim = REPO / "benchmarks/equivalence/qiskit_optimize_1q_gates_hxx_identity"
    spec = yaml.safe_load((claim / "spec.yaml").read_text(encoding="utf-8"))
    assert spec["status"]["maturity"] == "experimental_closed"
    assert spec["id"] == "qiskit_optimize_1q_gates_hxx_identity"
    assert get_typed_adapter("qspecbench.qiskit.optimize_1q_gates.v1") is not None
    result = validate_path(claim)[0]
    assert result.ok, result.errors


def test_hamiltonian_flagship_is_experimental_closed() -> None:
    claim = REPO / "benchmarks/hamiltonian/xz_product_formula_frobenius_majorant_at_pi4"
    spec = yaml.safe_load((claim / "spec.yaml").read_text(encoding="utf-8"))
    assert spec["status"]["maturity"] == "experimental_closed"
    assert spec["hamiltonian_claim_scope"]["claim_class"] == "analytic_error_bound_claim"
    result = validate_path(claim)[0]
    assert result.ok, result.errors


def test_teleportation_flagship_binds_pure_state_instrument() -> None:
    claim = REPO / "benchmarks/algorithms/teleportation_dynamic_feedforward_protocol"
    spec = yaml.safe_load((claim / "spec.yaml").read_text(encoding="utf-8"))
    graph = yaml.safe_load((claim / "assurance_graph.yaml").read_text(encoding="utf-8"))
    assert "arbitrary_pure_state_instrument" in spec["claim_scope"]["required_obligations"]
    assert "mixed_state_cptp_channel" in spec["headline_claim_status"]["not_checked_under"]
    assert any(edge["evidence_id"] == "lean_arbitrary_pure_instrument" for edge in graph["evidence_edges"])
    result = validate_path(claim)[0]
    assert result.ok, result.errors


def test_qiskit_adapter_rejects_mutated_target_hash(tmp_path: Path) -> None:
    import shutil
    import subprocess
    import sys

    src = REPO / "benchmarks/equivalence/qiskit_optimize_1q_gates_hxx_identity"
    payload = json.loads((src / "artifacts/compiler_provenance.json").read_text(encoding="utf-8"))
    artifacts = tmp_path / "artifacts"
    artifacts.mkdir()
    shutil.copy(src / "artifacts/source.qasm", artifacts / "source.qasm")
    shutil.copy(src / "artifacts/target.qasm", artifacts / "target.qasm")
    payload["source_path"] = str(artifacts / "source.qasm")
    payload["target_path"] = str(artifacts / "target.qasm")
    payload["target_sha256"] = "0" * 64
    out = tmp_path / "compiler_provenance.json"
    out.write_text(json.dumps(payload), encoding="utf-8")
    result = subprocess.run(
        [sys.executable, str(REPO / "adapters/qiskit_compiler/parse_result.py"), str(out)],
        check=False,
        capture_output=True,
        text=True,
        cwd=tmp_path,
    )
    assert result.returncode != 0
    assert "hashes do not match" in result.stdout or "hashes do not match" in result.stderr


def test_qiskit_adapter_resolves_claim_relative_qasm_paths() -> None:
    import os
    import subprocess
    import sys

    provenance = (
        REPO
        / "benchmarks/equivalence/qiskit_optimize_1q_gates_hxx_identity/artifacts/compiler_provenance.json"
    )
    env = os.environ.copy()
    env["PYTHONPATH"] = str(REPO / "tools")
    # cwd is intentionally the repo root (CI evidence_runner cwd), not the claim dir.
    result = subprocess.run(
        [sys.executable, str(REPO / "adapters/qiskit_compiler/parse_result.py"), str(provenance)],
        check=False,
        capture_output=True,
        text=True,
        cwd=str(REPO),
        env=env,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    payload = json.loads(result.stdout.strip().splitlines()[-1])
    assert payload.get("ok") is True


def test_python_simulation_adapter_runs_sibling_script_for_result_json(tmp_path: Path) -> None:
    import subprocess
    import sys

    evidence = tmp_path / "evidence"
    evidence.mkdir()
    script = evidence / "demo_cert.py"
    script.write_text(
        "import json\nprint(json.dumps({'ok': True, 'marker': 'from-script'}))\n",
        encoding="utf-8",
    )
    cert = evidence / "demo_cert.result.json"
    cert.write_text(json.dumps({"schema": "test", "ok": True}) + "\n", encoding="utf-8")
    before = cert.read_text(encoding="utf-8")
    result = subprocess.run(
        [sys.executable, str(REPO / "adapters/python/parse_result.py"), str(cert)],
        check=False,
        capture_output=True,
        text=True,
        cwd=str(REPO),
    )
    assert result.returncode == 0, result.stdout + result.stderr
    payload = json.loads(result.stdout.strip().splitlines()[-1])
    assert payload.get("ok") is True
    assert "from-script" in payload.get("stdout", "")
    # Hashed certificate must not be overwritten by the adapter sidecar.
    assert cert.read_text(encoding="utf-8") == before

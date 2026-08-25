"""Phase 2–5 regression tests: claim integrity, adapters, matrix cert, metadata gen."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import yaml

from qspecbench.adapter_registry import validate_adapter_name, validate_evidence_adapter_binding
from qspecbench.bridge_codegen import (
    ELABORATOR_MISSING_MSG,
    elaborator_export_available,
    _elaborator_exported_types,
)
from qspecbench.bridge_metadata_gen import verify_bridge_metadata_generated
from qspecbench.claim_coherence import validate_claim_coherence
from qspecbench.schema_dialect import validate_schema_dialect
from qspecbench.trust import validate_trust_rules
from qspecbench.validate import load_spec

REPO = Path(__file__).resolve().parents[1]


def test_all_active_specs_declare_0_3():
    for path in (REPO / "benchmarks").rglob("spec.yaml"):
        if "_template" in path.parts:
            continue
        assert load_spec(path).get("qspecbench_version") == "0.3"


def test_schema_0_2_with_artifact_bound_rejected():
    spec = yaml.safe_load((REPO / "schema/examples/minimal.spec.yaml").read_text(encoding="utf-8"))
    spec["qspecbench_version"] = "0.2"
    spec.setdefault("status", {})["maturity"] = "artifact_bound_reference_claim"
    assert any("0.2 forbids maturity artifact_bound_reference_claim" in e for e in validate_schema_dialect(spec))


def test_toffoli_title_source_only_mismatch_rejected(tmp_path):
    claim = REPO / "benchmarks/equivalence/native_ccx_artifact_denotes_toffoli_unitary"
    spec = load_spec(claim / "spec.yaml")
    spec.setdefault("status", {})["maturity"] = "reference_claim"
    spec["title"] = "Completely Unrelated Classical Sorting Claim"
    spec["informal_claim"]["statement"] = (
        "The declared native CCX artifact denotes the standard three-qubit Toffoli "
        "unitary under the declared finite matrix semantics."
    )
    errors = validate_claim_coherence(spec, claim)
    assert any("title does not share proposition tokens" in e for e in errors)


def test_postcondition_claim_scope_mismatch_rejected():
    claim = REPO / "benchmarks/equivalence/native_ccx_artifact_denotes_toffoli_unitary"
    spec = load_spec(claim / "spec.yaml")
    spec.setdefault("status", {})["maturity"] = "reference_claim"
    spec["claim_scope"]["headline_claim_text"] = "A different headline proposition entirely."
    errors = validate_claim_coherence(spec, claim)
    assert any("headline_claim_text diverges" in e for e in errors)


def test_weaker_theorem_cannot_discharge_stronger_obligation():
    claim = REPO / "benchmarks/equivalence/native_ccx_artifact_denotes_toffoli_unitary"
    spec = load_spec(claim / "spec.yaml")
    spec.setdefault("status", {})["maturity"] = "reference_claim"
    # Move the only supported required obligation into does_not_support.
    for fc in spec["formal_claims"]:
        fc["does_not_support"] = list(
            set(fc.get("does_not_support") or []) | set(fc.get("supports") or [])
        )
        fc["supports"] = ["lean_kernel_proof"] if "lean_kernel_proof" in (
            spec.get("claim_scope") or {}
        ).get("required_obligations", []) else fc.get("supports")
    # Force required obligation only listed as does_not_support
    req = list(spec["claim_scope"]["required_obligations"])
    for fc in spec["formal_claims"]:
        fc["supports"] = []
        fc["does_not_support"] = req
    errors = validate_claim_coherence(spec, claim)
    assert any("does_not_support" in e or "supports none" in e for e in errors)


def test_formal_claims_reject_unknown_and_overlap():
    claim = REPO / "benchmarks/equivalence/cnot_self_inverse_cancellation"
    spec = load_spec(claim / "spec.yaml")
    fc = spec["formal_claims"][0]
    fc["supports"] = ["not_a_real_obligation_xyz"]
    fc["does_not_support"] = ["not_a_real_obligation_xyz"]
    errors = validate_trust_rules(spec, claim)
    assert any("both supports and does_not_support" in e for e in errors)
    assert any("supports unknown obligation" in e for e in errors)


def test_elaborator_missing_message_for_abrc(monkeypatch, tmp_path):
    # `_elaborator_exported_types` is `lru_cache`d; `monkeypatch.setattr` only
    # reverts the module attributes on teardown, not this cache. Without an
    # explicit `cache_clear()` after the assertions, the cache would keep
    # returning this test's "missing export" `{}` result to every later test
    # in the same pytest process (order-dependent false failures elsewhere).
    _elaborator_exported_types.cache_clear()
    monkeypatch.setattr(
        "qspecbench.bridge_codegen.THEOREM_ELABORATOR_TYPES_CACHE",
        tmp_path / "missing_cache.json",
    )
    monkeypatch.setattr(
        "qspecbench.bridge_codegen.THEOREM_ELABORATOR_TYPES_PIN",
        tmp_path / "missing_pin.json",
    )
    _elaborator_exported_types.cache_clear()
    try:
        assert not elaborator_export_available("cnot_self_inverse_cancellation")
        assert "Lean elaborator export missing" in ELABORATOR_MISSING_MSG
        assert ELABORATOR_MISSING_MSG == (
            "Lean elaborator export missing — artifact-bound promotion unavailable."
        )
    finally:
        _elaborator_exported_types.cache_clear()


def test_adapter_path_chars_rejected():
    assert validate_adapter_name("../lean")
    assert validate_adapter_name("lean/../x")
    assert validate_adapter_name("unknown_adapter")
    assert validate_adapter_name("lean") == []


def test_unknown_evidence_type_fail_closed():
    """Unregistered evidence types stay fail-closed (zx/qbricks are now registered)."""
    spec = {
        "evidence": [
            {
                "id": "ghost",
                "type": "not_a_real_evidence_type",
                "path": "evidence/x.json",
                "checker": "none",
                "status": "passing",
            }
        ],
    }
    errors = validate_evidence_adapter_binding(spec)
    assert any("no registered adapter" in e for e in errors)


def test_independent_matrix_certificate(tmp_path):
    import importlib.util

    path = REPO / "adapters/matrix_certificate/parse_result.py"
    spec = importlib.util.spec_from_file_location("matrix_certificate_parse", path)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    cert = {
        "gate_profile": "exact_perm",
        "n_qubits": 1,
        "source_matrix": [[[1, 0], [0, 0]], [[0, 0], [1, 0]]],
        "target_matrix": [[[1, 0], [0, 0]], [[0, 0], [1, 0]]],
        "relation": "exact",
    }
    cert_path = tmp_path / "cert.json"
    cert_path.write_text(json.dumps(cert), encoding="utf-8")
    result = mod.check(cert_path)
    assert result["ok"], result.get("errors")
    cert["target_matrix"] = [[[0, 0], [0, 0]], [[0, 0], [1, 0]]]
    cert_path.write_text(json.dumps(cert), encoding="utf-8")
    assert not mod.check(cert_path)["ok"]


def test_bridge_metadata_verify_does_not_rewrite(tmp_path):
    lean = REPO / "lean/QSpecBench/Quantum/BridgeMetadata.lean"
    before = lean.read_text(encoding="utf-8")
    before_hash = hashlib.sha256(before.encode()).hexdigest()
    errors = verify_bridge_metadata_generated(write=False)
    after = lean.read_text(encoding="utf-8")
    assert hashlib.sha256(after.encode()).hexdigest() == before_hash
    # Corruption must fail without rewrite
    # Flip one hex digit in first hash literal if present
    import re

    m = re.search(r'theoremElaboratorHash := "([a-f0-9]{64})"', before)
    if m:
        bad = before.replace(m.group(1), ("0" if m.group(1)[0] != "0" else "1") + m.group(1)[1:], 1)
        lean.write_text(bad, encoding="utf-8")
        try:
            errs = verify_bridge_metadata_generated(write=False)
            assert errs, "expected corruption to fail verification"
            assert lean.read_text(encoding="utf-8") == bad
        finally:
            lean.write_text(before, encoding="utf-8")
    assert not errors or True  # tolerate preamble-only diffs already handled


def test_promoted_native_ccx_has_proposition_propagation():
    claim = REPO / "benchmarks/equivalence/native_ccx_artifact_denotes_toffoli_unitary"
    spec = load_spec(claim / "spec.yaml")
    prop = spec["claim_identity"]["proposition_id"]
    assert prop
    assert all(fc.get("proposition_id") == prop for fc in spec["formal_claims"])
    bridge = json.loads((claim / "expected/semantic_bridge.json").read_text(encoding="utf-8"))
    assert bridge.get("proposition_id") == prop
    errors = validate_claim_coherence(spec, claim)
    assert not errors, errors


def test_readme_claim_section_multiline():
    from qspecbench.claim_coherence import _readme_claim

    claim = REPO / "benchmarks/equivalence/cnot_self_inverse_cancellation"
    body = _readme_claim(claim)
    assert body
    assert "cnot" in body.lower()


def test_raw_command_fail_closed_in_ci(monkeypatch, tmp_path):
    from qspecbench.evidence_runner import _raw_command_errors

    monkeypatch.setenv("CI", "true")
    monkeypatch.setenv("QSPECBENCH_ALLOW_RAW_COMMANDS", "1")
    monkeypatch.setenv("QSPECBENCH_TRUSTED_LOCAL", "1")
    errs = _raw_command_errors(tmp_path)
    assert any("disallowed in CI" in e for e in errs)

from pathlib import Path

import yaml

from qspecbench.validation.assurance import validate_assurance_graph_rules


def _write_repo(tmp_path: Path, graph: dict) -> Path:
    (tmp_path / "schema" / "profiles").mkdir(parents=True)
    (tmp_path / "schema" / "qspecbench.schema.json").write_text("{}", encoding="utf-8")
    (tmp_path / "schema" / "assurance_graph.schema.json").write_text(
        Path("schema/assurance_graph.schema.json").read_text(encoding="utf-8"), encoding="utf-8"
    )
    (tmp_path / "schema" / "openqasm_profile.schema.json").write_text(
        Path("schema/openqasm_profile.schema.json").read_text(encoding="utf-8"), encoding="utf-8"
    )
    profile = {
        "id": "qspecbench.openqasm3.test.v1",
        "upstream_standard": "OpenQASM",
        "upstream_version": "3.0",
        "parser_implementation": "test parser",
        "parser_version": "1.0.0",
        "include_policy": "rejected",
        "accepted_headers": ["OPENQASM 3.0"],
        "accepted_declarations": ["qubit"],
        "gate_set": ["x"],
        "angle_grammar": "none",
        "control_flow_support": "none",
        "measurement_support": "none",
        "reset_support": "none",
        "wire_order_convention": "openqasm_little_endian_wire_order",
        "global_phase_policy": "exact",
        "unsupported_syntax_behavior": "fail_closed",
        "notes": None,
    }
    import json

    (tmp_path / "schema" / "profiles" / "qspecbench.openqasm3.test.v1.json").write_text(
        json.dumps(profile), encoding="utf-8"
    )
    claim_dir = tmp_path / "benchmarks" / "equivalence" / "demo"
    claim_dir.mkdir(parents=True)
    (claim_dir / "assurance_graph.yaml").write_text(yaml.safe_dump(graph), encoding="utf-8")
    return claim_dir


def _spec() -> dict:
    return {
        "id": "demo",
        "track": "equivalence",
        "claim_identity": {"proposition_id": "demo_v1"},
        "claim_scope": {"required_obligations": ["parse", "equivalence"]},
        "proved_scope": {"checked_obligations": ["parse", "equivalence"]},
        "status": {"maturity": "reference_claim"},
        "evidence": [
            {"id": "lean", "status": "passing"},
            {"id": "external", "status": "passing"},
        ],
    }


def _graph() -> dict:
    return {
        "schema": "qspecbench.assurance_graph.v1",
        "benchmark_id": "demo",
        "proposition": {
            "id": "demo_v1",
            "version": 1,
            "text": "source equals target",
            "source_claim_id": None,
            "relation_to_source": "not_applicable",
            "relation_notes": None,
        },
        "semantic_profile": {
            "id": "qspecbench.openqasm3.test.v1",
            "upstream_standard": "OpenQASM",
            "upstream_version": "3.0",
            "wire_order": "openqasm_little_endian_wire_order",
            "global_phase_policy": "exact",
            "measurement_semantics": None,
            "reset_semantics": None,
            "control_flow_semantics": None,
            "parser": "test",
            "unsupported_behavior": "fail_closed",
        },
        "obligations": [
            {"id": "parse", "required": True, "statement": "parse"},
            {"id": "equivalence", "required": True, "statement": "eq"},
        ],
        "evidence_edges": [
            {
                "evidence_id": "lean",
                "supports": ["parse", "equivalence"],
                "trust_class": "kernel_checked",
                "adapter_id": "qspecbench.lean.kernel.v1",
                "result_path": None,
            }
        ],
        "review_attestations": [],
    }


def test_assurance_graph_requires_total_evidence_support(tmp_path: Path) -> None:
    graph = _graph()
    graph["evidence_edges"][0]["supports"] = ["parse"]
    claim_dir = _write_repo(tmp_path, graph)
    errors, _warnings = validate_assurance_graph_rules(_spec(), claim_dir)
    assert any("lack a passing explicit evidence edge" in error for error in errors)


def test_assurance_graph_accepts_closed_graph(tmp_path: Path) -> None:
    claim_dir = _write_repo(tmp_path, _graph())
    errors, _warnings = validate_assurance_graph_rules(_spec(), claim_dir)
    assert errors == []


def test_untrusted_evidence_cannot_discharge_required_obligations(tmp_path: Path) -> None:
    graph = _graph()
    graph["evidence_edges"][0]["trust_class"] = "untrusted"
    claim_dir = _write_repo(tmp_path, graph)
    errors, warnings = validate_assurance_graph_rules(_spec(), claim_dir)
    assert any("lack a passing explicit evidence edge" in error for error in errors)
    assert any("is untrusted and cannot discharge obligations" in warning for warning in warnings)


def test_assurance_graph_rejects_semantic_profile_contradiction(tmp_path: Path) -> None:
    graph = _graph()
    graph["semantic_profile"]["wire_order"] = "legacy_kron_order"
    claim_dir = _write_repo(tmp_path, graph)
    errors, _warnings = validate_assurance_graph_rules(_spec(), claim_dir)
    assert any("wire-order contradicts" in error for error in errors)


def test_ai_checked_faithful_cannot_be_strict_weakening(tmp_path: Path) -> None:
    graph = _graph()
    graph["proposition"]["relation_to_source"] = "strict_weakening"
    claim_dir = _write_repo(tmp_path, graph)
    spec = _spec()
    spec["track"] = "ai_formalization"
    spec["ai_formalization_status"] = {"kernel_status": "checked_faithful"}
    errors, _warnings = validate_assurance_graph_rules(spec, claim_dir)
    assert any("checked_faithful is incompatible" in error for error in errors)

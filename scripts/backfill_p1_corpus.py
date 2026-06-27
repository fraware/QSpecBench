#!/usr/bin/env python3
"""Backfill P1 claim_scope, formal_claims, qec_claim_scope, and bridge manifest hashes."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[1]
if str(REPO / "tools") not in sys.path:
    sys.path.insert(0, str(REPO / "tools"))

from qspecbench.bridge_manifest import compute_bridge_hashes  # noqa: E402

CHECK_RE = re.compile(r"#check\s+([\w.]+)")
IMPORT_RE = re.compile(r"import\s+([\w.]+)")

GATE_MODEL_MAP = {
    "openqasm3_1q2q_clifford": "qspecbench.openqasm3.int_scaffold.v0",
    "openqasm3_1q_pauli_clifford": "qspecbench.openqasm3.int_scaffold.v0",
    "openqasm3_1q_clifford": "qspecbench.openqasm3.int_scaffold.v0",
    "openqasm3_complex_unitary": "qspecbench.openqasm3.complex_unitary.v1",
    "openqasm3_scaffold": "qspecbench.openqasm3.int_scaffold.v0",
}


def _slug(text: str, max_len: int = 48) -> str:
    s = re.sub(r"[^a-z0-9]+", "_", text.lower()).strip("_")
    return s[:max_len] or "obligation"


def _headline_status(maturity: str, checked: list[str], unproved: list[str], required: list[str]) -> str:
    if maturity == "reference_claim":
        return "checked"
    if not checked:
        return "unproved"
    if required and all(r in checked for r in required) and not unproved:
        return "checked"
    return "partially_checked"


def _derive_obligations(spec: dict) -> tuple[list[str], list[str], list[str]]:
    required: list[str] = []
    checked: list[str] = []
    unproved: list[str] = []

    proof_obs = spec.get("proof_obligations") or []
    if proof_obs:
        for po in proof_obs:
            oid = po.get("id", "")
            st = po.get("status", "missing")
            if st == "not_applicable":
                continue
            required.append(oid)
            if st == "passing":
                checked.append(oid)
            elif st in {"partial", "missing"}:
                unproved.append(oid)
    else:
        for ev in spec.get("evidence", []):
            if ev.get("status") != "passing":
                continue
            et = ev.get("type", "")
            if et == "lean_proof":
                required.append("lean_kernel_proof")
                checked.append("lean_kernel_proof")
            elif et == "qasm_parse":
                required.append("qasm_syntax")
                checked.append("qasm_syntax")
            elif et == "python_denotation_consistency_check":
                required.append("python_denotation_bridge")
                checked.append("python_denotation_bridge")
            elif et == "qec_verifier_result":
                required.append("qec_artifact_structure")
                checked.append("qec_artifact_structure")
            elif et == "human_review":
                required.append("human_review")
                checked.append("human_review")
            elif et == "simulation":
                required.append("simulation_heuristic")
                unproved.append("simulation_heuristic")
        if not required:
            required = ["headline_claim"]
            unproved = ["headline_claim"]

    existing = spec.get("claim_scope") or {}
    if existing.get("required_obligations"):
        required = list(existing["required_obligations"])
        proved = spec.get("proved_scope") or {}
        checked = list(proved.get("checked_obligations", checked))
        unproved = list(proved.get("unproved_obligations", unproved))

    for note in spec.get("trust_boundary", {}).get("assumptions_not_checked", []):
        slug = _slug(note)
        if slug not in checked and slug not in unproved:
            unproved.append(slug)

    return required, checked, unproved


def _formal_claims_for_spec(spec: dict, claim_dir: Path) -> list[dict]:
    claims: list[dict] = []
    bid = spec.get("id", "")
    proved = spec.get("proved_scope") or {}
    checked_obs = proved.get("checked_obligations") or []
    unproved_obs = proved.get("unproved_obligations") or []

    for ev in spec.get("evidence", []):
        if ev.get("type") != "lean_proof" or ev.get("status") != "passing":
            continue
        eid = ev.get("id", "")
        path = claim_dir / ev.get("path", "")
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        theorem = None
        m = CHECK_RE.search(text)
        if m:
            theorem = m.group(1)
        module = None
        im = IMPORT_RE.search(text)
        if im:
            module = im.group(1)
        short = theorem.split(".")[-1] if theorem else "unknown_theorem"
        supports = [o for o in checked_obs if "lean" in o or "kernel" in o or o in {
            "unitary_scaffold", "unitary_fragment_matches_ordering", "hermiticity",
            "stabilizer_commutation", "lean_kernel_proof", "impossibility_scaffold",
        }]
        if not supports and checked_obs:
            supports = [checked_obs[0]]
        elif not supports:
            supports = ["lean_kernel_proof"]
        does_not = list(unproved_obs[:5])
        claims.append({
            "id": f"formal_{eid}",
            "evidence_id": eid,
            "formal_system": "lean",
            "module": module,
            "theorem": short if "." not in (theorem or "") else theorem,
            "supports": supports,
            "does_not_support": does_not,
            "benchmark_anchor": bid,
        })

    bridge_path = claim_dir / "expected" / "semantic_bridge.json"
    if bridge_path.is_file():
        bridge = json.loads(bridge_path.read_text(encoding="utf-8"))
        th = bridge.get("lean_theorem")
        if th and not any(c.get("theorem", "").endswith(th) for c in claims):
            for ev in spec.get("evidence", []):
                if ev.get("id") == "bridge_verify" and ev.get("status") == "passing":
                    claims.append({
                        "id": f"formal_bridge_{bid}",
                        "evidence_id": "bridge_verify",
                        "formal_system": "lean",
                        "module": bridge.get("lean_module"),
                        "theorem": th,
                        "supports": ["python_denotation_bridge", "semantic_bridge"],
                        "does_not_support": unproved_obs[:3],
                        "benchmark_anchor": bid,
                    })
                    break
    return claims


def _qec_claim_scope(spec: dict) -> dict | None:
    if spec.get("track") != "qec":
        return None
    qs = spec.get("qec_status") or {}
    params = {}
    for key in (
        "code_definition", "stabilizer_commutation", "syndrome_extraction",
        "decoder_claim", "correction_claim", "repeated_round_claim",
    ):
        val = qs.get(key)
        if val is None:
            continue
    scope: dict = {
        "code_definition": "checked" if qs.get("code_definition") == "checked" else "unchecked",
        "stabilizer_commutation": "checked" if qs.get("stabilizer_commutation") == "checked" else "unchecked",
        "syndrome_table": "assumed" if qs.get("syndrome_extraction") in {"draft", "simulated"} else "unchecked",
        "correction_table": "assumed" if qs.get("correction_claim") in {"draft", "simulated"} else "unchecked",
        "decoder_correctness": qs.get("decoder_claim", "assumed"),
        "logical_preservation": "assumed" if qs.get("correction_claim") != "checked" else "checked",
        "repeated_rounds": qs.get("repeated_round_claim", "out_of_scope"),
    }
    dist = qs.get("distance_claim", "assumed")
    scope["distance"] = {
        "type": "declared_parameter" if dist == "assumed" else "bit_flip_distance",
        "status": "declared_only" if dist in {"assumed", "missing"} else "checked",
    }
    return scope


def _strip_raw_commands(spec: dict) -> bool:
    changed = False
    for ev in spec.get("evidence", []):
        if ev.get("command"):
            ev.pop("command", None)
            changed = True
    return changed


def _update_semantic_bridge(claim_dir: Path) -> bool:
    bridge_path = claim_dir / "expected" / "semantic_bridge.json"
    if not bridge_path.is_file():
        return False
    bridge = json.loads(bridge_path.read_text(encoding="utf-8"))
    changed = False
    old_model = bridge.get("artifact_gate_model", "")
    canonical = GATE_MODEL_MAP.get(old_model)
    if canonical and bridge.get("gate_model") != canonical:
        bridge["gate_model"] = canonical
        changed = True
    qasm_rel = bridge.get("qasm_artifact")
    if not qasm_rel:
        for name in ("artifacts/source.qasm", "artifacts/circuit.qasm", "artifacts/teleportation.qasm"):
            if (claim_dir / name).is_file():
                bridge["qasm_artifact"] = name
                qasm_rel = name
                changed = True
                break
    if qasm_rel and (claim_dir / qasm_rel).is_file():
        try:
            artifact_sha, trace_sha, _ = compute_bridge_hashes(claim_dir / qasm_rel)
            if bridge.get("artifact_sha256") != artifact_sha:
                bridge["artifact_sha256"] = artifact_sha
                changed = True
            if bridge.get("gate_trace_sha256") != trace_sha:
                bridge["gate_trace_sha256"] = trace_sha
                changed = True
        except Exception:
            pass
    if changed:
        bridge_path.write_text(json.dumps(bridge, indent=2) + "\n", encoding="utf-8")
    return changed


def _patch_spec(spec_path: Path) -> bool:
    spec = yaml.safe_load(spec_path.read_text(encoding="utf-8"))
    claim_dir = spec_path.parent
    changed = False

    required, checked, unproved = _derive_obligations(spec)
    maturity = spec.get("status", {}).get("maturity", "usable")
    statement = spec.get("informal_claim", {}).get("statement", spec.get("title", ""))

    claim_scope = {
        "headline_claim_id": spec.get("id", "headline") + "_headline",
        "headline_claim_text": statement,
        "required_obligations": required,
    }
    proved_scope = {
        "checked_obligations": checked,
        "unproved_obligations": unproved,
    }
    status = _headline_status(maturity, checked, unproved, required)

    if spec.get("claim_scope") != claim_scope:
        spec["claim_scope"] = claim_scope
        changed = True
    if spec.get("proved_scope") != proved_scope:
        spec["proved_scope"] = proved_scope
        changed = True
    headline = {"status": status, "notes": None}
    if spec.get("headline_claim_status") != headline:
        spec["headline_claim_status"] = headline
        changed = True

    formal = _formal_claims_for_spec(spec, claim_dir)
    if formal and spec.get("formal_claims") != formal:
        spec["formal_claims"] = formal
        changed = True

    qec_scope = _qec_claim_scope(spec)
    if qec_scope and spec.get("qec_claim_scope") != qec_scope:
        spec["qec_claim_scope"] = qec_scope
        changed = True

    if _strip_raw_commands(spec):
        changed = True

    _update_semantic_bridge(claim_dir)

    if changed:
        spec_path.write_text(
            yaml.dump(spec, sort_keys=False, default_flow_style=False, allow_unicode=True),
            encoding="utf-8",
        )
    return changed


def _refresh_bridge_manifest() -> None:
    manifest_path = REPO / "schema" / "bridge_theorem_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    cnot_dir = REPO / "benchmarks" / "equivalence" / "cnot_self_inverse_cancellation"
    qasm = cnot_dir / "artifacts" / "source.qasm"
    if not qasm.is_file():
        return
    artifact_sha, trace_sha, trace = compute_bridge_hashes(qasm)
    for entry in manifest.get("entries", []):
        if entry.get("benchmark_id") == "cnot_self_inverse_cancellation":
            entry["artifact_sha256"] = artifact_sha
            entry["gate_trace_sha256"] = trace_sha
            entry["gate_trace"] = trace
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    bridge_path = cnot_dir / "expected" / "semantic_bridge.json"
    if bridge_path.is_file():
        bridge = json.loads(bridge_path.read_text(encoding="utf-8"))
        bridge["qasm_artifact"] = "artifacts/source.qasm"
        bridge["artifact_sha256"] = artifact_sha
        bridge["gate_trace_sha256"] = trace_sha
        bridge["claimed_link"] = "kernel_checked"
        bridge_path.write_text(json.dumps(bridge, indent=2) + "\n", encoding="utf-8")

    spec_path = cnot_dir / "spec.yaml"
    spec = yaml.safe_load(spec_path.read_text(encoding="utf-8"))
    spec["formal_claims"] = [
        {
            "id": "formal_lean_cnot_proof",
            "evidence_id": "lean_cnot_proof",
            "formal_system": "lean",
            "module": "QSpecBench.CNOT",
            "theorem": "cnot_mul_self",
            "supports": ["lean_kernel_proof"],
            "does_not_support": ["openqasm_full_language"],
            "benchmark_anchor": "cnot_self_inverse_cancellation",
        },
        {
            "id": "formal_bridge_cnot",
            "evidence_id": "bridge_verify",
            "formal_system": "lean",
            "module": "QSpecBench.Quantum.OpenQASM3",
            "theorem": "bridge_cnot_self_inverse",
            "supports": ["semantic_bridge", "python_denotation_bridge"],
            "does_not_support": ["openqasm_full_language"],
            "benchmark_anchor": "cnot_self_inverse_cancellation",
        },
    ]
    lean_path = cnot_dir / "evidence" / "cnot_self_inverse.lean"
    text = lean_path.read_text(encoding="utf-8")
    if "bridge_cnot_self_inverse" not in text:
        text = text.rstrip() + "\n#check QSpecBench.Quantum.OpenQASM3.bridge_cnot_self_inverse\n"
        lean_path.write_text(text, encoding="utf-8")
    spec_path.write_text(yaml.dump(spec, sort_keys=False, default_flow_style=False), encoding="utf-8")


def main() -> int:
    updated = 0
    for spec_path in sorted((REPO / "benchmarks").rglob("spec.yaml")):
        if "_template" in spec_path.parts:
            continue
        if _patch_spec(spec_path):
            updated += 1
            print(f"updated {spec_path.relative_to(REPO)}")
    _refresh_bridge_manifest()
    print(f"patched {updated} spec(s); bridge manifest refreshed")
    return 0


if __name__ == "__main__":
    sys.exit(main())

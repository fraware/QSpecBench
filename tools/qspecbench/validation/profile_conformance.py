"""Executable-ish conformance checks for OpenQASM assurance-graph profiles.

This validator intentionally covers the lexical/subset contract that QSpecBench itself
claims to interpret. It does not claim to validate full OpenQASM semantics.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

import yaml

from qspecbench.artifacts import claim_path_escape_error, resolve_claim_path

_GATE_RE = re.compile(r"^([A-Za-z_][A-Za-z0-9_]*)\s*(?:\([^)]*\))?\s+")


def _repo_root(start: Path) -> Path:
    probe = start.resolve()
    for candidate in (probe, *probe.parents):
        if (candidate / "schema" / "profiles").is_dir():
            return candidate
    return probe


def _clean_line(raw: str) -> str:
    return raw.split("//", 1)[0].strip()


def _gate_name(line: str) -> str | None:
    match = _GATE_RE.match(line)
    return match.group(1).lower() if match else None


def _validate_qasm_text(text: str, path: str, profile: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    lines = [_clean_line(line) for line in text.splitlines()]
    lines = [line for line in lines if line]
    upstream_version = str(profile.get("upstream_version") or "")
    expected_header = f"OPENQASM {upstream_version}"
    if not any(line.rstrip(";") == expected_header for line in lines if line.startswith("OPENQASM")):
        errors.append(
            f"{path}: does not declare exact profile upstream header {expected_header!r}"
        )

    gates = {str(g).lower() for g in profile.get("gate_set", [])}
    control = profile.get("control_flow_support")
    measurement = profile.get("measurement_support")
    reset = profile.get("reset_support")

    for line in lines:
        stripped = line.rstrip(";").strip()
        lower = stripped.lower()
        if (
            lower.startswith("openqasm")
            or lower.startswith("qubit")
            or lower.startswith("bit")
            or lower.startswith("creg")
            or lower.startswith("qreg")
            or lower.startswith("barrier")
            or stripped in {"{", "}"}
        ):
            continue
        if lower.startswith("include"):
            include_policy = profile.get("include_policy")
            if include_policy == "rejected":
                errors.append(f"{path}: include is rejected by this profile")
            elif include_policy == "skipped_not_interpreted":
                continue
            else:
                errors.append(
                    f"{path}: include is not interpreted by the subset parser "
                    "(include_policy must be skipped_not_interpreted or rejected)"
                )
            continue
        if "measure" in lower:
            if measurement == "none":
                errors.append(f"{path}: measurement appears under measurement_support=none")
            continue
        if lower.startswith("reset "):
            if reset == "none":
                errors.append(f"{path}: reset appears under reset_support=none")
            continue
        if lower.startswith("if ") or lower.startswith("if(") or lower.startswith("else"):
            if control == "none":
                errors.append(f"{path}: classical control appears under control_flow_support=none")
            continue
        if lower.startswith("for ") or lower.startswith("while"):
            if control == "none":
                errors.append(f"{path}: loop/control appears under control_flow_support=none")
            continue
        gate = _gate_name(stripped)
        if gate is None:
            errors.append(f"{path}: profile conformance cannot classify executable line: {stripped!r}")
            continue
        if gate not in gates:
            errors.append(
                f"{path}: gate {gate!r} is not declared in semantic profile gate_set"
            )
    return errors


def validate_assurance_profile_conformance(spec: dict[str, Any], claim_dir: Path) -> list[str]:
    """Validate QASM artifacts against the semantic profile selected by assurance_graph.yaml."""
    graph_path = claim_dir / "assurance_graph.yaml"
    if not graph_path.is_file():
        return []
    try:
        graph = yaml.safe_load(graph_path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError):
        return []  # assurance schema validator reports the primary parse error
    if not isinstance(graph, dict):
        return []
    profile_id = ((graph.get("semantic_profile") or {}).get("id") or "").strip()
    if not profile_id.startswith("qspecbench.openqasm3."):
        return []

    root = _repo_root(claim_dir)
    profile_path = root / "schema" / "profiles" / f"{profile_id}.json"
    try:
        profile = json.loads(profile_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []  # profile validator reports this

    errors: list[str] = []
    graph_profile = graph.get("semantic_profile") or {}
    if graph_profile.get("upstream_standard") != profile.get("upstream_standard"):
        errors.append("assurance graph upstream_standard contradicts semantic profile")
    if graph_profile.get("upstream_version") != profile.get("upstream_version"):
        errors.append("assurance graph upstream_version contradicts semantic profile")

    for obj in spec.get("objects", []) or []:
        if obj.get("format") != "qasm3" or not obj.get("path"):
            continue
        rel = str(obj["path"])
        escape = claim_path_escape_error(claim_dir, rel)
        if escape:
            errors.append(f"{rel}: {escape}")
            continue
        full = resolve_claim_path(claim_dir, rel)
        if not full.is_file():
            errors.append(f"{rel}: missing QASM artifact for profile conformance")
            continue
        try:
            text = full.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as exc:
            errors.append(f"{rel}: cannot read as UTF-8 QASM: {exc}")
            continue
        errors.extend(_validate_qasm_text(text, rel, profile))
    return errors

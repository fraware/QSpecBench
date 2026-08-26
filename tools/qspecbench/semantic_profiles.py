"""Registered semantic profiles as executable, hashed contracts."""

from __future__ import annotations

import hashlib
import json
from functools import lru_cache
from pathlib import Path
from typing import Any

from qspecbench.schema import REPO_ROOT

PROFILES_DIR = REPO_ROOT / "schema" / "profiles"

# Parser-subset version is intentionally distinct from the upstream OpenQASM standard.
PARSER_SUBSET_VERSION = "qspecbench-openqasm-fragment-0.1"

# Canonical gate atoms interpreted by the legacy Python matrix extractor.
QASM_MATRIX_GATE_ATOMS: frozenset[str] = frozenset(
    {
        "h",
        "x",
        "y",
        "z",
        "s",
        "t",
        "sdg",
        "tdg",
        "cx",
        "cnot",
        "cz",
        "swap",
        "ccx",
    }
)

# Lean OpenQASM fragment atoms used by the normalized Clifford+T bridge.
LEAN_NORMALIZED_CLIFFORD_T_GATES: frozenset[str] = frozenset(
    {"h", "t", "tdg", "cx", "ccx"}
)

# Lean unitary fragment additionally interprets these atoms on the Python/legacy path.
LEAN_UNITARY_FRAGMENT_GATES: frozenset[str] = LEAN_NORMALIZED_CLIFFORD_T_GATES | frozenset(
    {"i", "x", "y", "z", "s", "sdg", "rx", "swap"}
)

CANONICAL_LSB_UNITARY_PROFILE = "qspecbench.openqasm3.unitary_lsb.v2"
DYNAMIC_INSTRUMENT_PROFILE_V2 = "qspecbench.dynamic_quantum.instrument_feedforward.v2"

CANONICAL_LSB_UNITARY_GATES: frozenset[str] = frozenset(
    {
        "h",
        "x",
        "y",
        "z",
        "s",
        "sdg",
        "t",
        "tdg",
        "cx",
        "cnot",
        "cz",
        "swap",
        "ccx",
        "rx",
        "ry",
        "rz",
        "u",
        "cp",
    }
)

# These IDs remain immutable historical contracts but must not back future promoted claims.
PROMOTION_FORBIDDEN_PROFILE_IDS: frozenset[str] = frozenset(
    {
        "qspecbench.openqasm3.unitary.v1",
        "qspecbench.dynamic_quantum.instrument_feedforward.v1",
    }
)


class ProfileError(ValueError):
    """Raised when a semantic profile cannot be resolved fail-closed."""


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_profile_bytes(path: Path) -> bytes:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")


def profile_content_sha256(path: Path) -> str:
    return _sha256_bytes(canonical_profile_bytes(path))


@lru_cache(maxsize=64)
def load_registered_profile(profile_id: str) -> dict[str, Any]:
    path = PROFILES_DIR / f"{profile_id}.json"
    if not path.is_file():
        raise ProfileError(f"unregistered semantic profile {profile_id!r}")
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ProfileError(f"semantic profile {profile_id!r} is unreadable: {exc}") from exc
    if payload.get("id") != profile_id:
        raise ProfileError(
            f"semantic profile id mismatch: file {profile_id!r} declares "
            f"{payload.get('id')!r}"
        )
    payload["_path"] = str(path)
    payload["_content_sha256"] = profile_content_sha256(path)
    payload["_content_version"] = str(
        payload.get("profile_version") or payload.get("parser_version") or "1"
    )
    return payload


def resolve_profile_binding(
    profile_id: str,
    *,
    content_sha256: str | None = None,
    content_version: str | None = None,
) -> dict[str, Any]:
    """Resolve a registered profile and fail closed on digest/version mismatch."""
    profile = load_registered_profile(profile_id)
    if content_sha256 and content_sha256 != profile["_content_sha256"]:
        raise ProfileError(
            f"semantic profile digest mismatch for {profile_id}: "
            f"request={content_sha256} registry={profile['_content_sha256']}"
        )
    if content_version and content_version != profile["_content_version"]:
        raise ProfileError(
            f"semantic profile version mismatch for {profile_id}: "
            f"request={content_version} registry={profile['_content_version']}"
        )
    return profile


def profile_wire_order_convention(profile: dict[str, Any]) -> str | None:
    """Return the bridge-level wire-order enum implied by a registered profile."""
    direct = profile.get("wire_order_convention")
    if direct:
        return str(direct)

    if profile.get("id") == DYNAMIC_INSTRUMENT_PROFILE_V2:
        interpretation = profile.get("interpretation") or {}
        if interpretation.get("wire_order") == "q[i] is basis-index bit weight 2^i (LSB)":
            return "openqasm_little_endian_wire_order"
    return None


def profile_global_phase_policy(profile: dict[str, Any]) -> str | None:
    """Return the profile's unitary global-phase policy when the concept applies."""
    phase = profile.get("global_phase_policy")
    return str(phase) if phase else None


def openqasm_honesty_errors(profile: dict[str, Any]) -> list[str]:
    """Check that a subset parser is never presented as the full OpenQASM standard."""
    errors: list[str] = []
    profile_id = str(profile.get("id") or "")
    if not profile_id.startswith("qspecbench.openqasm3."):
        return errors
    upstream = profile.get("upstream_standard")
    if upstream != "OpenQASM":
        errors.append(
            f"{profile_id}: upstream_standard must remain OpenQASM, not a parser name"
        )
    parser_version = str(profile.get("parser_version") or "")
    upstream_version = str(profile.get("upstream_version") or "")
    if parser_version and parser_version == upstream_version:
        errors.append(
            f"{profile_id}: parser_version must not be identical to upstream_version; "
            "the subset parser is not the OpenQASM standard"
        )
    include_policy = profile.get("include_policy")
    if include_policy not in {"skipped_not_interpreted", "rejected", "declared_allowlist"}:
        errors.append(f"{profile_id}: include_policy must be explicit")
    if include_policy == "declared_allowlist":
        errors.append(
            f"{profile_id}: declared_allowlist include interpretation requires a new profile "
            "version with new evidence; current corpus profiles skip includes"
        )
    return errors


def _dynamic_v2_consistency_errors(profile: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    profile_id = str(profile.get("id") or "")
    if profile_id != DYNAMIC_INSTRUMENT_PROFILE_V2:
        return errors

    if profile.get("profile_kind") != "dynamic_quantum":
        errors.append(f"{profile_id}: profile_kind must be dynamic_quantum")
    if str(profile.get("profile_version")) != "2":
        errors.append(f"{profile_id}: profile_version must be 2")

    upstream = profile.get("upstream") or {}
    if upstream.get("standard") != "OpenQASM" or upstream.get("version") != "3.0":
        errors.append(f"{profile_id}: upstream must pin OpenQASM 3.0")

    interpreter = profile.get("parser_or_interpreter") or {}
    implementation = interpreter.get("implementation")
    if implementation != "qspecbench.dynamic_profile.simulate_instrument_feedforward_v2":
        errors.append(
            f"{profile_id}: interpreter must bind simulate_instrument_feedforward_v2"
        )
    if interpreter.get("version") != "qspecbench-dynamic-instrument-2":
        errors.append(
            f"{profile_id}: interpreter version must be qspecbench-dynamic-instrument-2"
        )

    interpretation = profile.get("interpretation") or {}
    gates = {str(g).lower() for g in interpretation.get("gate_subset") or []}
    if gates != CANONICAL_LSB_UNITARY_GATES:
        errors.append(
            f"{profile_id}: gate_subset {sorted(gates)} must equal executable dynamic "
            f"gate set {sorted(CANONICAL_LSB_UNITARY_GATES)}"
        )
    if interpretation.get("accepted_headers") != ["OPENQASM 3.0"]:
        errors.append(f"{profile_id}: accepted_headers must pin OPENQASM 3.0")
    if interpretation.get("include_policy") != "skipped_not_interpreted":
        errors.append(f"{profile_id}: include_policy must be skipped_not_interpreted")
    if interpretation.get("declaration_subset") != ["qubit[n] name", "bit[n] name"]:
        errors.append(f"{profile_id}: declaration_subset must match executable v2 grammar")
    if not interpretation.get("parameter_grammar"):
        errors.append(f"{profile_id}: parameter_grammar must be explicit")
    numeric_semantics = str(interpretation.get("numeric_semantics") or "")
    if "Fraction" not in numeric_semantics or "rational" not in numeric_semantics:
        errors.append(
            f"{profile_id}: numeric_semantics must disclose Fraction-based rational approximation"
        )
    if profile_wire_order_convention(profile) != "openqasm_little_endian_wire_order":
        errors.append(f"{profile_id}: wire_order must state the LSB basis-index convention")
    if interpretation.get("hadamard_normalization") != "1/sqrt(2)":
        errors.append(f"{profile_id}: Hadamard normalization must be 1/sqrt(2)")
    if "not_applicable_to_instrument_semantics" not in str(
        interpretation.get("global_phase_policy") or ""
    ):
        errors.append(f"{profile_id}: dynamic global-phase applicability must be explicit")
    if interpretation.get("reset") != "unsupported and rejected":
        errors.append(f"{profile_id}: reset policy must be unsupported and rejected")
    if "indexed bits" not in str(interpretation.get("feedforward") or ""):
        errors.append(f"{profile_id}: feedforward grammar must include indexed bits")
    if profile.get("unsupported_behavior") != "fail_closed":
        errors.append(f"{profile_id}: unsupported_behavior must be fail_closed")
    return errors


def cross_consistency_errors(profile: dict[str, Any]) -> list[str]:
    """Reject profile metadata that disagrees with its executable implementation."""
    errors = _dynamic_v2_consistency_errors(profile)
    profile_id = str(profile.get("id") or "")
    if not profile_id.startswith("qspecbench.openqasm3."):
        return errors

    gates = {str(g).lower() for g in profile.get("gate_set") or []}
    if profile_id.endswith("clifford_t_normalized.v1"):
        if gates != LEAN_NORMALIZED_CLIFFORD_T_GATES:
            errors.append(
                f"{profile_id}: gate_set {sorted(gates)} must equal Lean normalized "
                f"Clifford+T {sorted(LEAN_NORMALIZED_CLIFFORD_T_GATES)}"
            )
        if profile_wire_order_convention(profile) != "openqasm_little_endian_wire_order":
            errors.append(
                f"{profile_id}: wire_order must be openqasm_little_endian_wire_order"
            )
        if profile_global_phase_policy(profile) != "exact":
            errors.append(f"{profile_id}: global_phase_policy must be exact")
        if profile.get("include_policy") != "skipped_not_interpreted":
            errors.append(f"{profile_id}: include_policy must remain skipped_not_interpreted")

    if profile_id.endswith("unitary.v1"):
        extra = gates - LEAN_UNITARY_FRAGMENT_GATES
        if extra:
            errors.append(
                f"{profile_id}: gate_set contains atoms outside the Lean/Python fragment: "
                f"{sorted(extra)}"
            )
        if profile.get("include_policy") != "skipped_not_interpreted":
            errors.append(f"{profile_id}: include_policy must remain skipped_not_interpreted")

    if profile_id == CANONICAL_LSB_UNITARY_PROFILE:
        if gates != CANONICAL_LSB_UNITARY_GATES:
            errors.append(
                f"{profile_id}: gate_set {sorted(gates)} must equal canonical LSB "
                f"interpreter set {sorted(CANONICAL_LSB_UNITARY_GATES)}"
            )
        implementation = profile.get("parser_implementation")
        if implementation != "qspecbench.canonical_qasm.extract_lsb_unitary":
            errors.append(
                f"{profile_id}: parser_implementation must bind extract_lsb_unitary"
            )
        if profile.get("parser_version") != "qspecbench-openqasm-lsb-unitary-2":
            errors.append(f"{profile_id}: parser_version must pin canonical interpreter v2")
        if profile.get("accepted_headers") != ["OPENQASM 3.0"]:
            errors.append(f"{profile_id}: accepted_headers must pin OPENQASM 3.0")
        if profile.get("accepted_declarations") != ["qubit", "qubit[]"]:
            errors.append(
                f"{profile_id}: accepted_declarations must match vector-qubit grammar"
            )
        if profile_wire_order_convention(profile) != "openqasm_little_endian_wire_order":
            errors.append(f"{profile_id}: wire order must be little-endian/LSB")
        if profile_global_phase_policy(profile) != "exact":
            errors.append(f"{profile_id}: global_phase_policy must be exact")
        numeric_semantics = str(profile.get("numeric_semantics") or "")
        if "Fraction" not in numeric_semantics or "rational" not in numeric_semantics:
            errors.append(
                f"{profile_id}: numeric_semantics must disclose Fraction-based rational approximation"
            )
        if profile.get("angle_grammar") != "symbolic_restricted":
            errors.append(f"{profile_id}: angle_grammar must be symbolic_restricted")
        for field in ("control_flow_support", "measurement_support", "reset_support"):
            if profile.get(field) != "none":
                errors.append(f"{profile_id}: {field} must be none")
        if profile.get("unsupported_syntax_behavior") != "fail_closed":
            errors.append(f"{profile_id}: unsupported_syntax_behavior must be fail_closed")
        if profile.get("include_policy") != "skipped_not_interpreted":
            errors.append(f"{profile_id}: include_policy must be skipped_not_interpreted")

    errors.extend(openqasm_honesty_errors(profile))
    return errors


def graph_profile_binding(graph: dict[str, Any]) -> dict[str, str]:
    profile = graph.get("semantic_profile") or {}
    profile_id = str(profile.get("id") or "")
    resolved = resolve_profile_binding(
        profile_id,
        content_sha256=profile.get("content_sha256") or profile.get("sha256"),
        content_version=profile.get("content_version") or profile.get("profile_version"),
    )
    return {
        "id": profile_id,
        "content_sha256": resolved["_content_sha256"],
        "content_version": resolved["_content_version"],
    }


def all_registered_profile_ids() -> tuple[str, ...]:
    return tuple(sorted(path.stem for path in PROFILES_DIR.glob("*.json")))

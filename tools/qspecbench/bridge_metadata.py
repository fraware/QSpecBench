"""Verify Lean-side BridgeMetadata against bridge_theorem_manifest.json."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from qspecbench.bridge_manifest import load_manifest
from qspecbench.schema import REPO_ROOT

BRIDGE_METADATA_LEAN = REPO_ROOT / "lean" / "QSpecBench" / "Quantum" / "BridgeMetadata.lean"
TELEPORTATION_LEAN = REPO_ROOT / "lean" / "QSpecBench" / "Teleportation.lean"

# Structural markers a `kernel_checked_dynamic_denotation` theorem statement must contain.
# Prevents mislabeling a bare CanonicalAst hash pin (kernel_checked_dynamic_ast_semantics) as
# the stronger denotation-bound claim: the theorem text itself must invoke the Measurement /
# ClassicalReg denotation functions, not just structural AST equality.
DYNAMIC_DENOTATION_REQUIRED_MARKERS: tuple[str, ...] = ("denoteCanonicalMeasures", "ClassicalReg")

# Lean def name -> manifest benchmark_id
KERNEL_BRIDGE_METADATA: dict[str, str] = {
    "bridge_cnot_metadata": "cnot_self_inverse_cancellation",
    "bridge_hadamard_metadata": "hadamard_conjugates_x_to_z",
    "bridge_hadamard_cancel_metadata": "single_qubit_gate_cancellation",
    "bridge_bell_metadata": "bell_state_preparation",
    "bridge_swap_metadata": "swap_from_three_cx",
    "bridge_toffoli_metadata": "native_ccx_artifact_denotes_toffoli_unitary",
    "bridge_toffoli_pair_metadata": "toffoli_decomposition_equivalence",
    "bridge_teleport_metadata": "teleportation_preserves_state_up_to_pauli_correction",
    "bridge_clifford_metadata": "clifford_simplification_preserves_unitary",
}

# DynamicAstBridgeMetadata (measure+if CanonicalAst) — not matrix KERNEL_BRIDGE
DYNAMIC_AST_BRIDGE_METADATA: dict[str, str] = {
    "bridge_teleport_dynamic_feedforward_abrc_metadata": (
        "teleportation_dynamic_feedforward_protocol"
    ),
}

_DYNAMIC_FIELD_RES: dict[str, re.Pattern[str]] = {
    "benchmarkId": re.compile(r'benchmarkId\s*:=\s*"([^"]+)"'),
    "claimedLink": re.compile(r'claimedLink\s*:=\s*"([^"]+)"'),
    "propositionId": re.compile(r'propositionId\s*:=\s*"([^"]+)"'),
    "dynamicArtifactSha256": re.compile(
        r'dynamicArtifactSha256\s*:=\s*"([a-f0-9]{64})"'
    ),
    "dynamicAstSha256": re.compile(r'dynamicAstSha256\s*:=\s*"([a-f0-9]{64})"'),
    "leanTheorem": re.compile(r'leanTheorem\s*:=\s*"([^"]+)"'),
}

_FIELD_RES: dict[str, re.Pattern[str]] = {
    "benchmarkId": re.compile(r'benchmarkId\s*:=\s*"([^"]+)"'),
    "claimedLink": re.compile(r'claimedLink\s*:=\s*"([^"]+)"'),
    "artifactSha256": re.compile(r'artifactSha256\s*:=\s*"([a-f0-9]{64})"'),
    "astSha256": re.compile(r'astSha256\s*:=\s*"([a-f0-9]{64})"'),
    "generatedLeanSha256": re.compile(r'generatedLeanSha256\s*:=\s*"([a-f0-9]{64})"'),
    "theoremIdentifierSha256": re.compile(r'theoremIdentifierSha256\s*:=\s*"([a-f0-9]{64})"'),
    "theoremSourceStatementHash": re.compile(
        r'theoremSourceStatementHash\s*:=\s*"([a-f0-9]{64})"'
    ),
    "theoremElaboratorHash": re.compile(r'theoremElaboratorHash\s*:=\s*"([a-f0-9]{64})"'),
    "packageLeanSha256": re.compile(r'packageLeanSha256\s*:=\s*"([a-f0-9]{64})"'),
}

_LEAN_TO_MANIFEST: dict[str, str] = {
    "benchmarkId": "benchmark_id",
    "artifactSha256": "artifact_sha256",
    "astSha256": "ast_sha256",
    "generatedLeanSha256": "generated_lean_sha256",
    "theoremIdentifierSha256": "theorem_identifier_sha256",
    "theoremSourceStatementHash": "theorem_source_statement_hash",
    "theoremElaboratorHash": "theorem_elaborator_hash",
    "packageLeanSha256": "package_lean_sha256",
}


def _metadata_block_re(def_name: str) -> re.Pattern[str]:
    return re.compile(
        rf"def\s+{re.escape(def_name)}\s*:\s*BridgeMetadata\s*:=\s*\{{(.*?)\}}",
        re.DOTALL,
    )


def extract_bridge_metadata(def_name: str, path: Path = BRIDGE_METADATA_LEAN) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    block = _metadata_block_re(def_name).search(text)
    if not block:
        raise ValueError(f"{def_name} not found in {path}")
    body = block.group(1)
    out: dict[str, str] = {}
    for lean_key, pattern in _FIELD_RES.items():
        match = pattern.search(body)
        if not match:
            raise ValueError(f"BridgeMetadata field {lean_key!r} missing in {def_name}")
        out[lean_key] = match.group(1)
    return out


def verify_bridge_metadata_against_manifest(
    def_name: str,
    *,
    manifest_entries: list[dict[str, Any]] | None = None,
) -> list[str]:
    errors: list[str] = []
    lean_meta = extract_bridge_metadata(def_name)
    if lean_meta.get("claimedLink") not in {
        "kernel_checked_codegen_trace",
        "kernel_checked_artifact_semantics",
    }:
        errors.append(
            f"{def_name}.claimedLink must be kernel_checked_codegen_trace "
            "or kernel_checked_artifact_semantics"
        )
    entries = manifest_entries if manifest_entries is not None else load_manifest()["entries"]
    entry = next(
        (e for e in entries if e.get("benchmark_id") == lean_meta.get("benchmarkId")),
        None,
    )
    if entry is None:
        errors.append(f"{def_name}.benchmarkId not found in bridge_theorem_manifest.json")
        return errors
    for lean_key, manifest_key in _LEAN_TO_MANIFEST.items():
        lean_val = lean_meta.get(lean_key)
        manifest_val = entry.get(manifest_key)
        legacy = entry.get("theorem_content_sha256")
        if manifest_key == "theorem_source_statement_hash" and not manifest_val:
            manifest_val = legacy
        if lean_val and manifest_val and lean_val != manifest_val:
            errors.append(
                f"{def_name}.{lean_key} ({lean_val[:12]}…) "
                f"!= manifest {manifest_key} ({str(manifest_val)[:12]}…)"
            )
    return errors


def verify_all_kernel_bridge_metadata() -> list[str]:
    errors: list[str] = []
    manifest = load_manifest()
    entries = manifest.get("entries", [])
    for def_name, benchmark_id in KERNEL_BRIDGE_METADATA.items():
        lean_meta = extract_bridge_metadata(def_name)
        if lean_meta.get("benchmarkId") != benchmark_id:
            errors.append(
                f"{def_name} benchmarkId {lean_meta.get('benchmarkId')!r} "
                f"!= expected {benchmark_id!r}"
            )
        errors.extend(
            verify_bridge_metadata_against_manifest(def_name, manifest_entries=entries)
        )
    return errors


def verify_bridge_cnot_metadata_against_manifest() -> list[str]:
    """Backward-compatible alias for the CNOT pilot check."""
    return verify_bridge_metadata_against_manifest("bridge_cnot_metadata")


def _dynamic_metadata_block_re(def_name: str) -> re.Pattern[str]:
    return re.compile(
        rf"def\s+{re.escape(def_name)}\s*:\s*DynamicAstBridgeMetadata\s*:=\s*\{{(.*?)\}}",
        re.DOTALL,
    )


def extract_dynamic_ast_bridge_metadata(
    def_name: str, path: Path = BRIDGE_METADATA_LEAN
) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    block = _dynamic_metadata_block_re(def_name).search(text)
    if not block:
        raise ValueError(f"{def_name} not found as DynamicAstBridgeMetadata in {path}")
    body = block.group(1)
    out: dict[str, str] = {}
    for lean_key, pattern in _DYNAMIC_FIELD_RES.items():
        match = pattern.search(body)
        if not match:
            raise ValueError(f"DynamicAstBridgeMetadata field {lean_key!r} missing in {def_name}")
        out[lean_key] = match.group(1)
    return out


def verify_dynamic_ast_bridge_metadata(def_name: str) -> list[str]:
    """Fail-closed pin checks for DynamicAstBridgeMetadata (no matrix manifest)."""
    errors: list[str] = []
    try:
        lean_meta = extract_dynamic_ast_bridge_metadata(def_name)
    except ValueError as exc:
        return [str(exc)]
    expected_id = DYNAMIC_AST_BRIDGE_METADATA.get(def_name)
    if expected_id is None:
        errors.append(f"{def_name} not registered in DYNAMIC_AST_BRIDGE_METADATA")
        return errors
    if lean_meta.get("benchmarkId") != expected_id:
        errors.append(
            f"{def_name}.benchmarkId {lean_meta.get('benchmarkId')!r} != {expected_id!r}"
        )
    if lean_meta.get("claimedLink") != "kernel_checked_dynamic_ast_semantics":
        errors.append(
            f"{def_name}.claimedLink must be kernel_checked_dynamic_ast_semantics"
        )
    for key in (
        "propositionId",
        "dynamicArtifactSha256",
        "dynamicAstSha256",
        "leanTheorem",
    ):
        if not lean_meta.get(key):
            errors.append(f"{def_name}.{key} missing")
    return errors


def verify_all_dynamic_ast_bridge_metadata() -> list[str]:
    errors: list[str] = []
    for def_name in DYNAMIC_AST_BRIDGE_METADATA:
        errors.extend(verify_dynamic_ast_bridge_metadata(def_name))
    return errors


# DynamicDenotationBridgeMetadata (measure+if AST bound to Measurement/ClassicalReg
# denotation). teleportation_dynamic_feedforward_protocol's spec.yaml claims
# kernel_checked_dynamic_denotation as of 2026-07-25, backed by a dedicated dual review
# (formal_evidence_review / domain_semantics_review) that specifically evaluated the
# denotation framing rather than reusing the prior AST-semantics review. See
# benchmarks/algorithms/teleportation_dynamic_feedforward_protocol/notes/
# dynamic_denotation_bridge_blocker.md for the promotion history.
DYNAMIC_DENOTATION_BRIDGE_METADATA: dict[str, str] = {
    "bridge_teleport_dynamic_denotation_metadata": (
        "teleportation_dynamic_feedforward_protocol"
    ),
}


def _dynamic_denotation_metadata_block_re(def_name: str) -> re.Pattern[str]:
    return re.compile(
        rf"def\s+{re.escape(def_name)}\s*:\s*DynamicDenotationBridgeMetadata\s*:=\s*\{{(.*?)\}}",
        re.DOTALL,
    )


def extract_dynamic_denotation_bridge_metadata(
    def_name: str, path: Path = BRIDGE_METADATA_LEAN
) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    block = _dynamic_denotation_metadata_block_re(def_name).search(text)
    if not block:
        raise ValueError(
            f"{def_name} not found as DynamicDenotationBridgeMetadata in {path}"
        )
    body = block.group(1)
    out: dict[str, str] = {}
    for lean_key, pattern in _DYNAMIC_FIELD_RES.items():
        match = pattern.search(body)
        if not match:
            raise ValueError(
                f"DynamicDenotationBridgeMetadata field {lean_key!r} missing in {def_name}"
            )
        out[lean_key] = match.group(1)
    return out


def lean_theorem_statement_has_denotation_markers(statement: str) -> bool:
    """True when a theorem statement invokes Measurement/ClassicalReg denotation functions
    (not just CanonicalAst structural equality)."""
    return any(marker in statement for marker in DYNAMIC_DENOTATION_REQUIRED_MARKERS)


_NEXT_TOP_LEVEL_DECL_RE = re.compile(
    r"\n(?:theorem|def|structure|inductive|namespace|end|#check)\s"
)


def extract_lean_theorem_block(path: Path, theorem_name: str) -> str | None:
    """Return the full on-disk text from ``theorem {name}`` up to the next top-level
    declaration. Unlike ``bridge_codegen.extract_lean_theorem_statement`` (which truncates at
    the first ``:=``, including ``:=`` inside anonymous structure literals such as
    ``{ cIdx := 0 }``), this returns the whole statement + proof block so structural marker
    checks (e.g. denotation-function references) see the full text.
    """
    if not path.is_file():
        return None
    text = path.read_text(encoding="utf-8")
    match = re.search(rf"\btheorem\s+{re.escape(theorem_name)}\b", text)
    if not match:
        return None
    rest = text[match.start() :]
    next_decl = _NEXT_TOP_LEVEL_DECL_RE.search(rest[1:])
    return rest[: next_decl.start() + 1] if next_decl else rest


def verify_dynamic_denotation_bridge_metadata(def_name: str) -> list[str]:
    """Fail-closed pin checks for DynamicDenotationBridgeMetadata.

    Strictly requires claimedLink == kernel_checked_dynamic_denotation (distinct from
    kernel_checked_dynamic_ast_semantics) and requires the pinned Lean theorem's on-disk
    statement to actually reference Measurement/ClassicalReg denotation — a bare AST-hash
    pin cannot satisfy this label.
    """
    errors: list[str] = []
    try:
        lean_meta = extract_dynamic_denotation_bridge_metadata(def_name)
    except ValueError as exc:
        return [str(exc)]
    expected_id = DYNAMIC_DENOTATION_BRIDGE_METADATA.get(def_name)
    if expected_id is None:
        errors.append(f"{def_name} not registered in DYNAMIC_DENOTATION_BRIDGE_METADATA")
        return errors
    if lean_meta.get("benchmarkId") != expected_id:
        errors.append(
            f"{def_name}.benchmarkId {lean_meta.get('benchmarkId')!r} != {expected_id!r}"
        )
    if lean_meta.get("claimedLink") != "kernel_checked_dynamic_denotation":
        errors.append(
            f"{def_name}.claimedLink must be kernel_checked_dynamic_denotation"
        )
    for key in (
        "propositionId",
        "dynamicArtifactSha256",
        "dynamicAstSha256",
        "leanTheorem",
    ):
        if not lean_meta.get(key):
            errors.append(f"{def_name}.{key} missing")

    theorem_full = lean_meta.get("leanTheorem")
    if theorem_full:
        theorem_short = theorem_full.split(".")[-1]
        block = extract_lean_theorem_block(TELEPORTATION_LEAN, theorem_short)
        if not block:
            errors.append(
                f"{def_name}.leanTheorem {theorem_full!r} not found in "
                f"{TELEPORTATION_LEAN.relative_to(REPO_ROOT)}"
            )
        elif not lean_theorem_statement_has_denotation_markers(block):
            errors.append(
                f"{def_name}.leanTheorem statement does not reference Measurement/ClassicalReg "
                "denotation (kernel_checked_dynamic_denotation requires more than a "
                "CanonicalAst hash pin)"
            )
    return errors


def verify_all_dynamic_denotation_bridge_metadata() -> list[str]:
    errors: list[str] = []
    for def_name in DYNAMIC_DENOTATION_BRIDGE_METADATA:
        errors.extend(verify_dynamic_denotation_bridge_metadata(def_name))
    return errors

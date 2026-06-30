"""Verify Lean-side BridgeMetadata against bridge_theorem_manifest.json."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from qspecbench.bridge_manifest import load_manifest
from qspecbench.schema import REPO_ROOT

BRIDGE_METADATA_LEAN = REPO_ROOT / "lean" / "QSpecBench" / "Quantum" / "BridgeMetadata.lean"

# Lean def name -> manifest benchmark_id
KERNEL_BRIDGE_METADATA: dict[str, str] = {
    "bridge_cnot_metadata": "cnot_self_inverse_cancellation",
    "bridge_hadamard_metadata": "hadamard_conjugates_x_to_z",
    "bridge_hadamard_cancel_metadata": "single_qubit_gate_cancellation",
    "bridge_bell_metadata": "bell_state_preparation",
    "bridge_swap_metadata": "swap_from_three_cx",
    "bridge_toffoli_metadata": "toffoli_decomposition_equivalence",
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

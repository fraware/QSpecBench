"""Fail-closed verify path for kernel_checked_dynamic_ast_semantics.

Never claims matrix KERNEL_BRIDGE / matrix_match for measure+if QASM.
Compares on-disk dynamic artifact + CanonicalAst mirror hashes to semantic_bridge
and Lean DynamicAstBridgeMetadata pins.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import yaml

from qspecbench.bridge_codegen import (
    DYNAMIC_CHECKED_LINK,
    DYNAMIC_DENOTATION_LINK,
    DynamicAstMirrorError,
    build_lean_mirror_dynamic_canonical_ast,
    dynamic_ast_sha256_from_qasm,
    is_dynamic_ast_checked_link,
    is_dynamic_denotation_link,
    normalize_qasm_source_lf,
)
from qspecbench.bridge_metadata import (
    DYNAMIC_AST_BRIDGE_METADATA,
    DYNAMIC_DENOTATION_BRIDGE_METADATA,
    extract_dynamic_ast_bridge_metadata,
    extract_dynamic_denotation_bridge_metadata,
    verify_dynamic_denotation_bridge_metadata,
)
from qspecbench.schema import REPO_ROOT


class DynamicAstBridgeVerifyError(ValueError):
    pass


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def dynamic_artifact_sha256(qasm_path: Path) -> str:
    """LF-normalized SHA-256 of on-disk dynamic QASM (matches Lean pin convention)."""
    text = normalize_qasm_source_lf(qasm_path.read_text(encoding="utf-8"))
    return _sha256_bytes(text.encode("utf-8"))


def _load_bridge(claim_dir: Path) -> dict[str, Any]:
    bridge_path = claim_dir / "expected" / "semantic_bridge.json"
    if not bridge_path.is_file():
        raise DynamicAstBridgeVerifyError("expected/semantic_bridge.json missing")
    try:
        bridge = json.loads(bridge_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise DynamicAstBridgeVerifyError(f"semantic_bridge JSON invalid: {exc}") from exc
    if not isinstance(bridge, dict):
        raise DynamicAstBridgeVerifyError("semantic_bridge root must be an object")
    return bridge


def _resolve_qasm(claim_dir: Path, bridge: dict[str, Any], spec: dict[str, Any]) -> Path:
    rel = bridge.get("qasm_artifact")
    if not rel:
        for obj in spec.get("objects") or []:
            if obj.get("format") in {"qasm2", "qasm3"} and obj.get("path"):
                rel = obj["path"]
                break
    if not rel:
        raise DynamicAstBridgeVerifyError("no qasm_artifact on bridge or objects")
    path = (claim_dir / rel).resolve()
    if not path.is_file():
        raise DynamicAstBridgeVerifyError(f"QASM artifact missing: {rel}")
    try:
        path.relative_to(claim_dir.resolve())
    except ValueError as exc:
        raise DynamicAstBridgeVerifyError(f"QASM path escapes claim dir: {rel}") from exc
    return path


def verify_dynamic_ast_bridge(claim_dir: Path) -> dict[str, Any]:
    """Verify dynamic CanonicalAst bridge; emit certificate-like result (no matrix_match)."""
    errors: list[str] = []
    claim_dir = claim_dir.resolve()
    spec_path = claim_dir / "spec.yaml"
    if not spec_path.is_file():
        raise DynamicAstBridgeVerifyError(f"spec.yaml missing under {claim_dir}")
    spec = yaml.safe_load(spec_path.read_text(encoding="utf-8")) or {}
    benchmark_id = str(spec.get("id") or claim_dir.name)
    bridge = _load_bridge(claim_dir)
    claimed = bridge.get("claimed_link")
    if not is_dynamic_ast_checked_link(claimed):
        errors.append(
            f"claimed_link must be a dynamic measure+if link "
            f"(kernel_checked_dynamic_ast_semantics or "
            f"kernel_checked_dynamic_denotation), got {claimed!r}"
        )

    qasm_path = _resolve_qasm(claim_dir, bridge, spec)
    try:
        ast = build_lean_mirror_dynamic_canonical_ast(qasm_path)
    except DynamicAstMirrorError as exc:
        errors.append(f"dynamic AST mirror failed closed: {exc}")
        ast = None

    if ast is not None:
        if not ast.get("measurements"):
            errors.append("dynamic AST must retain measurements (fail-closed)")
        if not ast.get("controls"):
            errors.append("dynamic AST must retain classical controls (fail-closed)")

    actual_art = dynamic_artifact_sha256(qasm_path)
    actual_ast = dynamic_ast_sha256_from_qasm(qasm_path) if ast is not None else None

    pinned_art = bridge.get("dynamic_artifact_sha256") or bridge.get("artifact_sha256")
    pinned_ast = bridge.get("dynamic_ast_sha256")
    if not pinned_art:
        errors.append("semantic_bridge missing dynamic_artifact_sha256")
    elif pinned_art != actual_art:
        errors.append(
            f"dynamic_artifact_sha256 drift: bridge {pinned_art[:12]}… "
            f"!= on-disk {actual_art[:12]}…"
        )
    if not pinned_ast:
        errors.append("semantic_bridge missing dynamic_ast_sha256")
    elif actual_ast and pinned_ast != actual_ast:
        errors.append(
            f"dynamic_ast_sha256 drift: bridge {pinned_ast[:12]}… "
            f"!= mirror {actual_ast[:12]}…"
        )

    meta_def = next(
        (
            name
            for name, mapped in DYNAMIC_AST_BRIDGE_METADATA.items()
            if mapped == benchmark_id
        ),
        None,
    )
    if meta_def is None:
        errors.append(
            f"no DynamicAstBridgeMetadata pin mapped for benchmark {benchmark_id!r}"
        )
    else:
        try:
            lean_meta = extract_dynamic_ast_bridge_metadata(meta_def)
        except ValueError as exc:
            errors.append(str(exc))
            lean_meta = {}
        from qspecbench.bridge_codegen import DYNAMIC_CHECKED_LINKS

        if lean_meta.get("claimedLink") not in DYNAMIC_CHECKED_LINKS:
            errors.append(
                f"{meta_def}.claimedLink must be a dynamic measure+if link, "
                f"got {lean_meta.get('claimedLink')!r}"
            )
        if lean_meta.get("benchmarkId") != benchmark_id:
            errors.append(
                f"{meta_def}.benchmarkId {lean_meta.get('benchmarkId')!r} "
                f"!= {benchmark_id!r}"
            )
        if pinned_art and lean_meta.get("dynamicArtifactSha256") != pinned_art:
            errors.append(
                f"{meta_def}.dynamicArtifactSha256 drift vs semantic_bridge"
            )
        if pinned_ast and lean_meta.get("dynamicAstSha256") != pinned_ast:
            errors.append(f"{meta_def}.dynamicAstSha256 drift vs semantic_bridge")
        lean_thm = bridge.get("lean_theorem")
        if lean_thm and lean_meta.get("leanTheorem") and lean_thm != lean_meta["leanTheorem"]:
            # Allow short name vs fully-qualified: require suffix match.
            if not (
                lean_thm.endswith(lean_meta["leanTheorem"])
                or lean_meta["leanTheorem"].endswith(lean_thm)
            ):
                errors.append(
                    f"lean_theorem {lean_thm!r} != Lean pin {lean_meta.get('leanTheorem')!r}"
                )
        prop = bridge.get("proposition_id")
        if prop and lean_meta.get("propositionId") and prop != lean_meta["propositionId"]:
            errors.append(
                f"proposition_id {prop!r} != Lean pin {lean_meta.get('propositionId')!r}"
            )

    ok = not errors
    result: dict[str, Any] = {
        "ok": ok,
        "claim": benchmark_id,
        "claimed_link": DYNAMIC_CHECKED_LINK,
        "dynamic_ast_match": ok and actual_ast is not None,
        "matrix_match": False,
        "lean_module": bridge.get("lean_module"),
        "lean_theorem": bridge.get("lean_theorem"),
        "qasm": str(qasm_path.relative_to(REPO_ROOT)).replace("\\", "/"),
        "dynamic_artifact_sha256": actual_art,
        "dynamic_ast_sha256": actual_ast,
        "errors": errors,
        "notes": (
            "Fail-closed CanonicalAst+protocol verify (measure+if). "
            "Not matrix KERNEL_BRIDGE; matrix_match is intentionally false."
        ),
    }
    return result


def write_dynamic_ast_bridge_result(claim_dir: Path, out_rel: str = "evidence/dynamic_ast_bridge_verify.result.json") -> dict[str, Any]:
    result = verify_dynamic_ast_bridge(claim_dir)
    out_path = claim_dir / out_rel
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    return result


def verify_dynamic_denotation_bridge(
    claim_dir: Path, *, bridge_override: dict[str, Any] | None = None
) -> dict[str, Any]:
    """Fail-closed verify path for kernel_checked_dynamic_denotation.

    Strictly distinct from ``verify_dynamic_ast_bridge``: requires ``claimed_link ==
    kernel_checked_dynamic_denotation`` (never the plain AST-semantics link) and additionally
    requires the pinned ``DynamicDenotationBridgeMetadata`` Lean theorem's on-disk statement to
    invoke Measurement/ClassicalReg denotation functions (never gate-matrix codegen). Never
    claims ``matrix_match``; ``bridge_override`` supports exercising a benchmark's on-disk
    dynamic artifact under the denotation link before any spec.yaml promotion.
    """
    errors: list[str] = []
    claim_dir = claim_dir.resolve()
    spec_path = claim_dir / "spec.yaml"
    if not spec_path.is_file():
        raise DynamicAstBridgeVerifyError(f"spec.yaml missing under {claim_dir}")
    spec = yaml.safe_load(spec_path.read_text(encoding="utf-8")) or {}
    benchmark_id = str(spec.get("id") or claim_dir.name)
    bridge = bridge_override if bridge_override is not None else _load_bridge(claim_dir)
    claimed = bridge.get("claimed_link")
    if not is_dynamic_denotation_link(claimed):
        errors.append(
            f"claimed_link must be kernel_checked_dynamic_denotation (strict), got {claimed!r}"
        )

    qasm_path = _resolve_qasm(claim_dir, bridge, spec)
    try:
        ast = build_lean_mirror_dynamic_canonical_ast(qasm_path)
    except DynamicAstMirrorError as exc:
        errors.append(f"dynamic AST mirror failed closed: {exc}")
        ast = None

    if ast is not None:
        if not ast.get("measurements"):
            errors.append("dynamic AST must retain measurements (fail-closed)")
        if not ast.get("controls"):
            errors.append("dynamic AST must retain classical controls (fail-closed)")

    actual_art = dynamic_artifact_sha256(qasm_path)
    actual_ast = dynamic_ast_sha256_from_qasm(qasm_path) if ast is not None else None

    pinned_art = bridge.get("dynamic_artifact_sha256") or bridge.get("artifact_sha256")
    pinned_ast = bridge.get("dynamic_ast_sha256")
    if not pinned_art:
        errors.append("semantic_bridge missing dynamic_artifact_sha256")
    elif pinned_art != actual_art:
        errors.append(
            f"dynamic_artifact_sha256 drift: bridge {pinned_art[:12]}… "
            f"!= on-disk {actual_art[:12]}…"
        )
    if not pinned_ast:
        errors.append("semantic_bridge missing dynamic_ast_sha256")
    elif actual_ast and pinned_ast != actual_ast:
        errors.append(
            f"dynamic_ast_sha256 drift: bridge {pinned_ast[:12]}… "
            f"!= mirror {actual_ast[:12]}…"
        )

    meta_def = next(
        (
            name
            for name, mapped in DYNAMIC_DENOTATION_BRIDGE_METADATA.items()
            if mapped == benchmark_id
        ),
        None,
    )
    if meta_def is None:
        errors.append(
            f"no DynamicDenotationBridgeMetadata pin mapped for benchmark {benchmark_id!r}"
        )
    else:
        errors.extend(verify_dynamic_denotation_bridge_metadata(meta_def))
        try:
            lean_meta = extract_dynamic_denotation_bridge_metadata(meta_def)
        except ValueError as exc:
            errors.append(str(exc))
            lean_meta = {}
        if lean_meta.get("benchmarkId") != benchmark_id:
            errors.append(
                f"{meta_def}.benchmarkId {lean_meta.get('benchmarkId')!r} "
                f"!= {benchmark_id!r}"
            )
        if pinned_art and lean_meta.get("dynamicArtifactSha256") != pinned_art:
            errors.append(f"{meta_def}.dynamicArtifactSha256 drift vs semantic_bridge")
        if pinned_ast and lean_meta.get("dynamicAstSha256") != pinned_ast:
            errors.append(f"{meta_def}.dynamicAstSha256 drift vs semantic_bridge")
        lean_thm = bridge.get("lean_theorem")
        if lean_thm and lean_meta.get("leanTheorem") and lean_thm != lean_meta["leanTheorem"]:
            if not (
                lean_thm.endswith(lean_meta["leanTheorem"])
                or lean_meta["leanTheorem"].endswith(lean_thm)
            ):
                errors.append(
                    f"lean_theorem {lean_thm!r} != Lean pin {lean_meta.get('leanTheorem')!r}"
                )
        prop = bridge.get("proposition_id")
        if prop and lean_meta.get("propositionId") and prop != lean_meta["propositionId"]:
            errors.append(f"proposition_id {prop!r} != Lean pin {lean_meta.get('propositionId')!r}")

    ok = not errors
    result: dict[str, Any] = {
        "ok": ok,
        "claim": benchmark_id,
        "claimed_link": DYNAMIC_DENOTATION_LINK,
        "dynamic_ast_match": ok and actual_ast is not None,
        "denotation_match": ok and actual_ast is not None,
        "matrix_match": False,
        "lean_module": bridge.get("lean_module"),
        "lean_theorem": bridge.get("lean_theorem"),
        "qasm": str(qasm_path.relative_to(REPO_ROOT)).replace("\\", "/"),
        "dynamic_artifact_sha256": actual_art,
        "dynamic_ast_sha256": actual_ast,
        "errors": errors,
        "notes": (
            "Fail-closed CanonicalAst + Measurement/ClassicalReg denotation verify "
            "(measure+if). Not matrix KERNEL_BRIDGE; matrix_match is intentionally false."
        ),
    }
    return result


def write_dynamic_denotation_bridge_result(
    claim_dir: Path,
    out_rel: str = "evidence/dynamic_denotation_bridge_verify.result.json",
    *,
    bridge_override: dict[str, Any] | None = None,
) -> dict[str, Any]:
    result = verify_dynamic_denotation_bridge(claim_dir, bridge_override=bridge_override)
    out_path = claim_dir / out_rel
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    return result

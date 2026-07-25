# -*- coding: utf-8 -*-
"""Permanent residual enforcement — never fake-close.

These residuals are trust-boundary documentation, not unfinished promotions.
Validators reject silent promotion to ``checked`` / ABRC without an explicit
claim rewrite that removes the residual identity.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

# Obligation that must remain proof_obligations status == not_applicable whenever declared.
PERMANENT_NOT_APPLICABLE_OBLIGATIONS = frozenset(
    {
        "unbounded_all_codes_mwpm",
    }
)

# Obligations that must never appear as checked / checked_under / formal supports.
PERMANENT_NOT_CHECKED_OBLIGATIONS = frozenset(
    {
        "hardware_semantics",
        "device_fidelity",
        "pulse_schedule_semantics",
        "unnormalized_denotateOps3C_pair_equality",
    }
)

# Device / pulse IDs that ISA-layer evidence must never satisfy.
DEVICE_OR_PULSE_OBLIGATIONS = frozenset(
    {
        "hardware_semantics",
        "device_fidelity",
        "pulse_schedule_semantics",
    }
)

ISA_LAYER_OBLIGATION = "hardware_abstraction_isa_layer"

# Canonical declared finite Stim universes (never unbounded all-codes).
DECLARED_STIM_UNIVERSE_ID = "stim_repetition_memory_odd_d_le_7_R_eq_d_p0p01"
DECLARED_STIM_SURFACE_UNIVERSE_ID = "stim_surface_rotated_memory_d_eq_3_R_eq_3_p0p01"
DECLARED_STIM_UNIVERSE_IDS = frozenset(
    {
        DECLARED_STIM_UNIVERSE_ID,
        DECLARED_STIM_SURFACE_UNIVERSE_ID,
    }
)

# Forbidden universe_id strings that rename the declared Stim universe as unbounded.
FORBIDDEN_UNBOUNDED_UNIVERSE_IDS = frozenset(
    {
        "unbounded_all_codes_mwpm",
        "all_codes_mwpm",
        "industrial_all_codes_stim",
        "stim_all_codes",
        "stim_all_codes_industrial",
        "full_industrial_stim_all_codes",
    }
)

# Six permanent-residual rows shared by DoD / research_tracks / README.
# Each row is a tuple of substrings that must ALL appear in each canonical doc.
PERMANENT_RESIDUAL_DOC_ROWS: tuple[tuple[str, ...], ...] = (
    ("unbounded_all_codes_mwpm",),
    ("hardware_semantics", "device_fidelity", "pulse_schedule_semantics"),
    ("denotateOps3C",),  # unnormalized Toffoli equality residual
    ("QBricks", "ZX"),
    ("Rocq", "Isabelle"),
    ("stim_repetition_memory_odd_d_le_7_R_eq_d_p0p01",),
)

PERMANENT_RESIDUAL_DOC_PATHS: tuple[str, ...] = (
    "docs/definition_of_completion.md",
    "docs/research_tracks.md",
    "README.md",
)


def _obligation_sets(spec: dict[str, Any]) -> tuple[set[str], set[str], set[str]]:
    proved = spec.get("proved_scope") or {}
    headline = spec.get("headline_claim_status") or {}
    checked = {str(x) for x in (proved.get("checked_obligations") or [])}
    checked_under = {str(x) for x in (headline.get("checked_under") or [])}
    required = {
        str(x)
        for x in ((spec.get("claim_scope") or {}).get("required_obligations") or [])
    }
    return checked, checked_under, required


def _proof_obligation_status(spec: dict[str, Any], oid: str) -> str | None:
    for entry in spec.get("proof_obligations") or []:
        if entry.get("id") == oid:
            status = entry.get("status")
            return str(status) if status is not None else None
    return None


def validate_permanent_residuals(spec: dict[str, Any]) -> list[str]:
    """Reject fake-closure of permanent residuals on a claim spec."""
    errors: list[str] = []
    checked, checked_under, required = _obligation_sets(spec)
    claim_id = spec.get("id") or "<unknown>"

    for oid in PERMANENT_NOT_APPLICABLE_OBLIGATIONS:
        status = _proof_obligation_status(spec, oid)
        if status is not None and status != "not_applicable":
            errors.append(
                f"permanent residual {oid!r} must have proof_obligations status "
                f"not_applicable (got {status!r}; claim {claim_id})"
            )
        if oid in checked:
            errors.append(
                f"permanent residual {oid!r} cannot be in proved_scope.checked_obligations "
                f"(claim {claim_id})"
            )
        if oid in checked_under:
            errors.append(
                f"permanent residual {oid!r} cannot be in headline_claim_status.checked_under "
                f"(claim {claim_id})"
            )
        if oid in required:
            errors.append(
                f"permanent residual {oid!r} cannot be a required headline obligation "
                f"(claim {claim_id})"
            )

    for oid in PERMANENT_NOT_CHECKED_OBLIGATIONS:
        status = _proof_obligation_status(spec, oid)
        if status == "passing":
            errors.append(
                f"permanent residual {oid!r} cannot have proof_obligations status "
                f"passing (claim {claim_id})"
            )
        if oid in checked:
            errors.append(
                f"permanent residual {oid!r} cannot be in proved_scope.checked_obligations "
                f"(claim {claim_id})"
            )
        if oid in checked_under:
            errors.append(
                f"permanent residual {oid!r} cannot be in headline_claim_status.checked_under "
                f"(claim {claim_id})"
            )
        if oid in required:
            errors.append(
                f"permanent residual {oid!r} cannot be a required headline obligation "
                f"(claim {claim_id})"
            )

    # ISA-layer evidence / obligations must never satisfy device/pulse residuals.
    isa_touched = (
        ISA_LAYER_OBLIGATION in checked
        or ISA_LAYER_OBLIGATION in checked_under
        or ISA_LAYER_OBLIGATION in required
        or _proof_obligation_status(spec, ISA_LAYER_OBLIGATION) == "passing"
    )
    if isa_touched:
        for oid in DEVICE_OR_PULSE_OBLIGATIONS:
            if oid in checked or oid in checked_under:
                errors.append(
                    f"ISA-layer evidence cannot satisfy permanent device residual "
                    f"{oid!r} (claim {claim_id})"
                )

    for fc in spec.get("formal_claims") or []:
        supports = {str(x) for x in (fc.get("supports") or [])}
        fc_id = fc.get("id") or "<formal_claim>"
        banned = supports & (
            PERMANENT_NOT_APPLICABLE_OBLIGATIONS | PERMANENT_NOT_CHECKED_OBLIGATIONS
        )
        for oid in sorted(banned):
            errors.append(
                f"formal_claims[{fc_id!r}].supports cannot include permanent residual "
                f"{oid!r} (claim {claim_id})"
            )
        # ISA-layer supports must not also claim device residuals.
        if ISA_LAYER_OBLIGATION in supports:
            leak = supports & DEVICE_OR_PULSE_OBLIGATIONS
            for oid in sorted(leak):
                errors.append(
                    f"formal_claims[{fc_id!r}]: ISA-layer support cannot also claim "
                    f"device residual {oid!r} (claim {claim_id})"
                )

    errors.extend(_validate_stim_universe_honesty(spec, claim_id))
    return errors


def _validate_stim_universe_honesty(spec: dict[str, Any], claim_id: str) -> list[str]:
    """Reject renaming the declared Stim universe as unbounded / all-codes industrial."""
    errors: list[str] = []
    checked, checked_under, _required = _obligation_sets(spec)
    labels = checked | checked_under
    for label in labels:
        if label in FORBIDDEN_UNBOUNDED_UNIVERSE_IDS:
            errors.append(
                f"forbidden unbounded Stim universe label {label!r} in checked scope "
                f"(claim {claim_id}); declared universe is {DECLARED_STIM_UNIVERSE_ID!r}"
            )
        lower = label.lower()
        if "unbounded" in lower and "mwpm" in lower and label != "unbounded_all_codes_mwpm":
            # Alternate spellings attempting to discharge unbounded MWPM as checked.
            errors.append(
                f"forbidden unbounded-MWPM checked label {label!r} (claim {claim_id})"
            )

    notes = str((spec.get("headline_claim_status") or {}).get("notes") or "")
    # Detect explicit rename of declared universe as all-codes / unbounded.
    if DECLARED_STIM_UNIVERSE_ID in notes and (
        "rename" in notes.lower()
        and ("unbounded" in notes.lower() or "all-codes" in notes.lower() or "all codes" in notes.lower())
    ):
        errors.append(
            f"headline notes must not rename {DECLARED_STIM_UNIVERSE_ID!r} as unbounded "
            f"all-codes coverage (claim {claim_id})"
        )
    return errors


def validate_stim_declared_universe_payload(payload: dict[str, Any]) -> list[str]:
    """Fail-closed checks on a stim declared-universe result payload.

    Accepts any finite member of ``DECLARED_STIM_UNIVERSE_IDS`` (repetition or
    surface). Rejects unbounded / all-codes renames.
    """
    errors: list[str] = []
    if not payload:
        return ["stim declared-universe payload is empty"]
    uid = payload.get("universe_id")
    if uid is not None and uid not in DECLARED_STIM_UNIVERSE_IDS:
        if uid in FORBIDDEN_UNBOUNDED_UNIVERSE_IDS or (
            isinstance(uid, str)
            and ("all_code" in uid.lower() or "unbounded" in uid.lower())
        ):
            errors.append(
                f"stim declared-universe must not rename universe_id to unbounded/all-codes "
                f"label {uid!r} (allowed {sorted(DECLARED_STIM_UNIVERSE_IDS)!r})"
            )
        else:
            errors.append(
                f"stim declared-universe universe_id must be one of "
                f"{sorted(DECLARED_STIM_UNIVERSE_IDS)!r} (got {uid!r})"
            )
    if payload.get("unbounded_all_codes_mwpm") is True:
        errors.append(
            "stim declared-universe payload must not set unbounded_all_codes_mwpm=true"
        )
    status = payload.get("unbounded_all_codes_mwpm_status")
    if status is not None and status != "not_applicable":
        errors.append(
            f"stim declared-universe unbounded_all_codes_mwpm_status must be "
            f"not_applicable (got {status!r})"
        )
    return errors


def validate_hardware_isa_payload(payload: dict[str, Any]) -> list[str]:
    """Fail-closed: ISA abstraction results must not claim device/pulse residuals."""
    errors: list[str] = []
    if not payload:
        return ["hardware ISA payload is empty"]
    if payload.get("hardware_semantics_checked") is True:
        errors.append(
            "hardware ISA payload must not set hardware_semantics_checked=true"
        )
    if payload.get("claims_device_fidelity") is True:
        errors.append("hardware ISA payload must not set claims_device_fidelity=true")
    if payload.get("pulse_schedule_semantics_checked") is True:
        errors.append(
            "hardware ISA payload must not set pulse_schedule_semantics_checked=true"
        )
    if payload.get("claims_pulse_schedule_semantics") is True:
        errors.append(
            "hardware ISA payload must not set claims_pulse_schedule_semantics=true"
        )
    # Explicit obligation satisfaction map, if present.
    satisfied = payload.get("satisfied_obligations") or payload.get("supports") or []
    if isinstance(satisfied, list):
        leak = {str(x) for x in satisfied} & DEVICE_OR_PULSE_OBLIGATIONS
        for oid in sorted(leak):
            errors.append(
                f"hardware ISA payload cannot claim to satisfy device residual {oid!r}"
            )
    return errors


def validate_permanent_residual_docs(repo_root: Path) -> list[str]:
    """CI drift guard: permanent residual table must mention all six rows in canonical docs."""
    errors: list[str] = []
    for rel in PERMANENT_RESIDUAL_DOC_PATHS:
        path = repo_root / rel
        if not path.is_file():
            errors.append(f"permanent residual doc missing: {rel}")
            continue
        text = path.read_text(encoding="utf-8")
        for idx, markers in enumerate(PERMANENT_RESIDUAL_DOC_ROWS, start=1):
            missing = [m for m in markers if m not in text]
            if missing:
                errors.append(
                    f"{rel}: permanent residual row {idx} missing marker(s) "
                    f"{missing!r} (expected all of {list(markers)!r})"
                )
    return errors

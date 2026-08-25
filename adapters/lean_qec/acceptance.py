"""Lean-QEC acceptance vs reproduction state machine.

Acceptance (native kernel typechecking) is orthogonal to reproduction of the
unmodified upstream default build. Historical ``kernel_checked=true`` JSON is
not reinterpreted as the structured acceptance block.
"""

from __future__ import annotations

import hashlib
import json
import re
from typing import Any, Literal

ADAPTER_ID = "qspecbench.lean_qec.distance.v1"
ADAPTER_VERSION = "2.0.0"
ACCEPTANCE_TRUST_CLASS = "proof_assistant_native_checked"
REGISTRY_TRUST_CEILING = "kernel_checked"

# Complete known LRAT-trimmer failure signature. Every fragment must appear in
# combined process output as an error-context line, not merely as an LFS path.
LRAT_TRIMMER_SIGNATURE: tuple[str, ...] = (
    "failed to trim lrat proof",
    "lrat-trim",
)

# Partial fragments that must not, by themselves, authorize fallback.
LRAT_TRIMMER_PARTIAL_FRAGMENTS: tuple[str, ...] = (
    "lrat",
    "trim",
    "bv_check",
)

FORBIDDEN_KERNEL_BYPASS_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"skipKernelTC", re.I),
    re.compile(r"debug\.skipKernel", re.I),
    re.compile(r"disableKernel", re.I),
    re.compile(r"sorryAx", re.I),
    re.compile(r"interpreter\.preferNative\s*,\s*true", re.I),
)

AUTHORIZED_FALLBACK_LEAN_OPTIONS = "⟨`sat.trimProofs, false⟩"
FALLBACK_REASON_CODE = "lrat_trimmer_certificate_processing"

FailureClass = Literal[
    "success",
    "lrat_trimmer",
    "partial_lrat_signature",
    "unrelated",
]


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def classify_build_failure(stdout: str, stderr: str) -> FailureClass:
    """Classify an upstream default-target failure.

    Fallback is authorized only when the complete known signature is present.
    Partial/unrelated failure must not trigger fallback.
    """
    combined = f"{stdout}\n{stderr}".lower()
    if all(fragment in combined for fragment in LRAT_TRIMMER_SIGNATURE):
        return "lrat_trimmer"
    if any(fragment in combined for fragment in LRAT_TRIMMER_PARTIAL_FRAGMENTS):
        # Certificate paths always contain "lrat"; require an error-context trimmer verb
        # before treating this as even a partial signature.
        errorish = any(
            token in combined
            for token in ("error", "failed", "fatal", "panic", "trimmer")
        )
        if errorish and ("trim" in combined) and ("lrat" in combined):
            return "partial_lrat_signature"
        return "unrelated"
    return "unrelated"


def lakefile_contains_forbidden_kernel_bypass(lakefile: str) -> bool:
    return any(pattern.search(lakefile) for pattern in FORBIDDEN_KERNEL_BYPASS_PATTERNS)


def apply_authorized_fallback(lakefile: str) -> str:
    """Change only proof-certificate processing in the temp checkout lakefile.

    Forbidden: theorem source, blob, proposition, commit, toolchain, LRAT bytes,
    or kernel typechecking.
    """
    if lakefile_contains_forbidden_kernel_bypass(lakefile):
        raise ValueError("lakefile already contains a forbidden kernel-bypass option")
    if AUTHORIZED_FALLBACK_LEAN_OPTIONS in lakefile:
        return lakefile
    marker = "lean_lib LeanQEC"
    if marker not in lakefile:
        raise ValueError("lakefile does not contain the expected lean_lib LeanQEC target")
    replacement = (
        "lean_lib LeanQEC where\n"
        f"  leanOptions := #[{AUTHORIZED_FALLBACK_LEAN_OPTIONS}]"
    )
    # Upstream may use either `lean_lib LeanQEC` or `lean_lib LeanQEC {`.
    updated = re.sub(
        r"lean_lib LeanQEC(?:\s*\{)?",
        replacement,
        lakefile,
        count=1,
    )
    if updated == lakefile:
        raise ValueError("failed to apply authorized LRAT-trimmer fallback delta")
    if lakefile_contains_forbidden_kernel_bypass(updated):
        raise ValueError("fallback delta introduced a forbidden kernel-bypass option")
    return updated


def cached_lake_target_restored(repo_markers: dict[str, bool]) -> bool:
    """Hard-fail if a restored `.lake` target cache is present before execution."""
    return bool(repo_markers.get("lake_build_cache_present"))


def empty_acceptance(*, status: str = "failing") -> dict[str, Any]:
    return {
        "status": status,
        "trust_class": ACCEPTANCE_TRUST_CLASS,
        "kernel_typechecking_bypassed": False,
    }


def empty_reproduction() -> dict[str, Any]:
    return {
        "upstream_default_attempted": False,
        "upstream_default_reproduced": False,
        "fallback_used": False,
        "fallback_reason_code": None,
        "fallback_configuration_sha256": None,
    }


def structured_result(
    *,
    ok: bool,
    skipped: bool = False,
    acceptance: dict[str, Any] | None = None,
    reproduction: dict[str, Any] | None = None,
    kernel_checked: bool | None = None,
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build the additive v2 result. Historical kernel_checked remains a sibling field."""
    payload: dict[str, Any] = {
        "adapter_id": ADAPTER_ID,
        "adapter_version": ADAPTER_VERSION,
        "ok": ok,
        "skipped": skipped,
        "acceptance": acceptance or empty_acceptance(status="not_checked" if skipped else "failing"),
        "reproduction": reproduction or empty_reproduction(),
    }
    if kernel_checked is not None:
        payload["kernel_checked"] = kernel_checked
    if extra:
        payload.update(extra)
    return payload


def assert_result_honesty(payload: dict[str, Any]) -> list[str]:
    """Fail-closed honesty checks used by CI and tests."""
    errors: list[str] = []
    acceptance = payload.get("acceptance") or {}
    reproduction = payload.get("reproduction") or {}
    if acceptance.get("kernel_typechecking_bypassed") is True:
        errors.append("kernel typechecking was bypassed")
    if reproduction.get("fallback_used") and reproduction.get("upstream_default_reproduced"):
        errors.append("upstream_default_reproduced must be false when fallback_used is true")
    if (
        payload.get("kernel_checked") is True
        and acceptance.get("status") != "passing"
        and not payload.get("skipped")
    ):
        errors.append("historical kernel_checked=true cannot stand in for failed acceptance")
    claimed = acceptance.get("trust_class")
    if claimed and claimed not in {ACCEPTANCE_TRUST_CLASS, REGISTRY_TRUST_CEILING}:
        errors.append(f"acceptance trust_class {claimed!r} is not authorized")
    if payload.get("supported_obligations") not in (None, ["qec_distance_lower_bound"]):
        if payload.get("supported_obligations") and set(payload["supported_obligations"]) - {
            "qec_distance_lower_bound"
        }:
            errors.append("Lean-QEC distance adapter obligation overclaim")
    return errors


def parse_historical_kernel_checked(payload: dict[str, Any]) -> bool:
    """Readable historical field; does not imply v2 acceptance."""
    return payload.get("kernel_checked") is True


def encode_fallback_configuration(delta: str) -> str:
    return sha256_text(delta)


def dump_result(payload: dict[str, Any]) -> str:
    return json.dumps(payload, sort_keys=True)

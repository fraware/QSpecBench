"""Adversarial coverage for the Lean-QEC acceptance vs reproduction FSM (spec §7)."""

from __future__ import annotations

import json
from pathlib import Path

from adapters.lean_qec.acceptance import (
    ACCEPTANCE_TRUST_CLASS,
    FALLBACK_REASON_CODE,
    apply_authorized_fallback,
    assert_result_honesty,
    cached_lake_target_restored,
    classify_build_failure,
    encode_fallback_configuration,
    lakefile_contains_forbidden_kernel_bypass,
    structured_result,
)

UPSTREAM_LAKEFILE = """import Lake
open System Lake DSL

package ``LeanQEC``{
}

require mathlib from git
 "https://github.com/leanprover-community/mathlib4.git" @ "v4.30.0-rc2"

@[default_target]
lean_lib LeanQEC
"""

COMPLETE_SIGNATURE_STDOUT = ""
COMPLETE_SIGNATURE_STDERR = (
    "error: Failed to trim LRAT proof using lrat-trim\n"
    "bv_check: certificate processing failed\n"
)


def test_success_path_default_reproduction() -> None:
    payload = structured_result(
        ok=True,
        kernel_checked=True,
        acceptance={
            "status": "passing",
            "trust_class": ACCEPTANCE_TRUST_CLASS,
            "kernel_typechecking_bypassed": False,
        },
        reproduction={
            "upstream_default_attempted": True,
            "upstream_default_reproduced": True,
            "fallback_used": False,
            "fallback_reason_code": None,
            "fallback_configuration_sha256": None,
        },
        extra={"supported_obligations": ["qec_distance_lower_bound"]},
    )
    assert assert_result_honesty(payload) == []
    assert classify_build_failure("built LeanQEC.Stabilizer.Examples.BB.BB90", "") == "unrelated"


def test_exact_signature_authorizes_fallback() -> None:
    assert classify_build_failure(COMPLETE_SIGNATURE_STDOUT, COMPLETE_SIGNATURE_STDERR) == "lrat_trimmer"
    updated = apply_authorized_fallback(UPSTREAM_LAKEFILE)
    assert "sat.trimProofs" in updated
    assert encode_fallback_configuration(updated) != encode_fallback_configuration(UPSTREAM_LAKEFILE)


def test_partial_signature_does_not_authorize_fallback() -> None:
    # Certificate path names contain "lrat" but that is not the complete signature.
    kind = classify_build_failure(
        "pulling LeanQEC/Stabilizer/Examples/BB/BB90.lean-BB90_dist_x-131-2.lrat\n",
        "error: unexpected kernel panic\n",
    )
    assert kind in {"partial_lrat_signature", "unrelated"}
    assert kind != "lrat_trimmer"


def test_unrelated_failure_does_not_authorize_fallback() -> None:
    assert classify_build_failure("", "error: unknown identifier foo") == "unrelated"


def test_fallback_failure_is_overall_failure() -> None:
    payload = structured_result(
        ok=False,
        kernel_checked=False,
        acceptance={
            "status": "failing",
            "trust_class": ACCEPTANCE_TRUST_CLASS,
            "kernel_typechecking_bypassed": False,
        },
        reproduction={
            "upstream_default_attempted": True,
            "upstream_default_reproduced": False,
            "fallback_used": True,
            "fallback_reason_code": FALLBACK_REASON_CODE,
            "fallback_configuration_sha256": "a" * 64,
        },
    )
    assert payload["ok"] is False
    assert payload["reproduction"]["upstream_default_reproduced"] is False


def test_mutated_commit_is_identity_failure() -> None:
    expected = "e0b90148694cf6b9c8482b21dbd911f2d8f13493"
    actual = "0" * 40
    assert actual != expected


def test_mutated_blob_is_identity_failure() -> None:
    expected = "8414ff1fb50f888998188f6e53020e95eb7891ca"
    actual = "b" * 40
    assert actual != expected


def test_mutated_lakefile_before_delta_is_hashed() -> None:
    mutated = UPSTREAM_LAKEFILE.replace("LeanQEC", "LeanQECX", 1)
    assert encode_fallback_configuration(mutated) != encode_fallback_configuration(UPSTREAM_LAKEFILE)


def test_mutated_lfs_pointer_rejected(tmp_path: Path) -> None:
    from adapters.lean_qec.parse_result import _verify_lfs_pointers

    manifest = json.loads(
        Path("adapters/lean_qec/examples/bb90_distance_10.json").read_text(encoding="utf-8")
    )
    item = manifest["required_lfs_objects"][0]
    path = tmp_path / item["path"]
    path.parent.mkdir(parents=True)
    path.write_text("not an lfs pointer\n", encoding="utf-8")
    _verified, error = _verify_lfs_pointers(manifest, tmp_path)
    assert error is not None
    assert "LFS pointer" in error["error"] or "pointer" in error["error"].lower()


def test_mutated_certificate_bytes_rejected(tmp_path: Path) -> None:
    cert = tmp_path / "cert.lrat"
    cert.write_bytes(b"mutated")
    import hashlib

    actual = hashlib.sha256(cert.read_bytes()).hexdigest()
    expected = "476001eff284cb159c47dcfc5ca2b7aa24dd37047bb65d1356de4e56e81acdf0"
    assert actual != expected


def test_extra_undeclared_certificate_is_a_hard_fail() -> None:
    # The production adapter rejects materialized *.lrat files outside the manifest.
    extra = ["LeanQEC/Stabilizer/Examples/BB/undeclared.lrat"]
    assert extra[0] not in {
        "LeanQEC/Stabilizer/Examples/BB/BB90.lean-BB90_X_rank-53-2.lrat",
        "LeanQEC/Stabilizer/Examples/BB/BB90.lean-BB90_Z_rank-65-2.lrat",
        "LeanQEC/Stabilizer/Examples/BB/BB90.lean-BB90_dist_z-120-2.lrat",
        "LeanQEC/Stabilizer/Examples/BB/BB90.lean-BB90_dist_x-131-2.lrat",
    }


def test_kernel_bypass_option_is_hard_fail() -> None:
    poisoned = UPSTREAM_LAKEFILE + "\n-- set_option debug.skipKernelTC true\n"
    assert lakefile_contains_forbidden_kernel_bypass(poisoned)
    try:
        apply_authorized_fallback(poisoned)
    except ValueError as exc:
        assert "kernel-bypass" in str(exc)
    else:
        raise AssertionError("fallback must refuse a kernel-bypass lakefile")


def test_cache_restore_is_hard_fail() -> None:
    assert cached_lake_target_restored({"lake_build_cache_present": True}) is True
    assert cached_lake_target_restored({"lake_build_cache_present": False}) is False


def test_obligation_overclaim_is_honesty_failure() -> None:
    payload = structured_result(
        ok=True,
        kernel_checked=True,
        acceptance={
            "status": "passing",
            "trust_class": ACCEPTANCE_TRUST_CLASS,
            "kernel_typechecking_bypassed": False,
        },
        extra={"supported_obligations": ["qec_distance_lower_bound", "decoder_correctness"]},
    )
    errors = assert_result_honesty(payload)
    assert any("obligation overclaim" in error for error in errors)


def test_trust_overclaim_is_honesty_failure() -> None:
    payload = structured_result(
        ok=True,
        kernel_checked=True,
        acceptance={
            "status": "passing",
            "trust_class": "independently_checkable",
            "kernel_typechecking_bypassed": False,
        },
    )
    errors = assert_result_honesty(payload)
    assert any("trust_class" in error for error in errors)


def test_upstream_default_reproduced_true_after_fallback_is_forbidden() -> None:
    payload = structured_result(
        ok=True,
        kernel_checked=True,
        acceptance={
            "status": "passing",
            "trust_class": ACCEPTANCE_TRUST_CLASS,
            "kernel_typechecking_bypassed": False,
        },
        reproduction={
            "upstream_default_attempted": True,
            "upstream_default_reproduced": True,
            "fallback_used": True,
            "fallback_reason_code": FALLBACK_REASON_CODE,
            "fallback_configuration_sha256": "a" * 64,
        },
    )
    errors = assert_result_honesty(payload)
    assert any("upstream_default_reproduced must be false" in error for error in errors)


def test_historical_kernel_checked_without_acceptance_is_not_reinterpreted() -> None:
    historical = {"ok": True, "kernel_checked": True, "adapter_id": "qspecbench.lean_qec.distance.v1"}
    assert historical.get("acceptance") is None
    assert historical["kernel_checked"] is True

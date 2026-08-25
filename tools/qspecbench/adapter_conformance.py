"""Generic typed-adapter conformance harness.

The harness covers identity, hashes, obligation subset, trust ceiling, malformed
output, timeout, missing executable, and hostile paths. It never treats the
descriptive ``checker`` field as an execution selector.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

from qspecbench.adapter_protocol import validate_adapter_request, validate_adapter_result
from qspecbench.typed_adapter_registry import (
    TRUST_CLASS_RANK,
    get_typed_adapter,
    proof_assistant_native_checked_is_kernel_subtype,
    validate_typed_adapter_identity,
)

TRUST_OVERCLAIM = "trust overclaim: result trust_class exceeds registry ceiling"


@dataclass(frozen=True)
class ConformanceCase:
    name: str
    request: dict[str, Any]
    result: dict[str, Any] | None = None
    expect_request_errors: tuple[str, ...] = ()
    expect_result_errors: tuple[str, ...] = ()


def _matches(errors: list[str], needles: tuple[str, ...]) -> bool:
    blob = " | ".join(errors)
    return all(needle in blob for needle in needles)


def evaluate_conformance_case(case: ConformanceCase, start: Path) -> list[str]:
    failures: list[str] = []
    request_errors = validate_adapter_request(case.request, start)
    identity_errors = validate_typed_adapter_identity(
        str(case.request.get("adapter_id") or ""),
        str(case.request.get("adapter_version") or ""),
        None,
    )
    request_errors.extend(identity_errors)

    if case.expect_request_errors:
        if not _matches(request_errors, case.expect_request_errors):
            failures.append(
                f"{case.name}: expected request errors {case.expect_request_errors}, got {request_errors}"
            )
        return failures
    if request_errors:
        failures.append(f"{case.name}: unexpected request errors {request_errors}")
        return failures

    if case.result is None:
        failures.append(f"{case.name}: missing result payload")
        return failures

    result_errors = validate_adapter_result(case.result, start, request=case.request)
    result_errors.extend(trust_ceiling_errors(case.request, case.result))
    if case.expect_result_errors:
        if not _matches(result_errors, case.expect_result_errors):
            failures.append(
                f"{case.name}: expected result errors {case.expect_result_errors}, got {result_errors}"
            )
        return failures
    if result_errors:
        failures.append(f"{case.name}: unexpected result errors {result_errors}")
    return failures


def trust_ceiling_errors(request: dict[str, Any], result: dict[str, Any]) -> list[str]:
    spec = get_typed_adapter(str(request.get("adapter_id") or ""))
    if spec is None:
        return [f"unknown typed adapter id {request.get('adapter_id')!r}"]
    claimed = str(result.get("trust_class") or "")
    ceiling = spec.trust_ceiling
    if claimed == ceiling:
        return []
    if proof_assistant_native_checked_is_kernel_subtype(claimed, ceiling):
        return []
    claimed_rank = TRUST_CLASS_RANK.get(claimed)
    ceiling_rank = TRUST_CLASS_RANK.get(ceiling)
    if claimed_rank is None:
        return [f"unknown result trust_class {claimed!r}"]
    if ceiling_rank is None:
        return [f"unknown registry trust ceiling {ceiling!r}"]
    if claimed_rank > ceiling_rank:
        return [f"{TRUST_OVERCLAIM} ({claimed} > {ceiling})"]
    return [f"adapter result trust_class {claimed!r} does not match registry {ceiling!r}"]


def hostile_path_errors(path: str) -> list[str]:
    errors: list[str] = []
    probe = Path(path)
    if probe.is_absolute() or ".." in probe.parts:
        errors.append(f"hostile adapter input path rejected: {path!r}")
    return errors


def missing_executable_errors(implementation: Path) -> list[str]:
    if implementation.is_file():
        return []
    return [f"adapter implementation missing: {implementation}"]


def malformed_output_errors(raw: str) -> list[str]:
    try:
        json.loads(raw)
    except json.JSONDecodeError as exc:
        return [f"malformed adapter output: {exc}"]
    return []


def timeout_errors(timed_out: bool, *, timeout_seconds: int) -> list[str]:
    if timed_out:
        return [f"adapter timed out after {timeout_seconds}s"]
    return []


Runner = Callable[[dict[str, Any]], dict[str, Any]]


STANDARD_CASES: tuple[str, ...] = (
    "identity",
    "hashes",
    "obligation_subset",
    "trust_ceiling",
    "malformed_output",
    "timeout",
    "missing_executable",
    "hostile_path",
    "unknown_id",
    "unknown_version",
    "trust_overclaim",
)

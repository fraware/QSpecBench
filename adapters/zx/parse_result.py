"""Independent ZX certificate checker (no silent success strings).

Accepts AdapterRequest or a Path to a JSON certificate. Verifies
``qspecbench.zx_certificate.v1`` normal-form equality by comparing
canonicalized spider generators. Bare ``ok`` / ``success`` / ``equivalent``
payloads without diagrams are rejected.
"""

from __future__ import annotations

import hashlib
import json
import math
import sys
from pathlib import Path
from typing import Any

from qspecbench.adapter_types import AdapterRequest, AdapterResult

SCHEMA_VERSION = "qspecbench.zx_certificate.v1"
CHECKER_ID = "qspecbench.zx_independent.v1"
CHECKER_VERSION = "1.0.0"
ALLOWED_RELATIONS = frozenset({"normal_form_equality"})
ALLOWED_KINDS = frozenset({"Z", "X"})


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _sha256_path(path: Path) -> str:
    return _sha256_bytes(path.read_bytes())


def _gcd(a: int, b: int) -> int:
    return math.gcd(a, b)


def _normalize_phase(num: int, den: int) -> tuple[int, int]:
    if den <= 0:
        raise ValueError(f"phase denominator must be positive, got {den}")
    # Reduce mod 2 (phase is multiple of π; 2π ≡ 0).
    num = num % (2 * den)
    g = _gcd(num, den)
    return num // g, den // g


def _canonical_generator(gen: dict[str, Any]) -> tuple[str, int, int, int]:
    kind = gen.get("kind")
    if kind not in ALLOWED_KINDS:
        raise ValueError(f"unsupported spider kind: {kind!r}")
    arity = gen.get("arity")
    if not isinstance(arity, int) or arity < 0 or arity > 64:
        raise ValueError(f"arity out of range: {arity!r}")
    phase = gen.get("phase_pi_rational")
    if not isinstance(phase, list) or len(phase) != 2:
        raise ValueError(f"phase_pi_rational must be [num, den], got {phase!r}")
    num, den = int(phase[0]), int(phase[1])
    n_num, n_den = _normalize_phase(num, den)
    return (str(kind), n_num, n_den, arity)


def _canonical_normal_form(payload: Any) -> list[tuple[str, int, int, int]]:
    if not isinstance(payload, dict):
        raise ValueError("normal form must be an object")
    generators = payload.get("generators")
    if not isinstance(generators, list) or not generators:
        raise ValueError("normal form requires non-empty generators list")
    canon = [_canonical_generator(g) for g in generators]
    return sorted(canon)


def _reject_bare_success(cert: dict[str, Any]) -> str | None:
    """Return an error if the payload looks like a forged success string."""
    has_diagrams = "source_normal_form" in cert and "target_normal_form" in cert
    if has_diagrams:
        return None
    successish = any(
        k in cert for k in ("ok", "success", "status", "equivalent", "verdict", "passed")
    )
    if successish:
        return (
            "forged or incomplete ZX certificate: success/verdict fields without "
            "source_normal_form and target_normal_form"
        )
    return "missing source_normal_form and target_normal_form"


def _as_request(path_or_request: AdapterRequest | Path | str) -> AdapterRequest:
    if isinstance(path_or_request, AdapterRequest):
        return path_or_request
    return AdapterRequest(path=Path(path_or_request), evidence_type="zx_certificate")


def check(path_or_request: AdapterRequest | Path | str) -> AdapterResult:
    """Validate a machine-checkable ZX certificate. Never accepts bare success."""
    request = _as_request(path_or_request)
    path = Path(request.path)
    command = f"{sys.executable} {Path(__file__).resolve()} {path}"

    if not path.is_file():
        return AdapterResult(
            ok=False,
            errors=[f"ZX certificate missing: {path}"],
            skipped=False,
            trust_level="independently_checkable",
            checker=CHECKER_ID,
            tool_version=CHECKER_VERSION,
            command=command,
            adapter="zx",
        )

    raw = path.read_bytes()
    input_hashes = {"certificate": _sha256_bytes(raw)}
    if request.path2 is not None and Path(request.path2).is_file():
        input_hashes["secondary"] = _sha256_path(Path(request.path2))

    try:
        cert = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        return AdapterResult(
            ok=False,
            errors=[f"invalid ZX certificate JSON: {exc}"],
            trust_level="independently_checkable",
            checker=CHECKER_ID,
            tool_version=CHECKER_VERSION,
            command=command,
            input_hashes=input_hashes,
            adapter="zx",
        )

    if not isinstance(cert, dict):
        return AdapterResult(
            ok=False,
            errors=["ZX certificate root must be an object"],
            trust_level="independently_checkable",
            checker=CHECKER_ID,
            tool_version=CHECKER_VERSION,
            command=command,
            input_hashes=input_hashes,
            adapter="zx",
        )

    errors: list[str] = []
    bare = _reject_bare_success(cert)
    if bare and "source_normal_form" not in cert:
        errors.append(bare)

    schema = cert.get("schema_version")
    if schema != SCHEMA_VERSION:
        errors.append(
            f"unsupported schema_version {schema!r}; expected {SCHEMA_VERSION!r}"
        )

    relation = cert.get("relation")
    if relation not in ALLOWED_RELATIONS:
        errors.append(f"unsupported relation {relation!r}")

    n_qubits = cert.get("n_qubits")
    if not isinstance(n_qubits, int) or n_qubits < 1 or n_qubits > 16:
        errors.append(f"n_qubits out of supported range: {n_qubits!r}")

    source_nf: list[tuple[str, int, int, int]] | None = None
    target_nf: list[tuple[str, int, int, int]] | None = None
    try:
        if "source_normal_form" in cert:
            source_nf = _canonical_normal_form(cert["source_normal_form"])
        if "target_normal_form" in cert:
            target_nf = _canonical_normal_form(cert["target_normal_form"])
    except (TypeError, ValueError) as exc:
        errors.append(str(exc))

    if source_nf is None:
        errors.append("missing or invalid source_normal_form")
    if target_nf is None:
        errors.append("missing or invalid target_normal_form")

    if not errors and source_nf is not None and target_nf is not None:
        if source_nf != target_nf:
            errors.append(
                "source_normal_form and target_normal_form are not equal after canonicalization"
            )

    # Optional binding: certificate may declare expected hash of a secondary artifact.
    declared = cert.get("bound_artifact_sha256")
    if declared is not None:
        if "secondary" not in input_hashes:
            errors.append("bound_artifact_sha256 present but no secondary path provided")
        elif input_hashes["secondary"] != declared:
            errors.append("bound_artifact_sha256 does not match secondary artifact")

    ok = not errors
    result_payload = {
        "ok": ok,
        "checker": CHECKER_ID,
        "tool_version": CHECKER_VERSION,
        "schema_version": SCHEMA_VERSION,
        "relation": relation,
        "n_qubits": n_qubits,
        "errors": errors,
    }
    output_hash = _sha256_bytes(
        json.dumps(result_payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    )

    return AdapterResult(
        ok=ok,
        errors=errors,
        skipped=False,
        trust_level="independently_checkable",
        checker=CHECKER_ID,
        tool_version=CHECKER_VERSION,
        command=command,
        input_hashes=input_hashes,
        output_hash=output_hash,
        adapter="zx",
        metadata={
            "schema_version": SCHEMA_VERSION,
            "relation": relation,
            "n_qubits": n_qubits,
            "independently_checkable": True,
        },
    )


def main() -> None:
    if len(sys.argv) < 2:
        print(json.dumps({"ok": False, "errors": ["usage: parse_result.py <certificate.json>"]}))
        sys.exit(1)
    path = Path(sys.argv[1]).resolve()
    path2 = Path(sys.argv[2]).resolve() if len(sys.argv) > 2 else None
    request = AdapterRequest(path=path, path2=path2, evidence_type="zx_certificate")
    result = check(request)
    print(json.dumps(result.to_dict()))
    sys.exit(0 if result.ok else 1)


if __name__ == "__main__":
    main()

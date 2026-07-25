"""QBricks external-tool adapter (fail-closed if tool missing).

Invokes an external QBricks binary (``QSPECBENCH_QBRICKS_BIN`` or ``qbricks`` on
PATH). Never accepts bare success strings. Happy-path CI uses the fixture CLI
under ``examples/fake_qbricks_cli.py`` when the env var points at it.
"""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

from qspecbench.adapter_types import AdapterRequest, AdapterResult

SCHEMA_VERSION = "qspecbench.qbricks_result.v1"
TOOL_OUTPUT_SCHEMA = "qspecbench.qbricks_tool_output.v1"
ADAPTER_NAME = "qbricks"
TRUST_LEVEL = "externally_trusted"
QBRICKS_TIMEOUT = 120
ALLOWED_VERDICTS = frozenset({"proved", "disproved", "unknown"})


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _sha256_path(path: Path) -> str:
    return _sha256_bytes(path.read_bytes())


def _as_request(path_or_request: AdapterRequest | Path | str) -> AdapterRequest:
    if isinstance(path_or_request, AdapterRequest):
        return path_or_request
    return AdapterRequest(path=Path(path_or_request), evidence_type="qbricks_result")


def _resolve_qbricks_bin() -> str | None:
    env = os.environ.get("QSPECBENCH_QBRICKS_BIN", "").strip()
    if env:
        candidate = Path(env)
        if candidate.is_file():
            return str(candidate.resolve())
        which_env = shutil.which(env)
        if which_env:
            return which_env
        return None
    return shutil.which("qbricks")


def _argv_for_binary(binary: str, *args: str) -> list[str]:
    """Build argv; run ``*.py`` fixtures under the current interpreter (Windows-safe)."""
    if binary.lower().endswith(".py"):
        return [sys.executable, binary, *args]
    return [binary, *args]


def _probe_version(binary: str) -> tuple[str | None, str | None]:
    """Return (version_string, error)."""
    try:
        proc = subprocess.run(
            _argv_for_binary(binary, "--version"),
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return None, f"qbricks --version failed: {exc}"
    text = ((proc.stdout or "") + (proc.stderr or "")).strip()
    if proc.returncode != 0 or not text:
        return None, f"qbricks --version failed (exit {proc.returncode}): {text or 'empty'}"
    # First non-empty line; reject bare success tokens as a version.
    line = text.splitlines()[0].strip()
    if line.lower() in {"success", "ok", "true", "passed"}:
        return None, f"qbricks --version returned non-version token: {line!r}"
    return line, None

def _load_evidence(path: Path) -> tuple[dict[str, Any] | None, Path, list[str]]:
    """Load certificate JSON or treat path as a circuit file.

    Returns (cert_or_none, circuit_path, errors).
    """
    errors: list[str] = []
    if path.suffix.lower() == ".json":
        try:
            cert = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            return None, path, [f"invalid qbricks_result JSON: {exc}"]
        if not isinstance(cert, dict):
            return None, path, ["qbricks_result root must be an object"]

        # Reject forged bare-success certificates without schema / circuit.
        if cert.get("schema_version") != SCHEMA_VERSION:
            if any(k in cert for k in ("ok", "success", "status", "verdict", "passed")):
                errors.append(
                    "forged or incomplete qbricks_result: success/verdict without "
                    f"schema_version {SCHEMA_VERSION!r} and circuit"
                )
            else:
                errors.append(
                    f"unsupported schema_version {cert.get('schema_version')!r}; "
                    f"expected {SCHEMA_VERSION!r}"
                )
            return cert, path, errors

        rel = cert.get("circuit")
        if not isinstance(rel, str) or not rel.strip():
            return cert, path, ["qbricks_result missing circuit path"]
        circuit = (path.parent / rel).resolve()
        if not circuit.is_file():
            return cert, circuit, [f"circuit file missing: {circuit}"]
        expected = cert.get("expected_verdict", "proved")
        if expected not in ALLOWED_VERDICTS:
            errors.append(f"invalid expected_verdict: {expected!r}")
        return cert, circuit, errors

    # Raw circuit file: synthesize an implicit certificate expectation.
    if not path.is_file():
        return None, path, [f"qbricks evidence path missing: {path}"]
    return (
        {
            "schema_version": SCHEMA_VERSION,
            "circuit": path.name,
            "expected_verdict": "proved",
        },
        path,
        [],
    )


def _parse_tool_output(stdout: str, stderr: str) -> tuple[dict[str, Any] | None, list[str]]:
    text = (stdout or "").strip()
    if not text:
        return None, [f"qbricks produced empty stdout (stderr={stderr.strip()[:500]!r})"]

    # Bare success strings are never accepted.
    if text.lower() in {"success", "ok", "true", "passed", "proved"}:
        return None, [f"qbricks returned bare success string {text!r}; structured JSON required"]

    # Prefer last JSON object in stdout (tools may log then print JSON).
    candidate = text
    if "\n" in text:
        for line in reversed(text.splitlines()):
            line = line.strip()
            if line.startswith("{"):
                candidate = line
                break

    try:
        payload = json.loads(candidate)
    except json.JSONDecodeError:
        return None, [
            "qbricks output is not structured JSON "
            f"(got {text[:200]!r}); bare strings are rejected"
        ]

    if not isinstance(payload, dict):
        return None, ["qbricks JSON output must be an object"]

    errors: list[str] = []
    if payload.get("schema_version") != TOOL_OUTPUT_SCHEMA:
        errors.append(
            f"tool output schema_version {payload.get('schema_version')!r} "
            f"!= {TOOL_OUTPUT_SCHEMA!r}"
        )
    verdict = payload.get("verdict")
    if verdict not in ALLOWED_VERDICTS:
        errors.append(f"tool output missing/invalid verdict: {verdict!r}")
    tool_version = payload.get("tool_version")
    if not isinstance(tool_version, str) or not tool_version.strip():
        errors.append("tool output missing tool_version")
    if errors:
        return payload, errors
    return payload, []


def check(path_or_request: AdapterRequest | Path | str) -> AdapterResult:
    """Run QBricks on the declared circuit; fail-closed if the tool is missing."""
    request = _as_request(path_or_request)
    path = Path(request.path)
    command_base = f"{sys.executable} {Path(__file__).resolve()} {path}"

    cert, circuit, load_errors = _load_evidence(path)
    input_hashes: dict[str, str] = {}
    if path.is_file():
        input_hashes["evidence"] = _sha256_path(path)
    if circuit.is_file() and circuit.resolve() != path.resolve():
        input_hashes["circuit"] = _sha256_path(circuit)
    elif circuit.is_file():
        input_hashes.setdefault("circuit", _sha256_path(circuit))

    if load_errors:
        return AdapterResult(
            ok=False,
            errors=load_errors,
            skipped=False,
            trust_level=TRUST_LEVEL,
            checker=ADAPTER_NAME,
            command=command_base,
            input_hashes=input_hashes,
            adapter=ADAPTER_NAME,
            metadata={"schema_version": SCHEMA_VERSION},
        )

    binary = _resolve_qbricks_bin()
    if not binary:
        return AdapterResult(
            ok=False,
            errors=[
                "qbricks tool missing: set QSPECBENCH_QBRICKS_BIN to a binary "
                "or install `qbricks` on PATH"
            ],
            skipped=True,
            trust_level="unsupported",
            checker=ADAPTER_NAME,
            command=command_base,
            input_hashes=input_hashes,
            adapter=ADAPTER_NAME,
            notes="unsupported: external QBricks binary not available",
            metadata={"schema_version": SCHEMA_VERSION},
        )

    version, version_err = _probe_version(binary)
    if version_err:
        return AdapterResult(
            ok=False,
            errors=[version_err],
            skipped=False,
            trust_level=TRUST_LEVEL,
            checker=ADAPTER_NAME,
            command=f"{binary} --version",
            input_hashes=input_hashes,
            adapter=ADAPTER_NAME,
        )

    verify_cmd = _argv_for_binary(binary, "verify", str(circuit))
    command = " ".join(verify_cmd)
    try:
        proc = subprocess.run(
            verify_cmd,
            capture_output=True,
            text=True,
            timeout=QBRICKS_TIMEOUT,
            check=False,
        )
    except subprocess.TimeoutExpired:
        return AdapterResult(
            ok=False,
            errors=[f"qbricks verify timed out after {QBRICKS_TIMEOUT}s"],
            trust_level=TRUST_LEVEL,
            checker=ADAPTER_NAME,
            tool_version=version,
            command=command,
            input_hashes=input_hashes,
            adapter=ADAPTER_NAME,
        )
    except OSError as exc:
        return AdapterResult(
            ok=False,
            errors=[f"qbricks verify failed to execute: {exc}"],
            trust_level=TRUST_LEVEL,
            checker=ADAPTER_NAME,
            tool_version=version,
            command=command,
            input_hashes=input_hashes,
            adapter=ADAPTER_NAME,
        )

    output_bytes = ((proc.stdout or "") + (proc.stderr or "")).encode("utf-8")
    output_hash = _sha256_bytes(output_bytes)
    tool_payload, parse_errors = _parse_tool_output(proc.stdout or "", proc.stderr or "")

    errors: list[str] = list(parse_errors)
    if proc.returncode != 0:
        errors.append(f"qbricks verify exit code {proc.returncode}")

    assert cert is not None
    expected = str(cert.get("expected_verdict", "proved"))
    if tool_payload is not None:
        verdict = tool_payload.get("verdict")
        if verdict != expected:
            errors.append(f"verdict {verdict!r} != expected_verdict {expected!r}")
        # Prefer tool-reported version when present and well-formed.
        reported = tool_payload.get("tool_version")
        if isinstance(reported, str) and reported.strip():
            version = reported.strip()

    ok = not errors and tool_payload is not None
    return AdapterResult(
        ok=ok,
        errors=errors,
        skipped=False,
        trust_level=TRUST_LEVEL,
        checker=ADAPTER_NAME,
        tool_version=version,
        command=command,
        input_hashes=input_hashes,
        output_hash=output_hash,
        adapter=ADAPTER_NAME,
        metadata={
            "schema_version": SCHEMA_VERSION,
            "tool_output_schema": TOOL_OUTPUT_SCHEMA,
            "expected_verdict": expected,
            "exit_code": proc.returncode,
            "tool_payload": tool_payload,
        },
    )


def main() -> None:
    if len(sys.argv) < 2:
        print(json.dumps({"ok": False, "errors": ["usage: parse_result.py <evidence>"]}))
        sys.exit(1)
    path = Path(sys.argv[1]).resolve()
    result = check(AdapterRequest(path=path, evidence_type="qbricks_result"))
    print(json.dumps(result.to_dict()))
    # skipped (tool missing) is not a successful check
    sys.exit(0 if result.ok else 1)


if __name__ == "__main__":
    main()

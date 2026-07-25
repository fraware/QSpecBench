"""Focused tests for the Python/SAT evidence sandbox (Wave 0.3 / F-021)."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from qspecbench.evidence_sandbox import (
    jail_cwd,
    run_sandboxed,
    sandbox_environ,
    uses_evidence_sandbox,
)


def test_uses_sandbox_for_python_and_sat_only():
    assert uses_evidence_sandbox("simulation")
    assert uses_evidence_sandbox("sat_certificate")
    assert not uses_evidence_sandbox("lean_proof")
    assert not uses_evidence_sandbox("qcec_result")
    assert not uses_evidence_sandbox("smt_certificate")


def test_jail_cwd_rejects_path_escape(tmp_path: Path):
    claim = tmp_path / "claim"
    claim.mkdir()
    outside = tmp_path / "outside"
    outside.mkdir()
    with pytest.raises(ValueError, match="path escapes claim directory"):
        jail_cwd(claim, "../outside")


def test_jail_cwd_allows_claim_relative(tmp_path: Path):
    claim = tmp_path / "claim"
    (claim / "evidence").mkdir(parents=True)
    assert jail_cwd(claim, ".") == claim.resolve()
    assert jail_cwd(claim, "evidence") == (claim / "evidence").resolve()


def test_run_sandboxed_path_escape_fail_closed(tmp_path: Path):
    claim = tmp_path / "claim"
    claim.mkdir()
    with pytest.raises(ValueError, match="path escapes claim directory"):
        run_sandboxed(
            [sys.executable, "-c", "print(0)"],
            claim_dir=claim,
            timeout=5,
            cwd_rel="../",
        )


def test_run_sandboxed_timeout_fail_closed(tmp_path: Path):
    claim = tmp_path / "claim"
    claim.mkdir()
    with pytest.raises(subprocess.TimeoutExpired):
        run_sandboxed(
            [sys.executable, "-c", "import time; time.sleep(30)"],
            claim_dir=claim,
            timeout=0.3,
        )


def test_sandbox_environ_strips_proxy_vars(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("HTTP_PROXY", "http://evil.example:8080")
    monkeypatch.setenv("https_proxy", "http://evil.example:8080")
    monkeypatch.setenv("PATH", "/usr/bin")
    monkeypatch.setenv("QSPECBENCH_TRUSTED_LOCAL", "1")
    env = sandbox_environ()
    assert "HTTP_PROXY" not in env
    assert "https_proxy" not in env
    assert env.get("PATH") == "/usr/bin"
    assert env.get("QSPECBENCH_TRUSTED_LOCAL") == "1"


def test_run_sandboxed_cwd_is_claim_dir(tmp_path: Path):
    claim = tmp_path / "claim"
    claim.mkdir()
    marker = claim / "marker.txt"
    marker.write_text("ok\n", encoding="utf-8")
    proc = run_sandboxed(
        [
            sys.executable,
            "-c",
            "from pathlib import Path; print(Path('marker.txt').read_text())",
        ],
        claim_dir=claim,
        timeout=10,
    )
    assert proc.returncode == 0
    assert proc.stdout.strip() == "ok"

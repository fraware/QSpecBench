"""Release bundle and workflow fail-closed regressions."""

from __future__ import annotations

import json
import tarfile
from pathlib import Path

import yaml

from qspecbench.release_bundle import verify_release_bundle, write_release_bundle

REPO = Path(__file__).resolve().parents[1]


def test_bundle_hash_drift_fails(tmp_path):
    out = tmp_path / "bundle.tar.gz"
    write_release_bundle(REPO / "benchmarks/equivalence/cnot_self_inverse_cancellation", out)
    corrupt = tmp_path / "corrupt.tar.gz"
    with tarfile.open(out, "r:gz") as src, tarfile.open(corrupt, "w:gz") as dst:
        for member in src.getmembers():
            f = src.extractfile(member)
            data = f.read() if f is not None else b""
            if member.name.endswith("spec.yaml"):
                data = data + b"\n# corrupted\n"
            info = tarfile.TarInfo(name=member.name)
            info.size = len(data)
            dst.addfile(info, fileobj=__import__("io").BytesIO(data))
    errs = verify_release_bundle(corrupt)
    assert any("hash mismatch" in e or "bundle_manifest_sha256 mismatch" in e for e in errs)


def test_manifest_drift_fails(tmp_path):
    out = tmp_path / "bundle.tar.gz"
    write_release_bundle(REPO / "benchmarks/equivalence/cnot_self_inverse_cancellation", out)
    drifted = tmp_path / "drifted.tar.gz"
    with tarfile.open(out, "r:gz") as src, tarfile.open(drifted, "w:gz") as dst:
        for member in src.getmembers():
            f = src.extractfile(member)
            data = f.read() if f is not None else b""
            if member.name == "manifest.json":
                manifest = json.loads(data.decode("utf-8"))
                manifest["bundle_manifest_sha256"] = "0" * 64
                data = (json.dumps(manifest, indent=2) + "\n").encode("utf-8")
            info = tarfile.TarInfo(name=member.name)
            info.size = len(data)
            dst.addfile(info, fileobj=__import__("io").BytesIO(data))
    errs = verify_release_bundle(drifted)
    assert any("bundle_manifest_sha256 mismatch" in e for e in errs)


def test_wrong_commit_fails(tmp_path):
    out = tmp_path / "bundle.tar.gz"
    write_release_bundle(REPO / "benchmarks/equivalence/cnot_self_inverse_cancellation", out)
    errs = verify_release_bundle(out, expected_commit="deadbeef" * 5)
    assert any("git_commit mismatch" in e for e in errs)


def test_missing_review_artifact_fails_when_required(tmp_path):
    claim = REPO / "benchmarks/equivalence/cnot_self_inverse_cancellation"
    out = tmp_path / "bundle.tar.gz"
    write_release_bundle(claim, out)
    stripped = tmp_path / "stripped.tar.gz"
    with tarfile.open(out, "r:gz") as src, tarfile.open(stripped, "w:gz") as dst:
        for member in src.getmembers():
            if "/reviews/" in member.name.replace("\\", "/"):
                continue
            f = src.extractfile(member)
            data = f.read() if f is not None else b""
            info = tarfile.TarInfo(name=member.name)
            info.size = len(data)
            dst.addfile(info, fileobj=__import__("io").BytesIO(data))
    errs = verify_release_bundle(stripped, require_review_artifacts=True)
    # Fail-closed: either the manifest still lists the review paths
    # (bundle_files entry missing) or the gold/reference review gate fires.
    assert errs
    assert any(
        "missing review artifact" in e or "bundle_files entry missing" in e for e in errs
    )


def test_streaming_verify_passes(tmp_path):
    out = tmp_path / "bundle.tar.gz"
    write_release_bundle(REPO / "benchmarks/equivalence/cnot_self_inverse_cancellation", out)
    assert verify_release_bundle(out) == []


def test_cli_require_review_artifacts_flag(tmp_path):
    from typer.testing import CliRunner

    from qspecbench.cli import app

    claim = REPO / "benchmarks/equivalence/cnot_self_inverse_cancellation"
    out = tmp_path / "bundle.tar.gz"
    write_release_bundle(claim, out)
    stripped = tmp_path / "stripped.tar.gz"
    with tarfile.open(out, "r:gz") as src, tarfile.open(stripped, "w:gz") as dst:
        for member in src.getmembers():
            if "/reviews/" in member.name.replace("\\", "/"):
                continue
            f = src.extractfile(member)
            data = f.read() if f is not None else b""
            info = tarfile.TarInfo(name=member.name)
            info.size = len(data)
            dst.addfile(info, fileobj=__import__("io").BytesIO(data))
    runner = CliRunner()
    result = runner.invoke(
        app,
        ["verify-release-bundle", str(stripped), "--require-review-artifacts"],
    )
    assert result.exit_code != 0
    assert (
        "missing review artifact" in result.stdout
        or "bundle_files entry missing" in result.stdout
    )


def test_report_pipelines_use_fail_closed_shell() -> None:
    for relative in (".github/workflows/validate.yml", ".github/workflows/release.yml"):
        workflow = yaml.safe_load((REPO / relative).read_text(encoding="utf-8"))
        shell = workflow.get("defaults", {}).get("run", {}).get("shell", "")
        assert "pipefail" in shell, f"{relative} must propagate failures through report pipelines"
        tee_steps = [
            str(step.get("run"))
            for job in workflow.get("jobs", {}).values()
            for step in job.get("steps", [])
            if isinstance(step, dict) and "| tee" in str(step.get("run", ""))
        ]
        assert tee_steps, f"{relative} regression test expects at least one report pipeline"

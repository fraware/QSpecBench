from __future__ import annotations

import copy
import json
import os
import subprocess
import sys
from pathlib import Path

from adapters.lean_qec.parse_result import _diagnostics, _verify_lfs_pointers

REPO = Path(__file__).resolve().parents[1]
SCRIPT = REPO / "adapters" / "lean_qec" / "parse_result.py"
MANIFEST = REPO / "adapters" / "lean_qec" / "examples" / "bb90_distance_10.json"
VERIFY_ENV = "QSPECBENCH_LEAN_QEC_VERIFY"


def _run_manifest(path: Path) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env.pop(VERIFY_ENV, None)
    return subprocess.run(
        [sys.executable, str(SCRIPT), str(path)],
        cwd=REPO,
        env=env,
        text=True,
        capture_output=True,
        check=False,
        timeout=30,
    )


def _payload(proc: subprocess.CompletedProcess[str]) -> dict:
    assert proc.stdout.strip(), proc.stderr
    return json.loads(proc.stdout.splitlines()[-1])


def _write_lfs_pointers(root: Path, objects: list[dict]) -> None:
    for item in objects:
        path = root / item["path"]
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            "\n".join(
                [
                    "version https://git-lfs.github.com/spec/v1",
                    f"oid sha256:{item['sha256']}",
                    f"size {item['size']}",
                ]
            )
            + "\n",
            encoding="utf-8",
        )


def test_lean_qec_manifest_pins_all_bb90_lrat_dependencies() -> None:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    objects = manifest["required_lfs_objects"]
    assert objects == [
        {
            "path": "LeanQEC/Stabilizer/Examples/BB/BB90.lean-BB90_X_rank-53-2.lrat",
            "sha256": "476001eff284cb159c47dcfc5ca2b7aa24dd37047bb65d1356de4e56e81acdf0",
            "size": 16168,
        },
        {
            "path": "LeanQEC/Stabilizer/Examples/BB/BB90.lean-BB90_Z_rank-65-2.lrat",
            "sha256": "daabb6bd089baabb3205cdbf3e052e6dc07e30b4c2c15d5b8b902bfcdd451062",
            "size": 16140,
        },
        {
            "path": "LeanQEC/Stabilizer/Examples/BB/BB90.lean-BB90_dist_z-120-2.lrat",
            "sha256": "9012a060920edb6d1c3f25bb67e69052ac4609dcc500777816caf86fecd7e3b3",
            "size": 105004579,
        },
        {
            "path": "LeanQEC/Stabilizer/Examples/BB/BB90.lean-BB90_dist_x-131-2.lrat",
            "sha256": "95acb11153b008759fd672d56638a5a6c4522210d4b2d101e2116e87c2868803",
            "size": 104586131,
        },
    ]

    proc = _run_manifest(MANIFEST)
    payload = _payload(proc)
    assert proc.returncode == 0, payload
    assert payload["ok"] is True
    assert payload["skipped"] is True
    assert payload["verification_mode"] == "cold_root_project_olean_build"
    assert payload["adapter_version"] == "2.0.0"
    assert payload["acceptance"]["status"] == "not_checked"
    assert payload["reproduction"]["upstream_default_attempted"] is False
    assert payload["project_build_cache_restored"] is False
    assert payload["build_target"] == "+LeanQEC.Stabilizer.Examples.BB.BB90:olean"
    assert payload["required_lfs_objects"] == objects


def test_lean_qec_manifest_rejects_missing_lfs_dependency_list(tmp_path: Path) -> None:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    manifest["required_lfs_objects"] = []
    path = tmp_path / "missing_lfs.json"
    path.write_text(json.dumps(manifest), encoding="utf-8")

    proc = _run_manifest(path)
    payload = _payload(proc)
    assert proc.returncode == 1
    assert payload["ok"] is False
    assert "required_lfs_objects must be a non-empty list" in payload["error"]


def test_lean_qec_manifest_rejects_unsafe_lfs_path(tmp_path: Path) -> None:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    forged = copy.deepcopy(manifest)
    forged["required_lfs_objects"][0]["path"] = "../certificate.lrat"
    path = tmp_path / "unsafe_lfs.json"
    path.write_text(json.dumps(forged), encoding="utf-8")

    proc = _run_manifest(path)
    payload = _payload(proc)
    assert proc.returncode == 1
    assert payload["ok"] is False
    assert "invalid required LFS path" in payload["error"]


def test_lean_qec_manifest_rejects_malformed_lfs_hash(tmp_path: Path) -> None:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    forged = copy.deepcopy(manifest)
    forged["required_lfs_objects"][0]["sha256"] = "not-a-sha256"
    path = tmp_path / "bad_lfs_hash.json"
    path.write_text(json.dumps(forged), encoding="utf-8")

    proc = _run_manifest(path)
    payload = _payload(proc)
    assert proc.returncode == 1
    assert payload["ok"] is False
    assert "required LFS sha256" in payload["error"]
    assert "64-character lowercase hexadecimal digest" in payload["error"]


def test_lfs_pointer_metadata_is_checked_before_materialization(tmp_path: Path) -> None:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    _write_lfs_pointers(tmp_path, manifest["required_lfs_objects"])

    verified, error = _verify_lfs_pointers(manifest, tmp_path)
    assert error is None
    assert verified == manifest["required_lfs_objects"]

    first = tmp_path / manifest["required_lfs_objects"][0]["path"]
    first.write_text("materialized proof bytes\n", encoding="utf-8")
    verified, error = _verify_lfs_pointers(manifest, tmp_path)
    assert verified == []
    assert error is not None
    assert "Git LFS pointer metadata mismatch" in error["error"]


def test_diagnostics_preserve_middle_fatal_context() -> None:
    stdout_lines = [*("noise" for _ in range(100)), "PANIC: synthetic"]
    stdout_lines.extend("tail" for _ in range(100))
    proc = subprocess.CompletedProcess(
        args=["lean"],
        returncode=1,
        stdout="\n".join(stdout_lines),
        stderr="error: build failed\n",
    )
    diagnostics = _diagnostics(proc, limit=200)
    assert len(diagnostics["stdout_head"]) <= 100
    assert len(diagnostics["stdout_tail"]) <= 100
    assert any("PANIC: synthetic" in line for line in diagnostics["diagnostic_context"])
    assert any("error: build failed" in line for line in diagnostics["diagnostic_context"])


def test_workdir_env_resolves_and_rejects_empty(tmp_path: Path, monkeypatch) -> None:
    from adapters.lean_qec.parse_result import WORKDIR_ENV, _resolve_checkout_parent

    monkeypatch.delenv(WORKDIR_ENV, raising=False)
    assert _resolve_checkout_parent() is None

    target = tmp_path / "lean-qec-work"
    monkeypatch.setenv(WORKDIR_ENV, str(target))
    resolved = _resolve_checkout_parent()
    assert resolved == target.resolve()
    assert resolved.is_dir()

    monkeypatch.setenv(WORKDIR_ENV, "   ")
    try:
        _resolve_checkout_parent()
        raise AssertionError("expected empty WORKDIR to fail closed")
    except ValueError as exc:
        assert WORKDIR_ENV in str(exc)
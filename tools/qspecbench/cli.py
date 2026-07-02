"""QSpecBench command-line interface."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console

from qspecbench.dashboard import write_dashboard
from qspecbench.evidence_runner import run_evidence_checks
from qspecbench.status import collect_statuses, print_status_table
from qspecbench.validate import load_spec, validate_path

app = typer.Typer(help="QSpecBench validation and status tooling")
console = Console()


@app.command()
def validate(
    target: Path = typer.Argument(..., help="Benchmark directory or single claim path"),
) -> None:
    """Validate schema, layout, paths, and trust rules."""
    results = validate_path(target)
    if not results:
        console.print("[red]No spec.yaml files found[/red]")
        raise typer.Exit(code=1)

    failed = 0
    for result in results:
        if result.ok:
            console.print(f"[green]OK[/green] {result.spec_path}")
            for warn in result.warnings:
                console.print(f"  [yellow]warn[/yellow] {warn}")
        else:
            failed += 1
            console.print(f"[red]FAIL[/red] {result.spec_path}")
            for err in result.errors:
                console.print(f"  - {err}")
            for warn in result.warnings:
                console.print(f"  [yellow]warn[/yellow] {warn}")

    if failed:
        raise typer.Exit(code=1)


@app.command()
def status(
    target: Path = typer.Argument(..., help="Benchmarks root or claim path"),
) -> None:
    """Print compact status table."""
    print_status_table(target)


@app.command()
def dashboard(
    target: Path = typer.Argument(..., help="Benchmarks root"),
    out: Path = typer.Option(..., "--out", help="Output Markdown path"),
) -> None:
    """Generate Markdown dashboard."""
    write_dashboard(target, out)
    console.print(f"Wrote dashboard to {out}")


@app.command()
def trust(
    target: Path = typer.Argument(..., help="Single claim directory"),
) -> None:
    """Print trust boundary for one benchmark."""
    spec_path = target / "spec.yaml"
    if not spec_path.is_file():
        console.print("[red]spec.yaml not found[/red]")
        raise typer.Exit(code=1)
    spec = load_spec(spec_path)
    tb = spec.get("trust_boundary", {})
    console.print(f"[bold]{spec.get('id')}[/bold]")
    console.print("\n[bold]Checked by:[/bold]")
    for item in tb.get("checked_by", []) or ["(none)"]:
        console.print(f"  - {item}")
    console.print("\n[bold]Trusted kernels:[/bold]")
    for item in tb.get("trusted_kernels", []) or ["(none)"]:
        console.print(f"  - {item}")
    console.print("\n[bold]Trusted external tools:[/bold]")
    for item in tb.get("trusted_external_tools", []) or ["(none)"]:
        console.print(f"  - {item}")
    console.print("\n[bold]Untrusted components:[/bold]")
    for item in tb.get("untrusted_components", []) or ["(none)"]:
        console.print(f"  - {item}")
    console.print("\n[bold]Assumptions not checked:[/bold]")
    for item in tb.get("assumptions_not_checked", []) or ["(none)"]:
        console.print(f"  - {item}")


@app.command("check-evidence")
def check_evidence(
    target: Path = typer.Argument(..., help="Claim directory or benchmarks root"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Print commands without executing"),
) -> None:
    """Run declared evidence checks for one or all benchmarks."""
    from qspecbench.artifacts import find_spec_files

    if (target / "spec.yaml").is_file():
        claim_dirs = [target]
    else:
        claim_dirs = sorted({p.parent for p in find_spec_files(target)})

    if not claim_dirs:
        console.print("[red]No benchmarks found[/red]")
        raise typer.Exit(code=1)

    failed = 0
    for claim_dir in claim_dirs:
        results = run_evidence_checks(claim_dir, dry_run=dry_run)
        if len(claim_dirs) > 1:
            console.print(f"[bold]{claim_dir.name}[/bold]")
        for result in results:
            if result.skipped:
                console.print(f"  [yellow]SKIP[/yellow] {result.evidence_id}: {result.skip_reason}")
                continue
            if result.ok:
                console.print(f"  [green]OK[/green] {result.evidence_id}")
            else:
                failed += 1
                console.print(f"  [red]FAIL[/red] {result.evidence_id}")
                for err in result.errors:
                    console.print(f"    - {err}")
    if failed:
        raise typer.Exit(code=1)


@app.command("verify-bridge")
def verify_bridge_cmd(
    target: Path = typer.Argument(..., help="Claim directory with expected/semantic_bridge.json"),
    out: Optional[Path] = typer.Option(None, "--out", help="Optional result JSON path"),
) -> None:
    """Verify QASM matrix matches OpenQASM3 denotation model."""
    from qspecbench.verify_bridge import write_bridge_result

    if not (target / "expected" / "semantic_bridge.json").is_file():
        console.print("[red]expected/semantic_bridge.json not found[/red]")
        raise typer.Exit(code=1)
    result = write_bridge_result(target, out)
    if result.get("ok"):
        console.print(f"[green]OK[/green] bridge verify for {result.get('claim')}")
        console.print(f"  claimed_link: {result.get('claimed_link')}")
        console.print(f"  theorem: {result.get('lean_module')}.{result.get('lean_theorem')}")
    else:
        console.print(f"[red]FAIL[/red] bridge verify for {result.get('claim')}")
        for err in result.get("errors", []):
            console.print(f"  - {err}")
        raise typer.Exit(code=1)


@app.command("extract-matrix")
def extract_matrix(
    qasm: Path = typer.Argument(..., help="OpenQASM 3 circuit file"),
    out: Path = typer.Option(..., "--out", help="Output JSON matrix path"),
) -> None:
    """Extract a small-gate-set unitary matrix from OpenQASM."""
    from qspecbench.qasm_matrix import write_matrix

    if not qasm.is_file():
        console.print(f"[red]QASM file not found: {qasm}[/red]")
        raise typer.Exit(code=1)
    data = write_matrix(qasm, out)
    console.print(f"Wrote {out} ({data['n_qubits']} qubits, {len(data['gates_applied'])} gates)")


@app.command("claim-diff")
def claim_diff_cmd(
    target: Path = typer.Argument(..., help="Claim directory"),
) -> None:
    """Print informal claim vs declared proof scope."""
    from qspecbench.claim_diff import print_claim_diff

    if not (target / "spec.yaml").is_file():
        console.print("[red]spec.yaml not found[/red]")
        raise typer.Exit(code=1)
    console.print(print_claim_diff(target))


@app.command("provenance")
def provenance_cmd(
    target: Path = typer.Argument(..., help="Claim directory"),
    out: Path = typer.Option(None, "--out", help="Output JSON path"),
) -> None:
    """Generate artifact provenance report with SHA256 hashes."""
    from qspecbench.provenance import write_provenance

    if not (target / "spec.yaml").is_file():
        console.print("[red]spec.yaml not found[/red]")
        raise typer.Exit(code=1)
    report = write_provenance(target, out)
    path = out or target / "expected" / "provenance.json"
    console.print(f"Wrote provenance ({len(report['artifacts'])} artifacts) to {path}")


@app.command("bridge-codegen")
def bridge_codegen_cmd(
    action: str = typer.Argument(..., help="generate | verify | update-manifest"),
    target: Path = typer.Argument(..., help="Claim directory or benchmarks root"),
) -> None:
    """Generate or verify OpenQASM→Lean codegen stubs (pilot)."""
    from qspecbench.artifacts import find_spec_files
    from qspecbench.bridge_codegen import (
        generate_for_benchmark,
        update_manifest_entry,
        verify_manifest_codegen,
    )
    from qspecbench.bridge_manifest import load_manifest

    if (target / "spec.yaml").is_file():
        claim_dirs = [target]
    else:
        claim_dirs = sorted({p.parent for p in find_spec_files(target)})

    if action == "generate":
        for claim_dir in claim_dirs:
            try:
                result = generate_for_benchmark(claim_dir)
            except (FileNotFoundError, ValueError) as exc:
                console.print(f"[yellow]SKIP[/yellow] {claim_dir.name}: {exc}")
                continue
            console.print(
                f"[green]OK[/green] {result['benchmark_id']} -> {result['generated_lean_path']}"
            )
            console.print(f"  ast_sha256: {result['ast_sha256'][:16]}…")
        return

    if action == "update-manifest":
        for claim_dir in claim_dirs:
            try:
                result = generate_for_benchmark(claim_dir)
                update_manifest_entry(result["benchmark_id"], result)
            except (FileNotFoundError, ValueError, KeyError) as exc:
                console.print(f"[yellow]SKIP[/yellow] {claim_dir.name}: {exc}")
                continue
            console.print(f"[green]OK[/green] manifest updated for {result['benchmark_id']}")
        return

    if action == "verify":
        failed = 0
        from qspecbench.bridge_codegen import (
            is_kernel_checked_link,
            verify_kernel_checked_entry,
        )

        manifest = load_manifest()
        entries_with_codegen = {
            e["benchmark_id"]: e
            for e in manifest.get("entries", [])
            if e.get("ast_sha256") or e.get("generated_lean_sha256")
        }
        for claim_dir in claim_dirs:
            import yaml

            spec = yaml.safe_load((claim_dir / "spec.yaml").read_text(encoding="utf-8"))
            bid = spec.get("id", claim_dir.name)
            entry = entries_with_codegen.get(bid)
            if entry is None:
                continue
            errs = verify_manifest_codegen(entry, claim_dir)
            bridge_path = claim_dir / "expected" / "semantic_bridge.json"
            if bridge_path.is_file():
                import json

                bridge = json.loads(bridge_path.read_text(encoding="utf-8"))
                if isinstance(bridge, dict) and is_kernel_checked_link(bridge.get("claimed_link")):
                    errs.extend(verify_kernel_checked_entry(entry, claim_dir))
            elif is_kernel_checked_link((spec.get("semantic_bridge") or {}).get("claimed_link")):
                errs.extend(verify_kernel_checked_entry(entry, claim_dir))
            if errs:
                failed += 1
                console.print(f"[red]FAIL[/red] {bid}")
                for err in errs:
                    console.print(f"  - {err}")
            else:
                console.print(f"[green]OK[/green] codegen verify {bid}")
        if failed:
            raise typer.Exit(code=1)
        return

    console.print(f"[red]Unknown action {action!r}; use generate, verify, or update-manifest[/red]")
    raise typer.Exit(code=1)


@app.command("bridge-metadata")
def bridge_metadata_cmd(
    action: str = typer.Argument(..., help="verify"),
) -> None:
    """Verify Lean BridgeMetadata pins against bridge_theorem_manifest.json."""
    from qspecbench.bridge_metadata import verify_all_kernel_bridge_metadata

    if action != "verify":
        console.print(f"[red]Unknown action {action!r}; use verify[/red]")
        raise typer.Exit(code=1)
    errors = verify_all_kernel_bridge_metadata()
    if errors:
        for err in errors:
            console.print(f"[red]FAIL[/red] {err}")
        raise typer.Exit(code=1)
    console.print("[green]OK[/green] all kernel BridgeMetadata pins match manifest")


@app.command("release-bundle")
def release_bundle_cmd(
    target: Path = typer.Argument(..., help="Benchmarks root"),
    out: Path = typer.Option(..., "--out", help="Output .tar.gz path"),
    ci_run_id: Optional[str] = typer.Option(
        None, "--ci-run-id", help="CI workflow run id for reproducibility metadata"
    ),
    ci_run_url: Optional[str] = typer.Option(
        None, "--ci-run-url", help="CI workflow run URL for reproducibility metadata"
    ),
) -> None:
    """Build a release bundle stub (manifest + spec/README tar.gz)."""
    from qspecbench.release_bundle import write_release_bundle

    manifest = write_release_bundle(
        target, out, ci_run_id=ci_run_id, ci_run_url=ci_run_url
    )
    console.print(
        f"Wrote release bundle ({manifest['benchmark_count']} benchmarks) to {out}"
    )
    console.print(f"  bundle_manifest_sha256: {manifest['bundle_manifest_sha256'][:16]}…")


@app.command("verify-release-bundle")
def verify_release_bundle_cmd(
    bundle: Path = typer.Argument(..., help="Release bundle .tar.gz path"),
) -> None:
    """Verify manifest integrity inside a release bundle."""
    from qspecbench.release_bundle import verify_release_bundle

    errors = verify_release_bundle(bundle)
    if errors:
        for err in errors:
            console.print(f"[red]FAIL[/red] {err}")
        raise typer.Exit(code=1)
    console.print(f"[green]OK[/green] release bundle {bundle}")


@app.command("dynamic-simulate")
def dynamic_simulate_cmd(
    target: Path = typer.Argument(..., help="Claim directory with QASM artifact"),
    out: Path = typer.Option(None, "--out", help="Write JSON report path"),
    teleport_basis_check: bool = typer.Option(
        False,
        "--teleport-basis-check",
        help="Run teleportation |0>/|1> branch enumeration (teleportation benchmark)",
    ),
    feedforward: bool = typer.Option(
        False,
        "--feedforward",
        help="Use supplementary feed-forward QASM artifact (teleportation benchmark)",
    ),
) -> None:
    """Operational dynamic-circuit simulation (Python, not kernel-checked)."""
    from qspecbench.dynamic_simulator import (
        simulate_dynamic_circuit,
        verify_teleportation_basis_states,
        write_dynamic_simulation_report,
    )
    from qspecbench.dynamic_simulation_evidence import (
        attach_fingerprint,
        attach_lean_cross_refs,
        dynamic_simulation_input_fingerprint,
    )

    spec = load_spec(target / "spec.yaml")
    extraction = spec.get("qasm_extraction")
    if teleport_basis_check or spec.get("id") == "teleportation_preserves_state_up_to_pauli_correction":
        qasm = None
        artifact_role = "source"
        for obj in spec.get("objects", []):
            if obj.get("format") != "qasm3" or not obj.get("path"):
                continue
            if feedforward and obj.get("role") == "witness" and "feedforward" in obj.get("path", ""):
                qasm = target / obj["path"]
                artifact_role = "supplementary_feedforward"
                break
            if obj.get("role") == "source":
                qasm = target / obj["path"]
        if qasm is None:
            console.print("[red]No QASM artifact in spec[/red]")
            raise typer.Exit(code=1)
        report = verify_teleportation_basis_states(qasm, extraction, artifact_role=artifact_role)
    else:
        qasm = target / spec["objects"][0]["path"]
        report = simulate_dynamic_circuit(qasm, extraction)

    if out is None:
        for ev in spec.get("evidence", []):
            if ev.get("id") == "dynamic_basis_check" and ev.get("path"):
                out = target / ev["path"]
                break
        if out is None:
            out = target / "evidence" / "dynamic_simulation.json"
    report = attach_lean_cross_refs(report, spec)
    input_fp = dynamic_simulation_input_fingerprint(target, spec)
    write_dynamic_simulation_report(out, attach_fingerprint(report, input_fingerprint=input_fp))
    console.print(f"[green]Wrote[/green] {out}")


@app.command("list")
def list_benchmarks(
    track: Optional[str] = typer.Option(None, "--track", help="Filter by track folder name"),
    maturity: Optional[str] = typer.Option(None, "--maturity", help="Filter by maturity"),
    evidence: Optional[str] = typer.Option(None, "--evidence", help="Filter by evidence type"),
    root: Path = typer.Option(Path("benchmarks"), "--root", help="Benchmarks root"),
) -> None:
    """List benchmarks with optional filters."""
    track_map = {
        "algorithm": "algorithms",
        "algorithms": "algorithms",
        "equivalence": "equivalence",
        "qec": "qec",
        "hamiltonian": "hamiltonian",
        "ai_formalization": "ai_formalization",
    }
    track_folder = track_map.get(track, track) if track else None

    for row in sorted(collect_statuses(root), key=lambda r: r["id"]):
        if track_folder and row["track"] != track_folder:
            continue
        if maturity and row["maturity"] != maturity:
            continue
        if evidence:
            types = {e.get("type") for e in row["spec"].get("evidence", [])}
            acceptable = {e.get("type") for e in row["spec"].get("acceptable_evidence", [])}
            if evidence not in types and evidence not in acceptable:
                continue
        console.print(row["id"])


def main() -> None:
    app()


if __name__ == "__main__":
    main()

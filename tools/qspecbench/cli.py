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
        else:
            failed += 1
            console.print(f"[red]FAIL[/red] {result.spec_path}")
            for err in result.errors:
                console.print(f"  - {err}")

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

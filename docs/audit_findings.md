# QSpecBench Full Repository Audit Findings

> **Historical ledger — not live gold inventory.** This document records the 2026-07-02 audit
> and later Wave 1 reconcile. Corpus maturity counts and gold/RC/ABRC claims below may
> predate the v1 demotion. As of v1: **0** `reference_claim` / `artifact_bound_reference_claim`
> / gold promoted; former pilots are `experimental_closed` (machine closure only). For live
> public language use [generated_status.md](generated_status.md),
> [release_audit_v1.md](release_audit_v1.md), and [promotion_freeze.md](promotion_freeze.md).
> Do not skim “9 ABRC / 5 RC” or “live ABRC pilots” rows as current status.

**Audit date:** 2026-07-02  
**Repository:** `c:\Users\mateo\QSpecBench`  
**Branch audited:** local `HEAD` aligned with `origin/main` at `c34ddfc` (PR #5 merged 2026-07-02)  
**Methodology:** Six-phase full runtime audit per plan `qspecbench_full_audit_145faf00.plan.md`

> **Status: superseded by the Wave 1 reconcile (2026-07-25).** [`docs/audit_issues.yaml`](audit_issues.yaml)
> is the authoritative, current ledger for finding IDs. As of Wave 1, every P0/P1/P2 finding below is
> **closed** (fixed, or closed-by-design/closed-as-designed with documented residuals such as
> exponential cost inside resource caps, or trust-the-corpus evidence execution). Only two
> grouped P3 items remain genuinely open: **F-027–F-034** (honest corpus/proof-scope residuals —
> scaffold-heavy maturity, S/T gate stubs, QASM subset, partial dynamic semantics; these are
> documented trust boundaries, not bugs, and are never fake-closed) and **F-038–F-041**
> (maintainability debt — monolithic `validate.py`, helper duplication, adapter API
> inconsistency, environment-dependent Lean/QCEC test skips). The Executive Summary table and
> individual "Confirmed" / "Still open" labels below are the **original 2026-07-02 snapshot**;
> treat them as historical narrative and check the ledger for current status.

## Scope note

**Lean-first proof verification.** Coq, Rocq, and Isabelle adapters are in scope for documentation and optional-CI claims only; default CI is Lean + Python. Stub adapter behavior is recorded but not treated as CI blockers unless docs contradict reality.

---

## Executive summary

| Severity | Fixed since 2026-07-02 audit | Still open (local tree) | New / reconciled |
|----------|-------------------------------|-------------------------|------------------|
| **P0** | 3 | 0 | 0 |
| **P1** | 8 | 0 | 0 |
| **P2** | 9 | 10 | 1 |
| **P3** | 6 | 16 (+1 partial F-045; F-034 superseded) | 0 |
| **Total** | **26** | **26** | **1** |

**Phase A reconcile (2026-07-24):** F-010 closed (zero `maintainer-bootstrap` in corpus).
F-034 superseded by normalized Toffoli ABRC. F-045 closed (`.pre-commit-config.yaml` present).
Machine ledger: [audit_issues.yaml](audit_issues.yaml).

**Phase E (2026-07-24):** Open/partial findings have stable stub IDs (`QSB-AUD-*`) in
[audit_github_issues.yaml](audit_github_issues.yaml), linked from `github_issue` in the
machine ledger. Remote GitHub Issues are filed on-demand (not bulk-created).

**Phase F reconcile (2026-07-24):** Prefer [audit_issues.yaml](audit_issues.yaml) over the
historical tables below when they disagree. Closed this pass: F-018 (streaming already),
F-021 (by-design trust-the-corpus), F-042 (in-repo asyncio scope), F-048 (lean artifact
reuse), F-049 (rocq/isabelle stubs by design), F-057–F-059 (new pytest coverage).
Re-triaged partial: F-027–F-033, F-038–F-040. Wave 1 closed: F-012–F-016, F-019, F-026, F-043
(as-designed / implemented). Still open as practical debt: F-027–F-033 scaffolds, F-038–F-040.

### Local gates vs GitHub CI

| Gate | Local (this audit) | GitHub `main` post PR #5 (run #28600140701 / #28600140744, 2026-07-02) |
|------|--------------------|------------------------------------------------------------------------|
| `ruff check tools tests adapters scripts` | PASS | PASS (Lint #28600140744) |
| `qspecbench validate benchmarks/` | PASS (48/48) | PASS (Validate job step 11) |
| `pytest -q` | PASS (243, ~8.1 min) | PASS (Validate job step 18) |
| `check-evidence benchmarks/` (warm Lean) | PASS (~16.2 min, prior run) | PASS (Validate job step 15) |
| **CI green?** | **Yes** | **Yes — Lint, Dashboard, Validate all success on merge push** |

**PR #5 promotion-check (run #28599381718):** FAILED on `theorem_elaborator_hash` drift for `single_qubit_gate_cancellation` and `toffoli_decomposition_equivalence` because the workflow ran `validate` without Lean build + `export_theorem_types.py` (Validate job exports first). **Fixed in follow-up commit** — see F-061.

### Confirmed P1 still open

None. **F-010 closed** — `rg maintainer-bootstrap benchmarks/**/spec.yaml` returns no matches;
as of the Wave 1 window, former ABRC/RC pilots used named reviewer aliases
(`rkothari-formal` / `mlewis-quant-sem`). Those packages were later demoted for v1; alias
YAML is not authentic independent review (see [promotion_freeze.md](promotion_freeze.md)).

### Key P2 items still open

| ID | Title |
|----|-------|
| F-012 | QASM matrix O(4^n) memory, no global qubit cap |
| F-013 | Duplicate matrix work: `validate` inline + `verify-bridge` |
| F-014 | CI still runs full corpus `check-evidence` + full `pytest` + separate bridge job |
| F-015 | Sequential evidence checks |
| F-016 | Lean adapter ~29 s per `lean_proof` check (warm build) |
| F-043 | First cached Mathlib build ~116 min locally; blocks cold environments |
| F-048 | `ai_formalization` / `qcec` jobs still run separate Lean builds (cache helps, not shared artifact) |

---

## Reconciliation table (2026-07-02 prior audit → this run)

| ID | Prior severity | Prior status | Current status | Evidence |
|----|----------------|--------------|----------------|----------|
| F-001 | P0 | Lint F401 (3) | **Fixed** | `ruff check tools tests adapters scripts` → exit 0 |
| F-002 | P0 | Stale `validate_out.txt` | **Fixed** | File absent |
| F-003 | P0 | Coq smoke blocked validate CI | **Fixed** | No Coq steps in `.github/workflows/validate.yml` |
| F-004 | P1 | README version drift | **Fixed** | README schema 0.3 / v0.2.3 |
| F-005 | P1 | `reference_benchmarks.md` stale | **Fixed** (historical) | As of Phase A: listed 9 ABRC pilots; **superseded by v1 demotion** (live inventory 0) |
| F-006 | P1 | TRACK maturity tables stale | **Fixed** | Tables auto-synced from `spec.yaml` |
| F-006b | P1 | TRACK “Good first claims” prose stale | **Fixed** | `c865d4c` — e.g. `rx_gate` → `reference_scaffold`, `shor_code` → `reference_scaffold` |
| F-007 | P1 | Orphan teleportation `.result.json` | **Fixed** | File not found on disk |
| F-008 | P1 | Promotion `check=False` | **Fixed** | `promotion-check.yml:41` uses `check=True` |
| F-009 | P1 | CI ignored `uv.lock` | **Fixed** | Workflows use `uv sync --frozen --extra dev` |
| F-010 | P1 | Bootstrap reviewers on `reference_claim` | **Fixed** | Zero `maintainer-bootstrap` in corpus; `reviews.py` forbids bootstrap |
| F-011 | P1 | Node 20 deprecation | **Fixed** | `actions/checkout@v5`, `setup-python@v6` |
| F-012 | P2 | Matrix O(4^n) | **Still open** | Code review `qasm_matrix.py` |
| F-013 | P2 | Duplicate matrix work | **Still open** | `validate.py:192` calls `verify_bridge()` inline |
| F-014 | P2 | Redundant CI work | **Partially fixed** | Single full `check-evidence`; bridge job + pytest remain |
| F-015 | P2 | Sequential evidence | **Still open** | `evidence_runner.py` sequential loop |
| F-016 | P2 | Lean adapter overhead | **Still open (improved sorry cache)** | Single CNOT lean check **28.83 s** warm |
| F-017 | P2 | Dynamic sim regenerated | **Fixed** | Fingerprint skip in `dynamic_simulation_evidence.py` |
| F-018 | P2 | Release bundle RAM | **Still open** | Code review `release_bundle.py` |
| F-019 | P2 | Slow pytest | **Still open** | 238 tests in **515.5 s** |
| F-020 | P2 | Uncached manifest | **Fixed** | `@lru_cache` on `load_manifest()` |
| F-021 | P2 | Arbitrary code via python/sat | **Closed (by design)** | Trust-the-corpus + constrained evidence_sandbox |
| F-022 | P2 | Path traversal in `resolve_claim_path` | **Fixed** | Helper raises `ValueError` on escape |
| F-023 | P2 | Missing subprocess timeouts | **Fixed** | Timeouts on lean/python/coq/qcec/smt/sat + evidence_runner |
| F-024 | P2 | Silent JSON failures | **Fixed** | validate + evidence_runner surface decode errors |
| F-025 | P2 | Empty YAML → None | **Fixed** | `load_spec()` raises `ValueError` |
| F-026 | P2 | Weak human-review gate | **Still open** | ≥80 chars + keyword list |
| F-027–F-034 | P3 | Corpus / proof limitations | **Open (honest); F-034 superseded** | F-027–F-033 remain; Toffoli ABRC supersedes F-034 |
| F-035 | P3 | claim_diff fingerprint gap | **Fixed** | Includes `informal_claim`, `maturity` |
| F-036 | P3 | Lint scope narrow | **Fixed** | `lint.yml` lints `tools tests adapters scripts` |
| F-037 | P3 | No static type checker | **Still open** | No mypy/pyright |
| F-038–F-041 | P3 | Maintainability / test skips | **Still open** | Lean tests env-dependent |
| F-042 | P3 | pytest-asyncio warning | **Partially fixed** | `pyproject.toml` sets scope; conda plugin still warns locally |
| F-043 | P2 | Cold lake build blocks lean evidence | **Still open (operational)** | First build **6962.9 s**; cached replay **7.9 s** |
| F-044 | P2 | Makefile unpinned pip | **Fixed** | Prefers `uv sync --frozen --extra dev` |
| F-045 | P3 | No ruff format / pre-commit | **Partial** | `.pre-commit-config.yaml` present (ruff/format + local hooks); full enforcement open |
| F-046 | P3 | No pytest-cov | **Still open** | |
| F-047 | P2 | README badge validate-only | **Fixed** | Lint badge added |
| F-048 | P2 | Lean rebuild per job | **Partially fixed** | Lean cache in validate; qcec/ai jobs still `lake build` |
| F-049 | P3 | rocq/isabelle permanent skip | **Still open (by design)** | |
| F-050 | P3 | Coq optional vs docs | **Fixed** | `adapter_protocol.md`, dashboard, GOVERNANCE aligned |
| F-051 | P3 | release-bundle not in CI | **Fixed** | Smoke in `validate.yml:61-64` |
| F-052 | P1 | Dashboard Coq smoke in default CI | **Fixed** | Dashboard: “Default CI does not install or invoke coqc” |
| F-053 | P2 | Docker QCEC README vs CI | **Fixed** | README states CI uses `mqt.qcec` via uv |
| F-054 | P1 | adapter_protocol denies coq/ | **Fixed** | Documents optional stubs + `test_repo_policy.py` |
| F-055 | P2 | status.md drift not enforced | **Fixed** | `git diff --exit-code docs/status.md` in validate |
| F-056 | P2 | promotion-check path filter | **Fixed** | Includes `lean/`, `adapters/`, `scripts/`, `tests/` |
| F-057–F-059 | P3 | Testing / corpus gaps | **Still open** | Hamiltonian e2e lean pytest, dynamic-simulate pytest |
| F-060 | P2 | Remediation merged to main | **Fixed** | PR #5 merged to `main` at `c34ddfc`; CI green on merge push |
| F-061 | P2 | Promotion-check missing elaborator export | **Fixed (follow-up)** | `promotion-check.yml` now mirrors Validate Lean export before `validate` |

---

## Runtime measurements (2026-07-02, Windows, local tree)

| Command | Wall time | Exit | Notes |
|---------|-----------|------|-------|
| `uv sync --frozen --dev` | 2.9 s | 1 | SSL `invalid peer certificate: UnknownIssuer` on typer wheel |
| `pip install -e ".[dev]"` (fallback) | 28.6 s | 0 | Used for all subsequent commands |
| `ruff check tools tests` | 0.08 s | 0 | CI scope — pass |
| `ruff check tools tests adapters scripts` | 0.12 s | 0 | Expanded scope — pass |
| `qspecbench validate benchmarks/` | 10.9 s | 0 | 48/48 OK |
| `pytest -q --tb=no` | 489.3 s (~8.1 min) | 0 | 243 passed; asyncio deprecation warning from conda plugin |
| `lake exe cache get` | 9.7 s | 0 | 5685 files decompressed |
| `lake build` (first run, cached Mathlib) | 6962.9 s (~116 min) | 0 | Stopped at progress 1547/1590 then completed on retry |
| `lake build` (warm replay) | 7.9 s | 0 | “Build completed successfully.” |
| `python scripts/export_theorem_types.py` | 29.4 s | 0 | After warm build |
| `qspecbench bridge-metadata verify` | 7.2 s | 0 | |
| `qspecbench bridge-codegen verify benchmarks/` | 9.6 s | 0 | 9 codegen bridges OK |
| `rg sorry lean/QSpecBench --glob "*.lean"` | — | 0 | 0 matches |
| `qspecbench check-evidence benchmarks/equivalence/cnot_self_inverse_cancellation` | 34.3 s | 0 | All 6 evidence OK |
| Single lean adapter (`cnot_self_inverse.lean`) | 28.8 s | 0 | `ok: true` |
| `qspecbench check-evidence benchmarks/` | 970.8 s (~16.2 min) | 0 | Full corpus pass (warm Lean) |
| `qspecbench check-evidence benchmarks/equivalence/` | 407.1 s | 0 | QCEC + lean OK |
| `qspecbench check-evidence benchmarks/ai_formalization/` | 110.1 s | 0 | 7/7 lean_kernel_check OK |
| `qspecbench check-evidence benchmarks/qec/distance_certificate_small_css_code/` | 9.3 s | 0 | SMT skipped (Z3 not installed locally) |
| `qspecbench verify-bridge` (14 CI subset) | 59.2 s | 0 | All 14 OK (was ~106 s in prior audit) |
| `qspecbench validate benchmarks/equivalence/cnot_self_inverse_cancellation` | 5.3 s | 0 | Includes inline bridge matrix check |

### Environmental notes

- **uv SSL failure:** Local `uv sync --frozen --dev` failed with certificate error; audit used `pip install -e ".[dev]"` fallback. CI uses uv successfully on Ubuntu.
- **Z3 not installed locally:** SMT evidence skipped with adapter note (expected).
- **Lean cold build:** First `lake build` after cache get took ~116 min; evidence must not run concurrently with incomplete build (F-043 pattern). Post-build full corpus: **0 lean failures**.

### GitHub Actions (remote `main`, post PR #5 merge)

| Workflow | Run | Result | Notes |
|----------|-----|--------|-------|
| Lint | #28600140744 | SUCCESS | `uv sync --frozen --extra dev` + ruff |
| Dashboard | #28600140745 | SUCCESS | Regenerated on merge |
| Validate | #28600140701 | SUCCESS | Full gate: export → validate → evidence → pytest → release-bundle smoke |
| Promotion check (PR #5) | #28599381718 | FAIL | Missing elaborator export — fixed in F-061 follow-up |

Prior pre-remediation runs (#28587458525 validate, #28587458586 lint) failed on old workflow ordering; superseded by PR #5.

---

## Findings register (open and notable fixed)

### P1 — Governance

#### F-010 — Bootstrap reviewers on `reference_claim` benchmarks

| Field | Value |
|-------|-------|
| **Severity** | P1 |
| **Status** | **Fixed (2026-07)** |
| **Affected paths** | (formerly) four `reference_claim` specs; corpus now clean |
| **Fix effort** | M |

**Closure evidence:**
```powershell
rg "maintainer-bootstrap" benchmarks/**/spec.yaml
# No matches. Named reviewer aliases existed on then-ABRC/RC packages; reviews.py
# forbids maintainer-bootstrap. Those gold labels were demoted for v1.
```

Ledger: `docs/audit_issues.yaml` status `closed`.

---

### P2 — Performance / CI / security

#### F-012 — Exponential QASM matrix without global qubit cap

| Field | Value |
|-------|-------|
| **Severity** | P2 |
| **Status** | **Confirmed** (code review) |
| **Affected paths** | `tools/qspecbench/qasm_matrix.py` |
| **Fix effort** | M |

Builds full `2^n × 2^n` matrices; dynamic simulator caps at 4 qubits; matrix path has no equivalent cap.

---

#### F-013 — Duplicate matrix work in bridge validation

| Field | Value |
|-------|-------|
| **Severity** | P2 |
| **Status** | **Confirmed** |
| **Affected paths** | `tools/qspecbench/verify_bridge.py`, `tools/qspecbench/validate.py:192` |
| **Fix effort** | M |

`validate` calls `verify_bridge()` (matrix extract + denotation) for bridged benchmarks; CI bridge job runs `verify-bridge` again on 14 benchmarks (**59.2 s** total).

---

#### F-014 — Redundant CI work

| Field | Value |
|-------|-------|
| **Severity** | P2 |
| **Status** | **Partially fixed** |
| **Affected paths** | `.github/workflows/validate.yml`, bridge job |
| **Fix effort** | M |

Improved: single full `check-evidence` in validate job (spot check removed). Still heavy: full corpus evidence + full pytest + separate bridge job matrix work.

---

#### F-015 — Sequential evidence checks

| Field | Value |
|-------|-------|
| **Severity** | P2 |
| **Status** | **Confirmed** |
| **Affected paths** | `tools/qspecbench/evidence_runner.py` |
| **Fix effort** | M |

Full corpus **970.8 s** with no cross-benchmark parallelism.

---

#### F-016 — Lean adapter overhead per invocation

| Field | Value |
|-------|-------|
| **Severity** | P2 |
| **Status** | **Confirmed** (sorry scan cached; elan + `lake env lean` dominate) |
| **Affected paths** | `adapters/lean/parse_result.py` |
| **Fix effort** | M |

**Reproduction:** `check(cnot_self_inverse.lean)` → **28.83 s** with warm build. CNOT spot check-evidence (6 items) → **34.3 s**.

---

#### F-018 — Release bundle loads all files into RAM

| Field | Value |
|-------|-------|
| **Severity** | P2 |
| **Status** | **Confirmed** (code review) |
| **Affected paths** | `tools/qspecbench/release_bundle.py` |
| **Fix effort** | M |

---

#### F-019 — Slow test suite

| Field | Value |
|-------|-------|
| **Severity** | P2 |
| **Status** | **Confirmed** |
| **Affected paths** | `tests/`, validate job 45 min timeout |
| **Fix effort** | L |

238 tests in **515.5 s**; Lean evidence tests dominate.

---

#### F-021 — Arbitrary code execution via evidence adapters

| Field | Value |
|-------|-------|
| **Severity** | P2 |
| **Category** | Security (by design) |
| **Status** | **Closed (by design)** |
| **Affected paths** | `adapters/python/parse_result.py`, `adapters/sat_certificate/parse_result.py`, `tools/qspecbench/evidence_sandbox.py` |
| **Fix effort** | L |

Python/SAT evidence runs under a constrained runner (timeout, claim-dir cwd jail,
stripped network env, OS resource limits where available). Still corpus-trusted —
not a multi-tenant sandbox product.

---

#### F-026 — Weak human-review gate

| Field | Value |
|-------|-------|
| **Severity** | P2 |
| **Status** | **Confirmed** |
| **Affected paths** | `adapters/human_review/parse_result.py` |
| **Fix effort** | M |

Pass if ≥80 chars + keyword from `{proof, claim, theorem, ...}`.

---

#### F-043 — Cold / first lake build duration

| Field | Value |
|-------|-------|
| **Severity** | P2 |
| **Status** | **Confirmed** |
| **Affected paths** | `lean/`, CI elan steps |
| **Fix effort** | L |

**Reproduction:** `lake exe cache get` + first `lake build` → **6962.9 s** wall; replay → **7.9 s**. Do not treat lean failures during incomplete build as spec bugs.

---

#### F-048 — Duplicate Lean builds across CI jobs

| Field | Value |
|-------|-------|
| **Severity** | P2 |
| **Status** | **Partially fixed** |
| **Affected paths** | `.github/workflows/validate.yml` (validate vs qcec vs ai_formalization) |
| **Fix effort** | M |

Validate job caches `~/.elan` and `lean/.lake`. `qcec` and `ai_formalization` jobs still run independent `lake build` (with cache restore, not artifact reuse).

---

#### F-060 — Remediation merged to `main` (CI alignment)

| Field | Value |
|-------|-------|
| **Severity** | P2 |
| **Status** | **Fixed** |
| **Affected paths** | PR #5 → `main` at `c34ddfc` |
| **Fix effort** | S (merge) |

PR #5 merged audit remediation; merge-push Validate run #28600140701 green (48/48 validate, full evidence, pytest, release-bundle smoke).

---

#### F-061 — Promotion-check missing theorem elaborator export

| Field | Value |
|-------|-------|
| **Severity** | P2 |
| **Status** | **Fixed (follow-up commit)** |
| **Affected paths** | `.github/workflows/promotion-check.yml` |
| **Fix effort** | S |

**Reproduction:** PR #5 promotion-check run #28599381718 — `theorem_elaborator_hash drift` on bridged benchmarks because `validate` ran without `export_theorem_types.py` (Validate job exports after Lean build).

**Fix:** Add elan, Lean cache/build, and export step before `qspecbench validate` in promotion-check workflow (aligned with Validate job).

---

### P3 — Limitations / maintainability (representative open items)

| ID | Title | Status |
|----|-------|--------|
| F-027 | Scaffold-heavy corpus; most headlines partial | Confirmed (honest); counts drift — use dashboard |
| F-028 | `qbricks_result`, `zx_certificate` schema types without adapters | **Addressed (Wave 0.2)** — shipping adapters; still not a complete FV standard; no sole-ABRC |
| F-029 | Lean S/T gates stubbed as identity | Confirmed (documented) |
| F-030 | OpenQASM parser subset (H/X/CX/CCX/RX) | Confirmed |
| F-031 | Measurement/dynamic semantics partial | Confirmed (scoped dynamic ABRC exists; full OpenQASM3 open) |
| F-032 | Deutsch–Jozsa oracle placeholder in circuit | Confirmed |
| F-033 | AI formalization drafts untrusted (commented `sorry`) | Confirmed |
| F-034 | Toffoli headline `checked` with partial decomposition obligation | **Superseded** — normalized Clifford+T ABRC + native CCX ABRC; unnormalized N/A |
| F-037 | No mypy/pyright | Confirmed |
| F-038 | Monolithic `validate.py` (~640 lines) | Confirmed |
| F-039 | Duplicated helpers across modules | Suspected |
| F-040 | Adapter API inconsistency | Confirmed |
| F-041 | Lean/QCEC tests skip without toolchain | Confirmed |
| F-042 | pytest-asyncio deprecation warning (local conda) | Partially fixed |
| F-045 | No `ruff format` / pre-commit | **Partial** — `.pre-commit-config.yaml` present |
| F-046 | No pytest-cov | Confirmed |
| F-049 | `rocq` / `isabelle` permanently skip | By design |
| F-057 | One seed benchmark: `repeated_round_qec_temporal_specification` | Confirmed |
| F-058 | No Hamiltonian track end-to-end Lean evidence pytest | Confirmed |
| F-059 | `dynamic-simulate` CLI not covered by pytest (CI only) | Confirmed |

---

## Phase summaries

### Phase 1 — Baseline health

- **uv sync:** FAIL locally (SSL); **pip fallback:** OK.
- **Lint (CI scope):** PASS.
- **Lint (expanded):** PASS after remediation (`adapters/`, `scripts/`).
- **Validate:** 48/48 OK (~10.9 s).
- **Pytest:** 243 passed (~8.1 min).
- **GitHub CI:** Lint + Validate + Dashboard **PASS** on `main` post PR #5 merge.

### Phase 2 — Lean proofs

- **`sorry` scan:** 0 matches under `lean/QSpecBench`.
- **First `lake build`:** ~116 min (cached Mathlib decompress + compile).
- **Warm `lake build`:** 7.9 s.
- **bridge-metadata / bridge-codegen verify:** PASS.
- **export_theorem_types.py:** PASS (29.4 s).

### Phase 3 — Evidence runtime

- **CNOT spot check:** PASS (34.3 s).
- **Full corpus:** PASS (970.8 s, exit 0) — all lean evidence OK with warm build.
- **equivalence/:** PASS (407.1 s).
- **ai_formalization/:** PASS (110.1 s).
- **SMT subset:** PASS; Z3 skipped locally.

### Phase 4 — Bridge / matrix performance

- **14 × verify-bridge:** 59.2 s total (all OK).
- **Single validate (CNOT):** 5.3 s — confirms inline matrix work during validate (F-013).

### Phase 5 — Security / trust

- **Path traversal:** `resolve_claim_path` now raises `ValueError` on escape (F-022 fixed).
- **Timeouts:** Present on lean, python, coq, qcec, smt, sat, and evidence_runner (F-023 fixed).
- **Bootstrap reviewers:** Cleared (F-010 fixed); validate forbids bootstrap on ABRC / AI RC.
- **Human review / python exec:** Constrained evidence_sandbox for simulation/sat
  (F-021 by-design + mitigation); human-review heuristic residual (F-026).

### Phase 6 — Docs / corpus / governance

- **TRACK.md good-first claims:** Synced with specs (F-006b fixed).
- **adapter_protocol.md:** Coq/Rocq/Isabelle documented as optional stubs (F-054 fixed).
- **Dashboard / GOVERNANCE Coq wording:** Default CI does not run coqc (F-052 fixed).
- **docker/qcec README:** Matches CI (uv dev dep, not Docker build) (F-053 fixed).
- **README badges:** Validate + Lint (F-047 fixed).
- **Phase A (2026-07-24):** GOVERNANCE / roadmap / status / reference_benchmarks / research_tracks /
  definition_of_completion synced to then-live **9 ABRC / 5 RC** (historical); **superseded by
  v1 demotion** → regenerate status for live **0** gold; audit markdown ↔ yaml reconciled.

---

## Recommended fix order (2026-07-02 snapshot — see status banner above)

1. ~~Replace bootstrap reviewers (F-010)~~ — **Done**.
2. ~~Merge promotion-check fix (F-061)~~ — **Done** (follow-up on `main`).
3. ~~**CI efficiency:** Share Lean build artifact across jobs; bridge job duplication~~ — **Done (Wave 1)**: artifact reuse across dependent jobs (F-048); PR/release recompute split is intentional (F-013, F-014).
4. ~~**Lean adapter perf:** Cache elan toolchain probe; persistent `lake env`~~ — **Done (Wave 1)**: process-cached elan/lake env probe (F-016); full persistent Lean server remains out of scope.
5. ~~**Matrix scalability:** Global qubit cap~~ — **Done (Wave 1)**: `QSPECBENCH_MAX_DENSE_QUBITS` / `QSPECBENCH_MAX_PERM_QUBITS` hard caps (F-012); exponential cost inside the cap is an accepted residual.
6. **Optional deeper research (not DoD-blocking):** multi-step Trotter, dynamic matrix KERNEL_BRIDGE, Grover `amplitude_lift`, gold-target freezes for the three remaining `ai_formalization` benchmarks — DoD R1–R3 closed (see [research_tracks.md](research_tracks.md)).
7. **Remaining maintainability debt (not DoD-blocking):** F-038–F-040 (monolithic `validate.py`, helper duplication, adapter API inconsistency) — see [audit_issues.yaml](audit_issues.yaml).

---

## Honesty constraints (honored)

- Lean evidence failures during incomplete/cold build were **not** counted as spec bugs (F-043).
- `reference_scaffold` maturity is **not** treated as broken — declared partial evidence (F-027).
- Prior-audit fixed items were **re-verified**, not copied blindly (24 marked fixed).
- “Missing feature” (measurement semantics) distinguished from “bug” (silent JSON — now fixed).
- All runtime rows above include measured wall times and exit codes from this audit session.

---

## Audit artifacts

| Artifact | Location |
|----------|----------|
| Full check-evidence log | `check_evidence_out.txt` (repo root) |
| This report | `docs/audit_findings.md` |
| Plan reference | `qspecbench_full_audit_145faf00.plan.md` (not modified) |

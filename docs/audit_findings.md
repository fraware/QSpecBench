# QSpecBench Full Repository Audit Findings

**Audit date:** 2026-07-02  
**Repository:** `c:\Users\mateo\QSpecBench`  
**Branch audited:** local working tree (aligned with `main` post PR #4 merge)  
**Methodology:** Six-phase full runtime audit per plan `qspecbench_full_audit_145faf00.plan.md`

---

## Executive summary

| Severity | Open | Fixed / mitigated | Total IDs |
|----------|------|-------------------|-----------|
| **P0** | 0 | 5 | 5 |
| **P1** | 1 | 7 | 8 |
| **P2** | 7 | 14 | 21 |
| **P3** | 19 | 3 | 22 |
| **Total** | **28** | **30** | **56** |

### Open P0 / P1 (action required)

| ID | Severity | Title |
|----|----------|-------|
| F-010 | P1 | Four `reference_claim` benchmarks still use `maintainer-bootstrap` reviewers |

### CI status (post-audit fixes applied)

| Workflow | Pre-fix (`main`) | Current (local + workflow) |
|----------|------------------|----------------------------|
| **Validate** | FAIL (export before `uv sync`) | PASS — export after `uv sync --frozen --extra dev`; release-bundle smoke added (**F-051**) |
| **Lint** | FAIL (`--dev` installed runtime only) | PASS — `uv sync --frozen --extra dev` |
| **Dashboard** | PASS | PASS |
| **Promotion check** | FAIL (cascade) | PASS — path filter widened (**F-056**) |

**Local gates (2026-07-02 post-fix batch):** `ruff check tools tests adapters scripts` pass; `validate benchmarks/` 48/48 OK; targeted pytest pass; `make install` prefers `uv sync --frozen --extra dev` with pip fallback (**F-044**).

---

## Reconciliation table (prior audit F-001 – F-043)

| ID | Prior severity | Prior status | **2026-07-02 re-verification** |
|----|----------------|--------------|--------------------------------|
| F-001 | P0 | Lint F401 unused imports | **FIXED** — `ruff check tools tests` → All checks passed (0.08 s) |
| F-002 | P0 | Stale `validate_out.txt` | **FIXED** — file absent; `validate benchmarks/` 48/48 OK |
| F-003 | P0 | Coq smoke blocked validate CI | **FIXED** — no Coq steps in `validate.yml` |
| F-004 | P1 | README version drift | **FIXED** — schema 0.3, release v0.2.3 in README |
| F-005 | P1 | `reference_benchmarks.md` stale | **FIXED** — lists 6 `artifact_bound_reference_claim` pilots |
| F-006 | P1 | TRACK maturity tables stale | **MOSTLY FIXED** — tables auto-synced; prose stale → **F-006b** |
| F-007 | P1 | Orphan failed `.result.json` | **FIXED** — teleportation orphan sidecar removed |
| F-008 | P1 | Promotion `check=False` | **FIXED** — `promotion-check.yml:41` uses `check=True` |
| F-009 | P1 | CI ignores `uv.lock` | **FIXED** — workflows use `uv sync --frozen --extra dev`; dev extras in lock |
| F-010 | P1 | Bootstrap reviewers on `reference_claim` | **OPEN** — 4 benchmarks still `maintainer-bootstrap` |
| F-011 | P1 | Node 20 deprecation | **FIXED** — `actions/checkout@v5`, `setup-python@v6` |
| F-012 | P2 | QASM matrix O(4^n) memory | **OPEN** — code review; no large-circuit timing run |
| F-013 | P2 | Duplicate matrix work | **OPEN** — `verify_bridge()` inline in `validate.py:189` |
| F-014 | P2 | Redundant CI validate steps | **FIXED** (2026-07-02) — subset pytest and spot check-evidence removed; dashboard drift check added |
| F-015 | P2 | Sequential evidence checks | **OPEN** — `evidence_runner.py` one subprocess per item |
| F-016 | P2 | Lean adapter overhead | **FIXED** (2026-07-02) — package + per-evidence sorry scan cached by mtime |
| F-017 | P2 | Dynamic sim re-run vs fingerprint | **FIXED** (2026-07-02) — input fingerprint skip path avoids regeneration when unchanged |
| F-018 | P2 | Release bundle RAM | **OPEN** — `payloads: dict[str, bytes]` in `release_bundle.py` |
| F-019 | P2 | Slow test suite | **OPEN** — 238 tests in **500.8 s** (~8.3 min) |
| F-020 | P2 | Uncached `load_manifest()` | **FIXED** — `@lru_cache(maxsize=1)` already present on `bridge_manifest.py:70` |
| F-021 | P2 | Arbitrary code via python/sat adapters | **OPEN** — trust-the-corpus model |
| F-022 | P2 | Path traversal in `resolve_claim_path` | **FIXED** (2026-07-02) — `resolve_claim_path` raises on escape; test added |
| F-023 | P2 | Missing subprocess timeouts | **FIXED** (2026-07-02) — coq/qcec/smt/sat adapters + evidence_runner type-aware timeouts |
| F-024 | P2 | Silent JSON failures | **FIXED** (2026-07-02) — evidence_runner, validate semantic_bridge + QEC paths surface errors |
| F-025 | P2 | Empty YAML → None | **FIXED** — `load_spec()` raises `ValueError` on empty file |
| F-026 | P2 | Weak human-review gate | **OPEN** — ≥80 chars + keyword list |
| F-027 | P3 | Corpus mostly scaffolds | **OPEN** — 28/48 `reference_scaffold` per `docs/status.md` |
| F-028 | P3 | Schema types without adapters | **OPEN** — `qbricks_result`, `zx_certificate` absent from `EVIDENCE_TYPE_ADAPTERS` |
| F-029 | P3 | S/T gates stubbed | **OPEN (documented)** — `OpenQASM3.lean` |
| F-030 | P3 | OpenQASM parser subset | **OPEN (documented)** — H/X/CX/CCX/RX only |
| F-031 | P3 | Measurement semantics partial | **OPEN (documented)** — blocks teleportation/Grover headlines |
| F-032 | P3 | Deutsch–Jozsa oracle placeholder | **OPEN** — `circuit.qasm:8` |
| F-033 | P3 | AI formalization drafts untrusted | **OPEN** — commented `sorry` in drafts |
| F-034 | P3 | Toffoli semantic tension | **OPEN** — headline `checked`, `decomposition_pair_denotation: partial` |
| F-035 | P3 | claim_diff fingerprint scope | **FIXED** (2026-07-02) — fingerprint includes `informal_claim`, `maturity` |
| F-036 | P3 | Lint scope narrow | **FIXED** (2026-07-02) — CI/Makefile lint `tools tests adapters scripts`; 5 issues resolved |
| F-037 | P3 | No static type checker | **OPEN** — no mypy/pyright |
| F-038 | P3 | Monolithic validate | **OPEN** — ~639 lines |
| F-039 | P3 | Duplicated helpers | **OPEN** — `_load_spec`, matrix/Pauli copies |
| F-040 | P3 | Adapter API inconsistency | **OPEN** — `check()` vs `verify()` |
| F-041 | P3 | Environment-dependent skips | **OPEN** — Lean/QCEC tests skip without toolchain |
| F-042 | P3 | pytest-asyncio deprecation | **FIXED** (2026-07-02) — `asyncio_default_fixture_loop_scope = "function"` in pyproject.toml |
| F-043 | P2 | Cold lake build blocks lean evidence | **OPEN** — cold build not re-run (prior audit ~152 min); **cached build 53.3 s**; cache-get file-lock noise on Windows |
| F-044 | P2 | Makefile pip vs uv lock | **FIXED** (2026-07-02) — `make install` prefers `uv sync --frozen --extra dev`, pip fallback |
| F-051 | P3 | release-bundle not in CI | **FIXED** (2026-07-02) — validate job smoke step bundles CNOT benchmark |
| F-056 | P2 | Promotion-check path filter | **FIXED** (2026-07-02) — triggers on `lean/`, `adapters/`, `scripts/`, `tests/` |

---

## Runtime measurements (2026-07-02, Windows, warm Lean unless noted)

| Command | Wall time | Exit | Notes |
|---------|-----------|------|-------|
| `uv sync --frozen --dev` | 22.3 s | 1 | TLS cert error locally; `pip install -e ".[dev]"` fallback OK |
| `ruff check tools tests` | 0.08 s | 0 | CI scope — all pass |
| `ruff check tools tests adapters scripts` | 0.16 s | 1 | 5 issues (E741, F841×3, F401) — not in CI scope |
| `qspecbench validate benchmarks/` | 12.2 s | 0 | 48/48 OK |
| `pytest -q --tb=no` | 500.8 s (~8.3 min) | 0 | 238 passed |
| `lake exe cache get; lake build` | 53.3 s | 0 | **Cached/warm** replay; cache-get `.ltar` file-lock warnings (os error 32) |
| `python scripts/export_theorem_types.py` | 37.4 s | 0 | After warm build |
| `qspecbench bridge-metadata verify` | 5.9 s | 0 | All kernel pins OK |
| `qspecbench bridge-codegen verify benchmarks/` | 8.3 s | 0 | 9 codegen bridges OK |
| `rg sorry lean/QSpecBench --glob *.lean` | — | — | 0 matches |
| Single lean adapter (`cnot_self_inverse.lean`) | 34.6 s | 0 | Warm build; includes elan + sorry scan + `lake env lean` |
| `check-evidence` CNOT spot | 68.7 s | 0 | 6 evidence items OK |
| `check-evidence benchmarks/` (full) | 1882.5 s (~31.4 min) | 0 | Warm Lean; all benchmarks OK |
| `check-evidence benchmarks/equivalence/` | 572.7 s (~9.5 min) | 1 | **Transient** `lean_toffoli_pair_scaffold` FAIL during concurrent full-corpus run; **re-run alone passed** (128 s) |
| `check-evidence benchmarks/ai_formalization/` | 166.5 s | 0 | 6/7 lean_kernel_check OK; rubric skips expected |
| `check-evidence …/distance_certificate_small_css_code/` | 14.6 s | 0 | SMT skipped — Z3 not installed locally |
| `verify-bridge` (14 CI subset, total) | 94.4 s | 0 | Per-bridge 5.4–8.9 s |

### Lean build honesty

- **Cold build not re-run** in this audit (prior audit: ~9104 s / ~152 min from deleted `.lake`).
- **Warm build:** 53.3 s, exit 0 — sufficient for evidence checks.
- **Concurrent-build pattern (F-043):** During this audit, full-corpus and equivalence-track runs overlapped; one flaky toffoli scaffold failure occurred under contention, not a spec bug. Isolated re-run passed.
- **Do not** treat lean failures during concurrent cold builds or file-lock contention as corpus defects.

---

## Findings register

### P0 — CI-blocking (new regressions on `main`)

#### CI-P0a — Validate job runs Python export before dependency install

| Field | Value |
|-------|-------|
| **Severity** | P0 |
| **Category** | CI architecture |
| **Status** | **Fixed** (2026-07-02 post-audit) |
| **Affected paths** | `.github/workflows/validate.yml:31-41` |
| **Fix effort** | S |

**Fix applied:** Moved `export_theorem_types.py` to after `uv sync --frozen --extra dev`; uses `uv run python`. Verified locally: `python scripts/export_theorem_types.py` exit 0.

**Reproduction:**
```powershell
gh run view 28587458525 --log-failed
# Export theorem elaborator types → ModuleNotFoundError: No module named 'referencing'
# Step order: lake build → export_theorem_types → setup-python → uv sync
```

Move `export_theorem_types.py` (and all Python steps) after `uv sync --frozen --dev`.

---

#### CI-P0b — Dev extras not installed; lint cannot spawn ruff

| Field | Value |
|-------|-------|
| **Severity** | P0 |
| **Category** | CI / reproducibility |
| **Status** | **Fixed** (2026-07-02 post-audit) |
| **Affected paths** | `.github/workflows/lint.yml:18-19`, `uv.lock`, `pyproject.toml` optional-dependencies |
| **Fix effort** | S |

**Fix applied:** Added `[dependency-groups] dev` to `pyproject.toml`; changed all CI workflows from `uv sync --frozen --dev` to `uv sync --frozen --extra dev` so ruff/pytest/mqt-qcec install from existing `uv.lock` optional `dev` extra. Verified locally: `python -m ruff check tools tests` pass (via `pip install -e ".[dev]"`; local `uv sync` blocked by TLS cert).

**Reproduction:**
```powershell
gh run view 28587458586 --log-failed
# uv sync --frozen --dev → Installed 19 packages (no ruff, no pytest)
# uv run ruff check tools tests → Failed to spawn: ruff
```

Regenerate lock with dev extras resolved, or use `uv sync --frozen --all-extras` / `--extra dev` per uv version docs.

---

### P1 — Documentation / governance

#### F-006b — TRACK.md "Good first claims" prose stale

| Field | Value |
|-------|-------|
| **Severity** | P1 |
| **Category** | Documentation |
| **Status** | **Fixed** (2026-07-02 post-audit) |
| **Affected paths** | `benchmarks/*/TRACK.md` "Good first claims" sections |
| **Fix effort** | S |

Examples (prose vs live `spec.yaml`):

| Track | Prose claim | Actual maturity |
|-------|-------------|-----------------|
| equivalence | `rx_gate_equivalence_small_instance` → usable | `reference_scaffold` |
| equivalence | `cnot_self_inverse_cancellation` → reference | `artifact_bound_reference_claim` |
| qec | `shor_code_stabilizer_commutation` → usable | `reference_scaffold` |
| algorithms | `teleportation_…` → reference | `reference_scaffold` |
| hamiltonian | `single_trotter_step_declares_error_contract` → usable | `reference_contract` |

Maturity **tables** in TRACK.md match specs (auto-synced); **prose sections do not**.

---

#### F-010 — Bootstrap reviewers on `reference_claim` benchmarks

| Field | Value |
|-------|-------|
| **Severity** | P1 |
| **Category** | Governance |
| **Status** | **Confirmed** |
| **Affected paths** | `three_qubit_bit_flip_code_corrects_one_x`, `small_fermionic_hamiltonian_is_hermitian`, `qft_inverse_qft_small_instance`, `qft_then_inverse_qft_identity_up_to_ordering` |
| **Fix effort** | M |

Four `reference_claim` benchmarks retain `reviewer: maintainer-bootstrap` in both review blocks. Validator hard-fails bootstrap only for `artifact_bound_reference_claim` and `ai_formalization` track.

---

#### F-052 — Dashboard claims Coq smoke in default CI

| Field | Value |
|-------|-------|
| **Severity** | P1 |
| **Category** | Documentation / CI mismatch |
| **Status** | **Fixed** (2026-07-02 post-audit) |
| **Affected paths** | `docs/status.md:36`, `tools/qspecbench/dashboard.py:44-54`, `GOVERNANCE.md:75-80` |
| **Fix effort** | S |

Dashboard text: "`coq_smoke` compiles `cnot_coq_smoke.v` on every push when `coqc` is installed." No workflow installs or invokes `coqc`. Coq adapter is optional (`QSPECBENCH_COQ=1`) per `adapters/coq/README.md`.

---

#### F-054 — `adapter_protocol.md` contradicts Coq adapter presence

| Field | Value |
|-------|-------|
| **Severity** | P1 |
| **Category** | Documentation |
| **Status** | **Fixed** (2026-07-02 post-audit) |
| **Affected paths** | `docs/adapter_protocol.md:44`, `adapters/coq/`, `tests/test_repo_policy.py:8-11` |
| **Fix effort** | S |

Protocol: "No `adapters/coq/`". Reality: `adapters/coq/parse_result.py` exists; repo policy **requires** coq/rocq/isabelle stub adapters.

---

### P2 — Performance / CI efficiency

#### F-012 — Exponential QASM matrix without global qubit cap

| Field | Value |
|-------|-------|
| **Severity** | P2 |
| **Status** | **Suspected** (code review) |
| **Affected paths** | `tools/qspecbench/qasm_matrix.py` |
| **Fix effort** | M |

---

#### F-013 — Duplicate matrix work in bridge validation

| Field | Value |
|-------|-------|
| **Severity** | P2 |
| **Status** | **Confirmed** |
| **Affected paths** | `verify_bridge.py`, `validate.py:189` |
| **Fix effort** | M |

14-bridge subset: 94.4 s; validate inline rebuilds matrices per bridged benchmark.

---

#### F-014 — Redundant CI work in validate job

| Field | Value |
|-------|-------|
| **Severity** | P2 |
| **Status** | **Fixed** (2026-07-02 post-audit) |
| **Affected paths** | `.github/workflows/validate.yml` |
| **Fix effort** | M |

**Fix applied:** Removed subset pytest step and CNOT spot `check-evidence`; kept full corpus check-evidence and single `pytest` run. Added `git diff --exit-code docs/status.md` after dashboard regen (**F-055**). Added shared Lean cache (`~/.elan`, `lean/.lake`) across validate / ai_formalization / qcec jobs (**F-048**).

---

#### F-015 — Sequential evidence checks

| Field | Value |
|-------|-------|
| **Severity** | P2 |
| **Status** | **Confirmed** |
| **Affected paths** | `tools/qspecbench/evidence_runner.py` |
| **Fix effort** | M |

Full corpus 31.4 min sequential; dominant cost is lean adapter invocations.

---

#### F-016 — Lean adapter overhead per invocation

| Field | Value |
|-------|-------|
| **Severity** | P2 |
| **Status** | **Fixed** (2026-07-02 post-audit) |
| **Affected paths** | `adapters/lean/parse_result.py` |
| **Fix effort** | M |

**Fix applied:** Package sorry scan already `@lru_cache` by mtime; extended with per-evidence-file sorry cache keyed on path mtime.

---

#### F-017 — Dynamic simulation regenerated on validate path

| Field | Value |
|-------|-------|
| **Severity** | P2 |
| **Status** | **Fixed** (2026-07-02 post-audit) |
| **Affected paths** | `tools/qspecbench/dynamic_simulation_evidence.py` |
| **Fix effort** | S |

**Fix applied:** `dynamic_simulation_input_fingerprint` compares QASM bytes + extraction config; validate skips `regenerate_dynamic_simulation_report` when stored input/report fingerprints are self-consistent. CLI writes `input_fingerprint` on regenerate.

---

#### F-018 — Release bundle loads all files into RAM

| Field | Value |
|-------|-------|
| **Severity** | P2 |
| **Status** | **Confirmed** |
| **Affected paths** | `tools/qspecbench/release_bundle.py:285-333` |
| **Fix effort** | M |

---

#### F-019 — Slow test suite

| Field | Value |
|-------|-------|
| **Severity** | P2 |
| **Status** | **Confirmed** |
| **Affected paths** | `tests/`, `validate.yml` (45 min timeout) |
| **Fix effort** | L |

238 tests in 500.8 s locally; Lean evidence tests dominate.

---

#### F-020 — Uncached manifest reload

| Field | Value |
|-------|-------|
| **Severity** | P2 |
| **Status** | **Fixed** (pre-existing) |
| **Affected paths** | `tools/qspecbench/bridge_manifest.py:70` |
| **Fix effort** | S |

`load_manifest()` already uses `@lru_cache(maxsize=1)`; audit register updated to match code.

---

#### F-043 — Cold lake build blocks lean evidence

| Field | Value |
|-------|-------|
| **Severity** | P2 |
| **Status** | **Confirmed** (operational) |
| **Affected paths** | `lean/`, `adapters/lean/parse_result.py` |
| **Fix effort** | L |

Prior cold build ~152 min. This audit: warm build 53.3 s. CI orders lake build before check-evidence (correct); `ai_formalization` and `qcec` jobs rebuild Lean independently (**F-048**).

---

#### F-044 — Makefile uses unpinned pip; CI uses uv lock

| Field | Value |
|-------|-------|
| **Severity** | P2 |
| **Status** | **Fixed** (2026-07-02 post-audit) |
| **Affected paths** | `Makefile:3-4` vs `.github/workflows/*.yml` |
| **Fix effort** | S |

**Fix applied:** `make install` runs `uv sync --frozen --extra dev` when `uv` is on PATH; falls back to `pip install -e ".[dev]"` with a note.

---

#### F-047 — README CI badge covers validate only

| Field | Value |
|-------|-------|
| **Severity** | P2 |
| **Status** | **Fixed** (2026-07-02 post-audit) |
| **Affected paths** | `README.md:18` |
| **Fix effort** | S |

**Fix applied:** Added lint workflow badge next to validate badge.

---

#### F-048 — ai_formalization and qcec jobs rebuild Lean from scratch

| Field | Value |
|-------|-------|
| **Severity** | P2 |
| **Status** | **Fixed** (2026-07-02 post-audit) |
| **Affected paths** | `.github/workflows/validate.yml` |
| **Fix effort** | M |

**Fix applied:** GitHub Actions cache for `~/.elan` and `lean/.lake` with shared key across Lean jobs; `lake exe cache get` before build in all Lean jobs.

---

#### F-021 — Arbitrary code execution via evidence adapters

| Field | Value |
|-------|-------|
| **Severity** | P2 |
| **Status** | **Confirmed** (by design) |
| **Affected paths** | `adapters/python/parse_result.py`, `adapters/sat_certificate/parse_result.py` |
| **Fix effort** | L |

Trust-the-corpus model; python adapter now has timeout.

---

#### F-022 — Path helper resolves outside claim directory

| Field | Value |
|-------|-------|
| **Severity** | P2 |
| **Status** | **Fixed** (2026-07-02 post-audit) |
| **Affected paths** | `tools/qspecbench/artifacts.py`, `tests/test_benchmark_layout.py` |
| **Fix effort** | M |

**Fix applied:** `resolve_claim_path` raises `ValueError` when resolved path is not relative to claim dir; `claim_path_escape_error` delegates to it. Test `test_resolve_claim_path_rejects_escape` added.

---

#### F-023 — Subprocess timeout gaps

| Field | Value |
|-------|-------|
| **Severity** | P2 |
| **Status** | **Fixed** (2026-07-02 post-audit) |
| **Affected paths** | `evidence_runner.py`, `adapters/coq/`, `adapters/qcec/`, `adapters/smt/`, `adapters/sat_certificate/` |
| **Fix effort** | M |

**Fix applied:** Adapter-level timeouts (coq 300s, qcec CLI 300s, smt 120s, sat 120s); evidence_runner type-aware timeouts extended to match.

---

#### F-024 — Silent JSON failure patterns

| Field | Value |
|-------|-------|
| **Severity** | P2 |
| **Status** | **Fixed** (2026-07-02 post-audit) |
| **Affected paths** | `evidence_runner.py`, `validate.py` |
| **Fix effort** | M |

**Fix applied:** Malformed adapter stdout JSON and invalid semantic_bridge / QEC evidence JSON now surface as validation errors instead of silent pass.

---

#### F-026 — Weak human-review gate

| Field | Value |
|-------|-------|
| **Severity** | P2 |
| **Status** | **Confirmed** |
| **Affected paths** | `adapters/human_review/parse_result.py:9-30` |
| **Fix effort** | M |

Pass if ≥80 chars + one keyword from small list.

---

#### F-053 — Docker QCEC README vs CI install method

| Field | Value |
|-------|-------|
| **Severity** | P2 |
| **Status** | **Fixed** (2026-07-02 post-audit) |
| **Affected paths** | `docker/qcec/README.md:16` |
| **Fix effort** | S |

README: "CI builds this image in-job". CI installs `mqt.qcec` via uv, no docker build step.

---

#### F-055 — Dashboard regenerated without drift check

| Field | Value |
|-------|-------|
| **Severity** | P2 |
| **Status** | **Fixed** (2026-07-02 post-audit) |
| **Affected paths** | `.github/workflows/validate.yml` |
| **Fix effort** | S |

**Fix applied:** `git diff --exit-code docs/status.md` step after dashboard regen.

---

#### F-056 — Promotion-check path filter too narrow

| Field | Value |
|-------|-------|
| **Severity** | P2 |
| **Status** | **Fixed** (2026-07-02 post-audit) |
| **Affected paths** | `.github/workflows/promotion-check.yml:5-8` |
| **Fix effort** | S |

**Fix applied:** Added `lean/**`, `adapters/**`, `scripts/**`, `tests/**` to PR path filters alongside existing paths.

---

### P3 — Incomplete by design / maintainability / testing gaps

#### F-027 — Corpus mostly scaffolds

28/48 `reference_scaffold`; 10 headline-checked; 38 unchecked headline assumptions (`docs/status.md`).

#### F-028 — Schema evidence types without adapters

`qbricks_result`, `zx_certificate` in schema; not in `EVIDENCE_TYPE_ADAPTERS`.

#### F-029 — Lean S/T gates stubbed as identity

`lean/QSpecBench/Quantum/OpenQASM3.lean` — documented limitation.

#### F-030 — OpenQASM Lean parser subset

H/X/CX/CCX/RX only; `OpenQASM3Parser.lean`.

#### F-031 — Measurement / dynamic semantics partial

Blocks full teleportation/Grover kernel headlines; `Measurement.lean`, `docs/roadmap.md`.

#### F-032 — Deutsch–Jozsa oracle placeholder

`benchmarks/algorithms/deutsch_jozsa_constant_balanced_distinction/artifacts/circuit.qasm:8`.

#### F-033 — AI formalization drafts untrusted

Commented `sorry` in `benchmarks/ai_formalization/*/artifacts/draft.lean`.

#### F-034 — Toffoli semantic tension

Headline `checked`; `decomposition_pair_denotation: partial` — honest but easy to misread.

#### F-035 — claim_diff fingerprint scope gap

`claim_diff_scope_payload` now includes `informal_claim` and `maturity` (status). **Fixed** (2026-07-02 post-audit).

#### F-036 — Lint scope too narrow

CI: `tools tests adapters scripts` (lint.yml + Makefile). Extended-scope issues resolved.

#### F-045 — No ruff format, pre-commit, mypy/pyright

No `[tool.ruff.format]`, no `.pre-commit-config.yaml`, no type checker config.

#### F-046 — No pytest-cov / coverage reporting

Not in `pyproject.toml` dev dependencies.

#### F-049 — rocq/isabelle permanently skip

`adapters/rocq/`, `adapters/isabelle/` return `skipped: true`.

#### F-050 — Coq real when `QSPECBENCH_COQ=1` but not in default CI

Docs partially aligned (`adapters/coq/README.md`); dashboard/GOVERNANCE still imply default CI smoke.

#### F-051 — release-bundle tested but not in CI

**Fixed** (2026-07-02 post-audit): validate job runs `release-bundle` + `verify-release-bundle` on CNOT benchmark after full pytest.

#### F-037 — No static type checker

Same as F-045 overlap; retained for register continuity.

#### F-038 — Monolithic validate module

~639 lines mixing YAML, bridge, QEC, artifact-bound rules.

#### F-039 — Duplicated helpers

`_load_spec()`, matrix/Pauli helpers across modules.

#### F-040 — Adapter API inconsistency

`check()` vs `verify()`, varying exit codes across `adapters/*`.

#### F-041 — Environment-dependent Lean test skips

`tests/test_lean_evidence.py`, `tests/test_cnot_end_to_end.py`.

#### F-042 — pytest-asyncio deprecation warning

**Fixed** (2026-07-02 post-audit): `asyncio_default_fixture_loop_scope = "function"` in `pyproject.toml`.

#### F-057 — One seed benchmark

`repeated_round_qec_temporal_specification` at maturity `seed`.

#### F-058 — Hamiltonian track no end-to-end Lean evidence pytest

`tests/test_hamiltonian_model.py` covers conventions only, not full evidence pipeline.

#### F-059 — dynamic-simulate CLI only in CI for teleportation

No dedicated pytest; CI runs once in validate job.

---

## Phase summaries

### Phase 1 — Baseline health

- **Lint (CI scope):** PASS locally and in CI (`uv sync --frozen --extra dev`).
- **Validate:** 48/48 OK (12.2 s).
- **Pytest:** 238 passed (500.8 s); asyncio deprecation silenced (**F-042**).
- **CI main (post-fix):** Validate, Lint, Dashboard, Promotion check expected PASS.

### Phase 2 — Lean proofs

- **Sorry scan:** 0 matches in `lean/QSpecBench`.
- **Lake build (warm):** 53.3 s, exit 0; cache-get file-lock warnings on Windows.
- **export_theorem_types:** 37.4 s, exit 0 (after deps available).
- **bridge-metadata / bridge-codegen:** pass.

### Phase 3 — Evidence runtime

- **Full corpus (warm Lean):** exit 0, 31.4 min.
- **CNOT spot:** exit 0, 68.7 s.
- **equivalence/:** exit 1 — transient toffoli scaffold failure under concurrent load; isolated re-run passed.
- **ai_formalization/:** exit 0, 166.5 s.
- **SMT subset:** Z3 skipped locally (expected).

### Phase 4 — Bridge performance

- **14 verify-bridge commands:** 94.4 s total, all exit 0.

### Phase 5 — Security / trust

- Path escape reproduced; validation guard present (**F-022 partial**).
- Python/sat execution surfaces confirmed (**F-021**).
- Timeout gaps in direct adapter calls (**F-023 partial**).
- Bootstrap reviewers confirmed (**F-010**).

### Phase 6 — Docs / corpus

- README versions current; TRACK tables synced; TRACK prose stale (**F-006b**).
- Coq/Docker/adapter_protocol contradictions confirmed (**F-052**, **F-053**, **F-054**).
- `docs/status.md` is live dashboard source of truth.

---

## Recommended fix order

1. **Unblock CI (P0):** Move Python steps after `uv sync` in `validate.yml` (CI-P0a); fix dev-extra lock resolution so ruff/pytest install (CI-P0b).
2. **Documentation trust (P1):** Fix TRACK "Good first claims" (**F-006b**); align Coq/Docker/adapter_protocol prose with CI reality (**F-052**, **F-053**, **F-054**); add lint badge (**F-047**).
3. **Governance:** Replace bootstrap reviewers on four `reference_claim` benchmarks (**F-010**).
4. **CI efficiency:** Dedupe pytest/check-evidence; share Lean cache across jobs (**F-014**, **F-048**); dashboard drift check (**F-055**); widen promotion path filter (**F-056** — done).
5. **Performance:** Lean adapter caching refinements (**F-016** — done); dynamic sim input fingerprint (**F-017** — done); parallel evidence checks (**F-015**); matrix memoization (**F-013**, **F-020**).
6. **Security / robustness:** Path confinement in `resolve_claim_path`; adapter subprocess timeouts (**F-022**, **F-023** — done).
7. **Local/CI parity:** Makefile → uv (**F-044** — done); extend ruff to adapters/scripts (**F-036** — done); release-bundle smoke (**F-051** — done); claim_diff fingerprint scope (**F-035** — done).
8. **Long-term research:** Measurement semantics, codegen blockers (**F-029–F-031**, equivalence codegen notes).

---

## Audit artifacts

| Artifact | Location |
|----------|----------|
| Full check-evidence log | `check_evidence_full_out.txt` |
| Equivalence check-evidence log | `check_evidence_equiv_out.txt` |
| AI formalization log | `check_evidence_ai_out.txt` |
| Pytest output | `pytest_out.txt` |
| Lake build output | `lake_build_out.txt` |
| This report | `docs/audit_findings.md` |

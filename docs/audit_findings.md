# QSpecBench Full Repository Audit Findings

**Audit date:** 2026-07-02  
**Repository:** `c:\Users\mateo\QSpecBench`  
**Branch audited:** local working tree (aligned with `main` post PR #3 merge)  
**Methodology:** Six-phase full runtime audit per plan `qspecbench_full_audit_d7fcde3e.plan.md`

## Scope note

**Lean-only proof verification.** Coq, Rocq, and Isabelle adapters, proofs, and runtime failures are **out of scope**. CI Coq install/smoke steps are noted only as CI noise to remove. No Coq/Rocq/Isabelle findings appear below.

---

## Executive summary

| Severity | Confirmed | Suspected | Total |
|----------|-----------|-----------|-------|
| **P0** | 3 | 0 | 3 |
| **P1** | 8 | 0 | 8 |
| **P2** | 10 | 1 | 11 |
| **P3** | 12 | 3 | 15 |
| **Total** | **33** | **4** | **37** |

### Confirmed P0 / P1 (action required)

| ID | Severity | Title |
|----|----------|-------|
| F-001 | P0 | Lint CI fails on 3 unused imports |
| F-002 | P0 | Stale `validate_out.txt` misreported 3 validation failures (deleted) |
| F-003 | P0 | Validate CI blocked by Coq smoke step before Lean/Python gates run |
| F-004 | P1 | README version table stale (schema 0.2 / v0.2.2 vs code 0.3 / v0.2.3) |
| F-005 | P1 | `docs/reference_benchmarks.md` claims `artifact_bound_reference_claim` unassigned; 6 benchmarks use it |
| F-006 | P1 | Track `TRACK.md` maturity tables stale vs live `spec.yaml` |
| F-007 | P1 | Orphaned failed teleportation `.result.json` sidecar misleads browsers |
| F-008 | P1 | Promotion CI uses `check=False` on claim-diff |
| F-009 | P1 | `uv.lock` present but CI uses unpinned `pip install -e ".[dev]"` |
| F-010 | P1 | Four `reference_claim` benchmarks still use `maintainer-bootstrap` reviewers |
| F-011 | P1 | GitHub Actions Node 20 deprecation warnings on checkout/setup-python |

### Runtime measurements (2026-07-02, Windows)

| Command | Wall time | Exit | Notes |
|---------|-----------|------|-------|
| `ruff check tools tests` | 0.08 s | 1 | 3 F401 unused imports |
| `qspecbench validate benchmarks/` | 8.99 s | 0 | 48/48 OK |
| `pytest tests/ -q --tb=no` | 538.69 s (~9.0 min) | 0 | 238 passed |
| `qspecbench bridge-codegen verify benchmarks/` | 9.35 s | 0 | 9 codegen bridges OK |
| `qspecbench verify-bridge` (14 CI subset) | 106.49 s | 0 | All 14 OK |
| `qspecbench check-evidence benchmarks/` | 601.65 s (~10.0 min) | 1 | 46 `lean_proof` FAIL (see F-043) |
| `qspecbench check-evidence benchmarks/equivalence/` | 216.57 s | 1 | QCEC OK; lean FAIL during cold build |
| `qspecbench check-evidence benchmarks/qec/distance_certificate_small_css_code/` | 19.4 s | 0 | SMT skipped (Z3 unavailable locally) |
| `qspecbench check-evidence benchmarks/ai_formalization/` | 59.24 s | 1 | 6/7 lean_kernel_check FAIL during cold build |
| `lake build` (cold, `.lake` deleted) | **9104.6 s (~152 min)** | 0 | Full Mathlib compile from scratch |
| `lake build` (cached, after cold) | 3.78 s | 0 | Replay-only |
| Single `lean` adapter invocation (CNOT evidence) | 21.62 s | 0 | After build; includes elan + sorry scan |

### Blockers and environmental notes

- **Lake/elan installed** — cold Mathlib build is extremely slow locally (~2.5 h).
- **Z3 not installed locally** — SMT evidence skipped with adapter note (expected).
- **F-043:** Full-corpus `check-evidence` ran concurrent with cold `lake build`; 46 `lean_proof` failures were missing `.olean` artifacts, not spec bugs. Post-build CNOT spot-check passes.

### CI divergence (Lean-relevant only)

| Workflow | Run (main, 2026-06-30) | Local | Lean-relevant root cause |
|----------|------------------------|-------|--------------------------|
| Lint | FAIL (#28429336211) | FAIL | Same 3 F401 errors |
| Validate | FAIL (#28429336243) | N/A | Coq smoke error — never reaches Python validate |
| Dashboard | PASS (#28429336265) | — | Independent |
| Promotion check | FAIL (PR runs) | — | Cascades from validate / claim-diff non-blocking |

Local validate/pytest **passes** (48/48, 238 tests) because Coq steps are not run locally.

---

## Findings register

### P0 — Broken / CI-blocking

#### F-001 — Lint CI fails on unused imports

| Field | Value |
|-------|-------|
| **Severity** | P0 |
| **Category** | CI / lint |
| **Status** | **Confirmed** |
| **Affected paths** | `tests/test_phase5.py:18`, `tools/qspecbench/bridge_manifest.py:325,332` |
| **Fix effort** | S |

**Reproduction:**
```powershell
ruff check tools tests
# F401: LEAN_AST_SHA256_FIELD, THEOREM_SOURCE_HASH_FIELD, verify_kernel_artifact_semantics_bridge
# Found 3 errors. Exit 1.
```

CI run `28429336211` fails identically.

---

#### F-002 — Stale local `validate_out.txt`

| Field | Value |
|-------|-------|
| **Severity** | P0 |
| **Category** | Governance / false alarm |
| **Status** | **Confirmed** (remediated: deleted) |
| **Affected paths** | `validate_out.txt` (was untracked) |
| **Fix effort** | S |

**Reproduction:** Stale file reported FAILs for teleportation claim_diff, toffoli YAML parse, bit-flip schema. Current run: `qspecbench validate benchmarks/` → 48/48 OK, exit 0.

**Action taken:** Deleted during audit.

---

#### F-003 — Validate CI blocked by Coq smoke

| Field | Value |
|-------|-------|
| **Severity** | P0 |
| **Category** | CI architecture |
| **Status** | **Confirmed** |
| **Affected paths** | `.github/workflows/validate.yml:31-39` |
| **Fix effort** | S (remove Coq steps only) |

**Reproduction:**
```text
gh run view 28429336243 --log-failed
# coqc cnot_coq_smoke.v — Error at line 6 — exit 1
```

---

### P1 — Documentation / governance

#### F-004 — README version table stale

| Field | Value |
|-------|-------|
| **Severity** | P1 |
| **Category** | Documentation |
| **Status** | **Confirmed** |
| **Affected paths** | `README.md:182-185`, `tools/qspecbench/__init__.py`, `docs/status.md` |
| **Fix effort** | S |

README: schema **0.2**, release **v0.2.2**. Code/dashboard: schema **0.3**, release **v0.2.3**.

---

#### F-005 — `reference_benchmarks.md` outdated

| Field | Value |
|-------|-------|
| **Severity** | P1 |
| **Category** | Documentation / governance |
| **Status** | **Confirmed** |
| **Affected paths** | `docs/reference_benchmarks.md:15-17` |
| **Fix effort** | S |

Claims `artifact_bound_reference_claim` unassigned; **6** benchmarks use it per dashboard and specs.

---

#### F-006 — Track `TRACK.md` maturity tables stale

| Field | Value |
|-------|-------|
| **Severity** | P1 |
| **Category** | Documentation / governance |
| **Status** | **Confirmed** |
| **Affected paths** | `benchmarks/*/TRACK.md`, `scripts/sync_readme_maturity.py:16-19` |
| **Fix effort** | M |

Example: `benchmarks/equivalence/TRACK.md` lists `toffoli_decomposition_equivalence` as `usable`; spec has `artifact_bound_reference_claim`. `MATURITY_RE` omits `artifact_bound_reference_claim`, so README sync silently skips those benchmarks.

---

#### F-007 — Orphaned failed evidence sidecar

| Field | Value |
|-------|-------|
| **Severity** | P1 |
| **Category** | Corpus hygiene |
| **Status** | **Confirmed** |
| **Affected paths** | `benchmarks/algorithms/teleportation_preserves_state_up_to_pauli_correction/evidence/dynamic_simulation_basis_check.result.json` |
| **Fix effort** | S |

Sidecar shows `ok: false` from attempting to execute JSON as Python (`NameError: name 'null' is not defined`). Not enforced by `validate`; misleading to humans. Current `dynamic_basis_check` evidence passes at runtime.

---

#### F-008 — Promotion CI ignores claim-diff failures

| Field | Value |
|-------|-------|
| **Severity** | P1 |
| **Category** | CI / governance |
| **Status** | **Confirmed** |
| **Affected paths** | `.github/workflows/promotion-check.yml:39` |
| **Fix effort** | S |

`subprocess.run(..., check=False)` — stale `claim_diff.md` will not block PRs.

---

#### F-009 — `uv.lock` unused in CI

| Field | Value |
|-------|-------|
| **Severity** | P1 |
| **Category** | CI / reproducibility |
| **Status** | **Confirmed** |
| **Affected paths** | `uv.lock`, `.github/workflows/*.yml`, `pyproject.toml` |
| **Fix effort** | M |

CI installs via `pip install -e ".[dev]"` with `>=` constraints; lockfile not enforced.

---

#### F-010 — Bootstrap reviewers on `reference_claim` benchmarks

| Field | Value |
|-------|-------|
| **Severity** | P1 |
| **Category** | Governance |
| **Status** | **Confirmed** |
| **Affected paths** | `three_qubit_bit_flip_code_corrects_one_x`, `small_fermionic_hamiltonian_is_hermitian`, `qft_inverse_qft_small_instance`, `qft_then_inverse_qft_identity_up_to_ordering` specs |
| **Fix effort** | M |

Four `reference_claim` benchmarks use `reviewer: maintainer-bootstrap`. Validator hard-fails bootstrap only for `artifact_bound_reference_claim` and `ai_formalization` reference_claim.

---

#### F-011 — GitHub Actions Node 20 deprecation warnings

| Field | Value |
|-------|-------|
| **Severity** | P1 |
| **Category** | CI maintenance |
| **Status** | **Confirmed** |
| **Affected paths** | `actions/checkout@v4`, `actions/setup-python@v5` |
| **Fix effort** | S |

CI logs: "Node 20 is being deprecated… running with Node 24 by default."

---

### P2 — Performance / scalability

#### F-012 — Exponential QASM matrix without global qubit cap

| Field | Value |
|-------|-------|
| **Severity** | P2 |
| **Category** | Performance |
| **Status** | **Suspected** (code review; no large-circuit timing run) |
| **Affected paths** | `tools/qspecbench/qasm_matrix.py` |
| **Fix effort** | M |

Builds full `2^n × 2^n` matrices with Python `Fraction` (O(4^n) memory). Dynamic simulator caps at 4 qubits; matrix extractor has no equivalent cap.

---

#### F-013 — Duplicate matrix work in bridge validation

| Field | Value |
|-------|-------|
| **Severity** | P2 |
| **Category** | Performance |
| **Status** | **Confirmed** (code + runtime) |
| **Affected paths** | `tools/qspecbench/verify_bridge.py:71-74`, `tools/qspecbench/validate.py:179` |
| **Fix effort** | M |

`verify_bridge()` calls `extract_matrix` then `denotate_ops` (rebuilds unitary). Invoked inline during validate for every bridged benchmark; 14-bridge subset took 106 s.

---

#### F-014 — Redundant CI work in validate job

| Field | Value |
|-------|-------|
| **Severity** | P2 |
| **Category** | Performance / CI |
| **Status** | **Confirmed** (workflow review) |
| **Affected paths** | `.github/workflows/validate.yml:49-58` |
| **Fix effort** | M |

Job runs full validate, bridge-codegen verify, check-evidence twice (single + full corpus), subset pytest, then full pytest — duplicating matrix/Lean work.

---

#### F-015 — Sequential evidence checks

| Field | Value |
|-------|-------|
| **Severity** | P2 |
| **Category** | Performance |
| **Status** | **Confirmed** |
| **Affected paths** | `tools/qspecbench/evidence_runner.py:208` |
| **Fix effort** | M |

One `subprocess.run` per evidence item; no cross-benchmark parallelism.

---

#### F-016 — Lean adapter overhead per invocation

| Field | Value |
|-------|-------|
| **Severity** | P2 |
| **Category** | Performance |
| **Status** | **Confirmed** |
| **Affected paths** | `adapters/lean/parse_result.py:81-130` |
| **Fix effort** | M |

Each check: full-package `sorry` scan (`rglob("*.lean")`), `elan toolchain install`, then `lake env lean`. Single CNOT evidence check: **21.6 s** even with warm build. Dominates 10-min full-corpus check-evidence.

---

#### F-017 — Dynamic simulation regenerated on validate path

| Field | Value |
|-------|-------|
| **Severity** | P2 |
| **Category** | Performance |
| **Status** | **Suspected** (code review) |
| **Affected paths** | `tools/qspecbench/dynamic_simulation_evidence.py` |
| **Fix effort** | S |

Teleportation basis checks re-run instead of fingerprint-only compare when inputs unchanged.

---

#### F-018 — Release bundle loads all files into RAM

| Field | Value |
|-------|-------|
| **Severity** | P2 |
| **Category** | Performance / memory |
| **Status** | **Confirmed** (code review) |
| **Affected paths** | `tools/qspecbench/release_bundle.py:285-333` |
| **Fix effort** | M |

`payloads: dict[str, bytes]` holds entire bundle before tar write.

---

#### F-019 — Slow local/CI test suite

| Field | Value |
|-------|-------|
| **Severity** | P2 |
| **Category** | Performance / CI |
| **Status** | **Confirmed** |
| **Affected paths** | `tests/`, `.github/workflows/validate.yml` (45 min timeout) |
| **Fix effort** | L |

238 tests in **538.7 s** (~9 min) locally; Lean evidence tests dominate. CI 45-minute timeout is tight as corpus grows.

---

#### F-020 — Uncached manifest reload

| Field | Value |
|-------|-------|
| **Severity** | P2 |
| **Category** | Performance |
| **Status** | **Confirmed** (code review) |
| **Affected paths** | `tools/qspecbench/bridge_manifest.py:69` |
| **Fix effort** | S |

`load_manifest()` re-reads JSON on every lookup (contrast `@lru_cache` in `schema.py`).

---

#### F-043 — Cold lake build blocks lean evidence (audit artifact)

| Field | Value |
|-------|-------|
| **Severity** | P2 |
| **Category** | Performance / operational |
| **Status** | **Confirmed** |
| **Affected paths** | `lean/`, `adapters/lean/parse_result.py`, CI elan steps |
| **Fix effort** | L |

**Reproduction:** During audit, cold `lake build` (~152 min) ran concurrent with `check-evidence`. Failures:
```text
object file '.\\.\\.lake\\build\\lib\\QSpecBench\\Quantum\\OpenQASM3.olean' ... does not exist
```
46 `FAIL lean_*` entries in full corpus run. After build: CNOT evidence `ok: true`. **pytest** (238 pass) uses Lean tests that assume prior/cached build.

---

### P2 — Security / robustness

#### F-021 — Arbitrary code execution via evidence adapters

| Field | Value |
|-------|-------|
| **Severity** | P2 |
| **Category** | Security (by design) |
| **Status** | **Confirmed** (code review) |
| **Affected paths** | `adapters/python/parse_result.py`, `adapters/sat_certificate/parse_result.py` |
| **Fix effort** | L |

Evidence scripts executed via `subprocess.run([sys.executable, path])` with no sandbox or timeout. High risk if corpus is compromised.

---

#### F-022 — No path confinement for artifact paths

| Field | Value |
|-------|-------|
| **Severity** | P2 |
| **Category** | Security |
| **Status** | **Confirmed** |
| **Affected paths** | `tools/qspecbench/artifacts.py:35-36` |
| **Fix effort** | M |

**Reproduction:**
```python
resolve_claim_path(Path("benchmarks/algorithms/bell_state_preparation"), "../../README.md")
# → C:\Users\mateo\QSpecBench\benchmarks\README.md (escapes claim dir)
```

---

#### F-023 — Subprocess calls lack timeouts

| Field | Value |
|-------|-------|
| **Severity** | P2 |
| **Category** | Security / robustness |
| **Status** | **Confirmed** |
| **Affected paths** | `evidence_runner.py`, `adapters/lean/parse_result.py`, `adapters/python/parse_result.py`, most adapters |
| **Fix effort** | M |

Only `bridge_codegen.py` (120 s) and `export_theorem_types.py` (300 s) set timeouts. Hung `lake env lean` can block CI/local indefinitely.

---

#### F-024 — Silent failure patterns

| Field | Value |
|-------|-------|
| **Severity** | P2 |
| **Category** | Robustness |
| **Status** | **Confirmed** (code review) |
| **Affected paths** | `validate.py:77-78` (JSON decode → None), `evidence_runner.py:241-242` (JSON parse pass), backfill scripts |
| **Fix effort** | M |

Malformed bridge JSON or adapter stdout can fail silently instead of surfacing validation errors.

---

#### F-025 — `load_spec()` returns None on empty YAML

| Field | Value |
|-------|-------|
| **Severity** | P2 |
| **Category** | Robustness |
| **Status** | **Confirmed** (code review) |
| **Affected paths** | `tools/qspecbench/validate.py:64-66` |
| **Fix effort** | S |

`yaml.safe_load` on empty file returns `None`; callers may raise `AttributeError` instead of a validation error.

---

#### F-026 — Weak human-review gate

| Field | Value |
|-------|-------|
| **Severity** | P2 |
| **Category** | Security / trust |
| **Status** | **Confirmed** |
| **Affected paths** | `adapters/human_review/parse_result.py` |
| **Fix effort** | M |

Pass if ≥80 chars + keyword from small list; `trust_level: externally_trusted`.

---

### P3 — Incomplete by design / limitations

#### F-027 — Corpus mostly scaffolds

| Field | Value |
|-------|-------|
| **Severity** | P3 |
| **Category** | Maturity |
| **Status** | **Confirmed** |
| **Affected paths** | `docs/status.md` |
| **Fix effort** | L (ongoing) |

Dashboard: 28 `reference_scaffold`, 10 headline-checked, 38 unchecked headline assumptions, 37 partial evidence statuses.

---

#### F-028 — Schema evidence types without adapters

| Field | Value |
|-------|-------|
| **Severity** | P3 |
| **Category** | Schema / tooling gap |
| **Status** | **Confirmed** |
| **Affected paths** | `schema/qspecbench.schema.json`, `tools/qspecbench/evidence_runner.py` |
| **Fix effort** | M |

`qbricks_result`, `zx_certificate` in schema; absent from `EVIDENCE_TYPE_ADAPTERS`. No corpus usage found.

---

#### F-029 — Lean S/T gates stubbed as identity

| Field | Value |
|-------|-------|
| **Severity** | P3 |
| **Category** | Proof limitation |
| **Status** | **Confirmed** (documented) |
| **Affected paths** | `lean/QSpecBench/Quantum/OpenQASM3.lean` |
| **Fix effort** | L |

Limits kernel-checked proofs on circuits needing phase gates.

---

#### F-030 — OpenQASM parser subset

| Field | Value |
|-------|-------|
| **Severity** | P3 |
| **Category** | Proof limitation |
| **Status** | **Confirmed** (documented) |
| **Affected paths** | `lean/QSpecBench/Quantum/OpenQASM3Parser.lean`, `docs/roadmap.md` |
| **Fix effort** | L |

Handles H/X/CX/CCX only; full codegen pipeline incomplete.

---

#### F-031 — Measurement / dynamic semantics partial

| Field | Value |
|-------|-------|
| **Severity** | P3 |
| **Category** | Proof limitation |
| **Status** | **Confirmed** (documented) |
| **Affected paths** | `lean/QSpecBench/Quantum/Measurement.lean`, teleportation/grover benchmarks |
| **Fix effort** | L |

Headline proofs blocked on measurement semantics.

---

#### F-032 — Deutsch–Jozsa oracle placeholder

| Field | Value |
|-------|-------|
| **Severity** | P3 |
| **Category** | Corpus completeness |
| **Status** | **Confirmed** |
| **Affected paths** | `benchmarks/algorithms/deutsch_jozsa_constant_balanced_distinction/artifacts/circuit.qasm:8` |
| **Fix effort** | M |

`// oracle placeholder` in circuit artifact.

---

#### F-033 — AI formalization drafts untrusted

| Field | Value |
|-------|-------|
| **Severity** | P3 |
| **Category** | Trust boundary |
| **Status** | **Confirmed** |
| **Affected paths** | `benchmarks/ai_formalization/*/artifacts/draft.lean` |
| **Fix effort** | N/A |

Placeholders with commented `sorry`; not checked evidence.

---

#### F-034 — Toffoli semantic tension

| Field | Value |
|-------|-------|
| **Severity** | P3 |
| **Category** | Governance clarity |
| **Status** | **Confirmed** |
| **Affected paths** | `benchmarks/equivalence/toffoli_decomposition_equivalence/spec.yaml` |
| **Fix effort** | S (docs) |

`proof_obligations.decomposition_pair_denotation: partial` but headline `checked` and empty `unproved_obligations` — honest per policy but easy to misread.

---

#### F-035 — claim_diff fingerprint scope gap

| Field | Value |
|-------|-------|
| **Severity** | P3 |
| **Category** | Tooling |
| **Status** | **Suspected** (code review) |
| **Affected paths** | `tools/qspecbench/claim_diff.py` |
| **Fix effort** | S |

`claim_diff_scope_payload` may omit fields present in rendered report (`informal_claim`, `maturity`), causing confusing stale-body errors.

---

### P3 — Code quality / maintainability

#### F-036 — Lint scope too narrow

| Field | Value |
|-------|-------|
| **Severity** | P3 |
| **Category** | Code quality |
| **Status** | **Confirmed** |
| **Affected paths** | CI lint workflow |
| **Fix effort** | S |

CI lints only `tools tests`; not `adapters/`, `scripts/`, benchmark evidence Python.

---

#### F-037 — No static type checker

| Field | Value |
|-------|-------|
| **Severity** | P3 |
| **Category** | Code quality |
| **Status** | **Confirmed** |
| **Affected paths** | repo-wide |
| **Fix effort** | L |

No mypy/pyright config.

---

#### F-038 — Monolithic validate module

| Field | Value |
|-------|-------|
| **Severity** | P3 |
| **Category** | Maintainability |
| **Status** | **Confirmed** |
| **Affected paths** | `tools/qspecbench/validate.py` (~620 lines) |
| **Fix effort** | L |

Mixes YAML, bridge, QEC, artifact-bound, AI reviewer rules.

---

#### F-039 — Duplicated helpers

| Field | Value |
|-------|-------|
| **Severity** | P3 |
| **Category** | Maintainability |
| **Status** | **Suspected** |
| **Affected paths** | bridge modules, scripts, benchmark evidence |
| **Fix effort** | M |

`_load_spec()`, matrix/Pauli helpers copied across modules.

---

#### F-040 — Adapter API inconsistency

| Field | Value |
|-------|-------|
| **Severity** | P3 |
| **Category** | Maintainability |
| **Status** | **Confirmed** (code review) |
| **Affected paths** | `adapters/*` |
| **Fix effort** | M |

`check()` vs `verify()`, varying arg counts, differing exit-code semantics.

---

#### F-041 — Environment-dependent Lean test skips

| Field | Value |
|-------|-------|
| **Severity** | P3 |
| **Category** | Testing |
| **Status** | **Confirmed** |
| **Affected paths** | `tests/test_lean_evidence.py`, `tests/test_cnot_end_to_end.py` |
| **Fix effort** | M |

Skip without `lake`/elan; reduced coverage signal for developers without Lean.

---

#### F-042 — pytest-asyncio deprecation warning

| Field | Value |
|-------|-------|
| **Severity** | P3 |
| **Category** | Testing / noise |
| **Status** | **Confirmed** |
| **Affected paths** | pytest run output |
| **Fix effort** | S |

Unset `asyncio_default_fixture_loop_scope` (conda pytest-asyncio plugin).

---

## Phase summaries

### Phase 1 — Baseline health

- **Lint:** FAIL (3 F401) — matches CI.
- **Validate:** 48/48 OK (~9 s).
- **Pytest:** 238 passed (~9 min).
- **CI:** Lint + Validate fail on main; Dashboard passes.
- **`validate_out.txt`:** Confirmed stale; **deleted**.

### Phase 2 — Lean proofs

- **`sorry` scan (`lean/`):** 0 matches.
- **Cold `lake build`:** Success after ~152 min.
- **Cached `lake build`:** 3.8 s.
- **Spot-check:** CNOT `lean_proof` passes post-build (`ok: true`).

### Phase 3 — Evidence runtime

- **Full corpus check-evidence:** Exit 1; 46 lean failures during concurrent cold build (F-043); non-lean evidence (QCEC, bridge_verify, qec, python) largely OK.
- **Bridge verify subset (14):** All OK (~106 s).
- **Bridge-codegen verify:** 9/9 OK (~9 s).
- **QCEC subset (`equivalence/`):** QCEC passes; lean failed during build window.
- **SMT subset:** Skipped — Z3 not installed locally.
- **AI formalization:** 6/7 lean_kernel_check failed during build; rubric checks mostly OK.

### Phase 4 — Performance

See runtime table above. Dominant costs: cold Mathlib build, sequential lean adapter (~22 s × N), full pytest (~9 min), verify-bridge inline during validate.

### Phase 5 — Security

Path traversal reproduced (F-022). Code execution surfaces confirmed (F-021). Timeout gaps confirmed (F-023). Silent JSON failures confirmed (F-024).

### Phase 6 — Docs / governance

README versions stale (F-004). `reference_benchmarks.md` stale (F-005). TRACK.md stale (F-006). Dashboard (`docs/status.md`) is current source of truth.

---

## Recommended fix order

1. **Unblock CI:** `ruff check --fix`; remove Coq steps from `validate.yml` (F-001, F-003).
2. **Sync docs:** README versions, `reference_benchmarks.md`, regen TRACK.md, fix `sync_readme_maturity.py` (F-004–F-006).
3. **CI hardening:** Promotion claim-diff `check=True`, adopt `uv sync` or hash pinning (F-008, F-009).
4. **Lean perf:** Cache sorry scan + elan install in lean adapter; ensure CI uses Mathlib cache before check-evidence (F-016, F-043).
5. **Security:** Path confinement, subprocess timeouts (F-022, F-023).
6. **Hygiene:** Remove teleportation orphan `.result.json` (F-007).

---

## Audit artifacts

| Artifact | Location |
|----------|----------|
| Full check-evidence log | `check_evidence_out.txt` (repo root, audit-generated) |
| This report | `docs/audit_findings.md` |

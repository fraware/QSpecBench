# Definition of completion

Single checklist for when QSpecBench may honestly be called a **community-grade**
benchmark and evidence infrastructure with selected checked claims — not a complete
quantum FV standard.

Until every box that is marked **required** is met, public language stays:
**scoped research benchmark and evidence infrastructure with selected checked claims.**

Regenerate live counts with:

```bash
qspecbench dashboard benchmarks/ --out docs/status.md
```

Cross-check maturity with `rg "maturity:" benchmarks/**/spec.yaml` (exclude `_template`).

---

## Truth (required)

| # | Criterion | How verified | Status |
|---|-----------|--------------|--------|
| T1 | Dashboard / README maturity counts match live `spec.yaml` | `docs/status.md` + validate drift gate (`git diff --exit-code docs/status.md`) | Met (regenerate on corpus change) |
| T2 | GOVERNANCE ABRC / RC lists match corpus | [GOVERNANCE.md](../GOVERNANCE.md), [reference_benchmarks.md](reference_benchmarks.md) | Synced to 10 ABRC / 9 RC |
| T3 | No `maintainer-bootstrap` reviewers on checked headlines | `rg maintainer-bootstrap benchmarks/**/spec.yaml` empty; `tools/qspecbench/reviews.py` | Met (F-010 closed) |
| T4 | Dual hash-bound reviews on every ABRC / `reference_claim` | `schema/review_artifact.schema.json` + `qspecbench validate` | Met for current ABRC/RC pilots |
| T5 | AI formalization: ≥1 gold + real dual reviews before `reference_claim` | [ai_formalization_track.md](ai_formalization_track.md); `benchmarks/ai_formalization/TRACK.md` | **Met** (4 of 7 benchmarks promoted with frozen gold + dual reviews); remaining 3 stay `reference_scaffold`/`usable` |
| T6 | Claim identity stable on promotions (`proposition_id`, obligation lists) | `claim_identity` in each promoted `spec.yaml` | Process requirement (ongoing) |

---

## Technical (required for trustworthy tags)

| # | Criterion | How verified | Status |
|---|-----------|--------------|--------|
| K1 | Schema validate + evidence + bridge gates in CI | `.github/workflows/validate.yml` | Met |
| K2 | Hard pyright (no soft-fail) on trust surface | `.github/workflows/lint.yml` | **Met** (Phase B) |
| K3 | `lake build QSpecBench.Evidence.All` in CI as separate job (never imported into root `QSpecBench.lean`) | [lean/QSpecBench.lean](../lean/QSpecBench.lean); release/validate workflows | **Met** (OOM split; separate Evidence.All job) |
| K4 | Release bundle with `--require-review-artifacts` | `tools/qspecbench/release_bundle.py`; `.github/workflows/release.yml` | **Met** (Phase B) |
| K5 | Stim / `qec-matching` extras installed where Stim evidence is claimed | `pyproject.toml` extra `qec-matching` + CI | **Met** (Phase B) |
| K6 | Meaningful coverage floor on promotion/reviews/bridges | pytest-cov / lint workflows | **Met** (F-046; `--cov-fail-under=55` on trust surface) |

---

## Research (required scientific leftovers)

| # | Criterion | Spec / obligation | Status |
|---|-----------|-------------------|--------|
| R1 | General CB for arbitrary CPTP, or honest permanent narrowing | `general_cb_arbitrary_cptp_mathlib` on Hamiltonian Trotter / CB benchmarks | **Closed (permanent N/A, v3):** proved subclass `qubit_cptp_cb_proved_subclass_mathlib`; obligation `not_applicable` |
| R2 | Syndrome-extraction circuit semantics for bit-flip QEC | `syndrome_extraction_circuit_semantics` on `three_qubit_bit_flip_code_corrects_one_x` | **Met** (`checked`; `unproved_obligations: []`) |
| R3 | AI formalization gold freeze + dual reviews (≥1 bench) | Four benches at `reference_claim`; see T5 and `benchmarks/ai_formalization/TRACK.md` | **Met** (4 RC benches with gold + dual reviews each) |

Required research boxes R1–R3 are closed. Optional deeper research (not DoD-blocking
unless claimed): multi-step Trotter composition, matrix KERNEL_BRIDGE for dynamic measure+if,
surface-code MWPM beyond declared universe, Grover `amplitude_lift`, general n-qubit
Clifford source→target kernel proof beyond the declared H-H-S instance, bytes→AST Lean
parser, second proof assistant in default CI, gold-target freezes for the three
remaining `ai_formalization` benchmarks.

---

## Community (required for “community-grade”)

| # | Criterion | Where | Status |
|---|-----------|-------|--------|
| C1 | Named track maintainers in CODEOWNERS (not placeholders only) | `.github/CODEOWNERS` + GOVERNANCE assignment table | **Met** (roles named; interim sole owner `@fraware`; vacancies explicit TBA) |
| C2 | Open audit findings have GitHub issue IDs | [audit_issues.yaml](audit_issues.yaml) + [audit_github_issues.yaml](audit_github_issues.yaml) | **Met** (stable `QSB-AUD-*` stubs; remote issues on-demand) |
| C3 | Second-kernel policy explicit (Lean-primary vs Coq in default CI) | GOVERNANCE § Second-kernel policy | **Met** (Lean-primary; Coq/Rocq/Isabelle discovery/opt-in) |
| C4 | Contributor path: pre-commit + schema 0.3 migration + ABRC checklist | CONTRIBUTING, `.pre-commit-config.yaml`, [schema_migration_0.3.md](schema_migration_0.3.md) | **Met** |
| C5 | This DoD document kept current with [research_tracks.md](research_tracks.md) + README permanent residuals | docs | Met (Phase A + Phase D) |

---

## Permanent residuals (never block DoD by faking them)

**Community-grade ≠ complete quantum FV standard.** Meeting this DoD means a
scoped research benchmark and evidence infrastructure with selected checked
claims under declared universes — not unbounded industrial coverage, device
pulse fidelity, or every informal headline.

These items are **trust-boundary documentation**, not unfinished promotions.
Do not reopen them as “almost done” research or rename them into checked scope.

| Item | Disposition |
|------|-------------|
| `unbounded_all_codes_mwpm` | Keep `not_applicable`. Lean surfaces the impossibility note: `unbounded_all_codes_mwpm_infeasible_open_ended` / `unboundedAllCodesMwpmImpossibilityNote` in [`lean/QSpecBench/QEC/SyndromeExtraction.lean`](../lean/QSpecBench/QEC/SyndromeExtraction.lean) (also `#check`’d from `Evidence.All`). Open-ended code/distance/round family admits no finite certificate. |
| Device `hardware_semantics` / `device_fidelity` / `pulse_schedule_semantics` | Remain `not_checked` until a real device evidence path exists. Checked **`hardware_abstraction_isa_layer`** (software CanonicalAst ISA + fail-closed offline profile) is a **separate** obligation — never rename ISA-layer checks as device/pulse fidelity. |
| Unnormalized `denotateOps3C` Toffoli equality | Permanently out of scope (wrong semantics for the decomposition claim). Honest ABRC uses normalized Clifford+T denotation / native-CCX denotation. |
| QBricks / ZX | Adapters exist (`adapters/qbricks/`, `adapters/zx/`); still not a complete FV standard. Never sole-ABRC on them. |
| Rocq / Isabelle skip stubs | Never checked evidence; excluded from default maturity counts; optional/opt-in only (audit F-049). |
| Corpus-executed Python/SAT evidence | Trust-the-corpus model; constrained runner (timeout, claim-dir cwd jail, stripped network env, OS limits where available) reduces foot-guns — **not** a sandbox product (audit F-021). |
| Full industrial Stim/Blossom for all codes | Outside declared universe `stim_repetition_memory_odd_d_le_7_R_eq_d_p0p01`. Do not rename declared-universe MWPM discharge as all-codes industrial coverage. |

Canonical copy also lives in [research_tracks.md](research_tracks.md) (Permanent N/A) and the [README](../README.md) permanent-residuals section. Trust-boundary field vocabulary: [trust_boundaries.md](trust_boundaries.md).

---

## Live corpus snapshot (regenerate; do not hand-edit)

Source of truth: [status.md](status.md). At last final sync:

- **ABRC (`artifact_bound_reference_claim`):** 10
- **`reference_claim`:** 9 (includes 4 `ai_formalization` pilots — see `benchmarks/ai_formalization/TRACK.md`)
- **Total benchmarks (excl. `_template`):** 50

Promotion rules: [reference_benchmarks.md](reference_benchmarks.md), [GOVERNANCE.md](../GOVERNANCE.md).
Roadmap / phase history: [roadmap.md](roadmap.md).
Audit ledger: [audit_issues.yaml](audit_issues.yaml) (markdown summarizes).

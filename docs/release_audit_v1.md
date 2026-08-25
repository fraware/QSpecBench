# release_audit_v1

Decision: **revise**

This tree is the v1 engineering substrate plus honest demotion of the former gold claims and four machine-closed experimental flagship packages. It is not yet an immutable tagged release.

## Required audit list

| Item | Status |
|---|---|
| Empty/demoted gold inventory | Met in this tree (RC/ABRC count is 0) |
| Flagship machine-closure | Compiler (Qiskit Optimize1qGates H;X;X instance), dynamic teleportation (arbitrary pure-state instrument, not mixed-state CPTP), Hamiltonian (Frobenius-majorant X,Z instance at t=pi/4; not a general operator-norm Lie-Trotter theorem), three-qubit bit-flip layered QEC are packaged as `experimental_closed` under declared domains |
| Lean-QEC structured result | Adapter emits acceptance vs reproduction; workflow asserts structured fields and fails closed unless `acceptance.status=passing`. Cold default / authorized-fallback native acceptance is **not** proven on this working tree; lane remains honestly failing until an exact-head cold run produces a passing structured result |
| Branch-protection evidence | Admin residual; see `docs/governance_verification.md` |
| #9 exclusion | Explicit; not claimed |
| Residual: no independent reviewers | Explicit |

## Ship gate

Only `ship` tags `v1.0.0`. This audit remains `revise`. Engineering substrate checks (validate --strict-all --audit-graph, generated-doc drift, migration-report digest, focused substrate tests) can pass on this tree while ship gates below are unmet.

## Revise taxonomy

### (A) By-design governance / scope residuals

These are intentional under the owner mandate. Do not invent reviewers, change live admin protection from this code path, or close #9.

1. **No independent reviewers** — gold/RC/ABRC inventory stays empty; alias YAML is `unauthenticated_legacy_review` only.
2. **Branch protection admin-only** — live `main` settings are a repository-admin step; `docs/governance_verification.md` does not claim they are enabled.
3. **Issue #9 out of scope** — independent third-party cold-host reproduction remains `post-v1`.
4. **Lean-QEC not greened without cold proof** — do not skip, delete, or simulate the workflow; fallback is authorized only on the complete LRAT-trimmer signature.

### (B) Remaining engineering blockers

1. **Lean-QEC cold native acceptance** — exact-head cold run of `adapters/lean_qec/parse_result.py` under `QSPECBENCH_LEAN_QEC_VERIFY=1` must emit `ok=true`, `acceptance.status=passing`, `kernel_typechecking_bypassed=false`, with either `upstream_default_reproduced=true` or authorized `fallback_used=true` (complete LRAT-trimmer signature only). Until that structured result exists for the candidate SHA, the Lean-QEC CI job remains an honest fail and this audit stays `revise`.

Local cold attempts on this host (25 Aug 2026):

- First attempt: structured failure at required LFS materialization into `%TEMP%` (`There is not enough space on the disk` for ~210MB LRAT objects). Build not attempted.
- After adding `QSPECBENCH_LEAN_QEC_WORKDIR` and reclaiming disk: LFS materialization and pointer verification succeeded; failure moved to **disk exhaustion during elan toolchain install / lake cache** (`No space left on device` / incomplete `leanprover/lean4:v4.30.0-rc2` extract). Upstream default build and authorized LRAT-trimmer fallback were **not** reached.

These are honest pre-acceptance **disk** failures, not a green result and not evidence that the LRAT-trimmer fallback path is established. Prefer a host with several free gigabytes (toolchain + Mathlib cache + LFS), using `QSPECBENCH_LEAN_QEC_WORKDIR=artifacts/lean-qec/work` and `QSPECBENCH_LEAN_QEC_LOG_DIR=artifacts/lean-qec/logs`.

No other non-design engineering blockers are currently known on this tree after local substrate verification.

## Public language

Do not say verified, independently reviewed, community-grade, or reproduced except where the corresponding gate is actually met.

# Interoperability and compatibility matrix

This matrix distinguishes evidence paths that ship today from optional, planned, or disabled integrations. Presence in this table is not evidence of theorem correctness.

| Ecosystem | Repository status | Version policy | Trust / scope | Full-vision action |
|---|---|---|---|---|
| Lean 4 / Mathlib | active, default kernel path | current repo toolchain is pinned; preserve exact historical toolchain per release | kernel checks formal theorems under declared axioms/semantics | keep theorem/elaborator exports hash-bound |
| MQT QCEC | active external checker | historical corpus evidence remains pinned to `mqt.qcec==3.6.0`; newer compatibility must be a separate lane | externally trusted supporting equivalence evidence | typed request/result + explicit version/config/digest |
| Stim / PyMatching | active for declared QEC universes | pinned extras in `pyproject.toml` | finite simulation/decoder evidence only for declared code/noise/round universe | typed adapter IDs; never infer family/all-code correctness |
| QBricks | shipping adapter, not full-vision authority | external binary identity must be recorded when executed | externally trusted | protocol conformance + exact artifact/tool binding |
| ZX | shipping certificate adapter | checker/version must be recorded | independently checkable only to exact certificate proposition | protocol conformance; proposition relation explicit |
| Coq | optional, not default CI | opt-in local/custom-job | second-kernel evidence only when actually compiled | do not count unexecuted smoke files as evidence |
| Rocq | fail-closed/optional stub | no default passing path | not checked unless concrete executable integration exists | activate only for a driving benchmark |
| Isabelle | fail-closed/optional stub | no default passing path | not checked unless concrete executable integration exists | activate only for a driving benchmark |
| Lean-QEC | **planned; integration scaffold in `adapters/lean_qec/`** | version-isolated import first | theorem/certificate may support only explicit QEC obligations | issue #18 |
| Lean-Quantum / Lean-QIT | planned | version-isolated theorem/certificate import first | preserve upstream proposition, semantics and toolchain | evaluate for dynamic/channel/operator foundations before dependency unification |

## Compatibility doctrine

1. Never silently upgrade a tool version recorded in historical evidence.
2. A newer compatibility lane answers “does the benchmark still work under this tool version?”; it does not rewrite the evidence identity of an older release.
3. Prefer certificate/theorem exports across incompatible toolchains.
4. Bind exact external repository commit/toolchain when importing formal results.
5. Record proposition relation. An external theorem that is an instance or weakening is not an equivalent substitute for the advertised QSpecBench proposition.
6. A registered adapter has an explicit trust ceiling; no adapter may promote itself by returning a stronger label.
7. Do not add integrations only to increase the count of supported proof systems.

Issue #22 tracks the remaining executable compatibility lanes and conformance work.

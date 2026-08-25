# Research tracks — honest status

Progress notes without gold inflation. Definition of completion:
[definition_of_completion.md](definition_of_completion.md). Live maturity counts:
[generated_status.md](generated_status.md) and [status.md](status.md).

**v1 maturity doctrine:** packages that formerly carried `reference_claim` /
`artifact_bound_reference_claim` were demoted. Machine-closed packages use
`experimental_closed`. That label means assurance-graph obligation closure under
declared semantics **without** authenticated independent review. Historical
alias dual reviews may remain as `unauthenticated_legacy_review` and must not be
described as gold or community-grade review ([promotion freeze](promotion_freeze.md)).

---

## Equivalence

- Kernel artifact-denotation pilots prove **parse → Generated.ops → matrix** (or
  normalized variants), not full compiler equivalence for every pair.
- Several former ABRC packages (e.g. CNOT cancel, Hadamard conjugation, Clifford
  H-H-S, Toffoli normalized Clifford+T, native CCX) are now `experimental_closed`
  under their declared denotation scopes.
- **Genuine source–target denotation (exact):** `swap_from_three_cx` retains
  wire-order / Lean parse of both QASM artifacts under its declared scope.
- **Toffoli:** unnormalized `denotateOps3C` source = target remains out of scope.
  Normalized Clifford+T denotation is the honest closed instance, not a general
  Toffoli compiler theorem.
- **Clifford (H-H-S):** unnormalized `denotateOps1C` remains out of scope; the
  declared single-qubit normalized instance is closed; general n-qubit Clifford
  source→target remains future work.
- **Compiler flagship:** `qiskit_optimize_1q_gates_hxx_identity` is an
  Optimize1qGates H;X;X instance with provenance + Lean + QCEC supporting —
  [flagship](flagships/compiler_transformation_equivalence.md).

## Algorithms / dynamic circuits

- **Teleport (parent):** unitary-prefix proposition under declared scope;
  maturity `experimental_closed` after demotion. No fake full-protocol / matrix
  KERNEL_BRIDGE claim.
- **Teleport (sibling dynamic):** `teleportation_dynamic_feedforward_protocol`
  closes an arbitrary **pure-state** instrument + classical Pauli correction under
  measure/if denotation binding. Not mixed-state CPTP.
  [flagship](flagships/dynamic_teleportation.md).
- Device `hardware_semantics` / fidelity remain `not_checked`; ISA-layer
  abstraction may be checked separately when declared.

## QEC

Stim repetition spacetime members **d=3,5,7** (R=d). **`full_spacetime_mwpm`**
discharged only under declared universe
`stim_repetition_memory_odd_d_le_7_R_eq_d_p0p01`.
**`unbounded_all_codes_mwpm` permanently `not_applicable`**.
Bit-flip syndrome-extraction circuit semantics is checked on the layered
three-qubit package under its declared single-X model
([flagship](flagships/qec_bit_flip_chain.md)). Maturity after demotion is
`experimental_closed` (machine closure), not gold `reference_claim`.

Lean-QEC interoperability is **distance-only** (`BB90_dist_10`). Cold native
acceptance is not claimed until a structured passing result exists for the
candidate SHA ([release_audit_v1.md](release_audit_v1.md)).

## Hamiltonian

Former gold Hamiltonian packages are demoted. Unitary CB / Choi / Mathlib
Hermitian Schatten-1 / Pauli-channel diamond subclasses remain scoped theorems
under their declared carriers.
**`general_cb_arbitrary_cptp_mathlib` permanently `not_applicable`**.
Multi-step Trotter composition under declared N=5 entry-modulus triangle proxy
is not an operator-norm / unbounded-N result.
**Hamiltonian flagship:** Frobenius majorant for X,Z at t=π/4 —
[flagship](flagships/hamiltonian_product_formula.md) — not a general
Lie-Trotter operator-norm theorem.

## AI formalization

AI formalization packages that formerly claimed `reference_claim` with frozen
gold and dual hash-bound reviews are demoted. Retained review JSON may be labeled
`unauthenticated_legacy_review`; that is **not** review-attestation v2 and does
**not** authorize gold labels. Semantic adjudication corpus-wide remains open
(issue #16). See `benchmarks/ai_formalization/TRACK.md`.

## Adapters / polish

- `StabilizerTableau`: **`backendStatus = agPhasedShipping`**.
- **Lake OOM mitigation:** `QSpecBench.lean` does not import `Evidence.All`.
  Default `lake build QSpecBench` builds the library without the aggregate `#check`
  surface. Build evidence separately: `lake build QSpecBench.Evidence.All`.

---

## DoD research residuals

Permanent N/A items and scoped closures are listed below and in the DoD. Closing
a narrow obligation does **not** complete Level C or authorize community-grade
language.

| Item | Disposition |
|------|-------------|
| General CPTP completely-bounded norm | Permanent N/A (v3 narrowing); proved subclass only |
| Syndrome extraction circuit semantics | Checked on bit-flip layered package under declared model |
| AI formalization gold + authenticated dual reviews | **Not met** for v1 — demoted; aliases are not independent review |

## Optional research (not DoD-blocking unless claimed)

Named residuals for future work only: matrix KERNEL_BRIDGE for dynamic measure+if,
Grover `amplitude_lift`, general n-qubit Clifford source→target beyond H-H-S,
bytes→AST Lean parser, operator-norm / unbounded-N Trotter, measure-theoretic Haar
integral, surface-code MWPM beyond the declared finite universe, authentic
reviewer identities for any future gold promotion.

---

## Permanent N/A / out of scope

Do not treat these as “almost done” research. Document and keep fail-closed.

| Item | Disposition |
|------|-------------|
| `unbounded_all_codes_mwpm` | Keep `not_applicable` (open-ended code family) |
| Device `hardware_semantics` / `device_fidelity` / `pulse_schedule_semantics` | Remain `not_checked` until real device evidence |
| Unnormalized `denotateOps3C` Toffoli equality | Permanently out of scope; normalized / native-CCX is the honest claim |
| QBricks / ZX certificates | Adapters exist; not a complete FV standard; do not sole-promote on them |
| Rocq / Isabelle skip stubs | Never checked evidence |
| Full industrial Stim/Blossom for all codes | Outside declared universe — do not rename |
| Issue #9 external cold-host reproduction | Out of v1 scope / `post-v1` |

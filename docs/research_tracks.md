# Research tracks — honest status

Phase 8+ research progress without promoting benchmarks that lack evidence.
Definition-of-completion checklist: [definition_of_completion.md](definition_of_completion.md).
Live maturity counts: [status.md](status.md).

## Equivalence

- Kernel ABRC pilots prove **artifact denotation** (parse → Generated.ops → matrix),
  not full compiler equivalence for every pair.
- **Genuine source–target denotation (exact):** `swap_from_three_cx` has
  `bridge_swap_source_target_exact` / wire-order plus Lean parse of both QASM artifacts.
- **Toffoli:** unnormalized `denotateOps3C` source = target remains out of scope.
  **Closed under normalized Clifford+T denotation** with ABRC:
  `bridge_toffoli_decomposition_normalized_exact` /
  `toffoli_decomposition_equivalence` at `artifact_bound_reference_claim`
  (LSB; φ=0; elaborator + BridgeMetadata + dual reviews).
- `native_ccx_artifact_denotes_toffoli_unitary` remains the honest ABRC claim for native CCX.
- **Clifford (H-H-S):** unnormalized `denotateOps1C` source = target is out of scope
  (scale factor 2). **Closed under normalized denotation** with ABRC:
  `bridge_clifford_source_target_normalized_exact` /
  `clifford_simplification_preserves_unitary` at `artifact_bound_reference_claim`
  for the declared single-qubit H-H-S -> S instance; a general n-qubit Clifford
  source-target kernel proof beyond this declared instance remains future work.

## Algorithms / dynamic circuits

- **Teleport (parent):** Headline ABRC remains **proposition v2** unitary-prefix at
  **`artifact_bound_reference_claim`**. No fake full-protocol / matrix KERNEL_BRIDGE ABRC.
- **Teleport (sibling dynamic ABRC):** `teleportation_dynamic_feedforward_protocol`
  at **`artifact_bound_reference_claim`** under
  `claimed_link = kernel_checked_dynamic_denotation` (promoted from the weaker
  `kernel_checked_dynamic_ast_semantics` framing via a dedicated dual review evaluating the
  denotation binding — measure/if AST nodes bound to `Measurement.writeZOutcome` /
  `ClassicalReg`, never gate-matrix codegen).
  Profile: measure/if/else/nested/for/while[N]/reset; checked
  **`hardware_abstraction_isa_layer`** (software CanonicalAst ISA + fail-closed offline
  profile adapter). **`hardware_semantics` / device fidelity remain `not_checked`**.
  Sibling artifact remains measure+if; ABRC claim_scope invariants unchanged.

## QEC

Stim repetition spacetime members **d=3,5,7** (R=d). **`full_spacetime_mwpm`**
discharged only under declared universe
`stim_repetition_memory_odd_d_le_7_R_eq_d_p0p01`.
**`unbounded_all_codes_mwpm` permanently `not_applicable`** (open-ended code family;
Lean impossibility note). Bit-flip
`syndrome_extraction_circuit_semantics` is **checked** (OpenQASM ancilla syndrome
denotation ≡ lookup decoder path under declared single-X model). Maturity
`reference_claim` (no headline overclaim).

## Hamiltonian

Maturity **`reference_claim`**. Unitary CB / Choi Schatten-1 / Mathlib Hermitian
Schatten-1 definition / replacement diamond=2. **Qubit Pauli-channel class** diamond
`∑|Δp_σ|` with extremes + depolarizing closed forms (specializes to true CB on
Ad_X vs Ad_I); orthogonal pure Choi diamond=2. Beyond-Pauli **Kraus / unital /
amplitude-damping** carriers with replacement diag-nuclear=2
(`qubit_cptp_cb_proved_subclass_mathlib`).
**`general_cb_arbitrary_cptp_mathlib` permanently `not_applicable`** (claim-identity
**v3** narrowing — Mathlib has no arbitrary-CPTP CB API; not a silent Pauli-only
rename). **Multi-step Trotter composition** discharged under declared step count
N=5 and the entry-modulus triangle proxy (`multi_step_trotter_composition_discharged`);
not an operator-norm / unbounded-N result. **Haar Monte-Carlo integral** discharged
under a hashed numerical certificate (256 Haar samples, seed 20260725, hash-bound
output) agreeing with the Nielsen closed form within declared tolerance, plus a
Lean-declared contract-parameter anchor; not a measure-theoretic proof of the
integral. Both remain scoped side obligations on
`single_trotter_step_declares_error_contract`, not headline claims.

## AI formalization

Four of seven `ai_formalization` benchmarks are `reference_claim`, each with its own
frozen gold target and dual hash-bound reviews (`reviews/formal_review.json`,
`reviews/domain_review.json`): `formalize_bit_flip_code_corrects_one_x`,
`formalize_small_hamiltonian_hermiticity_statement`,
`formalize_stabilizer_commutation_statement`, and
`extract_teleportation_correctness_statement`. The remaining three
(`formalize_no_cloning_statement` at `reference_scaffold`;
`formalize_qec_distance_claim_statement` and `formalize_teleportation_spec_statement`
at `usable`) stay below `reference_claim` until each gets its own gold freeze and dual
review — see `benchmarks/ai_formalization/TRACK.md` and
`benchmarks/ai_formalization/notes/dual_review_blocker.md`.

## Adapters / polish

- `StabilizerTableau`: **`backendStatus = agPhasedShipping`**.
- **Lake OOM mitigation:** `QSpecBench.lean` no longer imports `Evidence.All`.
  Default `lake build QSpecBench` builds the library without the aggregate `#check`
  surface. Build evidence separately: `lake build QSpecBench.Evidence.All`.
- `Evidence.All` anchors Pauli-channel CB class, unbounded-MWPM impossibility,
  ISA hardware abstraction, Stim d≤7 universe, and prior surfaces.

---

## DoD research (R1–R3) — closed

These were the required scientific leftovers for community-grade DoD research boxes.
They are no longer open blockers.

| Item | Obligation / artifact | Exit |
|------|----------------------|------|
| General CPTP completely-bounded norm | `general_cb_arbitrary_cptp_mathlib` | **Permanent N/A (v3 narrowing):** proved subclass `qubit_cptp_cb_proved_subclass_mathlib`; Mathlib has no arbitrary-CPTP CB API |
| Syndrome extraction circuit semantics | `syndrome_extraction_circuit_semantics` on bit-flip QEC | **Checked** on `three_qubit_bit_flip_code_corrects_one_x` (`unproved_obligations: []`) |
| AI formalization gold + dual reviews | `formalize_bit_flip_code_corrects_one_x` | **Met** — four AI `reference_claim` benchmarks with frozen gold + dual hash-bound reviews; remaining three stay `reference_scaffold`/`usable` |

## Optional research (not DoD-blocking unless claimed)

Named residuals for future work only: matrix KERNEL_BRIDGE for dynamic measure+if,
Grover `amplitude_lift`, general n-qubit Clifford source→target kernel proof beyond the
declared H-H-S instance, bytes→AST Lean parser,
operator-norm / unbounded-N multi-step Trotter composition (declared N=5
entry-modulus composition is discharged; the operator-norm / diamond-distance and
unbounded step-count generalizations remain open), full measure-theoretic Haar
integral (declared hashed numerical certificate is discharged; a Lean/measure-theoretic
proof of the integral itself remains open), surface-code MWPM beyond the declared
finite universe, gold-target freezes + dual reviews for the three remaining
`ai_formalization` benchmarks (`formalize_no_cloning_statement`,
`formalize_qec_distance_claim_statement`, `formalize_teleportation_spec_statement`).

---

## Permanent N/A / out of scope

Do not treat these as “almost done” research. Document and keep fail-closed.
**Community-grade DoD does not require closing any of these** — see
[definition_of_completion.md](definition_of_completion.md) and the README
permanent-residuals section.

| Item | Disposition |
|------|-------------|
| `unbounded_all_codes_mwpm` | Keep `not_applicable` (open-ended code family). Lean impossibility: `unbounded_all_codes_mwpm_infeasible_open_ended` in `lean/QSpecBench/QEC/SyndromeExtraction.lean` |
| Device `hardware_semantics` / `device_fidelity` / `pulse_schedule_semantics` | Remain `not_checked` until real device evidence. ISA-layer `hardware_abstraction_isa_layer` stays a separate checked obligation |
| Unnormalized `denotateOps3C` Toffoli equality | Permanently out of scope (wrong semantics); normalized / native-CCX ABRC is the honest claim |
| QBricks / ZX certificates | Adapters exist; still not a complete FV standard — do not sole-ABRC on them |
| Rocq / Isabelle skip stubs | Never checked evidence; excluded from default maturity counts |
| Full industrial Stim/Blossom for all codes | Outside declared universe `stim_repetition_memory_odd_d_le_7_R_eq_d_p0p01` — do not rename |

# Research and infrastructure roadmap

QSpecBench separates **infrastructure** (schema, validators, honest labels) from **scientific
results** (full protocol proofs). The dashboard counts each honestly.

## Infrastructure (tooling milestones)

- [x] Wire artifact JSON through schema validation in `qspecbench validate` (B5)
- [x] Bridge taxonomy: `manifest_checked_theorem_binding` vs `python_denotation_consistency` (P0)
- [x] Structured Lean evidence anchors for manifest bridges (P0)
- [x] Fail-closed QASM extraction with `qasm_extraction` policy (P0)
- [x] QEC granular `qec_claim_scope` + unknown label hard-fail (P0)
- [x] Expand `bridge_theorem_manifest.json` to 11 manifest-checked pairs
- [x] Align Lean `ComplexGate` with Python for S/T; complex-scaffold manifest bridges
- [x] QEC `single_pauli_error_correction_validator` brute-force logical preservation
- [x] OpenQASM `rz`/`ry`/`cz`/`u`/`cp` in Python matrix extractor
- [x] Release bundle CLI (`qspecbench release-bundle`)
- [x] Provenance SHA256 drift fails validation in CI
- [x] Stale `claim_diff.md` detection in `qspecbench validate`
- [x] Dual review gate for `reference_claim` promotions
- [x] README status block auto-sync from dashboard metrics
- [x] QEC logical-preservation validator wired as structured evidence
- [x] Hamiltonian artifact `type` migration complete (legacy skip removed)
- [ ] Second proof assistant in CI (Coq/Rocq/Isabelle beyond stubs) — **P2 partial** (adapter smoke tests + evidence type wiring; local `tests/test_coq_adapter.py`; CI path documented below)
- [x] Bridge codegen pilot (`ast_sha256` + `generated_lean_sha256` for CNOT) — **P2 partial** (see [bridge_codegen_design.md](bridge_codegen_design.md))
- [x] Bridge codegen expanded to `hadamard_conjugates_x_to_z` and `single_qubit_gate_cancellation` (codegen-trace hash chain)
- [x] First kernel-checked codegen-trace bridge — **P2 done** (`cnot_self_inverse_cancellation`; `kernel_checked_codegen_trace` + `bridge_cnot_codegen_self_inverse`)
- [x] Second and third kernel-checked codegen-trace bridges — **P2 done** (`hadamard_conjugates_x_to_z`, `single_qubit_gate_cancellation`; codegen trace + kernel proofs)
- [x] Fourth kernel-checked codegen-trace bridge — **P4 done** (`bell_state_preparation`; codegen trace + `bridge_bell_codegen_prep`)
- [ ] Full OpenQASM-to-Lean codegen pipeline — **P2 in progress** (5 benchmarks with AST/codegen hashes; RX manifest-bound; Lean parser stub designed)
- [x] `full_dynamic_semantics` QASM mode — **P3 partial** (projective POVM stub + `dynamic_circuit` semantics_base; teleportation pilot; classical-control metadata)
- [x] Compiler dual-manifest target hashes — **P3 partial** (`clifford_simplification_preserves_unitary` target-side codegen)
- [x] External QEC certificate semantic validation — **P3 partial** (`qec_external.py` + provenance linkage)
- [ ] Teleportation / Grover / no-cloning headline proofs — **research** (Section D; Grover `amplitude_lift` blocked on measurement semantics)

### Manifest bridge status (2026-06-27)

Eleven `manifest_checked_theorem_binding` bridges (integer + complex scaffolds). Three
`python_denotation_consistency` bridges. Five **kernel-checked codegen-trace** bridges
(`kernel_checked_codegen_trace`; legacy enum `kernel_checked_artifact_semantics` where still emitted):
`cnot_self_inverse_cancellation`, `hadamard_conjugates_x_to_z`, `single_qubit_gate_cancellation`,
`bell_state_preparation`, `swap_from_three_cx`.
RX manifest-bound at complex denotation (global phase vs H not claimed; Lean lemma documents gap).

**Blocked from manifest binding:**

| Benchmark | Reason |
|-----------|--------|
| `rx_gate_equivalence_small_instance` | Manifest-bound for `bridge_rx_pi2_denotation`; headline still excludes global-phase equivalence to H |

### full_dynamic_semantics requirements (P3)

Before `qasm_extraction.mode=full_dynamic_semantics` is accepted by validators:

1. **Measurement semantics** — projective (or declared POVM) update rules with classical outcomes
2. **Classical control** — `if (c) x q[i];` and feed-forward wiring in QASM AST
3. **Reset / initialize** — non-unitary state preparation in the extraction pipeline
4. **Codegen + Lean** — dynamic `QasmOp` constructors and proof obligations for each supported construct
5. **Benchmark coverage** — at least one `reference_scaffold` with checked fragment + documented dynamic gap

Until then, validators fail closed unless `semantics_base=dynamic_circuit` and
`allowed_to_skip` includes `measurement` (default remains `unitary_fragment`).

## Phase 4 status (2026-06-27)

| Goal | Status |
|------|--------|
| Kernel-checked codegen-trace expansion (H-X-H, H-H, Bell, swap) | **Done** — 5 codegen-trace bridges |
| Bell state codegen-trace bridge | **Done** — 4th codegen-trace bridge (`bell_state_preparation`) |
| Python→AST trust boundary docs | **Done** — `bridge_codegen_design.md` |
| `full_dynamic_semantics` foundation | **Partial** — projective stub + classical metadata + validate rules |
| RX global phase | **Documented** — `rx_pi2_entry01_ne_hadamard_entry01`; headline narrowed |
| QEC external certificate validate | **Partial** — schema + semantic checks in `qec_external.py` |
| Compiler dual-manifest | **Partial** — Clifford target hashes wired |
| Second proof assistant | **Partial** — stub adapters + expanded smoke tests |
| Section D research milestone | **Partial** — teleportation dynamic pilot; Grover amplitude_lift documented blocked |
| Docs / dashboard | **Done** — roadmap + regenerated `status.md` |

## Phase 5 status (2026-06-27)

| Goal | Status |
|------|--------|
| Bell state codegen-trace bridge | **Done** — 4th `kernel_checked_codegen_trace` |
| Stale dynamic simulation evidence | **Done** — `validate_dynamic_simulation_evidence` |
| Operational dynamic simulator | **Partial** — `dynamic_simulator.py` statevector + branch enumeration |
| Teleportation basis check | **Done** — operational wire model; `all_ok` true for basis inputs |
| Lean QASM parser stub | **Partial** — `OpenQASM3Parser.lean` line stub |
| QEC external witness validation | **Partial** — witness cross-checks in `qec_external.py` |
| CLI `dynamic-simulate` | **Done** |
| Operational semantics doc | **Done** — `docs/operational_semantics.md` |
| Protocol `reference_claim` | **Blocked** — kernel-checked dynamic semantics required |

### Phase 5 blockers

1. ~~Normalized gate model alignment for dynamic simulation vs OpenQASM int scaffold~~ — **Partial** (normalized operational path + int diagnostic)
2. Lean byte-level QASM parser kernel
3. Feed-forward corrections in teleportation artifacts
4. Kernel-checked measurement update rules in Lean
5. Compiler source→target equivalence proofs (Clifford)
6. Second proof assistant kernel in CI

## Phase 6 status (2026-06-28)

| Goal | Status |
|------|--------|
| Teleportation basis check root-cause | **Done** — legacy Kronecker vs OpenQASM wire mismatch in dynamic sim; operational model fixed |
| Teleportation `all_ok` (operational) | **Done** — documented Z-then-X correction table passes branch enumeration |
| Feed-forward supplementary artifact | **Done** — `teleportation_with_feedforward.qasm` |
| Lean parser line stub | **Done** — five kernel bridges + `parseLines_*_eq_generated_ops` + Python cross-test |
| Lean measurement scaffold | **Done** — Fin 4 Z / Z⊗Z projective checks in `Measurement.lean` |
| CI dynamic simulation | **Done** — `test_phase5.py` + `dynamic-simulate --teleport-basis-check` in validate workflow |
| Fifth kernel bridge | **Skipped** — swap/toffoli proof chains not low-risk for this pass |
| Grover / Hamiltonian housekeeping | **Done** — `amplitude_lift` blocked note; hamiltonian artifacts already typed v0.2.0 |

### Phase 6 remaining blockers

1. Lean byte-level QASM parser kernel (bytes→AST still Python-side)
2. Kernel-checked projective measurement update in Lean
3. Teleportation `reference_claim` (arbitrary-state relational transfer)
4. Int-scaffold / operational wire model alignment for verify-bridge (documented gap)
5. Compiler source→target equivalence proofs (Clifford)
6. Second proof assistant kernel in CI

## Phase 7 status (2026-06-28)

| Goal | Status |
|------|--------|
| Lean parser parse→toQasmOp theorems | **Done** — all five kernel bridge parseLines theorems + Python cross-test |
| Measurement scaffold | **Done** — Fin 4 statevector Z / Z⊗Z checks; teleportation evidence anchor |
| Int-scaffold vs operational gap | **Documented** — Kronecker table + diagnostic test in `test_phase5.py` |
| Feed-forward supplementary artifact | **Done** — spec object + `--feedforward` CLI path |
| Fifth kernel bridge (`swap_from_three_cx`) | **Done** — codegen hash chain + `bridge_swap_from_three_cx_codegen` |
| Grover / Clifford housekeeping | **Done** — amplitude_lift cross-ref to Measurement.lean; Clifford proof checklist |
| Second proof assistant | **Partial** — `QSPECBENCH_COQ=1` optional `coqc` path + smoke tests |

### Phase 7 blockers

1. Lean byte-level QASM parser kernel (bytes→AST still Python-side)
2. Kernel-checked projective measurement on arbitrary amplitudes (Fin 4 basis states done)
3. Teleportation `reference_claim` (arbitrary-state relational transfer)
4. Full int-scaffold / operational alignment for verify-bridge on multi-qubit circuits
5. Fifth kernel bridge — **Done** (`swap_from_three_cx` codegen hash wiring + manifest promotion)
6. Compiler source→target equivalence proofs (Clifford checklist open)

### Second proof assistant CI path (no yaml change in this pass)

1. Add `coqc` / `rocq` to optional CI matrix job (feature flag `QSPECBENCH_COQ=1`)
2. Run `python -m pytest tests/test_coq_adapter.py` (already in validate workflow)
3. Wire `coq_proof` evidence through `evidence_runner` when adapter returns `ok`
4. Require kernel-checked certificate before `reference_claim` promotion

## P1 deferred (post-P0)

| Item | Notes |
|------|-------|
| Kernel-checked codegen-trace bridges | **Done** — 5 bridges (CNOT, H-X-H, H-H, Bell prep, swap) |
| Teleportation `reference_claim` | Full protocol + measurement feed-forward semantics |
| QEC correction `reference_claim` | **Done (narrow)** — `three_qubit_bit_flip_code_corrects_one_x` lookup-table scope |
| Distance proofs | **Partial** — bruteforce `distance_result` wired for `distance_certificate_small_css_code` |
| Hamiltonian corpus v0.2.0 | Migrate remaining untyped `hamiltonian.json` artifacts |
| README status auto-sync | Extend `scripts/sync_readme_maturity.py` to pull dashboard summary block |
| RX(π/2) vs H | Manifest-bound `bridge_rx_pi2_denotation`; Lean `rx_pi2_entry01_ne_hadamard_entry01`; global phase not claimed |

## Research (corpus milestones — not validator tasks)

These require new mathematics or substantial formalization effort:

| Claim area | Example benchmark | What a real proof requires |
|------------|-------------------|----------------------------|
| Teleportation protocol | `teleportation_preserves_state_up_to_pauli_correction` | Measurement, classical feed-forward, arbitrary-state relational semantics |
| QEC correction | `three_qubit_bit_flip_code_corrects_one_x` | Decoder correctness + logical preservation, not lookup-table assumption |
| Algorithm correctness | Grover, Deutsch–Jozsa, phase estimation | Full algorithm specs, not scaffold nontriviality |
| No-cloning | `no_cloning_negative_claim` | Arbitrary states and linear maps, not permutation-matrix scaffold |
| Hamiltonian analytics | Trotter contracts | Analytic error bounds, not declared positive constants |
| Distance | `distance_certificate_small_css_code` | Actual minimum weight, not SMT toy `d ≥ 3` |

Promoting any of these to `reference_claim` before the proof exists would violate the project's core
honesty rule.

## Phase 8 status (2026-06-28)

| Goal | Status |
|------|--------|
| Fifth codegen-trace bridge (`swap_from_three_cx`) | **Done** — codegen hash chain + `bridge_swap_from_three_cx_codegen` (`kernel_checked_codegen_trace`) |
| Lean `parseLines` + gate-list theorems | **Done** — computable `parseLineQasmOp`; `parseLines_bell_*` + `parseLines_swap_*`; Python cross-test on 5 kernel QASM artifacts |
| Measurement scaffold (2-qubit) | **Partial** — `TwoQubitZOutcome`, sequential syndrome stub; no Fin (2^n) amplitude update |
| Int-scaffold wire-index gap | **Documented** — `docs/operational_semantics.md` + `test_int_scaffold_vs_operational_h_on_q0_three_qubits` |
| Feed-forward teleportation tests | **Done** — `test_teleportation_feedforward_artifact_basis_check` + supplementary artifact |
| Toffoli / circuit_identity kernel bridge | **Skipped** — `ast_sha256` null in manifest; CCX denotation chain not low-risk |
| Clifford source→target kernel proof | **Blocked** — dual-manifest hashes present; `source_target_equivalence_open.lean` checklist open |
| Coq second-assistant CI | **Partial** — `test_coq_adapter.py` + `QSPECBENCH_COQ=1` documented; no coqc in default matrix |

### Phase 8 blockers (unchanged)

1. Lean byte-level QASM parser kernel (bytes→AST still Python-side)
2. Kernel-checked projective measurement update on state vectors in Lean
3. Teleportation `reference_claim` (arbitrary-state relational transfer)
4. Toffoli / layout-identity codegen kernel chains (`ast_sha256` null)
5. Compiler source→target equivalence proofs (Clifford)
6. Second proof assistant kernel in default CI

## Phase 9 status (2026-06-28)

| Goal | Status |
|------|--------|
| Lean `canonicalAstFromLines` mirroring Python JSON AST | **Done** — six kernel QASM gate lines + Python cross-test |
| Sixth kernel-checked codegen-trace bridge (Toffoli CCX source) | **Done** — `bridge_toffoli_codegen_ccx` + manifest hashes |
| Fin 8 basis-state measurement scaffold | **Partial** — Z-outcome checks; no amplitude update |
| Teleportation basis-state Lean anchors | **Partial** — `measurement_scaffold.lean` Fin 8 examples |
| Release bundle SBOM-lite + verify integration | **Done** |
| QEC witness syndrome hash export | **Done** — `qec_witness.py` |
| Coq optional CI job | **Done** — repo var `QSPECBENCH_COQ=1` |
| Toffoli decomposition / circuit_identity full kernel | **Blocked** — target H/T/CX trace; layout proof open |

### Phase 9 blockers

1. Lean byte-level QASM parser kernel (bytes→AST still Python-side)
2. Kernel-checked projective measurement on arbitrary amplitudes
3. Teleportation `reference_claim` (arbitrary-state relational transfer)
4. Decomposed Toffoli target circuit codegen (rotations outside stub subset)
5. Compiler source→target equivalence proofs (Clifford)
6. Wire-order alignment proof (`wire_order_bridge_theorem` reserved)

## Phase 10 priorities (2026-06-28)

| Goal | Status |
|------|--------|
| Bytes→AST Lean parser kernel | **Blocked** |
| Arbitrary-amplitude projective measurement in Lean | **Blocked** |
| Teleportation / Grover `reference_claim` | **Blocked** |
| Clifford source→target kernel proof | **Blocked** |
| Second proof assistant in default CI | **Partial** — optional Coq job only |
| Pinned dependency lockfiles in release SBOM | **Partial** — SBOM-lite lists declared deps |

### Phase 10 blockers

1. No pinned Python lockfile in repo — SBOM lists `pyproject.toml` deps only
2. External tool versions (QCEC) not embedded in release bundle
3. Int-scaffold vs operational wire model proof gap
4. QEC decoder correctness beyond lookup-table scope
5. Analytic Hamiltonian simulation bounds (Trotter contracts)

## P1 deferred (post-P0)

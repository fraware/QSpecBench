# Semantic faithfulness rubric

Source: `artifacts/source.txt`

Target system: Lean 4 (`QSpecBench.Teleportation`)

## Score: 4

The kernel-checked theorem pair `teleport_measure_correct_ket0` / `teleport_measure_correct_ket1`
faithfully captures the source claim that quantum teleportation transfers an unknown qubit state to
a remote party up to Pauli corrections, for the declared computational-basis inputs zero and one,
quantified over all four possible Alice measurement outcomes. General-state transfer for an
arbitrary superposition is explicitly rejected as outside this gold target; that broader claim is
covered by the sibling full-protocol benchmark `teleportation_preserves_state_up_to_pauli_correction`.

## Reviewer role

QSpecBench Layer 3 reviewer (AI formalization track)

## Assumptions

- Declared computational-basis inputs (zero, one) embedded on the fixed 3-qubit wire ordering
- Measure-then-correct recovery quantified over all four Alice syndrome outcomes (c0, c1)
- Library theorems are the adjudicated gold; AI draft text remains untrusted
- Arbitrary-superposition transfer is out of gold scope for this AI formalization pilot

## Rubric checklist

- [x] Source claim identified correctly
- [x] Transfer relation formalized for both computational-basis inputs
- [x] Measurement and Pauli-correction semantics explicit (all four syndromes)
- [x] Statement matches source under documented conventions
- [x] Library-compatible statement shape
- [x] Nearby weaker statements (Bell-pair nontriviality only) rejected
- [ ] General-state (arbitrary superposition) transfer — explicitly out of gold scope

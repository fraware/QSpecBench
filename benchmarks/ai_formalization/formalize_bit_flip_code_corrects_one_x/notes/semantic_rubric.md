# Semantic faithfulness rubric

Source: `artifacts/source.txt`

Target system: Lean 4 (`QSpecBench.Stabilizer`)

## Score: 4

The kernel-checked theorem `bit_flip_stabilizers_commute` matches the three-qubit bit-flip stabilizer commutation claim in the source text.

## Reviewer role

QSpecBench Layer 3 reviewer (AI formalization track)

## Assumptions

- Z-type stabilizers on adjacent qubit pairs
- Commutation defined on Pauli support overlap

## Rubric checklist

- [x] Source claim identified correctly
- [x] Stabilizer generators named
- [x] Commutation claim explicit
- [x] Statement matches source under documented conventions
- [x] Library-compatible statement shape

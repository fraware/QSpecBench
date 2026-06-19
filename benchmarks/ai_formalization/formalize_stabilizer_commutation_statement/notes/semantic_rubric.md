# Semantic faithfulness rubric

Source: `artifacts/source.txt`

Target system: Lean 4 (`QSpecBench.Stabilizer`)

## Score: 4

The kernel-checked theorem `steane_stabilizers_commute` captures stabilizer commutation for the Steane scaffold under documented Pauli conventions.

## Reviewer role

QSpecBench Layer 3 reviewer (AI formalization track)

## Assumptions

- Pauli stabilizer generators act on disjoint support or commute by construction
- Steane [[7,1,3]] generator pairing matches source text

## Rubric checklist

- [x] Source claim identified correctly
- [x] Stabilizer commutation predicate stated
- [x] Generator set matches Steane scaffold
- [x] Statement matches source under documented conventions
- [x] Library-compatible statement shape

# Semantic faithfulness rubric

Source: `artifacts/source.txt`

Target system: Lean 4 (`QSpecBench.NoCloning`)

## Score: 4

The kernel-checked library theorem `no_cloning_basis_states` encodes the standard obstruction for basis-state cloners under linear extension to the |+⟩ input. Linearity and ancilla |0⟩ assumptions are explicit in the evidence notes.

## Reviewer role

QSpecBench Layer 3 reviewer (AI formalization track)

## Rubric checklist

- [x] Source claim identified correctly
- [x] Cloning map model stated
- [x] Linearity/unitarity assumptions explicit
- [x] Statement matches source under documented conventions
- [x] Library-compatible statement shape

## Assumptions

- source claim identified correctly
- cloning map model stated
- linearity and unitarity assumptions explicit
- universal cloner scaffold uses computational basis + |+⟩ linearity obstruction

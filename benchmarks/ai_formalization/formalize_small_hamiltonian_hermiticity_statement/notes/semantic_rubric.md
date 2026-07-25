# Semantic faithfulness rubric

Source: `artifacts/source.txt`

Target system: Lean 4 (`QSpecBench.Hamiltonian`)

## Score: 4

The kernel-checked theorem `small_fermionic_hamiltonian_is_hermitian` faithfully captures the source
claim that a small Pauli-decomposed Hamiltonian with real coefficients represents a Hermitian
operator, under the declared 2-qubit Pauli-term artifact (Z, X, Y generators with real
coefficients). Nearby general-size or complex-coefficient Hamiltonian statements are rejected as
outside this gold target.

## Reviewer role

QSpecBench Layer 3 reviewer (AI formalization track)

## Assumptions

- Declared 2-qubit Pauli-term decomposition with real coefficients (Z, X, Y generators)
- Hermiticity checked via conjugate-transpose equality on the declared matrix (`conjTranspose`)
- General-size or complex-coefficient Hamiltonians remain out of gold scope
- Library theorem is the adjudicated gold; AI draft text remains untrusted

## Rubric checklist

- [x] Source claim identified correctly
- [x] Operator model stated (Pauli decomposition)
- [x] Hermiticity definition explicit
- [x] Statement matches source under documented conventions
- [x] Library-compatible statement shape
- [x] Nearby weaker statements (general-size Hermiticity) rejected

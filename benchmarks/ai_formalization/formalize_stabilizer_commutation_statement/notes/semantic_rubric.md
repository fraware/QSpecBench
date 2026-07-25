# Semantic faithfulness rubric

Source: `artifacts/source.txt`

Target system: Lean 4 (`QSpecBench.Stabilizer`)

## Score: 4

The kernel-checked theorem `steane_stabilizers_commute` faithfully captures the source claim for the
declared six-generator Steane Z-chain scaffold's five adjacent generator pairs
(`steaneZ01`/`steaneZ12`, `steaneZ12`/`steaneZ23`, `steaneZ23`/`steaneZ34`, `steaneZ34`/`steaneZ45`,
`steaneZ45`/`steaneZ56`) under the `pauliCommutes7` disjoint-support predicate. The broader source
claim — all-pairs pairwise commutation for a general stabilizer code, including non-adjacent Steane
pairs — is explicitly rejected as outside this gold target.

## Reviewer role

QSpecBench Layer 3 reviewer (AI formalization track)

## Assumptions

- Declared six-generator Steane Z-chain scaffold (steaneZ01..steaneZ56) on 7 qubits
- Pauli stabilizer generators commute via the `pauliCommutes7` disjoint-support predicate
- Only 5 adjacent chain pairs are checked; non-adjacent pairs and the full Steane [[7,1,3]] generator
  set (including X-type generators) remain outside gold scope

## Rubric checklist

- [x] Source claim identified correctly
- [x] Stabilizer commutation predicate stated
- [x] Generator set matches Steane Z-chain scaffold
- [x] Statement matches source under documented conventions
- [x] Library-compatible statement shape
- [x] Nearby broader statements (all-pairs / non-adjacent / full generator set) rejected

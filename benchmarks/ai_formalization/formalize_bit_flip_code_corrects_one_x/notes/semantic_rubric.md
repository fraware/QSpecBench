# Semantic faithfulness rubric

Source: `artifacts/source.txt`

Target system: Lean 4 (`QSpecBench.QEC.BitFlip`)

## Score: 4

The kernel-checked theorem `bit_flip_lookup_decoder_correct` faithfully captures the source claim that the three-qubit bit-flip code detects and corrects a single X error, under the declared lookup-table decoder and single-X Pauli error model. Nearby stabilizer-commutation-only statements are rejected as incomplete for this gold target.

## Reviewer role

QSpecBench Layer 3 reviewer (AI formalization track)

## Assumptions

- Declared single-X Pauli error model on three data qubits (exactly one of XII, IXI, IIX)
- Syndrome bits from anticommutation with ZZI / IZZ generators; lookup correction restores identity
- Syndrome-extraction circuit semantics and general decoder algorithms remain out of gold scope
- Library theorem is the adjudicated gold; AI draft text remains untrusted

## Rubric checklist

- [x] Source claim identified correctly
- [x] Single-X correction claim explicit
- [x] Lookup-table decoder model stated
- [x] Statement matches source under documented conventions
- [x] Library-compatible statement shape
- [x] Nearby weaker statements (stabilizer commutation only) rejected

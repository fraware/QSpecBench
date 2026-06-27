# Bit-flip code

Informal QEC notes for the three-qubit bit-flip code.

## Stabilizers and syndrome convention

Qubit order: `q0, q1, q2`.

- `S0 = Z0 Z1` (pauli `ZZI`), measured into syndrome bit `s0`.
- `S1 = Z1 Z2` (pauli `IZZ`), measured into syndrome bit `s1`.

A single `X` error on qubit `i` anticommutes with stabilizer `Sj` (flipping `sj`)
iff `Sj` carries a `Z` on qubit `i`. Writing the syndrome string as `s0 s1`:

| Error | s0 (from Z0Z1) | s1 (from Z1Z2) | Syndrome | Correction |
|-------|----------------|----------------|----------|------------|
| I     | 0              | 0              | 00       | III        |
| X0    | 1              | 0              | 10       | XII        |
| X1    | 1              | 1              | 11       | IXI        |
| X2    | 0              | 1              | 01       | IIX        |

Note that `X1` triggers both stabilizers (syndrome `11`) and `X2` triggers only
`S1` (syndrome `01`). An earlier revision of the table swapped these two entries;
they now follow the natural stabilizer order `ZZI, IZZ` above.

## Distance

The declared distance `d = 3` is the **bit-flip distance** (`X`-only). The code
provides no protection against `Z`/phase errors, so its **quantum distance is 1**.
See `artifacts/code.json` (`parameters.bit_flip_distance`, `parameters.quantum_distance`)
for the explicit distance-type fields.

## Trust boundary

Decoder/lookup-table correctness is assumed, not kernel-checked. The Lean evidence
covers stabilizer commutation only; the full correction claim for all single `X`
errors is not yet machine-checked.

# Syndrome table (three-qubit bit-flip code)

| Syndrome (Z0Z1, Z1Z2) | Error   | Correction |
|-----------------------|---------|------------|
| (+, +)                | I       | I          |
| (-, +)                | X on q0 | X on q0    |
| (+, -)                | X on q2 | X on q2    |
| (-, -)                | X on q1 | X on q1    |

Stabilizer generators: Z0Z1, Z1Z2. Decoder lookup is **assumed**, not kernel-checked.

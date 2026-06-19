# No-cloning theorem (negative claim)

## Claim

No unitary quantum process can copy an arbitrary unknown pure qubit state to two outputs.

## Why this matters

Canonical **negative** benchmark: the claim is impossibility, not circuit equivalence. Tests whether tooling respects negative specifications and does not over-claim proof status.

## Objects

- `notes/cloning_channel.md` — schematic channel specification (not an implementation)

## Specification

Mode `negative`. Semantic object: impossibility of a universal cloner on pure states.

## Evidence

- Informal proof sketch in `notes/informal_derivation.md` (partial human review)
- Acceptable future evidence: **Lean 4 kernel proof** (not yet present — theorem requires substantial formalization)

## Trust boundary

No kernel-checked proof. Informal sketch is not proof. No benchmark status claims verification.

## Status

Current maturity: **reference**.

## Known gaps

- Lean 4 formalization of no-cloning in repository proof library
- No executable circuit artifact (claim is impossibility, not a program)

## References

- Standard no-cloning presentations in quantum information texts

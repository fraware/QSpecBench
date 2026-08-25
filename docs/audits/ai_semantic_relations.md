# AI formalization semantic-relation audit

Status: active audit under issue #16. This document records evidence-supported findings; it does not silently rewrite benchmark maturity.

## Required relation taxonomy

Every AI source→gold pair should be adjudicated as one of:
- `equivalent`
- `strict_weakening`
- `strict_strengthening`
- `instance`
- `incomparable`
- `ambiguous`

Kernel elaboration/proof completion and semantic relation are separate axes.

## Confirmed finding: `extract_teleportation_correctness_statement`

Source artifact:

> Quantum teleportation transfers an unknown qubit state to a remote party up to Pauli corrections.

The current frozen gold target is explicitly the pair of checked computational-basis theorems for input zero and input one, over the four Alice measurement outcomes. The benchmark itself states that arbitrary-superposition/general-state transfer is outside the gold target.

Therefore the relation from the original source artifact to the accepted gold theorem pair is **`strict_weakening`** (or, viewed theorem-by-theorem, finite instances of the universal source claim), not semantic equivalence to the original unknown-qubit proposition.

The current benchmark headline has already been narrowed to disclose this basis-state restriction. That disclosure is good scope discipline, but it does not turn the gold pair into an equivalent formalization of the original source sentence. The existing `faithfulness_score: 4` / `gold_target.kernel_status: checked_faithful` should be re-adjudicated under the new relation model.

The kernel evidence remains useful and valid for the two basis-state theorems. The audit finding concerns **construct validity / relation to source**, not Lean proof validity.

## Corpus-wide audit procedure

For every current AI promoted claim:
1. read the immutable source artifact, not only the narrowed benchmark headline;
2. identify quantifiers, domain, modality, approximation, assumptions and semantic objects in the source;
3. identify the exact accepted gold theorem(s);
4. classify source→gold relation;
5. separately record syntax/elaboration, theorem proof status, assumption capture, nearby-wrong rejection, and reviewer agreement;
6. if relation is not `equivalent`, prevent any semantic-equivalence faithfulness metric from passing merely because the theorem checks;
7. preserve the narrower theorem as valid evidence when it is scientifically useful.

No remaining AI benchmark is assigned a relation in this file without an artifact-by-artifact adjudication. Issue #16 remains open until all promoted AI examples have been reviewed under this procedure by authenticated independent adjudicators.

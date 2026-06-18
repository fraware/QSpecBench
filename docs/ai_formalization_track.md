# AI formalization track

## Purpose

Evaluate AI-assisted extraction and formalization of quantum claims.

## Requirements per benchmark

- Source text
- Target formal system
- Expected statement shape
- Semantic review rubric
- Trust boundary marking AI output untrusted

## Semantic faithfulness rubric

| Score | Meaning |
|-------|---------|
| 0 | Unrelated to source claim |
| 1 | Relevant terms but changed claim |
| 2 | Partial claim; key assumptions dropped |
| 3 | Main claim captured; convention mismatches |
| 4 | Faithful under documented assumptions |
| 5 | Faithful, reusable, library-compatible, semantically reviewed |

## Rules

- AI output labels: draft, syntactically valid, kernel checked, semantically reviewed, rejected
- Syntactic validity does not imply semantic faithfulness
- Kernel-checked theorems require separate faithfulness review

## Example

`formalize_no_cloning_statement` — AI draft with rubric score 2.

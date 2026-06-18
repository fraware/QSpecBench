# AI formalization track

## Purpose

Evaluate AI-assisted extraction and formalization of quantum claims.

## Requirements per benchmark

- `artifacts/source.txt` — informal claim text
- `artifacts/draft.lean` — AI-generated Lean draft (untrusted)
- `notes/semantic_rubric.md` — human semantic faithfulness rubric (score 0–5)
- `evidence/rubric_result.json` — machine-readable rubric output from the adapter

## Semantic faithfulness rubric

| Score | Meaning |
|-------|---------|
| 0 | Unrelated to source claim |
| 1 | Relevant terms but changed claim |
| 2 | Partial claim; key assumptions dropped |
| 3 | Main claim captured; convention mismatches |
| 4 | Faithful under documented assumptions |
| 5 | Faithful, reusable, library-compatible, semantically reviewed |

Required rubric fields (validated by `adapters/ai_formalization/parse_result.py`):

- `score` — integer 0–5
- `reviewer_role` — non-empty string
- `assumptions` — list of documented assumption strings

## Evidence ladder

| Stage | Evidence type | Status | Trust |
|-------|---------------|--------|-------|
| AI output | `ai_draft` | `draft` | untrusted |
| Rubric review | `human_review` | `partial` | externally_trusted reviewer |
| Lean parse (optional) | `ai_draft` label `syntactically_valid` | not kernel-checked | tool parse only |
| Kernel check | `lean_proof` | `passing` | checked (requires separate faithfulness review) |

Rules:

- `ai_draft` with `status: passing` is rejected by trust rules
- Syntactic validity (`lean --parse` on draft) does **not** imply semantic faithfulness
- Kernel-checked theorems require separate faithfulness review against `semantic_rubric.md`

## Runnable adapter

```bash
python adapters/ai_formalization/parse_result.py notes/semantic_rubric.md artifacts/draft.lean
```

Writes `evidence/rubric_result.json` and validates rubric structure. When `lean` is on `PATH`, performs parse-only syntax check on the draft (not kernel verification).

## Example

`formalize_no_cloning_statement` — AI draft with rubric score 2 and generated `evidence/rubric_result.json`.

# Adding a benchmark

## Step 1: Choose a track

Place the benchmark under `benchmarks/<track>/<claim_id>/` where `claim_id` is lowercase snake_case.

## Step 2: Copy a template

Copy `benchmarks/_template/` to `benchmarks/<track>/<claim_id>/`, rename fields so `id` matches the directory name, then follow the steps below.

```
benchmarks/<track>/<claim_id>/
  README.md
  spec.yaml
  artifacts/
  evidence/
  expected/
  notes/
```

## Step 3: Write the claim card

Follow the README template sections: Claim, Why this matters, Objects, Specification, Evidence, Trust boundary, Status, Known gaps, References.

## Step 4: Write spec.yaml

Validate against the schema. Ensure `id` matches the directory name.

## Step 5: Add artifacts

Put circuits, JSON codes, Hamiltonians, and source files in `artifacts/`. Declare paths in `objects`.

## Step 6: Declare evidence

List `acceptable_evidence` and current `evidence` with honest `status` and `trust_level`.

### Lean evidence (optional)

1. Add theorem module under `lean/QSpecBench/`
2. Add `evidence/<name>.lean` in the benchmark importing that module
3. Declare `lean_proof` in `acceptable_evidence` and `evidence` with checker `Lean 4 kernel`
4. Command: `python adapters/lean/parse_result.py evidence/<name>.lean`
5. Run `lake build` locally; CI builds Lean before validation

Do not mark `passing` until `lake build` succeeds without `sorry`.

## Step 7: Validate locally

```bash
pip install -e .
qspecbench validate benchmarks/<track>/<claim_id>/
```

## Step 8: Open a PR

Use the new benchmark issue template. Do not claim "verified" without a declared checker.

# Release / CI prep notes (Wave 0.4)

Local process checklist for remaining-landscape Wave 0.4. **Do not commit or push
from this note alone** — these are dry-run commands and a commit-message draft for
when a maintainer chooses to cut a commit.

Public posture (unchanged; see confirmation below): QSpecBench is
**community-grade scoped research infrastructure with selected checked claims** —
not a complete quantum FV standard.

---

## Commit message draft (do not run `git commit`)

Suggested subject/body when packaging Wave 0 process/docs (and any sibling Wave 0
locks/adapters/sandbox work that is ready):

```text
docs: add CI/release dry-run prep and track-maintainer assignment procedure

Document local validate/lint/evidence-all/qec-matching and release-bundle
verify checklists without cutting a tag. Keep CODEOWNERS track vacancies TBA
and record how to assign a real handle when one exists.
```

Shorter alternative if the commit is **docs-only** (this wave’s files):

```text
docs: Wave 0.4 CI/release dry-run notes and GOVERNANCE maintainer procedure
```

**Before any real commit:** refresh the file list with `git status` / `git diff`
and stage only intentional paths. Do not include secrets, `.coverage`,
`__pycache__`, or scratch artifacts (`_tmp_*.qasm`, etc.).

### File-list note (Wave 0.4 docs)

Expected paths for this process wave (docs/governance only):

| Path | Role |
|------|------|
| `docs/release_prep_notes.md` | This checklist (commit draft, CI/release dry-runs, dashboard, posture) |
| `GOVERNANCE.md` | Short “how to assign a track maintainer” procedure; vacancies stay TBA |
| `CONTRIBUTING.md` | Dashboard regen after corpus edits |
| `docs/index.md` | Index link to this note |

Sibling Wave 0.1–0.3 work (locks, QBricks/ZX adapters, evidence sandbox) may add
non-doc paths; list those separately when those waves land. Avoid mixing
unrelated adapter/runner/Lean conflicts into a docs-only commit.

---

## CI dry-run checklist

Mirrors PR gates in [`.github/workflows/validate.yml`](../.github/workflows/validate.yml)
and [`.github/workflows/lint.yml`](../.github/workflows/lint.yml). Full E2E on the
entire corpus is **not** required for this prep wave; run the slices below locally
when practical.

### 0. Sync (include `qec-matching` where Stim evidence matters)

```bash
uv sync --frozen --extra dev --extra qec-matching
```

The `qec-matching` extra installs pinned `stim` / `pymatching` used by Stim honesty
paths (DoD K5; validate + release workflows).

### 1. Lint / hard pyright

```bash
uv run ruff check tools tests adapters scripts
uv run pyright tools/qspecbench adapters scripts
```

Optional trust-surface coverage gate (same idea as `lint.yml`):

```bash
uv run pytest \
  tests/test_phase9_governance.py \
  tests/test_phase10_maintainability.py \
  tests/test_schema_dialect.py \
  tests/test_resource_bounds.py \
  tests/test_release_failclosed.py \
  tests/test_trust_boundaries.py \
  tests/test_headline_scope.py \
  tests/test_p1_negative.py \
  tests/test_p2.py \
  tests/test_semantic_bridge_files_validate.py \
  tests/test_benchmark_layout.py \
  --cov=qspecbench.trust --cov=qspecbench.reviews --cov=qspecbench.adapter_registry \
  --cov=qspecbench.validation --cov=qspecbench.adapter_types \
  --cov=qspecbench.release_bundle --cov=qspecbench.resource_bounds \
  --cov-report=term-missing --cov-fail-under=55
```

### 2. Validate (Python corpus gate)

After Lean build artifacts are available (CI job `lean-build`, or local
`cd lean && lake build`):

```bash
uv run qspecbench validate benchmarks/
uv run qspecbench bridge-codegen verify benchmarks/
uv run qspecbench check-evidence benchmarks/
```

### 3. `evidence-all` (separate Lean target)

Never import `Evidence.All` into root `lean/QSpecBench.lean` (OOM). Build the
aggregate as CI does:

```bash
cd lean
lake build QSpecBench.Evidence.All
```

### 4. `qec-matching` honesty spot-check

With the extra installed, any claim that depends on Stim/pymatching adapters must
not silently skip as “ok” without the pins. Prefer a focused validate on QEC
benches that declare Stim evidence, or rely on the validate job after
`uv sync --extra qec-matching`.

---

## Release dry-run checklist

Mirrors [`.github/workflows/release.yml`](../.github/workflows/release.yml). Do
**not** create a git tag from this prep.

```bash
COMMIT="$(git rev-parse HEAD)"
mkdir -p artifacts/release

uv run qspecbench release-bundle benchmarks/ --out artifacts/release/release-bundle.tar.gz \
  --ci-run-id "local-dry-run" \
  --ci-run-url "local://dry-run"

uv run qspecbench verify-release-bundle artifacts/release/release-bundle.tar.gz \
  --require-review-artifacts \
  --expected-commit "${COMMIT}"
```

### Manifest field asserts (exact-commit gate)

After verify succeeds, assert reproducibility fields match the checked-out commit
(same checks as the release workflow “Assert exact-commit metadata” step):

```bash
python - <<'PY'
import json, os, tarfile
commit = os.environ.get("COMMIT") or __import__("subprocess").check_output(
    ["git", "rev-parse", "HEAD"], text=True
).strip()
with tarfile.open("artifacts/release/release-bundle.tar.gz", "r:gz") as tar:
    manifest = json.loads(tar.extractfile("manifest.json").read())
repro = manifest["reproducibility"]
assert repro.get("git_commit") == commit, (repro.get("git_commit"), commit)
required = [
    "schema_version", "tooling_version", "corpus_version",
    "lean_version", "mathlib_commit", "qcec_version", "uv_lock_hash",
]
missing = [k for k in required if not repro.get(k)]
assert not missing, missing
print("release dry-run commit gate OK", commit)
PY
```

CI also records `workflow_run_id` / `ci_run_id` on real runs; local dry-runs may
use the `--ci-run-id` stub above.

PR smoke (lighter): single-bench bundle without `--require-review-artifacts` is
enough for validate.yml; full release must use both flags above.

---

## Dashboard regen

After any corpus maturity / count-affecting edit:

```bash
qspecbench dashboard benchmarks/ --out docs/status.md
```

Or via uv:

```bash
uv run qspecbench dashboard benchmarks/ --out docs/status.md
```

Then confirm no drift (`git diff --exit-code docs/status.md`). CI validate fails if
`docs/status.md` is stale. Optional README status block sync:
`uv run python scripts/sync_readme_maturity.py` when that script is part of the
edit set.

Also noted in [CONTRIBUTING.md](../CONTRIBUTING.md) and the PR template.

---

## Public posture language (confirmed unchanged)

Wave 0.4 does **not** change README / DoD posture. Canonical wording remains:

From [definition_of_completion.md](definition_of_completion.md):

> Single checklist for when QSpecBench may honestly be called a **community-grade**
> benchmark and evidence infrastructure with selected checked claims — not a complete
> quantum FV standard.
>
> Until every box that is marked **required** is met, public language stays:
> **scoped research benchmark and evidence infrastructure with selected checked claims.**

From [README.md](../README.md) permanent residuals:

> Even when the [definition of completion](definition_of_completion.md) is met,
> QSpecBench remains a **scoped research benchmark** — not a complete quantum formal-verification
> standard.

From [docs/index.md](index.md):

> “Community-grade” … still means selected checked claims under declared universes —
> **not** a complete quantum FV standard.

Do not advertise unbounded industrial FV, device pulse fidelity, or fake-closed
permanent residuals when cutting releases.

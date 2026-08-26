# Lean-QEC version-isolated distance adapter

This adapter verifies a theorem from an **exact upstream Lean-QEC commit in its own Lean toolchain**.
It does not import Lean-QEC into QSpecBench's Lean 4.14 environment and it does not reinterpret a
distance theorem as syndrome-extraction, decoder, correction, or fault-tolerance evidence.

## Concrete pilot

The checked integration manifest pins:

- repository: `https://github.com/VerifiedQC/Lean-QEC.git`;
- commit: `c9c85603ab522b9f7df6315ed51513bcfb95fd90`;
- upstream toolchain: `leanprover/lean4:v4.30.0-rc2`;
- source: `LeanQEC/Stabilizer/Examples/BB/BB90.lean`;
- source Git blob: `8414ff1fb50f888998188f6e53020e95eb7891ca`;
- theorem: `BB90_dist_10`;
- proposition supported: the BB90 CSS-code distance lower bound `10 ≤ distance`;
- every LRAT certificate read by the BB90 module, with its Git-LFS SHA-256 object ID and exact byte size.

The pin intentionally uses the parent of upstream commit `5a0f9904bdce4b995a7abc1503cce363802c4857`
(`reconfigure lrat file endings`). A cold QSpecBench run against a later upstream commit reached the
pinned Lean toolchain but failed replay of `BB90_dist_z` with `The LRAT certificate could not be
verified` and LRAT-trimmer panics. Upstream Lean-QEC issue #29 independently reports that commit
`5a0f990` line-ending-normalized binary BB distance certificates and records the pre-change BB90
object IDs. QSpecBench therefore binds the immutable pre-change commit rather than broadening a
local fallback or modifying certificate bytes after checkout.

This repin does not substitute nearby evidence. At `c9c85603ab522b9f7df6315ed51513bcfb95fd90`,
the BB90 source has the same Git blob as the later pin, and the Lean toolchain, `lakefile.lean`, and
`lake-manifest.json` are unchanged. The two BB90 rank-certificate objects are unchanged as well; only
the two distance-certificate objects differ, and the manifest binds their exact pre-change LFS
SHA-256 IDs and byte sizes. A passing result still requires a fresh cold build of this exact state.

At the pinned source, the theorem is proved by two SAT distance obligations (`BB90_dist_z` and
`BB90_dist_x`) using LRAT-backed `bv_check`, followed by the verified SAT-to-distance translation.
The source also reads LRAT certificates for the two rank obligations. Because upstream stores these
proof certificates through Git LFS, source-commit identity alone is insufficient to reproduce the
kernel build: the certificate bytes are part of the evidence dependency closure.

## Execution

Normal corpus `check-evidence` does not silently perform a network build. Without explicit
activation, the adapter returns a structured skip. To execute the external kernel check:

```bash
QSPECBENCH_LEAN_QEC_VERIFY=1 \
  python adapters/lean_qec/parse_result.py \
  adapters/lean_qec/examples/bb90_distance_10.json
```

Verification mode is `cold_root_project_olean_build`. It deliberately does not restore a Lean-QEC
project `.lake` cache. It may fetch the ordinary Mathlib dependency cache before rebuilding the
pinned root-project module's OLean artifact from source. A successful cached upstream project CI run
is therefore useful provenance but is not substituted for this cold root-project proof check.

Verification mode:

1. creates an isolated temporary checkout and configures repository-local Git LFS with smudging disabled;
2. fetches only the exact upstream commit;
3. checks the commit, toolchain, source Git blob identity, and theorem declaration;
4. verifies that each required proof path is still the exact Git-LFS pointer committed by upstream;
5. materializes only the four manifest-declared LRAT objects and verifies each SHA-256 and byte size;
6. runs `lake exe cache get` for dependency artifacts without restoring an upstream project build cache;
7. builds `+LeanQEC.Stabilizer.Examples.BB.BB90:olean`;
8. emits structured JSON binding all verified identities, pointer metadata, materialized certificate hashes, and the exact build target.

When `QSPECBENCH_LEAN_QEC_LOG_DIR` is set, the adapter also persists full cache/build stdout and
stderr with SHA-256 digests. Structured failure diagnostics retain the output endpoints plus fatal
context extracted from the complete logs, so a long stack trace cannot silently displace the first
causal error. A failed cold build is reported as a failed reproduction attempt; it is not evidence
that the mathematical theorem is false.

When `QSPECBENCH_LEAN_QEC_WORKDIR` is set, the isolated checkout is created under that directory
instead of the process tempfile root (for example `artifacts/lean-qec/work` on a volume with enough
free space for Git-LFS materialization and the cold Lake build). An empty value or a non-directory
target fails closed. The directory is still a throwaway `qspecbench-lean-qec-*` temporary tree and
is removed when verification finishes.

## Scope discipline

A successful result can support only a **distance lower-bound** obligation. It does not support:

- syndrome-extraction circuit semantics;
- physical noise-model adequacy;
- decoder implementation correctness;
- correction/logical-state preservation;
- repeated-round/fault-tolerance behavior.

Those remain separate assurance-graph edges. This is an interoperability adapter, not the excluded
external reproduction program.

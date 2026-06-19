import Lake
open Lake DSL

package «qspecbench-proofs» where
  version := v!"0.2.0"

require mathlib from git
  "https://github.com/leanprover-community/mathlib4" @ "v4.14.0"

@[default_target]
lean_lib QSpecBench where

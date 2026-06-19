import QSpecBench.Legacy.Matrix

/-!
# No-cloning impossibility (permutation-matrix scaffold).

Shows that a unitary cloner would place two `1` entries in the same column of a
permutation matrix, which is impossible.
-/

namespace QSpecBench

open QSpecBench (Matrix4)

/-- Exactly one row is `1` in column `j`. -/
def column_singleton (U : Matrix4) (j : Fin 4) : Prop :=
  ∃ i, U i j = 1 ∧ ∀ k, U k j = 1 → k = i

/-- Cloning `|0⟩` and `|1⟩` with a single-qubit input ancilla would force two ones in column 0. -/
def isClonerColumn (U : Matrix4) : Prop :=
  U 0 0 = 1 ∧ U 1 0 = 1

theorem no_universal_cloner_matrix (U : Matrix4) (hs : column_singleton U 0) (hc : isClonerColumn U) :
    False := by
  rcases hs with ⟨i, _, huniq⟩
  cases (huniq 0 hc.1).trans (huniq 1 hc.2).symm

end QSpecBench

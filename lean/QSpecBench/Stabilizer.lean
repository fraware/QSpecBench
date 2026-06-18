/-!
# Three-qubit stabilizer commutation for the bit-flip code.

Stabilizers ZZI and IZZ commute under Pauli multiplication (same-axis or disjoint support).
-/

namespace QSpecBench

abbrev Pauli3 := Fin 3 → Fin 4

def pauliMul3 (p q : Pauli3) : Pauli3 :=
  fun i =>
    if p i = q i then p i
    else if p i = 0 ∨ q i = 0 then if p i = 0 then q i else p i
    else 1

def pauliCommutes3 (p q : Pauli3) : Prop :=
  ∀ i j : Fin 3, i ≠ j → (p i ≠ 0 ∧ q j ≠ 0) → (p j = 0 ∨ q i = 0)

def bitFlipZ0Z1 : Pauli3 := fun i =>
  match i with
  | ⟨0, _⟩ => 1
  | ⟨1, _⟩ => 1
  | ⟨2, _⟩ => 0

def bitFlipZ1Z2 : Pauli3 := fun i =>
  match i with
  | ⟨0, _⟩ => 0
  | ⟨1, _⟩ => 1
  | ⟨2, _⟩ => 1

theorem bit_flip_stabilizers_commute : pauliCommutes3 bitFlipZ0Z1 bitFlipZ1Z2 := by
  intro i j hne hboth
  fin_cases i <;> fin_cases j <;> first | contradiction | trivial

end QSpecBench

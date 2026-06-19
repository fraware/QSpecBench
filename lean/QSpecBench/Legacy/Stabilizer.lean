import Mathlib.Tactic.FinCases

/-!
# Pauli stabilizer commutation (legacy layer).
-/

namespace QSpecBench

abbrev Pauli3 := Fin 3 → Fin 4

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

theorem repetition_stabilizers_commute : pauliCommutes3 bitFlipZ0Z1 bitFlipZ1Z2 :=
  bit_flip_stabilizers_commute

def phaseFlipX0X1 : Pauli3 := fun i =>
  match i with
  | ⟨0, _⟩ => 2
  | ⟨1, _⟩ => 2
  | ⟨2, _⟩ => 0

def phaseFlipX1X2 : Pauli3 := fun i =>
  match i with
  | ⟨0, _⟩ => 0
  | ⟨1, _⟩ => 2
  | ⟨2, _⟩ => 2

theorem phase_flip_stabilizers_commute : pauliCommutes3 phaseFlipX0X1 phaseFlipX1X2 := by
  intro i j hne hboth
  fin_cases i <;> fin_cases j <;> first | contradiction | trivial

abbrev Pauli7 := Fin 7 → Fin 4

def pauliCommutes7 (p q : Pauli7) : Prop :=
  ∀ i j : Fin 7, i ≠ j → (p i ≠ 0 ∧ q j ≠ 0) → (p j = 0 ∨ q i = 0)

def steaneZ01 : Pauli7 := fun i => if i.val ≤ 1 then 1 else 0
def steaneZ12 : Pauli7 := fun i => if i.val = 1 ∨ i.val = 2 then 1 else 0
def steaneZ23 : Pauli7 := fun i => if i.val = 2 ∨ i.val = 3 then 1 else 0
def steaneZ34 : Pauli7 := fun i => if i.val = 3 ∨ i.val = 4 then 1 else 0
def steaneZ45 : Pauli7 := fun i => if i.val = 4 ∨ i.val = 5 then 1 else 0
def steaneZ56 : Pauli7 := fun i => if i.val = 5 ∨ i.val = 6 then 1 else 0

theorem steane_stabilizers_commute :
    pauliCommutes7 steaneZ01 steaneZ12 ∧
    pauliCommutes7 steaneZ12 steaneZ23 ∧
    pauliCommutes7 steaneZ23 steaneZ34 ∧
    pauliCommutes7 steaneZ34 steaneZ45 ∧
    pauliCommutes7 steaneZ45 steaneZ56 := by
  refine ⟨?_, ?_, ?_, ?_, ?_⟩
  all_goals
    intro i j hne hboth
    fin_cases i <;> fin_cases j <;> first | contradiction | simp [steaneZ01, steaneZ12, steaneZ23, steaneZ34, steaneZ45, steaneZ56]

abbrev Pauli9 := Fin 9 → Fin 4

def pauliCommutes9 (p q : Pauli9) : Prop :=
  ∀ i j : Fin 9, i ≠ j → (p i ≠ 0 ∧ q j ≠ 0) → (p j = 0 ∨ q i = 0)

def shorZ01 : Pauli9 := fun i => if i.val ≤ 1 then 1 else 0
def shorZ12 : Pauli9 := fun i => if i.val = 1 ∨ i.val = 2 then 1 else 0
def shorZ34 : Pauli9 := fun i => if i.val = 3 ∨ i.val = 4 then 1 else 0
def shorZ45 : Pauli9 := fun i => if i.val = 4 ∨ i.val = 5 then 1 else 0
def shorZ67 : Pauli9 := fun i => if i.val = 6 ∨ i.val = 7 then 1 else 0
def shorZ78 : Pauli9 := fun i => if i.val = 7 ∨ i.val = 8 then 1 else 0

theorem shor_stabilizers_commute :
    pauliCommutes9 shorZ01 shorZ12 ∧
    pauliCommutes9 shorZ34 shorZ45 ∧
    pauliCommutes9 shorZ67 shorZ78 := by
  refine ⟨?_, ?_, ?_⟩
  all_goals
    intro i j hne hboth
    fin_cases i <;> fin_cases j <;> first | contradiction | simp [shorZ01, shorZ12, shorZ34, shorZ45, shorZ67, shorZ78]

def surfaceZPlaq0 : Pauli9 := fun i => if i.val ≤ 1 then 1 else 0
def surfaceZPlaq1 : Pauli9 := fun i => if i.val = 1 ∨ i.val = 2 then 1 else 0
def surfaceZPlaq2 : Pauli9 := fun i => if i.val = 3 ∨ i.val = 4 then 1 else 0
def surfaceZPlaq3 : Pauli9 := fun i => if i.val = 4 ∨ i.val = 5 then 1 else 0

theorem surface_stabilizers_commute :
    pauliCommutes9 surfaceZPlaq0 surfaceZPlaq1 ∧
    pauliCommutes9 surfaceZPlaq1 surfaceZPlaq2 ∧
    pauliCommutes9 surfaceZPlaq2 surfaceZPlaq3 ∧
    pauliCommutes9 surfaceZPlaq0 surfaceZPlaq2 ∧
    pauliCommutes9 surfaceZPlaq0 surfaceZPlaq3 ∧
    pauliCommutes9 surfaceZPlaq1 surfaceZPlaq3 := by
  refine ⟨?_, ?_, ?_, ?_, ?_, ?_⟩
  all_goals
    intro i j hne hboth
    fin_cases i <;> fin_cases j <;> first | contradiction | simp [surfaceZPlaq0, surfaceZPlaq1, surfaceZPlaq2, surfaceZPlaq3]

end QSpecBench

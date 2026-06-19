import Mathlib.Tactic.FinCases
import Mathlib.Tactic.Ring

/-!
Shared matrix utilities for QSpecBench gate models (Mathlib-free legacy layer).
-/

namespace QSpecBench

abbrev Matrix2 := Fin 2 → Fin 2 → Int

def mul2 (A B : Matrix2) (i j : Fin 2) : Int :=
  A i 0 * B 0 j + A i 1 * B 1 j

def id2 (i j : Fin 2) : Int :=
  if i = j then 1 else 0

def scale2 (k : Int) (M : Matrix2) (i j : Fin 2) : Int :=
  k * M i j

theorem mul2_assoc (A B C : Matrix2) (i j : Fin 2) :
    mul2 A (mul2 B C) i j = mul2 (mul2 A B) C i j := by
  fin_cases i <;> fin_cases j <;> simp [mul2] <;> ring

abbrev Matrix4 := Fin 4 → Fin 4 → Int

def mul4 (A B : Matrix4) (i j : Fin 4) : Int :=
  A i 0 * B 0 j + A i 1 * B 1 j + A i 2 * B 2 j + A i 3 * B 3 j

def id4 (i j : Fin 4) : Int :=
  if i = j then 1 else 0

abbrev Matrix8 := Fin 8 → Fin 8 → Int

def mul8 (A B : Matrix8) (i j : Fin 8) : Int :=
  A i 0 * B 0 j + A i 1 * B 1 j + A i 2 * B 2 j + A i 3 * B 3 j +
    A i 4 * B 4 j + A i 5 * B 5 j + A i 6 * B 6 j + A i 7 * B 7 j

def id8 (i j : Fin 8) : Int :=
  if i = j then 1 else 0

def scale4 (k : Int) (M : Matrix4) (i j : Fin 4) : Int :=
  k * M i j

/-- CCX with controls q0,q1 and target q2 in lexicographic |q0 q1 q2⟩ basis. -/
def ccx8 (i j : Fin 8) : Int :=
  if i = j then 1
  else if (i.val = 3 ∧ j.val = 7) ∨ (i.val = 7 ∧ j.val = 3) then 1
  else 0

/-- SWAP on qubits 0 and 1 in lexicographic two-qubit basis. -/
def swap4 (i j : Fin 4) : Int :=
  match i, j with
  | ⟨0, _⟩, ⟨0, _⟩ => 1
  | ⟨1, _⟩, ⟨2, _⟩ => 1
  | ⟨2, _⟩, ⟨1, _⟩ => 1
  | ⟨3, _⟩, ⟨3, _⟩ => 1
  | _, _ => 0

/-- Kronecker product I₂ ⊗ A for single-qubit A on the second tensor factor. -/
def kronI2 (A : Matrix2) (i j : Fin 4) : Int :=
  let i0 : Fin 2 := ⟨i.val / 2, by omega⟩
  let i1 : Fin 2 := ⟨i.val % 2, by omega⟩
  let j0 : Fin 2 := ⟨j.val / 2, by omega⟩
  let j1 : Fin 2 := ⟨j.val % 2, by omega⟩
  if i0 = j0 then A i1 j1 else 0

/-- Kronecker product A ⊗ I₂ for single-qubit A on the first tensor factor. -/
def kron2I (A : Matrix2) (i j : Fin 4) : Int :=
  let i0 : Fin 2 := ⟨i.val / 2, by omega⟩
  let i1 : Fin 2 := ⟨i.val % 2, by omega⟩
  let j0 : Fin 2 := ⟨j.val / 2, by omega⟩
  let j1 : Fin 2 := ⟨j.val % 2, by omega⟩
  if i1 = j1 then A i0 j0 else 0

end QSpecBench

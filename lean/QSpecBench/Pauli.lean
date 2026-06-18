/-!
# Single-qubit Pauli/Hadamard matrix lemmas (Mathlib-free, integer model).

`hadamard2` is the **unnormalized** Hadamard (entries ±1). Squaring yields `2 • I`, matching
OpenQASM `H` up to the global factor `1/√2` per gate (declared in benchmark assumptions).
-/

namespace QSpecBench

abbrev Matrix2 := Fin 2 → Fin 2 → Int

def mul2 (A B : Matrix2) (i j : Fin 2) : Int :=
  A i 0 * B 0 j + A i 1 * B 1 j

def id2 (i j : Fin 2) : Int :=
  if i = j then 1 else 0

def scale2 (k : Int) (M : Matrix2) (i j : Fin 2) : Int :=
  k * M i j

/-- Unnormalized Hadamard matrix. -/
def hadamard2 (i j : Fin 2) : Int :=
  match i, j with
  | ⟨0, _⟩, ⟨0, _⟩ => 1
  | ⟨0, _⟩, ⟨1, _⟩ => 1
  | ⟨1, _⟩, ⟨0, _⟩ => 1
  | ⟨1, _⟩, ⟨1, _⟩ => -1

theorem hadamard_mul_self (i j : Fin 2) : mul2 hadamard2 hadamard2 i j = scale2 2 id2 i j := by
  funext i j
  fin_cases i <;> fin_cases j <;> rfl

def pauliX2 (i j : Fin 2) : Int :=
  match i, j with
  | ⟨0, _⟩, ⟨1, _⟩ => 1
  | ⟨1, _⟩, ⟨0, _⟩ => 1
  | _, _ => 0

def pauliZ2 (i j : Fin 2) : Int :=
  match i, j with
  | ⟨0, _⟩, ⟨0, _⟩ => 1
  | ⟨1, _⟩, ⟨1, _⟩ => -1
  | _, _ => 0

/-- Unnormalized model: H X H = 2 • Z (OpenQASM H carries 1/√2 scaling per gate). -/
theorem hadamard_conjugates_x (i j : Fin 2) :
    mul2 (mul2 hadamard2 pauliX2) hadamard2 i j = scale2 2 pauliZ2 i j := by
  funext i j
  fin_cases i <;> fin_cases j <;> rfl

end QSpecBench

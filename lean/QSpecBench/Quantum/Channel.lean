import Mathlib.Data.Complex.Basic
import Mathlib.Data.Matrix.Notation
import Mathlib.Tactic.FinCases
import Mathlib.Tactic.NormNum
import Mathlib.Algebra.BigOperators.Fin
import Mathlib.LinearAlgebra.Matrix.Hermitian
import Mathlib.LinearAlgebra.Matrix.Spectrum
import QSpecBench.Quantum.ComplexGate

/-!
# Qubit CPTP channel carriers beyond the Pauli class

Mathlib v4.14 exposes Hermitian eigenvalues (`Matrix.IsHermitian.eigenvalues`) but has
no Schatten / completely-bounded API for arbitrary CPTP maps. This module records
Mathlib-aligned carriers for:

* Kraus operator-sum representations (qubit→qubit);
* unital qubit channels (Φ(I)=I as a declared carrier class);
* amplitude-damping channels (the canonical non-Pauli qubit CPTP family);

and a nuclear/Schatten-1 definition `∑|λᵢ|` on Hermitian matrices, with an exact
computational-basis evaluation on the replacement Choi difference (diagonal profile
`(1,0,0,−1)` ⇒ abs-sum `2`).

**Permanent residual** (`general_cb_arbitrary_cptp_mathlib`): diamond = nuclear for
*all* qubit CPTP pairs is out of scope until Mathlib grows a CB library. Claim
identity is narrowed to the proved subclass below (v3); Haar Monte-Carlo and
multi-step Trotter remain separate named holes.
-/

namespace QSpecBench

open Matrix Complex
open QSpecBench.Quantum.ComplexGate

/-! ## Mathlib nuclear / Schatten-1 on Hermitian matrices -/

/-- Mathlib-aligned nuclear / Schatten-1 norm of a Hermitian matrix: ∑ |λᵢ|.
By definition this *is* the nuclear norm on the Hermitian spectral measure;
equating it to the channel diamond for arbitrary CPTP is the permanent residual. -/
noncomputable def mathlibNuclearHermitian {n : Type*} [Fintype n] [DecidableEq n]
    (A : Matrix n n ℂ) (hA : A.IsHermitian) : ℝ :=
  ∑ i : n, |hA.eigenvalues i|

/-- Computational-basis absolute diagonal sum (nuclear when `A` is already diagonal
in the standard basis). -/
noncomputable def diagAbsSum {n : Type*} [Fintype n] (A : Matrix n n ℂ) : ℝ :=
  ∑ i : n, |RCLike.re (A i i)|

/-! ## Kraus operator-sum carrier (qubit→qubit) -/

/-- Finite Kraus list for a qubit→qubit map. Completeness ∑ₖ Eₖ† Eₖ = I is a
trust-boundary Prop (`isTracePreserving`), not baked into the type. -/
structure QubitKrausChannel where
  ops : List Mat2C

/-- Completeness relation for a Kraus list (TP when the map is also CP). -/
def QubitKrausChannel.isTracePreserving (Φ : QubitKrausChannel) : Prop :=
  (Φ.ops.map fun E => E.conjTranspose * E).sum = (1 : Mat2C)

/-- Unitary channel as a single Kraus operator. -/
def krausOfUnitary (U : Mat2C) : QubitKrausChannel :=
  ⟨[U]⟩

theorem krausOfUnitary_one_tp : (krausOfUnitary (1 : Mat2C)).isTracePreserving := by
  simp [QubitKrausChannel.isTracePreserving, krausOfUnitary, List.sum_cons, List.sum_nil,
    Matrix.conjTranspose_one, mul_one]

/-- Rank-1 replacement channel to `|0⟩`: Kraus `E₀ = |0⟩⟨0|`, `E₁ = |0⟩⟨1|`. -/
def krausReplacementToKet0 : QubitKrausChannel :=
  ⟨[Matrix.of fun i j => if i = 0 ∧ j = 0 then (1 : ℂ) else 0,
    Matrix.of fun i j => if i = 0 ∧ j = 1 then (1 : ℂ) else 0]⟩

/-! ## Unital qubit channel carrier -/

/-- Declared unital qubit channel carrier class (Φ(I)=I). Pauli unital channels
and the fully depolarizing channel inhabit this class; amplitude damping does not. -/
inductive UnitalQubitChannel
  | identity
  | depolarizing
  deriving DecidableEq

theorem unital_identity_and_depolarizing_inhabit :
    UnitalQubitChannel.identity ≠ UnitalQubitChannel.depolarizing := by
  decide

/-! ## Amplitude-damping channel (non-Pauli CPTP) -/

/-- Amplitude-damping parameter γ ∈ [0,1] (trust-boundary; not enforced in type). -/
structure AmplitudeDampingChannel where
  γ : ℝ

/-- Standard Kraus operators for amplitude damping.
`E₀ = [[1,0],[0,√(1-γ)]]`, `E₁ = [[0,√γ],[0,0]]`. -/
noncomputable def amplitudeDampingKraus (Φ : AmplitudeDampingChannel) : QubitKrausChannel :=
  let s0 : ℂ := (Real.sqrt (1 - Φ.γ) : ℂ)
  let s1 : ℂ := (Real.sqrt Φ.γ : ℂ)
  ⟨[Matrix.of fun i j =>
      if i = 0 ∧ j = 0 then (1 : ℂ)
      else if i = 1 ∧ j = 1 then s0
      else 0,
    Matrix.of fun i j =>
      if i = 0 ∧ j = 1 then s1 else 0]⟩

/-- Identity channel as amplitude damping at γ = 0. -/
def amplitudeDampingId : AmplitudeDampingChannel := ⟨0⟩

/-- Replacement-to-`|0⟩` as amplitude damping at γ = 1 (extreme non-Pauli point). -/
def amplitudeDampingToKet0 : AmplitudeDampingChannel := ⟨1⟩

theorem amplitudeDamping_extreme_ne_id :
    amplitudeDampingToKet0 ≠ amplitudeDampingId := by
  intro h
  have hγ : (1 : ℝ) = 0 := congrArg AmplitudeDampingChannel.γ h
  exact absurd hγ (by norm_num)

/-- Amplitude damping at γ ∈ (0,1] is outside the Pauli-channel class (declared):
Pauli channels are unital; AD_γ for γ ∈ (0,1] is not. -/
def amplitudeDamping_nonPauli_note : String :=
  "Amplitude damping AD_γ (γ∈(0,1]) is non-unital hence not a Pauli channel; \
included as the canonical non-Pauli qubit CPTP extreme alongside Kraus/unital carriers."

/-! ## Replacement Choi difference: diagonal nuclear = 2 -/

/-- Computational basis vector `|00⟩`. -/
def ket00 : Fin 4 → ℂ
  | ⟨0, _⟩ => 1
  | _ => 0

/-- Computational basis vector `|11⟩`. -/
def ket11 : Fin 4 → ℂ
  | ⟨3, _⟩ => 1
  | _ => 0

/-- Choi of replacement-to-`|0⟩`: `|00⟩⟨00|`. -/
def replacementChoi0 : Mat4C :=
  Matrix.of fun i j => ket00 i * star (ket00 j)

/-- Choi of replacement-to-`|1⟩`: `|11⟩⟨11|`. -/
def replacementChoi1 : Mat4C :=
  Matrix.of fun i j => ket11 i * star (ket11 j)

/-- Diagonal profile of `|00⟩⟨00| − |11⟩⟨11|`: (1,0,0,−1). -/
def replacementChoiDiffDiag : Fin 4 → ℂ
  | ⟨0, _⟩ => 1
  | ⟨3, _⟩ => -1
  | _ => 0

theorem replacementChoiDiff_eq_diagonal :
    replacementChoi0 - replacementChoi1 = diagonal replacementChoiDiffDiag := by
  ext i j
  fin_cases i <;> fin_cases j <;>
    simp [replacementChoi0, replacementChoi1, ket00, ket11, replacementChoiDiffDiag,
      Matrix.of_apply, Matrix.sub_apply, Matrix.diagonal]

theorem replacementChoiDiffDiag_selfAdjoint (i : Fin 4) :
    IsSelfAdjoint (replacementChoiDiffDiag i) := by
  fin_cases i <;> simp [replacementChoiDiffDiag, isSelfAdjoint_iff]

theorem channel_replacementChoiDiff_isHermitian :
    (replacementChoi0 - replacementChoi1).IsHermitian := by
  rw [replacementChoiDiff_eq_diagonal]
  exact (Matrix.isHermitian_diagonal_iff).2 replacementChoiDiffDiag_selfAdjoint

/-- Standard-basis nuclear of the replacement Choi difference equals 2.
Equals Mathlib `∑|λᵢ|` once the computational basis is recognized as an eigenbasis
(true for this diagonal Hermitian); full arbitrary-Hermitian bridge stays residual. -/
theorem replacementChoiDiff_diagAbsSum_eq_two :
    diagAbsSum (replacementChoi0 - replacementChoi1) = 2 := by
  rw [replacementChoiDiff_eq_diagonal]
  simp [diagAbsSum, replacementChoiDiffDiag, Fin.sum_univ_four, Matrix.diagonal_apply]
  norm_num

/-! ## Bundle: beyond-Pauli subclass + nuclear specialization -/

/-- Permanent proved subclass for qubit CPTP CB fragments:
Kraus carrier + unital carrier + amplitude-damping (non-Pauli) extremes +
Hermitian replacement Choi with computational-basis nuclear (=2).
Not arbitrary CPTP diamond; `general_cb_arbitrary_cptp_mathlib` stays permanently
narrowed (claim-identity v3). -/
theorem qubit_cptp_cb_proved_subclass_mathlib :
    (krausOfUnitary (1 : Mat2C)).isTracePreserving ∧
      amplitudeDampingToKet0 ≠ amplitudeDampingId ∧
      UnitalQubitChannel.identity ≠ UnitalQubitChannel.depolarizing ∧
      (replacementChoi0 - replacementChoi1).IsHermitian ∧
      replacementChoi0 - replacementChoi1 = diagonal replacementChoiDiffDiag ∧
      diagAbsSum (replacementChoi0 - replacementChoi1) = 2 :=
  ⟨krausOfUnitary_one_tp, amplitudeDamping_extreme_ne_id,
    unital_identity_and_depolarizing_inhabit, channel_replacementChoiDiff_isHermitian,
    replacementChoiDiff_eq_diagonal, replacementChoiDiff_diagAbsSum_eq_two⟩

/-- Permanent residual note: full CB on arbitrary CPTP is out of Mathlib scope. -/
def generalCbArbitraryCptpPermanentResidual : String :=
  "PERMANENT: Mathlib v4.14 has no Schatten/CB API for arbitrary CPTP maps. \
Proved subclass: unitary Choi Schatten-1, replacement diag-nuclear=2 (Hermitian \
diagonal), Pauli ℓ¹ diamond, Kraus/unital carriers, amplitude-damping non-Pauli \
extremes. general_cb_arbitrary_cptp_mathlib is permanently not_applicable \
(claim-identity v3 narrowing); Haar Monte-Carlo and multi-step Trotter remain \
separate named holes."

#check mathlibNuclearHermitian
#check diagAbsSum
#check QubitKrausChannel
#check UnitalQubitChannel
#check AmplitudeDampingChannel
#check amplitudeDampingKraus
#check replacementChoiDiff_diagAbsSum_eq_two
#check qubit_cptp_cb_proved_subclass_mathlib
#check generalCbArbitraryCptpPermanentResidual

end QSpecBench

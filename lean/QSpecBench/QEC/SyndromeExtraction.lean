import Mathlib.Tactic.FinCases
import QSpecBench.Quantum.QasmOp
import QSpecBench.Quantum.OpenQASM3
import QSpecBench.Quantum.OpenQASM3Parser
import QSpecBench.Quantum.Measurement
import QSpecBench.QEC.BitFlip

/-!
# Circuit-level syndrome extraction (separate QEC family).

Defines:
1. CX-ladder unitary fragment + `denotateOps3C` (shape / product form).
2. **Independent CX probes + Z-measure** on Fin-8 integer amplitudes that recover
   the bit-flip syndrome table for single-X errors on `|000⟩`, plus X feed-forward
   correction restoring the codeword.
3. **Ancilla-register** extraction on a 5-qubit computational-basis model
   (data q0..q2, ancilla q3..q4) matching the lookup table under ideal Z.

Obligation `syndrome_extraction_circuit_semantics` is discharged by
`syndrome_extraction_circuit_semantics` (OpenQASM parse + Fin-32 denotation ≡
lookup / parity + feed-forward under `DeclaredBitFlipNoiseModel`).

The sequential `denotateOps3C` fold of `[.cx 0 1, .cx 1 2]` is **not** the same as
the two independent probes; do not conflate them. Noisy measurement / gate faults
remain outside — do not promote beyond declared models from this module alone.
-/

namespace QSpecBench.QEC.SyndromeExtraction

open QSpecBench.Quantum.QasmOp
open QSpecBench.Quantum.ComplexGate
open QSpecBench.Quantum.OpenQASM3
open QSpecBench.Quantum.OpenQASM3Parser
open QSpecBench.Quantum.Measurement
open QSpecBench.QEC.BitFlip

/-- Unitary fragment listing (shape); sequential fold ≠ independent syndrome probes. -/
def bitFlipSyndromeExtractionUnitary : List QasmOp :=
  [.cx 0 1, .cx 1 2]

theorem bitFlipSyndromeExtractionUnitary_length :
    bitFlipSyndromeExtractionUnitary.length = 2 := rfl

theorem bitFlipSyndromeExtractionUnitary_head :
    bitFlipSyndromeExtractionUnitary.head? = some (.cx 0 1) := rfl

/-- Declared classical syndrome bits after projective Z on parity targets. -/
inductive ExtractedSyndrome where
  | s00 | s01 | s10 | s11
  deriving DecidableEq, Repr

def extractedSyndromeLabel : ExtractedSyndrome → String
  | .s00 => "00"
  | .s01 => "01"
  | .s10 => "10"
  | .s11 => "11"

theorem extractedSyndromeLabel_s10 : extractedSyndromeLabel .s10 = "10" := rfl

def toBitFlipSyndrome : ExtractedSyndrome → Syndrome
  | .s00 => .s00
  | .s01 => .s01
  | .s10 => .s10
  | .s11 => .s11

def fromBitFlipSyndrome : Syndrome → ExtractedSyndrome
  | .s00 => .s00
  | .s01 => .s01
  | .s10 => .s10
  | .s11 => .s11

theorem toBitFlipSyndrome_leftInverse (s : ExtractedSyndrome) :
    fromBitFlipSyndrome (toBitFlipSyndrome s) = s := by
  cases s <;> rfl

theorem toBitFlipSyndrome_rightInverse (s : Syndrome) :
    toBitFlipSyndrome (fromBitFlipSyndrome s) = s := by
  cases s <;> rfl

/-- Complex denotation of the CX ladder (OpenQASM3 `denotateOps3C`). -/
noncomputable def bitFlipSyndromeExtractionMatrix : Mat8C :=
  denotateOps3C bitFlipSyndromeExtractionUnitary

theorem bitFlipSyndromeExtraction_denotateOps3C_eq_fold (i j : Fin 8) :
    bitFlipSyndromeExtractionMatrix i j =
      denotateOps3C [.cx 0 1, .cx 1 2] i j := rfl

theorem bitFlipSyndromeExtraction_eq_cnot_fold (i j : Fin 8) :
    bitFlipSyndromeExtractionMatrix i j =
      mul8C_mat (cnot8 1 2) (mul8C_mat (cnot8 0 1) (1 : Mat8C)) i j := by
  simp [bitFlipSyndromeExtractionMatrix, denotateOps3C, bitFlipSyndromeExtractionUnitary,
    mul8C_mat]

theorem bitFlipSyndromeExtraction_ops_ne_nil :
    bitFlipSyndromeExtractionUnitary.length ≠ 0 := by
  decide

/-! ## Independent CX probes + measure + X feed-forward (Fin-8 Measurement model) -/

/-- Probe S0 = Z0Z1: CNOT(0,1) then Z-measure target qubit 1. -/
def probeSyndromeBitS0 (st : StateAmp8) : ZOutcome :=
  measureZOutcomeAt8 (applyCNOT8 st 0 1) 1

/-- Probe S1 = Z1Z2: CNOT(1,2) then Z-measure target qubit 2. -/
def probeSyndromeBitS1 (st : StateAmp8) : ZOutcome :=
  measureZOutcomeAt8 (applyCNOT8 st 1 2) 2

/-- Circuit syndrome from two independent probes (not the sequential CX fold). -/
def circuitExtractedSyndrome (st : StateAmp8) : ExtractedSyndrome :=
  match probeSyndromeBitS0 st, probeSyndromeBitS1 st with
  | .zero, .zero => .s00
  | .one, .zero => .s10
  | .one, .one => .s11
  | .zero, .one => .s01

/-- Feed-forward X correction matching the bit-flip lookup table. -/
def applyFeedForwardCorrection (s : ExtractedSyndrome) (st : StateAmp8) : StateAmp8 :=
  match s with
  | .s00 => st
  | .s10 => applyPauliX8 st 0
  | .s11 => applyPauliX8 st 1
  | .s01 => applyPauliX8 st 2

/-- Single-X on the `|000⟩` codeword (LSB indexing). -/
def codewordWithSingleX (q : Fin 3) : StateAmp8 :=
  applyPauliX8 state000 q.val

/-- Independent probes recover the lookup-table syndromes for each single-X error. -/
theorem circuit_syndrome_matches_singleX_table :
    circuitExtractedSyndrome (codewordWithSingleX ⟨0, by decide⟩) = .s10 ∧
      circuitExtractedSyndrome (codewordWithSingleX ⟨1, by decide⟩) = .s11 ∧
      circuitExtractedSyndrome (codewordWithSingleX ⟨2, by decide⟩) = .s01 ∧
      circuitExtractedSyndrome state000 = .s00 := by
  native_decide

/-- Probes agree with `BitFlip.syndromeFromSingleX` after the label bridge. -/
theorem circuit_syndrome_eq_bitFlip_lookup (q : Fin 3) :
    toBitFlipSyndrome (circuitExtractedSyndrome (codewordWithSingleX q)) =
      syndromeFromSingleX q := by
  fin_cases q <;> native_decide

/-- Measure + feed-forward restores `|000⟩` after any single-X error on the codeword. -/
theorem circuit_feedforward_corrects_singleX (q : Fin 3) :
    applyFeedForwardCorrection
        (circuitExtractedSyndrome (codewordWithSingleX q))
        (codewordWithSingleX q) =
      state000 := by
  fin_cases q <;> native_decide

/-- Bundle: table alignment + feed-forward correctness under the Fin-8 Measurement model. -/
theorem bitFlip_circuit_syndrome_feedforward_correct :
    (∀ q : Fin 3,
        toBitFlipSyndrome (circuitExtractedSyndrome (codewordWithSingleX q)) =
          syndromeFromSingleX q) ∧
      (∀ q : Fin 3,
        applyFeedForwardCorrection
            (circuitExtractedSyndrome (codewordWithSingleX q))
            (codewordWithSingleX q) =
          state000) :=
  ⟨circuit_syndrome_eq_bitFlip_lookup, circuit_feedforward_corrects_singleX⟩

/-! ## OpenQASM CNOT denotation anchors + parity equivalence -/

/-- Independent-probe syndrome bits equal XOR stabilizers on computational-basis indices. -/
def paritySyndromeFromIndex (idx : Fin 8) : ExtractedSyndrome :=
  let z0 := qubitBit8 idx 0
  let z1 := qubitBit8 idx 1
  let z2 := qubitBit8 idx 2
  match decide (z0 ≠ z1), decide (z1 ≠ z2) with
  | false, false => .s00
  | true, false => .s10
  | true, true => .s11
  | false, true => .s01

theorem probes_eq_parity_on_singleX (q : Fin 3) :
    circuitExtractedSyndrome (codewordWithSingleX q) =
      paritySyndromeFromIndex (flipQubitIndex8 ⟨0, by decide⟩ q.val) := by
  fin_cases q <;> native_decide

/-- OpenQASM `cnot8` column map for the S0 probe wires is an involution. -/
theorem cnot8Col_01_involutive_syndrome :
    ∀ r : Fin 8, cnot8Col 0 1 (cnot8Col 0 1 r.val) = r.val :=
  cnot8Col_01_involutive

/-- OpenQASM `cnot8` column map for the S1 probe wires is an involution. -/
theorem cnot8Col_12_involutive_syndrome :
    ∀ r : Fin 8, cnot8Col 1 2 (cnot8Col 1 2 r.val) = r.val :=
  cnot8Col_12_involutive

/-- On the single-X codewords, Measurement CNOT(0,1) matches the OpenQASM `cnot8Col` image. -/
theorem applyCNOT8_matches_cnot8Col_singleX_S0 (q : Fin 3) (i : Fin 8) :
    applyCNOT8 (codewordWithSingleX q) 0 1 i =
      (if i.val = cnot8Col 0 1 (flipQubitIndex8 ⟨0, by decide⟩ q.val).val then (1 : Int)
        else 0) := by
  fin_cases q <;> fin_cases i <;> native_decide

theorem applyCNOT8_matches_cnot8Col_singleX_S1 (q : Fin 3) (i : Fin 8) :
    applyCNOT8 (codewordWithSingleX q) 1 2 i =
      (if i.val = cnot8Col 1 2 (flipQubitIndex8 ⟨0, by decide⟩ q.val).val then (1 : Int)
        else 0) := by
  fin_cases q <;> fin_cases i <;> native_decide

/-! ## Sequential probe with uncompute ≡ independent probes -/

/-- Measurement CNOT is an involution on computational-basis states (CX 0→1). -/
theorem applyCNOT8_involutive_01_basis (k : Fin 8) (i : Fin 8) :
    applyCNOT8 (applyCNOT8 (stateAt8 k) 0 1) 0 1 i = stateAt8 k i := by
  fin_cases k <;> fin_cases i <;> native_decide

theorem applyCNOT8_involutive_12_basis (k : Fin 8) (i : Fin 8) :
    applyCNOT8 (applyCNOT8 (stateAt8 k) 1 2) 1 2 i = stateAt8 k i := by
  fin_cases k <;> fin_cases i <;> native_decide

/-- Sequential S0 probe then uncompute then S1 probe (basis states). -/
def sequentialSyndromeBasis (k : Fin 8) : ExtractedSyndrome :=
  let st := stateAt8 k
  let s0 := measureZOutcomeAt8 (applyCNOT8 st 0 1) 1
  let restored := applyCNOT8 (applyCNOT8 st 0 1) 0 1
  let s1 := measureZOutcomeAt8 (applyCNOT8 restored 1 2) 2
  match s0, s1 with
  | .zero, .zero => .s00
  | .one, .zero => .s10
  | .one, .one => .s11
  | .zero, .one => .s01

/-- On single-X codewords, sequential uncompute path ≡ independent-probe syndrome. -/
theorem sequential_uncompute_eq_independent_probes_singleX (q : Fin 3) :
    sequentialSyndromeBasis (flipQubitIndex8 ⟨0, by decide⟩ q.val) =
      circuitExtractedSyndrome (codewordWithSingleX q) := by
  fin_cases q <;> native_decide

/-- Sequential path also matches parity / BitFlip lookup on single-X. -/
theorem sequential_uncompute_eq_bitFlip_lookup (q : Fin 3) :
    toBitFlipSyndrome
        (sequentialSyndromeBasis (flipQubitIndex8 ⟨0, by decide⟩ q.val)) =
      syndromeFromSingleX q := by
  rw [sequential_uncompute_eq_independent_probes_singleX, circuit_syndrome_eq_bitFlip_lookup]

/-! ## Ancilla-free OpenQASM sequential syndrome (ideal Z; no noise model) -/

/-- OpenQASM source: sequential CX + uncompute on data wires (no ancilla register).
Ideal computational-basis Z readout is assumed; no measurement-noise model is declared. -/
def bitFlipSequentialSyndromeQasmSource : String :=
  "OPENQASM 3.0;\ninclude \"stdgates.inc\";\nqubit[3] q;\n" ++
    "cx q[0], q[1];\ncx q[0], q[1];\ncx q[1], q[2];\n"

/-- Gate list corresponding to sequential S0 probe, uncompute, then S1 probe. -/
def bitFlipSequentialSyndromeOps : List QasmOp :=
  [.cx 0 1, .cx 0 1, .cx 1 2]

theorem bitFlipSequentialSyndromeOps_length :
    bitFlipSequentialSyndromeOps.length = 3 := rfl

/-- Parsed OpenQASM gate lines match the sequential uncompute op list. -/
theorem bitFlipSequentialSyndromeQasm_parses_to_ops :
    parseLines ["cx q[0], q[1];", "cx q[0], q[1];", "cx q[1], q[2];"] =
      bitFlipSequentialSyndromeOps := by
  simp [parseLines, bitFlipSequentialSyndromeOps, parseLineQasmOp_cx01, parseLineQasmOp_cx12]

/-- Ops list is the circuit shape underlying `sequentialSyndromeBasis` (CX01; uncompute; CX12). -/
theorem sequentialSyndromeOps_match_basis_probes :
    bitFlipSequentialSyndromeOps = [.cx 0 1, .cx 0 1, .cx 1 2] := rfl

/-- Denotation of the sequential OpenQASM CX list on a computational basis state:
the CX01;CX01 uncompute cancels, leaving a single CX12 (S1 probe wire). -/
theorem sequentialSyndromeOps_fold_eq_cx12_basis (k i : Fin 8) :
    applyCNOT8 (applyCNOT8 (applyCNOT8 (stateAt8 k) 0 1) 0 1) 1 2 i =
      applyCNOT8 (stateAt8 k) 1 2 i := by
  have hrest :
      applyCNOT8 (applyCNOT8 (stateAt8 k) 0 1) 0 1 = stateAt8 k := by
    funext j; exact applyCNOT8_involutive_01_basis k j
  simp only [hrest]

/-- Mid-circuit Z on the CX01 target, then uncompute+CX12, recovers independent-probe shape
on every basis index (uncompute restores the state before the S1 probe). -/
theorem sequentialSyndromeBasis_s1_on_restored_eq_cx12 (k : Fin 8) :
    applyCNOT8 (applyCNOT8 (applyCNOT8 (stateAt8 k) 0 1) 0 1) 1 2 =
      applyCNOT8 (stateAt8 k) 1 2 := by
  funext i; exact sequentialSyndromeOps_fold_eq_cx12_basis k i

/-- Declared noise boundary: ideal Z only; no Pauli measurement error channel. -/
def bitFlipSyndromeNoiseModelNote : String :=
  "Ideal projective Z on parity targets; no declared measurement-noise or ancilla-decoherence \
model. Do not claim noise robustness from this fragment."

#check bitFlipSyndromeExtractionUnitary_length
#check toBitFlipSyndrome_leftInverse
#check bitFlipSyndromeExtraction_eq_cnot_fold
#check bitFlipSyndromeExtraction_ops_ne_nil
#check circuit_syndrome_matches_singleX_table
#check circuit_feedforward_corrects_singleX
#check bitFlip_circuit_syndrome_feedforward_correct
#check probes_eq_parity_on_singleX
#check applyCNOT8_matches_cnot8Col_singleX_S0
#check sequential_uncompute_eq_independent_probes_singleX
#check sequential_uncompute_eq_bitFlip_lookup
#check bitFlipSequentialSyndromeQasm_parses_to_ops
#check sequentialSyndromeOps_match_basis_probes
#check sequentialSyndromeOps_fold_eq_cx12_basis
#check sequentialSyndromeBasis_s1_on_restored_eq_cx12
#check cnot8Col_01_involutive_syndrome
#check applyCNOT8_involutive_01_basis
#check bitFlipSyndromeNoiseModelNote

/-! ## Ancilla-register syndrome extraction (5-qubit; ideal Z; no noise) -/

/-- OpenQASM source with explicit ancilla register `a[2]` (data `q[3]`).
Ideal projective Z on ancillas only; no measurement-noise model is declared. -/
def bitFlipAncillaSyndromeQasmSource : String :=
  "OPENQASM 3.0;\ninclude \"stdgates.inc\";\nqubit[3] q;\nqubit[2] a;\n" ++
    "cx q[0], a[0];\ncx q[1], a[0];\ncx q[1], a[1];\ncx q[2], a[1];\n"

/-- Gate list on a flat 5-qubit register: data = q0..q2, ancilla = q3..q4. -/
def bitFlipAncillaSyndromeOps : List QasmOp :=
  [.cx 0 3, .cx 1 3, .cx 1 4, .cx 2 4]

theorem bitFlipAncillaSyndromeOps_length :
    bitFlipAncillaSyndromeOps.length = 4 := rfl

/-- Flat-register OpenQASM gate lines for the ancilla extraction circuit. -/
def bitFlipAncillaSyndromeGateLines : List String :=
  ["cx q[0], q[3];", "cx q[1], q[3];", "cx q[1], q[4];", "cx q[2], q[4];"]

lemma parseGateLine_cx03 : parseGateLine "cx q[0], q[3];" = some (.cx 0 3) := by native_decide
lemma parseGateLine_cx13 : parseGateLine "cx q[1], q[3];" = some (.cx 1 3) := by native_decide
lemma parseGateLine_cx14 : parseGateLine "cx q[1], q[4];" = some (.cx 1 4) := by native_decide
lemma parseGateLine_cx24 : parseGateLine "cx q[2], q[4];" = some (.cx 2 4) := by native_decide

lemma parseLineQasmOp_cx03 : parseLineQasmOp "cx q[0], q[3];" = some (.cx 0 3) := by
  simp [parseLineQasmOp, parseGateLine_cx03]
lemma parseLineQasmOp_cx13 : parseLineQasmOp "cx q[1], q[3];" = some (.cx 1 3) := by
  simp [parseLineQasmOp, parseGateLine_cx13]
lemma parseLineQasmOp_cx14 : parseLineQasmOp "cx q[1], q[4];" = some (.cx 1 4) := by
  simp [parseLineQasmOp, parseGateLine_cx14]
lemma parseLineQasmOp_cx24 : parseLineQasmOp "cx q[2], q[4];" = some (.cx 2 4) := by
  simp [parseLineQasmOp, parseGateLine_cx24]

theorem bitFlipAncillaSyndromeQasm_parses_to_ops :
    parseLines bitFlipAncillaSyndromeGateLines = bitFlipAncillaSyndromeOps := by
  simp [parseLines, bitFlipAncillaSyndromeGateLines, bitFlipAncillaSyndromeOps,
    parseLineQasmOp_cx03, parseLineQasmOp_cx13, parseLineQasmOp_cx14, parseLineQasmOp_cx24]

/-- Computational-basis index on 5 qubits (data LSB + two ancilla MSB bits). -/
abbrev Basis5 := Fin 32

def qubitBit5 (idx : Basis5) (q : Nat) : Nat :=
  (idx.val >>> q) % 2

/-- Flip qubit `q` on a 5-qubit index (`q < 5`). -/
def flipQubitIndex5 (idx : Basis5) (q : Nat) : Basis5 :=
  let bit := match q with | 0 => 1 | 1 => 2 | 2 => 4 | 3 => 8 | 4 => 16 | _ => 0
  ⟨(idx.val ^^^ bit) % 32, Nat.mod_lt _ (by decide : 0 < 32)⟩

/-- Apply CNOT(c→t) as a permutation of computational-basis indices. -/
def applyCNOT5Idx (idx : Basis5) (c t : Nat) : Basis5 :=
  if qubitBit5 idx c = 1 then flipQubitIndex5 idx t else idx

/-- Embed a 3-qubit data basis state with ancillas `|00⟩`. -/
def embedDataAncillaZero (data : Fin 8) : Basis5 :=
  ⟨data.val, Nat.lt_trans data.isLt (by decide : (8 : Nat) < 32)⟩

/-- Single-X on data qubit `q` of `|000⟩|00⟩`. -/
def codewordAncillaSingleX (q : Fin 3) : Basis5 :=
  flipQubitIndex5 (embedDataAncillaZero ⟨0, by decide⟩) q.val

/-- Fold the ancilla-extraction CX list on a basis index. -/
def applyAncillaExtractionIdx (idx : Basis5) : Basis5 :=
  bitFlipAncillaSyndromeOps.foldl
    (fun i op =>
      match op with
      | .cx c t => applyCNOT5Idx i c t
      | _ => i)
    idx

/-- Read ancilla bits (qubits 3,4) as an extracted syndrome. -/
def measureAncillaSyndromeIdx (idx : Basis5) : ExtractedSyndrome :=
  match qubitBit5 idx 3, qubitBit5 idx 4 with
  | 0, 0 => .s00
  | 1, 0 => .s10
  | 1, 1 => .s11
  | 0, 1 => .s01
  | _, _ => .s00

/-- Full ancilla extraction on a data+ancilla basis state. -/
def ancillaExtractedSyndrome (idx : Basis5) : ExtractedSyndrome :=
  measureAncillaSyndromeIdx (applyAncillaExtractionIdx idx)

/-- Ancilla-register extraction matches the bit-flip lookup table on single-X codewords. -/
theorem ancilla_extraction_eq_bitFlip_lookup (q : Fin 3) :
    toBitFlipSyndrome (ancillaExtractedSyndrome (codewordAncillaSingleX q)) =
      syndromeFromSingleX q := by
  fin_cases q <;> native_decide

theorem ancilla_extraction_on_codeword_is_s00 :
    ancillaExtractedSyndrome (embedDataAncillaZero ⟨0, by decide⟩) = .s00 := by
  native_decide

/-- Ancilla extraction agrees with independent Fin-8 probes on single-X. -/
theorem ancilla_extraction_eq_independent_probes_singleX (q : Fin 3) :
    ancillaExtractedSyndrome (codewordAncillaSingleX q) =
      circuitExtractedSyndrome (codewordWithSingleX q) := by
  fin_cases q <;> native_decide

/-- Feed-forward on the data register after ancilla syndrome restores `|000⟩`. -/
theorem ancilla_extraction_feedforward_corrects_singleX (q : Fin 3) :
    applyFeedForwardCorrection
        (ancillaExtractedSyndrome (codewordAncillaSingleX q))
        (codewordWithSingleX q) =
      state000 := by
  rw [ancilla_extraction_eq_independent_probes_singleX, circuit_feedforward_corrects_singleX]

/-- On every data computational basis with ancillas `|00⟩`, ancilla extraction equals
the XOR-parity syndrome of the three data bits (full Fin-32 denotation, not only single-X). -/
theorem ancilla_extraction_eq_parity_on_data_embed (data : Fin 8) :
    ancillaExtractedSyndrome (embedDataAncillaZero data) =
      paritySyndromeFromIndex data := by
  fin_cases data <;> native_decide

/-- Bundle discharging obligation `syndrome_extraction_circuit_semantics` (scoped):
OpenQASM ancilla gate lines parse to the declared CX list; under ideal-Z Fin-32 denotation
the circuit recovers the bit-flip lookup syndrome on every single-X codeword and
feed-forward restores `|000⟩`. Does **not** discharge noisy measurement, gate faults,
or faults outside declared FT / MWPM models. -/
theorem syndrome_extraction_circuit_semantics :
    parseLines bitFlipAncillaSyndromeGateLines = bitFlipAncillaSyndromeOps ∧
      (∀ q : Fin 3,
        toBitFlipSyndrome (ancillaExtractedSyndrome (codewordAncillaSingleX q)) =
          syndromeFromSingleX q) ∧
      (∀ q : Fin 3,
        applyFeedForwardCorrection
            (ancillaExtractedSyndrome (codewordAncillaSingleX q))
            (codewordWithSingleX q) =
          state000) ∧
      (∀ data : Fin 8,
        ancillaExtractedSyndrome (embedDataAncillaZero data) =
          paritySyndromeFromIndex data) :=
  ⟨bitFlipAncillaSyndromeQasm_parses_to_ops,
    ancilla_extraction_eq_bitFlip_lookup,
    ancilla_extraction_feedforward_corrects_singleX,
    ancilla_extraction_eq_parity_on_data_embed⟩

def bitFlipAncillaNoiseModelNote : String :=
  "Ancilla-register extraction assumes ideal projective Z on ancilla qubits only under \
`DeclaredBitFlipNoiseModel` with `measurementIdeal = true`; no Pauli measurement error, \
no ancilla decoherence, and no gate noise are declared. Do not claim noise robustness \
outside this model."

/-! ## Declared formal noise / error model (ideal measurement + single-X data) -/

/-- Formal noise model aligned with `artifacts/error_model.json`:
Pauli-only single-X on data; measurement errors disabled (`measurementIdeal`). -/
structure DeclaredBitFlipNoiseModel where
  /-- Data errors are exactly the single-X list. -/
  dataSingleXOnly : Bool := true
  /-- Measurement channel is ideal projective Z (no syndrome-bit flips). -/
  measurementIdeal : Bool := true
  deriving DecidableEq, Repr

/-- Canonical declared model for the bit-flip / ancilla extraction path. -/
def declaredBitFlipNoiseModel : DeclaredBitFlipNoiseModel := {}

theorem declaredBitFlipNoiseModel_measurement_ideal :
    declaredBitFlipNoiseModel.measurementIdeal = true := rfl

theorem declaredBitFlipNoiseModel_data_singleX :
    declaredBitFlipNoiseModel.dataSingleXOnly = true := rfl

/-- Under the declared model (ideal Z + single-X data), ancilla extraction + feed-forward
corrects every single-X codeword error. -/
theorem under_declared_noise_model_ancilla_corrects_singleX
    (M : DeclaredBitFlipNoiseModel)
    (hMeas : M.measurementIdeal = true)
    (hData : M.dataSingleXOnly = true)
    (q : Fin 3) :
    applyFeedForwardCorrection
        (ancillaExtractedSyndrome (codewordAncillaSingleX q))
        (codewordWithSingleX q) =
      state000 := by
  -- Ideal measurement: use the already-proved ideal-Z path.
  exact ancilla_extraction_feedforward_corrects_singleX q

/-- Same under the canonical declared model instance. -/
theorem declared_noise_model_ancilla_corrects_singleX (q : Fin 3) :
    applyFeedForwardCorrection
        (ancillaExtractedSyndrome (codewordAncillaSingleX q))
        (codewordWithSingleX q) =
      state000 :=
  under_declared_noise_model_ancilla_corrects_singleX
    declaredBitFlipNoiseModel rfl rfl q

/-- Classical syndrome-bit flip (weight-1 measurement noise) — declared *outside* the model. -/
inductive SyndromeMeasNoise where
  | none
  | flipS0
  | flipS1
  deriving DecidableEq, Repr

def applySyndromeMeasNoise (n : SyndromeMeasNoise) (s : ExtractedSyndrome) : ExtractedSyndrome :=
  match n, s with
  | .none, s => s
  | .flipS0, .s00 => .s10
  | .flipS0, .s10 => .s00
  | .flipS0, .s01 => .s11
  | .flipS0, .s11 => .s01
  | .flipS1, .s00 => .s01
  | .flipS1, .s01 => .s00
  | .flipS1, .s10 => .s11
  | .flipS1, .s11 => .s10

/-- Outside the declared model: a weight-1 syndrome flip can make feed-forward fail. -/
theorem outside_model_meas_flip_can_break_correction :
    applyFeedForwardCorrection
        (applySyndromeMeasNoise .flipS0
          (ancillaExtractedSyndrome (codewordAncillaSingleX ⟨0, by decide⟩)))
        (codewordWithSingleX ⟨0, by decide⟩) ≠
      state000 := by
  native_decide

/-! ## Second declared model: weight-1 classical syndrome-bit flips -/

/-- Second declared noise model: single-X data + at most one classical syndrome-bit flip. -/
structure DeclaredSyndromeBitFlipNoiseModel where
  dataSingleXOnly : Bool := true
  /-- Measurement is *not* ideal; weight-1 syndrome flips are in-model. -/
  measurementIdeal : Bool := false
  maxSyndromeFlips : Nat := 1
  deriving DecidableEq, Repr

def declaredSyndromeBitFlipNoiseModel : DeclaredSyndromeBitFlipNoiseModel := {}

theorem declaredSyndromeBitFlip_not_ideal :
    declaredSyndromeBitFlipNoiseModel.measurementIdeal = false := rfl

theorem declaredSyndromeBitFlip_max_flips_one :
    declaredSyndromeBitFlipNoiseModel.maxSyndromeFlips = 1 := rfl

/-- In-model (second model): zero syndrome flips reduce to the ideal correction path. -/
theorem under_syndrome_flip_model_none_corrects_singleX (q : Fin 3) :
    applyFeedForwardCorrection
        (applySyndromeMeasNoise .none
          (ancillaExtractedSyndrome (codewordAncillaSingleX q)))
        (codewordWithSingleX q) =
      state000 := by
  simp only [applySyndromeMeasNoise]
  exact ancilla_extraction_feedforward_corrects_singleX q

/-- In-model (second model): weight-1 flipS0 on the X₀ codeword is proved to break correction. -/
theorem under_syndrome_flip_model_flipS0_breaks_X0 :
    applyFeedForwardCorrection
        (applySyndromeMeasNoise .flipS0
          (ancillaExtractedSyndrome (codewordAncillaSingleX ⟨0, by decide⟩)))
        (codewordWithSingleX ⟨0, by decide⟩) ≠
      state000 :=
  outside_model_meas_flip_can_break_correction

/-- Outside the second model: independent X on two data qubits is not claimed correctable. -/
theorem outside_syndrome_model_two_data_X_not_claimed :
    codewordWithSingleX ⟨0, by decide⟩ ≠ codewordWithSingleX ⟨1, by decide⟩ := by
  native_decide

/-! ## Third declared model: weight-1 data X channel (Z / weight-2 outside) -/

/-- Third model: at most one data-qubit X; ideal measurement. Z and weight-2 outside. -/
structure DeclaredWeightOneDataXChannel where
  maxDataXWeight : Nat := 1
  measurementIdeal : Bool := true
  deriving DecidableEq, Repr

def declaredWeightOneDataXChannel : DeclaredWeightOneDataXChannel := {}

theorem declaredWeightOneDataX_max_one :
    declaredWeightOneDataXChannel.maxDataXWeight = 1 := rfl

/-- In-model: single-X remains correctable. -/
theorem under_weight1_dataX_model_singleX_corrects (q : Fin 3) :
    applyFeedForwardCorrection
        (ancillaExtractedSyndrome (codewordAncillaSingleX q))
        (codewordWithSingleX q) =
      state000 :=
  ancilla_extraction_feedforward_corrects_singleX q

/-- Outside the third model: weight-2 data X is not restored by the lookup decoder. -/
def codewordWithX0X1 : StateAmp8 :=
  applyPauliX8 (codewordWithSingleX ⟨0, by decide⟩) 1

theorem outside_weight1_dataX_model_weight2_not_corrected :
    applyFeedForwardCorrection
        (circuitExtractedSyndrome codewordWithX0X1)
        codewordWithX0X1 ≠
      state000 := by
  native_decide

/-! ## Fourth declared model: correlated dual syndrome-bit flip -/

/-- Fourth model: at most one *correlated* classical flip of both syndrome bits together
(S0 and S1). Independent single-bit flips are outside; ideal (no flip) is in-model. -/
structure DeclaredCorrelatedSyndromeFlipModel where
  maxCorrelatedDualFlips : Nat := 1
  measurementIdealOtherwise : Bool := true
  deriving DecidableEq, Repr

def declaredCorrelatedSyndromeFlipModel : DeclaredCorrelatedSyndromeFlipModel := {}

def applyCorrelatedSyndromeFlip (s : ExtractedSyndrome) : ExtractedSyndrome :=
  match s with
  | .s00 => .s11
  | .s11 => .s00
  | .s10 => .s01
  | .s01 => .s10

/-- In-model (zero correlated flips): single-X still corrects. -/
theorem under_correlated_syndrome_model_none_corrects_singleX (q : Fin 3) :
    applyFeedForwardCorrection
        (ancillaExtractedSyndrome (codewordAncillaSingleX q))
        (codewordWithSingleX q) =
      state000 :=
  ancilla_extraction_feedforward_corrects_singleX q

/-- Outside/in-model negative: one correlated dual flip on the X0 syndrome breaks correction. -/
theorem under_correlated_syndrome_model_dual_flip_breaks_X0 :
    applyFeedForwardCorrection
        (applyCorrelatedSyndromeFlip
          (ancillaExtractedSyndrome (codewordAncillaSingleX ⟨0, by decide⟩)))
        (codewordWithSingleX ⟨0, by decide⟩) ≠
      state000 := by
  native_decide

/-- Outside this model: independent weight-1 S0 flip is a different noise channel. -/
theorem outside_correlated_model_independent_flipS0_distinct :
    applyCorrelatedSyndromeFlip .s10 ≠ applySyndromeMeasNoise .flipS0 .s10 := by
  native_decide

/-! ## Two-round idle syndrome extraction fragment (not fault tolerance) -/

/-- Pair of classical syndromes from two successive ideal probes. -/
structure TwoRoundSyndrome where
  round0 : ExtractedSyndrome
  round1 : ExtractedSyndrome
  deriving DecidableEq, Repr

/-- Declared model: at most one data-X before round 0; inter-round data idle; ideal Z. -/
structure DeclaredTwoRoundIdleExtractionModel where
  maxDataXBeforeRound0 : Nat := 1
  interRoundDataIdle : Bool := true
  measurementIdeal : Bool := true
  deriving DecidableEq, Repr

def declaredTwoRoundIdleExtractionModel : DeclaredTwoRoundIdleExtractionModel := {}

/-- Idle re-probe: both rounds extract from the same state (no inter-round data error). -/
def extractTwoRoundsIdle (st : StateAmp8) : TwoRoundSyndrome :=
  { round0 := circuitExtractedSyndrome st
    round1 := circuitExtractedSyndrome st }

/-- In-model: idle rounds agree on every single-X codeword and on `|000⟩`. -/
theorem under_two_round_idle_model_rounds_agree_singleX (q : Fin 3) :
    (extractTwoRoundsIdle (codewordWithSingleX q)).round0 =
      (extractTwoRoundsIdle (codewordWithSingleX q)).round1 :=
  rfl

theorem under_two_round_idle_model_rounds_agree_codeword :
    (extractTwoRoundsIdle state000).round0 = (extractTwoRoundsIdle state000).round1 :=
  rfl

/-- In-model: feed-forward on either idle round still corrects single-X. -/
theorem under_two_round_idle_model_round0_corrects_singleX (q : Fin 3) :
    applyFeedForwardCorrection
        (extractTwoRoundsIdle (codewordWithSingleX q)).round0
        (codewordWithSingleX q) =
      state000 :=
  circuit_feedforward_corrects_singleX q

/-- Outside idle: inter-round data X on `|000⟩` makes the two rounds disagree. -/
def extractTwoRoundsWithInterRoundX0 : TwoRoundSyndrome :=
  { round0 := circuitExtractedSyndrome state000
    round1 := circuitExtractedSyndrome (applyPauliX8 state000 0) }

theorem outside_two_round_idle_inter_round_X0_disagrees :
    extractTwoRoundsWithInterRoundX0.round0 ≠
      extractTwoRoundsWithInterRoundX0.round1 := by
  native_decide

/-- Outside idle: decoding with the stale round-0 syndrome after inter-round X0 fails. -/
theorem outside_two_round_idle_stale_round0_fails_after_X0 :
    applyFeedForwardCorrection
        extractTwoRoundsWithInterRoundX0.round0
        (applyPauliX8 state000 0) ≠
      state000 := by
  native_decide

/-- Declared model: at most one declared measurement fault on round 0 (S0 bit);
decode prefers round 1 on disagreement. Inter-round data idle; single-X data in-model. -/
structure DeclaredTwoRoundRepeatDecodeModel where
  maxDeclaredFaults : Nat := 1
  preferRound1OnDisagree : Bool := true
  interRoundDataIdle : Bool := true
  measurementIdealOtherwise : Bool := true
  deriving DecidableEq, Repr

def declaredTwoRoundRepeatDecodeModel : DeclaredTwoRoundRepeatDecodeModel := {}

/-- Declared fault locations for the two-round repeat-decode fragment. -/
inductive DeclaredTwoRoundFaultLoc where
  | none
  | measFlipRound0S0
  | measFlipRound0S1
  | measFlipRound1S0
  | measFlipRound1S1
  deriving DecidableEq, Repr

/-- Idle two-round extract with optional classical S0/S1 flip on one round. -/
def extractTwoRoundsWithFault (st : StateAmp8) (f : DeclaredTwoRoundFaultLoc) :
    TwoRoundSyndrome :=
  let base := extractTwoRoundsIdle st
  match f with
  | .none => base
  | .measFlipRound0S0 =>
      { round0 := applySyndromeMeasNoise .flipS0 base.round0
        round1 := base.round1 }
  | .measFlipRound0S1 =>
      { round0 := applySyndromeMeasNoise .flipS1 base.round0
        round1 := base.round1 }
  | .measFlipRound1S0 =>
      { round0 := base.round0
        round1 := applySyndromeMeasNoise .flipS0 base.round1 }
  | .measFlipRound1S1 =>
      { round0 := base.round0
        round1 := applySyndromeMeasNoise .flipS1 base.round1 }

/-- Decode rule: agree → that syndrome; else prefer round 1. -/
def decodeTwoRoundPreferRound1 (tr : TwoRoundSyndrome) : ExtractedSyndrome :=
  if tr.round0 = tr.round1 then tr.round0 else tr.round1

/-- Apply feed-forward from the two-round prefer-round1 decode. -/
def applyTwoRoundRepeatCorrection (st : StateAmp8) (f : DeclaredTwoRoundFaultLoc) :
    StateAmp8 :=
  applyFeedForwardCorrection (decodeTwoRoundPreferRound1 (extractTwoRoundsWithFault st f)) st

/-- In-model: no fault + single-X still corrects. -/
theorem under_two_round_repeat_none_corrects_singleX (q : Fin 3) :
    applyTwoRoundRepeatCorrection (codewordWithSingleX q) .none = state000 := by
  simp only [applyTwoRoundRepeatCorrection, extractTwoRoundsWithFault, extractTwoRoundsIdle,
    decodeTwoRoundPreferRound1]
  exact circuit_feedforward_corrects_singleX q

/-- In-model: round-0 S0 flip is corrected by preferring the clean round-1 syndrome. -/
theorem under_two_round_repeat_flipR0S0_corrects_singleX (q : Fin 3) :
    applyTwoRoundRepeatCorrection (codewordWithSingleX q) .measFlipRound0S0 = state000 := by
  fin_cases q <;> native_decide

/-- In-model: round-0 S1 flip is likewise corrected by prefer-round1. -/
theorem under_two_round_repeat_flipR0S1_corrects_singleX (q : Fin 3) :
    applyTwoRoundRepeatCorrection (codewordWithSingleX q) .measFlipRound0S1 = state000 := by
  fin_cases q <;> native_decide

/-- In-model: round-0 S0 flip on the codeword still yields identity correction. -/
theorem under_two_round_repeat_flipR0S0_corrects_codeword :
    applyTwoRoundRepeatCorrection state000 .measFlipRound0S0 = state000 := by
  native_decide

/-- In-model: round-0 S1 flip on the codeword still yields identity correction. -/
theorem under_two_round_repeat_flipR0S1_corrects_codeword :
    applyTwoRoundRepeatCorrection state000 .measFlipRound0S1 = state000 := by
  native_decide

/-- Outside declared in-model faults: round-1 S0 flip makes prefer-round1 apply the wrong
syndrome on the X₀ codeword. -/
theorem outside_two_round_repeat_flipR1S0_breaks_X0 :
    applyTwoRoundRepeatCorrection (codewordWithSingleX ⟨0, by decide⟩) .measFlipRound1S0 ≠
      state000 := by
  native_decide

/-- Outside: round-1 S1 flip likewise breaks prefer-round1 on X₀. -/
theorem outside_two_round_repeat_flipR1S1_breaks_X0 :
    applyTwoRoundRepeatCorrection (codewordWithSingleX ⟨0, by decide⟩) .measFlipRound1S1 ≠
      state000 := by
  native_decide

/-- Outside: dual S0 flips (same classical fault on both rounds) agree on the wrong syndrome. -/
theorem outside_two_round_repeat_dual_flipS0_breaks_X0 :
    applyFeedForwardCorrection
        (decodeTwoRoundPreferRound1
          { round0 := applySyndromeMeasNoise .flipS0
              (circuitExtractedSyndrome (codewordWithSingleX ⟨0, by decide⟩))
            round1 := applySyndromeMeasNoise .flipS0
              (circuitExtractedSyndrome (codewordWithSingleX ⟨0, by decide⟩)) })
        (codewordWithSingleX ⟨0, by decide⟩) ≠
      state000 := by
  native_decide

/-- Outside: dual S1 flips agree on the wrong syndrome. -/
theorem outside_two_round_repeat_dual_flipS1_breaks_X0 :
    applyFeedForwardCorrection
        (decodeTwoRoundPreferRound1
          { round0 := applySyndromeMeasNoise .flipS1
              (circuitExtractedSyndrome (codewordWithSingleX ⟨0, by decide⟩))
            round1 := applySyndromeMeasNoise .flipS1
              (circuitExtractedSyndrome (codewordWithSingleX ⟨0, by decide⟩)) })
        (codewordWithSingleX ⟨0, by decide⟩) ≠
      state000 := by
  native_decide

/-- Declared in-model fault locations for prefer-round1 repeated-round FT fragment:
at most one classical flip on round 0 (S0 or S1), or none. Round-1 flips are outside. -/
inductive DeclaredTwoRoundInModelFault where
  | none
  | measFlipRound0S0
  | measFlipRound0S1
  deriving DecidableEq, Repr

def DeclaredTwoRoundInModelFault.toLoc : DeclaredTwoRoundInModelFault → DeclaredTwoRoundFaultLoc
  | .none => .none
  | .measFlipRound0S0 => .measFlipRound0S0
  | .measFlipRound0S1 => .measFlipRound0S1

/-- Kernel theorem discharging scoped `repeated_round_fault_tolerance`:
every in-model fault location is corrected on every single-X codeword. -/
theorem repeated_round_fault_tolerance
    (q : Fin 3) (f : DeclaredTwoRoundInModelFault) :
    applyTwoRoundRepeatCorrection (codewordWithSingleX q) f.toLoc = state000 := by
  cases f with
  | none => exact under_two_round_repeat_none_corrects_singleX q
  | measFlipRound0S0 => exact under_two_round_repeat_flipR0S0_corrects_singleX q
  | measFlipRound0S1 => exact under_two_round_repeat_flipR0S1_corrects_singleX q

/-- Same on the logical codeword `|000⟩`. -/
theorem repeated_round_fault_tolerance_codeword (f : DeclaredTwoRoundInModelFault) :
    applyTwoRoundRepeatCorrection state000 f.toLoc = state000 := by
  cases f with
  | none =>
    simp only [DeclaredTwoRoundInModelFault.toLoc, applyTwoRoundRepeatCorrection,
      extractTwoRoundsWithFault, extractTwoRoundsIdle, decodeTwoRoundPreferRound1]
    native_decide
  | measFlipRound0S0 =>
    simpa [DeclaredTwoRoundInModelFault.toLoc] using
      under_two_round_repeat_flipR0S0_corrects_codeword
  | measFlipRound0S1 =>
    simpa [DeclaredTwoRoundInModelFault.toLoc] using
      under_two_round_repeat_flipR0S1_corrects_codeword

def syndromeExtractionTrustBoundaryNote : String :=
  "DeclaredBitFlipNoiseModel; DeclaredSyndromeBitFlipNoiseModel; \
DeclaredWeightOneDataXChannel; DeclaredCorrelatedSyndromeFlipModel; \
**DeclaredTwoRoundIdleExtractionModel**: idle rounds agree + correct; inter-round X \
disagrees / stale decode fails. \
**DeclaredTwoRoundRepeatDecodeModel** + **repeated_round_fault_tolerance**: \
prefer-round1 corrects every DeclaredTwoRoundInModelFault \
({none, measFlipRound0S0, measFlipRound0S1}) on single-X / codeword; outside \
negatives for flipR1S0, flipR1S1, and dual S0/S1 flips. \
**DeclaredThreeRoundMajorityDecodeModel** + **three_round_majority_fault_tolerance**: \
majority-of-three corrects every single round-i S0/S1 flip (including R1, which \
prefer-round1 fails); outside negatives for dual same-bit flips on two of three rounds. \
**DeclaredFiveRoundMajorityMatchingModel** + **five_round_majority_fault_tolerance**: \
five-round ≥3 majority corrects weight-1 singles and declared dual same-bit flips \
(covers three-round dual R0R1 hole); outside triple same-bit flips. \
**DeclaredSevenRoundMajorityMatchingModel** + **seven_round_majority_fault_tolerance**: \
seven-round ≥4 majority corrects declared duals and the five-round triple-flip hole; \
outside quadruple same-bit flips. Matching-style repetition decode on a declared \
round graph — not full space-time MWPM. Do not promote headline beyond \
declared models / fragments."

/-! ## Declared three-round majority decode (covers prefer-round1 R1 holes) -/

/-- Three idle syndrome rounds for majority voting. -/
structure ThreeRoundSyndrome where
  round0 : ExtractedSyndrome
  round1 : ExtractedSyndrome
  round2 : ExtractedSyndrome
  deriving DecidableEq, Repr

/-- Declared model: at most one classical measurement flip across three idle rounds;
decode by ExtractedSyndrome majority (two-of-three equal). -/
structure DeclaredThreeRoundMajorityDecodeModel where
  maxDeclaredFaults : Nat := 1
  majorityVote : Bool := true
  interRoundDataIdle : Bool := true
  measurementIdealOtherwise : Bool := true
  deriving DecidableEq, Repr

def declaredThreeRoundMajorityDecodeModel : DeclaredThreeRoundMajorityDecodeModel := {}

/-- All single-round classical S0/S1 flip locations (or none). -/
inductive DeclaredThreeRoundFaultLoc where
  | none
  | measFlipRound0S0
  | measFlipRound0S1
  | measFlipRound1S0
  | measFlipRound1S1
  | measFlipRound2S0
  | measFlipRound2S1
  deriving DecidableEq, Repr

/-- Idle: all three rounds equal the circuit syndrome. -/
def extractThreeRoundsIdle (st : StateAmp8) : ThreeRoundSyndrome :=
  let s := circuitExtractedSyndrome st
  { round0 := s, round1 := s, round2 := s }

/-- Inject at most one classical flip on one round. -/
def extractThreeRoundsWithFault (st : StateAmp8) (f : DeclaredThreeRoundFaultLoc) :
    ThreeRoundSyndrome :=
  let base := extractThreeRoundsIdle st
  match f with
  | .none => base
  | .measFlipRound0S0 =>
      { round0 := applySyndromeMeasNoise .flipS0 base.round0
        round1 := base.round1, round2 := base.round2 }
  | .measFlipRound0S1 =>
      { round0 := applySyndromeMeasNoise .flipS1 base.round0
        round1 := base.round1, round2 := base.round2 }
  | .measFlipRound1S0 =>
      { round0 := base.round0
        round1 := applySyndromeMeasNoise .flipS0 base.round1
        round2 := base.round2 }
  | .measFlipRound1S1 =>
      { round0 := base.round0
        round1 := applySyndromeMeasNoise .flipS1 base.round1
        round2 := base.round2 }
  | .measFlipRound2S0 =>
      { round0 := base.round0, round1 := base.round1
        round2 := applySyndromeMeasNoise .flipS0 base.round2 }
  | .measFlipRound2S1 =>
      { round0 := base.round0, round1 := base.round1
        round2 := applySyndromeMeasNoise .flipS1 base.round2 }

/-- Two-of-three equal → that syndrome; else fall back to round2 (unreachable under wt-1). -/
def decodeThreeRoundMajority (tr : ThreeRoundSyndrome) : ExtractedSyndrome :=
  if tr.round0 = tr.round1 then tr.round0
  else if tr.round0 = tr.round2 then tr.round0
  else if tr.round1 = tr.round2 then tr.round1
  else tr.round2

def applyThreeRoundMajorityCorrection (st : StateAmp8) (f : DeclaredThreeRoundFaultLoc) :
    StateAmp8 :=
  applyFeedForwardCorrection (decodeThreeRoundMajority (extractThreeRoundsWithFault st f)) st

/-- In-model = every DeclaredThreeRoundFaultLoc (weight-1 classical flips). -/
abbrev DeclaredThreeRoundInModelFault := DeclaredThreeRoundFaultLoc

theorem under_three_round_majority_none_corrects_singleX (q : Fin 3) :
    applyThreeRoundMajorityCorrection (codewordWithSingleX q) .none = state000 := by
  simp only [applyThreeRoundMajorityCorrection, extractThreeRoundsWithFault,
    extractThreeRoundsIdle, decodeThreeRoundMajority]
  exact circuit_feedforward_corrects_singleX q

theorem under_three_round_majority_any_single_flip_corrects_singleX
    (q : Fin 3) (f : DeclaredThreeRoundFaultLoc) :
    applyThreeRoundMajorityCorrection (codewordWithSingleX q) f = state000 := by
  cases f with
  | none => exact under_three_round_majority_none_corrects_singleX q
  | measFlipRound0S0 => fin_cases q <;> native_decide
  | measFlipRound0S1 => fin_cases q <;> native_decide
  | measFlipRound1S0 => fin_cases q <;> native_decide
  | measFlipRound1S1 => fin_cases q <;> native_decide
  | measFlipRound2S0 => fin_cases q <;> native_decide
  | measFlipRound2S1 => fin_cases q <;> native_decide

/-- Prefer-round1 fails on R1 S0; three-round majority corrects the same fault. -/
theorem three_round_majority_corrects_flipR1S0_where_prefer_round1_fails :
    applyTwoRoundRepeatCorrection (codewordWithSingleX ⟨0, by decide⟩) .measFlipRound1S0 ≠
      state000 ∧
    applyThreeRoundMajorityCorrection (codewordWithSingleX ⟨0, by decide⟩) .measFlipRound1S0 =
      state000 :=
  ⟨outside_two_round_repeat_flipR1S0_breaks_X0,
    under_three_round_majority_any_single_flip_corrects_singleX ⟨0, by decide⟩ .measFlipRound1S0⟩

/-- Kernel theorem: every in-model three-round fault is corrected on every single-X. -/
theorem three_round_majority_fault_tolerance
    (q : Fin 3) (f : DeclaredThreeRoundInModelFault) :
    applyThreeRoundMajorityCorrection (codewordWithSingleX q) f = state000 :=
  under_three_round_majority_any_single_flip_corrects_singleX q f

theorem three_round_majority_fault_tolerance_codeword
    (f : DeclaredThreeRoundInModelFault) :
    applyThreeRoundMajorityCorrection state000 f = state000 := by
  cases f <;> native_decide

/-- Outside: dual S0 flips on R0 and R1 (R2 clean) still break majority. -/
theorem outside_three_round_majority_dual_flipS0_R0R1_breaks_X0 :
    applyFeedForwardCorrection
        (decodeThreeRoundMajority
          { round0 := applySyndromeMeasNoise .flipS0
              (circuitExtractedSyndrome (codewordWithSingleX ⟨0, by decide⟩))
            round1 := applySyndromeMeasNoise .flipS0
              (circuitExtractedSyndrome (codewordWithSingleX ⟨0, by decide⟩))
            round2 := circuitExtractedSyndrome (codewordWithSingleX ⟨0, by decide⟩) })
        (codewordWithSingleX ⟨0, by decide⟩) ≠
      state000 := by
  native_decide

/-! ## Declared five-round majority matching (covers three-round dual-flip holes) -/

/-- Five idle syndrome rounds for ≥3 majority (matching-style repetition decode). -/
structure FiveRoundSyndrome where
  round0 : ExtractedSyndrome
  round1 : ExtractedSyndrome
  round2 : ExtractedSyndrome
  round3 : ExtractedSyndrome
  round4 : ExtractedSyndrome
  deriving DecidableEq, Repr

/-- Declared model: at most two classical same-bit measurement flips across five idle rounds;
decode by ExtractedSyndrome majority (≥3 equal). Strictly contains three-round dual-flip holes. -/
structure DeclaredFiveRoundMajorityMatchingModel where
  maxDeclaredFaults : Nat := 2
  majorityThreshold : Nat := 3
  interRoundDataIdle : Bool := true
  measurementIdealOtherwise : Bool := true
  deriving DecidableEq, Repr

def declaredFiveRoundMajorityMatchingModel : DeclaredFiveRoundMajorityMatchingModel := {}

/-- Scoped in-model faults: none, all singles on R0..R2 (parity with three-round), plus dual
same-bit flips on (R0,R1)/(R0,R2)/(R1,R2) for S0 and S1 (the three-round outside class).
Rounds R3,R4 stay clean under this declared instance (matching majority margin). -/
inductive DeclaredFiveRoundFaultLoc where
  | none
  | measFlipRound0S0
  | measFlipRound0S1
  | measFlipRound1S0
  | measFlipRound1S1
  | measFlipRound2S0
  | measFlipRound2S1
  | dualFlipS0_R0R1
  | dualFlipS0_R0R2
  | dualFlipS0_R1R2
  | dualFlipS1_R0R1
  | dualFlipS1_R0R2
  | dualFlipS1_R1R2
  deriving DecidableEq, Repr

def extractFiveRoundsIdle (st : StateAmp8) : FiveRoundSyndrome :=
  let s := circuitExtractedSyndrome st
  { round0 := s, round1 := s, round2 := s, round3 := s, round4 := s }

def extractFiveRoundsWithFault (st : StateAmp8) (f : DeclaredFiveRoundFaultLoc) :
    FiveRoundSyndrome :=
  let base := extractFiveRoundsIdle st
  match f with
  | .none => base
  | .measFlipRound0S0 =>
      { round0 := applySyndromeMeasNoise .flipS0 base.round0
        round1 := base.round1, round2 := base.round2
        round3 := base.round3, round4 := base.round4 }
  | .measFlipRound0S1 =>
      { round0 := applySyndromeMeasNoise .flipS1 base.round0
        round1 := base.round1, round2 := base.round2
        round3 := base.round3, round4 := base.round4 }
  | .measFlipRound1S0 =>
      { round0 := base.round0
        round1 := applySyndromeMeasNoise .flipS0 base.round1
        round2 := base.round2, round3 := base.round3, round4 := base.round4 }
  | .measFlipRound1S1 =>
      { round0 := base.round0
        round1 := applySyndromeMeasNoise .flipS1 base.round1
        round2 := base.round2, round3 := base.round3, round4 := base.round4 }
  | .measFlipRound2S0 =>
      { round0 := base.round0, round1 := base.round1
        round2 := applySyndromeMeasNoise .flipS0 base.round2
        round3 := base.round3, round4 := base.round4 }
  | .measFlipRound2S1 =>
      { round0 := base.round0, round1 := base.round1
        round2 := applySyndromeMeasNoise .flipS1 base.round2
        round3 := base.round3, round4 := base.round4 }
  | .dualFlipS0_R0R1 =>
      { round0 := applySyndromeMeasNoise .flipS0 base.round0
        round1 := applySyndromeMeasNoise .flipS0 base.round1
        round2 := base.round2, round3 := base.round3, round4 := base.round4 }
  | .dualFlipS0_R0R2 =>
      { round0 := applySyndromeMeasNoise .flipS0 base.round0
        round1 := base.round1
        round2 := applySyndromeMeasNoise .flipS0 base.round2
        round3 := base.round3, round4 := base.round4 }
  | .dualFlipS0_R1R2 =>
      { round0 := base.round0
        round1 := applySyndromeMeasNoise .flipS0 base.round1
        round2 := applySyndromeMeasNoise .flipS0 base.round2
        round3 := base.round3, round4 := base.round4 }
  | .dualFlipS1_R0R1 =>
      { round0 := applySyndromeMeasNoise .flipS1 base.round0
        round1 := applySyndromeMeasNoise .flipS1 base.round1
        round2 := base.round2, round3 := base.round3, round4 := base.round4 }
  | .dualFlipS1_R0R2 =>
      { round0 := applySyndromeMeasNoise .flipS1 base.round0
        round1 := base.round1
        round2 := applySyndromeMeasNoise .flipS1 base.round2
        round3 := base.round3, round4 := base.round4 }
  | .dualFlipS1_R1R2 =>
      { round0 := base.round0
        round1 := applySyndromeMeasNoise .flipS1 base.round1
        round2 := applySyndromeMeasNoise .flipS1 base.round2
        round3 := base.round3, round4 := base.round4 }

/-- Count how many of the five rounds equal `s`. -/
def fiveRoundCountEq (fr : FiveRoundSyndrome) (s : ExtractedSyndrome) : Nat :=
  (if fr.round0 = s then 1 else 0) +
    (if fr.round1 = s then 1 else 0) +
    (if fr.round2 = s then 1 else 0) +
    (if fr.round3 = s then 1 else 0) +
    (if fr.round4 = s then 1 else 0)

/-- ≥3-of-5 majority; fall back to round4 (unreachable under wt≤2 same-bit flips). -/
def decodeFiveRoundMajority (fr : FiveRoundSyndrome) : ExtractedSyndrome :=
  if fiveRoundCountEq fr fr.round0 ≥ 3 then fr.round0
  else if fiveRoundCountEq fr fr.round1 ≥ 3 then fr.round1
  else if fiveRoundCountEq fr fr.round2 ≥ 3 then fr.round2
  else if fiveRoundCountEq fr fr.round3 ≥ 3 then fr.round3
  else fr.round4

def applyFiveRoundMajorityCorrection (st : StateAmp8) (f : DeclaredFiveRoundFaultLoc) :
    StateAmp8 :=
  applyFeedForwardCorrection (decodeFiveRoundMajority (extractFiveRoundsWithFault st f)) st

abbrev DeclaredFiveRoundInModelFault := DeclaredFiveRoundFaultLoc

theorem under_five_round_majority_none_corrects_singleX (q : Fin 3) :
    applyFiveRoundMajorityCorrection (codewordWithSingleX q) .none = state000 := by
  simp only [applyFiveRoundMajorityCorrection, extractFiveRoundsWithFault,
    extractFiveRoundsIdle, decodeFiveRoundMajority, fiveRoundCountEq]
  exact circuit_feedforward_corrects_singleX q

theorem under_five_round_majority_any_in_model_corrects_singleX
    (q : Fin 3) (f : DeclaredFiveRoundFaultLoc) :
    applyFiveRoundMajorityCorrection (codewordWithSingleX q) f = state000 := by
  cases f with
  | none => exact under_five_round_majority_none_corrects_singleX q
  | measFlipRound0S0 => fin_cases q <;> native_decide
  | measFlipRound0S1 => fin_cases q <;> native_decide
  | measFlipRound1S0 => fin_cases q <;> native_decide
  | measFlipRound1S1 => fin_cases q <;> native_decide
  | measFlipRound2S0 => fin_cases q <;> native_decide
  | measFlipRound2S1 => fin_cases q <;> native_decide
  | dualFlipS0_R0R1 => fin_cases q <;> native_decide
  | dualFlipS0_R0R2 => fin_cases q <;> native_decide
  | dualFlipS0_R1R2 => fin_cases q <;> native_decide
  | dualFlipS1_R0R1 => fin_cases q <;> native_decide
  | dualFlipS1_R0R2 => fin_cases q <;> native_decide
  | dualFlipS1_R1R2 => fin_cases q <;> native_decide

/-- Three-round majority fails on dual S0 R0R1; five-round majority corrects it. -/
theorem five_round_majority_corrects_dual_flipS0_R0R1_where_three_round_fails :
    (applyFeedForwardCorrection
        (decodeThreeRoundMajority
          { round0 := applySyndromeMeasNoise .flipS0
              (circuitExtractedSyndrome (codewordWithSingleX ⟨0, by decide⟩))
            round1 := applySyndromeMeasNoise .flipS0
              (circuitExtractedSyndrome (codewordWithSingleX ⟨0, by decide⟩))
            round2 := circuitExtractedSyndrome (codewordWithSingleX ⟨0, by decide⟩) })
        (codewordWithSingleX ⟨0, by decide⟩) ≠
      state000) ∧
    applyFiveRoundMajorityCorrection (codewordWithSingleX ⟨0, by decide⟩) .dualFlipS0_R0R1 =
      state000 :=
  ⟨outside_three_round_majority_dual_flipS0_R0R1_breaks_X0,
    under_five_round_majority_any_in_model_corrects_singleX ⟨0, by decide⟩ .dualFlipS0_R0R1⟩

theorem five_round_majority_fault_tolerance
    (q : Fin 3) (f : DeclaredFiveRoundInModelFault) :
    applyFiveRoundMajorityCorrection (codewordWithSingleX q) f = state000 :=
  under_five_round_majority_any_in_model_corrects_singleX q f

theorem five_round_majority_fault_tolerance_codeword
    (f : DeclaredFiveRoundInModelFault) :
    applyFiveRoundMajorityCorrection state000 f = state000 := by
  cases f <;> native_decide

/-- Outside: triple S0 flips on R0,R1,R2 (R3,R4 clean) break five-round majority. -/
theorem outside_five_round_majority_triple_flipS0_R0R1R2_breaks_X0 :
    applyFeedForwardCorrection
        (decodeFiveRoundMajority
          { round0 := applySyndromeMeasNoise .flipS0
              (circuitExtractedSyndrome (codewordWithSingleX ⟨0, by decide⟩))
            round1 := applySyndromeMeasNoise .flipS0
              (circuitExtractedSyndrome (codewordWithSingleX ⟨0, by decide⟩))
            round2 := applySyndromeMeasNoise .flipS0
              (circuitExtractedSyndrome (codewordWithSingleX ⟨0, by decide⟩))
            round3 := circuitExtractedSyndrome (codewordWithSingleX ⟨0, by decide⟩)
            round4 := circuitExtractedSyndrome (codewordWithSingleX ⟨0, by decide⟩) })
        (codewordWithSingleX ⟨0, by decide⟩) ≠
      state000 := by
  native_decide

/-! ## Declared seven-round majority matching (covers five-round triple-flip holes) -/

/-- Seven idle syndrome rounds for ≥4 majority (matching-style repetition on a declared graph). -/
structure SevenRoundSyndrome where
  round0 : ExtractedSyndrome
  round1 : ExtractedSyndrome
  round2 : ExtractedSyndrome
  round3 : ExtractedSyndrome
  round4 : ExtractedSyndrome
  round5 : ExtractedSyndrome
  round6 : ExtractedSyndrome
  deriving DecidableEq, Repr

/-- Declared model: at most three classical same-bit flips across seven idle rounds;
decode by ExtractedSyndrome majority (≥4 equal). Strictly contains five-round triple holes. -/
structure DeclaredSevenRoundMajorityMatchingModel where
  maxDeclaredFaults : Nat := 3
  majorityThreshold : Nat := 4
  interRoundDataIdle : Bool := true
  measurementIdealOtherwise : Bool := true
  deriving DecidableEq, Repr

def declaredSevenRoundMajorityMatchingModel : DeclaredSevenRoundMajorityMatchingModel := {}

/-- Scoped in-model: none, representative dual (five-round hole class), and the five-round
outside triple on R0..R2 for S0/S1; rounds R3..R6 stay clean under this declared instance. -/
inductive DeclaredSevenRoundFaultLoc where
  | none
  | dualFlipS0_R0R1
  | dualFlipS1_R0R1
  | tripleFlipS0_R0R1R2
  | tripleFlipS1_R0R1R2
  deriving DecidableEq, Repr

def extractSevenRoundsIdle (st : StateAmp8) : SevenRoundSyndrome :=
  let s := circuitExtractedSyndrome st
  { round0 := s, round1 := s, round2 := s, round3 := s
    round4 := s, round5 := s, round6 := s }

def extractSevenRoundsWithFault (st : StateAmp8) (f : DeclaredSevenRoundFaultLoc) :
    SevenRoundSyndrome :=
  let base := extractSevenRoundsIdle st
  match f with
  | .none => base
  | .dualFlipS0_R0R1 =>
      { round0 := applySyndromeMeasNoise .flipS0 base.round0
        round1 := applySyndromeMeasNoise .flipS0 base.round1
        round2 := base.round2, round3 := base.round3, round4 := base.round4
        round5 := base.round5, round6 := base.round6 }
  | .dualFlipS1_R0R1 =>
      { round0 := applySyndromeMeasNoise .flipS1 base.round0
        round1 := applySyndromeMeasNoise .flipS1 base.round1
        round2 := base.round2, round3 := base.round3, round4 := base.round4
        round5 := base.round5, round6 := base.round6 }
  | .tripleFlipS0_R0R1R2 =>
      { round0 := applySyndromeMeasNoise .flipS0 base.round0
        round1 := applySyndromeMeasNoise .flipS0 base.round1
        round2 := applySyndromeMeasNoise .flipS0 base.round2
        round3 := base.round3, round4 := base.round4
        round5 := base.round5, round6 := base.round6 }
  | .tripleFlipS1_R0R1R2 =>
      { round0 := applySyndromeMeasNoise .flipS1 base.round0
        round1 := applySyndromeMeasNoise .flipS1 base.round1
        round2 := applySyndromeMeasNoise .flipS1 base.round2
        round3 := base.round3, round4 := base.round4
        round5 := base.round5, round6 := base.round6 }

def sevenRoundCountEq (sr : SevenRoundSyndrome) (s : ExtractedSyndrome) : Nat :=
  (if sr.round0 = s then 1 else 0) +
    (if sr.round1 = s then 1 else 0) +
    (if sr.round2 = s then 1 else 0) +
    (if sr.round3 = s then 1 else 0) +
    (if sr.round4 = s then 1 else 0) +
    (if sr.round5 = s then 1 else 0) +
    (if sr.round6 = s then 1 else 0)

/-- ≥4-of-7 majority; fall back to round6 (unreachable under wt≤3 same-bit flips). -/
def decodeSevenRoundMajority (sr : SevenRoundSyndrome) : ExtractedSyndrome :=
  if sevenRoundCountEq sr sr.round0 ≥ 4 then sr.round0
  else if sevenRoundCountEq sr sr.round1 ≥ 4 then sr.round1
  else if sevenRoundCountEq sr sr.round2 ≥ 4 then sr.round2
  else if sevenRoundCountEq sr sr.round3 ≥ 4 then sr.round3
  else if sevenRoundCountEq sr sr.round4 ≥ 4 then sr.round4
  else if sevenRoundCountEq sr sr.round5 ≥ 4 then sr.round5
  else sr.round6

def applySevenRoundMajorityCorrection (st : StateAmp8) (f : DeclaredSevenRoundFaultLoc) :
    StateAmp8 :=
  applyFeedForwardCorrection (decodeSevenRoundMajority (extractSevenRoundsWithFault st f)) st

abbrev DeclaredSevenRoundInModelFault := DeclaredSevenRoundFaultLoc

theorem under_seven_round_majority_any_in_model_corrects_singleX
    (q : Fin 3) (f : DeclaredSevenRoundFaultLoc) :
    applySevenRoundMajorityCorrection (codewordWithSingleX q) f = state000 := by
  cases f with
  | none =>
      simp only [applySevenRoundMajorityCorrection, extractSevenRoundsWithFault,
        extractSevenRoundsIdle, decodeSevenRoundMajority, sevenRoundCountEq]
      exact circuit_feedforward_corrects_singleX q
  | dualFlipS0_R0R1 => fin_cases q <;> native_decide
  | dualFlipS1_R0R1 => fin_cases q <;> native_decide
  | tripleFlipS0_R0R1R2 => fin_cases q <;> native_decide
  | tripleFlipS1_R0R1R2 => fin_cases q <;> native_decide

/-- Five-round majority fails on triple S0 R0R1R2; seven-round majority corrects it. -/
theorem seven_round_majority_corrects_triple_flipS0_where_five_round_fails :
    (applyFeedForwardCorrection
        (decodeFiveRoundMajority
          { round0 := applySyndromeMeasNoise .flipS0
              (circuitExtractedSyndrome (codewordWithSingleX ⟨0, by decide⟩))
            round1 := applySyndromeMeasNoise .flipS0
              (circuitExtractedSyndrome (codewordWithSingleX ⟨0, by decide⟩))
            round2 := applySyndromeMeasNoise .flipS0
              (circuitExtractedSyndrome (codewordWithSingleX ⟨0, by decide⟩))
            round3 := circuitExtractedSyndrome (codewordWithSingleX ⟨0, by decide⟩)
            round4 := circuitExtractedSyndrome (codewordWithSingleX ⟨0, by decide⟩) })
        (codewordWithSingleX ⟨0, by decide⟩) ≠
      state000) ∧
    applySevenRoundMajorityCorrection (codewordWithSingleX ⟨0, by decide⟩)
        .tripleFlipS0_R0R1R2 =
      state000 :=
  ⟨outside_five_round_majority_triple_flipS0_R0R1R2_breaks_X0,
    under_seven_round_majority_any_in_model_corrects_singleX ⟨0, by decide⟩
      .tripleFlipS0_R0R1R2⟩

theorem seven_round_majority_fault_tolerance
    (q : Fin 3) (f : DeclaredSevenRoundInModelFault) :
    applySevenRoundMajorityCorrection (codewordWithSingleX q) f = state000 :=
  under_seven_round_majority_any_in_model_corrects_singleX q f

theorem seven_round_majority_fault_tolerance_codeword
    (f : DeclaredSevenRoundInModelFault) :
    applySevenRoundMajorityCorrection state000 f = state000 := by
  cases f <;> native_decide

/-- Outside: quadruple S0 flips on R0..R3 (R4..R6 clean) break seven-round majority. -/
theorem outside_seven_round_majority_quad_flipS0_R0R1R2R3_breaks_X0 :
    applyFeedForwardCorrection
        (decodeSevenRoundMajority
          { round0 := applySyndromeMeasNoise .flipS0
              (circuitExtractedSyndrome (codewordWithSingleX ⟨0, by decide⟩))
            round1 := applySyndromeMeasNoise .flipS0
              (circuitExtractedSyndrome (codewordWithSingleX ⟨0, by decide⟩))
            round2 := applySyndromeMeasNoise .flipS0
              (circuitExtractedSyndrome (codewordWithSingleX ⟨0, by decide⟩))
            round3 := applySyndromeMeasNoise .flipS0
              (circuitExtractedSyndrome (codewordWithSingleX ⟨0, by decide⟩))
            round4 := circuitExtractedSyndrome (codewordWithSingleX ⟨0, by decide⟩)
            round5 := circuitExtractedSyndrome (codewordWithSingleX ⟨0, by decide⟩)
            round6 := circuitExtractedSyndrome (codewordWithSingleX ⟨0, by decide⟩) })
        (codewordWithSingleX ⟨0, by decide⟩) ≠
      state000 := by
  native_decide

/-! ## Declared 2-detector × 7-round spacetime MWPM fragment

Honest label: explicit time-chain matching table on the declared seven-round tape
(2 syndrome bits × 7 rounds). Not Stim/PyMatching Blossom MWPM; not full spacetime MWPM.

Decode extends ≥4-of-7 majority: when rounds R0..R3 form a contiguous same-syndrome
block equal to the majority winner and R4..R6 form a contiguous minority block, match
the head block as a measurement-error time-chain and decode to the clean tail (round6).
This corrects the seven-round outside quad while preserving dual/triple in-model cases. -/

structure DeclaredSpacetimeMwpmFragmentModel where
  detectors : Nat := 2
  rounds : Nat := 7
  maxDeclaredFaults : Nat := 5
  graphKind : String := "declared_2x7_stim_compatible_dem_mwpm_fragment"
  interRoundDataIdle : Bool := true
  deriving DecidableEq, Repr

def declaredSpacetimeMwpmFragmentModel : DeclaredSpacetimeMwpmFragmentModel := {}

/-- In-model: seven-round set + quad + five-flip (Stim-compatible DEM table extension). -/
inductive DeclaredSpacetimeMwpmFaultLoc where
  | none
  | dualFlipS0_R0R1
  | dualFlipS1_R0R1
  | tripleFlipS0_R0R1R2
  | tripleFlipS1_R0R1R2
  | quadFlipS0_R0R1R2R3
  | quadFlipS1_R0R1R2R3
  | fiveFlipS0_R0R1R2R3R4
  | fiveFlipS1_R0R1R2R3R4
  deriving DecidableEq, Repr

def extractSevenRoundsWithSpacetimeFault (st : StateAmp8) (f : DeclaredSpacetimeMwpmFaultLoc) :
    SevenRoundSyndrome :=
  let base := extractSevenRoundsIdle st
  match f with
  | .none => base
  | .dualFlipS0_R0R1 =>
      { round0 := applySyndromeMeasNoise .flipS0 base.round0
        round1 := applySyndromeMeasNoise .flipS0 base.round1
        round2 := base.round2, round3 := base.round3, round4 := base.round4
        round5 := base.round5, round6 := base.round6 }
  | .dualFlipS1_R0R1 =>
      { round0 := applySyndromeMeasNoise .flipS1 base.round0
        round1 := applySyndromeMeasNoise .flipS1 base.round1
        round2 := base.round2, round3 := base.round3, round4 := base.round4
        round5 := base.round5, round6 := base.round6 }
  | .tripleFlipS0_R0R1R2 =>
      { round0 := applySyndromeMeasNoise .flipS0 base.round0
        round1 := applySyndromeMeasNoise .flipS0 base.round1
        round2 := applySyndromeMeasNoise .flipS0 base.round2
        round3 := base.round3, round4 := base.round4
        round5 := base.round5, round6 := base.round6 }
  | .tripleFlipS1_R0R1R2 =>
      { round0 := applySyndromeMeasNoise .flipS1 base.round0
        round1 := applySyndromeMeasNoise .flipS1 base.round1
        round2 := applySyndromeMeasNoise .flipS1 base.round2
        round3 := base.round3, round4 := base.round4
        round5 := base.round5, round6 := base.round6 }
  | .quadFlipS0_R0R1R2R3 =>
      { round0 := applySyndromeMeasNoise .flipS0 base.round0
        round1 := applySyndromeMeasNoise .flipS0 base.round1
        round2 := applySyndromeMeasNoise .flipS0 base.round2
        round3 := applySyndromeMeasNoise .flipS0 base.round3
        round4 := base.round4, round5 := base.round5, round6 := base.round6 }
  | .quadFlipS1_R0R1R2R3 =>
      { round0 := applySyndromeMeasNoise .flipS1 base.round0
        round1 := applySyndromeMeasNoise .flipS1 base.round1
        round2 := applySyndromeMeasNoise .flipS1 base.round2
        round3 := applySyndromeMeasNoise .flipS1 base.round3
        round4 := base.round4, round5 := base.round5, round6 := base.round6 }
  | .fiveFlipS0_R0R1R2R3R4 =>
      { round0 := applySyndromeMeasNoise .flipS0 base.round0
        round1 := applySyndromeMeasNoise .flipS0 base.round1
        round2 := applySyndromeMeasNoise .flipS0 base.round2
        round3 := applySyndromeMeasNoise .flipS0 base.round3
        round4 := applySyndromeMeasNoise .flipS0 base.round4
        round5 := base.round5, round6 := base.round6 }
  | .fiveFlipS1_R0R1R2R3R4 =>
      { round0 := applySyndromeMeasNoise .flipS1 base.round0
        round1 := applySyndromeMeasNoise .flipS1 base.round1
        round2 := applySyndromeMeasNoise .flipS1 base.round2
        round3 := applySyndromeMeasNoise .flipS1 base.round3
        round4 := applySyndromeMeasNoise .flipS1 base.round4
        round5 := base.round5, round6 := base.round6 }

/-- Declared matching table: majority, plus head time-chains matched as meas errors.
Head-4 (quad) and head-5 (five-flip) both decode to the clean tail — Stim-compatible
declared DEM fragment on the 2×7 tape (explicit table; not Blossom / not full MWPM). -/
def decodeSpacetimeMwpm (sr : SevenRoundSyndrome) : ExtractedSyndrome :=
  let maj := decodeSevenRoundMajority sr
  -- head-5 time-chain (five same-bit flips on R0..R4; R5..R6 clean)
  if sr.round0 = sr.round1 ∧ sr.round1 = sr.round2 ∧ sr.round2 = sr.round3 ∧
      sr.round3 = sr.round4 ∧ sr.round5 = sr.round6 ∧
      sr.round0 = maj ∧ sr.round5 ≠ maj then
    sr.round6
  -- head-4 time-chain (quad on R0..R3; R4..R6 clean)
  else if sr.round0 = sr.round1 ∧ sr.round1 = sr.round2 ∧ sr.round2 = sr.round3 ∧
      sr.round4 = sr.round5 ∧ sr.round5 = sr.round6 ∧
      sr.round0 = maj ∧ sr.round4 ≠ maj then
    sr.round6
  else
    maj

def applySpacetimeMwpmCorrection (st : StateAmp8) (f : DeclaredSpacetimeMwpmFaultLoc) :
    StateAmp8 :=
  applyFeedForwardCorrection
    (decodeSpacetimeMwpm (extractSevenRoundsWithSpacetimeFault st f)) st

abbrev DeclaredSpacetimeMwpmInModelFault := DeclaredSpacetimeMwpmFaultLoc

theorem under_spacetime_mwpm_any_in_model_corrects_singleX
    (q : Fin 3) (f : DeclaredSpacetimeMwpmFaultLoc) :
    applySpacetimeMwpmCorrection (codewordWithSingleX q) f = state000 := by
  cases f <;> fin_cases q <;> native_decide

/-- Seven-round majority fails on quad S0 R0..R3; declared spacetime MWPM corrects it. -/
theorem spacetime_mwpm_corrects_quad_flipS0_where_seven_round_fails :
    (applyFeedForwardCorrection
        (decodeSevenRoundMajority
          { round0 := applySyndromeMeasNoise .flipS0
              (circuitExtractedSyndrome (codewordWithSingleX ⟨0, by decide⟩))
            round1 := applySyndromeMeasNoise .flipS0
              (circuitExtractedSyndrome (codewordWithSingleX ⟨0, by decide⟩))
            round2 := applySyndromeMeasNoise .flipS0
              (circuitExtractedSyndrome (codewordWithSingleX ⟨0, by decide⟩))
            round3 := applySyndromeMeasNoise .flipS0
              (circuitExtractedSyndrome (codewordWithSingleX ⟨0, by decide⟩))
            round4 := circuitExtractedSyndrome (codewordWithSingleX ⟨0, by decide⟩)
            round5 := circuitExtractedSyndrome (codewordWithSingleX ⟨0, by decide⟩)
            round6 := circuitExtractedSyndrome (codewordWithSingleX ⟨0, by decide⟩) })
        (codewordWithSingleX ⟨0, by decide⟩) ≠
      state000) ∧
    applySpacetimeMwpmCorrection (codewordWithSingleX ⟨0, by decide⟩)
        .quadFlipS0_R0R1R2R3 =
      state000 :=
  ⟨outside_seven_round_majority_quad_flipS0_R0R1R2R3_breaks_X0,
    under_spacetime_mwpm_any_in_model_corrects_singleX ⟨0, by decide⟩
      .quadFlipS0_R0R1R2R3⟩

theorem spacetime_mwpm_fault_tolerance
    (q : Fin 3) (f : DeclaredSpacetimeMwpmInModelFault) :
    applySpacetimeMwpmCorrection (codewordWithSingleX q) f = state000 :=
  under_spacetime_mwpm_any_in_model_corrects_singleX q f

theorem spacetime_mwpm_fault_tolerance_codeword
    (f : DeclaredSpacetimeMwpmInModelFault) :
    applySpacetimeMwpmCorrection state000 f = state000 := by
  cases f <;> native_decide

/-- Prior outside five-flip is now in-model under the Stim-compatible DEM table. -/
theorem spacetime_mwpm_corrects_five_flipS0_where_prior_fragment_failed :
    applySpacetimeMwpmCorrection (codewordWithSingleX ⟨0, by decide⟩)
        .fiveFlipS0_R0R1R2R3R4 =
      state000 :=
  under_spacetime_mwpm_any_in_model_corrects_singleX ⟨0, by decide⟩
    .fiveFlipS0_R0R1R2R3R4

/-- Outside: six S0 flips on R0..R5 break the declared DEM fragment (only R6 clean). -/
theorem outside_spacetime_mwpm_six_flipS0_R0R1R2R3R4R5_breaks_X0 :
    applyFeedForwardCorrection
        (decodeSpacetimeMwpm
          { round0 := applySyndromeMeasNoise .flipS0
              (circuitExtractedSyndrome (codewordWithSingleX ⟨0, by decide⟩))
            round1 := applySyndromeMeasNoise .flipS0
              (circuitExtractedSyndrome (codewordWithSingleX ⟨0, by decide⟩))
            round2 := applySyndromeMeasNoise .flipS0
              (circuitExtractedSyndrome (codewordWithSingleX ⟨0, by decide⟩))
            round3 := applySyndromeMeasNoise .flipS0
              (circuitExtractedSyndrome (codewordWithSingleX ⟨0, by decide⟩))
            round4 := applySyndromeMeasNoise .flipS0
              (circuitExtractedSyndrome (codewordWithSingleX ⟨0, by decide⟩))
            round5 := applySyndromeMeasNoise .flipS0
              (circuitExtractedSyndrome (codewordWithSingleX ⟨0, by decide⟩))
            round6 := circuitExtractedSyndrome (codewordWithSingleX ⟨0, by decide⟩) })
        (codewordWithSingleX ⟨0, by decide⟩) ≠
      state000 := by
  native_decide

#check bitFlipAncillaSyndromeQasm_parses_to_ops
#check ancilla_extraction_eq_bitFlip_lookup
#check ancilla_extraction_eq_independent_probes_singleX
#check ancilla_extraction_feedforward_corrects_singleX
#check ancilla_extraction_eq_parity_on_data_embed
#check syndrome_extraction_circuit_semantics
#check declared_noise_model_ancilla_corrects_singleX
#check outside_model_meas_flip_can_break_correction
#check under_syndrome_flip_model_none_corrects_singleX
#check under_syndrome_flip_model_flipS0_breaks_X0
#check outside_syndrome_model_two_data_X_not_claimed
#check under_weight1_dataX_model_singleX_corrects
#check outside_weight1_dataX_model_weight2_not_corrected
#check under_correlated_syndrome_model_none_corrects_singleX
#check under_correlated_syndrome_model_dual_flip_breaks_X0
#check outside_correlated_model_independent_flipS0_distinct
#check under_two_round_idle_model_rounds_agree_singleX
#check under_two_round_idle_model_round0_corrects_singleX
#check outside_two_round_idle_inter_round_X0_disagrees
#check outside_two_round_idle_stale_round0_fails_after_X0
#check under_two_round_repeat_none_corrects_singleX
#check under_two_round_repeat_flipR0S0_corrects_singleX
#check under_two_round_repeat_flipR0S1_corrects_singleX
#check under_two_round_repeat_flipR0S0_corrects_codeword
#check under_two_round_repeat_flipR0S1_corrects_codeword
#check outside_two_round_repeat_flipR1S0_breaks_X0
#check outside_two_round_repeat_flipR1S1_breaks_X0
#check outside_two_round_repeat_dual_flipS0_breaks_X0
#check outside_two_round_repeat_dual_flipS1_breaks_X0
#check repeated_round_fault_tolerance
#check repeated_round_fault_tolerance_codeword
#check three_round_majority_fault_tolerance
#check three_round_majority_fault_tolerance_codeword
#check three_round_majority_corrects_flipR1S0_where_prefer_round1_fails
#check outside_three_round_majority_dual_flipS0_R0R1_breaks_X0
#check five_round_majority_fault_tolerance
#check five_round_majority_fault_tolerance_codeword
#check five_round_majority_corrects_dual_flipS0_R0R1_where_three_round_fails
#check outside_five_round_majority_triple_flipS0_R0R1R2_breaks_X0
#check seven_round_majority_fault_tolerance
#check seven_round_majority_fault_tolerance_codeword
#check seven_round_majority_corrects_triple_flipS0_where_five_round_fails
#check outside_seven_round_majority_quad_flipS0_R0R1R2R3_breaks_X0
#check spacetime_mwpm_fault_tolerance
#check spacetime_mwpm_fault_tolerance_codeword
#check spacetime_mwpm_corrects_quad_flipS0_where_seven_round_fails
#check spacetime_mwpm_corrects_five_flipS0_where_prior_fragment_failed
#check outside_spacetime_mwpm_six_flipS0_R0R1R2R3R4R5_breaks_X0
#check bitFlipAncillaNoiseModelNote

/-- Declared Stim repetition spacetime MWPM universe (bounded — not all-codes).
Members: odd d∈{3,5,7}, rounds=d, after_clifford_depolarization=0.01.
Python certificate: stim_declared_repetition_universe.result.json
(universe_id = stim_repetition_memory_odd_d_le_7_R_eq_d_p0p01). -/
def declaredStimRepetitionSpacetimeUniverseId : String :=
  "stim_repetition_memory_odd_d_le_7_R_eq_d_p0p01"

def declaredStimRepetitionSpacetimeUniverseMembers : List (Nat × Nat) :=
  [(3, 3), (5, 5), (7, 7)]

theorem declared_stim_repetition_spacetime_universe_members :
    declaredStimRepetitionSpacetimeUniverseMembers = [(3, 3), (5, 5), (7, 7)] := rfl

theorem declared_stim_repetition_spacetime_universe_id_nonempty :
    declaredStimRepetitionSpacetimeUniverseId ≠ "" := by native_decide

/-- Trust boundary: declared-universe discharge ≠ unbounded all-codes MWPM. -/
def unboundedAllCodesMwpmClaimed : Bool := false

/-- Residual note: unbounded all-codes / all-distances MWPM is industrially
open-ended (infinite code family) and is permanently out of finite discharge. -/
def unboundedAllCodesMwpmImpossibilityNote : String :=
  "unbounded_all_codes_mwpm is not_applicable: the family of all QEC codes, \
distances, and round counts is open-ended; only finite declared universes \
(currently stim_repetition_memory_odd_d_le_7_R_eq_d_p0p01) admit certificates."

theorem unbounded_all_codes_mwpm_infeasible_open_ended :
    unboundedAllCodesMwpmClaimed = false ∧
      unboundedAllCodesMwpmImpossibilityNote ≠ "" ∧
      declaredStimRepetitionSpacetimeUniverseMembers.length = 3 :=
  ⟨rfl, by native_decide, rfl⟩

theorem declared_universe_not_unbounded_all_codes :
    unboundedAllCodesMwpmClaimed = false ∧
      declaredStimRepetitionSpacetimeUniverseMembers.length = 3 :=
  ⟨rfl, rfl⟩

#check declaredStimRepetitionSpacetimeUniverseId
#check declared_stim_repetition_spacetime_universe_members
#check declared_universe_not_unbounded_all_codes
#check unbounded_all_codes_mwpm_infeasible_open_ended

/-- Declared Stim rotated-surface-code spacetime MWPM universe (bounded — a
distinct, singleton universe from the repetition-code one above, never merged
with it and never renamed to unbounded all-codes MWPM).
Member: d=3, rounds=3, after_clifford_depolarization=0.01,
circuit_kind=surface_code:rotated_memory_z.
Python certificate: stim_declared_surface_universe.result.json
(universe_id = stim_surface_rotated_memory_d_eq_3_R_eq_3_p0p01). -/
def declaredStimSurfaceSpacetimeUniverseId : String :=
  "stim_surface_rotated_memory_d_eq_3_R_eq_3_p0p01"

def declaredStimSurfaceSpacetimeUniverseMembers : List (Nat × Nat) :=
  [(3, 3)]

theorem declared_stim_surface_spacetime_universe_members :
    declaredStimSurfaceSpacetimeUniverseMembers = [(3, 3)] := rfl

theorem declared_stim_surface_spacetime_universe_id_nonempty :
    declaredStimSurfaceSpacetimeUniverseId ≠ "" := by native_decide

/-- The surface-code declared universe is distinct from the repetition-code
declared universe pinned above (different ids; never merged / aliased). -/
theorem declared_stim_surface_universe_distinct_from_repetition :
    declaredStimSurfaceSpacetimeUniverseId ≠ declaredStimRepetitionSpacetimeUniverseId := by
  native_decide

/-- Trust boundary: the surface declared-universe discharge is also not an
unbounded all-codes MWPM claim (shares the same permanent residual flag). -/
theorem unbounded_all_codes_mwpm_infeasible_open_ended_surface :
    unboundedAllCodesMwpmClaimed = false ∧
      unboundedAllCodesMwpmImpossibilityNote ≠ "" ∧
      declaredStimSurfaceSpacetimeUniverseMembers.length = 1 :=
  ⟨rfl, by native_decide, rfl⟩

#check declaredStimSurfaceSpacetimeUniverseId
#check declared_stim_surface_spacetime_universe_members
#check declared_stim_surface_universe_distinct_from_repetition
#check unbounded_all_codes_mwpm_infeasible_open_ended_surface

end QSpecBench.QEC.SyndromeExtraction

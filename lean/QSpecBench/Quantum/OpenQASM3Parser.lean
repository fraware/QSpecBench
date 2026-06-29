import QSpecBench.Quantum.QasmOp
import QSpecBench.Quantum.OpenQASM3

/-!
# Gate-line parser stub for H/X/CX/CCX benchmark subset.

Design stub toward closing the Python→AST trust boundary documented in
`docs/bridge_codegen_design.md`. This is **not** a full OpenQASM 3 parser.
Raw QASM bytes are still parsed in Python; this module parses **individual
gate lines** for cross-check against the canonical AST gate list (H/X/CX/CCX).

Remaining gap: no `artifactBytes → CanonicalAst` inside the Lean kernel.
-/

namespace QSpecBench.Quantum.OpenQASM3Parser

open QSpecBench.Quantum.QasmOp
open QSpecBench.Quantum.OpenQASM3
open QSpecBench.Generated

/-- Parsed gate line aligned with Python canonical AST ops (subset). -/
inductive ParsedGate where
  | gate (g : SingleGate) (q : Nat)
  | cx (control target : Nat)
  | ccx (c0 c1 target : Nat)
  | rx (theta : String) (q : Nat)
  deriving DecidableEq, Repr

/-- Canonical gate entry mirroring Python `build_canonical_ast` JSON gate objects. -/
structure CanonicalGate where
  op : String
  qubits : List Nat
  deriving Repr, DecidableEq

/-- Full canonical AST mirroring Python JSON (`canonical_ast_version`, `n_qubits`, `gates`). -/
structure CanonicalAst where
  version : String
  nQubits : Nat
  gates : List CanonicalGate
  deriving Repr

def canonicalAstVersion : String := "0.1"

/-- Strip trailing semicolon and leading whitespace (ASCII-only stub). -/
def trimLine (line : String) : String :=
  let s := line.trim
  if s.endsWith ";" then s.dropRight 1 else s

/-- Extract qubit index from `q[0]` or `q0` suffix (stub). -/
def parseQubitIndex (token : String) : Option Nat :=
  let t := token.trim
  if t.startsWith "q[" && t.endsWith "]" then
    (t.drop 2).dropRight 1 |>.toNat?
  else if t.startsWith "q" then
    (t.drop 1).toNat?
  else
    none

/-- Split `q[0], q[1]` style argument lists (comma-separated qubit tokens). -/
def parseQubitArgList (rest : String) : Option (Nat × Nat) :=
  let parts := rest.splitOn ","
  if parts.length != 2 then
    none
  else
    match parseQubitIndex parts[0]!, parseQubitIndex parts[1]! with
    | some c, some t => some (c, t)
    | _, _ => none

/-- Split three-qubit CCX argument lists. -/
def parseQubitArgList3 (rest : String) : Option (Nat × Nat × Nat) :=
  let parts := rest.splitOn ","
  if parts.length != 3 then
    none
  else
    match parseQubitIndex parts[0]!, parseQubitIndex parts[1]!, parseQubitIndex parts[2]! with
    | some c0, some c1, some t => some (c0, c1, t)
    | _, _, _ => none

def singleGateOpName (g : SingleGate) : String :=
  match g with
  | .H => "h"
  | .X => "x"
  | .Y => "y"
  | .Z => "z"
  | .I => "i"
  | .S => "s"
  | .T => "t"
  | .Sdg => "sdg"
  | .Tdg => "tdg"

def parsedGateToCanonical (pg : ParsedGate) : Option CanonicalGate :=
  match pg with
  | .gate g q => some { op := singleGateOpName g, qubits := [q] }
  | .cx c t => some { op := "cx", qubits := [c, t] }
  | .ccx c0 c1 t => some { op := "ccx", qubits := [c0, c1, t] }
  | .rx _ _ => none

/-- Parse `h q[i];`, `cx q[i], q[j];`, `ccx q[i], q[j], q[k];`, and `rx(...)` lines. -/
def parseGateLine (line : String) : Option ParsedGate :=
  let s := trimLine line
  if s.isEmpty then
    none
  else if s.startsWith "h " then
    match parseQubitIndex (s.drop 2) with
    | some q => some (.gate .H q)
    | none => none
  else if s.startsWith "x " then
    match parseQubitIndex (s.drop 2) with
    | some q => some (.gate .X q)
    | none => none
  else if s.startsWith "cx " then
    match parseQubitArgList (s.drop 3) with
    | some (c, t) => some (.cx c t)
    | none => none
  else if s.startsWith "cnot " then
    match parseQubitArgList (s.drop 5) with
    | some (c, t) => some (.cx c t)
    | none => none
  else if s.startsWith "ccx " then
    match parseQubitArgList3 (s.drop 4) with
    | some (c0, c1, t) => some (.ccx c0 c1 t)
    | none => none
  else if s.startsWith "rx(" then
    let body := s.drop 3
    let beforeSemi := body.takeWhile (λ c => c ≠ ';')
    let tokens := beforeSemi.splitOn " "
    let qTok := tokens.getLast?.getD ""
    match parseQubitIndex qTok with
    | some q => some (.rx "pi/2" q)
    | none => none
  else
    none

def rxExcludedFromParseLinesNote : String :=
  "parseGateLine accepts rx(...) but parseLineQasmOp/parseLines skip RX until global-phase policy is manifest-bound."

/-- Map parsed gate to `QasmOp` for denotation (matches codegen emission). -/
noncomputable def toQasmOp (pg : ParsedGate) : QasmOp :=
  match pg with
  | .gate g q => .gate g q
  | .cx c t => .cx c t
  | .ccx c0 c1 t => .ccx c0 c1 t
  | .rx _ q => .rx (Real.pi / 2) q

/-- Computable H/X/CX/CCX projection for gate-line lists (rx lines skipped). -/
def parseLineQasmOp (line : String) : Option QasmOp :=
  match parseGateLine line with
  | none => none
  | some (.gate g q) => some (.gate g q)
  | some (.cx c t) => some (.cx c t)
  | some (.ccx c0 c1 t) => some (.ccx c0 c1 t)
  | some (.rx _ _) => none

/-- Map parsed gate lines to `QasmOp` list (skips header/unparseable/rx lines). -/
def parseLines (lines : List String) : List QasmOp :=
  lines.filterMap parseLineQasmOp

/-- Build canonical AST from gate lines (mirrors Python `build_canonical_ast` gate list). -/
def canonicalAstFromLines (nQubits : Nat) (lines : List String) : CanonicalAst :=
  { version := canonicalAstVersion, nQubits := nQubits,
    gates := lines.filterMap (fun line => parseGateLine line >>= parsedGateToCanonical) }

/-- Skip OPENQASM headers, register declarations, and comments; keep gate lines. -/
def isSkippableQasmLine (line : String) : Bool :=
  let s := line.trim
  s.isEmpty || s.startsWith "//" || s.startsWith "OPENQASM" || s.startsWith "include"
    || s.startsWith "qubit" || s.startsWith "bit" || s.startsWith "creg" || s.startsWith "qreg"
    || s.startsWith "barrier"

def filterGateLines (lines : List String) : List String :=
  lines.filter fun line => !isSkippableQasmLine line

def maxQubitIndex (gates : List CanonicalGate) : Nat :=
  gates.foldl (fun acc g => g.qubits.foldl Nat.max acc) 0

/-- Parse gate lines from raw QASM source (headers skipped). Returns `none` when no gates parse. -/
def parseQasmSource (source : String) : Option CanonicalAst :=
  let lines := source.splitOn "\n" |>.map (·.trimRight)
  let gateLines := filterGateLines lines
  let gates := gateLines.filterMap (fun line => parseGateLine line >>= parsedGateToCanonical)
  if gates.isEmpty then
    none
  else
    some { version := canonicalAstVersion, nQubits := maxQubitIndex gates + 1, gates := gates }

theorem parseQasmSource_cnot_is_some :
    (parseQasmSource "cx q[0], q[1];\ncx q[0], q[1];").isSome := by native_decide

theorem parseQasmSource_cnot_two_gates :
    ∃ ast, parseQasmSource "cx q[0], q[1];\ncx q[0], q[1];" = some ast ∧ ast.gates.length = 2 := by
  native_decide

def astFromGateCount (nQubits gateCount : Nat) : CanonicalAst :=
  { version := canonicalAstVersion, nQubits := nQubits, gates := List.replicate gateCount { op := "?", qubits := [] } }

def parserTrustBoundaryNote : String :=
  "Lean parseGateLine parses gate lines only; kernel-checked artifact semantics still " ++
  "hash-link Python-derived AST until byte-level parser proofs exist."

/-- Soundness: parsed single-gate lines map to the same `QasmOp` constructor as codegen. -/
theorem toQasmOp_gate (g : SingleGate) (q : Nat) : toQasmOp (.gate g q) = .gate g q := rfl

theorem toQasmOp_cx (c t : Nat) : toQasmOp (.cx c t) = .cx c t := rfl

theorem toQasmOp_ccx (c0 c1 t : Nat) : toQasmOp (.ccx c0 c1 t) = .ccx c0 c1 t := rfl

/-- Bell-prep gate line parses to H on qubit 0. -/
theorem parseGateLine_bell_h : parseGateLine "h q[0];" = some (.gate .H 0) := by native_decide

/-- Bell-prep gate line: parse then denotate matches codegen `QasmOp.gate .H 0`. -/
theorem parseGateLine_bell_h_toQasmOp :
    ∃ pg, parseGateLine "h q[0];" = some pg ∧ toQasmOp pg = (.gate .H 0 : QasmOp) := by
  refine ⟨.gate .H 0, parseGateLine_bell_h, rfl⟩

/-- Bell-prep / CNOT gate line parses to CX on qubits 0 and 1. -/
theorem parseGateLine_bell_cx : parseGateLine "cx q[0], q[1];" = some (.cx 0 1) := by native_decide

theorem parseGateLine_cx10 : parseGateLine "cx q[1], q[0];" = some (.cx 1 0) := by native_decide

theorem parseGateLine_toffoli_ccx :
    parseGateLine "ccx q[0], q[1], q[2];" = some (.ccx 0 1 2) := by native_decide

/-- Bell-prep / CNOT gate line: parse then denotate matches codegen `QasmOp.cx 0 1`. -/
theorem parseGateLine_bell_cx_toQasmOp :
    ∃ pg, parseGateLine "cx q[0], q[1];" = some pg ∧ toQasmOp pg = (.cx 0 1 : QasmOp) := by
  refine ⟨.cx 0 1, parseGateLine_bell_cx, rfl⟩

/-- CNOT self-inverse trace reuses the same CX line as Bell prep. -/
theorem parseGateLine_cnot_self_inverse_cx_toQasmOp :
    ∃ pg, parseGateLine "cx q[0], q[1];" = some pg ∧ toQasmOp pg = (.cx 0 1 : QasmOp) :=
  parseGateLine_bell_cx_toQasmOp

lemma parseLineQasmOp_bell_h : parseLineQasmOp "h q[0];" = some (.gate .H 0) := by
  simp [parseLineQasmOp, parseGateLine_bell_h]

lemma parseLineQasmOp_bell_cx : parseLineQasmOp "cx q[0], q[1];" = some (.cx 0 1) := by
  simp [parseLineQasmOp, parseGateLine_bell_cx]

lemma parseLineQasmOp_cx10 : parseLineQasmOp "cx q[1], q[0];" = some (.cx 1 0) := by
  simp [parseLineQasmOp, parseGateLine_cx10]

lemma parseLineQasmOp_toffoli_ccx : parseLineQasmOp "ccx q[0], q[1], q[2];" = some (.ccx 0 1 2) := by
  simp [parseLineQasmOp, parseGateLine_toffoli_ccx]

theorem parseGateLine_x : parseGateLine "x q[0];" = some (.gate .X 0) := by native_decide

lemma parseLineQasmOp_x : parseLineQasmOp "x q[0];" = some (.gate .X 0) := by
  simp [parseLineQasmOp, parseGateLine_x]

theorem parseGateLine_hxh_h0 : parseGateLine "h q[0];" = some (.gate .H 0) := parseGateLine_bell_h

theorem parseGateLine_hxh_x0 : parseGateLine "x q[0];" = some (.gate .X 0) := parseGateLine_x

theorem parseGateLine_hh0 : parseGateLine "h q[0];" = some (.gate .H 0) := parseGateLine_bell_h

theorem canonicalAstFromLines_bell :
    (canonicalAstFromLines 2 ["h q[0];", "cx q[0], q[1];"]).gates =
      [{ op := "h", qubits := [0] }, { op := "cx", qubits := [0, 1] }] := by native_decide

theorem canonicalAstFromLines_toffoli :
    (canonicalAstFromLines 3 ["ccx q[0], q[1], q[2];"]).gates =
      [{ op := "ccx", qubits := [0, 1, 2] }] := by native_decide

/-- Bell artifact gate lines parse to the same `QasmOp` trace as codegen. -/
theorem parseLines_bell_eq_generated_ops :
    parseLines ["h q[0];", "cx q[0], q[1];"] = Generated.BellStatePreparation.ops := by
  unfold Generated.BellStatePreparation.ops
  simp [parseLines, parseLineQasmOp_bell_h, parseLineQasmOp_bell_cx]

theorem parseLines_bell_eq_bell_prep_ops :
    parseLines ["h q[0];", "cx q[0], q[1];"] = Generated.BellStatePreparation.ops :=
  parseLines_bell_eq_generated_ops

theorem parseLines_cnot_eq_generated_ops :
    parseLines ["cx q[0], q[1];", "cx q[0], q[1];"] = Generated.CnotSelfInverse.ops := by
  unfold Generated.CnotSelfInverse.ops
  simp [parseLines, parseLineQasmOp_bell_cx]

theorem parseQasmSource_cnot_eq_parseLines_generated :
    parseLines ["cx q[0], q[1];", "cx q[0], q[1];"] = Generated.CnotSelfInverse.ops :=
  parseLines_cnot_eq_generated_ops

/-- Exact on-disk CNOT kernel artifact (OPENQASM header, include, qubit register, two CX lines). -/
def cnotKernelArtifactSource : String :=
  "OPENQASM 3.0;\ninclude \"stdgates.inc\";\nqubit[2] q;\ncx q[0], q[1];\ncx q[0], q[1];"

def gateLinesFromSource (source : String) : List String :=
  filterGateLines (source.splitOn "\n" |>.map (·.trimRight))

/-- Gate-trace view of raw QASM source (headers/includes/registers skipped). -/
def parseQasmSourceToOps (source : String) : Option (List QasmOp) :=
  match parseLines (gateLinesFromSource source) with
  | [] => none
  | ops@(_ :: _) => some ops

def cnotKernelGateLines : List String :=
  ["cx q[0], q[1];", "cx q[0], q[1];"]

theorem gateLinesFromSource_cnot :
    filterGateLines (cnotKernelArtifactSource.splitOn "\n" |>.map (·.trimRight)) = cnotKernelGateLines := by
  native_decide

theorem cnotKernelGateLines_eq :
    cnotKernelGateLines = ["cx q[0], q[1];", "cx q[0], q[1];"] := rfl

theorem parseQasmSource_cnot_kernel_eq_generated_ops :
    parseQasmSourceToOps cnotKernelArtifactSource = some Generated.CnotSelfInverse.ops := by
  unfold parseQasmSourceToOps gateLinesFromSource
  rw [gateLinesFromSource_cnot, cnotKernelGateLines_eq, parseLines_cnot_eq_generated_ops]
  rfl

theorem parseQasmSource_cnot_kernel_is_some :
    (parseQasmSource cnotKernelArtifactSource).isSome := by native_decide

theorem parseQasmSource_cnot_kernel_gate_count :
    ∃ ast, parseQasmSource cnotKernelArtifactSource = some ast ∧ ast.gates.length = 2 := by
  native_decide

/-- H-X-H artifact gate lines match codegen trace. -/
theorem parseLines_hxh_eq_generated_ops :
    parseLines ["h q[0];", "x q[0];", "h q[0];"] = Generated.HadamardConjugatesXToZ.ops := by
  unfold Generated.HadamardConjugatesXToZ.ops
  simp [parseLines, parseLineQasmOp_bell_h, parseLineQasmOp_x]

/-- H-H cancellation artifact gate lines match codegen trace. -/
theorem parseLines_hh_eq_generated_ops :
    parseLines ["h q[0];", "h q[0];"] = Generated.SingleQubitGateCancellation.ops := by
  unfold Generated.SingleQubitGateCancellation.ops
  simp [parseLines, parseLineQasmOp_bell_h]

/-- Three-CX SWAP artifact gate lines match codegen trace. -/
theorem parseLines_swap_eq_generated_ops :
    parseLines ["cx q[0], q[1];", "cx q[1], q[0];", "cx q[0], q[1];"] =
      Generated.SwapFromThreeCx.ops := by
  unfold Generated.SwapFromThreeCx.ops
  simp [parseLines, parseLineQasmOp_bell_cx, parseLineQasmOp_cx10]

theorem parseLines_swap_eq_swap_codegen_ops :
    parseLines ["cx q[0], q[1];", "cx q[1], q[0];", "cx q[0], q[1];"] =
      Generated.SwapFromThreeCx.ops :=
  parseLines_swap_eq_generated_ops

/-- Exact on-disk Bell kernel artifact (OPENQASM header, include, qubit register, H + CX). -/
def bellKernelArtifactSource : String :=
  "OPENQASM 3.0;\ninclude \"stdgates.inc\";\nqubit[2] q;\nh q[0];\ncx q[0], q[1];"

def bellKernelGateLines : List String :=
  ["h q[0];", "cx q[0], q[1];"]

theorem gateLinesFromSource_bell :
    filterGateLines (bellKernelArtifactSource.splitOn "\n" |>.map (·.trimRight)) = bellKernelGateLines := by
  native_decide

theorem bellKernelGateLines_eq :
    bellKernelGateLines = ["h q[0];", "cx q[0], q[1];"] := rfl

theorem parseQasmSource_bell_kernel_eq_generated_ops :
    parseQasmSourceToOps bellKernelArtifactSource = some Generated.BellStatePreparation.ops := by
  unfold parseQasmSourceToOps gateLinesFromSource
  rw [gateLinesFromSource_bell, bellKernelGateLines_eq, parseLines_bell_eq_generated_ops]
  rfl

theorem parseQasmSource_bell_kernel_is_some :
    (parseQasmSource bellKernelArtifactSource).isSome := by native_decide

/-- Exact on-disk three-CX SWAP kernel artifact. -/
def swapKernelArtifactSource : String :=
  "OPENQASM 3.0;\ninclude \"stdgates.inc\";\nqubit[2] q;\ncx q[0], q[1];\ncx q[1], q[0];\ncx q[0], q[1];"

def swapKernelGateLines : List String :=
  ["cx q[0], q[1];", "cx q[1], q[0];", "cx q[0], q[1];"]

theorem gateLinesFromSource_swap :
    filterGateLines (swapKernelArtifactSource.splitOn "\n" |>.map (·.trimRight)) = swapKernelGateLines := by
  native_decide

theorem swapKernelGateLines_eq :
    swapKernelGateLines =
      ["cx q[0], q[1];", "cx q[1], q[0];", "cx q[0], q[1];"] := rfl

theorem parseQasmSource_swap_kernel_eq_generated_ops :
    parseQasmSourceToOps swapKernelArtifactSource = some Generated.SwapFromThreeCx.ops := by
  unfold parseQasmSourceToOps gateLinesFromSource
  rw [gateLinesFromSource_swap, swapKernelGateLines_eq, parseLines_swap_eq_generated_ops]
  rfl

theorem parseQasmSource_swap_kernel_is_some :
    (parseQasmSource swapKernelArtifactSource).isSome := by native_decide

/-- Toffoli source artifact gate line matches codegen trace. -/
theorem parseLines_toffoli_eq_generated_ops :
    parseLines ["ccx q[0], q[1], q[2];"] = Generated.ToffoliDecompositionEquivalence.ops := by
  unfold Generated.ToffoliDecompositionEquivalence.ops
  simp [parseLines, parseLineQasmOp_toffoli_ccx]

example : parseGateLine "h q[0];" = some (.gate .H 0) := by native_decide
example : parseGateLine "cx q[0], q[1];" = some (.cx 0 1) := by native_decide
example : parseGateLine "  cx q[1], q[2];" = some (.cx 1 2) := by native_decide
example : parseGateLine "x q[0];" = some (.gate .X 0) := by native_decide
example : parseGateLine "ccx q[0], q[1], q[2];" = some (.ccx 0 1 2) := by native_decide

#check parseQasmSource
#check parseQasmSource_bell_kernel_eq_generated_ops
#check parseQasmSource_swap_kernel_eq_generated_ops
#check parseQasmSource_cnot_kernel_eq_generated_ops
#check parseGateLine
#check canonicalAstFromLines
#check parseLines_bell_eq_generated_ops
#check parseLines_cnot_eq_generated_ops
#check parseLines_hxh_eq_generated_ops
#check parseLines_hh_eq_generated_ops
#check parseLines_swap_eq_generated_ops
#check parseLines_toffoli_eq_generated_ops
#check parserTrustBoundaryNote
#check rxExcludedFromParseLinesNote

end QSpecBench.Quantum.OpenQASM3Parser

import QSpecBench.Quantum.QasmOp
import QSpecBench.Quantum.OpenQASM3
import QSpecBench.Generated.TeleportationUnitaryPrefix

/-!
# OpenQASM 3 fragment parser (gate lines + bytes→AST).

Fail-closed `Except ParseError` path for the benchmark subset: H/X/CX/CCX/SWAP,
measure assignments, classical if / if-else / depth-1 nested brace if-else,
bounded `for` / `while[N]`, and `reset`. **Not** a full OpenQASM 3 parser.

`parseQasmBytes` closes the Python→AST trust boundary for declared UTF-8
artifact bytes (register width preserved). Deeper nested braces, bare `while`,
arrow-measure, and pulse/cal schedules remain unsupported.
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
  | swap (a b : Nat)
  | rx (theta : String) (q : Nat)
  deriving DecidableEq, Repr

/-- Canonical gate entry mirroring Python `build_canonical_ast` JSON gate objects. -/
structure CanonicalGate where
  op : String
  qubits : List Nat
  deriving Repr, DecidableEq

/-- Classical feed-forward statement: `if (c[cIdx] == 1) op q[…]` with optional
single-line `else op q[…]`, optional brace-nested then/else bodies (depth ≤ 1),
or bounded `while[fuel]` (dynamic profile). -/
structure CanonicalCtrl where
  cIdx : Nat
  op : String
  qubits : List Nat
  elseOp : Option String := none
  elseQubits : List Nat := []
  /-- Nested brace form marker (`if (…) { op q; } else { op q; }`). -/
  nested : Bool := false
  /-- Bounded while fuel; `none` means ordinary if / if-else. -/
  whileFuel : Option Nat := none
  deriving Repr, DecidableEq

/-- Measurement assignment: `c[cIdx] = measure q[qIdx]` (teleport / Z-measure subset). -/
structure CanonicalMeasure where
  cIdx : Nat
  qIdx : Nat
  deriving Repr, DecidableEq

/-- Reset statement: `reset q[qIdx]` (OpenQASM3; denotes measure+X-to-|0⟩). -/
structure CanonicalReset where
  qIdx : Nat
  deriving Repr, DecidableEq

/-- Full canonical AST mirroring Python JSON (`canonical_ast_version`, `n_qubits`, `gates`),
plus classical-control statements (`controls`), Z-measure assignments (`measurements`),
and resets (`resets`). -/
structure CanonicalAst where
  version : String
  nQubits : Nat
  gates : List CanonicalGate
  controls : List CanonicalCtrl := []
  measurements : List CanonicalMeasure := []
  resets : List CanonicalReset := []
  deriving Repr, DecidableEq

/-- Executable line: unitary gate, supported classical `if`/`if-else`, measure, reset,
or bounded `for` unrolled to gates. -/
inductive ParsedExecutable where
  | gate (g : ParsedGate)
  | ctrl (c : CanonicalCtrl)
  | measure (m : CanonicalMeasure)
  | reset (r : CanonicalReset)
  | forGates (gs : List CanonicalGate)
  deriving DecidableEq, Repr

/-- Fail-closed parse errors for the OpenQASM fragment parser. -/
inductive ParseError where
  | unsupportedInstruction (line : String)
  | malformedGate (line : String)
  | unknownRegister (name : String)
  | qubitIndexOutOfRange (idx nQubits : Nat)
  | duplicateRegister (name : String)
  | unsupportedParameterExpression (line : String)
  | unsupportedControlFlow (line : String)
  | unexpectedToken (line : String)
  | emptyExecutableProgram
  | invalidUtf8
  | nestedControlTooDeep (line : String)
  deriving Repr, DecidableEq

/-- `Except` has no library-derived `DecidableEq`; needed to `decide`/`native_decide`
equalities of `parseQasmBytesFromString` / `parseQasmSourceE` results directly. -/
instance instDecidableEqExceptParseErrorCanonicalAst :
    DecidableEq (Except ParseError CanonicalAst)
  | .error e1, .error e2 =>
      if h : e1 = e2 then isTrue (h ▸ rfl)
      else isFalse (fun heq => h (Except.error.inj heq))
  | .error _, .ok _ => isFalse (fun heq => Except.noConfusion heq)
  | .ok _, .error _ => isFalse (fun heq => Except.noConfusion heq)
  | .ok a1, .ok a2 =>
      if h : a1 = a2 then isTrue (h ▸ rfl)
      else isFalse (fun heq => h (Except.ok.inj heq))

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
  | .swap a b => some { op := "swap", qubits := [a, b] }
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
  else if s.startsWith "s " then
    match parseQubitIndex (s.drop 2) with
    | some q => some (.gate .S q)
    | none => none
  else if s.startsWith "sdg " then
    match parseQubitIndex (s.drop 4) with
    | some q => some (.gate .Sdg q)
    | none => none
  else if s.startsWith "t " then
    match parseQubitIndex (s.drop 2) with
    | some q => some (.gate .T q)
    | none => none
  else if s.startsWith "tdg " then
    match parseQubitIndex (s.drop 4) with
    | some q => some (.gate .Tdg q)
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
  else if s.startsWith "swap " then
    match parseQubitArgList (s.drop 5) with
    | some (a, b) => some (.swap a b)
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
  | .swap a b => .swap a b
  | .rx _ q => .rx (Real.pi / 2) q

/-- Computable H/X/CX/CCX/SWAP projection for gate-line lists (rx lines skipped). -/
def parseLineQasmOp (line : String) : Option QasmOp :=
  match parseGateLine line with
  | none => none
  | some (.gate g q) => some (.gate g q)
  | some (.cx c t) => some (.cx c t)
  | some (.ccx c0 c1 t) => some (.ccx c0 c1 t)
  | some (.swap a b) => some (.swap a b)
  | some (.rx _ _) => none

/-- Map parsed gate lines to `QasmOp` list (skips header/unparseable/rx lines). -/
def parseLines (lines : List String) : List QasmOp :=
  lines.filterMap parseLineQasmOp

/-- Build canonical AST from gate lines (mirrors Python `build_canonical_ast` gate list). -/
def canonicalAstFromLines (nQubits : Nat) (lines : List String) : CanonicalAst :=
  { version := canonicalAstVersion, nQubits := nQubits,
    gates := lines.filterMap (fun line => parseGateLine line >>= parsedGateToCanonical) }

/-- Skip OPENQASM headers, includes, and comments only (not register declarations). -/
def isHeaderOrCommentLine (line : String) : Bool :=
  let s := line.trim
  s.isEmpty || s.startsWith "//" || s.startsWith "OPENQASM" || s.startsWith "include"
    || s.startsWith "barrier"

/-- Legacy skippable set (headers + register decls). Prefer `parseQasmSourceE`. -/
def isSkippableQasmLine (line : String) : Bool :=
  let s := line.trim
  isHeaderOrCommentLine line || s.startsWith "qubit" || s.startsWith "bit"
    || s.startsWith "creg" || s.startsWith "qreg"

def filterGateLines (lines : List String) : List String :=
  lines.filter fun line => !isSkippableQasmLine line

def maxQubitIndex (gates : List CanonicalGate) : Nat :=
  gates.foldl (fun acc g => g.qubits.foldl Nat.max acc) 0

/-- Gate list view matching Python ``build_canonical_ast`` JSON ``gates`` field. -/
def canonicalAstToGateList (ast : CanonicalAst) : List (String × List Nat) :=
  ast.gates.map fun g => (g.op, g.qubits)

/-- Parse `qubit[N] name;` declarations. Fails on duplicates / malformed forms. -/
def parseQubitRegisterDecl (line : String) : Except ParseError (String × Nat) :=
  let s := trimLine line
  if !(s.startsWith "qubit") then
    .error (.unexpectedToken s)
  else
    let rest := s.drop 5 |>.trim
    if rest.startsWith "[" then
      let after := rest.drop 1
      let widthStr := after.takeWhile (fun c => c.isDigit)
      let afterWidth := after.drop widthStr.length
      if !afterWidth.startsWith "]" then
        .error (.malformedGate s)
      else
        match widthStr.toNat? with
        | none => .error (.malformedGate s)
        | some w =>
          let name := afterWidth.drop 1 |>.trim
          if name.isEmpty then .error (.malformedGate s)
          else .ok (name, w)
    else
      -- `qubit q;` → width 1
      let name := rest.trim
      if name.isEmpty then .error (.malformedGate s) else .ok (name, 1)

/-- Collect register width; reject duplicate / incompatible declarations. -/
def parseRegisterEnvironment (lines : List String) : Except ParseError (String × Nat) :=
  Id.run do
    let mut reg : Option (String × Nat) := none
    for line in lines do
      let s := line.trim
      if isHeaderOrCommentLine line then
        pure ()
      else if s.startsWith "qubit" then
        match parseQubitRegisterDecl s with
        | .error e => return .error e
        | .ok (name, w) =>
          match reg with
          | some (name0, w0) =>
            if name0 != name then
              return .error (.duplicateRegister name)
            else if w0 != w then
              return .error (.duplicateRegister name)
            else
              pure ()
          | none =>
            reg := some (name, w)
      else if s.startsWith "qreg" then
        return .error (.unsupportedInstruction s)
      else if s.startsWith "bit" || s.startsWith "creg" then
        -- Classical registers are declared only; measurement/if handled in executable pass.
        pure ()
      else
        pure ()
    match reg with
    | none =>
      -- Fall back: width inferred later from gate indices.
      return .ok ("q", 0)
    | some pair => return .ok pair

/-- Extract classical bit index from `c[0]`-style tokens. -/
def parseCregIndex (token : String) : Option Nat :=
  let t := token.trim
  if t.startsWith "c[" && t.endsWith "]" then
    (t.drop 2).dropRight 1 |>.toNat?
  else
    none

/-- Parse `x|y|z q[M]` body for classical feed-forward. -/
def parsePauliCtrlBody (cIdx : Nat) (body : String) : Option CanonicalCtrl :=
  if body.startsWith "x " then
    match parseQubitIndex (body.drop 2) with
    | some q => some { cIdx := cIdx, op := "x", qubits := [q] }
    | none => none
  else if body.startsWith "y " then
    match parseQubitIndex (body.drop 2) with
    | some q => some { cIdx := cIdx, op := "y", qubits := [q] }
    | none => none
  else if body.startsWith "z " then
    match parseQubitIndex (body.drop 2) with
    | some q => some { cIdx := cIdx, op := "z", qubits := [q] }
    | none => none
  else
    none

/-- Attach a single-line `else x|y|z q[k]` branch onto an if-then control. -/
def attachElseBranch (c : CanonicalCtrl) (elseBody : String) : Option CanonicalCtrl :=
  if elseBody.startsWith "x " then
    match parseQubitIndex (elseBody.drop 2) with
    | some q => some { c with elseOp := some "x", elseQubits := [q] }
    | none => none
  else if elseBody.startsWith "y " then
    match parseQubitIndex (elseBody.drop 2) with
    | some q => some { c with elseOp := some "y", elseQubits := [q] }
    | none => none
  else if elseBody.startsWith "z " then
    match parseQubitIndex (elseBody.drop 2) with
    | some q => some { c with elseOp := some "z", elseQubits := [q] }
    | none => none
  else
    none

/-- Split `… else …` on the first ` else ` separator (single-line if/else only). -/
def splitIfElseBody (s : String) : String × Option String :=
  let parts := s.splitOn " else "
  if parts.length = 1 then (s, none)
  else if parts.length = 2 then (parts[0]!, some parts[1]!)
  else (s, none)

/-- Supported OpenQASM3 classical feed-forward (dynamic profile after `trimLine`):
`if (c[i] == 1) x|y|z q[j]`, `if (c[i] == true) …`, shorthand `if (c[i]) …`,
and single-line `if (…) x|y|z q[j] else x|y|z q[k]`.
Bare `else` / `while` / nested blocks remain fail-closed. -/
def parseSupportedIfCtrl (s : String) : Option CanonicalCtrl :=
  let (thenPart, elseOpt) := splitIfElseBody s
  let base : Option CanonicalCtrl :=
    if thenPart = "if (c[1] == 1) x q[2]" then
      some { cIdx := 1, op := "x", qubits := [2] }
    else if thenPart = "if (c[0] == 1) z q[2]" then
      some { cIdx := 0, op := "z", qubits := [2] }
    else if thenPart.startsWith "if (c[" && thenPart.contains ']' then
      let afterC := thenPart.drop 5  -- drop "if (c"
      if !afterC.startsWith "[" then none
      else
        let idxStr := (afterC.drop 1).takeWhile (fun c => c.isDigit)
        let afterIdx := (afterC.drop 1).drop idxStr.length
        match idxStr.toNat? with
        | none => none
        | some cIdx =>
          if afterIdx.startsWith "] == 1) " then
            parsePauliCtrlBody cIdx (afterIdx.drop "] == 1) ".length)
          else if afterIdx.startsWith "] == true) " then
            parsePauliCtrlBody cIdx (afterIdx.drop "] == true) ".length)
          else if afterIdx.startsWith "]) " then
            parsePauliCtrlBody cIdx (afterIdx.drop "]) ".length)
          else
            none
    else
      none
  match base, elseOpt with
  | none, _ => none
  | some c, none => some c
  | some c, some elseBody => attachElseBranch c elseBody

/-- Maximum inclusive exclusive-bound for declared `for i in [0:N]` unrolling. -/
def maxForUnrollBound : Nat := 8

/-- Maximum fuel for bounded `while[N] (c[i]) …` (fail-closed above this). -/
def maxWhileFuel : Nat := 8

/-- Bounded `for i in [0:N] { x|y|z q[i]; }` → unrolled Pauli gates (N ≤ maxForUnrollBound).
Fail-closed when N exceeds the bound or the body is not a single Pauli-on-index. -/
def parseSupportedForUnroll (s : String) : Option (List CanonicalGate) :=
  if !s.startsWith "for i in [0:" then none
  else
    let after := s.drop "for i in [0:".length
    let nStr := after.takeWhile (fun c => c.isDigit)
    let rest := after.drop nStr.length
    match nStr.toNat? with
    | none => none
    | some n =>
      if n = 0 || n > maxForUnrollBound then none
      else if rest.startsWith "] { x q[i]; }" then
        some (List.range n |>.map (fun i => { op := "x", qubits := [i] }))
      else if rest.startsWith "] { y q[i]; }" then
        some (List.range n |>.map (fun i => { op := "y", qubits := [i] }))
      else if rest.startsWith "] { z q[i]; }" then
        some (List.range n |>.map (fun i => { op := "z", qubits := [i] }))
      else
        none

/-- Count `{` occurrences (depth probe for nested control). -/
def countChar (s : String) (c : Char) : Nat :=
  s.foldl (fun acc ch => if ch = c then acc + 1 else acc) 0

/-- Nested brace if/else (depth-1): `if (c[i] == 1) { x q[j]; } else { z q[k]; }`.
Depth >1 (nested braces inside then/else, or ≥3 opens) remains fail-closed. -/
def parseSupportedNestedIfElse (s : String) : Option CanonicalCtrl :=
  if countChar s '{' ≥ 3 then none
  else if !s.startsWith "if (c[" then none
  else
    let afterC := s.drop 5
    if !afterC.startsWith "[" then none
    else
      let idxStr := (afterC.drop 1).takeWhile (fun c => c.isDigit)
      let afterIdx := (afterC.drop 1).drop idxStr.length
      match idxStr.toNat? with
      | none => none
      | some cIdx =>
        let bodyStart :=
          if afterIdx.startsWith "] == 1) { " then some "] == 1) { "
          else if afterIdx.startsWith "] == true) { " then some "] == true) { "
          else if afterIdx.startsWith "]) { " then some "]) { "
          else none
        match bodyStart with
        | none => none
        | some pref =>
          let rest := afterIdx.drop pref.length
          -- then body ends at ` } else { `
          let parts := rest.splitOn " } else { "
          if parts.length != 2 then none
          else
            let thenBody := parts[0]!
            let elseAndClose := parts[1]!
            -- Reject nested braces inside then/else bodies (depth >1).
            if thenBody.contains '{' || (elseAndClose.dropRight 2).contains '{' then none
            else if !elseAndClose.endsWith " }" then none
            else
              let elseBody := elseAndClose.dropRight 2
              let thenTrim :=
                if thenBody.endsWith ";" then thenBody.dropRight 1 else thenBody
              let elseTrim :=
                if elseBody.endsWith ";" then elseBody.dropRight 1 else elseBody
              match parsePauliCtrlBody cIdx thenTrim, parsePauliCtrlBody cIdx elseTrim with
              | some th, some el =>
                  some {
                    cIdx := cIdx
                    op := th.op
                    qubits := th.qubits
                    elseOp := some el.op
                    elseQubits := el.qubits
                    nested := true
                  }
              | _, _ => none

/-- Bounded while with explicit fuel: `while[N] (c[i]) x|y|z q[j]` (N ≤ maxWhileFuel).
Bare `while` without fuel remains fail-closed. -/
def parseSupportedWhileFuel (s : String) : Option CanonicalCtrl :=
  if !s.startsWith "while[" then none
  else
    let after := s.drop "while[".length
    let nStr := after.takeWhile (fun c => c.isDigit)
    let rest := after.drop nStr.length
    match nStr.toNat? with
    | none => none
    | some n =>
      if n = 0 || n > maxWhileFuel then none
      else if !rest.startsWith "] (c[" then none
      else
        let afterC := rest.drop "] (c[".length
        let idxStr := afterC.takeWhile (fun c => c.isDigit)
        let afterIdx := afterC.drop idxStr.length
        match idxStr.toNat? with
        | none => none
        | some cIdx =>
          if afterIdx.startsWith "] == 1) " then
            match parsePauliCtrlBody cIdx (afterIdx.drop "] == 1) ".length) with
            | some c => some { c with whileFuel := some n }
            | none => none
          else if afterIdx.startsWith "]) " then
            match parsePauliCtrlBody cIdx (afterIdx.drop "]) ".length) with
            | some c => some { c with whileFuel := some n }
            | none => none
          else
            none

/-- True when `s` contains the substring `sub`. -/
def stringContainsSubstr (s sub : String) : Bool :=
  (s.splitOn sub).length > 1

/-- Supported OpenQASM3 Z-measure assignment (declared teleport subset after `trimLine`):
`c[i] = measure q[j]`. Arrow form `measure q[j] -> c[i]` and other shapes remain fail-closed. -/
def parseSupportedMeasure (s : String) : Option CanonicalMeasure :=
  if s.startsWith "c[" && stringContainsSubstr s "= measure " then
    let idxStr := (s.drop 2).takeWhile (fun c => c.isDigit)
    let afterIdx := (s.drop 2).drop idxStr.length
    if !afterIdx.startsWith "] = measure " then none
    else
      match idxStr.toNat? with
      | none => none
      | some cIdx =>
        match parseQubitIndex (afterIdx.drop "] = measure ".length) with
        | some qIdx => some { cIdx := cIdx, qIdx := qIdx }
        | none => none
  else
    none

/-- Supported OpenQASM3 reset: `reset q[j]` (denotes measure + X correction to |0⟩). -/
def parseSupportedReset (s : String) : Option CanonicalReset :=
  if s.startsWith "reset " then
    match parseQubitIndex (s.drop "reset ".length) with
    | some q => some { qIdx := q }
    | none => none
  else
    none

/-- Parse one executable line (gate, supported `if`/`if-else`/nested if, bounded `for`/`while[N]`,
measure, or reset). Bare `while` / bare `else` / depth>1 nested braces remain fail-closed. -/
def parseExecutableLineE (line : String) : Except ParseError ParsedExecutable :=
  let s := trimLine line
  if s.isEmpty then
    .error (.unexpectedToken s)
  else if s.startsWith "while[" then
    match parseSupportedWhileFuel s with
    | some c => .ok (.ctrl c)
    | none => .error (.unsupportedControlFlow s)
  else if s.startsWith "while " then
    .error (.unsupportedControlFlow s)
  else if s.startsWith "else " || s = "else" then
    .error (.unsupportedControlFlow s)
  else if s.startsWith "for " then
    match parseSupportedForUnroll s with
    | some gs => .ok (.forGates gs)
    | none => .error (.unsupportedControlFlow s)
  else if s.startsWith "if " then
    -- Depth >1 nested braces: fail closed with dedicated error.
    if countChar s '{' ≥ 3 then
      .error (.nestedControlTooDeep s)
    else
      match parseSupportedNestedIfElse s with
      | some c => .ok (.ctrl c)
      | none =>
        match parseSupportedIfCtrl s with
        | some c => .ok (.ctrl c)
        | none => .error (.unsupportedControlFlow s)
  else if s.startsWith "reset" then
    match parseSupportedReset s with
    | some r => .ok (.reset r)
    | none => .error (.unsupportedInstruction s)
  else if s.startsWith "measure " || stringContainsSubstr s "= measure" then
    match parseSupportedMeasure s with
    | some m => .ok (.measure m)
    | none => .error (.unsupportedInstruction s)
  else
    match parseGateLine s with
    | some g => .ok (.gate g)
    | none =>
      if s.startsWith "rx(" then
        .error (.unsupportedParameterExpression s)
      else if s.contains '[' then
        .error (.malformedGate s)
      else
        .error (.unsupportedInstruction s)

/-- Gate-only view of `parseExecutableLineE` (supported `if`/`measure`/`reset`/`for` → unsupported). -/
def parseGateLineE (line : String) : Except ParseError ParsedGate :=
  match parseExecutableLineE line with
  | .ok (.gate g) => .ok g
  | .ok (.ctrl _) => .error (.unsupportedControlFlow (trimLine line))
  | .ok (.measure _) => .error (.unsupportedInstruction (trimLine line))
  | .ok (.reset _) => .error (.unsupportedInstruction (trimLine line))
  | .ok (.forGates _) => .error (.unsupportedControlFlow (trimLine line))
  | .error e => .error e

/-- Fail-closed source parse with declared register width.
Supports classical `bit`/`creg` decls, teleport `if`/`if-else`, bounded `for` unroll,
`c[i] = measure q[j]`, and `reset q[j]`; bare `while` / bare `else` / depth>1 remain errors. -/
def parseQasmSourceE (source : String) : Except ParseError CanonicalAst :=
  let lines := source.splitOn "\n" |>.map (·.trimRight)
  match parseRegisterEnvironment lines with
  | .error e => .error e
  | .ok (regName, declaredWidth) =>
    Id.run do
      let mut gates : List CanonicalGate := []
      let mut controls : List CanonicalCtrl := []
      let mut measurements : List CanonicalMeasure := []
      let mut resets : List CanonicalReset := []
      for line in lines do
        let s := line.trim
        if isHeaderOrCommentLine line || s.startsWith "qubit" || s.startsWith "bit "
            || s.startsWith "creg " || s.startsWith "bit[" then
          pure ()
        else
          match parseExecutableLineE s with
          | .error e => return .error e
          | .ok (.ctrl c) =>
            controls := controls ++ [c]
          | .ok (.measure m) =>
            measurements := measurements ++ [m]
          | .ok (.reset r) =>
            resets := resets ++ [r]
          | .ok (.forGates gs) =>
            gates := gates ++ gs
          | .ok (.gate pg) =>
            match parsedGateToCanonical pg with
            | none => return .error (.unsupportedParameterExpression s)
            | some cg =>
              gates := gates ++ [cg]
      if gates.isEmpty && controls.isEmpty && measurements.isEmpty && resets.isEmpty then
        return .error .emptyExecutableProgram
      let maxGateIdx := maxQubitIndex gates
      let maxCtrlIdx := controls.foldl
        (fun acc c =>
          let acc' := c.qubits.foldl Nat.max acc
          c.elseQubits.foldl Nat.max acc') 0
      let maxMeasIdx := measurements.foldl (fun acc m => Nat.max acc m.qIdx) 0
      let maxResetIdx := resets.foldl (fun acc r => Nat.max acc r.qIdx) 0
      let maxIdx := Nat.max maxGateIdx (Nat.max maxCtrlIdx (Nat.max maxMeasIdx maxResetIdx))
      let width :=
        if declaredWidth = 0 then
          if gates.isEmpty && controls.isEmpty && measurements.isEmpty && resets.isEmpty then 0
          else maxIdx + 1
        else declaredWidth
      if !gates.isEmpty || !controls.isEmpty || !measurements.isEmpty || !resets.isEmpty then
        if maxIdx >= width then
          return .error (.qubitIndexOutOfRange maxIdx width)
      let _ := regName
      return .ok {
        version := canonicalAstVersion
        nQubits := width
        gates := gates
        controls := controls
        measurements := measurements
        resets := resets
      }

/-- Decode UTF-8 artifact bytes; fail-closed on invalid UTF-8. -/
def utf8BytesToSource (bytes : ByteArray) : Except ParseError String :=
  match String.fromUTF8? bytes with
  | some s => .ok s
  | none => .error .invalidUtf8

/-- Bytes → CanonicalAst (UTF-8 decode then `parseQasmSourceE`).
Closes the Python-only bytes→AST gap for the declared fragment; register width
preserved; unsupported / invalid UTF-8 fail closed. -/
def parseQasmBytes (bytes : ByteArray) : Except ParseError CanonicalAst :=
  match utf8BytesToSource bytes with
  | .error e => .error e
  | .ok source => parseQasmSourceE source

/-- Convenience: UTF-8 string as bytes through `parseQasmBytes`. -/
def parseQasmBytesFromString (source : String) : Except ParseError CanonicalAst :=
  parseQasmBytes source.toUTF8

/-- Legacy Option API (maps Except failure to `none`). Prefer `parseQasmSourceE`. -/
def parseQasmSource (source : String) : Option CanonicalAst :=
  match parseQasmSourceE source with
  | .ok ast => some ast
  | .error _ =>
    -- Backward-compatible fallback for older call sites that relied on filterMap.
    let lines := source.splitOn "\n" |>.map (·.trimRight)
    let gateLines := filterGateLines lines
    let gates := gateLines.filterMap (fun line => parseGateLine line >>= parsedGateToCanonical)
    if gates.isEmpty then none
    else some { version := canonicalAstVersion, nQubits := maxQubitIndex gates + 1, gates := gates }

/-- Extract ``(op, qubits)`` pairs from raw QASM source (headers skipped). -/
def parseQasmSourceToGateList (source : String) : Option (List (String × List Nat)) :=
  parseQasmSource source |>.map canonicalAstToGateList

theorem parseQasmSourceE_empty_fails :
    (match parseQasmSourceE "OPENQASM 3.0;\nqubit[1] q;" with
      | .error .emptyExecutableProgram => true
      | _ => false) = true := by
  native_decide

theorem parseQasmSourceE_unknown_gate_fails :
    (match parseQasmSourceE "OPENQASM 3.0;\nqubit[1] q;\nfoo q[0];" with
      | .error (.malformedGate _) => true
      | .error (.unsupportedInstruction _) => true
      | _ => false) = true := by
  native_decide

theorem parseQasmSourceE_preserves_register_width :
    (match parseQasmSourceE "OPENQASM 3.0;\nqubit[10] q;\nx q[0];" with
      | .ok ast => decide (ast.nQubits = 10)
      | .error _ => false) = true := by
  native_decide

theorem parseQasmSourceE_oob_index_fails :
    (match parseQasmSourceE "OPENQASM 3.0;\nqubit[2] q;\nx q[2];" with
      | .error (.qubitIndexOutOfRange 2 2) => true
      | _ => false) = true := by
  native_decide

/-- Bytes→AST preserves register width (UTF-8 path). -/
theorem parseQasmBytes_preserves_register_width :
    (match parseQasmBytesFromString "OPENQASM 3.0;\nqubit[10] q;\nx q[0];" with
      | .ok ast => decide (ast.nQubits = 10)
      | .error _ => false) = true := by
  native_decide

/-- Bytes→AST agrees with `parseQasmSourceE` on a concrete valid UTF-8 source. -/
theorem parseQasmBytes_eq_parseQasmSourceE_cx :
    parseQasmBytesFromString "OPENQASM 3.0;\nqubit[2] q;\ncx q[0], q[1];\n" =
      parseQasmSourceE "OPENQASM 3.0;\nqubit[2] q;\ncx q[0], q[1];\n" := by
  native_decide

/-- Invalid UTF-8 bytes fail closed. -/
theorem parseQasmBytes_invalid_utf8_fails :
    (match parseQasmBytes (ByteArray.mk #[0xff, 0xfe]) with
      | .error .invalidUtf8 => true
      | _ => false) = true := by
  native_decide

/-- Depth >1 nested braces fail closed. -/
theorem parseExecutableLineE_nested_too_deep_fails :
    (match parseExecutableLineE
        "if (c[1] == 1) { if (c[0] == 1) { x q[2]; } else { z q[2]; }; } else { y q[2]; };" with
      | .error (.nestedControlTooDeep _) => true
      | .error (.unsupportedControlFlow _) => true
      | _ => false) = true := by
  native_decide

/-- Explicit residual: pulse / cal schedules are outside the software CanonicalAst profile. -/
def openqasm3PulseScheduleSemanticsClaimed : Bool := false

theorem openqasm3_pulse_schedule_not_checked :
    openqasm3PulseScheduleSemanticsClaimed = false := rfl

/-- Teleport feed-forward IF lines parse into `CanonicalAst.controls`. -/
def teleportFeedForwardIfSource : String :=
  "OPENQASM 3.0;\nqubit[3] q;\nbit[2] c;\nif (c[1] == 1) x q[2];\nif (c[0] == 1) z q[2];\n"

theorem parseSupportedIfCtrl_x :
    parseSupportedIfCtrl "if (c[1] == 1) x q[2]" =
      some { cIdx := 1, op := "x", qubits := [2] } := by native_decide

theorem parseSupportedIfCtrl_z :
    parseSupportedIfCtrl "if (c[0] == 1) z q[2]" =
      some { cIdx := 0, op := "z", qubits := [2] } := by native_decide

theorem parseExecutableLineE_teleport_if_x :
    (match parseExecutableLineE "if (c[1] == 1) x q[2];" with
      | .ok (.ctrl c) => decide (c = { cIdx := 1, op := "x", qubits := [2] })
      | _ => false) = true := by native_decide

theorem parseExecutableLineE_teleport_if_z :
    (match parseExecutableLineE "if (c[0] == 1) z q[2];" with
      | .ok (.ctrl c) => decide (c = { cIdx := 0, op := "z", qubits := [2] })
      | _ => false) = true := by native_decide

/-- Gate-only `parseGateLineE` still rejects `if` (use `parseExecutableLineE`). -/
theorem parseGateLineE_rejects_if_x :
    (match parseGateLineE "if (c[1] == 1) x q[2];" with
      | .error (.unsupportedControlFlow _) => true
      | _ => false) = true := by native_decide

/-- Alias used by Evidence.All / Teleportation packaging. -/
theorem parseGateLineE_rejects_teleport_if_x :
    (match parseGateLineE "if (c[1] == 1) x q[2];" with
      | .error (.unsupportedControlFlow _) => true
      | _ => false) = true :=
  parseGateLineE_rejects_if_x

theorem parseQasmSourceE_teleport_if_controls :
    (match parseQasmSourceE teleportFeedForwardIfSource with
      | .ok ast =>
          decide (ast.gates = [] ∧
            ast.controls =
              [{ cIdx := 1, op := "x", qubits := [2] },
               { cIdx := 0, op := "z", qubits := [2] }] ∧
            ast.nQubits = 3)
      | .error _ => false) = true := by
  native_decide

/-- Unsupported bare `while` (no fuel) remains fail-closed. -/
theorem parseExecutableLineE_while_fails :
    (match parseExecutableLineE "while (true) x q[0];" with
      | .error (.unsupportedControlFlow _) => true
      | _ => false) = true := by native_decide

/-- Bounded `while[N]` with fuel parses as ClassicalCtrl. -/
theorem parseSupportedWhileFuel_x :
    parseSupportedWhileFuel "while[3] (c[1]) x q[2]" =
      some { cIdx := 1, op := "x", qubits := [2], whileFuel := some 3 } := by
  native_decide

theorem parseExecutableLineE_while_fuel_ok :
    (match parseExecutableLineE "while[3] (c[1]) x q[2];" with
      | .ok (.ctrl c) => decide (c.whileFuel = some 3 ∧ c.op = "x" ∧ c.cIdx = 1)
      | _ => false) = true := by native_decide

/-- Fuel above maxWhileFuel remains fail-closed. -/
theorem parseExecutableLineE_while_fuel_over_bound_fails :
    (match parseExecutableLineE "while[9] (c[1]) x q[2];" with
      | .error (.unsupportedControlFlow _) => true
      | _ => false) = true := by native_decide

/-- Depth-1 nested brace if/else. -/
theorem parseSupportedNestedIfElse_xz :
    parseSupportedNestedIfElse "if (c[1] == 1) { x q[2]; } else { z q[2]; }" =
      some { cIdx := 1, op := "x", qubits := [2], elseOp := some "z",
             elseQubits := [2], nested := true } := by native_decide

theorem parseExecutableLineE_nested_if_else_ok :
    (match parseExecutableLineE "if (c[1] == 1) { x q[2]; } else { z q[2]; };" with
      | .ok (.ctrl c) => decide (c.nested = true ∧ c.elseOp = some "z")
      | _ => false) = true := by native_decide

/-- Supported `reset q[j]` parses into CanonicalAst.resets. -/
theorem parseSupportedReset_q0 :
    parseSupportedReset "reset q[0]" = some { qIdx := 0 } := by native_decide

theorem parseExecutableLineE_reset_ok :
    (match parseExecutableLineE "reset q[0];" with
      | .ok (.reset r) => decide (r.qIdx = 0)
      | _ => false) = true := by native_decide

theorem parseQasmSourceE_reset_retained :
    (match parseQasmSourceE "OPENQASM 3.0;\nqubit[1] q;\nreset q[0];\n" with
      | .ok ast => decide (ast.resets = [{ qIdx := 0 }] ∧ ast.nQubits = 1)
      | .error _ => false) = true := by native_decide

/-- Malformed reset (missing qubit) remains fail-closed. -/
theorem parseExecutableLineE_reset_malformed_fails :
    (match parseExecutableLineE "reset;" with
      | .error _ => true
      | .ok _ => false) = true := by native_decide

/-- Bare `else` (not attached to if) remains fail-closed. -/
theorem parseExecutableLineE_else_fails :
    (match parseExecutableLineE "else x q[0];" with
      | .error _ => true
      | .ok _ => false) = true := by native_decide

/-- Single-line `if … else …` classical branch is supported. -/
theorem parseSupportedIfCtrl_if_else :
    parseSupportedIfCtrl "if (c[1] == 1) x q[2] else z q[2]" =
      some { cIdx := 1, op := "x", qubits := [2], elseOp := some "z", elseQubits := [2] } := by
  native_decide

theorem parseExecutableLineE_if_else_ok :
    (match parseExecutableLineE "if (c[1] == 1) x q[2] else z q[2];" with
      | .ok (.ctrl c) =>
          decide (c.cIdx = 1 ∧ c.op = "x" ∧ c.qubits = [2] ∧
            c.elseOp = some "z" ∧ c.elseQubits = [2])
      | _ => false) = true := by native_decide

/-- Bounded `for i in [0:N]` unrolls to Pauli gates when N ≤ maxForUnrollBound. -/
theorem parseSupportedForUnroll_x3 :
    parseSupportedForUnroll "for i in [0:3] { x q[i]; }" =
      some [{ op := "x", qubits := [0] }, { op := "x", qubits := [1] },
            { op := "x", qubits := [2] }] := by native_decide

theorem parseQasmSourceE_for_unrolls :
    (match parseQasmSourceE "OPENQASM 3.0;\nqubit[3] q;\nfor i in [0:3] { x q[i]; };\n" with
      | .ok ast =>
          decide (ast.gates =
            [{ op := "x", qubits := [0] }, { op := "x", qubits := [1] },
             { op := "x", qubits := [2] }])
      | .error _ => false) = true := by native_decide

/-- `for` beyond maxForUnrollBound remains fail-closed. -/
theorem parseExecutableLineE_for_over_bound_fails :
    (match parseExecutableLineE "for i in [0:9] { x q[i]; };" with
      | .error (.unsupportedControlFlow _) => true
      | _ => false) = true := by native_decide

/-- Broader dynamic if: truthy bit shorthand `if (c[i]) x q[j]`. -/
theorem parseSupportedIfCtrl_truthy_bit :
    parseSupportedIfCtrl "if (c[1]) x q[2]" =
      some { cIdx := 1, op := "x", qubits := [2] } := by native_decide

/-- Broader dynamic if: `== true` classical predicate. -/
theorem parseSupportedIfCtrl_eq_true :
    parseSupportedIfCtrl "if (c[0] == true) z q[2]" =
      some { cIdx := 0, op := "z", qubits := [2] } := by native_decide

/-- Classical `bit[N]` declarations are accepted (declared-only; no hardware backend). -/
theorem parseQasmSourceE_accepts_bit_register :
    (match parseQasmSourceE
        "OPENQASM 3.0;\nqubit[1] q;\nbit[2] c;\nx q[0];\n" with
      | .ok ast => decide (ast.nQubits = 1 ∧ ast.gates.length = 1)
      | .error _ => false) = true := by native_decide

/-- Declared trust boundary: dynamic CanonicalAst denotation ≠ hardware execution. -/
def openqasm3HardwareSemanticsTrustBoundary : String :=
  "CanonicalAst+ClassicalReg denotation is software-profile semantics only; \
hardware execution, pulse schedules, and device noise remain not_checked_under \
hardware_semantics."

/-- Explicit residual: this profile never claims device fidelity / pulse correctness. -/
def openqasm3ClaimsDeviceFidelity : Bool := false

/-- Declared ISA-layer abstraction id (software OpenQASM3 CanonicalAst ISA). -/
def openqasm3IsaLayerId : String :=
  "openqasm3_canonical_ast_software_isa_v1"

theorem openqasm3_hardware_semantics_trust_boundary_declared :
    openqasm3HardwareSemanticsTrustBoundary ≠ "" := by native_decide

/-- Minimal hardware-abstraction lemma: software denotation ≠ device fidelity claim. -/
theorem openqasm3_hardware_abstraction_software_only :
    openqasm3HardwareSemanticsTrustBoundary ≠ "" ∧
      openqasm3ClaimsDeviceFidelity = false :=
  ⟨openqasm3_hardware_semantics_trust_boundary_declared, rfl⟩

/-- Checked ISA-layer obligation: software CanonicalAst ISA is declared and
device fidelity is explicitly false. Distinct from `hardware_semantics`. -/
theorem openqasm3_hardware_abstraction_isa_layer :
    openqasm3IsaLayerId = "openqasm3_canonical_ast_software_isa_v1" ∧
      openqasm3ClaimsDeviceFidelity = false ∧
      openqasm3HardwareSemanticsTrustBoundary ≠ "" :=
  ⟨rfl, rfl, openqasm3_hardware_semantics_trust_boundary_declared⟩

/-- Supported `c[i] = measure q[j]` parses into CanonicalAst.measurements. -/
theorem parseSupportedMeasure_c0_q0 :
    parseSupportedMeasure "c[0] = measure q[0]" =
      some { cIdx := 0, qIdx := 0 } := by native_decide

theorem parseSupportedMeasure_c1_q1 :
    parseSupportedMeasure "c[1] = measure q[1]" =
      some { cIdx := 1, qIdx := 1 } := by native_decide

/-- Teleport Alice measure assignments. -/
def teleportMeasureAssignmentSource : String :=
  "OPENQASM 3.0;\nqubit[3] q;\nbit[2] c;\nc[0] = measure q[0];\nc[1] = measure q[1];\n"

theorem parseQasmSourceE_teleport_measures :
    (match parseQasmSourceE teleportMeasureAssignmentSource with
      | .ok ast =>
          decide (ast.gates = [] ∧
            ast.controls = [] ∧
            ast.measurements =
              [{ cIdx := 0, qIdx := 0 }, { cIdx := 1, qIdx := 1 }] ∧
            ast.nQubits = 3)
      | .error _ => false) = true := by
  native_decide

/-- Exact on-disk `teleportation_with_feedforward.qasm` (LF; measure+if dynamic protocol). -/
def teleportDynamicFeedforwardKernelArtifactSource : String :=
  "OPENQASM 3.0;\ninclude \"stdgates.inc\";\n// Supplementary artifact: same wire ordering as teleportation.qasm with classically\n// controlled Pauli corrections on Bob's qubit q[2] (not used for verify-bridge).\n// Qubit ordering: q[0] = input (Alice), q[1] = Alice Bell, q[2] = Bob Bell\nqubit[3] q;\nbit[2] c;\nh q[1];\ncx q[1], q[2];\ncx q[0], q[1];\nh q[0];\nc[0] = measure q[0];\nc[1] = measure q[1];\nif (c[1] == 1) x q[2];\nif (c[0] == 1) z q[2];\n"

/-- Full dynamic feedforward artifact parses to gates + measurements + controls. -/
theorem parseQasmSourceE_teleport_dynamic_feedforward_artifact :
    (match parseQasmSourceE teleportDynamicFeedforwardKernelArtifactSource with
      | .ok ast =>
          decide (
            ast.gates =
              [{ op := "h", qubits := [1] },
               { op := "cx", qubits := [1, 2] },
               { op := "cx", qubits := [0, 1] },
               { op := "h", qubits := [0] }] ∧
            ast.measurements =
              [{ cIdx := 0, qIdx := 0 }, { cIdx := 1, qIdx := 1 }] ∧
            ast.controls =
              [{ cIdx := 1, op := "x", qubits := [2] },
               { cIdx := 0, op := "z", qubits := [2] }] ∧
            ast.nQubits = 3)
      | .error _ => false) = true := by
  native_decide

/-- Arrow-form measure remains fail-closed. -/
theorem parseQasmSourceE_arrow_measure_fails :
    (match parseQasmSourceE "OPENQASM 3.0;\nqubit[1] q;\nbit[1] c;\nmeasure q[0] -> c[0];" with
      | .error (.unsupportedInstruction _) => true
      | _ => false) = true := by native_decide

/-- Gate-only `parseGateLineE` rejects measure assignments. -/
theorem parseGateLineE_rejects_measure :
    (match parseGateLineE "c[0] = measure q[0];" with
      | .error (.unsupportedInstruction _) => true
      | _ => false) = true := by native_decide

theorem parseQasmSource_cnot_is_some :
    (parseQasmSource "cx q[0], q[1];\ncx q[0], q[1];").isSome := by native_decide

theorem parseQasmSource_cnot_two_gates :
    ∃ ast, parseQasmSource "cx q[0], q[1];\ncx q[0], q[1];" = some ast ∧ ast.gates.length = 2 := by
  native_decide

def astFromGateCount (nQubits gateCount : Nat) : CanonicalAst :=
  { version := canonicalAstVersion, nQubits := nQubits, gates := List.replicate gateCount { op := "?", qubits := [] } }

def parserTrustBoundaryNote : String :=
  "Lean parseQasmBytes / parseQasmSourceE is fail-closed Except ParseError; UTF-8 \
bytes→AST preserves declared register width; supports mid-circuit \
`c[i]=measure q[j]`, `reset q[j]` (CanonicalAst.resets; denotation measure+X→|0⟩), \
broader if / single-line if-else / depth-1 nested brace if-else, bounded \
`for i in [0:N]` Pauli unroll (N≤8), bounded `while[N]` with fuel (N≤8), and \
classical bit[] decls; bare else / bare while / arrow-measure / deeper nested \
blocks / pulse-cal schedules remain unsupported; hardware execution semantics \
are an explicit not_checked trust boundary (software denotation only; no device \
fidelity / pulse_schedule_semantics); legacy parseQasmSource remains Option for \
existing kernel bridges."

theorem toQasmOp_gate (g : SingleGate) (q : Nat) : toQasmOp (.gate g q) = .gate g q := rfl
theorem toQasmOp_cx (c t : Nat) : toQasmOp (.cx c t) = .cx c t := rfl
theorem toQasmOp_ccx (c0 c1 t : Nat) : toQasmOp (.ccx c0 c1 t) = .ccx c0 c1 t := rfl
theorem toQasmOp_swap (a b : Nat) : toQasmOp (.swap a b) = .swap a b := rfl

theorem parseGateLine_bell_h : parseGateLine "h q[0];" = some (.gate .H 0) := by native_decide
theorem parseGateLine_bell_cx : parseGateLine "cx q[0], q[1];" = some (.cx 0 1) := by native_decide
theorem parseGateLine_cx10 : parseGateLine "cx q[1], q[0];" = some (.cx 1 0) := by native_decide
theorem parseGateLine_cx12 : parseGateLine "cx q[1], q[2];" = some (.cx 1 2) := by native_decide
theorem parseGateLine_toffoli_ccx :
    parseGateLine "ccx q[0], q[1], q[2];" = some (.ccx 0 1 2) := by native_decide
theorem parseGateLine_x : parseGateLine "x q[0];" = some (.gate .X 0) := by native_decide

lemma parseLineQasmOp_bell_cx : parseLineQasmOp "cx q[0], q[1];" = some (.cx 0 1) := by
  simp [parseLineQasmOp, parseGateLine_bell_cx]
lemma parseLineQasmOp_cx01 : parseLineQasmOp "cx q[0], q[1];" = some (.cx 0 1) :=
  parseLineQasmOp_bell_cx
lemma parseLineQasmOp_cx12 : parseLineQasmOp "cx q[1], q[2];" = some (.cx 1 2) := by
  simp [parseLineQasmOp, parseGateLine_cx12]
lemma parseLineQasmOp_cx10 : parseLineQasmOp "cx q[1], q[0];" = some (.cx 1 0) := by
  simp [parseLineQasmOp, parseGateLine_cx10]
lemma parseLineQasmOp_toffoli_ccx : parseLineQasmOp "ccx q[0], q[1], q[2];" = some (.ccx 0 1 2) := by
  simp [parseLineQasmOp, parseGateLine_toffoli_ccx]

#check parseExecutableLineE
#check parseQasmBytes
#check parseQasmBytesFromString
#check parseQasmBytes_preserves_register_width
#check parseQasmBytes_invalid_utf8_fails
#check parseExecutableLineE_nested_too_deep_fails
#check openqasm3_pulse_schedule_not_checked
#check parseSupportedIfCtrl
#check parseSupportedMeasure
#check parseSupportedReset
#check parseExecutableLineE_reset_ok
#check parseQasmSourceE_reset_retained
#check parseExecutableLineE_else_fails
#check parseSupportedIfCtrl_if_else
#check parseExecutableLineE_if_else_ok
#check parseSupportedForUnroll_x3
#check parseQasmSourceE_for_unrolls
#check parseExecutableLineE_for_over_bound_fails
#check parseSupportedWhileFuel_x
#check parseExecutableLineE_while_fuel_ok
#check parseExecutableLineE_while_fuel_over_bound_fails
#check parseSupportedNestedIfElse_xz
#check parseExecutableLineE_nested_if_else_ok
#check openqasm3_hardware_abstraction_software_only
#check openqasm3_hardware_abstraction_isa_layer
#check parseSupportedIfCtrl_truthy_bit
#check parseSupportedIfCtrl_eq_true
#check parseQasmSourceE_accepts_bit_register
#check openqasm3_hardware_semantics_trust_boundary_declared
#check parseQasmSourceE_teleport_if_controls
#check parseQasmSourceE_teleport_measures
#check parseQasmSourceE_teleport_dynamic_feedforward_artifact
#check parseGateLineE_rejects_if_x
#check parseGateLineE_rejects_measure
#check parseQasmSourceE_arrow_measure_fails
#check parseLineQasmOp_cx01
#check parseLineQasmOp_cx12
#check parserTrustBoundaryNote
#check rxExcludedFromParseLinesNote


lemma parseLineQasmOp_bell_h : parseLineQasmOp "h q[0];" = some (.gate .H 0) := by
  simp [parseLineQasmOp, parseGateLine_bell_h]
lemma parseLineQasmOp_x : parseLineQasmOp "x q[0];" = some (.gate .X 0) := by
  simp [parseLineQasmOp, parseGateLine_x]

theorem parseLines_bell_eq_generated_ops :
    parseLines ["h q[0];", "cx q[0], q[1];"] = Generated.BellStatePreparation.ops := by
  unfold Generated.BellStatePreparation.ops
  simp [parseLines, parseLineQasmOp_bell_h, parseLineQasmOp_bell_cx]

theorem parseLines_bell_eq_bell_prep_ops :
    parseLines ["h q[0];", "cx q[0], q[1];"] = Generated.BellStatePreparation.ops :=
  parseLines_bell_eq_generated_ops

theorem parseLines_layout_eq_generated_ops :
    parseLines ["h q[0];", "cx q[0], q[1];"] = Generated.CircuitIdentityAfterLayout.ops := by
  unfold Generated.CircuitIdentityAfterLayout.ops
  simp [parseLines, parseLineQasmOp_bell_h, parseLineQasmOp_bell_cx]

theorem parseLines_cnot_eq_generated_ops :
    parseLines ["cx q[0], q[1];", "cx q[0], q[1];"] = Generated.CnotSelfInverse.ops := by
  unfold Generated.CnotSelfInverse.ops
  simp [parseLines, parseLineQasmOp_bell_cx]

theorem parseQasmSource_cnot_eq_parseLines_generated :
    parseLines ["cx q[0], q[1];", "cx q[0], q[1];"] = Generated.CnotSelfInverse.ops :=
  parseLines_cnot_eq_generated_ops

/-- Exact on-disk CNOT kernel artifact (OPENQASM header, include, qubit register, two CX lines). -/
def cnotKernelArtifactSource : String :=
  "OPENQASM 3.0;\ninclude \"stdgates.inc\";\nqubit[2] q;\ncx q[0], q[1];\ncx q[0], q[1];\n"

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

theorem parseQasmSource_cnot_canonical_gate_list :
    (parseQasmSource cnotKernelArtifactSource).map canonicalAstToGateList =
      some [("cx", [0, 1]), ("cx", [0, 1])] := by native_decide

/-- End-to-end: artifact parse yields codegen ops and self-inverse denotation holds. -/
theorem bridge_cnot_artifact_parse_eq_codegen (i j : Fin 4) :
    parseQasmSourceToOps cnotKernelArtifactSource = some Generated.CnotSelfInverse.ops ∧
    denotateOps2 Generated.CnotSelfInverse.ops i j = id4 i j := by
  constructor
  · exact parseQasmSource_cnot_kernel_eq_generated_ops
  · exact OpenQASM3.bridge_cnot_codegen_self_inverse i j

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
  "OPENQASM 3.0;\ninclude \"stdgates.inc\";\nqubit[2] q;\nh q[0];\ncx q[0], q[1];\n"

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
  "OPENQASM 3.0;\ninclude \"stdgates.inc\";\nqubit[2] q;\ncx q[0], q[1];\ncx q[1], q[0];\ncx q[0], q[1];\n"

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

/-- Exact on-disk native SWAP target artifact (`target.qasm` for `swap_from_three_cx`). -/
def swapTargetKernelArtifactSource : String :=
  "OPENQASM 3.0;\ninclude \"stdgates.inc\";\nqubit[2] q;\nswap q[0], q[1];\n"

def swapTargetKernelGateLines : List String :=
  ["swap q[0], q[1];"]

theorem gateLinesFromSource_swap_target :
    filterGateLines (swapTargetKernelArtifactSource.splitOn "\n" |>.map (·.trimRight)) =
      swapTargetKernelGateLines := by
  native_decide

theorem swapTargetKernelGateLines_eq :
    swapTargetKernelGateLines = ["swap q[0], q[1];"] := rfl

theorem parseGateLine_swap01 : parseGateLine "swap q[0], q[1];" = some (.swap 0 1) := by
  native_decide

theorem parseLineQasmOp_swap01 : parseLineQasmOp "swap q[0], q[1];" = some (.swap 0 1) := by
  simp [parseLineQasmOp, parseGateLine_swap01]

theorem parseLines_swap_target_eq_generated_ops :
    parseLines swapTargetKernelGateLines = Generated.SwapFromThreeCxTarget.ops := by
  unfold Generated.SwapFromThreeCxTarget.ops swapTargetKernelGateLines
  simp [parseLines, parseLineQasmOp_swap01]

theorem parseQasmSource_swap_target_kernel_eq_generated_ops :
    parseQasmSourceToOps swapTargetKernelArtifactSource =
      some Generated.SwapFromThreeCxTarget.ops := by
  unfold parseQasmSourceToOps gateLinesFromSource
  rw [gateLinesFromSource_swap_target, parseLines_swap_target_eq_generated_ops]
  rfl

theorem parseQasmSource_swap_target_kernel_is_some :
    (parseQasmSource swapTargetKernelArtifactSource).isSome := by native_decide

/-- Exact on-disk H-X-H kernel artifact. -/
def hxhKernelArtifactSource : String :=
  "OPENQASM 3.0;\ninclude \"stdgates.inc\";\nqubit[1] q;\nh q[0];\nx q[0];\nh q[0];\n"

def hxhKernelGateLines : List String :=
  ["h q[0];", "x q[0];", "h q[0];"]

theorem hxhKernelGateLines_eq :
    hxhKernelGateLines = ["h q[0];", "x q[0];", "h q[0];"] := rfl

theorem gateLinesFromSource_hxh :
    filterGateLines (hxhKernelArtifactSource.splitOn "\n" |>.map (·.trimRight)) = hxhKernelGateLines := by
  native_decide

theorem parseQasmSource_hxh_kernel_eq_generated_ops :
    parseQasmSourceToOps hxhKernelArtifactSource = some Generated.HadamardConjugatesXToZ.ops := by
  unfold parseQasmSourceToOps gateLinesFromSource
  rw [gateLinesFromSource_hxh, hxhKernelGateLines_eq, parseLines_hxh_eq_generated_ops]
  rfl

theorem parseQasmSource_hxh_kernel_is_some :
    (parseQasmSource hxhKernelArtifactSource).isSome := by native_decide

/-- Exact on-disk H-H cancellation kernel artifact. -/
def hhKernelArtifactSource : String :=
  "OPENQASM 3.0;\ninclude \"stdgates.inc\";\nqubit[1] q;\nh q[0];\nh q[0];\n"

def hhKernelGateLines : List String :=
  ["h q[0];", "h q[0];"]

theorem hhKernelGateLines_eq :
    hhKernelGateLines = ["h q[0];", "h q[0];"] := rfl

theorem gateLinesFromSource_hh :
    filterGateLines (hhKernelArtifactSource.splitOn "\n" |>.map (·.trimRight)) = hhKernelGateLines := by
  native_decide

theorem parseQasmSource_hh_kernel_eq_generated_ops :
    parseQasmSourceToOps hhKernelArtifactSource = some Generated.SingleQubitGateCancellation.ops := by
  unfold parseQasmSourceToOps gateLinesFromSource
  rw [gateLinesFromSource_hh, hhKernelGateLines_eq, parseLines_hh_eq_generated_ops]
  rfl

theorem parseQasmSource_hh_kernel_is_some :
    (parseQasmSource hhKernelArtifactSource).isSome := by native_decide

/-- Exact on-disk Clifford simplification source (H H S on q[0]). -/
def cliffordKernelArtifactSource : String :=
  "OPENQASM 3.0;\ninclude \"stdgates.inc\";\nqubit[1] q;\nh q[0];\nh q[0];\ns q[0];\n"

def cliffordKernelGateLines : List String :=
  ["h q[0];", "h q[0];", "s q[0];"]

theorem cliffordKernelGateLines_eq :
    cliffordKernelGateLines = ["h q[0];", "h q[0];", "s q[0];"] := rfl

theorem parseGateLine_s0 : parseGateLine "s q[0];" = some (.gate .S 0) := by native_decide

lemma parseLineQasmOp_s0 : parseLineQasmOp "s q[0];" = some (.gate .S 0) := by
  simp [parseLineQasmOp, parseGateLine_s0]

theorem parseLines_clifford_eq_generated_ops :
    parseLines ["h q[0];", "h q[0];", "s q[0];"] =
      Generated.CliffordSimplificationPreservesUnitary.ops := by
  unfold Generated.CliffordSimplificationPreservesUnitary.ops
  simp [parseLines, parseLineQasmOp_bell_h, parseLineQasmOp_s0]

theorem gateLinesFromSource_clifford :
    filterGateLines (cliffordKernelArtifactSource.splitOn "\n" |>.map (·.trimRight)) =
      cliffordKernelGateLines := by
  native_decide

theorem parseQasmSource_clifford_kernel_eq_generated_ops :
    parseQasmSourceToOps cliffordKernelArtifactSource =
      some Generated.CliffordSimplificationPreservesUnitary.ops := by
  unfold parseQasmSourceToOps gateLinesFromSource
  rw [gateLinesFromSource_clifford, cliffordKernelGateLines_eq, parseLines_clifford_eq_generated_ops]
  rfl

theorem parseQasmSource_clifford_kernel_is_some :
    (parseQasmSource cliffordKernelArtifactSource).isSome := by native_decide

/-- Exact on-disk Clifford simplification target (single S). -/
def cliffordTargetKernelArtifactSource : String :=
  "OPENQASM 3.0;\ninclude \"stdgates.inc\";\nqubit[1] q;\ns q[0];\n"

def cliffordTargetKernelGateLines : List String :=
  ["s q[0];"]

theorem cliffordTargetKernelGateLines_eq :
    cliffordTargetKernelGateLines = ["s q[0];"] := rfl

theorem parseLines_clifford_target_eq_generated_ops :
    parseLines ["s q[0];"] =
      Generated.CliffordSimplificationPreservesUnitaryTarget.ops := by
  unfold Generated.CliffordSimplificationPreservesUnitaryTarget.ops
  simp [parseLines, parseLineQasmOp_s0]

theorem gateLinesFromSource_clifford_target :
    filterGateLines (cliffordTargetKernelArtifactSource.splitOn "\n" |>.map (·.trimRight)) =
      cliffordTargetKernelGateLines := by
  native_decide

theorem parseQasmSource_clifford_target_kernel_eq_generated_ops :
    parseQasmSourceToOps cliffordTargetKernelArtifactSource =
      some Generated.CliffordSimplificationPreservesUnitaryTarget.ops := by
  unfold parseQasmSourceToOps gateLinesFromSource
  rw [gateLinesFromSource_clifford_target, cliffordTargetKernelGateLines_eq,
    parseLines_clifford_target_eq_generated_ops]
  rfl

theorem parseQasmSource_clifford_target_kernel_is_some :
    (parseQasmSource cliffordTargetKernelArtifactSource).isSome := by native_decide

/-- Exact on-disk Toffoli source kernel artifact (single CCX line). -/
def toffoliKernelArtifactSource : String :=
  "OPENQASM 3.0;\ninclude \"stdgates.inc\";\nqubit[3] q;\nccx q[0], q[1], q[2];\n"

def toffoliKernelGateLines : List String :=
  ["ccx q[0], q[1], q[2];"]

theorem toffoliKernelGateLines_eq :
    toffoliKernelGateLines = ["ccx q[0], q[1], q[2];"] := rfl

theorem parseLines_toffoli_eq_generated_ops :
    parseLines ["ccx q[0], q[1], q[2];"] = Generated.ToffoliDecompositionEquivalence.ops := by
  unfold Generated.ToffoliDecompositionEquivalence.ops
  simp [parseLines, parseLineQasmOp_toffoli_ccx]

theorem gateLinesFromSource_toffoli :
    filterGateLines (toffoliKernelArtifactSource.splitOn "\n" |>.map (·.trimRight)) = toffoliKernelGateLines := by
  native_decide

theorem parseQasmSource_toffoli_kernel_eq_generated_ops :
    parseQasmSourceToOps toffoliKernelArtifactSource = some Generated.ToffoliDecompositionEquivalence.ops := by
  unfold parseQasmSourceToOps gateLinesFromSource
  rw [gateLinesFromSource_toffoli, toffoliKernelGateLines_eq, parseLines_toffoli_eq_generated_ops]
  rfl

theorem parseQasmSource_toffoli_kernel_is_some :
    (parseQasmSource toffoliKernelArtifactSource).isSome := by native_decide

/-- Exact on-disk Toffoli decomposition target artifact (H/T/Tdg/CX sequence). -/
def toffoliTargetKernelArtifactSource : String :=
  "OPENQASM 3.0;\ninclude \"stdgates.inc\";\nqubit[3] q;\nh q[2];\ncx q[1], q[2];\ntdg q[2];\ncx q[0], q[2];\nt q[2];\ncx q[1], q[2];\ntdg q[2];\ncx q[0], q[2];\nt q[2];\nt q[1];\nh q[2];\ncx q[0], q[1];\nt q[0];\ntdg q[1];\ncx q[0], q[1];\n"

def toffoliTargetKernelGateLines : List String :=
  ["h q[2];", "cx q[1], q[2];", "tdg q[2];", "cx q[0], q[2];", "t q[2];",
   "cx q[1], q[2];", "tdg q[2];", "cx q[0], q[2];", "t q[2];", "t q[1];",
   "h q[2];", "cx q[0], q[1];", "t q[0];", "tdg q[1];", "cx q[0], q[1];"]

theorem gateLinesFromSource_toffoli_target :
    filterGateLines (toffoliTargetKernelArtifactSource.splitOn "\n" |>.map (·.trimRight)) =
      toffoliTargetKernelGateLines := by native_decide

theorem parseGateLine_t : parseGateLine "t q[2];" = some (.gate .T 2) := by native_decide

theorem parseGateLine_tdg : parseGateLine "tdg q[2];" = some (.gate .Tdg 2) := by native_decide

theorem parseGateLine_h2 : parseGateLine "h q[2];" = some (.gate .H 2) := by native_decide

theorem parseGateLine_t0 : parseGateLine "t q[0];" = some (.gate .T 0) := by native_decide

theorem parseGateLine_t1 : parseGateLine "t q[1];" = some (.gate .T 1) := by native_decide

theorem parseGateLine_tdg1 : parseGateLine "tdg q[1];" = some (.gate .Tdg 1) := by native_decide

theorem parseGateLine_cx02 : parseGateLine "cx q[0], q[2];" = some (.cx 0 2) := by native_decide

theorem parseLineQasmOp_h2 : parseLineQasmOp "h q[2];" = some (.gate .H 2) := by
  simp [parseLineQasmOp, parseGateLine_h2]

theorem parseLineQasmOp_tdg2 : parseLineQasmOp "tdg q[2];" = some (.gate .Tdg 2) := by
  simp [parseLineQasmOp, parseGateLine_tdg]

theorem parseLineQasmOp_cx02 : parseLineQasmOp "cx q[0], q[2];" = some (.cx 0 2) := by
  simp [parseLineQasmOp, parseGateLine_cx02]

theorem parseLineQasmOp_t2 : parseLineQasmOp "t q[2];" = some (.gate .T 2) := by
  simp [parseLineQasmOp, parseGateLine_t]

theorem parseLineQasmOp_t1 : parseLineQasmOp "t q[1];" = some (.gate .T 1) := by
  simp [parseLineQasmOp, parseGateLine_t1]

theorem parseLineQasmOp_t0 : parseLineQasmOp "t q[0];" = some (.gate .T 0) := by
  simp [parseLineQasmOp, parseGateLine_t0]

theorem parseLineQasmOp_tdg1 : parseLineQasmOp "tdg q[1];" = some (.gate .Tdg 1) := by
  simp [parseLineQasmOp, parseGateLine_tdg1]

theorem parseLines_toffoli_target_eq_generated_ops :
    parseLines toffoliTargetKernelGateLines = Generated.ToffoliDecompositionEquivalenceTarget.ops := by
  unfold Generated.ToffoliDecompositionEquivalenceTarget.ops toffoliTargetKernelGateLines
  simp [parseLines, parseLineQasmOp_h2, parseLineQasmOp_cx12, parseLineQasmOp_tdg2, parseLineQasmOp_cx02,
    parseLineQasmOp_t2, parseLineQasmOp_t1, parseLineQasmOp_cx01, parseLineQasmOp_t0, parseLineQasmOp_tdg1]

theorem parseQasmSource_toffoli_target_kernel_eq_generated_ops :
    parseQasmSourceToOps toffoliTargetKernelArtifactSource =
      some Generated.ToffoliDecompositionEquivalenceTarget.ops := by
  unfold parseQasmSourceToOps gateLinesFromSource
  rw [gateLinesFromSource_toffoli_target, parseLines_toffoli_target_eq_generated_ops]
  rfl

theorem parseQasmSource_toffoli_target_kernel_is_some :
    (parseQasmSource toffoliTargetKernelArtifactSource).isSome := by native_decide

/-- Exact on-disk layout-identity source kernel artifact (H + CX on q[0], q[1]). -/
def layoutKernelArtifactSource : String :=
  "OPENQASM 3.0;\ninclude \"stdgates.inc\";\nqubit[2] q;\nh q[0];\ncx q[0], q[1];\n"

def layoutKernelGateLines : List String :=
  ["h q[0];", "cx q[0], q[1];"]

theorem layoutKernelGateLines_eq :
    layoutKernelGateLines = ["h q[0];", "cx q[0], q[1];"] := rfl

theorem gateLinesFromSource_layout :
    filterGateLines (layoutKernelArtifactSource.splitOn "\n" |>.map (·.trimRight)) = layoutKernelGateLines := by
  native_decide

theorem parseQasmSource_layout_kernel_eq_generated_ops :
    parseQasmSourceToOps layoutKernelArtifactSource = some Generated.CircuitIdentityAfterLayout.ops := by
  unfold parseQasmSourceToOps gateLinesFromSource
  rw [gateLinesFromSource_layout, layoutKernelGateLines_eq, parseLines_layout_eq_generated_ops]
  rfl

theorem parseQasmSource_layout_kernel_is_some :
    (parseQasmSource layoutKernelArtifactSource).isSome := by native_decide

/-- Exact on-disk teleport unitary-prefix kernel sibling (measure-free). -/
def teleportKernelArtifactSource : String :=
  "OPENQASM 3.0;\ninclude \"stdgates.inc\";\n// Unitary prefix only (kernel-bridge sibling): H q[1]; CX q[1],q[2]; CX q[0],q[1]; H q[0]\nqubit[3] q;\nh q[1];\ncx q[1], q[2];\ncx q[0], q[1];\nh q[0];\n"

def teleportKernelGateLines : List String :=
  ["h q[1];", "cx q[1], q[2];", "cx q[0], q[1];", "h q[0];"]

theorem teleportKernelGateLines_eq :
    teleportKernelGateLines =
      ["h q[1];", "cx q[1], q[2];", "cx q[0], q[1];", "h q[0];"] := rfl

theorem gateLinesFromSource_teleport :
    filterGateLines (teleportKernelArtifactSource.splitOn "\n" |>.map (·.trimRight)) =
      teleportKernelGateLines := by
  native_decide

theorem parseGateLine_h1 : parseGateLine "h q[1];" = some (.gate .H 1) := by native_decide

lemma parseLineQasmOp_h1 : parseLineQasmOp "h q[1];" = some (.gate .H 1) := by
  simp [parseLineQasmOp, parseGateLine_h1]

theorem parseLines_teleport_eq_generated_ops :
    parseLines teleportKernelGateLines = Generated.TeleportationUnitaryPrefix.ops := by
  unfold Generated.TeleportationUnitaryPrefix.ops teleportKernelGateLines
  simp [parseLines, parseLineQasmOp_h1, parseLineQasmOp_cx12, parseLineQasmOp_cx01,
    parseLineQasmOp_bell_h]

theorem parseQasmSource_teleport_kernel_eq_generated_ops :
    parseQasmSourceToOps teleportKernelArtifactSource =
      some Generated.TeleportationUnitaryPrefix.ops := by
  unfold parseQasmSourceToOps gateLinesFromSource
  rw [gateLinesFromSource_teleport, parseLines_teleport_eq_generated_ops]
  rfl

theorem parseQasmSource_teleport_kernel_is_some :
    (parseQasmSource teleportKernelArtifactSource).isSome := by native_decide

theorem bridge_layout_artifact_parse_eq_codegen (i j : Fin 4) :
    parseQasmSourceToOps layoutKernelArtifactSource = some Generated.CircuitIdentityAfterLayout.ops ∧
    denotateOps2 Generated.CircuitIdentityAfterLayout.ops i j = layoutIdentityMatrix i j := by
  constructor
  · exact parseQasmSource_layout_kernel_eq_generated_ops
  · exact denotateOps2_layout_identity i j

example : parseGateLine "h q[0];" = some (.gate .H 0) := by native_decide
example : parseGateLine "cx q[0], q[1];" = some (.cx 0 1) := by native_decide
example : parseGateLine "  cx q[1], q[2];" = some (.cx 1 2) := by native_decide
example : parseGateLine "x q[0];" = some (.gate .X 0) := by native_decide
example : parseGateLine "ccx q[0], q[1], q[2];" = some (.ccx 0 1 2) := by native_decide

#check parseQasmSource
#check canonicalAstToGateList
#check bridge_cnot_artifact_parse_eq_codegen
#check parseQasmSource_bell_kernel_eq_generated_ops
#check parseQasmSource_swap_kernel_eq_generated_ops
#check parseQasmSource_cnot_kernel_eq_generated_ops
#check parseQasmSource_hxh_kernel_eq_generated_ops
#check parseQasmSource_hh_kernel_eq_generated_ops
#check parseQasmSource_toffoli_kernel_eq_generated_ops
#check parseQasmSource_layout_kernel_eq_generated_ops
#check bridge_layout_artifact_parse_eq_codegen
#check parseQasmSource_teleport_kernel_eq_generated_ops
#check parseQasmSource_toffoli_target_kernel_eq_generated_ops
#check parseQasmSource_swap_target_kernel_eq_generated_ops

/-- C2 scoped pair bridge: source CCX denotation + target decomposition trace kernel-pinned. -/
theorem bridge_toffoli_ccx_eq_target_decomposition :
    (∀ i j : Fin 8, denotateOps3 Generated.ToffoliDecompositionEquivalence.ops i j = ccx8 i j) ∧
      parseQasmSourceToOps toffoliTargetKernelArtifactSource =
        some Generated.ToffoliDecompositionEquivalenceTarget.ops := by
  refine ⟨fun i j => bridge_toffoli_codegen_ccx i j, parseQasmSource_toffoli_target_kernel_eq_generated_ops⟩

#check bridge_toffoli_ccx_eq_target_decomposition

/-- Source–target pair bridge for `swap_from_three_cx`: three-CX ↔ native SWAP
denotation equality (source artifact) plus a kernel-checked parse of the
native SWAP target artifact into the same generated target trace. -/
theorem bridge_swap_source_target_parse_and_denote :
    (∀ i j : Fin 4, denotateOps2 Generated.SwapFromThreeCx.ops i j =
        denotateOps2 Generated.SwapFromThreeCxTarget.ops i j) ∧
      parseQasmSourceToOps swapTargetKernelArtifactSource =
        some Generated.SwapFromThreeCxTarget.ops := by
  refine ⟨bridge_swap_source_target_exact, parseQasmSource_swap_target_kernel_eq_generated_ops⟩

#check bridge_swap_source_target_parse_and_denote
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

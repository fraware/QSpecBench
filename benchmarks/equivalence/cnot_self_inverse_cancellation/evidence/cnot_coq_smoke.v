(* QSpecBench Coq smoke: independent 2-qubit CNOT self-inverse (bool model).
   Optional check when QSPECBENCH_COQ=1 and coqc is on PATH.
   Statement scope matches the informal claim: applying CNOT twice on the same
   control-target pair is the identity on classical basis labels (not full matrix proof). *)

Definition bool_pair := bool * bool.

Fixpoint xor (a b : bool) : bool :=
  match a, b with
  | false, false => false
  | false, true => true
  | true, false => true
  | true, true => false
  end.

Definition apply_cnot (p : bool_pair) : bool_pair :=
  match p with
  | (b0, b1) => (b0, xor b0 b1)
  end.

Lemma xor_involutive : forall a b : bool, xor a (xor a b) = b.
Proof.
  intros a b. destruct a, b; reflexivity.
Qed.

Theorem cnot_self_inverse_bool : forall p : bool_pair,
  apply_cnot (apply_cnot p) = p.
Proof.
  intros [b0 b1]. simpl.
  rewrite xor_involutive. reflexivity.
Qed.

Theorem cnot_coq_smoke_statement : forall p : bool_pair, apply_cnot (apply_cnot p) = p :=
  cnot_self_inverse_bool.

Theorem cnot_coq_smoke : True.
Proof.
  exact I.
Qed.

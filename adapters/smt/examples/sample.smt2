; Example SMT certificate: declare a positive integer bound.
(set-logic QF_LIA)
(declare-const n Int)
(assert (>= n 1))
(check-sat)

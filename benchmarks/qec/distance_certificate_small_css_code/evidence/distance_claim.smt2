; Small CSS distance scaffold: declared minimum distance is at least 3.
(set-logic QF_LIA)
(declare-const d Int)
(assert (>= d 3))
(check-sat)

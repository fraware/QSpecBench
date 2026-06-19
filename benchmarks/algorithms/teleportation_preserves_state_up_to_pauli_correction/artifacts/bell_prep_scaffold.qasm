OPENQASM 3.0;
include "stdgates.inc";
// Two-qubit Bell-pair preparation scaffold for semantic bridge verification.
qubit[2] q;
h q[0];
cx q[0], q[1];

OPENQASM 3.0;
include "stdgates.inc";
// Unitary prefix only (kernel-bridge sibling): H q[1]; CX q[1],q[2]; CX q[0],q[1]; H q[0]
qubit[3] q;
h q[1];
cx q[1], q[2];
cx q[0], q[1];
h q[0];

OPENQASM 3.0;
include "stdgates.inc";
qubit[2] q;
h q[0];
cp(pi/2) q[0], q[1];
h q[0];

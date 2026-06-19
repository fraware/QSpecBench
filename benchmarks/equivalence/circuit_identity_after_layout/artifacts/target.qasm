OPENQASM 3.0;
include "stdgates.inc";
qubit[2] r;
h r[0];
cx r[0], r[1];

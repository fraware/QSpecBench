OPENQASM 3.0;
include "stdgates.inc";
// Deutsch-Jozsa scaffold (2 qubits)
qubit[2] q;
bit[1] c;
h q[0];
h q[1];
// oracle placeholder
h q[0];
measure q[0] -> c[0];

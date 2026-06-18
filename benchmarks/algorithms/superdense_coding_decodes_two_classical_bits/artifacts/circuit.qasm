OPENQASM 3.0;
include "stdgates.inc";
// Superdense coding scaffold (2 qubits)
qubit[2] q;
h q[0];
cx q[0], q[1];
// Alice encodes classical bits via Pauli operations (not expanded)

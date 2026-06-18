OPENQASM 3.0;
include "stdgates.inc";
// Qubit ordering: q[0] = input (Alice), q[1] = Alice Bell, q[2] = Bob Bell
qubit[3] q;
bit[2] c;
// Prepare Bell pair on q[1], q[2]
h q[1];
cx q[1], q[2];
// Bell measurement between input and Alice's Bell qubit
cx q[0], q[1];
h q[0];
c[0] = measure q[0];
c[1] = measure q[1];
// Pauli corrections on Bob's qubit q[2] are classically controlled (not expanded here)

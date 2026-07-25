OPENQASM 3.0;
include "stdgates.inc";
// Supplementary artifact: same wire ordering as teleportation.qasm with classically
// controlled Pauli corrections on Bob's qubit q[2] (not used for verify-bridge).
// Qubit ordering: q[0] = input (Alice), q[1] = Alice Bell, q[2] = Bob Bell
qubit[3] q;
bit[2] c;
h q[1];
cx q[1], q[2];
cx q[0], q[1];
h q[0];
c[0] = measure q[0];
c[1] = measure q[1];
if (c[1] == 1) x q[2];
if (c[0] == 1) z q[2];

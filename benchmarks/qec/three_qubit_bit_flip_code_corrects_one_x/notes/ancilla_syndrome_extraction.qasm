OPENQASM 3.0;
include "stdgates.inc";
qubit[3] q;
qubit[2] a;
// Ideal Z on ancillas; DeclaredBitFlipNoiseModel (single-X data, measurementIdeal).
cx q[0], a[0];
cx q[1], a[0];
cx q[1], a[1];
cx q[2], a[1];

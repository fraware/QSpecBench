OPENQASM 3.0;
include "stdgates.inc";
qubit[3] q;
// Ancilla-free sequential syndrome: S0 probe, uncompute, S1 probe.
// Ideal Z readout under DeclaredBitFlipNoiseModel; measurement flips outside model.
cx q[0], q[1];
cx q[0], q[1];
cx q[1], q[2];

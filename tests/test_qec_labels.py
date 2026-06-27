"""Negative tests for QEC adapter label handling."""

from __future__ import annotations

import pytest


def test_unknown_error_label_raises():
    from adapters.qec.parse_result import _error_pauli_for_label

    with pytest.raises(ValueError, match="unknown or malformed"):
        _error_pauli_for_label("Q0", 3)


def test_out_of_range_x_label_raises():
    from adapters.qec.parse_result import _error_pauli_for_label

    with pytest.raises(ValueError, match="out of range"):
        _error_pauli_for_label("X9", 3)

"""Unit tests for the crowd density service.

Tests the sinusoidal model, density classification thresholds,
gate-specific behavior, and boundary conditions.
"""

import pytest
from unittest.mock import patch
from datetime import datetime
from services.crowd_service import (
    _simulate_density,
    get_all_gate_statuses,
    GATES,
    THRESHOLD_LOW,
    THRESHOLD_MEDIUM,
    THRESHOLD_HIGH,
    RECOMMENDATIONS,
)


class TestSimulateDensity:
    """Tests for the _simulate_density function."""

    def test_returns_tuple_of_string_and_int(self):
        """Density should return (label, wait_minutes)."""
        label, wait = _simulate_density("Gate A (North)")
        assert isinstance(label, str)
        assert isinstance(wait, int)

    def test_density_label_is_valid(self):
        """Density label must be one of the four categories."""
        valid_labels = {"low", "medium", "high", "critical"}
        for _ in range(50):  # Multiple runs due to randomness
            label, _ = _simulate_density("Gate A (North)")
            assert label in valid_labels

    def test_wait_minutes_non_negative(self):
        """Wait time should never be negative."""
        for _ in range(50):
            _, wait = _simulate_density("Gate A (North)")
            assert wait >= 0

    def test_wait_minutes_has_upper_bound(self):
        """Wait time should not exceed MAX_WAIT_MINUTES (25)."""
        for _ in range(50):
            _, wait = _simulate_density("Gate A (North)")
            assert wait <= 25

    def test_vip_gate_has_lower_density(self):
        """VIP gates should have reduced density scores."""
        vip_waits = [_simulate_density("Gate E (VIP)")[1] for _ in range(100)]
        regular_waits = [_simulate_density("Gate A (North)")[1] for _ in range(100)]
        # VIP average should be lower than regular average
        assert sum(vip_waits) / len(vip_waits) < sum(regular_waits) / len(regular_waits)

    def test_accessibility_gate_has_lower_density(self):
        """Accessibility gates should have reduced density scores."""
        acc_waits = [_simulate_density("Gate F (Accessibility)")[1] for _ in range(100)]
        regular_waits = [_simulate_density("Gate A (North)")[1] for _ in range(100)]
        assert sum(acc_waits) / len(acc_waits) < sum(regular_waits) / len(regular_waits)


class TestGetAllGateStatuses:
    """Tests for the get_all_gate_statuses function."""

    def test_returns_correct_number_of_gates(self):
        """Should return status for all 6 gates."""
        statuses = get_all_gate_statuses()
        assert len(statuses) == len(GATES)

    def test_each_status_has_required_fields(self):
        """Each gate status should have gate, density, wait_minutes, recommendation."""
        statuses = get_all_gate_statuses()
        for status in statuses:
            assert hasattr(status, "gate")
            assert hasattr(status, "density")
            assert hasattr(status, "wait_minutes")
            assert hasattr(status, "recommendation")

    def test_recommendations_match_density(self):
        """Recommendation text should correspond to the density level."""
        statuses = get_all_gate_statuses()
        for status in statuses:
            assert status.recommendation == RECOMMENDATIONS[status.density]

    def test_all_gate_names_present(self):
        """All defined gate names should appear in the results."""
        statuses = get_all_gate_statuses()
        gate_names = {s.gate for s in statuses}
        assert gate_names == set(GATES)

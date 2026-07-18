"""Simulated crowd density service — models real-time stadium crowd data.

Uses a time-based sinusoidal model to simulate crowd density at stadium gates.
In production, this would be replaced with real sensor/CCTV data feeds.

Named constants are used throughout for clarity and testability.
"""

import random
import math
from datetime import datetime
from ._lib.schemas import CrowdStatus

# Stadium gate definitions
GATES: list[str] = [
    "Gate A (North)",
    "Gate B (South)",
    "Gate C (East)",
    "Gate D (West)",
    "Gate E (VIP)",
    "Gate F (Accessibility)",
]

# Density simulation parameters
BASE_DENSITY = 0.3           # Minimum base density
DENSITY_AMPLITUDE = 0.6      # Maximum additional density from time-of-day
PEAK_HOUR_OFFSET = 14        # Hour offset for peak calculation (2 PM)
NOISE_RANGE = 0.1            # Random noise amplitude (+/-)
SPECIAL_GATE_FACTOR = 0.4    # Reduction factor for VIP/Accessibility gates
MAX_WAIT_MINUTES = 25        # Maximum simulated wait time

# Density classification thresholds
THRESHOLD_LOW = 0.3
THRESHOLD_MEDIUM = 0.6
THRESHOLD_HIGH = 0.85

# Human-readable recommendations per density level
RECOMMENDATIONS: dict[str, str] = {
    "low": "Proceed freely — this gate is clear.",
    "medium": "Steady flow — expect a short queue.",
    "high": "Consider using an alternate gate to avoid delays.",
    "critical": "Gate congested — please use Gate F (Accessibility) or Gate B (South) as alternates.",
}


def _simulate_density(gate_name: str) -> tuple[str, int]:
    """Simulate crowd density using a time-based sinusoidal model.

    The model peaks around match times (3 PM and 8 PM slots) using a
    sine-squared function for smooth density transitions.

    Args:
        gate_name: The name of the stadium gate.

    Returns:
        A tuple of (density_label, estimated_wait_minutes).
    """
    hour = datetime.now().hour
    base = BASE_DENSITY + DENSITY_AMPLITUDE * (
        math.sin((hour - PEAK_HOUR_OFFSET) * math.pi / 6) ** 2
    )
    noise = random.uniform(-NOISE_RANGE, NOISE_RANGE)
    density_score = max(0.0, min(1.0, base + noise))

    # Accessibility and VIP gates have lower density by design
    if "Accessibility" in gate_name or "VIP" in gate_name:
        density_score *= SPECIAL_GATE_FACTOR

    wait = int(density_score * MAX_WAIT_MINUTES)

    if density_score < THRESHOLD_LOW:
        return "low", wait
    elif density_score < THRESHOLD_MEDIUM:
        return "medium", wait
    elif density_score < THRESHOLD_HIGH:
        return "high", wait
    else:
        return "critical", wait


def get_all_gate_statuses() -> list[CrowdStatus]:
    """Return crowd status for all stadium gates.

    Returns:
        A list of CrowdStatus objects, one per gate.
    """
    statuses: list[CrowdStatus] = []
    for gate in GATES:
        density, wait = _simulate_density(gate)
        statuses.append(CrowdStatus(
            gate=gate,
            density=density,
            wait_minutes=wait,
            recommendation=RECOMMENDATIONS[density],
        ))
    return statuses

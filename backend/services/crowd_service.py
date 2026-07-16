"""Simulated crowd density service — models real-time stadium crowd data."""

import random
import math
from datetime import datetime
from models.schemas import CrowdStatus

GATES = ["Gate A (North)", "Gate B (South)", "Gate C (East)", "Gate D (West)",
         "Gate E (VIP)", "Gate F (Accessibility)"]


def _simulate_density(gate_name: str) -> tuple[str, int]:
    """
    Simulate crowd density using a time-based sinusoidal model.
    In production, replace with real sensor/CCTV data feeds.
    """
    hour = datetime.now().hour
    # Peak crowds around match time (assume 3 PM and 8 PM slots)
    base = 0.3 + 0.6 * (math.sin((hour - 14) * math.pi / 6) ** 2)
    noise = random.uniform(-0.1, 0.1)
    density_score = max(0.0, min(1.0, base + noise))
    
    # Accessibility and VIP gates are always lower
    if "Accessibility" in gate_name or "VIP" in gate_name:
        density_score *= 0.4
    
    wait = int(density_score * 25)  # 0–25 minute wait
    
    if density_score < 0.3:
        return "low", wait
    elif density_score < 0.6:
        return "medium", wait
    elif density_score < 0.85:
        return "high", wait
    else:
        return "critical", wait


RECOMMENDATIONS = {
    "low": "Proceed freely — this gate is clear.",
    "medium": "Steady flow — expect a short queue.",
    "high": "Consider using an alternate gate to avoid delays.",
    "critical": "Gate congested — please use Gate F (Accessibility) or Gate B (South) as alternates.",
}


def get_all_gate_statuses() -> list[CrowdStatus]:
    """Return crowd status for all stadium gates."""
    statuses = []
    for gate in GATES:
        density, wait = _simulate_density(gate)
        statuses.append(CrowdStatus(
            gate=gate,
            density=density,
            wait_minutes=wait,
            recommendation=RECOMMENDATIONS[density],
        ))
    return statuses

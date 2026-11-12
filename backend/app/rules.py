def evaluate_temperature(temperature, occupied, warn_below, critical_below):
    """Return (severity, priority) for a cold room, or None if it's warm enough."""
    if temperature >= warn_below:
        return None
    if not occupied:
        return "yellow", "low"
    if temperature < critical_below:
        return "red", "urgent"
    return "yellow", "normal"
"""Unit conversion helpers for UI display/input."""

from __future__ import annotations

SPEED_UNIT_FACTORS_TO_MS = {
    "km/h": 1000.0 / 3600.0,
    "m/s": 1.0,
    "mph": 0.44704,
    "kn": 0.514444,
}

FORCE_UNIT_FACTORS_FROM_N = {
    "N": 1.0,
    "kg": 1.0 / 9.80665,
    "lb": 0.22480894387096,
}

UNIT_PRESETS = {
    "Metric": {"speed": "km/h", "force": "kg"},
    "Imperial": {"speed": "mph", "force": "lb"},
    "Marine/Aero": {"speed": "kn", "force": "N"},
}

SPEED_SLIDER_LIMITS = {
    "km/h": (1.0, 300.0, 1.0),
    "m/s": (0.5, 85.0, 0.1),
    "mph": (1.0, 190.0, 1.0),
    "kn": (1.0, 160.0, 1.0),
}


def speed_to_ms(speed_value: float, speed_unit: str) -> float:
    factor = SPEED_UNIT_FACTORS_TO_MS.get(speed_unit, SPEED_UNIT_FACTORS_TO_MS["km/h"])
    return float(speed_value) * factor


def ms_to_speed(speed_ms: float, speed_unit: str) -> float:
    factor = SPEED_UNIT_FACTORS_TO_MS.get(speed_unit, SPEED_UNIT_FACTORS_TO_MS["km/h"])
    if factor <= 1e-12:
        return float(speed_ms)
    return float(speed_ms) / factor


def force_from_newton(force_newton: float, force_unit: str) -> float:
    factor = FORCE_UNIT_FACTORS_FROM_N.get(force_unit, FORCE_UNIT_FACTORS_FROM_N["kg"])
    return float(force_newton) * factor


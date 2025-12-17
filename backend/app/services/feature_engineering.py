from __future__ import annotations

from dataclasses import dataclass

from app.schemas.common import TelemetryPayload


@dataclass(frozen=True)
class FeatureSet:
    version: str
    values: dict


def build_features(telemetry: TelemetryPayload) -> FeatureSet:
    # Lightweight feature engineering for a low-compute prototype
    # (You can expand with rolling stats once you have time-series)
    values = {
        "speed_kph": telemetry.speed_kph,
        "engine_temp_c": telemetry.engine_temp_c,
        "vibration_rms": telemetry.vibration_rms,
        "oil_pressure_kpa": telemetry.oil_pressure_kpa,
        "battery_v": telemetry.battery_v,
        "odometer_km": telemetry.odometer_km,
        "ambient_temp_c": telemetry.ambient_temp_c,
        "temp_delta": telemetry.engine_temp_c - telemetry.ambient_temp_c,
        "vibration_x_temp": telemetry.vibration_rms * telemetry.engine_temp_c,
        "low_oil_pressure": 1.0 if telemetry.oil_pressure_kpa < 180 else 0.0,
        "low_battery": 1.0 if telemetry.battery_v < 11.8 else 0.0,
    }
    return FeatureSet(version="v1", values=values)

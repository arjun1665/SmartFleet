from __future__ import annotations

import numpy as np


def make_synthetic_dataset(n: int = 5000, seed: int = 7):
    rng = np.random.default_rng(seed)

    speed_kph = rng.normal(60, 20, n).clip(0, 140)
    ambient_temp_c = rng.normal(25, 8, n).clip(-10, 50)
    engine_temp_c = (ambient_temp_c + rng.normal(65, 12, n)).clip(60, 130)
    vibration_rms = rng.gamma(shape=2.2, scale=0.12, size=n).clip(0, 2.5)
    oil_pressure_kpa = rng.normal(240, 45, n).clip(80, 350)
    battery_v = rng.normal(12.4, 0.5, n).clip(10.0, 14.5)
    odometer_km = rng.uniform(0, 250_000, n)

    # Failure risk: combine signals into a probability
    score = (
        0.025 * (engine_temp_c - 90)
        + 1.8 * (vibration_rms - 0.25)
        - 0.015 * (oil_pressure_kpa - 220)
        - 0.6 * (battery_v - 12.2)
        + 0.000004 * (odometer_km - 90_000)
    )

    p = 1 / (1 + np.exp(-score))
    y = rng.binomial(1, p)

    # Component label (multiclass-ish), derived from dominant factor
    comp = np.where(engine_temp_c > 105, "cooling", "")
    comp = np.where(vibration_rms > 0.7, "bearing", comp)
    comp = np.where(oil_pressure_kpa < 160, "lubrication", comp)
    comp = np.where(battery_v < 11.6, "electrical", comp)
    comp = np.where(comp == "", "general", comp)

    X = {
        "speed_kph": speed_kph,
        "engine_temp_c": engine_temp_c,
        "vibration_rms": vibration_rms,
        "oil_pressure_kpa": oil_pressure_kpa,
        "battery_v": battery_v,
        "odometer_km": odometer_km,
        "ambient_temp_c": ambient_temp_c,
        "temp_delta": engine_temp_c - ambient_temp_c,
        "vibration_x_temp": vibration_rms * engine_temp_c,
        "low_oil_pressure": (oil_pressure_kpa < 180).astype(float),
        "low_battery": (battery_v < 11.8).astype(float),
    }

    return X, y, comp

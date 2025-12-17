from __future__ import annotations

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.models import FeatureRow, TelemetryEvent
from app.ml.inference import predict_risk
from app.schemas.common import PredictionOut, TelemetryIn
from app.services.feature_engineering import build_features


def _risk_level(score: float) -> str:
    if score >= 0.8:
        return "critical"
    if score >= 0.6:
        return "high"
    if score >= 0.35:
        return "medium"
    return "low"


def _predict_component(features: dict) -> str:
    # Simple rule-based component prediction (kept cheap); can be replaced with a classifier later
    if features.get("engine_temp_c", 0) > 105:
        return "cooling"
    if features.get("vibration_rms", 0) > 0.7:
        return "bearing"
    if features.get("oil_pressure_kpa", 999) < 160:
        return "lubrication"
    if features.get("battery_v", 99) < 11.6:
        return "electrical"
    return "general"


async def predict_from_telemetry(payload: TelemetryIn, session: AsyncSession) -> PredictionOut:
    # Persist telemetry for audit/retraining
    event = TelemetryEvent(
        customer_id=payload.customer_id,
        vehicle_id=payload.telemetry.vehicle_id,
        timestamp=payload.telemetry.timestamp,
        payload=payload.telemetry.model_dump(mode="json"),
    )
    session.add(event)
    await session.flush()  # obtain event.id

    feature_set = build_features(payload.telemetry)
    session.add(
        FeatureRow(
            telemetry_event_id=event.id,
            version=feature_set.version,
            features=feature_set.values,
        )
    )

    score = predict_risk(feature_set.values, model_path=settings.model_path, encoder_path=settings.encoder_path)
    level = _risk_level(score)
    component = _predict_component(feature_set.values)

    await session.commit()

    return PredictionOut(risk_score=score, risk_level=level, predicted_component=component)

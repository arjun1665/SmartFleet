from __future__ import annotations

import datetime as dt
import uuid

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Alert, FeatureRow, TelemetryEvent
from app.schemas.common import OrchestrationOut, TelemetryIn
from app.services.booking import BookingSelectIn, select_and_reserve_slot
from app.services.feature_engineering import build_features
from app.services.prediction import _predict_component, _risk_level
from app.services.rca import RCAIn, analyze_rca
from app.services.security import SecurityResult, security_check
from app.services.voice import generate_call_script
from app.services.feedback import FeedbackIn, create_feedback


async def run_full_workflow(payload: TelemetryIn, session: AsyncSession) -> OrchestrationOut:
    # STRICT ORDER (logical):
    # /telemetry -> /predict -> /orchestrate -> /security/check -> /booking/select -> /voice/call -> /rca/analyze -> /feedback

    # 1) Persist telemetry
    event = TelemetryEvent(
        customer_id=payload.customer_id,
        vehicle_id=payload.telemetry.vehicle_id,
        timestamp=payload.telemetry.timestamp or dt.datetime.now(dt.timezone.utc),
        payload=payload.telemetry.model_dump(mode="json"),
    )
    session.add(event)
    await session.flush()

    # 2) Feature engineering + store features
    feature_set = build_features(payload.telemetry)
    session.add(FeatureRow(telemetry_event_id=event.id, version=feature_set.version, features=feature_set.values))
    await session.flush()

    # 3) Prediction (XGBoost inference)
    from app.core.config import settings
    from app.ml.inference import predict_risk

    risk_score = predict_risk(feature_set.values, model_path=settings.model_path, encoder_path=settings.encoder_path)
    risk_level = _risk_level(risk_score)
    predicted_component = _predict_component(feature_set.values)

    alert = Alert(
        telemetry_event_id=event.id,
        risk_score=risk_score,
        risk_level=risk_level,
        predicted_component=predicted_component,
    )
    session.add(alert)
    await session.flush()
    await session.commit()

    # 4) Security check
    sec = await security_check(
        payload=type(
            "SecurityPayload",
            (),
            {
                "request_id": f"req-{uuid.uuid4().hex[:12]}",
                "customer_id": str(payload.customer_id),
                "action": "orchestrate",
                "telemetry": payload.telemetry.model_dump(mode="json"),
            },
        )(),
        session=session,
    )
    if isinstance(sec, SecurityResult) and not sec.allowed:
        raise HTTPException(status_code=403, detail=f"Security blocked request: {sec.reason}")

    # 5) Booking
    booking = await select_and_reserve_slot(
        payload=BookingSelectIn(customer_id=payload.customer_id, alert_id=alert.id, preferred_center_id="CENTER-001"),
        session=session,
    )

    # 6) Customer preferences (read for personalization)
    from app.db.models import CustomerPreference

    pref_res = await session.execute(select(CustomerPreference).where(CustomerPreference.customer_id == payload.customer_id))
    prefs = pref_res.scalar_one_or_none()
    language = getattr(prefs, "language", "en") if prefs else "en"
    channel = getattr(prefs, "channel", "sms") if prefs else "sms"

    # Also load customer contact for notification stub
    from app.db.models import Customer

    cust_res = await session.execute(select(Customer).where(Customer.id == payload.customer_id))
    customer = cust_res.scalar_one_or_none()
    destination = (customer.phone or customer.email) if customer else None

    # 7) Voice script stub
    voice_payload = type(
        "VoicePayload",
        (),
        {
            "customer_id": payload.customer_id,
            "risk_level": risk_level,
            "predicted_component": predicted_component,
            "booking_center_id": booking.center_id,
            "booking_starts_at": booking.starts_at.isoformat(),
            "language": language,
            "channel": channel,
        },
    )()
    voice_script = generate_call_script(voice_payload)

    # Async notification + optional retraining
    try:
        from app.tasks.tasks import send_notification, retrain_model
        from app.core.config import settings

        if destination:
            send_notification.delay(channel=channel, destination=destination, message=voice_script)
        if risk_level in {"high", "critical"}:
            retrain_model.delay(model_path=settings.model_path, encoder_path=settings.encoder_path)
    except Exception:
        # Celery worker may be down in dev; don't fail the request
        pass

    # 8) RCA stub
    rca = await analyze_rca(
        payload=RCAIn(alert_id=alert.id, predicted_component=predicted_component, features=feature_set.values),
        session=session,
    )

    # 9) Feedback (closed loop) — create a placeholder feedback row for prototype completeness
    try:
        await create_feedback(
            payload=FeedbackIn(booking_id=booking.booking_id, csat=5, technician_notes="auto-generated placeholder"),
            session=session,
        )
    except Exception:
        pass

    return OrchestrationOut(
        telemetry_event_id=event.id,
        alert_id=alert.id,
        prediction={"risk_score": risk_score, "risk_level": risk_level, "predicted_component": predicted_component},
        booking=booking,
        rca=rca,
        voice_script=voice_script,
        security_allowed=True,
    )

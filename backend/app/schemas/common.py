import datetime as dt
import uuid

from pydantic import BaseModel, Field


class APIError(BaseModel):
    code: str
    message: str


class TelemetryPayload(BaseModel):
    vehicle_id: str = Field(min_length=1, max_length=64)
    timestamp: dt.datetime | None = None

    speed_kph: float = 0
    engine_temp_c: float = 90
    vibration_rms: float = 0.2
    oil_pressure_kpa: float = 250
    battery_v: float = 12.5

    odometer_km: float = 0
    ambient_temp_c: float = 25


class TelemetryIn(BaseModel):
    customer_id: uuid.UUID
    telemetry: TelemetryPayload


class PredictionOut(BaseModel):
    risk_score: float
    risk_level: str
    predicted_component: str


class BookingOut(BaseModel):
    booking_id: uuid.UUID
    slot_id: uuid.UUID
    center_id: str
    starts_at: dt.datetime
    ends_at: dt.datetime
    status: str


class RCAOut(BaseModel):
    rca_case_id: uuid.UUID
    summary: str
    similar_cases: dict = {}


class OrchestrationOut(BaseModel):
    telemetry_event_id: uuid.UUID
    alert_id: uuid.UUID
    prediction: PredictionOut
    booking: BookingOut
    rca: RCAOut
    voice_script: str
    security_allowed: bool

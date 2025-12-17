import uuid

from fastapi import APIRouter
from pydantic import BaseModel

from app.services.voice import generate_call_script


router = APIRouter(prefix="/voice", tags=["voice"])


class VoiceCallIn(BaseModel):
    customer_id: uuid.UUID
    risk_level: str
    predicted_component: str
    booking_center_id: str
    booking_starts_at: str
    language: str = "en"
    channel: str = "sms"


class VoiceCallOut(BaseModel):
    script: str
    tts_generated: bool = False


@router.post("/call", response_model=VoiceCallOut)
async def call(payload: VoiceCallIn):
    script = generate_call_script(payload)
    return VoiceCallOut(script=script, tts_generated=False)

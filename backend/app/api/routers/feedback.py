import uuid

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db_session
from app.services.feedback import create_feedback


router = APIRouter(prefix="", tags=["feedback"])


class FeedbackIn(BaseModel):
    booking_id: uuid.UUID
    csat: int = Field(ge=1, le=5)
    technician_notes: str | None = None


class FeedbackOut(BaseModel):
    feedback_id: uuid.UUID


@router.post("/feedback", response_model=FeedbackOut)
async def feedback(payload: FeedbackIn, session: AsyncSession = Depends(get_db_session)):
    return await create_feedback(payload=payload, session=session)

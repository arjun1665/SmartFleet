from __future__ import annotations

import uuid

from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Feedback


class FeedbackIn(BaseModel):
    booking_id: uuid.UUID
    csat: int
    technician_notes: str | None = None


class FeedbackOut(BaseModel):
    feedback_id: uuid.UUID


async def create_feedback(payload: BaseModel, session: AsyncSession) -> FeedbackOut:
    row = Feedback(
        booking_id=getattr(payload, "booking_id"),
        csat=int(getattr(payload, "csat")),
        technician_notes=getattr(payload, "technician_notes", None),
    )
    session.add(row)
    await session.commit()
    return FeedbackOut(feedback_id=row.id)

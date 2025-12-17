import uuid

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import CustomerPreference
from app.db.session import get_db_session


router = APIRouter(prefix="/customer", tags=["customer"])


class PreferencesOut(BaseModel):
    customer_id: uuid.UUID
    language: str
    channel: str
    time_window: str


@router.get("/{customer_id}/preferences", response_model=PreferencesOut)
async def get_preferences(customer_id: uuid.UUID, session: AsyncSession = Depends(get_db_session)):
    res = await session.execute(select(CustomerPreference).where(CustomerPreference.customer_id == customer_id))
    pref = res.scalar_one_or_none()
    if pref is None:
        raise HTTPException(status_code=404, detail="preferences not found")

    return PreferencesOut(
        customer_id=pref.customer_id,
        language=pref.language,
        channel=pref.channel,
        time_window=pref.time_window,
    )

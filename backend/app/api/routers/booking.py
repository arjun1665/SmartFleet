import uuid

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db_session
from app.schemas.common import BookingOut
from app.services.booking import select_and_reserve_slot


router = APIRouter(prefix="/booking", tags=["booking"])


class BookingSelectIn(BaseModel):
    customer_id: uuid.UUID
    alert_id: uuid.UUID
    preferred_center_id: str | None = None


@router.post("/select", response_model=BookingOut)
async def select(payload: BookingSelectIn, session: AsyncSession = Depends(get_db_session)):
    return await select_and_reserve_slot(payload=payload, session=session)

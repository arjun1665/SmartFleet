from __future__ import annotations

import datetime as dt
import uuid

from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Booking, ServiceSlot
from app.schemas.common import BookingOut


class BookingSelectIn(BaseModel):
    customer_id: uuid.UUID
    alert_id: uuid.UUID
    preferred_center_id: str | None = None


async def select_and_reserve_slot(payload: BookingSelectIn, session: AsyncSession) -> BookingOut:
    # Simplified ranking: earliest available slot in preferred center (or any)
    now = dt.datetime.now(dt.timezone.utc)

    q = select(ServiceSlot).where(
        ServiceSlot.is_active.is_(True),
        ServiceSlot.starts_at >= now,
        ServiceSlot.reserved < ServiceSlot.capacity,
    )
    if payload.preferred_center_id:
        q = q.where(ServiceSlot.center_id == payload.preferred_center_id)

    q = q.order_by(ServiceSlot.starts_at.asc()).limit(1)

    res = await session.execute(q)
    slot = res.scalar_one_or_none()
    if slot is None:
        # fallback: any slot
        res = await session.execute(
            select(ServiceSlot)
            .where(ServiceSlot.is_active.is_(True), ServiceSlot.starts_at >= now, ServiceSlot.reserved < ServiceSlot.capacity)
            .order_by(ServiceSlot.starts_at.asc())
            .limit(1)
        )
        slot = res.scalar_one()

    slot.reserved += 1
    booking = Booking(customer_id=payload.customer_id, alert_id=payload.alert_id, slot_id=slot.id, status="reserved")
    session.add(booking)
    await session.commit()

    return BookingOut(
        booking_id=booking.id,
        slot_id=slot.id,
        center_id=slot.center_id,
        starts_at=slot.starts_at,
        ends_at=slot.ends_at,
        status=booking.status,
    )

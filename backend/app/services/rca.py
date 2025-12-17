from __future__ import annotations

import uuid

from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import RCACase
from app.schemas.common import RCAOut


class RCAIn(BaseModel):
    alert_id: uuid.UUID
    predicted_component: str
    features: dict


async def analyze_rca(payload: BaseModel, session: AsyncSession) -> RCAOut:
    # RCA agent stub: returns a deterministic summary; optional FAISS later.
    predicted_component = getattr(payload, "predicted_component", "general")

    summary = (
        f"RCA suggests {predicted_component} degradation pattern. "
        f"Recommend inspection of related subsystem and sensor calibration."
    )

    row = RCACase(alert_id=getattr(payload, "alert_id"), summary=summary, similar_cases={"stub": True})
    session.add(row)
    await session.commit()

    return RCAOut(rca_case_id=row.id, summary=row.summary, similar_cases=row.similar_cases or {})

import uuid

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db_session
from app.schemas.common import RCAOut
from app.services.rca import analyze_rca


router = APIRouter(prefix="/rca", tags=["rca"])


class RCAIn(BaseModel):
    alert_id: uuid.UUID
    predicted_component: str
    features: dict


@router.post("/analyze", response_model=RCAOut)
async def analyze(payload: RCAIn, session: AsyncSession = Depends(get_db_session)):
    return await analyze_rca(payload=payload, session=session)

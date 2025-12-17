from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db_session
from app.services.security import security_check


router = APIRouter(prefix="/security", tags=["security"])


class SecurityCheckIn(BaseModel):
    request_id: str = Field(min_length=1, max_length=64)
    customer_id: str | None = None
    action: str = Field(default="orchestrate")
    telemetry: dict = {}


class SecurityCheckOut(BaseModel):
    allowed: bool
    reason: str | None = None


@router.post("/check", response_model=SecurityCheckOut)
async def check(payload: SecurityCheckIn, session: AsyncSession = Depends(get_db_session)):
    return await security_check(payload=payload, session=session)

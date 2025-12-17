from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db_session
from app.schemas.common import OrchestrationOut, TelemetryIn
from app.services.orchestration import run_full_workflow


router = APIRouter(prefix="", tags=["orchestrator"])


@router.post("/orchestrate", response_model=OrchestrationOut)
async def orchestrate(payload: TelemetryIn, session: AsyncSession = Depends(get_db_session)):
    return await run_full_workflow(payload=payload, session=session)

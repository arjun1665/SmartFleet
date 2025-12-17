from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.common import OrchestrationOut, TelemetryIn
from app.db.session import get_db_session
from app.services.orchestration import run_full_workflow


router = APIRouter(prefix="", tags=["telemetry"])


@router.post("/telemetry", response_model=OrchestrationOut)
async def ingest_telemetry(payload: TelemetryIn, session: AsyncSession = Depends(get_db_session)):
    # Strict workflow entrypoint
    return await run_full_workflow(payload=payload, session=session)

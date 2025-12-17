from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db_session
from app.schemas.common import PredictionOut, TelemetryIn
from app.services.prediction import predict_from_telemetry


router = APIRouter(prefix="", tags=["prediction"])


@router.post("/predict", response_model=PredictionOut)
async def predict(payload: TelemetryIn, session: AsyncSession = Depends(get_db_session)):
    return await predict_from_telemetry(payload=payload, session=session)

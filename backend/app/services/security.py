from __future__ import annotations

import re
import uuid

from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import SecurityAudit


class SecurityResult(BaseModel):
    allowed: bool
    reason: str | None = None


async def security_check(payload: BaseModel, session: AsyncSession) -> SecurityResult:
    # Stub UEBA: block obviously malformed request IDs or extreme values
    request_id = getattr(payload, "request_id", "")
    action = getattr(payload, "action", "orchestrate")
    telemetry = getattr(payload, "telemetry", {}) or {}

    allowed = True
    reason = None

    if not re.fullmatch(r"[a-zA-Z0-9\-_.]{6,64}", request_id):
        allowed = False
        reason = "invalid request_id"

    if "engine_temp_c" in telemetry and float(telemetry["engine_temp_c"]) > 200:
        allowed = False
        reason = "telemetry out of bounds"

    customer_id = None
    try:
        if getattr(payload, "customer_id", None):
            customer_id = uuid.UUID(str(getattr(payload, "customer_id")))
    except Exception:
        customer_id = None

    session.add(
        SecurityAudit(
            customer_id=customer_id,
            request_id=str(request_id),
            action=str(action),
            allowed=allowed,
            reason=reason,
            audit_metadata={"telemetry_keys": list(telemetry.keys())},
        )
    )
    await session.commit()

    return SecurityResult(allowed=allowed, reason=reason)

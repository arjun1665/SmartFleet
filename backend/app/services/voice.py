from __future__ import annotations


def generate_call_script(payload) -> str:
    # Voice agent stub: returns a call script; optional TTS can be added later.
    # The payload is a pydantic model in router.
    return (
        f"Hello! This is your service assistant. "
        f"We detected a {payload.risk_level.upper()} risk related to {payload.predicted_component}. "
        f"We reserved a service slot at {payload.booking_center_id} starting {payload.booking_starts_at}. "
        f"Reply YES to confirm or NO to reschedule."
    )

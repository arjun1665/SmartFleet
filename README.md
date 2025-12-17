# Autonomous Predictive Maintenance Platform (Prototype)

Local, open-source prototype with a multi-agent style workflow:

`/telemetry` → `/predict` → `/orchestrate` → `/security/check` → `/booking/select` → `/voice/call` → `/rca/analyze` → `/feedback`

This repo is designed to be **low-compute** and runnable locally via Docker.

## Stack

- Backend: FastAPI + Pydantic + SQLAlchemy (async) + PostgreSQL
- ML: XGBoost + scikit-learn (synthetic training data)
- Async tasks: Celery (RabbitMQ broker) + Redis result backend
- Messaging: RabbitMQ (management UI exposed)
- Frontend: React + Tailwind + Vite

## Quickstart (Docker)

From the repo root:

1. Start everything:

```bash
docker compose up --build
```

2. Open:

- API health: http://localhost:8000/health
- Swagger UI: http://localhost:8000/docs
- Frontend: http://localhost:5173
- RabbitMQ UI: http://localhost:15672 (guest/guest)

> On first startup, the backend auto-trains a small XGBoost model and stores artifacts in `backend/artifacts/`.

## Demo Request

The backend seeds a demo customer:

- `customer_id`: `11111111-1111-1111-1111-111111111111`

You can call `/orchestrate` directly:

```bash
curl -X POST http://localhost:8000/orchestrate \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": "11111111-1111-1111-1111-111111111111",
    "telemetry": {
      "vehicle_id": "VEH-001",
      "speed_kph": 62,
      "engine_temp_c": 108,
      "vibration_rms": 0.82,
      "oil_pressure_kpa": 155,
      "battery_v": 11.5,
      "odometer_km": 120000,
      "ambient_temp_c": 28
    }
  }'
```

## Backend Layout

- [backend/app/main.py](backend/app/main.py): app bootstrap + DB init + seed + model training
- [backend/app/services/orchestration.py](backend/app/services/orchestration.py): strict workflow execution
- [backend/app/db/models.py](backend/app/db/models.py): PostgreSQL schema (async SQLAlchemy)

## Notes / Stubs

- Voice: returns a generated call script (no TTS/STT runtime dependency)
- RCA: deterministic text summary (FAISS can be added later)
- Feedback: a placeholder feedback row is created during orchestration for prototype completeness

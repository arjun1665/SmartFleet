import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routers import booking, customer, feedback, orchestrate, predict, rca, security, telemetry, voice
from app.core.config import settings
from app.db.models import Base, Customer, CustomerPreference, ServiceSlot
from app.db.session import engine


def create_app() -> FastAPI:
    app = FastAPI(title=settings.app_name)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(telemetry.router)
    app.include_router(predict.router)
    app.include_router(orchestrate.router)
    app.include_router(security.router)
    app.include_router(booking.router)
    app.include_router(customer.router)
    app.include_router(voice.router)
    app.include_router(rca.router)
    app.include_router(feedback.router)

    @app.get("/health")
    async def health():
        return {"status": "ok", "env": settings.environment}

    @app.on_event("startup")
    async def on_startup():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        # Seed a sample customer + preferences + some slots for demo
        # (Idempotent-ish: best effort)
        from sqlalchemy import select
        from sqlalchemy.ext.asyncio import AsyncSession
        from app.db.session import AsyncSessionLocal
        import datetime as dt
        import uuid

        async with AsyncSessionLocal() as session:  # type: AsyncSession
            existing = await session.execute(select(Customer).limit(1))
            if existing.scalar_one_or_none() is None:
                customer = Customer(
                    id=uuid.UUID("11111111-1111-1111-1111-111111111111"),
                    name="Demo Customer",
                    email="demo@example.com",
                    phone="+10000000000",
                )
                session.add(customer)
                session.add(
                    CustomerPreference(
                        customer_id=customer.id,
                        language="en",
                        channel="sms",
                        time_window="9-18",
                    )
                )

                now = dt.datetime.now(dt.timezone.utc).replace(minute=0, second=0, microsecond=0)
                for i in range(1, 10):
                    starts = now + dt.timedelta(hours=i)
                    ends = starts + dt.timedelta(hours=1)
                    session.add(
                        ServiceSlot(
                            center_id="CENTER-001",
                            starts_at=starts,
                            ends_at=ends,
                            capacity=5,
                            reserved=0,
                            is_active=True,
                        )
                    )

                await session.commit()

        # Auto-train a tiny model if artifacts missing
        model_path = settings.model_path
        encoder_path = settings.encoder_path
        if not (os.path.exists(model_path) and os.path.exists(encoder_path)):
            os.makedirs(os.path.dirname(model_path), exist_ok=True)
            from app.ml.train import train_and_save

            await train_and_save(model_path=model_path, encoder_path=encoder_path)

    return app


app = create_app()

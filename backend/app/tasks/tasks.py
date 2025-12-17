import asyncio

from app.tasks.celery_app import celery_app


@celery_app.task(name="tasks.send_notification")
def send_notification(channel: str, destination: str, message: str) -> dict:
    # Stub: integrate SMS/email provider later
    return {"sent": True, "channel": channel, "destination": destination, "message": message}


@celery_app.task(name="tasks.retrain_model")
def retrain_model(model_path: str, encoder_path: str) -> dict:
    # Run training sync inside the worker
    from app.ml.train import _train_and_save_sync

    _train_and_save_sync(model_path=model_path, encoder_path=encoder_path)
    return {"trained": True, "model_path": model_path}

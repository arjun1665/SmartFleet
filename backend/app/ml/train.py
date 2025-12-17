from __future__ import annotations

import asyncio
import os

import joblib
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder

from app.ml.synthetic_data import make_synthetic_dataset


async def train_and_save(model_path: str, encoder_path: str) -> None:
    # Train in a thread to avoid blocking FastAPI startup too hard
    await asyncio.to_thread(_train_and_save_sync, model_path, encoder_path)


def _train_and_save_sync(model_path: str, encoder_path: str) -> None:
    from xgboost import XGBClassifier

    X_dict, y, component = make_synthetic_dataset(n=4000, seed=7)

    feature_names = list(X_dict.keys())
    X = np.column_stack([X_dict[k] for k in feature_names])

    # Encode predicted component as an auxiliary target (stubbed by heuristic at inference)
    enc = OneHotEncoder(handle_unknown="ignore", sparse_output=False)
    enc.fit(component.reshape(-1, 1))

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=7, stratify=y)

    model = XGBClassifier(
        n_estimators=80,
        max_depth=4,
        learning_rate=0.1,
        subsample=0.9,
        colsample_bytree=0.9,
        reg_lambda=1.0,
        eval_metric="logloss",
        n_jobs=1,
        random_state=7,
    )
    model.fit(X_train, y_train)

    os.makedirs(os.path.dirname(model_path), exist_ok=True)
    model.save_model(model_path)

    joblib.dump({"feature_names": feature_names, "component_encoder": enc}, encoder_path)

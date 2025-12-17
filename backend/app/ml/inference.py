from __future__ import annotations

import os
from dataclasses import dataclass

import joblib
import numpy as np


@dataclass
class ModelBundle:
    feature_names: list[str]
    model: object


_bundle: ModelBundle | None = None


def load_bundle(model_path: str, encoder_path: str) -> ModelBundle:
    global _bundle
    if _bundle is not None:
        return _bundle

    from xgboost import XGBClassifier

    meta = joblib.load(encoder_path)
    feature_names: list[str] = meta["feature_names"]

    model = XGBClassifier()
    model.load_model(model_path)

    _bundle = ModelBundle(feature_names=feature_names, model=model)
    return _bundle


def predict_risk(features: dict, model_path: str, encoder_path: str) -> float:
    if not (os.path.exists(model_path) and os.path.exists(encoder_path)):
        # Should be trained at startup, but be defensive
        return 0.5

    bundle = load_bundle(model_path=model_path, encoder_path=encoder_path)
    x = np.array([[float(features.get(name, 0.0)) for name in bundle.feature_names]])

    proba = bundle.model.predict_proba(x)[0, 1]
    return float(proba)

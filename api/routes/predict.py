# api/routes/predict.py
import json
import numpy as np
import joblib
from fastapi import APIRouter, HTTPException
from api.schemas import EnergyPredictRequest, EnergyPredictResponse

router = APIRouter()

MODEL_PATH = "ml/artifacts/energy_estimator_linear_regression.pkl"
METRICS_PATH = "ml/artifacts/energy_estimator_metrics.json"

model = joblib.load(MODEL_PATH)
with open(METRICS_PATH) as f:
    _metrics = json.load(f)
FEATURE_COLS = _metrics["_meta"]["feature_cols"]
N_ROWS = _metrics["_meta"]["n_rows"]


def build_feature_vector(req: EnergyPredictRequest) -> list[float]:
    total_tokens = req.input_tokens + req.output_tokens
    log_total_tokens = np.log1p(total_tokens)

    values = {
        "log_total_tokens": log_total_tokens,
        "is_long_prompt": int(req.is_long_prompt),
        "is_reasoning_or_heavy": int(req.is_reasoning_or_heavy),
    }
    # zero out every org dummy, then set the matching one
    for col in FEATURE_COLS:
        if col.startswith("org_"):
            values[col] = 0
    org_col = f"org_{req.organization}"
    if org_col in FEATURE_COLS:
        values[org_col] = 1
    elif any(c.startswith("org_") for c in FEATURE_COLS):
        raise HTTPException(
            status_code=400,
            detail=f"Unknown organization '{req.organization}'. "
                    f"Known: {[c.replace('org_', '') for c in FEATURE_COLS if c.startswith('org_')]}"
        )

    return [values[col] for col in FEATURE_COLS]


@router.post("/predict/energy", response_model=EnergyPredictResponse)
def predict_energy(req: EnergyPredictRequest):
    features = build_feature_vector(req)
    pred_log_wh = model.predict([features])[0]
    estimated_wh = float(np.expm1(pred_log_wh))  # inverse of log1p used in training

    return EnergyPredictResponse(
        estimated_wh=round(max(estimated_wh, 0.0), 3),
        model_version="linear_regression_v1",
        confidence_note=f"Trained on n={N_ROWS} examples across 9 models — treat as order-of-magnitude, not precise.",
    )
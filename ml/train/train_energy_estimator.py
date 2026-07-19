# ml/train/train_energy_estimator.py
import json
import joblib
import mlflow
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import LeaveOneOut, cross_val_predict
from sklearn.metrics import mean_absolute_error, r2_score
from ml.features.build_features import build_training_table
from sklearn.dummy import DummyRegressor

df, feature_cols = build_training_table()
X = df[feature_cols].astype(float).values
y = df["log_energy_wh"].values

cv = LeaveOneOut()

models = {
    "baseline_mean": DummyRegressor(strategy="mean"),
    "linear_regression": LinearRegression(),
    "random_forest": RandomForestRegressor(n_estimators=100, max_depth=3, random_state=42),
}

metrics = {}
mlflow.set_experiment("energy_estimator")

for name, model in models.items():
    with mlflow.start_run(run_name=name):
        preds = cross_val_predict(model, X, y, cv=cv)
        mae = mean_absolute_error(y, preds)
        r2 = r2_score(y, preds)
        mlflow.log_params({"model": name, "n_rows": len(y)})
        mlflow.log_metrics({"mae_log_wh": mae, "r2": r2})
        metrics[name] = {"mae_log_wh": round(float(mae), 4), "r2": round(float(r2), 4)}
        print(f"{name}: MAE(log Wh)={mae:.4f}  R2={r2:.4f}")
        print(f"  actual vs predicted (log Wh): {list(zip(y.round(2), preds.round(2)))}")

        model.fit(X, y)
        joblib.dump(model, f"ml/artifacts/energy_estimator_{name}.pkl")

metrics["_meta"] = {"n_rows": len(y), "feature_cols": feature_cols}
with open("ml/artifacts/energy_estimator_metrics.json", "w") as f:
    json.dump(metrics, f, indent=2)

best = min((k for k in metrics if k != "_meta"), key=lambda k: metrics[k]["mae_log_wh"])
print(f"\nBest by MAE: {best} — with n={len(y)}, treat as directional, not definitive.")

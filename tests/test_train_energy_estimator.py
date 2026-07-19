# tests/test_train_energy_estimator.py
import json
import os

def test_metrics_file_exists_and_sane():
    path = "ml/artifacts/energy_estimator_metrics.json"
    assert os.path.exists(path), "Run training first"
    with open(path) as f:
        metrics = json.load(f)
    for name in ["baseline_mean", "linear_regression", "random_forest"]:
        assert metrics[name]["mae_log_wh"] > 0
        assert metrics["linear_regression"]["mae_log_wh"] < metrics["baseline_mean"]["mae_log_wh"], \
            "A real model should beat the naive baseline"
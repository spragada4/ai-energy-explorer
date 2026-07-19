# tests/test_features.py
import pandas as pd
from ml.features.build_features import build_training_table

def test_build_training_table_shape():
    df, feature_cols = build_training_table()
    assert len(df) > 0
    assert set(feature_cols).issubset(df.columns)

def test_no_missing_values_in_features():
    df, feature_cols = build_training_table()
    assert df[feature_cols].isnull().sum().sum() == 0

def test_known_outliers_flagged():
    df, _ = build_training_table()
    reasoning_rows = df[df.model_name.isin(["DeepSeek-R1", "GPT-4.5"])]
    assert (reasoning_rows["is_reasoning_or_heavy"] == 1).all()
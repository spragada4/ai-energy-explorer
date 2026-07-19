# ml/features/build_features.py
import numpy as np
import pandas as pd

def build_training_table():
    specs = pd.read_csv("data/processed/model_specs.csv")
    energy = pd.read_csv("data/processed/energy_measurements.csv")

    df = energy.merge(specs, on="model_name", how="inner")

    df["log_energy_wh"] = np.log1p(df["energy_wh"])
    df["is_long_prompt"] = (df["prompt_length_bucket"] == "long").astype(int)
    df["total_tokens"] = df["input_tokens"] + df["output_tokens"]
    df["log_total_tokens"] = np.log1p(df["total_tokens"])

    # organization as a coarse proxy for "which infra stack" — real signal,
    # unlike parameter count, which is undisclosed for most proprietary models
    org_dummies = pd.get_dummies(df["organization"], prefix="org")
    df = pd.concat([df, org_dummies], axis=1)

    REASONING_MODELS = {"DeepSeek-R1", "GPT-4.5"}  # from Jegham et al.: high energy despite
                                                    # (GPT-4.5) or because of (DeepSeek-R1)
                                                    # extended/heavier inference compute
    df["is_reasoning_or_heavy"] = df["model_name"].isin(REASONING_MODELS).astype(int)

    feature_cols = ["log_total_tokens", "is_long_prompt", "is_reasoning_or_heavy"] + list(org_dummies.columns)
    return df, feature_cols

if __name__ == "__main__":
    df, cols = build_training_table()
    print(df[["model_name", "prompt_length_bucket"] + cols + ["log_energy_wh"]].to_string())
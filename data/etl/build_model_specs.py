# data/etl/build_model_specs.py
import pandas as pd

df = pd.read_csv("data/raw/notable_ai_models.csv")

# Epoch's column names shift slightly over time — inspect first:
# print(df.columns.tolist())

keep = df[[
    "Model", "Organization", "Publication date",
    "Parameters", "Training compute (FLOP)"
]].rename(columns={
    "Model": "model_name",
    "Organization": "organization",
    "Publication date": "release_date",
    "Parameters": "params",
    "Training compute (FLOP)": "training_flop",
})

# Filter to models you can actually match against energy measurements later —
# start with the well-known chat models (GPT, Claude, Gemini, LLaMA, DeepSeek
# families) since that's where energy data exists. Don't try to keep all
# thousands of rows.
keep = keep[keep["model_name"].str.contains(
    "GPT|Claude|Gemini|LLaMA|Llama|DeepSeek", case=False, na=False
)]

keep["params_billion"] = keep["params"] / 1e9
keep.to_csv("data/processed/model_specs.csv", index=False)
print(f"Wrote {len(keep)} rows")
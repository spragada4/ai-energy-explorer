# data/etl/build_demand_timeseries.py
import pandas as pd

# Source: IEA "Energy and AI" report (2025/2026 editions), Base Case and
# High Efficiency Case. Historical years are reported figures; 2030/2035 are
# IEA projections. Cite the report in your README.
rows = [
    {"year": 2022, "scenario": "historical", "twh": 460},
    {"year": 2024, "scenario": "historical", "twh": 415},
    {"year": 2025, "scenario": "historical", "twh": 475},   # midpoint of 460-490 range
    {"year": 2026, "scenario": "base",       "twh": 620},   # interpolated toward 2030
    {"year": 2028, "scenario": "base",       "twh": 780},
    {"year": 2030, "scenario": "base",       "twh": 945},
    {"year": 2035, "scenario": "base",       "twh": 1150},
    {"year": 2030, "scenario": "high_efficiency", "twh": 850},  # ~-100 TWh vs base
    {"year": 2035, "scenario": "high_efficiency", "twh": 970},
]
pd.DataFrame(rows).to_csv("data/processed/demand_timeseries.csv", index=False)
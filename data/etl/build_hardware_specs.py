# data/etl/build_hardware_specs.py
import pandas as pd

df = pd.read_csv("data/raw/ml_hardware.csv")

wanted = ["Hardware name", "Manufacturer", "Release date",
          "TDP (W)", "Energy efficiency"]
missing = [c for c in wanted if c not in df.columns]

if missing:
    print(f"Missing columns: {missing}")
    raise SystemExit(1)

keep = df[wanted].rename(columns={
    "Hardware name": "chip_name",
    "Manufacturer": "manufacturer",
    "Release date": "release_date",
    "TDP (W)": "tdp_watts",
    "Energy efficiency": "efficiency_gflop_per_joule",
})
keep["release_year"] = pd.to_datetime(keep["release_date"], errors="coerce").dt.year
keep = keep.dropna(subset=["tdp_watts"])
keep.to_csv("data/processed/hardware_specs.csv", index=False)
print(f"Wrote {len(keep)} rows")
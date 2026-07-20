# AI Energy Efficiency Explorer

**Status: Work in progress — Phase 3 in progress. API (predict/energy) built, tested, and verified end-to-end. Frontend estimator page not yet built.**

An interactive dashboard exploring AI energy consumption and efficiency — not just
displaying static projections, but predicting per-inference energy cost, ranking
models by performance-per-watt, and forecasting aggregate demand, all backed by
a few small ML models trained on public data.

Positioning note: this project doesn't try to replace measurement tools like
[CodeCarbon](https://codecarbon.io) or the [ML CO2 Impact Calculator](https://mlco2.github.io/impact/) —
those measure a single run on your own hardware. This is an *explorable, predictive*
layer on top of publicly reported AI energy data.

---

## Project structure

```
ai-energy-explorer/
├── data/
│   ├── raw/            # untouched downloads (gitignored — regenerate via etl/)
│   ├── processed/       # clean CSVs everything else reads from
│   └── etl/              # build scripts, one per table
├── ml/
│   ├── features/         # feature engineering (joins specs + energy data)
│   ├── train/             # training scripts, one per model task
│   └── artifacts/         # trained models + metrics.json (metrics.json committed, .pkl gitignored)
├── api/
│   ├── main.py            # FastAPI app
│   ├── schemas.py         # request/response models
│   └── routes/predict.py  # /predict/energy — done
├── frontend/            # Next.js dashboard — estimator page not yet built
├── tests/
└── docs/
```

---

## Current status

### Phase 1 — Data pipeline: done

Four processed tables in `data/processed/`, built from public sources.

| Table | Rows | Source |
|---|---|---|
| `model_specs.csv` | 105 | Epoch AI — Notable AI Models (CC-BY), filtered to GPT/Claude/Gemini/Llama/DeepSeek families |
| `hardware_specs.csv` | 153 | Epoch AI — Machine Learning Hardware (CC-BY) |
| `demand_timeseries.csv` | 9 | Hand-built from IEA "Energy and AI" report; 2026/2028 values are linear interpolation between IEA's published anchor points, flagged as such |
| `energy_measurements.csv` | 28 | Jegham et al., "How Hungry is AI?" Table 4 (9 matched models x 3 prompt lengths) + Google's Gemini environmental impact paper |

`data/etl/check_join.py` verifies every `energy_measurements.csv` model matches
`model_specs.csv` by exact name, with one documented exception (`LLaMA-3.2-1B`
— below Epoch's notability threshold, kept for comparison purposes, excluded
from join-dependent training).

```bash
python data/etl/run_all.py
pytest tests/test_data_pipeline.py -v
```

### Phase 2 — Model A: energy-per-inference estimator: done

**Result: linear regression, MAE (log Wh) = 0.42, R² = 0.73, n=28, Leave-One-Out CV.**

Three models compared on the same feature set (`log_total_tokens`,
`is_long_prompt`, `is_reasoning_or_heavy`, one-hot `organization`):

| Model | MAE (log Wh) | R² |
|---|---|---|
| Baseline (predict mean) | 0.98 | -0.08 |
| Linear regression | 0.42 | 0.73 |
| Random forest (max_depth=3) | 0.54 | 0.62 |

**Finding worth keeping for the model-comparison panel:** linear regression
outperformed random forest on this task. With a small, largely categorical
feature set, added model complexity didn't pay for itself — a legitimate
result, not a failed experiment.

Key modeling decisions:
- **No parameter-count feature** — most proprietary models don't disclose
  parameter counts, so `organization` is used as a coarse infrastructure proxy.
- **`is_reasoning_or_heavy` flag added by hand** for DeepSeek-R1 and GPT-4.5 —
  both are energy outliers in the source data. This single feature raised R²
  from ~0.13 to ~0.51 on an earlier, smaller version of the dataset.
- **Leave-One-Out CV**, not a train/test split — the dataset is too small for
  a single held-out split to be meaningful.
- **XGBoost swapped for a shallow, regularized Random Forest** at this dataset
  size; XGBoost's defaults would overfit n=28 across only 9 distinct models.

```bash
python -m ml.train.train_energy_estimator
pytest tests/test_features.py tests/test_train_energy_estimator.py -v
```

### Phase 3 — API: in progress (backend done, frontend next)

`POST /predict/energy` is live, tested, and verified against real training
data via manual curl checks:

| Input | Predicted | Compares to actual training value |
|---|---|---|
| OpenAI, short prompt, no reasoning flag | 0.383 Wh | ~0.42 Wh (GPT-4o / GPT-4o mini, short) |
| OpenAI, short prompt, reasoning flag | 6.709 Wh | 6.723 Wh (GPT-4.5, short — near-exact) |
| DeepSeek, long prompt, reasoning flag | 61.227 Wh | 33.634 Wh (DeepSeek-R1, long) — over-predicts ~1.8x |

The DeepSeek over-prediction isn't a bug — it's the same high-end
over-extrapolation already visible in the Phase 2 LOOCV diagnostics for
DeepSeek-R1's medium/long rows, now confirmed live through the API. Documented
as a known limitation rather than patched over.

The API builds its feature vector directly from `ml/artifacts/energy_estimator_metrics.json`'s
`_meta.feature_cols`, rather than hardcoding the one-hot column order a second
time — this avoids the feature vector silently drifting out of sync with what
the model was actually trained on.

```bash
uvicorn api.main:app --reload
pytest tests/test_api.py -v
```

**Not yet done:** Next.js estimator page (form → API → rendered result),
CORS configuration between `localhost:3000` and the API, Docker Compose for
the full stack.

### Known limitations

- n=28 rows across 9 distinct models is still small by ML standards — results
  are directional, not definitive, and are reported with that caveat in the
  API's `confidence_note` field.
- Linear regression over-extrapolates at the high end for reasoning-flagged
  models on long prompts (see DeepSeek-R1 comparison above).
- `demand_timeseries.csv` interpolates between IEA's published years; only
  2022, 2024, 2025, 2030, and 2035 are IEA's own reported/projected figures.
- Some `energy_wh` values (e.g. certain GPT-4o figures) are third-party
  estimates rather than vendor-disclosed numbers — marked via the `source`
  column rather than presented as authoritative.
- An earlier version of `energy_measurements.csv` mislabeled a data point:
  17.045 Wh was attributed to "Claude 3.7 Sonnet" but actually belongs to the
  paper's separate "Claude-3.7 Sonnet ET (Extended Thinking)" variant. Corrected
  in the current dataset (regular Claude 3.7 Sonnet's long-prompt figure is
  5.518 Wh).

---

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

cd frontend && npm install && cd ..
echo "NEXT_PUBLIC_API_URL=http://127.0.0.1:8000" > frontend/.env.local
```

## Running everything

```bash
# data + model (one-time / re-run after data changes)
curl -o data/raw/notable_ai_models.csv https://epoch.ai/data/notable_ai_models.csv
curl -o data/raw/ml_hardware.csv https://epoch.ai/data/ml_hardware.csv
python data/etl/run_all.py
python -m ml.train.train_energy_estimator

# tests
pytest tests/ -v

# API (terminal 1)
uvicorn api.main:app --reload

# frontend (terminal 2, once built)
cd frontend && npm run dev
```

---

## Roadmap

- [x] Phase 0 — repo scaffold, Python/Node environments, Docker skeleton
- [x] Phase 1 — data pipeline (4 tables, join-checked, tested)
- [x] Phase 2 — Model A: energy-per-inference estimator (linear vs RF vs baseline, LOOCV, R²=0.73)
- [ ] Phase 3 — API done, backend tested; frontend estimator page + Docker still pending
- [ ] Phase 4 — Model B: efficiency tier classifier + SHAP explainability
- [ ] Phase 5 — Model C: demand forecasting (Prophet vs gradient-boosted trees)
- [ ] Phase 6 — scenario simulator (parametrized, client-side)
- [ ] Phase 7 — model comparison panel
- [ ] Phase 8 — production hardening (CI, logging, config)
- [ ] Phase 9 — deploy (Render/Fly.io + Vercel)

---

## Data licensing / attribution

- Epoch AI datasets used under CC-BY 4.0
- IEA figures cited per their standard terms of use for report figures
- Academic paper figures (Google, Jegham et al.) cited for research/attribution
  purposes; no verbatim text reproduced, only reported numeric values
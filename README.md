# AI Energy Efficiency Explorer

**Status: 🚧 Work in progress — Phase 1 (data pipeline) complete, Phase 2 (ML models) not started.**

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
├── ml/                  # (Phase 2+) feature engineering, training, artifacts
├── api/                  # (Phase 3+) FastAPI backend
├── frontend/            # (Phase 3+) Next.js dashboard
├── tests/
└── docs/
```

---

## Current status: Phase 1 — Data pipeline ✅

Four processed tables live in `data/processed/`, built from public sources via
scripts in `data/etl/`.

### Tables

| Table | Rows | Source | Notes |
|---|---|---|---|
| `model_specs.csv` | 105 | [Epoch AI — Notable AI Models](https://epoch.ai/data/ai-models) (CC-BY) | Filtered to GPT/Claude/Gemini/Llama/DeepSeek families |
| `hardware_specs.csv` | 153 | [Epoch AI — Machine Learning Hardware](https://epoch.ai/data/machine-learning-hardware) (CC-BY) | TDP + energy efficiency (GFLOP/J) for ~150 accelerators |
| `demand_timeseries.csv` | ~9 | Hand-built from [IEA "Energy and AI" report](https://www.iea.org/reports/energy-and-ai/energy-demand-from-ai) figures | 2026/2028 values are linear interpolation between IEA's published anchor points, not primary IEA numbers — flagged in the `scenario` column |
| `energy_measurements.csv` | 6 | Google's [Gemini environmental impact paper](https://arxiv.org/abs/2508.15734) + [Jegham et al., "How Hungry is AI?"](https://arxiv.org/abs/2505.09598) | Small — see "Known limitations" below |

### Join integrity

`data/etl/check_join.py` verifies that every model in `energy_measurements.csv`
matches a row in `model_specs.csv` by exact `model_name`, with one documented
exception (`LLaMA-3.2-1B` — below Epoch's notability threshold, kept for
comparison purposes but excluded from any join-dependent training).

```bash
python data/etl/run_all.py
pytest tests/test_data_pipeline.py -v
```

### Known limitations (being addressed before Phase 2 training)

- `energy_measurements.csv` currently has only 6 rows / 4 joinable models.
  This is too thin to train a meaningful regression model. Before Phase 2,
  this table needs to be expanded — primarily by pulling more per-model,
  per-prompt-length rows from the Jegham et al. paper, which covers more
  models/sizes than are currently included.
- Some `energy_wh` values (e.g. the GPT-4o figure) are third-party estimates
  rather than vendor-disclosed numbers — marked in the `source` column
  (`*_estimate` / `*_assumed` suffixes) rather than presented as authoritative.
- `demand_timeseries.csv` interpolates between IEA's published years; only
  2022, 2024, 2025, 2030, and 2035 are IEA's own reported/projected figures.

---

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

cd frontend && npm install && cd ..
```

## Running the data pipeline

```bash
curl -o data/raw/notable_ai_models.csv https://epoch.ai/data/notable_ai_models.csv
curl -o data/raw/ml_hardware.csv https://epoch.ai/data/ml_hardware.csv

python data/etl/run_all.py
pytest tests/ -v
```

---

## Roadmap

- [x] Phase 0 — repo scaffold, Python/Node environments, Docker skeleton
- [x] Phase 1 — data pipeline (4 tables, join-checked, tested)
- [ ] Phase 2 — Model A: energy-per-inference estimator (linear / XGBoost / MLP comparison)
- [ ] Phase 3 — thin vertical slice: API + frontend estimator page, dockerized
- [ ] Phase 4 — Model B: efficiency tier classifier + SHAP explainability
- [ ] Phase 5 — Model C: demand forecasting (Prophet vs gradient-boosted trees)
- [ ] Phase 6 — scenario simulator (parametrized, client-side)
- [ ] Phase 7 — model comparison panel
- [ ] Phase 8 — production hardening (CI, logging, config)
- [ ] Phase 9 — deploy (Render/Fly.io + Vercel)

---

## Data licensing / attribution

- Epoch AI datasets used under [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/)
- IEA figures cited per their standard terms of use for report figures
- Academic paper figures (Google, Jegham et al.) cited for research/attribution
  purposes; no verbatim text reproduced, only reported numeric values
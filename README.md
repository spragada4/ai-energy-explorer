# AI Energy Efficiency Explorer

**Status: v1 complete.** A working, tested, end-to-end ML product: real public
data -> trained model -> API -> interactive frontend. Further phases (listed
below) were scoped but deliberately not built — see "Scope" for why.

An interactive tool exploring AI energy consumption and efficiency: instead of
just displaying static projections, it predicts per-inference energy cost from
a small model trained on real published measurements.

Positioning note: this project doesn't try to replace measurement tools like
[CodeCarbon](https://codecarbon.io) or the [ML CO2 Impact Calculator](https://mlco2.github.io/impact/) —
those measure a single run on your own hardware. This is an *explorable,
predictive* layer on top of publicly reported AI energy data.

See [`FINDINGS.md`](./FINDINGS.md) for a write-up of what the model actually
showed, including its honest limitations.

---

## What's built

```
ai-energy-explorer/
├── data/
│   ├── raw/            # untouched downloads (gitignored — regenerate via etl/)
│   ├── processed/       # 4 clean CSVs, join-checked and tested
│   └── etl/              # build scripts, one per table
├── ml/
│   ├── features/         # feature engineering (joins specs + energy data)
│   ├── train/             # training script: baseline vs linear vs random forest
│   └── artifacts/         # trained model + metrics.json (committed)
├── api/                  # FastAPI: POST /predict/energy
├── frontend/            # Next.js: homepage + /estimator page
├── tests/                # 9 tests: data pipeline, features, training, API
└── conftest.py           # makes `ml`/`api` importable for pytest and -m runs
```

### Data — 4 tables, real public sources, join-verified

| Table | Rows | Source |
|---|---|---|
| `model_specs.csv` | 105 | Epoch AI — Notable AI Models (CC-BY) |
| `hardware_specs.csv` | 153 | Epoch AI — Machine Learning Hardware (CC-BY) |
| `demand_timeseries.csv` | 9 | IEA "Energy and AI" report (interpolated between published anchor years, flagged) |
| `energy_measurements.csv` | 28 | Jegham et al., "How Hungry is AI?" (arXiv:2505.09598) + Google's Gemini environmental impact paper (arXiv:2508.15734) |

### Model — energy-per-inference estimator

Three models trained and compared on identical features (`log_total_tokens`,
`is_long_prompt`, `is_reasoning_or_heavy`, one-hot `organization`), evaluated
with Leave-One-Out CV (n=28):

| Model | MAE (log Wh) | R² |
|---|---|---|
| Baseline (predict mean) | 0.98 | -0.08 |
| **Linear regression (served)** | **0.42** | **0.73** |
| Random forest (max_depth=3) | 0.54 | 0.62 |

Full discussion of this result, and where it breaks down, is in `FINDINGS.md`.

### API + frontend

`POST /predict/energy` serves live predictions from the trained model. The
Next.js frontend has a homepage and an `/estimator` page — a form that calls
the API and renders the real result. Verified end-to-end in-browser, matching
manual curl tests exactly.

---

## Running it

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cd frontend && npm install && cd ..
echo "NEXT_PUBLIC_API_URL=http://127.0.0.1:8000" > frontend/.env.local

# rebuild data + model from scratch (optional — processed/ and artifacts/ are already committed)
curl -o data/raw/notable_ai_models.csv https://epoch.ai/data/notable_ai_models.csv
curl -o data/raw/ml_hardware.csv https://epoch.ai/data/ml_hardware.csv
python data/etl/run_all.py
python -m ml.train.train_energy_estimator

pytest tests/ -v

# terminal 1, from repo root
uvicorn api.main:app --reload

# terminal 2
cd frontend && npm run dev
# visit http://localhost:3000
```

---

## Scope — what's in v1, and what was deliberately left out

This project was originally scoped as a 9-phase build (classifier, forecaster,
scenario simulator, comparison panel, Docker, CI, deploy). v1 closes after
Phase 3 deliberately, not by running out of time:

- **Phase 4 (efficiency classifier) and Phase 5 (demand forecasting)** would
  have repeated the same modeling pattern already demonstrated in Phase 2
  (baseline vs simple vs complex model, honestly compared) on different
  targets. Valuable for breadth, lower marginal learning value than what's
  already built.
- **Phase 6 (scenario simulator)** is mostly frontend work, independent of
  the small dataset's limitations — a reasonable next addition if this
  project is picked back up.
- **Docker / CI / deploy** were scoped but skipped by choice for v1 — the
  project runs correctly from a fresh clone via the steps above, which covers
  the reproducibility goal without the added surface area.

---

## Known limitations

- n=28 training rows across 9 distinct models is small by ML standards —
  results are directional, not definitive, and the API says so in its
  `confidence_note` field on every response.
- The served model over-extrapolates for reasoning-flagged models at long
  prompt lengths (e.g. predicts ~61 Wh vs an actual ~34 Wh for DeepSeek-R1 at
  its longest measured prompt). Documented, not patched over.
- `demand_timeseries.csv` interpolates between IEA's published years; only
  2022, 2024, 2025, 2030, and 2035 are IEA's own figures.
- Some `energy_wh` values are third-party estimates rather than
  vendor-disclosed numbers, flagged via the `source` column.
- `conftest.py` was accidentally gitignored for part of the build — meaning
  earlier commits in this repo's history would have failed to import cleanly
  on a fresh clone. Fixed in the closing pass; flagged here rather than
  silently corrected, since it's a real detail about how the project evolved.

---

## Data licensing / attribution

- Epoch AI datasets used under [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/)
- IEA figures cited per their standard terms of use for report figures
- Academic paper figures (Google, Jegham et al.) cited for research/attribution
  purposes; no verbatim text reproduced, only reported numeric values
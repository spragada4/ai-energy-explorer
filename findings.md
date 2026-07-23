# Findings: What Predicts AI Inference Energy?

A write-up of what came out of training a small model to predict per-query
energy use (Wh) for LLM inference, using real published measurements rather
than synthetic data.

## The question

Given a model's organization, a prompt's length, and whether the model does
extended reasoning, can you predict roughly how much energy one inference
costs? And does throwing more ML at the problem actually help?

## The data

28 measurements across 9 models (GPT-4.5, GPT-4o, GPT-4o mini, Claude 3.7
Sonnet, DeepSeek-R1, DeepSeek-V3, Llama 3-70B, Llama 3.3-70B, Llama
3.1-405B), each measured at up to three prompt lengths (short/medium/long),
pulled from two sources: a peer-reviewed cross-model energy comparison paper
(Jegham et al., 2025) and Google's own disclosed per-prompt figures for
Gemini. Model specs (organization, release date) came from Epoch AI's public
dataset.

This is a small dataset by ML standards — 28 rows is not enough to train
anything sophisticated reliably. That constraint shaped every modeling
decision below, and is the most important context for reading the results.

## What I tried

Three models, same features, evaluated with Leave-One-Out cross-validation
(the right choice at this sample size — a single train/test split would be
too noisy to trust):

| Model | MAE (log Wh) | R² |
|---|---|---|
| Predict the mean every time (baseline) | 0.98 | -0.08 |
| **Linear regression** | **0.42** | **0.73** |
| Random forest (depth-limited) | 0.54 | 0.62 |

**Linear regression won.** Not narrowly — by a clear margin, and it beat a
more "sophisticated" tree-based model doing the same job. That's worth sitting
with rather than explaining away: with a small, mostly categorical feature
set, the extra flexibility of a random forest had nothing useful to fit, and
likely started modeling noise instead of signal. XGBoost was in the original
plan and was deliberately not used here for the same reason — its default
hyperparameters would have overfit a 28-row dataset almost immediately.

## The one feature that mattered most

The initial feature set (prompt length + organization) explained very little
— R² around 0.13, barely better than guessing. The real jump came from adding
a single hand-crafted binary flag: `is_reasoning_or_heavy`, set for
DeepSeek-R1 and GPT-4.5, the two models that use meaningfully more compute
per response than their peers (DeepSeek-R1 through visible chain-of-thought
reasoning, GPT-4.5 for architectural reasons discussed in the source paper).

Adding that one flag raised R² from ~0.13 to ~0.51 on an earlier, smaller
version of the dataset, and the fully expanded dataset above reached 0.73.

The takeaway: **which "class" of model you're using (reasoning vs standard)
predicts energy cost far better than prompt length or company alone.** This
matches the intuitive story in the energy-and-AI discourse — chain-of-thought
and extended-reasoning models are frequently singled out as the main driver
of rising inference costs — but it's satisfying to see it fall directly out
of a small, transparent model rather than take it on faith.

## Where the model breaks

It's not accurate everywhere, and the honest place to look is the biggest
miss: DeepSeek-R1 at long prompt length. Actual measured energy: ~34 Wh. The
model's prediction, tested live through the deployed API: ~61 Wh — nearly
double.

This is a real limitation, not a bug: with only two reasoning-flagged
examples in the training data (DeepSeek-R1 and GPT-4.5), the model has
almost nothing to learn *how* the reasoning effect should scale with prompt
length specifically — it's extrapolating past what it actually saw. More
reasoning-model examples at more prompt lengths would be the direct fix, and
is the clearest next step if this project were extended.

## What I'd do differently

- **Start the dataset bigger.** The first version had 10 rows and produced a
  much weaker, partly misleading result (including one data-entry error — a
  17 Wh figure that actually belonged to a different model variant than the
  one it was recorded against, caught and corrected before the final run).
  Investing the extra hour to pull the full comparison table up front would
  have saved a full iteration cycle.
- **A naive baseline should be step one, not an afterthought.** It was added
  after the fact here, and it's the single most useful number in the whole
  table — without it, "R²=0.73" has no anchor for whether that's actually
  good.
- **One tooling issue slipped through:** a helper file (`conftest.py`) that
  made the test suite and training scripts importable was accidentally
  gitignored for part of the build, meaning a fresh clone of the repo at that
  point in its history would have failed with a `ModuleNotFoundError`. Caught
  and fixed in a final cleanup pass — a reminder that "it works on my
  machine" and "it works from a clean clone" are different claims worth
  checking separately.

## Bottom line

A simple, interpretable model, trained on a small but real and carefully
joined dataset, explained a meaningful majority of the variance in AI
inference energy cost (R²=0.73) — and did so better than a more complex
alternative. The strongest single signal wasn't model size or company, but
whether a model does extended reasoning. That's a small, honest, defensible
result, with its limitations stated rather than hidden.
# data/etl/build_energy_measurements.py
import pandas as pd

# Sources:
#  - Google, "Measuring the environmental impact of Gemini" (arXiv:2508.15734)
#  - Jegham et al., "How Hungry is AI?" (arXiv:2505.09598)
rows = [
    {"model_name": "Gemini 2.5 Pro (May 2025)", "prompt_length_bucket": "short",
     "input_tokens": 100, "output_tokens": 300, "energy_wh": 0.24, "source": "google_2025"},

    {"model_name": "GPT-4o", "prompt_length_bucket": "short",
     "input_tokens": 100, "output_tokens": 300, "energy_wh": 0.34, "source": "nano_gpt_estimate_gpt4o_assumed"},

    {"model_name": "Claude 3.7 Sonnet", "prompt_length_bucket": "short",
     "input_tokens": 100, "output_tokens": 300, "energy_wh": 0.84, "source": "jegham_2025"},

    {"model_name": "DeepSeek-R1", "prompt_length_bucket": "short",
     "input_tokens": 100, "output_tokens": 300, "energy_wh": 23.8, "source": "jegham_2025"},

    {"model_name": "LLaMA-3.2-1B", "prompt_length_bucket": "short",
     "input_tokens": 100, "output_tokens": 300, "energy_wh": 0.07, "source": "jegham_2025"},

    {"model_name": "Gemini 2.5 Pro (May 2025)", "prompt_length_bucket": "long",
     "input_tokens": 10000, "output_tokens": 1500, "energy_wh": 1.9, "source": "google_2025_extrapolated"},
]
pd.DataFrame(rows).to_csv("data/processed/energy_measurements.csv", index=False)
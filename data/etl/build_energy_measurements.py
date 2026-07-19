# data/etl/build_energy_measurements.py
import pandas as pd

# Sources:
#  - Google, "Measuring the environmental impact of Gemini" (arXiv:2508.15734)
#  - Jegham et al., "How Hungry is AI?" Table 4 (arXiv:2505.09598) — mean values.
#    Buckets: short=100in/300out, medium=1000in/1000out, long=10000in/1500out.
#    Model names below use model_specs.csv's exact casing for a clean join.
rows = [
    # Google Gemini (Google's own paper; not covered by Jegham et al.)
    {"model_name": "Gemini 2.5 Pro (May 2025)", "prompt_length_bucket": "short",
     "input_tokens": 100, "output_tokens": 300, "energy_wh": 0.24, "source": "google_2025"},
    {"model_name": "Gemini 2.5 Pro (May 2025)", "prompt_length_bucket": "long",
     "input_tokens": 10000, "output_tokens": 1500, "energy_wh": 1.9, "source": "google_2025_extrapolated"},

    # GPT-4.5
    {"model_name": "GPT-4.5", "prompt_length_bucket": "short", "input_tokens": 100, "output_tokens": 300, "energy_wh": 6.723, "source": "jegham_2025"},
    {"model_name": "GPT-4.5", "prompt_length_bucket": "medium", "input_tokens": 1000, "output_tokens": 1000, "energy_wh": 20.500, "source": "jegham_2025"},
    {"model_name": "GPT-4.5", "prompt_length_bucket": "long", "input_tokens": 10000, "output_tokens": 1500, "energy_wh": 30.495, "source": "jegham_2025"},

    # DeepSeek-R1
    {"model_name": "DeepSeek-R1", "prompt_length_bucket": "short", "input_tokens": 100, "output_tokens": 300, "energy_wh": 23.815, "source": "jegham_2025"},
    {"model_name": "DeepSeek-R1", "prompt_length_bucket": "medium", "input_tokens": 1000, "output_tokens": 1000, "energy_wh": 29.000, "source": "jegham_2025"},
    {"model_name": "DeepSeek-R1", "prompt_length_bucket": "long", "input_tokens": 10000, "output_tokens": 1500, "energy_wh": 33.634, "source": "jegham_2025"},

    # DeepSeek-V3
    {"model_name": "DeepSeek-V3", "prompt_length_bucket": "short", "input_tokens": 100, "output_tokens": 300, "energy_wh": 3.514, "source": "jegham_2025"},
    {"model_name": "DeepSeek-V3", "prompt_length_bucket": "medium", "input_tokens": 1000, "output_tokens": 1000, "energy_wh": 9.129, "source": "jegham_2025"},
    {"model_name": "DeepSeek-V3", "prompt_length_bucket": "long", "input_tokens": 10000, "output_tokens": 1500, "energy_wh": 13.838, "source": "jegham_2025"},

    # Claude 3.7 Sonnet (regular, NOT the Extended Thinking variant)
    {"model_name": "Claude 3.7 Sonnet", "prompt_length_bucket": "short", "input_tokens": 100, "output_tokens": 300, "energy_wh": 0.836, "source": "jegham_2025"},
    {"model_name": "Claude 3.7 Sonnet", "prompt_length_bucket": "medium", "input_tokens": 1000, "output_tokens": 1000, "energy_wh": 2.781, "source": "jegham_2025"},
    {"model_name": "Claude 3.7 Sonnet", "prompt_length_bucket": "long", "input_tokens": 10000, "output_tokens": 1500, "energy_wh": 5.518, "source": "jegham_2025"},

    # GPT-4o (Mar 2025) — matches specs' dated release
    {"model_name": "GPT-4o (Mar 2025)", "prompt_length_bucket": "short", "input_tokens": 100, "output_tokens": 300, "energy_wh": 0.421, "source": "jegham_2025"},
    {"model_name": "GPT-4o (Mar 2025)", "prompt_length_bucket": "medium", "input_tokens": 1000, "output_tokens": 1000, "energy_wh": 1.214, "source": "jegham_2025"},
    {"model_name": "GPT-4o (Mar 2025)", "prompt_length_bucket": "long", "input_tokens": 10000, "output_tokens": 1500, "energy_wh": 1.788, "source": "jegham_2025"},

    # GPT-4o mini
    {"model_name": "GPT-4o mini", "prompt_length_bucket": "short", "input_tokens": 100, "output_tokens": 300, "energy_wh": 0.421, "source": "jegham_2025"},
    {"model_name": "GPT-4o mini", "prompt_length_bucket": "medium", "input_tokens": 1000, "output_tokens": 1000, "energy_wh": 1.418, "source": "jegham_2025"},
    {"model_name": "GPT-4o mini", "prompt_length_bucket": "long", "input_tokens": 10000, "output_tokens": 1500, "energy_wh": 2.106, "source": "jegham_2025"},

    # Llama 3.3 70B
    {"model_name": "Llama 3.3 70B", "prompt_length_bucket": "short", "input_tokens": 100, "output_tokens": 300, "energy_wh": 0.247, "source": "jegham_2025"},
    {"model_name": "Llama 3.3 70B", "prompt_length_bucket": "medium", "input_tokens": 1000, "output_tokens": 1000, "energy_wh": 0.857, "source": "jegham_2025"},
    {"model_name": "Llama 3.3 70B", "prompt_length_bucket": "long", "input_tokens": 10000, "output_tokens": 1500, "energy_wh": 1.646, "source": "jegham_2025"},

    # Llama 3.1-405B
    {"model_name": "Llama 3.1-405B", "prompt_length_bucket": "short", "input_tokens": 100, "output_tokens": 300, "energy_wh": 1.991, "source": "jegham_2025"},
    {"model_name": "Llama 3.1-405B", "prompt_length_bucket": "medium", "input_tokens": 1000, "output_tokens": 1000, "energy_wh": 6.911, "source": "jegham_2025"},
    {"model_name": "Llama 3.1-405B", "prompt_length_bucket": "long", "input_tokens": 10000, "output_tokens": 1500, "energy_wh": 20.757, "source": "jegham_2025"},

    # Llama 3-70B (long-prompt excluded in paper — context window limits)
    {"model_name": "Llama 3-70B", "prompt_length_bucket": "short", "input_tokens": 100, "output_tokens": 300, "energy_wh": 0.636, "source": "jegham_2025"},
    {"model_name": "Llama 3-70B", "prompt_length_bucket": "medium", "input_tokens": 1000, "output_tokens": 1000, "energy_wh": 2.105, "source": "jegham_2025"},

    # LLaMA-3.2-1B — not in Epoch's notable-models set; kept for comparison panel only
    {"model_name": "LLaMA-3.2-1B", "prompt_length_bucket": "short", "input_tokens": 100, "output_tokens": 300, "energy_wh": 0.070, "source": "jegham_2025"},
]
pd.DataFrame(rows).to_csv("data/processed/energy_measurements.csv", index=False)
print(f"Wrote {len(rows)} rows")
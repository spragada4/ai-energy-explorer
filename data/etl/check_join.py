import pandas as pd

specs = pd.read_csv("data/processed/model_specs.csv")
energy = pd.read_csv("data/processed/energy_measurements.csv")

# Models we know on purpose won't be in Epoch's notable-models file (e.g. too
# small to meet their notability bar). These stay in energy_measurements.csv
# for the cross-model comparison panel, but are excluded from Model A's
# training join since they have no params/hardware features to join against.
KNOWN_UNMATCHABLE = {"LLaMA-3.2-1B"}

specs_names = set(specs.model_name)
energy_names = set(energy.model_name)

matched = energy_names & specs_names
unmatched = energy_names - specs_names - KNOWN_UNMATCHABLE
unmatched_but_expected = energy_names & KNOWN_UNMATCHABLE

joinable_total = len(energy_names - KNOWN_UNMATCHABLE)
print(f"Matched: {len(matched)} / {joinable_total}")

if unmatched_but_expected:
    print(f"Excluded by design (not in Epoch's notable set): {unmatched_but_expected}")

if unmatched:
    print("Unmatched energy rows — fix these model_name values by hand:")
    for name in sorted(unmatched):
        print(f"  {name!r}")
else:
    print("All joinable rows matched. Phase 1 join check passed.")
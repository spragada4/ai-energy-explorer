# tests/test_data_pipeline.py
import pandas as pd

def test_energy_measurements_valid():
    df = pd.read_csv("data/processed/energy_measurements.csv")
    assert len(df) > 0
    assert df.energy_wh.min() > 0
    assert df.energy_wh.max() < 100  # sanity ceiling — catches unit errors
    assert df.model_name.notna().all()

def test_hardware_specs_valid():
    df = pd.read_csv("data/processed/hardware_specs.csv")
    assert len(df) > 20  # should have plenty from the Epoch download
    assert df.tdp_watts.min() > 0
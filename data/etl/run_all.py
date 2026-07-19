# data/etl/run_all.py
import subprocess
for script in [
    "build_model_specs.py", "build_hardware_specs.py",
    "build_demand_timeseries.py", "build_energy_measurements.py",
    "check_join.py",
]:
    print(f"--- {script} ---")
    subprocess.run(["python", f"data/etl/{script}"], check=True)
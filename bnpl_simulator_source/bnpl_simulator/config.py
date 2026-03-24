# config.py

from pathlib import Path

# This configuration file makes the application portable by defining paths
# relative to the project's root directory.

# Assumes the project structure is:
# /bnpl simulator app/
# |-- bnpl_dataset_v2.csv
# |-- /bnpl_simulator/
# |   |-- main.py
# |   |-- config.py

PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATABASE_URL = f"sqlite:///{PROJECT_ROOT / 'bnpl_simulator' / 'bnpl_simulator.db'}"
DATASET_FILEPATH = str(PROJECT_ROOT / "bnpl_dataset_v2.csv")
MODEL_FILE = str(PROJECT_ROOT / 'bnpl_simulator' / "best_risk_model.joblib")
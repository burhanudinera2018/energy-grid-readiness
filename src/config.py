# src/config.py - VERSI STABIL (Tanpa Fallback Rumit)
from pathlib import Path
import os

# Root directory
PROJECT_ROOT = Path(__file__).parent.parent

# Data directories
DATA_DIR = PROJECT_ROOT / 'data'
RAW_DATA_DIR = DATA_DIR / 'raw'
PROCESSED_DATA_DIR = PROJECT_ROOT / 'data' / 'processed'

# Output directories
OUTPUT_DIR = PROJECT_ROOT / 'output'
FIGURES_DIR = OUTPUT_DIR / 'figures'
TABLES_DIR = OUTPUT_DIR / 'tables'

# Pastikan direktori ada
for dir_path in [RAW_DATA_DIR, PROCESSED_DATA_DIR, FIGURES_DIR, TABLES_DIR]:
    try:
        dir_path.mkdir(parents=True, exist_ok=True)
    except PermissionError:
        pass

print(f"✅ PROJECT_ROOT: {PROJECT_ROOT}")

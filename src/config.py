# src/config.py
from pathlib import Path

# Root directory project-energy-2026 (gunakan absolute path)
PROJECT_ROOT = Path("/Users/macos/Study_burhanudin_2025/Data Analytics/Portfolio Project/project-energy-2026")

# Data directories
DATA_DIR = PROJECT_ROOT / 'data'
RAW_DATA_DIR = DATA_DIR / 'raw'
PROCESSED_DATA_DIR = DATA_DIR / 'processed'

# Output directories
OUTPUT_DIR = PROJECT_ROOT / 'output'
FIGURES_DIR = OUTPUT_DIR / 'figures'
TABLES_DIR = OUTPUT_DIR / 'tables'

# Pastikan semua direktori ada
for dir_path in [RAW_DATA_DIR, PROCESSED_DATA_DIR, FIGURES_DIR, TABLES_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)

print(f"✅ PROJECT_ROOT: {PROJECT_ROOT}")
print(f"✅ RAW_DATA_DIR: {RAW_DATA_DIR}")
print(f"✅ FIGURES_DIR: {FIGURES_DIR}")
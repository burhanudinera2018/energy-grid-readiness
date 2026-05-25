#!/usr/bin/env python
# scripts/01_load_filter_plants.py
"""
Tahap 1: Load dan filter Global Power Plant Database untuk Indonesia
Usage: python scripts/01_load_filter_plants.py
"""

import sys
from pathlib import Path

# Tambahkan folder scripts ke path agar bisa import utils
sys.path.append(str(Path(__file__).parent))

# Tambahkan src ke path
sys.path.append(str(Path(__file__).parent.parent / 'src'))

from config import RAW_DATA_DIR
from utils import load_indonesia_plants, plot_plant_composition, save_cleaned_data

def main():
    print("=" * 60)
    print("TAHAP 1: LOAD & FILTER POWER PLANT DATABASE")
    print("=" * 60)
    
    # Load data Indonesia
    print(f"\n📂 Membaca data dari: {RAW_DATA_DIR}")
    df = load_indonesia_plants(RAW_DATA_DIR)
    
    # Tampilkan statistik
    print(f"\n✅ Total pembangkit di Indonesia: {len(df):,}")
    print(f"⚡ Total kapasitas terinstall: {df['capacity_mw'].sum():,.0f} MW ({df['capacity_mw'].sum()/1000:.1f} GW)")
    print(f"📊 Kapasitas rata-rata: {df['capacity_mw'].mean():,.0f} MW")
    print(f"🏆 Kapasitas terbesar: {df['capacity_mw'].max():,.0f} MW")
    
    print(f"\n📊 Komposisi berdasarkan tipe:")
    for fuel, count in df['primary_fuel'].value_counts().head(10).items():
        print(f"   - {fuel}: {count} unit")
    
    # Buat visualisasi
    print(f"\n📈 Membuat visualisasi...")
    plot_plant_composition(df, save=True)
    
    # Simpan data bersih
    save_cleaned_data(df)
    
    print("\n" + "=" * 60)
    print("✅ TAHAP 1 SELESAI!")
    print("=" * 60)

if __name__ == "__main__":
    main()
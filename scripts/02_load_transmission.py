#!/usr/bin/env python
# scripts/02_load_transmission.py
"""
Tahap 2.2: Load dan filter data transmisi Indonesia dari GTD (Global Transmission Database)
Usage: python scripts/02_load_transmission.py
"""

import sys
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# Tambahkan path
sys.path.append(str(Path(__file__).parent))
sys.path.append(str(Path(__file__).parent.parent / 'src'))

from config import RAW_DATA_DIR, PROCESSED_DATA_DIR, FIGURES_DIR

def load_gtd_regional(file_name, region_filter='Indonesia'):
    """Load GTD regional file dan filter untuk Indonesia dengan encoding otomatis"""
    file_path = RAW_DATA_DIR / file_name
    
    if not file_path.exists():
        raise FileNotFoundError(f"File tidak ditemukan: {file_path}")
    
    # Coba beberapa encoding yang umum
    encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1', 'mac_roman']
    
    df = None
    used_encoding = None
    
    for encoding in encodings:
        try:
            df = pd.read_csv(file_path, encoding=encoding)
            used_encoding = encoding
            break
        except (UnicodeDecodeError, UnicodeError):
            continue
    
    if df is None:
        raise ValueError(f"Tidak dapat membaca file dengan encoding apapun: {file_path}")
    
    print(f"✅ Loaded {file_name} dengan encoding '{used_encoding}': {len(df)} records")
    print(f"   Kolom yang tersedia: {df.columns.tolist()}")
    
    # Filter untuk Indonesia (cari kolom yang berisi 'Indonesia')
    # Cari kolom yang mungkin berisi nama negara/region
    text_cols = df.select_dtypes(include=['object']).columns
    
    indo_mask = pd.Series([False] * len(df))
    for col in text_cols:
        mask = df[col].astype(str).str.contains('Indonesia|INDONESIA', case=False, na=False)
        indo_mask = indo_mask | mask
    
    df_indo = df[indo_mask].copy()
    
    if len(df_indo) == 0:
        print(f"⚠️ Tidak menemukan data 'Indonesia' dalam file {file_name}")
        print(f"   Tampilkan 5 baris pertama untuk inspeksi:")
        print(df.head())
        return df  # return semua data jika tidak ditemukan
    
    print(f"   - Data untuk Indonesia: {len(df_indo)} records")
    
    return df_indo

def analyze_transmission_capacity(df_existing, df_planned, df_mapping):
    """Analisis kapasitas transmisi untuk Indonesia"""
    
    print("\n" + "=" * 60)
    print("📡 DATA TRANSMISI INDONESIA (GTD)")
    print("=" * 60)
    
    if len(df_existing) == 0:
        print("⚠️ Tidak ada data existing untuk dianalisis")
        return {'kapasitas_ke_jawa': 0, 'total_regional': 0}
    
    # Tampilkan data existing untuk Indonesia
    print("\n📋 Data Existing untuk Indonesia:")
    print(df_existing.to_string())
    
    # Cari kolom kapasitas
    capacity_cols = [col for col in df_existing.columns if 'capacity' in col.lower() or 'mw' in col.lower()]
    print(f"\n🔍 Kolom kapasitas yang ditemukan: {capacity_cols}")
    
    # Cari kolom region/wilayah
    region_cols = [col for col in df_existing.columns if 'region' in col.lower() or 'area' in col.lower() or 'from' in col.lower() or 'to' in col.lower()]
    print(f"🔍 Kolom wilayah yang ditemukan: {region_cols}")
    
    kapasitas_ke_jawa = 0
    total_kapasitas = 0
    
    if capacity_cols:
        capacity_col = capacity_cols[0]
        total_kapasitas = df_existing[capacity_col].sum()
        print(f"\n📊 Total kapasitas transmisi (Indonesia): {total_kapasitas:,.0f} MW")
        
        # Cari data yang mengarah ke Jawa
        for col in region_cols:
            jawa_mask = df_existing[col].astype(str).str.contains('Jawa|Java', case=False, na=False)
            if jawa_mask.any():
                kapasitas_ke_jawa = df_existing[jawa_mask][capacity_col].sum()
                print(f"🎯 Kapasitas transmisi menuju Jawa (via kolom '{col}'): {kapasitas_ke_jawa:,.0f} MW")
                break
    
    return {
        'kapasitas_ke_jawa': kapasitas_ke_jawa,
        'total_regional': total_kapasitas,
        'columns': df_existing.columns.tolist(),
        'data_sample': df_existing.head()
    }

def main():
    print("=" * 60)
    print("TAHAP 2.2: LOAD DATA TRANSMISI DARI GTD")
    print("=" * 60)
    
    # Load data
    df_existing = load_gtd_regional('GTD-v1.0_regional_existing.csv')
    df_planned = load_gtd_regional('GTD-v1.0_regional_planned.csv')
    
    # Load mapping (jika ada)
    mapping_path = RAW_DATA_DIR / 'GTD_mapping.csv'
    df_mapping = pd.read_csv(mapping_path, encoding='latin-1') if mapping_path.exists() else None
    
    # Analisis
    result = analyze_transmission_capacity(df_existing, df_planned, df_mapping)
    
    # Simpan data bersih
    if len(df_existing) > 0:
        existing_save_path = PROCESSED_DATA_DIR / 'gtd_indonesia_existing.csv'
        df_existing.to_csv(existing_save_path, index=False)
        print(f"\n✅ Data existing tersimpan di: {existing_save_path}")
    
    if len(df_planned) > 0:
        planned_save_path = PROCESSED_DATA_DIR / 'gtd_indonesia_planned.csv'
        df_planned.to_csv(planned_save_path, index=False)
        print(f"✅ Data planned tersimpan di: {planned_save_path}")
    
    print("\n" + "=" * 60)
    print("✅ TAHAP 2.2 SELESAI!")
    print("=" * 60)
    
    return df_existing, df_planned, result

if __name__ == "__main__":
    df_existing, df_planned, result = main()

# Setelah result = analyze_transmission_capacity(...)
# Panggil analisis detail
from utils import analyze_transmission_capacity_detailed
detail = analyze_transmission_capacity_detailed(df_existing, df_planned)

# Simpan hasil analisis
import json
detail_path = PROCESSED_DATA_DIR / 'transmission_analysis.json'
with open(detail_path, 'w') as f:
    json.dump(detail, f, indent=2, default=str)
print(f"✅ Analisis detail tersimpan di: {detail_path}")
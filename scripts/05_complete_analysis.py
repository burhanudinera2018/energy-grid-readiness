#!/usr/bin/env python
# scripts/05_complete_analysis.py
"""
TAHAP 3 & 4: Analisis Lengkap - Pembangkit + Transmisi + Pusat Data AI
Menjawab: Apakah grid Indonesia siap untuk pusat data AI 500 MW-1 GW di Bekasi?
Usage: python scripts/05_complete_analysis.py
"""

import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import json
from pathlib import Path

sys.path.append(str(Path(__file__).parent))
sys.path.append(str(Path(__file__).parent.parent / 'src'))

from config import PROCESSED_DATA_DIR, FIGURES_DIR

# ============================================
# 1. LOAD SEMUA DATA
# ============================================

def load_all_data():
    """Load semua data yang sudah diproses"""
    
    print("=" * 60)
    print("📂 LOADING DATA...")
    print("=" * 60)
    
    # Load pembangkit
    plants_path = PROCESSED_DATA_DIR / 'indonesia_power_plants_clean.csv'
    if not plants_path.exists():
        raise FileNotFoundError(f"File tidak ditemukan: {plants_path}. Jalankan script 01 dulu.")
    
    df_plants = pd.read_csv(plants_path)
    print(f"✅ Pembangkit: {len(df_plants):,} unit, {df_plants['capacity_mw'].sum():,.0f} MW total")
    
    # Load transmisi existing
    trans_path = PROCESSED_DATA_DIR / 'gtd_indonesia_existing.csv'
    if trans_path.exists():
        df_trans = pd.read_csv(trans_path)
        print(f"✅ Transmisi: {len(df_trans)} pathway")
    else:
        print(f"⚠️ File transmisi tidak ditemukan: {trans_path}")
        df_trans = pd.DataFrame()  # empty dataframe
    
    # Load atau buat transmission_analysis.json
    detail_path = PROCESSED_DATA_DIR / 'transmission_analysis.json'
    
    if detail_path.exists():
        with open(detail_path, 'r') as f:
            trans_detail = json.load(f)
        print(f"✅ Load transmission analysis dari JSON")
    else:
        # Buat dari data yang tersedia
        print(f"⚠️ File JSON tidak ditemukan, membuat dari data CSV...")
        
        # Hitung kapasitas ke Jawa dari df_trans jika ada
        kapasitas_ke_jawa = 0
        if not df_trans.empty and 'max_flow' in df_trans.columns and 'to_region' in df_trans.columns:
            df_trans['max_flow'] = pd.to_numeric(df_trans['max_flow'], errors='coerce')
            to_java = df_trans[
                (df_trans['to_region'].astype(str).str.contains('JW', na=False)) & 
                (df_trans['max_flow'] > 0)
            ]
            kapasitas_ke_jawa = to_java['max_flow'].sum()
        
        trans_detail = {
            'kapasitas_ke_jawa': kapasitas_ke_jawa,
            'kapasitas_dari_jawa': 400,  # default
            'pathway_aktif': [],
            'pathway_rencana': []
        }
        
        # Simpan untuk下次
        with open(detail_path, 'w') as f:
            json.dump(trans_detail, f, indent=2)
        print(f"✅ File JSON dibuat: {detail_path}")
    
    # Hitung kapasitas pembangkit di Jawa (perkiraan)
    # Asumsikan 60% kapasitas nasional berada di Jawa (berdasarkan data dari berbagai sumber)
    kapasitas_jawa = df_plants['capacity_mw'].sum() * 0.6
    print(f"✅ Estimasi kapasitas pembangkit di Jawa: {kapasitas_jawa:,.0f} MW")
    
    return df_plants, df_trans, trans_detail, kapasitas_jawa

# ============================================
# 2. PROYEKSI BEBAN PUSAT DATA AI
# ============================================

def create_demand_projection():
    """Proyeksi beban pusat data AI 2025-2030"""
    
    # Data dari Research and Markets + Digital Edge
    years = [2025, 2026, 2027, 2028, 2029, 2030]
    
    # Beban data center existing (MW)
    data_center_load = [1440, 1650, 1950, 2350, 2900, 3560]
    
    # Beban tambahan dari AI (10x lipat dari search biasa, asumsikan 30% dari total data center)
    ai_share = [0.15, 0.20, 0.25, 0.30, 0.35, 0.40]  # meningkat tiap tahun
    ai_workload_factor = 10  # AI 10x lebih berat
    
    # Hitung beban AI (MW) = total data center * ai_share * factor
    ai_load = [data_center_load[i] * ai_share[i] * (ai_workload_factor - 1) / 10 
               for i in range(len(years))]
    
    # Beban non-AI (data center biasa)
    non_ai_load = [data_center_load[i] - (data_center_load[i] * ai_share[i]) for i in range(len(years))]
    
    # Total beban data center (dengan bobot AI)
    total_load = [non_ai_load[i] + ai_load[i] for i in range(len(years))]
    
    df_demand = pd.DataFrame({
        'Tahun': years,
        'Data_Center_Conventional_MW': non_ai_load,
        'Data_Center_AI_MW': ai_load,
        'Total_Demand_MW': total_load,
        'Tambahan_dari_2025_MW': [total_load[i] - total_load[0] for i in range(len(years))]
    })
    
    return df_demand

# ============================================
# 3. PROYEKSI PASOKAN (RUPTL + Existing)
# ============================================

def create_supply_projection(current_capacity, kapasitas_jawa):
    """Proyeksi kapasitas pembangkit berdasarkan RUPTL"""
    
    # Data RUPTL 2025-2034 (tambahan kapasitas per tahun)
    ruptl_addition = {
        2025: 4800, 2026: 5200, 2027: 5600, 2028: 6100,
        2029: 6700, 2030: 7400, 2031: 8200, 2032: 9100,
        2033: 10100, 2034: 11200
    }
    
    years = list(range(2025, 2031))
    supply = []
    supply_jawa = []
    
    cumulative = current_capacity
    cumulative_jawa = kapasitas_jawa
    
    for year in years:
        if year in ruptl_addition:
            cumulative += ruptl_addition[year]
            # Asumsikan 60% tambahan kapasitas di Jawa
            cumulative_jawa += ruptl_addition[year] * 0.6
        
        supply.append(cumulative)
        supply_jawa.append(cumulative_jawa)
    
    df_supply = pd.DataFrame({
        'Tahun': years,
        'Kapasitas_Nasional_MW': supply,
        'Kapasitas_Jawa_MW': supply_jawa
    })
    
    return df_supply

# ============================================
# 4. ANALISIS GAP
# ============================================

def analyze_gap(df_demand, df_supply, trans_detail):
    """Hitung gap supply-demand"""
    
    df_gap = pd.merge(df_demand, df_supply, on='Tahun', how='left')
    
    # Hitung gap (kapasitas nasional vs demand)
    df_gap['Gap_Nasional_MW'] = df_gap['Kapasitas_Nasional_MW'] - df_gap['Total_Demand_MW']
    df_gap['Rasio_Demand_Nasional'] = (df_gap['Total_Demand_MW'] / df_gap['Kapasitas_Nasional_MW']) * 100
    
    # Hitung gap Jawa saja (lebih relevan untuk pusat data di Bekasi)
    df_gap['Gap_Jawa_MW'] = df_gap['Kapasitas_Jawa_MW'] - df_gap['Total_Demand_MW']
    df_gap['Rasio_Demand_Jawa'] = (df_gap['Total_Demand_MW'] / df_gap['Kapasitas_Jawa_MW']) * 100
    
    # Tambahan beban spesifik pusat data AI 500 MW di Bekasi
    beban_bekasi = 500  # MW
    df_gap['Setelah_Bekasi_500MW_MW'] = df_gap['Gap_Jawa_MW'] - beban_bekasi
    
    return df_gap

# ============================================
# 5. VISUALISASI
# ============================================

def plot_analysis(df_gap, df_demand, trans_detail):
    """Buat visualisasi lengkap"""
    
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    
    # Grafik 1: Proyeksi Beban Data Center
    ax1 = axes[0, 0]
    ax1.stackplot(df_demand['Tahun'], 
                  df_demand['Data_Center_Conventional_MW'], 
                  df_demand['Data_Center_AI_MW'],
                  labels=['Conventional Data Center', 'AI Workload'],
                  colors=['#4ECDC4', '#FF6B6B'], alpha=0.8)
    ax1.set_xlabel('Tahun')
    ax1.set_ylabel('Beban (MW)')
    ax1.set_title('Proyeksi Beban Data Center di Indonesia (2025-2030)', fontsize=12)
    ax1.legend(loc='upper left')
    ax1.grid(True, alpha=0.3)
    
    # Grafik 2: Supply vs Demand (Nasional)
    ax2 = axes[0, 1]
    ax2.plot(df_gap['Tahun'], df_gap['Kapasitas_Nasional_MW'] / 1000, 
             'o-', linewidth=2, markersize=8, label='Kapasitas Nasional', color='#2E86AB')
    ax2.plot(df_gap['Tahun'], df_gap['Total_Demand_MW'] / 1000, 
             's-', linewidth=2, markersize=8, label='Beban Data Center', color='#A23B72')
    ax2.fill_between(df_gap['Tahun'], 
                      df_gap['Total_Demand_MW'] / 1000, 
                      df_gap['Kapasitas_Nasional_MW'] / 1000, 
                      alpha=0.3, color='#A23B72')
    ax2.set_xlabel('Tahun')
    ax2.set_ylabel('Kapasitas (GW)')
    ax2.set_title('Perbandingan Supply vs Demand (Nasional)', fontsize=12)
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    # Grafik 3: Gap Jawa (kritis untuk Bekasi)
    ax3 = axes[1, 0]
    colors_gap = ['#4ECDC4' if x > 0 else '#FF6B6B' for x in df_gap['Gap_Jawa_MW']]
    bars = ax3.bar(df_gap['Tahun'], df_gap['Gap_Jawa_MW'] / 1000, color=colors_gap)
    ax3.axhline(y=0, color='black', linestyle='-', linewidth=1)
    ax3.axhline(y=-0.5, color='red', linestyle='--', linewidth=1.5, label='Beban Bekasi 500 MW')
    ax3.set_xlabel('Tahun')
    ax3.set_ylabel('Gap (GW)')
    ax3.set_title('Gap Supply-Demand di Jawa (Positif = Aman, Negatif = Krisis)', fontsize=12)
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    
    # Grafik 4: Rasio Demand terhadap Kapasitas
    ax4 = axes[1, 1]
    ax4.plot(df_gap['Tahun'], df_gap['Rasio_Demand_Jawa'], 
             'o-', linewidth=2, markersize=8, color='#FF6B6B')
    ax4.axhline(y=10, color='orange', linestyle='--', label='Batasan 10% (Signifikan)')
    ax4.axhline(y=20, color='red', linestyle='--', label='Batasan 20% (Kritis)')
    ax4.fill_between(df_gap['Tahun'], 0, df_gap['Rasio_Demand_Jawa'], alpha=0.3, color='#FF6B6B')
    ax4.set_xlabel('Tahun')
    ax4.set_ylabel('Rasio (%)')
    ax4.set_title('Kontribusi Data Center terhadap Beban Listrik Jawa', fontsize=12)
    ax4.legend()
    ax4.grid(True, alpha=0.3)
    
    plt.tight_layout()
    save_path = FIGURES_DIR / 'complete_analysis.png'
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    print(f"\n✅ Grafik lengkap tersimpan di: {save_path}")
    plt.show()

# ============================================
# 6. KESIMPULAN & REKOMENDASI
# ============================================

def print_conclusions(df_gap, trans_detail, df_demand):
    """Cetak kesimpulan dan rekomendasi"""
    
    print("\n" + "=" * 70)
    print("🎯 KESIMPULAN ANALISIS: KESIAPAN GRID UNTUK PUSAT DATA AI")
    print("=" * 70)
    
    # Temuan 1: Kapasitas Transmisi ke Jawa
    kapasitas_ke_jawa = trans_detail.get('kapasitas_ke_jawa', 0)
    print(f"\n1️⃣ KAPASITAS TRANSMISI MENUJU JAWA:")
    print(f"   - Kapasitas existing: {kapasitas_ke_jawa:.0f} MW")
    print(f"   - Proyek Jawa-Sumatra (3.000 MW): masih dalam rencana, belum beroperasi")
    
    # Temuan 2: Kapasitas Pembangkit di Jawa
    gap_2030 = df_gap[df_gap['Tahun'] == 2030]['Gap_Jawa_MW'].values[0]
    print(f"\n2️⃣ KAPASITAS PEMBANGKIT DI JAWA:")
    print(f"   - Estimasi kapasitas Jawa 2030: {df_gap[df_gap['Tahun'] == 2030]['Kapasitas_Jawa_MW'].values[0]:.0f} MW")
    print(f"   - Beban data center 2030: {df_gap[df_gap['Tahun'] == 2030]['Total_Demand_MW'].values[0]:.0f} MW")
    print(f"   - Gap di Jawa 2030: {gap_2030/1000:.1f} GW")
    
    # Temuan 3: Dampak Pusat Data Bekasi
    after_bekasi = df_gap[df_gap['Tahun'] == 2026]['Setelah_Bekasi_500MW_MW'].values[0]
    if after_bekasi < 0:
        print(f"\n3️⃣ DAMPAK PUSAT DATA AI 500 MW DI BEKASI (2026):")
        print(f"   ⚠️ KRITIS: Setelah beban Bekasi 500 MW, gap di Jawa menjadi {after_bekasi/1000:.1f} GW")
        print(f"   → Kapasitas pembangkit & transmisi di Jawa TIDAK mencukupi")
    else:
        print(f"\n3️⃣ DAMPAK PUSAT DATA AI 500 MW DI BEKASI (2026):")
        print(f"   ✅ Masih aman. Sisa kapasitas setelah beban Bekasi: {after_bekasi/1000:.1f} GW")
    
    # Rekomendasi
    print("\n" + "=" * 70)
    print("📋 REKOMENDASI UNTUK STAKEHOLDER PLN:")
    print("=" * 70)
    print("""
    1. PERCEPAT PROYEK TRANSMISI JAWA-SUMATRA
       - Proyek 3.000 MW masih dalam rencana tanpa tahun operasi pasti
       - Dipercepat menjadi 2028 untuk mengantisipasi lonjakan beban
    
    2. DEDICATED RENEWABLE ENERGY UNTUK PUSAT DATA
       - Pusat data AI membutuhkan uptime 99.999%
       - Skema co-location solar farm + BESS di sekitar Bekasi
    
    3. AUDIT KAPASITAS PEMBANGKIT JAWA
       - Data GTD menunjukkan kapasitas transmisi ke Jawa sangat terbatas
       - Perlu verifikasi dengan data internal PLN untuk akurasi
    
    4. SKENARIO DARURAT (CONTINGENCY PLAN)
       - Jika terjadi blackout seperti Sumatra 2026, pusat data 500 MW akan loss
       - Dibutuhkan backup generator minimal 100% di lokasi
    """)
    
    # Simpan kesimpulan
    conclusions_path = PROCESSED_DATA_DIR / 'analysis_conclusions.json'
    conclusions = {
        'kapasitas_transmisi_ke_jawa_mw': kapasitas_ke_jawa,
        'gap_jawa_2030_mw': float(gap_2030),
        'dampak_bekasi_2026_mw': float(after_bekasi),
        'status_kesiapan': 'KRITIS' if after_bekasi < 0 else 'AMAN',
        'rekomendasi': [
            'Percepat proyek transmisi Jawa-Sumatra',
            'Dedicated renewable energy untuk pusat data',
            'Audit kapasitas pembangkit Jawa',
            'Skenario darurat untuk blackout'
        ]
    }
    
    with open(conclusions_path, 'w') as f:
        json.dump(conclusions, f, indent=2)
    print(f"\n✅ Kesimpulan tersimpan di: {conclusions_path}")

# ============================================
# MAIN FUNCTION
# ============================================

def main():
    print("\n" + "=" * 60)
    print("🚀 ANALISIS LENGKAP: GRID LISTRIK INDONESIA")
    print("   vs PUSAT DATA AI")
    print("=" * 60)
    
    # Load data
    df_plants, df_trans, trans_detail, kapasitas_jawa = load_all_data()
    
    # Proyeksi demand (pusat data AI)
    df_demand = create_demand_projection()
    print("\n📈 Proyeksi Beban Pusat Data AI:")
    print(df_demand.to_string())
    
    # Proyeksi supply (RUPTL)
    current_capacity = df_plants['capacity_mw'].sum()
    df_supply = create_supply_projection(current_capacity, kapasitas_jawa)
    print("\n⚡ Proyeksi Kapasitas Pembangkit:")
    print(df_supply.to_string())
    
    # Analisis gap
    df_gap = analyze_gap(df_demand, df_supply, trans_detail)
    print("\n📊 Analisis Gap Supply-Demand:")
    print(df_gap[['Tahun', 'Total_Demand_MW', 'Kapasitas_Jawa_MW', 'Gap_Jawa_MW', 'Setelah_Bekasi_500MW_MW']].to_string())
    
    # Visualisasi
    plot_analysis(df_gap, df_demand, trans_detail)
    
    # Kesimpulan
    print_conclusions(df_gap, trans_detail, df_demand)
    
    # Simpan semua data untuk referensi
    df_gap.to_csv(PROCESSED_DATA_DIR / 'final_gap_analysis.csv', index=False)
    print(f"\n✅ Data gap tersimpan di: {PROCESSED_DATA_DIR / 'final_gap_analysis.csv'}")
    
    print("\n" + "=" * 60)
    print("✅ ANALISIS LENGKAP SELESAI!")
    print("=" * 60)

if __name__ == "__main__":
    main()
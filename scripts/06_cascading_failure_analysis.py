#!/usr/bin/env python
# scripts/06_cascading_failure_analysis.py
"""
Analisis Cascading Failure: Belajar dari Blackout Sumatra 2026
Studi kasus: Dampak gangguan pada pusat data AI 500 MW di Bekasi
Usage: python scripts/06_cascading_failure_analysis.py
"""

import sys
import pandas as pd
import numpy as np
import json
import plotly.graph_objects as go
import plotly.express as px
from pathlib import Path
from datetime import datetime

sys.path.append(str(Path(__file__).parent))
sys.path.append(str(Path(__file__).parent.parent / 'src'))

from config import PROCESSED_DATA_DIR, FIGURES_DIR

# ============================================
# DATA PEMADAMAN SUMATRA 2026 (BASELINE)
# ============================================
sumatra_blackout = {
    'total_pelanggan_terdampak': 13_100_000,
    'pelanggan_pulih_24jam': 8_350_000,
    'total_pasokan_mw': 5_344,
    'pasokan_pulih_mw': 3_192,
    'gardu_induk_terdampak': 176,
    'gardu_induk_pulih': 157,
    'waktu_pemulihan_transmisi': 2,
    'waktu_pemulihan_pltu': 18,
    'penyebab_utama': 'Gangguan SUTET 275 kV akibat cuaca buruk'
}

# ============================================
# DATA TITIK KRITIS GRID JAWA
# ============================================
critical_locations = pd.DataFrame([
    {'nama': 'Gardu Induk Bekasi (Cikarang)', 'lat': -6.345, 'lon': 107.148, 
     'jenis': 'Gardu Induk', 'risiko': 'Kritis', 'beban_mw': 500,
     'keterangan': 'Titik interkoneksi pusat data 500 MW'},
    {'nama': 'Digital Edge CGK Campus (Pusat Data)', 'lat': -6.238, 'lon': 107.001, 
     'jenis': 'Pusat Data', 'risiko': 'Sangat Tinggi', 'beban_mw': 500,
     'keterangan': 'Target operasi Q4 2026, 500 MW'},
    {'nama': 'SUTET 500 kV Bekasi - Cawang', 'lat': -6.280, 'lon': 106.950, 
     'jenis': 'SUTET', 'risiko': 'Kritis', 'beban_mw': 1500,
     'keterangan': 'Backbone transmisi Jakarta Timur'},
    {'nama': 'Gardu Induk Gandul', 'lat': -6.400, 'lon': 106.800, 
     'jenis': 'Gardu Induk', 'risiko': 'Tinggi', 'beban_mw': 800,
     'keterangan': 'Sistem proteksi dan switching'},
    {'nama': 'PLTU Suralaya', 'lat': -5.880, 'lon': 106.020, 
     'jenis': 'Pembangkit', 'risiko': 'Tinggi', 'beban_mw': 3400,
     'keterangan': 'PLTU terbesar di Jawa (3.400 MW)'},
    {'nama': 'Gardu Induk Cawang', 'lat': -6.240, 'lon': 106.870, 
     'jenis': 'Gardu Induk', 'risiko': 'Sedang', 'beban_mw': 600,
     'keterangan': 'Titik koneksi Jakarta Selatan'},
    {'nama': 'PLTG Muara Tawar', 'lat': -6.120, 'lon': 107.080, 
     'jenis': 'Pembangkit', 'risiko': 'Sedang', 'beban_mw': 2200,
     'keterangan': 'PLTG gas (2.200 MW)'}
])

# ============================================
# FUNGSI SIMULASI
# ============================================

def simulate_cascading_failure(trigger_point='Gardu Induk Bekasi', data_center_load_mw=500):
    """Simulasi efek berantai dari satu titik gangguan"""
    
    total_jawa_capacity = 45000  # MW (estimasi)
    
    stages = []
    
    # Stage 0: Gangguan awal
    stages.append({
        'tahap': 0,
        'waktu_menit': 0,
        'kejadian': f'Gangguan di {trigger_point}',
        'beban_hilang_mw': data_center_load_mw,
        'status': 'Gangguan lokal'
    })
    
    # Stage 1: Proteksi bekerja
    stages.append({
        'tahap': 1,
        'waktu_menit': 0.1,
        'kejadian': 'Sistem proteksi memisahkan titik gangguan - CB trip',
        'beban_hilang_mw': data_center_load_mw,
        'status': 'Isolasi gangguan'
    })
    
    # Stage 2: Penurunan frekuensi
    frekuensi_awal = 50.0
    penurunan = (data_center_load_mw / total_jawa_capacity) * 100 * 0.05
    stages.append({
        'tahap': 2,
        'waktu_menit': 0.5,
        'kejadian': f'Penurunan frekuensi sistem ke {frekuensi_awal - penurunan:.1f} Hz',
        'beban_hilang_mw': data_center_load_mw,
        'status': 'Under-frequency'
    })
    
    # Stage 3: Pembangkit ikut trip (jika frekuensi turun drastis)
    if penurunan > 1.5:
        extra_loss = 2000
        stages.append({
            'tahap': 3,
            'waktu_menit': 1.0,
            'kejadian': f'Under-frequency relay aktif - {extra_loss} MW pembangkit trip',
            'beban_hilang_mw': data_center_load_mw + extra_loss,
            'status': 'Cascading mulai'
        })
    else:
        stages.append({
            'tahap': 3,
            'waktu_menit': 1.0,
            'kejadian': 'Frekuensi masih dalam batas aman (49.5-50.2 Hz)',
            'beban_hilang_mw': data_center_load_mw,
            'status': 'Sistem stabil'
        })
    
    # Stage 4: Efek domino ke wilayah sekitar
    if len(stages) > 3 and stages[3]['beban_hilang_mw'] > data_center_load_mw:
        domino_effect = 3000
        stages.append({
            'tahap': 4,
            'waktu_menit': 3.0,
            'kejadian': f'Efek domino - {domino_effect} MW beban di sekitar Bekasi ikut padam',
            'beban_hilang_mw': stages[3]['beban_hilang_mw'] + domino_effect,
            'status': 'Cascading failure'
        })
    
    return stages


def estimate_recovery_time():
    """Estimasi waktu pemulihan untuk 3 skenario"""
    
    recovery_scenarios = {
        'skenario_ringan': {
            'deskripsi': 'Gangguan transmisi saja, pembangkit aman',
            'waktu_pemulihan_jam': 2,
            'beban_kembali_persen': 90
        },
        'skenario_sedang': {
            'deskripsi': 'Gangguan + PLTU hot start trip',
            'waktu_pemulihan_jam': 8,
            'beban_kembali_persen': 70
        },
        'skenario_berat': {
            'deskripsi': 'Gangguan + PLTU cold start (seperti Sumatra 2026)',
            'waktu_pemulihan_jam': 18,
            'beban_kembali_persen': 50
        }
    }
    
    return recovery_scenarios


# ============================================
# FUNGSI PEMBUATAN PETA
# ============================================

def create_vulnerability_map():
    """Membuat peta interaktif kerentanan grid Jawa"""
    
    risk_colors = {'Kritis': '#E74C3C', 'Sangat Tinggi': '#E67E22', 
                   'Tinggi': '#F39C12', 'Sedang': '#F1C40F'}
    
    fig = px.scatter_mapbox(
        critical_locations,
        lat='lat', lon='lon',
        color='risiko',
        size='beban_mw',
        hover_name='nama',
        hover_data={'jenis': True, 'keterangan': True, 'beban_mw': ':,.0f MW'},
        color_discrete_map=risk_colors,
        zoom=8,
        center=dict(lat=-6.250, lon=107.000),
        title='🗺️ Titik-Titik Kritis Grid Jawa di Sekitar Bekasi'
    )
    
    fig.update_layout(
        mapbox_style="open-street-map",
        height=500,
        margin=dict(l=0, r=0, t=40, b=0)
    )
    
    return fig


# ============================================
# MAIN FUNCTION
# ============================================

def main():
    print("=" * 70)
    print("⚠️ ANALISIS CASCADING FAILURE")
    print("Studi Kasus: Pusat Data AI 500 MW di Bekasi")
    print("=" * 70)
    
    # 1. Baseline
    print("\n📊 [1] BASELINE: BLACKOUT SUMATRA 2026")
    print("-" * 50)
    print(f"   Total pelanggan: {sumatra_blackout['total_pelanggan_terdampak']:,}")
    print(f"   Pasokan hilang: {sumatra_blackout['total_pasokan_mw']} MW")
    print(f"   Waktu pemulihan PLTU: {sumatra_blackout['waktu_pemulihan_pltu']} jam")
    
    # 2. Simulasi
    print("\n⚡ [2] SIMULASI CASCADING FAILURE")
    print("-" * 50)
    stages = simulate_cascading_failure()
    for stage in stages:
        print(f"   Tahap {stage['tahap']}: {stage['kejadian'][:50]}...")
    
    # 3. Recovery
    print("\n⏱️ [3] ESTIMASI WAKTU PEMULIHAN")
    print("-" * 50)
    recovery = estimate_recovery_time()
    for skenario, data in recovery.items():
        print(f"   {skenario}: {data['waktu_pemulihan_jam']} jam")
    
    # 4. Simpan hasil
    print("\n💾 [4] MENYIMPAN HASIL")
    
    results = {
        'sumatra_baseline': sumatra_blackout,
        'critical_locations': critical_locations.to_dict('records'),
        'cascading_stages': stages,
        'recovery_scenarios': recovery,
        'generated_at': datetime.now().isoformat()
    }
    
    output_path = PROCESSED_DATA_DIR / 'cascading_failure_analysis.json'
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    print(f"   ✅ Tersimpan di: {output_path}")
    
    # 5. Buat peta
    print("\n🗺️ [5] MEMBUAT PETA KERENTANAN")
    fig = create_vulnerability_map()
    fig.write_html(FIGURES_DIR / 'vulnerability_map.html')
    print(f"   ✅ Tersimpan di: {FIGURES_DIR / 'vulnerability_map.html'}")
    
    print("\n" + "=" * 70)
    print("✅ ANALISIS SELESAI!")
    print("=" * 70)
    
    return results


if __name__ == "__main__":
    main()
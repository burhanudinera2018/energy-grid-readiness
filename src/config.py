# src/config.py
from pathlib import Path
import os
import pandas as pd
import numpy as np
import tempfile

# ============================================
# DETEKSI LINGKUNGAN (LOCAL vs CLOUD)
# ============================================

def is_streamlit_cloud():
    """Cek apakah sedang berjalan di Streamlit Cloud"""
    return os.environ.get('STREAMLIT_SHARING_MODE', '').lower() == 'true' or 'STREAMLIT_CLOUD' in os.environ

def get_project_root():
    """Mendapatkan root directory project dengan aman"""
    possible_roots = [
        Path(__file__).parent.parent,
        Path('/mount/src/energy-grid-readiness'),
        Path('/app'),
        Path.cwd(),
    ]
    
    for root in possible_roots:
        if root.exists():
            return root
    
    return Path(tempfile.gettempdir()) / 'energy-grid-readiness'

# ============================================
# SETUP PATH DENGAN AMAN
# ============================================

PROJECT_ROOT = get_project_root()

DATA_DIR = PROJECT_ROOT / 'data'
RAW_DATA_DIR = DATA_DIR / 'raw'
PROCESSED_DATA_DIR = DATA_DIR / 'processed'

OUTPUT_DIR = PROJECT_ROOT / 'output'
FIGURES_DIR = OUTPUT_DIR / 'figures'
TABLES_DIR = OUTPUT_DIR / 'tables'

# ============================================
# MEMBUAT DIREKTORI DENGAN AMAN
# ============================================

def safe_mkdir(path):
    """Membuat direktori dengan aman (tidak error jika gagal)"""
    try:
        path.mkdir(parents=True, exist_ok=True)
        return True
    except (PermissionError, OSError):
        return False

safe_mkdir(RAW_DATA_DIR)
safe_mkdir(PROCESSED_DATA_DIR)
safe_mkdir(FIGURES_DIR)
safe_mkdir(TABLES_DIR)

# ============================================
# KOORDINAT PROVINSI REALISTIS (UNTUK FALLBACK)
# ============================================

PROVINCE_COORDS = {
    'Aceh': (4.5, 96.5),
    'Sumatera Utara': (2.0, 99.0),
    'Sumatera Barat': (-1.0, 100.5),
    'Riau': (0.5, 102.0),
    'Jambi': (-1.5, 103.5),
    'Sumatera Selatan': (-3.0, 104.0),
    'Bengkulu': (-3.5, 102.0),
    'Lampung': (-4.5, 105.0),
    'Kep. Bangka Belitung': (-2.5, 106.5),
    'Kep. Riau': (0.5, 107.0),
    'DKI Jakarta': (-6.2, 106.8),
    'Jawa Barat': (-6.8, 107.5),
    'Jawa Tengah': (-7.5, 110.0),
    'DI Yogyakarta': (-7.8, 110.4),
    'Jawa Timur': (-7.5, 112.5),
    'Banten': (-6.3, 106.0),
    'Bali': (-8.3, 115.2),
    'Nusa Tenggara Barat': (-8.5, 118.0),
    'Nusa Tenggara Timur': (-8.8, 121.5),
    'Kalimantan Barat': (0.0, 110.0),
    'Kalimantan Tengah': (-1.5, 113.0),
    'Kalimantan Selatan': (-3.0, 115.0),
    'Kalimantan Timur': (0.5, 117.0),
    'Kalimantan Utara': (3.0, 116.0),
    'Sulawesi Utara': (1.0, 124.0),
    'Sulawesi Tengah': (-1.0, 121.0),
    'Sulawesi Selatan': (-4.0, 120.0),
    'Sulawesi Tenggara': (-4.0, 122.5),
    'Gorontalo': (0.5, 123.0),
    'Sulawesi Barat': (-2.5, 119.5),
    'Maluku': (-3.0, 129.0),
    'Maluku Utara': (0.5, 127.5),
    'Papua Barat': (-1.5, 133.0),
    'Papua': (-4.0, 138.0),
}

# ============================================
# FALLBACK DATA (REALISTIS)
# ============================================

def get_fallback_plants_data():
    """Fallback data pembangkit dengan koordinat REALISTIS (bukan random)"""
    
    fuel_types = ['Coal', 'Gas', 'Hydro', 'Geothermal', 'Solar', 'Wind', 'Biomass']
    fuel_weights = [0.35, 0.20, 0.15, 0.10, 0.10, 0.05, 0.05]  # distribusi realistis
    
    data = []
    for province, (base_lat, base_lon) in PROVINCE_COORDS.items():
        # Setiap provinsi punya 3-10 pembangkit
        num_plants = np.random.randint(3, 11)
        
        for i in range(num_plants):
            # Koordinat dengan variasi kecil dalam provinsi (masih di daratan)
            lat_variasi = base_lat + np.random.uniform(-0.8, 0.8)
            lon_variasi = base_lon + np.random.uniform(-0.8, 0.8)
            
            # Kapasitas bervariasi
            capacity = np.random.choice([10, 25, 50, 100, 200, 500, 1000], p=[0.3, 0.25, 0.2, 0.1, 0.08, 0.05, 0.02])
            
            # Tahun commissioning
            year = np.random.randint(1980, 2026)
            
            data.append({
                'name': f'PL{"TU" if np.random.random() > 0.5 else "TA"} {province} {i+1}',
                'country': 'IDN',
                'country_long': province,
                'primary_fuel': np.random.choice(fuel_types, p=fuel_weights),
                'capacity_mw': capacity,
                'latitude': lat_variasi,
                'longitude': lon_variasi,
                'commissioning_year': year,
            })
    
    return pd.DataFrame(data)


def get_fallback_gap_data():
    """Fallback data gap analysis"""
    years = list(range(2025, 2031))
    data = {
        'Tahun': years,
        'Total_Demand_MW': [1300, 1350, 1400, 1450, 1500, 1550],
        'Kapasitas_Jawa_MW': [55000, 58000, 60000, 62000, 65000, 68000],
        'Gap_Jawa_MW': [53700, 56650, 58600, 60550, 63500, 66450],
    }
    return pd.DataFrame(data)


def get_fallback_ebt_data():
    """Fallback data EBT dengan koordinat realistis"""
    data = []
    for province, (lat, lon) in PROVINCE_COORDS.items():
        data.append({
            'province': province,
            'lat': lat,
            'lon': lon,
            'total_potential_mw': np.random.randint(5000, 25000),
            'existing_capacity_mw': np.random.randint(10, 1000),
            'gap_mw': np.random.randint(4000, 24000),
            'utilization_rate': np.random.uniform(0.1, 5.0),
            'priority_level': np.random.choice(['Sangat Tinggi', 'Tinggi', 'Sedang', 'Rendah'], p=[0.1, 0.2, 0.3, 0.4]),
            'priority_score': np.random.uniform(40, 100),
        })
    return pd.DataFrame(data)


def get_fallback_coal_data():
    """Fallback data PLTU"""
    data = {
        'name': ['PLTU Paiton', 'PLTU Suralaya', 'PLTU Tanjung Jati', 'PLTU Cirebon', 'PLTU Tenayan',
                 'PLTU Lontar', 'PLTU Pelabuhan Ratu', 'PLTU Indramayu', 'PLTU Banten', 'PLTU Riau'],
        'capacity_mw': [1230, 3400, 1320, 660, 220, 650, 1000, 1000, 600, 300],
        'age_years': [25, 30, 20, 15, 25, 18, 22, 12, 10, 8],
        'annual_co2_tons': [8000000, 22000000, 8500000, 4300000, 1430000, 4200000, 6500000, 6500000, 3900000, 1950000],
        'priority_level': ['Tinggi', 'Sangat Tinggi', 'Tinggi', 'Sedang', 'Tinggi', 'Sedang', 'Tinggi', 'Sedang', 'Rendah', 'Rendah'],
        'latitude': [-7.5, -5.9, -6.5, -6.7, 0.5, -6.0, -6.9, -6.4, -6.0, 0.5],
        'longitude': [113.5, 106.0, 110.5, 108.5, 101.5, 106.5, 106.5, 108.5, 106.0, 101.5],
    }
    return pd.DataFrame(data)


def get_fallback_cascading_data():
    """Fallback data cascading failure"""
    return {
        'sumatra_baseline': {
            'total_pelanggan_terdampak': 13100000,
            'total_pasokan_mw': 5344,
            'gardu_induk_terdampak': 176,
            'gardu_induk_pulih': 157,
            'waktu_pemulihan_pltu': 18,
            'waktu_pemulihan_transmisi': 2,
            'penyebab_utama': 'Gangguan SUTET 275 kV akibat cuaca buruk'
        },
        'cascading_stages': [
            {'tahap': 0, 'waktu_menit': 0, 'kejadian': 'Gangguan di GI Bekasi', 'beban_hilang_mw': 500, 'status': 'Gangguan lokal'},
            {'tahap': 1, 'waktu_menit': 0.1, 'kejadian': 'CB Trip - isolasi gangguan', 'beban_hilang_mw': 500, 'status': 'Isolasi gangguan'},
            {'tahap': 2, 'waktu_menit': 0.5, 'kejadian': 'Penurunan frekuensi ke 49.9 Hz', 'beban_hilang_mw': 500, 'status': 'Under-frequency'},
            {'tahap': 3, 'waktu_menit': 1.0, 'kejadian': 'Frekuensi dalam batas aman', 'beban_hilang_mw': 500, 'status': 'Sistem stabil'},
        ],
        'recovery_scenarios': {
            'skenario_ringan': {'deskripsi': 'Gangguan transmisi saja', 'waktu_pemulihan_jam': 2, 'beban_kembali_persen': 90},
            'skenario_sedang': {'deskripsi': 'Gangguan + PLTU hot start', 'waktu_pemulihan_jam': 8, 'beban_kembali_persen': 70},
            'skenario_berat': {'deskripsi': 'Gangguan + PLTU cold start', 'waktu_pemulihan_jam': 18, 'beban_kembali_persen': 50}
        },
        'critical_locations': [
            {'nama': 'Gardu Induk Bekasi', 'lat': -6.345, 'lon': 107.148, 'risiko': 'Kritis'},
            {'nama': 'Digital Edge Bekasi', 'lat': -6.238, 'lon': 107.001, 'risiko': 'Sangat Tinggi'},
            {'nama': 'SUTET 500 kV', 'lat': -6.280, 'lon': 106.950, 'risiko': 'Kritis'},
            {'nama': 'PLTU Suralaya', 'lat': -5.880, 'lon': 106.020, 'risiko': 'Tinggi'},
        ]
    }


def get_fallback_cba_data():
    """Fallback data CBA"""
    return {
        'subsidi_tahunan_juta_usd': 61,
        'biaya_pensiun_juta_usd': 110,
        'manfaat_subsidi_juta_usd': 832,
        'net_benefit_juta_usd': 722,
        'net_benefit_ratio': 7.6,
        'kenaikan_bpp_persen': 48,
        'total_potential_gw': 673,
        'total_existing_gw': 4.4,
        'provinsi_prioritas_sangat_tinggi': ['Jawa Timur', 'Jawa Barat', 'Jawa Tengah', 'Papua'],
        'provinsi_prioritas_tinggi': ['Aceh', 'Sulawesi Selatan', 'Bali', 'Sulawesi Tengah', 'Sulawesi Utara'],
        'threshold': {'p90_sangat_tinggi': 85, 'p75_tinggi': 75, 'p50_sedang': 65}
    }


def is_cloud_deployment():
    """Cek apakah sedang berjalan di Streamlit Cloud"""
    return is_streamlit_cloud()


# Cetak informasi path (hanya di lokal)
if not is_streamlit_cloud():
    print(f"✅ PROJECT_ROOT: {PROJECT_ROOT}")
    print(f"✅ RAW_DATA_DIR: {RAW_DATA_DIR}")
    print(f"✅ PROCESSED_DATA_DIR: {PROCESSED_DATA_DIR}")
    print(f"✅ FIGURES_DIR: {FIGURES_DIR}")
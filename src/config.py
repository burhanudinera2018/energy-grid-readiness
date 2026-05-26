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
    # Coba beberapa kemungkinan lokasi
    possible_roots = [
        Path(__file__).parent.parent,  # Lokasi normal
        Path('/mount/src/energy-grid-readiness'),  # Streamlit Cloud
        Path('/app'),  # Alternatif cloud
        Path.cwd(),  # Current working directory
    ]
    
    for root in possible_roots:
        if root.exists():
            return root
    
    # Fallback: gunakan temp directory
    return Path(tempfile.gettempdir()) / 'energy-grid-readiness'

# ============================================
# SETUP PATH DENGAN AMAN
# ============================================

PROJECT_ROOT = get_project_root()

# Data directories
DATA_DIR = PROJECT_ROOT / 'data'
RAW_DATA_DIR = DATA_DIR / 'raw'
PROCESSED_DATA_DIR = DATA_DIR / 'processed'

# Output directories
OUTPUT_DIR = PROJECT_ROOT / 'output'
FIGURES_DIR = OUTPUT_DIR / 'figures'
TABLES_DIR = OUTPUT_DIR / 'tables'

# ============================================
# MEMBUAT DIREKTORI DENGAN AMAN (TIDAK ERROR)
# ============================================

def safe_mkdir(path):
    """Membuat direktori dengan aman (tidak error jika gagal)"""
    try:
        path.mkdir(parents=True, exist_ok=True)
        return True
    except (PermissionError, OSError):
        # Di cloud, mungkin tidak bisa membuat folder
        return False

# Buat direktori (abaikan jika gagal)
safe_mkdir(RAW_DATA_DIR)
safe_mkdir(PROCESSED_DATA_DIR)
safe_mkdir(FIGURES_DIR)
safe_mkdir(TABLES_DIR)

# ============================================
# FALLBACK DATA (Untuk Streamlit Cloud Deployment)
# ============================================

def get_fallback_plants_data():
    """Fallback data pembangkit jika file CSV tidak ditemukan"""
    import pandas as pd
    import numpy as np
    
    provinces = [
        'Aceh', 'Sumatera Utara', 'Sumatera Barat', 'Riau', 'Jambi',
        'Sumatera Selatan', 'Bengkulu', 'Lampung', 'Kep. Bangka Belitung', 'Kep. Riau',
        'DKI Jakarta', 'Jawa Barat', 'Jawa Tengah', 'DI Yogyakarta', 'Jawa Timur',
        'Banten', 'Bali', 'NTB', 'NTT', 'Kalimantan Barat',
        'Kalimantan Tengah', 'Kalimantan Selatan', 'Kalimantan Timur', 'Kalimantan Utara',
        'Sulawesi Utara', 'Sulawesi Tengah', 'Sulawesi Selatan', 'Sulawesi Tenggara',
        'Gorontalo', 'Sulawesi Barat', 'Maluku', 'Maluku Utara', 'Papua Barat', 'Papua'
    ]
    
    np.random.seed(42)
    data = []
    for prov in provinces:
        data.append({
            'name': f'PLTU {prov}',
            'country': 'IDN',
            'country_long': prov,
            'primary_fuel': np.random.choice(['Coal', 'Gas', 'Hydro', 'Geothermal', 'Solar'], p=[0.4, 0.2, 0.2, 0.1, 0.1]),
            'capacity_mw': np.random.uniform(10, 500),
            'latitude': -2.5 + np.random.uniform(-5, 5),
            'longitude': 118 + np.random.uniform(-10, 10),
            'commissioning_year': np.random.randint(1990, 2020),
        })
    
    return pd.DataFrame(data)


def get_fallback_gap_data():
    """Fallback data gap analysis jika file tidak ditemukan"""
    import pandas as pd
    
    years = list(range(2025, 2031))
    data = {
        'Tahun': years,
        'Total_Demand_MW': [1300, 1350, 1400, 1450, 1500, 1550],
        'Kapasitas_Jawa_MW': [55000, 58000, 60000, 62000, 65000, 68000],
        'Gap_Jawa_MW': [53700, 56650, 58600, 60550, 63500, 66450],
    }
    
    return pd.DataFrame(data)


def get_fallback_ebt_data():
    """Fallback data EBT jika file tidak ditemukan"""
    import pandas as pd
    
    data = {
        'province': ['Jawa Timur', 'Jawa Barat', 'Jawa Tengah', 'Papua', 'Aceh'],
        'total_potential_mw': [22400, 23200, 22100, 22500, 22250],
        'existing_capacity_mw': [680, 850, 520, 85, 85],
        'gap_mw': [21720, 22350, 21580, 22415, 22165],
        'priority_level': ['Sangat Tinggi', 'Sangat Tinggi', 'Sangat Tinggi', 'Sangat Tinggi', 'Tinggi']
    }
    
    return pd.DataFrame(data)


def get_fallback_coal_data():
    """Fallback data PLTU jika file tidak ditemukan"""
    import pandas as pd
    
    data = {
        'name': ['PLTU Paiton', 'PLTU Suralaya', 'PLTU Tanjung Jati', 'PLTU Cirebon', 'PLTU Tenayan'],
        'capacity_mw': [1230, 3400, 1320, 660, 220],
        'age_years': [25, 30, 20, 15, 25],
        'annual_co2_tons': [8000000, 22000000, 8500000, 4300000, 1430000],
        'priority_level': ['Tinggi', 'Sangat Tinggi', 'Tinggi', 'Sedang', 'Tinggi']
    }
    
    return pd.DataFrame(data)


def get_fallback_cascading_data():
    """Fallback data cascading failure jika file tidak ditemukan"""
    return {
        'sumatra_baseline': {
            'total_pelanggan_terdampak': 13100000,
            'total_pasokan_mw': 5344,
            'gardu_induk_terdampak': 176,
            'waktu_pemulihan_pltu': 18,
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
        }
    }


def get_fallback_cba_data():
    """Fallback data CBA jika file tidak ditemukan"""
    return {
        'subsidi_tahunan_juta_usd': 61,
        'biaya_pensiun_juta_usd': 110,
        'manfaat_subsidi_juta_usd': 832,
        'net_benefit_juta_usd': 722,
        'net_benefit_ratio': 7.6,
        'kenaikan_bpp_persen': 48
    }


def is_cloud_deployment():
    """Cek apakah sedang berjalan di Streamlit Cloud"""
    return is_streamlit_cloud()


# Cetak informasi path (untuk debugging)
if not is_streamlit_cloud():
    print(f"✅ PROJECT_ROOT: {PROJECT_ROOT}")
    print(f"✅ RAW_DATA_DIR: {RAW_DATA_DIR}")
    print(f"✅ PROCESSED_DATA_DIR: {PROCESSED_DATA_DIR}")
    print(f"✅ FIGURES_DIR: {FIGURES_DIR}")
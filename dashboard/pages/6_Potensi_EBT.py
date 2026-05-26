# dashboard/pages/6_Potensi_EBT.py
import streamlit as st
import pandas as pd
import plotly.express as px
import json
from pathlib import Path
import sys

project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from src.config import PROCESSED_DATA_DIR, FIGURES_DIR
from utils_fallback import load_ebt_data, check_data_status
from footer import show_footer

st.set_page_config(page_title="Potensi EBT", layout="wide")
st.title("🌱 Analisis Potensi EBT Indonesia")
st.markdown("### Identifikasi Provinsi Prioritas Pengembangan Energi Baru Terbarukan")
st.markdown("*Metode: Persentil (P90, P75, P50, P25) untuk prioritas yang objektif*")

# Cek status data
data_available = check_data_status()

# Load data dengan fallback
df_ebt = load_ebt_data()

# ============================================
# PERBAIKAN 1: Gunakan koordinat dari CSV, bukan hardcode
# ============================================

# Pastikan kolom lat/lon ada dan numeric
if 'lat' in df_ebt.columns and 'lon' in df_ebt.columns:
    # Sudah ada kolom lat/lon, langsung pakai
    df_ebt['lat'] = pd.to_numeric(df_ebt['lat'], errors='coerce')
    df_ebt['lon'] = pd.to_numeric(df_ebt['lon'], errors='coerce')
else:
    # Fallback: koordinat lengkap 38 provinsi
    province_coords = {
        'Aceh': (4.6951, 96.7494),
        'Sumatera Utara': (2.1154, 99.5451),
        'Sumatera Barat': (-0.7399, 100.8000),
        'Riau': (0.2933, 101.7068),
        'Jambi': (-1.6101, 103.6131),
        'Sumatera Selatan': (-3.3194, 103.9144),
        'Bengkulu': (-3.7928, 102.2608),
        'Lampung': (-5.4500, 105.2667),
        'Kepulauan Bangka Belitung': (-2.8000, 106.1167),
        'Kepulauan Riau': (0.9000, 104.4500),
        'DKI Jakarta': (-6.2088, 106.8456),
        'Jawa Barat': (-6.9175, 107.6191),
        'Jawa Tengah': (-7.1509, 110.1403),
        'DI Yogyakarta': (-7.7956, 110.3695),
        'Jawa Timur': (-7.5361, 112.2384),
        'Banten': (-6.4058, 106.0640),
        'Bali': (-8.3405, 115.0920),
        'Nusa Tenggara Barat': (-8.6529, 117.3616),
        'Nusa Tenggara Timur': (-8.6574, 121.0794),
        'Kalimantan Barat': (-0.0288, 109.3244),
        'Kalimantan Tengah': (-1.6815, 113.3824),
        'Kalimantan Selatan': (-3.0926, 115.2838),
        'Kalimantan Timur': (0.5387, 116.4194),
        'Kalimantan Utara': (3.0731, 116.0411),
        'Sulawesi Utara': (1.3985, 124.2441),
        'Sulawesi Tengah': (-0.9000, 119.8667),
        'Sulawesi Selatan': (-3.6688, 119.9741),
        'Sulawesi Tenggara': (-3.9752, 122.5151),
        'Gorontalo': (0.5435, 123.0568),
        'Sulawesi Barat': (-2.4975, 119.3918),
        'Maluku': (-3.2385, 130.1453),
        'Maluku Utara': (1.5700, 127.8088),
        'Papua Barat': (-1.3362, 133.1747),
        'Papua': (-4.2699, 138.0804),
        'Papua Tengah': (-3.0000, 136.0000),
        'Papua Pegunungan': (-4.0000, 139.0000),
        'Papua Selatan': (-7.0000, 139.0000),
    }
    
    # Terapkan koordinat
    df_ebt['lat'] = df_ebt['province'].map(lambda x: province_coords.get(x, (-2.5, 118))[0])
    df_ebt['lon'] = df_ebt['province'].map(lambda x: province_coords.get(x, (-2.5, 118))[1])

# Hapus data dengan koordinat invalid
df_ebt = df_ebt.dropna(subset=['lat', 'lon'])

# Filter koordinat di dalam batas Indonesia
df_ebt = df_ebt[(df_ebt['lat'].between(-11, 6)) & (df_ebt['lon'].between(95, 141))]

# ============================================
# PERBAIKAN 2: Tampilkan koordinat yang digunakan
# ============================================

with st.expander("📍 Validasi Koordinat Provinsi"):
    st.success(f"✅ {len(df_ebt)} provinsi memiliki koordinat valid")
    koordinat_tampil = df_ebt[['province', 'lat', 'lon', 'priority_level']].copy()
    koordinat_tampil['lat'] = koordinat_tampil['lat'].round(4)
    koordinat_tampil['lon'] = koordinat_tampil['lon'].round(4)
    st.dataframe(koordinat_tampil, use_container_width=True, hide_index=True)

# ============================================
# PERBAIKAN 3: Load hasil rekomendasi
# ============================================

json_path = PROCESSED_DATA_DIR / 'ebt_potential_results.json'
if json_path.exists():
    with open(json_path, 'r') as f:
        results = json.load(f)
else:
    results = {
        'total_potential_gw': 673,
        'total_existing_gw': 4.4,
        'provinsi_prioritas_sangat_tinggi': df_ebt[df_ebt['priority_level'] == 'Sangat Tinggi']['province'].tolist(),
        'provinsi_prioritas_tinggi': df_ebt[df_ebt['priority_level'] == 'Tinggi']['province'].tolist(),
        'threshold': {'p90_sangat_tinggi': 85, 'p75_tinggi': 75, 'p50_sedang': 65}
    }

# ============================================
# METRIK UTAMA
# ============================================

st.header("📊 Ringkasan Eksekutif")
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Potensi EBT", f"{results.get('total_potential_gw', 673):.0f} GW", "673 GW")
with col2:
    st.metric("Kapasitas Existing", f"{results.get('total_existing_gw', 4.4):.1f} GW", "4,4 GW")
with col3:
    gap = results.get('total_potential_gw', 673) - results.get('total_existing_gw', 4.4)
    st.metric("Gap Pengembangan", f"{gap:.0f} GW", "669 GW")
with col4:
    st.metric("Provinsi Prioritas", f"{len(results.get('provinsi_prioritas_sangat_tinggi', []))}", "Sangat Tinggi")

# ============================================
# METODE
# ============================================

with st.expander("📐 Metode Penentuan Prioritas (Persentil)"):
    st.markdown(f"""
    **Pendekatan Statistik yang Digunakan:**
    | Level | Persentil | Jumlah Provinsi |
    |:------|:----------|:----------------|
    | 🔴 Sangat Tinggi | ≥ P90 (Top 10%) | {len(results.get('provinsi_prioritas_sangat_tinggi', []))} |
    | 🟠 Tinggi | P75 - P90 | {len(results.get('provinsi_prioritas_tinggi', []))} |
    """)

# ============================================
# PETA PRIORITAS - PERBAIKAN UTAMA
# ============================================

st.header("🗺️ Peta Prioritas Pengembangan EBT")

# Definisi warna prioritas
priority_colors = {
    'Sangat Tinggi': '#E74C3C',  # Merah
    'Tinggi': '#F39C12',         # Oranye
    'Sedang': '#F1C40F',         # Kuning
    'Rendah': '#2ECC71'          # Hijau
}

# Pastikan kolom priority_level ada
if 'priority_level' not in df_ebt.columns:
    df_ebt['priority_level'] = 'Sedang'

# Buat peta dengan data yang sudah memiliki koordinat valid
df_map = df_ebt.dropna(subset=['lat', 'lon'])

if len(df_map) > 0:
    fig_map = px.scatter_mapbox(
        df_map,
        lat='lat',
        lon='lon',
        size='gap_mw',
        color='priority_level',
        hover_name='province',
        hover_data={
            'total_potential_mw': ':,.0f MW',
            'existing_capacity_mw': ':,.0f MW',
            'gap_mw': ':,.0f MW',
            'utilization_rate': '{:.1f}%',
            'lat': False,
            'lon': False
        },
        color_discrete_map=priority_colors,
        size_max=25,
        zoom=4.5,
        center=dict(lat=-2.5, lon=118),
        title='Prioritas Pengembangan EBT per Provinsi',
        mapbox_style="open-street-map"
    )
    
    fig_map.update_layout(
        height=600,
        margin=dict(l=0, r=0, t=40, b=0),
        legend_title_text='Level Prioritas'
    )
    
    st.plotly_chart(fig_map, use_container_width=True)
    
    # Informasi tambahan
    st.info(f"📍 Menampilkan {len(df_map)} provinsi dengan koordinat valid")
else:
    st.error("❌ Tidak ada data provinsi dengan koordinat valid untuk ditampilkan di peta")

# ============================================
# PRIORITAS PROVINSI
# ============================================

st.header("🎯 Prioritas Pengembangan EBT")

col1, col2 = st.columns(2)

with col1:
    st.subheader("🔴 Prioritas SANGAT TINGGI")
    sangat_tinggi = df_ebt[df_ebt['priority_level'] == 'Sangat Tinggi'][['province', 'total_potential_mw', 'existing_capacity_mw', 'gap_mw']].copy()
    if len(sangat_tinggi) > 0:
        sangat_tinggi.columns = ['Provinsi', 'Potensi (MW)', 'Existing (MW)', 'Gap (MW)']
        st.dataframe(sangat_tinggi, use_container_width=True, hide_index=True)
    else:
        st.info("Tidak ada provinsi dengan prioritas sangat tinggi")

with col2:
    st.subheader("🟠 Prioritas TINGGI")
    tinggi = df_ebt[df_ebt['priority_level'] == 'Tinggi'][['province', 'total_potential_mw', 'existing_capacity_mw', 'gap_mw']].copy()
    if len(tinggi) > 0:
        tinggi.columns = ['Provinsi', 'Potensi (MW)', 'Existing (MW)', 'Gap (MW)']
        st.dataframe(tinggi, use_container_width=True, hide_index=True)
    else:
        st.info("Tidak ada provinsi dengan prioritas tinggi")

# ============================================
# DATA TABLE LENGKAP
# ============================================

with st.expander("📋 Lihat Seluruh Data EBT per Provinsi"):
    st.dataframe(
        df_ebt[['province', 'total_potential_mw', 'existing_capacity_mw', 'gap_mw', 'utilization_rate', 'priority_level', 'lat', 'lon']],
        use_container_width=True,
        hide_index=True
    )

# ============================================
# FOOTER
# ============================================

show_footer("Analisis Potensi EBT - Metode Persentil | Data: GPPD, Statistik PLN, Kementerian ESDM | Koordinat: Pusat Provinsi")
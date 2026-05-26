# dashboard/pages/6_Potensi_EBT.py
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
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

# Coba load hasil rekomendasi
json_path = PROCESSED_DATA_DIR / 'ebt_potential_results.json'
if json_path.exists():
    with open(json_path, 'r') as f:
        results = json.load(f)
else:
    results = {
        'total_potential_gw': 673,
        'total_existing_gw': 4.4,
        'provinsi_prioritas_sangat_tinggi': ['Jawa Timur', 'Jawa Barat', 'Jawa Tengah', 'Papua'],
        'provinsi_prioritas_tinggi': ['Aceh', 'Sulawesi Selatan', 'Bali', 'Sulawesi Tengah', 'Sulawesi Utara'],
        'threshold': {'p90_sangat_tinggi': 85, 'p75_tinggi': 75, 'p50_sedang': 65}
    }

# Metrik utama
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

# Metode
with st.expander("📐 Metode Penentuan Prioritas (Persentil)"):
    st.markdown(f"""
    **Pendekatan Statistik yang Digunakan:**
    | Level | Persentil | Jumlah Provinsi |
    |:------|:----------|:----------------|
    | 🔴 Sangat Tinggi | ≥ P90 (Top 10%) | {len(results.get('provinsi_prioritas_sangat_tinggi', []))} |
    | 🟠 Tinggi | P75 - P90 | {len(results.get('provinsi_prioritas_tinggi', []))} |
    """)

# Peta prioritas
st.header("🗺️ Peta Prioritas Pengembangan EBT")

province_coords = {
    'Jawa Timur': {'lat': -7.5, 'lon': 112.5}, 'Jawa Barat': {'lat': -6.8, 'lon': 107.5},
    'Jawa Tengah': {'lat': -7.5, 'lon': 110.0}, 'Papua': {'lat': -4.0, 'lon': 138.0},
    'Aceh': {'lat': 4.5, 'lon': 96.5}, 'Sulawesi Selatan': {'lat': -4.0, 'lon': 120.0},
    'Bali': {'lat': -8.3, 'lon': 115.2}, 'Sulawesi Tengah': {'lat': -1.0, 'lon': 121.0},
    'Sulawesi Utara': {'lat': 1.0, 'lon': 124.0},
}

df_ebt['lat'] = df_ebt['province'].map(lambda x: province_coords.get(x, {}).get('lat', -2.5))
df_ebt['lon'] = df_ebt['province'].map(lambda x: province_coords.get(x, {}).get('lon', 118))

priority_colors = {'Sangat Tinggi': '#E74C3C', 'Tinggi': '#F39C12', 'Sedang': '#F1C40F', 'Rendah': '#2ECC71'}
df_map = df_ebt.dropna(subset=['lat', 'lon'])
if len(df_map) > 0:
    fig_map = px.scatter_mapbox(df_map, lat='lat', lon='lon', size='gap_mw', color='priority_level',
                                 hover_name='province', hover_data={'total_potential_mw': ':,.0f MW', 'gap_mw': ':,.0f MW'},
                                 color_discrete_map=priority_colors, zoom=3.5, center=dict(lat=-2.5, lon=118),
                                 title='Prioritas Pengembangan EBT per Provinsi', mapbox_style="open-street-map")
    fig_map.update_layout(height=600, margin=dict(l=0, r=0, t=40, b=0))
    st.plotly_chart(fig_map, use_container_width=True)

# Prioritas provinsi
st.header("🎯 Prioritas Pengembangan EBT")
col1, col2 = st.columns(2)
with col1:
    st.subheader("🔴 Prioritas SANGAT TINGGI")
    sangat_tinggi = df_ebt[df_ebt['priority_level'] == 'Sangat Tinggi'][['province', 'total_potential_mw', 'existing_capacity_mw', 'gap_mw']].copy()
    sangat_tinggi.columns = ['Provinsi', 'Potensi (MW)', 'Existing (MW)', 'Gap (MW)']
    st.dataframe(sangat_tinggi, use_container_width=True, hide_index=True)
with col2:
    st.subheader("🟠 Prioritas TINGGI")
    tinggi = df_ebt[df_ebt['priority_level'] == 'Tinggi'][['province', 'total_potential_mw', 'existing_capacity_mw', 'gap_mw']].copy()
    tinggi.columns = ['Provinsi', 'Potensi (MW)', 'Existing (MW)', 'Gap (MW)']
    st.dataframe(tinggi, use_container_width=True, hide_index=True)

# Footer
show_footer("Analisis Potensi EBT - Metode Persentil | Data: GPPD, Statistik PLN, Kementerian ESDM")
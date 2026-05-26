# dashboard/pages/5_Pensiun_PLTU.py
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import json
from pathlib import Path
import sys

project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from src.config import PROCESSED_DATA_DIR
from utils_fallback import load_coal_data, check_data_status
from footer import show_footer

st.set_page_config(page_title="Pensiun PLTU", layout="wide")
st.title("🏭 Analisis Pensiun Dini PLTU Batubara")
st.markdown("### Membandingkan Skenario BAU vs Pensiun Dini (2026-2056)")

# Cek status data
data_available = check_data_status()

# Load data dengan fallback
df_coal = load_coal_data()

# Coba load hasil agregasi jika ada
json_path = PROCESSED_DATA_DIR / 'coal_retirement_results.json'
if json_path.exists():
    with open(json_path, 'r') as f:
        results = json.load(f)
else:
    results = {
        'total_plants': len(df_coal),
        'total_capacity_mw': df_coal['capacity_mw'].sum() if 'capacity_mw' in df_coal.columns else 29333,
        'total_annual_co2_million_tons': 183.1,
        'total_annual_cost_billion_usd': 11.3,
        'total_cost_bau_billion_usd': 752,
        'total_cost_pensiun_cepat_billion_usd': 351,
        'total_cost_pensiun_agresif_billion_usd': 100.3,
        'savings_cepat_billion_usd': 401,
        'savings_agresif_billion_usd': 651.7,
        'health_cost_saving_billion_usd': 2080
    }

# Metrik utama
st.header("📊 Ringkasan Eksekutif")
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total PLTU", f"{results.get('total_plants', 0)}", "70 unit")
with col2:
    st.metric("Total Kapasitas", f"{results.get('total_capacity_mw', 0)/1000:.1f} GW", "29,333 MW")
with col3:
    st.metric("Emisi CO2/Tahun", f"{results.get('total_annual_co2_million_tons', 0):.1f} Jt ton", "183 Juta ton")
with col4:
    st.metric("Biaya Operasional/Tahun", f"${results.get('total_annual_cost_billion_usd', 0):.1f} M", "US$ 11.3 Miliar")

# Perbandingan skenario
st.header("💰 Perbandingan Skenario Biaya")

col1, col2 = st.columns(2)
with col1:
    scenarios = ['BAU (2056)', 'Pensiun Cepat (2040)', 'Pensiun Agresif (2030)']
    costs = [results.get('total_cost_bau_billion_usd', 0), 
             results.get('total_cost_pensiun_cepat_billion_usd', 0),
             results.get('total_cost_pensiun_agresif_billion_usd', 0)]
    fig = go.Figure()
    fig.add_trace(go.Bar(x=scenarios, y=costs, text=[f'${c:.1f} B' for c in costs],
                          textposition='auto', marker_color=['#3498DB', '#F39C12', '#E74C3C']))
    fig.update_layout(title='Total Biaya (Operasional + Karbon)', xaxis_title='Skenario',
                       yaxis_title='Biaya (US$ Miliar)', height=400)
    st.plotly_chart(fig, use_container_width=True)

with col2:
    savings = [results.get('savings_cepat_billion_usd', 0), results.get('savings_agresif_billion_usd', 0)]
    fig2 = go.Figure()
    fig2.add_trace(go.Bar(x=['Pensiun Cepat (2040)', 'Pensiun Agresif (2030)'], y=savings,
                           text=[f'${s:.1f} B' for s in savings], textposition='auto',
                           marker_color=['#2ECC71', '#27AE60']))
    fig2.update_layout(title='Penghematan vs Skenario BAU', xaxis_title='Skenario',
                        yaxis_title='Penghematan (US$ Miliar)', height=400)
    st.plotly_chart(fig2, use_container_width=True)

# Peta prioritas
st.header("🗺️ Peta Prioritas Pensiun PLTU")
priority_colors = {'Sangat Tinggi': '#E74C3C', 'Tinggi': '#F39C12', 'Sedang': '#F1C40F', 'Rendah': '#2ECC71'}
if 'latitude' in df_coal.columns and 'longitude' in df_coal.columns:
    df_map = df_coal.dropna(subset=['latitude', 'longitude'])
    if len(df_map) > 0:
        fig_map = px.scatter_mapbox(df_map, lat='latitude', lon='longitude', size='capacity_mw', color='priority_level',
                                     hover_name='name', hover_data={'capacity_mw': ':,.0f MW', 'age_years': 'tahun'},
                                     color_discrete_map=priority_colors, zoom=4, center=dict(lat=-2.5, lon=118),
                                     title='Prioritas Pensiun PLTU Batubara Indonesia', mapbox_style="open-street-map")
        fig_map.update_layout(height=600, margin=dict(l=0, r=0, t=40, b=0))
        st.plotly_chart(fig_map, use_container_width=True)

# Top prioritas
st.header("📋 Top 10 PLTU Prioritas Pensiun")
if 'priority_score' in df_coal.columns:
    top_priority = df_coal.nlargest(10, 'priority_score')[['name', 'capacity_mw', 'age_years', 'priority_level']].copy()
    top_priority.columns = ['Nama PLTU', 'Kapasitas (MW)', 'Umur (tahun)', 'Prioritas']
    st.dataframe(top_priority, use_container_width=True, hide_index=True)

# Kesimpulan
st.header("🎯 Kesimpulan")
st.markdown(f"""
<div style="background-color: #1a1a2e; padding: 20px; border-radius: 10px;">
    <p style="color: white;"><b>Berdasarkan analisis 70 PLTU batubara di Indonesia:</b></p>
    <ul style="color: #cccccc;">
    <li>Total emisi CO2 tahunan: <b>{results.get('total_annual_co2_million_tons', 0):.1f} Juta ton</b></li>
    <li>Biaya operasional + karbon tahunan: <b>US$ {results.get('total_annual_cost_billion_usd', 0):.1f} Miliar</b></li>
    <li>Pensiun cepat ke 2040 menghemat <b>US$ {results.get('savings_cepat_billion_usd', 0):.0f} Miliar</b></li>
    <li>Pensiun agresif ke 2030 menghemat <b>US$ {results.get('savings_agresif_billion_usd', 0):.0f} Miliar</b></li>
    </ul>
</div>
""", unsafe_allow_html=True)

# Footer
show_footer("Analisis Pensiun PLTU - Berdasarkan Data GPPD & Literatur IEEFA/IESR")
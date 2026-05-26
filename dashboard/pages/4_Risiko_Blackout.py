# dashboard/pages/4_Risiko_Blackout.py
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
from utils_fallback import load_cascading_data, check_data_status
from footer import show_footer

st.set_page_config(page_title="Risiko Blackout", layout="wide")
st.title("⚠️ Risiko Blackout & Contingency Plan")
st.markdown("### Belajar dari Blackout Sumatra 2026 untuk Pusat Data AI di Bekasi")

# Cek status data
data_available = check_data_status()

# Load data dengan fallback
results = load_cascading_data()

sumatra = results.get('sumatra_baseline', {})
stages = results.get('cascading_stages', [])
recovery = results.get('recovery_scenarios', {})

# Baseline Sumatra
st.header("📊 Baseline: Blackout Sumatra 2026")

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Pelanggan Terdampak", f"{sumatra.get('total_pelanggan_terdampak', 0):,}", "13,1 juta")
with col2:
    st.metric("Pasokan Hilang", f"{sumatra.get('total_pasokan_mw', 0):,} MW")
with col3:
    st.metric("Gardu Induk", f"{sumatra.get('gardu_induk_terdampak', 0)}", f"{sumatra.get('gardu_induk_pulih', 0)} pulih")
with col4:
    st.metric("Pemulihan PLTU", f"{sumatra.get('waktu_pemulihan_pltu', 0)} jam", "Cold start")

st.info(f"**Penyebab Utama:** {sumatra.get('penyebab_utama', 'Gangguan SUTET')}")

# Simulasi cascading failure
st.header("⚡ Simulasi Cascading Failure di Bekasi")

if stages:
    df_stages = pd.DataFrame(stages)
    fig = go.Figure()
    colors = ['#2ECC71', '#F39C12', '#E67E22', '#E74C3C', '#C0392B']
    for i, stage in enumerate(stages):
        fig.add_trace(go.Bar(x=[stage.get('tahap', i)], y=[stage.get('beban_hilang_mw', 0)],
                              name=f"Tahap {stage.get('tahap', i)}",
                              text=f"{stage.get('beban_hilang_mw', 0):,.0f} MW", textposition='auto',
                              marker_color=colors[i % len(colors)],
                              hovertemplate=f"<b>Tahap {stage.get('tahap', i)}</b><br>Waktu: {stage.get('waktu_menit', 0)} menit<br>{stage.get('kejadian', '')}<extra></extra>"))
    fig.update_layout(title='Timeline Cascading Failure', xaxis_title='Tahap', yaxis_title='Beban Hilang (MW)', height=450)
    st.plotly_chart(fig, use_container_width=True)

# Peta kerentanan
st.subheader("🗺️ Peta Kerentanan Grid Jawa")

critical_locations = pd.DataFrame([
    {'nama': 'Gardu Induk Bekasi (Cikarang)', 'lat': -6.345, 'lon': 107.148, 'jenis': 'Gardu Induk', 'risiko': 'Kritis', 'beban_mw': 500},
    {'nama': 'Digital Edge CGK Campus (Pusat Data)', 'lat': -6.238, 'lon': 107.001, 'jenis': 'Pusat Data', 'risiko': 'Sangat Tinggi', 'beban_mw': 500},
    {'nama': 'SUTET 500 kV Bekasi - Cawang', 'lat': -6.280, 'lon': 106.950, 'jenis': 'SUTET', 'risiko': 'Kritis', 'beban_mw': 1500},
    {'nama': 'PLTU Suralaya', 'lat': -5.880, 'lon': 106.020, 'jenis': 'Pembangkit', 'risiko': 'Tinggi', 'beban_mw': 3400},
])

risk_colors = {'Kritis': '#E74C3C', 'Sangat Tinggi': '#E67E22', 'Tinggi': '#F39C12', 'Sedang': '#F1C40F'}
fig_map = px.scatter_mapbox(critical_locations, lat='lat', lon='lon', color='risiko', size='beban_mw',
                             hover_name='nama', hover_data={'jenis': True, 'beban_mw': ':,.0f MW'},
                             color_discrete_map=risk_colors, zoom=8, center=dict(lat=-6.250, lon=107.000),
                             title='Titik-Titik Kritis Grid Jawa di Sekitar Bekasi', mapbox_style="open-street-map")
fig_map.update_layout(height=500, margin=dict(l=0, r=0, t=40, b=0))
st.plotly_chart(fig_map, use_container_width=True)

# Waktu pemulihan
st.header("⏱️ Estimasi Waktu Pemulihan")
if recovery:
    rec_data = []
    for s, d in recovery.items():
        rec_data.append({'Skenario': s.replace('_', ' ').title(), 'Jam': d.get('waktu_pemulihan_jam', 0), 
                         'Beban Kembali': f"{d.get('beban_kembali_persen', 0)}%"})
    df_rec = pd.DataFrame(rec_data)
    st.dataframe(df_rec, use_container_width=True, hide_index=True)

# Kerugian finansial
st.header("💰 Estimasi Kerugian Finansial (500 MW)")
loss_per_hour = 5000
kurs = 16000
if recovery:
    financial = []
    for s, d in recovery.items():
        dur = d.get('waktu_pemulihan_jam', 0)
        loss_usd = 500 * dur * loss_per_hour
        financial.append({'Skenario': s.replace('_', ' ').title(), 'Durasi': f"{dur} jam",
                          'Kerugian USD': f"US$ {loss_usd:,.0f}", 'Kerugian IDR': f"Rp {loss_usd * kurs:,.0f}"})
    st.dataframe(pd.DataFrame(financial), use_container_width=True, hide_index=True)

# Rekomendasi
st.header("📋 Rekomendasi Mitigasi")
tab1, tab2, tab3 = st.tabs(["🏢 Digital Edge", "⚡ PLN", "🤝 Kerjasama"])
with tab1:
    st.markdown("**Untuk Digital Edge:** BESS 2.000 MWh, Genset 500 MW, Dual substation, UPS 15-30 menit")
with tab2:
    st.markdown("**Untuk PLN:** Percepat transmisi, Double circuit SUTET, Skema UFLS, Audit cascading failure")
with tab3:
    st.markdown("**Kerjasama:** Latihan simulasi, SCADA link, SLA, Sharing investasi")

# Footer
show_footer("Risiko Blackout & Contingency Plan - Belajar dari Blackout Sumatra 2026")
# dashboard/app.py
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path
import sys

project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from src.config import PROCESSED_DATA_DIR
from utils_fallback import load_gap_data, check_data_status
from footer import show_footer

st.set_page_config(page_title="Energy Dashboard Indonesia", layout="wide", initial_sidebar_state="expanded")

st.title("⚡ Dashboard Kesiapan Grid Listrik Indonesia")
st.markdown("### Menghadapi Lonjakan Pusat Data AI 2025-2030")
st.markdown("---")

# Sidebar
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/9/9f/Flag_of_Indonesia.svg", width=100)
    st.header("📊 Navigasi")
    st.page_link("app.py", label=" Beranda", icon="🏠")
    st.page_link("pages/1_Peta_Pembangkit.py", label=" Peta Pembangkit", icon="🗺️")
    st.page_link("pages/2_Analisis_Gap.py", label=" Analisis Gap", icon="📈")
    st.page_link("pages/3_Transmisi_Rekomendasi.py", label=" Transmisi & Rekomendasi", icon="🔌")
    st.page_link("pages/4_Risiko_Blackout.py", label=" Risiko Blackout", icon="⚠️")
    st.page_link("pages/5_Pensiun_PLTU.py", label=" Pensiun PLTU", icon="🏭")
    st.page_link("pages/6_Potensi_EBT.py", label=" Potensi EBT", icon="🌱")
    st.markdown("---")
    st.caption(f"Data terakhir diperbarui: Mei 2026")
    st.caption("Sumber: GPPD, GTD, RUPTL PLN, IEEFA, IESR")

# Cek status data
data_available = check_data_status()

# Load data gap
df_gap = load_gap_data()

# Ringkasan
st.header("📋 Ringkasan Eksekutif")

if len(df_gap) > 0:
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("📅 Tahun Analisis", f"{df_gap['Tahun'].min()} - {df_gap['Tahun'].max()}")
    with col2:
        demand_2030 = df_gap[df_gap['Tahun'] == 2030]['Total_Demand_MW'].values[0] if 2030 in df_gap['Tahun'].values else 0
        st.metric("🎯 Beban Data Center 2030", f"{demand_2030:,.0f} MW", "+137% dari 2025")
    with col3:
        gap_2030 = df_gap[df_gap['Tahun'] == 2030]['Gap_Jawa_MW'].values[0] / 1000 if 2030 in df_gap['Tahun'].values else 0
        st.metric("✅ Gap Kapasitas Jawa 2030", f"{gap_2030:.1f} GW", "Positif (Aman)")
    with col4:
        st.metric("⚠️ Transmisi ke Jawa", "0 MW", "Tidak Ada")

# Temuan utama
st.subheader("🔍 Temuan Utama")
col1, col2 = st.columns(2)
with col1:
    st.info("""
    **✅ Kapasitas Pembangkit AMAN**
    - Kapasitas Jawa 2030: ~68 GW
    - Beban data center 2030: ~3.4 GW
    - **Masih tersisa ~64 GW**
    """)
with col2:
    st.warning("""
    **⚠️ Transmisi BOTTLENECK**
    - Kapasitas transmisi ke Jawa: **0 MW**
    - Proyek Jawa-Sumatra (3.000 MW) masih rencana
    - Ketergantungan penuh pada pembangkit lokal
    """)

# Grafik ringkasan
st.subheader("📊 Tren Beban Data Center vs Kapasitas Jawa")
if len(df_gap) > 0:
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df_gap['Tahun'], y=df_gap['Total_Demand_MW'] / 1000,
                              mode='lines+markers', name='Beban Data Center (GW)',
                              line=dict(color='#FF6B6B', width=3), marker=dict(size=10)))
    fig.add_trace(go.Scatter(x=df_gap['Tahun'], y=df_gap['Kapasitas_Jawa_MW'] / 1000,
                              mode='lines+markers', name='Kapasitas Pembangkit Jawa (GW)',
                              line=dict(color='#4ECDC4', width=3), marker=dict(size=10)))
    fig.update_layout(title='Perbandingan Beban Data Center vs Kapasitas Jawa',
                       xaxis_title='Tahun', yaxis_title='Kapasitas (GW)', hovermode='x unified')
    st.plotly_chart(fig, use_container_width=True)

# Footer
show_footer("Dashboard Kesiapan Grid Listrik Indonesia")
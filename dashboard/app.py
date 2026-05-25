# dashboard/app.py
"""
Dashboard Interaktif: Kesiapan Grid Listrik Indonesia untuk Pusat Data AI
Run dengan: streamlit run dashboard/app.py
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import sys

# Tambahkan path ke project root
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from src.config import PROCESSED_DATA_DIR, FIGURES_DIR

# Konfigurasi halaman
st.set_page_config(
    page_title="Energy Dashboard Indonesia",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Judul utama
st.title("⚡ Dashboard Kesiapan Grid Listrik Indonesia")
st.markdown("### Menghadapi Lonjakan Pusat Data AI 2025-2030")
st.markdown("---")

# Sidebar
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/9/9f/Flag_of_Indonesia.svg", width=100)
    st.header("📊 Navigasi")
    st.page_link("app.py", label="Beranda", icon="🏠")
    st.page_link("pages/1_Peta_Pembangkit.py", label="Peta Pembangkit", icon="🗺️")
    st.page_link("pages/2_Analisis_Gap.py", label="Analisis Gap", icon="📈")
    st.page_link("pages/3_Transmisi_Rekomendasi.py", label="Transmisi & Rekomendasi", icon="🔌")
    
    st.markdown("---")
    st.caption(f"Data terakhir diperbarui: Mei 2026")
    st.caption("Sumber: Global Power Plant Database, GTD, RUPTL PLN")

# ========== BERANDA ==========
st.header("📋 Ringkasan Eksekutif")

# Load data gap
gap_path = PROCESSED_DATA_DIR / 'final_gap_analysis.csv'
if gap_path.exists():
    df_gap = pd.read_csv(gap_path)
    
    # Metric cards
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="📅 Tahun Analisis", 
            value=f"{df_gap['Tahun'].min()} - {df_gap['Tahun'].max()}"
        )
    
    with col2:
        demand_2030 = df_gap[df_gap['Tahun'] == 2030]['Total_Demand_MW'].values[0]
        st.metric(
            label="🎯 Beban Data Center 2030", 
            value=f"{demand_2030:,.0f} MW",
            delta="+137% dari 2025"
        )
    
    with col3:
        gap_2030 = df_gap[df_gap['Tahun'] == 2030]['Gap_Jawa_MW'].values[0] / 1000
        st.metric(
            label="✅ Gap Kapasitas Jawa 2030", 
            value=f"{gap_2030:.1f} GW",
            delta="Positif (Aman)"
        )
    
    with col4:
        st.metric(
            label="⚠️ Transmisi ke Jawa", 
            value="0 MW",
            delta="Tidak Ada"
        )
    
    st.markdown("---")
    
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
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=df_gap['Tahun'], 
        y=df_gap['Total_Demand_MW'] / 1000,
        mode='lines+markers',
        name='Beban Data Center (GW)',
        line=dict(color='#FF6B6B', width=3),
        marker=dict(size=10)
    ))
    
    fig.add_trace(go.Scatter(
        x=df_gap['Tahun'], 
        y=df_gap['Kapasitas_Jawa_MW'] / 1000,
        mode='lines+markers',
        name='Kapasitas Pembangkit Jawa (GW)',
        line=dict(color='#4ECDC4', width=3),
        marker=dict(size=10)
    ))
    
    fig.update_layout(
        title='Perbandingan Beban Data Center vs Kapasitas Jawa',
        xaxis_title='Tahun',
        yaxis_title='Kapasitas (GW)',
        hovermode='x unified',
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1)
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
else:
    st.error("Data final_gap_analysis.csv tidak ditemukan. Jalankan script 05_complete_analysis.py terlebih dahulu.")

st.markdown("---")
st.caption("Dashboard ini dibuat untuk project portfolio analisis energi Indonesia | Data: GPPD, GTD, RUPTL PLN")

# ========== FOOTER COPYRIGHT ==========
st.markdown("---")
st.markdown(
    """
    <div style="text-align: center; padding: 20px; background-color: #f0f2f6; border-radius: 10px;">
        <p style="margin: 0; color: #1f1f1f;">
            © 2026 <strong>Burhanudin Badiuzaman</strong> - Portfolio Project Energy 2026
        </p>
        <p style="margin: 5px 0 0 0; font-size: 12px; color: #666;">
            Data sources: Global Power Plant Database | Global Transmission Database | RUPTL PLN
        </p>
    </div>
    """,
    unsafe_allow_html=True
)
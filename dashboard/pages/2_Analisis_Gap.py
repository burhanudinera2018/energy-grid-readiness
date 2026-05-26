# dashboard/pages/2_Analisis_Gap.py
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from pathlib import Path
import sys

project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from src.config import PROCESSED_DATA_DIR
from utils_fallback import load_gap_data, check_data_status
from footer import show_footer

st.set_page_config(page_title="Analisis Gap", layout="wide")
st.title("📈 Analisis Gap: Data Center vs Kapasitas Grid")
st.markdown("### Proyeksi Beban Pusat Data AI vs Kapasitas Pembangkit Jawa")

# Cek status data
data_available = check_data_status()

# Load data dengan fallback
df_gap = load_gap_data()

# Data proyek pusat data (untuk anotasi)
projects_schedule = pd.DataFrame([
    {'nama': 'EDGNEX MT Haryono (Jakarta)', 'tahun': 2026, 'kapasitas_mw': 19.2, 'status': 'Q3 2026', 'warna': '#FFA500'},
    {'nama': 'Digital Edge CGK Campus (Bekasi) - Fase 1', 'tahun': 2026, 'kapasitas_mw': 500, 'status': 'Q4 2026', 'warna': '#FF6B6B'},
    {'nama': 'EDGNEX Jakarta', 'tahun': 2026, 'kapasitas_mw': 144, 'status': 'Desember 2026', 'warna': '#FFA500'},
    {'nama': 'Digital Edge CGK Campus - Fase 2 (Ekspansi)', 'tahun': 2028, 'kapasitas_mw': 500, 'status': 'Rencana Ekspansi 2028', 'warna': '#FF6B6B'},
])

# Sidebar
st.sidebar.header("🎛️ Skenario Analisis")

growth_factor = st.sidebar.slider(
    "Faktor Pertumbuhan Beban Data Center (%)",
    min_value=50, max_value=200, value=100, step=10,
    help="100% = skenario dasar (proyeksi Research and Markets)"
) / 100

show_projects = st.sidebar.checkbox("📌 Tampilkan Anotasi Proyek Data Center", value=True)
show_historical = st.sidebar.checkbox("📊 Tampilkan Data Historis (2024-2025)", value=True)

# Data historis
historical_demand = pd.DataFrame([
    {'Tahun': 2024, 'Total_Demand_MW': 206},
    {'Tahun': 2025, 'Total_Demand_MW': 243},
])

# Hitung skenario
df_scenario = df_gap.copy()
df_scenario['Total_Demand_Skenario_MW'] = df_scenario['Total_Demand_MW'] * growth_factor
df_scenario['Gap_Jawa_Skenario_MW'] = df_scenario['Kapasitas_Jawa_MW'] - df_scenario['Total_Demand_Skenario_MW']

# Grafik utama
st.subheader("📊 Perbandingan Skenario Beban Data Center")

fig = go.Figure()

fig.add_trace(go.Bar(
    x=df_gap['Tahun'], y=df_gap['Total_Demand_MW'] / 1000,
    name='Skenario Dasar (100%)', marker_color='#4ECDC4',
    hovertemplate='Tahun: %{x}<br>Beban Dasar: %{y:.1f} GW<extra></extra>'
))

fig.add_trace(go.Bar(
    x=df_scenario['Tahun'], y=df_scenario['Total_Demand_Skenario_MW'] / 1000,
    name=f'Skenario {growth_factor*100:.0f}%', marker_color='#FF6B6B',
    hovertemplate='Tahun: %{x}<br>Beban Skenario: %{y:.1f} GW<extra></extra>'
))

fig.add_trace(go.Scatter(
    x=df_gap['Tahun'], y=df_gap['Kapasitas_Jawa_MW'] / 1000,
    mode='lines+markers', name='Kapasitas Pembangkit Jawa (GW)',
    line=dict(color='#2E86AB', width=3, dash='dash'),
    marker=dict(size=10, symbol='diamond'),
    hovertemplate='Tahun: %{x}<br>Kapasitas Jawa: %{y:.1f} GW<extra></extra>'
))

if show_historical and len(historical_demand) > 0:
    fig.add_trace(go.Scatter(
        x=historical_demand['Tahun'], y=historical_demand['Total_Demand_MW'] / 1000,
        mode='markers', name='Data Historis (PLN Jabar)',
        marker=dict(size=12, symbol='circle', color='#9B59B6'),
        hovertemplate='Tahun: %{x}<br>Beban Aktual: %{y:.2f} GW<extra></extra>'
    ))

if show_projects:
    for _, proyek in projects_schedule.iterrows():
        beban_tahun = df_gap[df_gap['Tahun'] == proyek['tahun']]['Total_Demand_MW'].values
        beban_value = beban_tahun[0] / 1000 if len(beban_tahun) > 0 else 0
        
        fig.add_annotation(
            x=proyek['tahun'], y=beban_value + 0.5,
            text=f"🔵 {proyek['nama']}<br>{proyek['kapasitas_mw']} MW | {proyek['status']}",
            showarrow=True, arrowhead=2, arrowsize=1, arrowwidth=2,
            arrowcolor=proyek['warna'], ax=20, ay=(-40 if proyek['tahun'] % 2 == 0 else -60),
            bgcolor="rgba(255,255,255,0.9)", bordercolor=proyek['warna'],
            borderwidth=1, borderpad=4, font=dict(size=10, color=proyek['warna'])
        )
        
        fig.add_vline(x=proyek['tahun'], line_dash="dot", line_color=proyek['warna'],
                      line_width=1.5, opacity=0.5, annotation_text=f"⚡ {proyek['status']}",
                      annotation_position="top")

fig.update_layout(
    title={'text': 'Perbandingan Beban Data Center vs Kapasitas Jawa (2024-2030)', 'font': {'size': 16}},
    xaxis_title='Tahun', yaxis_title='Kapasitas / Beban (GW)',
    barmode='group', hovermode='x unified', height=600,
    legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1)
)

st.plotly_chart(fig, use_container_width=True)

# Metrik tahun 2026
st.subheader("🎯 Proyeksi dan Anotasi Proyek 2026")

col1, col2, col3, col4 = st.columns(4)
with col1:
    demand_2025 = df_gap[df_gap['Tahun'] == 2025]['Total_Demand_MW'].values[0]
    st.metric("Beban DC 2025", f"{demand_2025:.0f} MW", "Dasar")
with col2:
    total_2026 = projects_schedule[projects_schedule['tahun'] == 2026]['kapasitas_mw'].sum()
    st.metric("Proyek Beroperasi 2026", f"{total_2026:.0f} MW", "+ Tambahan Beban", delta_color="inverse")
with col3:
    demand_2026 = df_gap[df_gap['Tahun'] == 2026]['Total_Demand_MW'].values[0]
    st.metric("Beban DC 2026 (Proyeksi)", f"{demand_2026:.0f} MW", f"+{demand_2026 - demand_2025:.0f} MW dari 2025")
with col4:
    kapasitas_jawa_2026 = df_gap[df_gap['Tahun'] == 2026]['Kapasitas_Jawa_MW'].values[0]
    rasio = (demand_2026 / kapasitas_jawa_2026) * 100
    st.metric("Rasio DC vs Kapasitas Jawa", f"{rasio:.2f}%", "Masih Aman (<5%)")

# Kesimpulan
st.subheader("📝 Kesimpulan Analisis")
if show_projects:
    st.success("""
    **🎯 Insight Penting dari Anotasi Proyek:**
    1. **Tahun 2026 adalah titik balik** — tiga proyek besar mulai beroperasi (total ~663 MW tambahan beban)
    2. **Beban data center akan melonjak drastis** setelah Q3-Q4 2026, bukan sebelumnya
    3. **Dashboard ini menunjukkan proyeksi** — lonjakan belum terjadi karena proyek masih dalam konstruksi
    4. **Kapasitas pembangkit Jawa saat ini masih sangat aman** — buffer sekitar 45-50 GW
    5. **Rekomendasi:** Persiapkan infrastruktur sekarang, karena 2026-2027 beban akan meningkat signifikan
    """)

# Footer
show_footer("Analisis Gap - Proyeksi Beban Data Center dengan Anotasi Proyek 2026-2028")
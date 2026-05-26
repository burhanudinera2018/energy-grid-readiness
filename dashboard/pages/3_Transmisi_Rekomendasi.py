# dashboard/pages/3_Transmisi_Rekomendasi.py
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from pathlib import Path
import sys
from datetime import datetime

project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from src.config import PROCESSED_DATA_DIR
from utils_fallback import load_gap_data, check_data_status
from footer import show_footer

st.set_page_config(page_title="Transmisi & Rekomendasi", layout="wide")
st.title("🔌 Analisis Transmisi & Rekomendasi")
st.markdown("### Kapasitas Transmisi ke Jawa dan Proyek Interkoneksi")

# Cek status data
data_available = check_data_status()

# Load data gap untuk kapasitas Jawa
df_gap = load_gap_data()

# ============================================
# KAPASITAS TRANSMISI KE JAWA (EKSISTING)
# ============================================
st.header("📡 Kapasitas Transmisi ke Jawa (Eksisting)")

st.warning("⚠️ **Berdasarkan data GTD (Global Transmission Database):**")
st.info("""
**Implikasi:**
- Seluruh beban listrik di Jawa (termasuk pusat data AI di Bekasi) harus dipenuhi oleh pembangkit di Jawa sendiri
- Tidak ada 'backup' dari luar pulau jika terjadi gangguan besar
""")

# ============================================
# RENCANA TRANSMISI MENDATANG
# ============================================
st.header("📋 Rencana Transmisi Mendatang")

df_planned_manual = pd.DataFrame([
    {'from_region': 'IDNSM', 'to_region': 'IDNJW', 'max_flow': 3000, 
     'status': 'Rencana (Jawa-Sumatra)', 'target_tahun': 2028},
    {'from_region': 'IDNKA', 'to_region': 'IDNJW', 'max_flow': 2000, 
     'status': 'Rencana (Jawa-Kalimantan)', 'target_tahun': 2030},
])
st.dataframe(df_planned_manual, use_container_width=True)

# ============================================
# TIMELINE GANTT CHART (DIPERBAIKI)
# ============================================
st.subheader("📅 Timeline Proyek Transmisi (Gantt Chart)")

# Data untuk Gantt Chart dengan format tanggal yang benar
df_timeline = pd.DataFrame([
    {'Proyek': 'Jawa-Sumatra', 'Mulai': '2025-01-01', 'Selesai': '2028-12-31', 'Kapasitas_MW': 3000, 'Status': 'Rencana'},
    {'Proyek': 'Jawa-Kalimantan', 'Mulai': '2027-01-01', 'Selesai': '2030-12-31', 'Kapasitas_MW': 2000, 'Status': 'Rencana'},
])

# Konversi ke datetime
df_timeline['Mulai'] = pd.to_datetime(df_timeline['Mulai'])
df_timeline['Selesai'] = pd.to_datetime(df_timeline['Selesai'])

# Buat Gantt Chart
fig_gantt = px.timeline(
    df_timeline, 
    x_start='Mulai', 
    x_end='Selesai', 
    y='Proyek',
    color='Kapasitas_MW',
    title='Jadwal Proyek Transmisi Interkoneksi ke Jawa',
    labels={'Kapasitas_MW': 'Kapasitas (MW)', 'Proyek': 'Proyek Transmisi'},
    color_continuous_scale='Viridis'
)

fig_gantt.update_layout(
    height=400,
    xaxis_title='Tahun',
    yaxis_title='',
    showlegend=False
)

# Update x-axis untuk menampilkan tahun saja
fig_gantt.update_xaxes(
    tickformat="%Y",
    dtick="M12"
)

# Tambahkan anotasi kapasitas pada bar
for i, row in df_timeline.iterrows():
    mid_date = row['Mulai'] + (row['Selesai'] - row['Mulai']) / 2
    fig_gantt.add_annotation(
        x=mid_date,
        y=row['Proyek'],
        text=f"{row['Kapasitas_MW']} MW",
        showarrow=False,
        font=dict(size=10, color='white'),
        bgcolor='rgba(0,0,0,0.5)',
        borderpad=2
    )

st.plotly_chart(fig_gantt, use_container_width=True)

# ============================================
# PERBANDINGAN KAPASITAS SEBELUM VS SESUDAH
# ============================================
st.subheader("📈 Perbandingan Kapasitas Transmisi ke Jawa: Sebelum vs Sesudah Proyek")

years = [2026, 2027, 2028, 2029, 2030, 2031]
eksisting = [0, 0, 0, 0, 0, 0]
dengan_proyek = [0, 0, 3000, 3000, 5000, 5000]

df_plot = pd.DataFrame({
    'Tahun': years, 
    'Eksisting (Tanpa Proyek)': eksisting, 
    'Dengan Proyek': dengan_proyek
})

fig_comparison = go.Figure()

fig_comparison.add_trace(go.Bar(
    x=df_plot['Tahun'], 
    y=df_plot['Eksisting (Tanpa Proyek)'],
    name='Eksisting (Tanpa Proyek)', 
    marker_color='#FF6B6B'
))

fig_comparison.add_trace(go.Bar(
    x=df_plot['Tahun'], 
    y=df_plot['Dengan Proyek'],
    name='Dengan Proyek (Jawa-Sumatra + Jawa-Kalimantan)', 
    marker_color='#4ECDC4'
))

# Tambahkan garis batas kebutuhan pusat data AI
fig_comparison.add_hline(
    y=500, 
    line_dash="dash", 
    line_color="orange",
    annotation_text="Kebutuhan Pusat Data AI 500 MW", 
    annotation_position="bottom right"
)

fig_comparison.add_hline(
    y=1000, 
    line_dash="dash", 
    line_color="red",
    annotation_text="Kebutuhan Pusat Data AI 1 GW (Ekspansi)", 
    annotation_position="top right"
)

fig_comparison.update_layout(
    title='Proyeksi Kapasitas Transmisi ke Jawa (MW)',
    xaxis_title='Tahun',
    yaxis_title='Kapasitas (MW)',
    barmode='group',
    height=450
)

st.plotly_chart(fig_comparison, use_container_width=True)

# Insight
st.info("""
**💡 Insight dari Perbandingan Kapasitas:**
- **Tanpa proyek transmisi:** Kapasitas ke Jawa tetap **0 MW** → ketergantungan penuh pada pembangkit lokal Jawa
- **Dengan proyek (2028):** Kapasitas meningkat menjadi **3.000 MW** → sudah melebihi kebutuhan pusat data AI 500 MW
- **Dengan proyek (2030):** Kapasitas mencapai **5.000 MW** → cukup untuk ekspansi hingga 1 GW lebih
- **Kesimpulan:** Proyek transmisi **WAJIB selesai tepat waktu** agar infrastruktur tidak menjadi bottleneck
""")

# ============================================
# REKOMENDASI
# ============================================
st.header("📋 Rekomendasi untuk Stakeholder PLN")

tab1, tab2, tab3 = st.tabs(["🏢 Digital Edge (Pusat Data)", "⚡ PLN (Grid)", "🤝 Kerjasama"])

with tab1:
    st.markdown("""
    **Untuk Digital Edge:**
    1. **On-site BESS 2.000 MWh** (4 jam operasi) — US$ 150-200 juta
    2. **Genset 500 MW** (N+1 redundancy) — US$ 50-100 juta
    3. **Dual substation connection** — terhubung ke 2 gardu induk berbeda
    4. **UPS 15-30 menit** untuk bridging BESS-genset
    """)

with tab2:
    st.markdown("""
    **Untuk PLN:**
    1. **Percepat proyek transmisi Jawa-Sumatra** (target 2028)
    2. **Double circuit SUTET Bekasi-Cawang**
    3. **Skema UFLS** dengan pusat data sebagai protected load
    4. **Audit cascading failure** sistem Jawa-Bali
    """)

with tab3:
    st.markdown("""
    **Kerjasama:**
    1. **Latihan blackout simulation** rutin (setiap 6 bulan)
    2. **Komunikasi real-time** via SCADA link
    3. **SLA khusus** dengan kompensasi jika blackout >1 jam
    4. **Sharing investasi** penguatan SUTET
    """)

# ============================================
# FOOTER
# ============================================
show_footer("Transmisi & Rekomendasi - Kapasitas & Timeline Proyek")
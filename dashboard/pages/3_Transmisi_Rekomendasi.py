# dashboard/pages/3_Transmisi_Rekomendasi.py
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from pathlib import Path
import json
import sys

project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from src.config import PROCESSED_DATA_DIR
from footer import show_footer

st.set_page_config(page_title="Transmisi & Rekomendasi", layout="wide")
st.title("🔌 Analisis Transmisi & Rekomendasi")

# Load data transmisi
trans_path = PROCESSED_DATA_DIR / 'gtd_indonesia_existing.csv'
conclusions_path = PROCESSED_DATA_DIR / 'analysis_conclusions.json'

# ============================================
# 1. KAPASITAS TRANSMISI KE JAWA (EKSISTING)
# ============================================
st.header("📡 Kapasitas Transmisi ke Jawa (Eksisting)")

if trans_path.exists():
    df_trans = pd.read_csv(trans_path)
    
    # Filter untuk jalur yang mengarah ke Jawa
    to_java = df_trans[df_trans['to_region'].astype(str).str.contains('JW', na=False)]
    
    if len(to_java) > 0:
        st.dataframe(to_java, use_container_width=True)
    else:
        st.warning("⚠️ **Tidak ditemukan jalur transmisi eksisting yang mengarah ke Jawa**")
        
        st.info("""
        **Implikasi:**
        - Seluruh beban listrik di Jawa (termasuk pusat data AI di Bekasi) harus dipenuhi oleh pembangkit di Jawa sendiri
        - Tidak ada 'backup' dari luar pulau jika terjadi gangguan besar
        """)
else:
    st.warning("Data transmisi belum tersedia")

# ============================================
# 2. RENCANA TRANSMISI MENDATANG
# ============================================
st.header("📋 Rencana Transmisi Mendatang")

# Data rencana proyek
df_planned_manual = pd.DataFrame([
    {'from_region': 'IDNSM', 'to_region': 'IDNJW', 'max_flow': 3000, 
     'status': 'Rencana (Jawa-Sumatra)', 'target_tahun': 2028},
    {'from_region': 'IDNKA', 'to_region': 'IDNJW', 'max_flow': 2000, 
     'status': 'Rencana (Jawa-Kalimantan)', 'target_tahun': 2030},
])

st.dataframe(df_planned_manual, use_container_width=True)

# ============================================
# 3. TIMELINE GANTT CHART (FITUR BARU 1)
# ============================================
st.subheader("📅 Timeline Proyek Transmisi (Gantt Chart)")

# Data untuk Gantt Chart
df_timeline = pd.DataFrame([
    {'Proyek': 'Jawa-Sumatra', 'Mulai': 2025, 'Selesai': 2028, 'Kapasitas_MW': 3000, 'Status': 'Rencana'},
    {'Proyek': 'Jawa-Kalimantan', 'Mulai': 2027, 'Selesai': 2030, 'Kapasitas_MW': 2000, 'Status': 'Rencana'},
])

# Buat Gantt Chart dengan Plotly
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

# Tambahkan anotasi kapasitas pada bar
for i, row in df_timeline.iterrows():
    fig_gantt.add_annotation(
        x=(row['Mulai'] + row['Selesai']) / 2,
        y=row['Proyek'],
        text=f"{row['Kapasitas_MW']} MW",
        showarrow=False,
        font=dict(size=10, color='white')
    )

st.plotly_chart(fig_gantt, use_container_width=True)

# ============================================
# 4. PERBANDINGAN KAPASITAS SEBELUM VS SESUDAH PROYEK (FITUR BARU 2 - DIPERBAIKI)
# ============================================
st.subheader("📈 Perbandingan Kapasitas Transmisi ke Jawa: Sebelum vs Sesudah Proyek")

# Data proyeksi kapasitas - SEMUA ARRAY SAMA PANJANG
years = [2026, 2027, 2028, 2029, 2030, 2031]
eksisting = [0, 0, 0, 0, 0, 0]
dengan_proyek = [0, 0, 3000, 3000, 5000, 5000]

df_plot = pd.DataFrame({
    'Tahun': years,
    'Eksisting (Tanpa Proyek)': eksisting,
    'Dengan Proyek': dengan_proyek
})

fig_comparison = go.Figure()

# Bar untuk eksisting
fig_comparison.add_trace(go.Bar(
    x=df_plot['Tahun'],
    y=df_plot['Eksisting (Tanpa Proyek)'],
    name='Eksisting (Tanpa Proyek)',
    marker_color='#FF6B6B',
    hovertemplate='Tahun: %{x}<br>Kapasitas: %{y} MW<extra></extra>'
))

# Bar untuk dengan proyek
fig_comparison.add_trace(go.Bar(
    x=df_plot['Tahun'],
    y=df_plot['Dengan Proyek'],
    name='Dengan Proyek (Jawa-Sumatra + Jawa-Kalimantan)',
    marker_color='#4ECDC4',
    hovertemplate='Tahun: %{x}<br>Kapasitas: %{y} MW<extra></extra>'
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
    height=450,
    hovermode='x unified'
)

st.plotly_chart(fig_comparison, use_container_width=True)

# Insight dari perbandingan
st.info("""
**💡 Insight dari Perbandingan Kapasitas:**

- **Tanpa proyek transmisi:** Kapasitas ke Jawa tetap **0 MW** → ketergantungan penuh pada pembangkit lokal Jawa
- **Dengan proyek (2028):** Kapasitas meningkat menjadi **3.000 MW** → sudah melebihi kebutuhan pusat data AI 500 MW
- **Dengan proyek (2030):** Kapasitas mencapai **5.000 MW** → cukup untuk ekspansi hingga 1 GW lebih
- **Kesimpulan:** Proyek transmisi **WAJIB selesai tepat waktu** agar infrastruktur tidak menjadi bottleneck
""")

# ============================================
# 5. VISUALISASI JALUR TRANSMISI (SANKELY DIAGRAM)
# ============================================
st.subheader("🗺️ Visualisasi Jalur Transmisi Indonesia")

if trans_path.exists():
    df_trans = pd.read_csv(trans_path)
    
    # Pastikan max_flow numeric
    if 'max_flow' in df_trans.columns:
        df_trans['max_flow'] = pd.to_numeric(df_trans['max_flow'], errors='coerce').fillna(0)
    
    # Tampilkan data mentah
    with st.expander("📋 Lihat Data Transmisi Mentah (GTD)"):
        st.dataframe(df_trans, use_container_width=True)
    
    # Filter pathway dengan kapasitas > 0
    df_active = df_trans[df_trans['max_flow'] > 0].copy()
    
    # GABUNGKAN dengan data rencana manual untuk visualisasi yang lebih lengkap
    df_planned_for_viz = df_planned_manual.copy()
    df_planned_for_viz['max_flow'] = df_planned_for_viz['max_flow']
    df_planned_for_viz['voltage'] = 500  # asumsi tegangan tinggi
    df_planned_for_viz['distance'] = 'Rencana'
    
    # Gabungkan data existing dan rencana
    df_all_active = pd.concat([df_active, df_planned_for_viz], ignore_index=True)
    
    if len(df_all_active) > 0:
        st.success(f"✅ Menampilkan {len(df_all_active)} jalur transmisi (Eksisting + Rencana)")
        
        # Buat Sankey diagram
        all_nodes = list(set(df_all_active['from_region'].tolist() + df_all_active['to_region'].tolist()))
        node_to_idx = {node: i for i, node in enumerate(all_nodes)}
        
        # Warna node: hijau untuk Jawa, biru untuk lainnya
        node_colors = []
        for node in all_nodes:
            if 'JW' in str(node):
                node_colors.append('#2ECC71')  # hijau untuk Jawa (tujuan)
            elif 'SM' in str(node):
                node_colors.append('#E74C3C')  # merah untuk Sumatra
            elif 'KA' in str(node):
                node_colors.append('#F39C12')  # orange untuk Kalimantan
            else:
                node_colors.append('#3498DB')  # biru untuk lainnya
        
        fig_sankey = go.Figure(data=[go.Sankey(
            node=dict(
                pad=15,
                thickness=20,
                label=all_nodes,
                color=node_colors,
                hovertemplate='%{label}<extra></extra>'
            ),
            link=dict(
                source=[node_to_idx[row['from_region']] for _, row in df_all_active.iterrows()],
                target=[node_to_idx[row['to_region']] for _, row in df_all_active.iterrows()],
                value=[row['max_flow'] for _, row in df_all_active.iterrows()],
                hovertemplate='%{source.label} → %{target.label}<br>Kapasitas: %{value:.0f} MW<extra></extra>'
            )
        )])
        
        fig_sankey.update_layout(
            title='Diagram Alir Transmisi Antar Region (Eksisting + Rencana)',
            height=500,
            font=dict(size=12)
        )
        
        st.plotly_chart(fig_sankey, use_container_width=True)
        
        # Tabel detail jalur aktif
        st.subheader("🔌 Detail Jalur Transmisi (Eksisting + Rencana)")
        
        # Siapkan kolom untuk ditampilkan
        display_cols = ['from_region', 'to_region', 'max_flow']
        if 'voltage' in df_all_active.columns:
            display_cols.append('voltage')
        if 'distance' in df_all_active.columns:
            display_cols.append('distance')
        if 'status' in df_all_active.columns:
            display_cols.append('status')
        if 'target_tahun' in df_all_active.columns:
            display_cols.append('target_tahun')
        
        st.dataframe(df_all_active[display_cols], use_container_width=True)
        
    else:
        st.warning("⚠️ **Belum ada jalur transmisi yang tercatat**")
        
        st.info("""
        ### 📌 Penjelasan:
        
        Berdasarkan data GTD (Global Transmission Database), saat ini:
        - **Tidak ada jalur transmisi eksisting** yang mengirim listrik dari luar Jawa ke Jawa
        - Semua kapasitas yang tercatat adalah **0 MW** (masih dalam tahap perencanaan)
        
        ### 🎯 Implikasi untuk Pusat Data AI di Bekasi:
        
        1. Seluruh kebutuhan listrik pusat data (500 MW - 1 GW) harus dipenuhi oleh **pembangkit di Pulau Jawa sendiri**
        2. Tidak ada **backup interkoneksi** dari Sumatra, Kalimantan, atau Sulawesi jika terjadi gangguan
        3. Proyek transmisi Jawa-Sumatra (3.000 MW) perlu **dipercepat realisasinya**
        """)
        
        # Tampilkan semua pathway untuk transparansi
        st.subheader("📋 Semua Jalur Transmisi yang Tercatat (Termasuk Rencana)")
        st.dataframe(
            df_trans[['from_region', 'to_region', 'max_flow', 'voltage', 'distance', 'notes']].head(20),
            use_container_width=True
        )
else:
    st.warning("Data transmisi belum tersedia. Pastikan file gtd_indonesia_existing.csv ada di folder data/processed/")

# ============================================
# 6. REKOMENDASI UNTUK STAKEHOLDER PLN
# ============================================
st.header("📋 Rekomendasi untuk Stakeholder PLN")

if conclusions_path.exists():
    with open(conclusions_path, 'r') as f:
        conclusions = json.load(f)
    
    # Status kesiapan
    status = conclusions.get('status_kesiapan', 'Unknown')
    if status == 'AMAN':
        st.success(f"✅ Status Kesiapan: **{status}**")
    else:
        st.error(f"⚠️ Status Kesiapan: **{status}**")
    
    # Rekomendasi
    st.subheader("🎯 Rekomendasi Prioritas")
    
    recommendations = conclusions.get('rekomendasi', [])
    for i, rec in enumerate(recommendations, 1):
        st.markdown(f"{i}. {rec}")
    
    # Export button
    st.download_button(
        label="📥 Download Rekomendasi (JSON)",
        data=json.dumps(conclusions, indent=2),
        file_name="rekomendasi_pln.json",
        mime="application/json"
    )
else:
    st.warning("File analysis_conclusions.json tidak ditemukan")
    
    # Rekomendasi default
    st.markdown("""
    ### Berdasarkan analisis yang telah dilakukan, berikut rekomendasi untuk PLN:
    
    1. **PERCEPAT PROYEK TRANSMISI JAWA-SUMATRA**
       - Proyek 3.000 MW masih dalam rencana tanpa tahun operasi pasti
       - Targetkan selesai 2028 untuk mengantisipasi lonjakan beban
    
    2. **DEDICATED RENEWABLE ENERGY UNTUK PUSAT DATA**
       - Pusat data AI membutuhkan uptime 99.999%
       - Skema co-location solar farm + BESS di sekitar Bekasi
    
    3. **AUDIT KAPASITAS PEMBANGKIT JAWA**
       - Data GTD menunjukkan kapasitas transmisi ke Jawa sangat terbatas
       - Perlu verifikasi dengan data internal PLN untuk akurasi
    
    4. **SKENARIO DARURAT (CONTINGENCY PLAN)**
       - Jika terjadi blackout seperti Sumatra 2026, pusat data 500 MW akan loss
       - Dibutuhkan backup generator minimal 100% di lokasi
    """)

# ============================================
# 7. FOOTER COPYRIGHT
# ============================================
st.markdown("---")
st.caption("Rekomendasi ini disusun berdasarkan analisis data Global Power Plant Database, GTD, dan RUPTL PLN.")

# Footer dengan fungsi show_footer
show_footer("Transmisi & Rekomendasi - Kapasitas & Timeline Proyek")
# dashboard/pages/4_Risiko_Blackout.py
"""
Halaman: Risiko Blackout & Contingency Plan
Menampilkan hasil analisis cascading failure untuk pusat data AI di Bekasi
"""

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
from footer import show_footer

st.set_page_config(page_title="Risiko Blackout", layout="wide")
st.title("⚠️ Risiko Blackout & Contingency Plan")
st.markdown("### Belajar dari Blackout Sumatra 2026 untuk Pusat Data AI di Bekasi")

# ============================================
# LOAD HASIL ANALISIS
# ============================================

analysis_path = PROCESSED_DATA_DIR / 'cascading_failure_analysis.json'

if analysis_path.exists():
    with open(analysis_path, 'r') as f:
        results = json.load(f)
    
    sumatra = results['sumatra_baseline']
    stages = results['cascading_stages']
    recovery = results['recovery_scenarios']
    critical_locs = pd.DataFrame(results['critical_locations'])
    
    # ============================================
    # 1. BASELINE SUMATRA
    # ============================================
    st.header("📊 Baseline: Blackout Sumatra 2026")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Pelanggan Terdampak", f"{sumatra['total_pelanggan_terdampak']:,}", "13,1 juta")
    with col2:
        st.metric("Pasokan Hilang", f"{sumatra['total_pasokan_mw']:,} MW")
    with col3:
        st.metric("Gardu Induk", f"{sumatra['gardu_induk_terdampak']}", f"{sumatra['gardu_induk_pulih']} pulih")
    with col4:
        st.metric("Pemulihan PLTU", f"{sumatra['waktu_pemulihan_pltu']} jam", "Cold start")
    
    st.info(f"**Penyebab Utama:** {sumatra['penyebab_utama']}")
    
    # ============================================
    # 2. SIMULASI CASCADING FAILURE
    # ============================================
    st.header("⚡ Simulasi Cascading Failure di Bekasi")
    
    df_stages = pd.DataFrame(stages)
    
    # Grafik timeline
    fig = go.Figure()
    colors = ['#2ECC71', '#F39C12', '#E67E22', '#E74C3C', '#C0392B']
    
    for i, stage in enumerate(stages):
        fig.add_trace(go.Bar(
            x=[stage['tahap']],
            y=[stage['beban_hilang_mw']],
            name=f"Tahap {stage['tahap']}",
            text=f"{stage['beban_hilang_mw']:,.0f} MW",
            textposition='auto',
            marker_color=colors[i % len(colors)],
            hovertemplate=f"<b>Tahap {stage['tahap']}</b><br>Waktu: {stage['waktu_menit']} menit<br>Beban Hilang: {stage['beban_hilang_mw']:,.0f} MW<br>{stage['kejadian']}<extra></extra>"
        ))
    
    fig.update_layout(title='Timeline Cascading Failure', xaxis_title='Tahap', yaxis_title='Beban Hilang (MW)', height=450)
    st.plotly_chart(fig, use_container_width=True)
    
    with st.expander("📋 Detail Tahapan"):
        st.dataframe(df_stages[['tahap', 'waktu_menit', 'kejadian', 'beban_hilang_mw', 'status']], use_container_width=True)
    
    # ============================================
    # 3. PETA KERENTANAN (FITUR BARU)
    # ============================================
    st.subheader("🗺️ Peta Kerentanan Grid Jawa")
    
    # Warna berdasarkan risiko
    risk_colors = {'Kritis': '#E74C3C', 'Sangat Tinggi': '#E67E22', 'Tinggi': '#F39C12', 'Sedang': '#F1C40F'}
    
    fig_map = px.scatter_mapbox(
        critical_locs,
        lat='lat', lon='lon',
        color='risiko',
        size='beban_mw',
        hover_name='nama',
        hover_data={'jenis': True, 'keterangan': True, 'beban_mw': ':,.0f MW'},
        color_discrete_map=risk_colors,
        zoom=8,
        center=dict(lat=-6.250, lon=107.000),
        title='Titik-Titik Kritis di Sekitar Bekasi'
    )
    fig_map.update_layout(mapbox_style="open-street-map", height=500, margin=dict(l=0, r=0, t=40, b=0))
    st.plotly_chart(fig_map, use_container_width=True)
    
    with st.expander("📋 Daftar Titik Kritis"):
        st.dataframe(critical_locs[['nama', 'jenis', 'risiko', 'beban_mw', 'keterangan']], use_container_width=True, hide_index=True)
    
    st.info("""
    **Interpretasi Warna:**
    - 🔴 **Merah (Kritis):** Gardu Induk Bekasi & SUTET — titik paling rentan
    - 🟠 **Orange (Sangat Tinggi):** Pusat Data Digital Edge — beban 500 MW
    - 🟡 **Kuning (Tinggi):** PLTU Suralaya & Gardu Gandul — pemasok utama
    """)
    
    # ============================================
    # 4. WAKTU PEMULIHAN
    # ============================================
    st.header("⏱️ Estimasi Waktu Pemulihan")
    
    rec_data = []
    for s, d in recovery.items():
        rec_data.append({'Skenario': s.replace('_', ' ').title(), 'Jam': d['waktu_pemulihan_jam'], 'Beban Kembali': f"{d['beban_kembali_persen']}%"})
    
    df_rec = pd.DataFrame(rec_data)
    
    col1, col2 = st.columns(2)
    with col1:
        fig_rec = px.bar(df_rec, x='Skenario', y='Jam', color='Jam', title='Waktu Pemulihan', text='Jam')
        fig_rec.update_traces(textposition='auto')
        st.plotly_chart(fig_rec, use_container_width=True)
    
    with col2:
        st.dataframe(df_rec, use_container_width=True, hide_index=True)
    
    # ============================================
    # 5. KERUGIAN FINANSIAL
    # ============================================
    st.header("💰 Estimasi Kerugian Finansial (500 MW)")
    
    loss_per_hour = 5000  # US$
    kurs = 16000
    
    financial = []
    for s, d in recovery.items():
        dur = d['waktu_pemulihan_jam']
        loss_usd = 500 * dur * loss_per_hour
        financial.append({'Skenario': s.replace('_', ' ').title(), 'Durasi': f"{dur} jam", 'Kerugian USD': f"US$ {loss_usd:,.0f}", 'Kerugian IDR': f"Rp {loss_usd * kurs:,.0f}"})
    
    st.dataframe(pd.DataFrame(financial), use_container_width=True, hide_index=True)
    
    worst = max([d['waktu_pemulihan_jam'] for d in recovery.values()])
    worst_loss = 500 * worst * loss_per_hour
    st.error(f"⚠️ **Skenario Terburuk (Cold Start):** Kerugian US$ {worst_loss:,.0f} (Rp {worst_loss * kurs:,.0f})")
    
    # ============================================
    # 6. PENILAIAN RISIKO
    # ============================================
    st.header("⚠️ Penilaian Risiko")
    
    risks = [
        {'Risiko': 'Gangguan SUTET', 'Probabilitas': 'Rendah', 'Dampak': 'Sangat Tinggi', 'Tingkat': 'Kritis'},
        {'Risiko': 'Trip PLTU karena under-frequency', 'Probabilitas': 'Sedang', 'Dampak': 'Tinggi', 'Tingkat': 'Tinggi'},
        {'Risiko': 'Cascading failure ke wilayah sekitar', 'Probabilitas': 'Rendah', 'Dampak': 'Sangat Tinggi', 'Tingkat': 'Tinggi'},
    ]
    
    for r in risks:
        color = '#E74C3C' if r['Tingkat'] == 'Kritis' else '#F39C12'
        st.markdown(f"""
        <div style="padding: 10px; margin: 5px 0; border-left: 4px solid {color}; background-color: #f8f9fa;">
            <b>{'🔴' if r['Tingkat'] == 'Kritis' else '🟠'} {r['Risiko']}</b><br>
            <small>Probabilitas: {r['Probabilitas']} | Dampak: {r['Dampak']} | Tingkat: <b>{r['Tingkat']}</b></small>
        </div>
        """, unsafe_allow_html=True)
    
    # ============================================
    # 7. REKOMENDASI
    # ============================================
    st.header("📋 Rekomendasi Mitigasi")
    
    tab1, tab2, tab3 = st.tabs(["🏢 Digital Edge", "⚡ PLN", "🤝 Kerjasama"])
    
    with tab1:
        st.markdown("""
        **Untuk Digital Edge:**
        1. **BESS 2.000 MWh** (4 jam operasi) — US$ 150-200 juta
        2. **Genset 500 MW** (N+1 redundancy) — US$ 50-100 juta
        3. **Redundansi koneksi** ke 2 gardu induk berbeda
        4. **UPS 15-30 menit** untuk bridging
        """)
    
    with tab2:
        st.markdown("""
        **Untuk PLN:**
        1. **Penguatan proteksi** di Gardu Induk Bekasi
        2. **Double circuit** SUTET Bekasi-Cawang
        3. **Skema UFLS** dengan pusat data sebagai protected load
        4. **Audit cascading failure** sistem Jawa-Bali
        """)
    
    with tab3:
        st.markdown("""
        **Kerjasama:**
        1. **Latihan blackout simulation** rutin
        2. **Komunikasi real-time** via SCADA link
        3. **SLA khusus** dengan kompensasi blackout
        4. **Sharing investasi** penguatan SUTET
        """)
    
    # ============================================
    # 8. KESIMPULAN
    # ============================================
    st.header("🎯 Kesimpulan")
    
    st.markdown("""
    <div style="background-color: #1a1a2e; padding: 20px; border-radius: 10px;">
        <p style="color: white;"><b>Berdasarkan analisis cascading failure:</b></p>
        <ul style="color: #cccccc;">
        <li>Gangguan di Gardu Induk Bekasi berpotensi menyebabkan pemadaman berantai</li>
        <li>Waktu pemulihan bisa mencapai <b>18 jam</b> (skenario cold start)</li>
        <li>Kerugian finansial: <b>US$ 45 juta</b> (Rp 720 miliar) untuk blackout 18 jam</li>
        <li>Investasi mitigasi US$ 200-300 juta jauh lebih kecil dari potensi kerugian</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    # ============================================
    # FOOTER
    # ============================================
    show_footer("Risiko Blackout & Contingency Plan - Belajar dari Blackout Sumatra 2026")

else:
    st.warning("⚠️ File hasil analisis belum tersedia. Jalankan: python scripts/06_cascading_failure_analysis.py")
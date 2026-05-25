# dashboard/pages/1_Peta_Pembangkit.py
import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path
import sys

project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from src.config import PROCESSED_DATA_DIR

st.set_page_config(page_title="Peta Pembangkit", layout="wide")
st.title("🗺️ Peta Pembangkit Listrik Indonesia")

# Load data
plants_path = PROCESSED_DATA_DIR / 'indonesia_power_plants_clean.csv'

if plants_path.exists():
    df = pd.read_csv(plants_path)
    
    # Sidebar filters
    st.sidebar.header("🔍 Filter")
    
    # Filter tipe pembangkit
    fuel_types = ['Semua'] + sorted(df['primary_fuel'].unique().tolist())
    selected_fuel = st.sidebar.selectbox("Tipe Pembangkit", fuel_types)
    
    # Filter kapasitas minimum
    min_capacity = st.sidebar.slider(
        "Kapasitas Minimum (MW)",
        min_value=0,
        max_value=int(df['capacity_mw'].max()),
        value=0
    )
    
    # Apply filters
    df_filtered = df.copy()
    if selected_fuel != 'Semua':
        df_filtered = df_filtered[df_filtered['primary_fuel'] == selected_fuel]
    df_filtered = df_filtered[df_filtered['capacity_mw'] >= min_capacity]
    
    # Informasi jumlah data
    st.info(f"Menampilkan {len(df_filtered):,} dari {len(df):,} pembangkit")
    
    # Statistik ringkas
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Kapasitas", f"{df_filtered['capacity_mw'].sum():,.0f} MW")
    with col2:
        st.metric("Kapasitas Rata-rata", f"{df_filtered['capacity_mw'].mean():,.0f} MW")
    with col3:
        st.metric("Kapasitas Terbesar", f"{df_filtered['capacity_mw'].max():,.0f} MW")
    
    # Peta interaktif dengan Plotly
    st.subheader("📍 Sebaran Lokasi Pembangkit")
    
    # Siapkan data untuk peta
    df_map = df_filtered.dropna(subset=['latitude', 'longitude'])
    
    if len(df_map) > 0:
        fig = px.scatter_mapbox(
            df_map,
            lat='latitude',
            lon='longitude',
            size='capacity_mw',
            color='primary_fuel',
            hover_name='name',
            hover_data={
                'capacity_mw': ':,.0f MW',
                'primary_fuel': True,
                'commissioning_year': True
            },
            size_max=30,
            zoom=3.5,
            center=dict(lat=-2.5, lon=118),
            title="Peta Pembangkit Listrik Indonesia"
        )
        
        fig.update_layout(
            mapbox_style="open-street-map",
            height=600,
            margin=dict(l=0, r=0, t=40, b=0)
        )
        
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Tidak ada data koordinat untuk ditampilkan")
    
    # Tabel data
    with st.expander("📋 Lihat Tabel Data Pembangkit"):
        st.dataframe(
            df_filtered[['name', 'primary_fuel', 'capacity_mw', 'country_long', 'commissioning_year']].head(100),
            use_container_width=True
        )
    
else:
    st.error("Data pembangkit tidak ditemukan. Jalankan script 01_load_filter_plants.py terlebih dahulu.")

# Di setiap file halaman
from footer import show_footer

# Di bagian akhir halaman
show_footer("Peta Pembangkit Listrik Indonesia")  # untuk halaman 1
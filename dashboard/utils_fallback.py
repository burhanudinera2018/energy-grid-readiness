# dashboard/utils_fallback.py - VERSI SEDERHANA
import streamlit as st
import pandas as pd
import json
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent.parent))
from src.config import PROCESSED_DATA_DIR


@st.cache_data
def load_plants_data():
    """Load data pembangkit"""
    file_path = PROCESSED_DATA_DIR / 'indonesia_power_plants_clean.csv'
    if file_path.exists():
        df = pd.read_csv(file_path)
        st.success(f"✅ Data pembangkit: {len(df)} unit")
        return df
    else:
        st.error("❌ Data pembangkit tidak ditemukan!")
        return pd.DataFrame()


@st.cache_data
def load_gap_data():
    """Load data gap analysis"""
    file_path = PROCESSED_DATA_DIR / 'final_gap_analysis.csv'
    if file_path.exists():
        df = pd.read_csv(file_path)
        st.success("✅ Data gap analysis loaded")
        return df
    else:
        st.error("❌ Data gap analysis tidak ditemukan!")
        return pd.DataFrame()


@st.cache_data
def load_ebt_data():
    """Load data EBT"""
    file_path = PROCESSED_DATA_DIR / 'ebt_spatial_analysis.csv'
    if file_path.exists():
        df = pd.read_csv(file_path)
        st.success(f"✅ Data EBT: {len(df)} provinsi")
        return df
    else:
        st.error("❌ Data EBT tidak ditemukan!")
        return pd.DataFrame()


@st.cache_data
def load_coal_data():
    """Load data PLTU"""
    file_path = PROCESSED_DATA_DIR / 'coal_plants_analysis.csv'
    if file_path.exists():
        df = pd.read_csv(file_path)
        st.success(f"✅ Data PLTU: {len(df)} unit")
        return df
    else:
        st.error("❌ Data PLTU tidak ditemukan!")
        return pd.DataFrame()


@st.cache_data
def load_cascading_data():
    """Load data cascading failure"""
    file_path = PROCESSED_DATA_DIR / 'cascading_failure_analysis.json'
    if file_path.exists():
        with open(file_path, 'r') as f:
            data = json.load(f)
        st.success("✅ Data cascading failure loaded")
        return data
    else:
        st.error("❌ Data cascading failure tidak ditemukan!")
        return {}


def check_data_status():
    """Cek status data di sidebar"""
    st.sidebar.markdown("### 📊 Status Data")
    
    files = {
        'Data Pembangkit': PROCESSED_DATA_DIR / 'indonesia_power_plants_clean.csv',
        'Data Gap Analysis': PROCESSED_DATA_DIR / 'final_gap_analysis.csv',
        'Data EBT': PROCESSED_DATA_DIR / 'ebt_spatial_analysis.csv',
        'Data PLTU': PROCESSED_DATA_DIR / 'coal_plants_analysis.csv',
    }
    
    for label, path in files.items():
        if path.exists():
            st.sidebar.success(f"✅ {label}")
        else:
            st.sidebar.error(f"❌ {label}")

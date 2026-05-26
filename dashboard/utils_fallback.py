# dashboard/utils_fallback.py
"""
Utility functions for loading data with fallback
"""

import streamlit as st
import pandas as pd
import json
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent.parent))
from src.config import PROCESSED_DATA_DIR, get_fallback_plants_data, get_fallback_gap_data, get_fallback_ebt_data, get_fallback_coal_data, get_fallback_cascading_data, get_fallback_cba_data, is_cloud_deployment


@st.cache_data
def load_plants_data():
    """Load data pembangkit dengan fallback"""
    file_path = PROCESSED_DATA_DIR / 'indonesia_power_plants_clean.csv'
    
    if file_path.exists():
        df = pd.read_csv(file_path)
        st.info(f"✅ Menggunakan data asli ({len(df)} pembangkit)")
        return df
    else:
        df = get_fallback_plants_data()
        st.warning(f"⚠️ Fallback: Data asli tidak ditemukan. Menggunakan {len(df)} data dummy untuk demo.")
        return df


@st.cache_data
def load_gap_data():
    """Load data gap analysis dengan fallback"""
    file_path = PROCESSED_DATA_DIR / 'final_gap_analysis.csv'
    
    if file_path.exists():
        df = pd.read_csv(file_path)
        st.info("✅ Menggunakan data gap analysis asli")
        return df
    else:
        df = get_fallback_gap_data()
        st.warning("⚠️ Fallback: Data gap analysis tidak ditemukan. Menggunakan data dummy untuk demo.")
        return df


@st.cache_data
def load_ebt_data():
    """Load data EBT dengan fallback"""
    file_path = PROCESSED_DATA_DIR / 'ebt_spatial_analysis.csv'
    
    if file_path.exists():
        df = pd.read_csv(file_path)
        st.info("✅ Menggunakan data EBT asli")
        return df
    else:
        df = get_fallback_ebt_data()
        st.warning("⚠️ Fallback: Data EBT tidak ditemukan. Menggunakan data dummy untuk demo.")
        return df


@st.cache_data
def load_coal_data():
    """Load data PLTU dengan fallback"""
    file_path = PROCESSED_DATA_DIR / 'coal_plants_analysis.csv'
    
    if file_path.exists():
        df = pd.read_csv(file_path)
        st.info(f"✅ Menggunakan data PLTU asli ({len(df)} unit)")
        return df
    else:
        df = get_fallback_coal_data()
        st.warning(f"⚠️ Fallback: Data PLTU tidak ditemukan. Menggunakan {len(df)} data dummy untuk demo.")
        return df


@st.cache_data
def load_cascading_data():
    """Load data cascading failure dengan fallback"""
    file_path = PROCESSED_DATA_DIR / 'cascading_failure_analysis.json'
    
    if file_path.exists():
        with open(file_path, 'r') as f:
            data = json.load(f)
        st.info("✅ Menggunakan data cascading failure asli")
        return data
    else:
        data = get_fallback_cascading_data()
        st.warning("⚠️ Fallback: Data cascading failure tidak ditemukan. Menggunakan data dummy untuk demo.")
        return data


@st.cache_data
def load_cba_data():
    """Load data CBA dengan fallback"""
    file_path = PROCESSED_DATA_DIR / 'cba_macro_calibration.json'
    
    if file_path.exists():
        with open(file_path, 'r') as f:
            data = json.load(f)
        st.info("✅ Menggunakan data CBA asli")
        return data
    else:
        data = get_fallback_cba_data()
        st.warning("⚠️ Fallback: Data CBA tidak ditemukan. Menggunakan data dummy untuk demo.")
        return data


def check_data_status():
    """Tampilkan status ketersediaan data"""
    files_to_check = [
        ('indonesia_power_plants_clean.csv', 'Data Pembangkit'),
        ('final_gap_analysis.csv', 'Data Gap Analysis'),
        ('ebt_spatial_analysis.csv', 'Data EBT'),
        ('coal_plants_analysis.csv', 'Data PLTU'),
        ('cascading_failure_analysis.json', 'Data Cascading Failure'),
        ('cba_macro_calibration.json', 'Data CBA'),
    ]
    
    st.sidebar.markdown("### 📊 Status Data")
    
    all_available = True
    for filename, label in files_to_check:
        file_path = PROCESSED_DATA_DIR / filename
        if file_path.exists():
            st.sidebar.success(f"✅ {label}")
        else:
            st.sidebar.warning(f"⚠️ {label} (Fallback)")
            all_available = False
    
    if not all_available:
        st.sidebar.info("💡 **Info:** Beberapa data menggunakan fallback. Untuk hasil lengkap, jalankan script analisis terlebih dahulu.")
    
    return all_available
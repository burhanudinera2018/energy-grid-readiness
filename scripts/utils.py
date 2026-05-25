# scripts/utils.py
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
import sys

# Tambahkan src ke path agar bisa import config
sys.path.append(str(Path(__file__).parent.parent / 'src'))
from config import FIGURES_DIR, PROCESSED_DATA_DIR

def load_indonesia_plants(raw_data_dir):
    """Load dan filter power plant database untuk Indonesia"""
    csv_path = raw_data_dir / 'global_power_plant_database.csv'
    
    if not csv_path.exists():
        raise FileNotFoundError(f"File tidak ditemukan: {csv_path}")
    
    df = pd.read_csv(csv_path)
    
    # Deteksi kode Indonesia
    if 'IDN' in df['country'].values:
        df_id = df[df['country'] == 'IDN'].copy()
    elif 'INA' in df['country'].values:
        df_id = df[df['country'] == 'INA'].copy()
    else:
        indo_candidates = [c for c in df['country'].unique() if 'IND' in str(c).upper()]
        if indo_candidates:
            df_id = df[df['country'] == indo_candidates[0]].copy()
        else:
            raise ValueError("Data Indonesia tidak ditemukan")
    
    # Konversi kapasitas
    df_id['capacity_mw'] = pd.to_numeric(df_id['capacity_mw'], errors='coerce')
    df_id = df_id.dropna(subset=['capacity_mw'])
    
    return df_id

def plot_plant_composition(df, save=True):
    """Buat visualisasi komposisi pembangkit"""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    
    # Jumlah per tipe
    tipe_counts = df['primary_fuel'].value_counts().head(10)
    ax1.barh(tipe_counts.index, tipe_counts.values, color='#2E86AB')
    ax1.set_xlabel('Jumlah Pembangkit')
    ax1.set_title('Top 10 Tipe Pembangkit di Indonesia', fontsize=12)
    
    # Kapasitas per tipe
    kapasitas_per_tipe = df.groupby('primary_fuel')['capacity_mw'].sum().sort_values(ascending=False).head(10)
    ax2.barh(kapasitas_per_tipe.index, kapasitas_per_tipe.values / 1000, color='#A23B72')
    ax2.set_xlabel('Kapasitas Total (GW)')
    ax2.set_title('Top 10 Tipe Pembangkit berdasarkan Kapasitas', fontsize=12)
    
    plt.tight_layout()
    
    if save:
        save_path = FIGURES_DIR / 'indonesia_power_plant_composition.png'
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"✅ Grafik tersimpan di: {save_path}")
    
    plt.show()
    return fig

def save_cleaned_data(df, filename='indonesia_power_plants_clean.csv'):
    """Simpan data yang sudah dibersihkan"""
    save_path = PROCESSED_DATA_DIR / filename
    df.to_csv(save_path, index=False)
    print(f"✅ Data tersimpan di: {save_path}")
    return save_path

# ============================================
# FUNGSI UNTUK DATA TRANSMISI
# ============================================

def load_indonesia_buses(raw_data_dir):
    """Load dan filter data buses untuk Indonesia"""
    csv_path = raw_data_dir / 'buses.csv'
    
    if not csv_path.exists():
        raise FileNotFoundError(f"File tidak ditemukan: {csv_path}")
    
    df_buses = pd.read_csv(csv_path)
    print(f"📡 Total bus dalam database global: {len(df_buses):,}")
    
    # Deteksi kolom country (mungkin 'country' atau 'country_code')
    country_col = None
    for col in ['country', 'country_code', 'cnt', 'iso3']:
        if col in df_buses.columns:
            country_col = col
            break
    
    if country_col is None:
        print("⚠️ Kolom negara tidak ditemukan. Cek struktur kolom:")
        print(df_buses.columns.tolist())
        # Jika tidak ada kolom negara, kembalikan semua data
        return df_buses
    
    # Filter Indonesia
    if 'IDN' in df_buses[country_col].values:
        df_id = df_buses[df_buses[country_col] == 'IDN'].copy()
    elif 'INA' in df_buses[country_col].values:
        df_id = df_buses[df_buses[country_col] == 'INA'].copy()
    else:
        # Cari yang mengandung 'IND'
        indo_candidates = [c for c in df_buses[country_col].unique() if 'IND' in str(c).upper()]
        if indo_candidates:
            df_id = df_buses[df_buses[country_col] == indo_candidates[0]].copy()
        else:
            print("⚠️ Data Indonesia untuk buses tidak ditemukan. Kembalikan semua data.")
            return df_buses
    
    print(f"✅ Bus di Indonesia: {len(df_id):,}")
    return df_id

def load_indonesia_lines(raw_data_dir, df_buses_id):
    """Load dan filter data lines berdasarkan bus_id yang ada di Indonesia"""
    csv_path = raw_data_dir / 'lines.csv'
    
    if not csv_path.exists():
        raise FileNotFoundError(f"File tidak ditemukan: {csv_path}")
    
    df_lines = pd.read_csv(csv_path)
    print(f"🔌 Total segmen line dalam database global: {len(df_lines):,}")
    
    # Jika df_buses_id kosong atau tidak memiliki bus_id, return empty
    if len(df_buses_id) == 0:
        print("⚠️ Tidak ada bus Indonesia, skip filter lines")
        return df_lines
    
    # Cari kolom bus_id
    bus_col_i = None
    bus_col_j = None
    
    for col in ['bus_i', 'bus_from', 'from_bus', 'source']:
        if col in df_lines.columns:
            bus_col_i = col
            break
    
    for col in ['bus_j', 'bus_to', 'to_bus', 'target']:
        if col in df_lines.columns:
            bus_col_j = col
            break
    
    if bus_col_i is None or bus_col_j is None:
        print("⚠️ Kolom bus tidak ditemukan. Cek struktur kolom:")
        print(df_lines.columns.tolist())
        return df_lines
    
    # Filter lines berdasarkan bus_id
    bus_ids = df_buses_id['bus_id'].unique() if 'bus_id' in df_buses_id.columns else df_buses_id.index
    
    if len(bus_ids) == 0:
        return df_lines
    
    df_lines_id = df_lines[
        df_lines[bus_col_i].isin(bus_ids) & 
        df_lines[bus_col_j].isin(bus_ids)
    ].copy()
    
    print(f"✅ Segmen transmisi di Indonesia: {len(df_lines_id):,}")
    return df_lines_id

def get_transmission_stats(df_buses, df_lines):
    """Dapatkan statistik ringkas data transmisi"""
    stats = {
        'jumlah_bus': len(df_buses),
        'jumlah_segmen': len(df_lines),
        'rata_rata_tegangan': None
    }
    
    # Cek kolom tegangan jika ada
    if 'voltage' in df_lines.columns:
        stats['rata_rata_tegangan'] = df_lines['voltage'].mean()
    elif 'kv' in df_lines.columns:
        stats['rata_rata_tegangan'] = df_lines['kv'].mean()
    
    return stats

# Tambahkan fungsi ini ke utils.py

def analyze_transmission_capacity_detailed(df_existing, df_planned):
    """Analisis detail kapasitas transmisi Indonesia"""
    
    print("\n" + "=" * 60)
    print("📡 ANALISIS DETAIL TRANSMISI INDONESIA")
    print("=" * 60)
    
    # Pastikan kolom max_flow dibaca sebagai numerik
    if 'max_flow' in df_existing.columns:
        df_existing['max_flow'] = pd.to_numeric(df_existing['max_flow'], errors='coerce')
    else:
        print("❌ Kolom 'max_flow' tidak ditemukan!")
        return {}
    
    # Filter pathway dengan kapasitas > 0
    df_active = df_existing[df_existing['max_flow'] > 0].copy()
    
    print(f"\n✅ Pathway dengan kapasitas > 0 MW: {len(df_active)}")
    print("\n📋 Daftar Pathway Aktif:")
    for _, row in df_active.iterrows():
        print(f"   - {row['from_region']} → {row['to_region']}: {row['max_flow']:.0f} MW (via {row['from_country']}-{row['to_country']})")
    
    # Pathway ke Jawa (dari atau menuju)
    to_java = df_existing[
        (df_existing['to_region'].astype(str).str.contains('JW', na=False)) & 
        (df_existing['max_flow'] > 0)
    ]
    
    from_java = df_existing[
        (df_existing['from_region'].astype(str).str.contains('JW', na=False)) & 
        (df_existing['max_flow'] > 0)
    ]
    
    print(f"\n🎯 Kapasitas menuju Jawa (ke region IDNJW): {to_java['max_flow'].sum():.0f} MW")
    print(f"🎯 Kapasitas keluar dari Jawa (dari region IDNJW): {from_java['max_flow'].sum():.0f} MW")
    
    # Pathway rencana (planned) dengan kapasitas > 0
    if 'max_flow' in df_planned.columns:
        df_planned['max_flow'] = pd.to_numeric(df_planned['max_flow'], errors='coerce')
        df_planned_active = df_planned[df_planned['max_flow'] > 0].copy()
        
        print(f"\n📋 Rencana Pathway Mendatang (planned):")
        for _, row in df_planned_active.iterrows():
            print(f"   - {row['from_region']} → {row['to_region']}: {row['max_flow']:.0f} MW (rencana)")
    
    return {
        'kapasitas_ke_jawa': to_java['max_flow'].sum(),
        'kapasitas_dari_jawa': from_java['max_flow'].sum(),
        'pathway_aktif': df_active.to_dict('records'),
        'pathway_rencana': df_planned_active.to_dict('records') if 'df_planned_active' in dir() else []
    }
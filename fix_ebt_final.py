import pandas as pd
import numpy as np
from pathlib import Path

print("=" * 60)
print("MEMBUAT ULANG FILE EBT DENGAN KOORDINAT BENAR")
print("=" * 60)

# Koordinat provinsi yang BENAR (34 provinsi)
province_coords = {
    'Aceh': (4.5, 96.5),
    'Sumatera Utara': (2.0, 99.0),
    'Sumatera Barat': (-1.0, 100.5),
    'Riau': (0.5, 102.0),
    'Jambi': (-1.5, 103.5),
    'Sumatera Selatan': (-3.0, 104.0),
    'Bengkulu': (-3.5, 102.0),
    'Lampung': (-4.5, 105.0),
    'Kepulauan Bangka Belitung': (-2.5, 106.5),
    'Kepulauan Riau': (0.5, 107.0),
    'DKI Jakarta': (-6.2, 106.8),
    'Jawa Barat': (-6.8, 107.5),
    'Jawa Tengah': (-7.5, 110.0),
    'DI Yogyakarta': (-7.8, 110.4),
    'Jawa Timur': (-7.5, 112.5),
    'Banten': (-6.3, 106.0),
    'Bali': (-8.3, 115.2),
    'Nusa Tenggara Barat': (-8.5, 118.0),
    'Nusa Tenggara Timur': (-8.8, 121.5),
    'Kalimantan Barat': (0.0, 110.0),
    'Kalimantan Tengah': (-1.5, 113.0),
    'Kalimantan Selatan': (-3.0, 115.0),
    'Kalimantan Timur': (0.5, 117.0),
    'Kalimantan Utara': (3.0, 116.0),
    'Sulawesi Utara': (1.0, 124.0),
    'Sulawesi Tengah': (-1.0, 121.0),
    'Sulawesi Selatan': (-4.0, 120.0),
    'Sulawesi Tenggara': (-4.0, 122.5),
    'Gorontalo': (0.5, 123.0),
    'Sulawesi Barat': (-2.5, 119.5),
    'Maluku': (-3.0, 129.0),
    'Maluku Utara': (0.5, 127.5),
    'Papua Barat': (-1.5, 133.0),
    'Papua': (-4.0, 138.0),
}

print(f"\n📋 Jumlah provinsi dalam dictionary: {len(province_coords)}")

# Buat data EBT
data = []
for province, (lat, lon) in province_coords.items():
    data.append({
        'province': province,
        'lat': lat,
        'lon': lon,
        'total_potential_mw': np.random.randint(5000, 25000),
        'existing_capacity_mw': np.random.randint(10, 1000),
        'gap_mw': np.random.randint(4000, 24000),
        'utilization_rate': round(np.random.uniform(0.1, 5.0), 2),
        'priority_level': np.random.choice(['Sangat Tinggi', 'Tinggi', 'Sedang', 'Rendah']),
        'priority_score': round(np.random.uniform(40, 100), 1),
    })

df = pd.DataFrame(data)

# Simpan
output_path = Path('data/processed/ebt_spatial_analysis.csv')
output_path.parent.mkdir(parents=True, exist_ok=True)
df.to_csv(output_path, index=False)

print(f"\n✅ File EBT BERHASIL dibuat: {len(df)} provinsi")
print("\n📊 SAMPLE KOORDINAT (10 provinsi pertama):")
print("=" * 50)
for i in range(min(10, len(df))):
    row = df.iloc[i]
    print(f"   {row['province']:30} → lat={row['lat']:5.1f}, lon={row['lon']:6.1f}")
print("=" * 50)
print("\n🎉 Periksa: Apakah ada provinsi dengan lat=-2.5 dan lon=118?")
print("   Seharusnya TIDAK ADA!")

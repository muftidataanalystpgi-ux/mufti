import streamlit as st
import pandas as pd
import folium
from streamlit_folium import folium_static

# Set layout halaman agar lebar penuh
st.set_page_config(layout="wide")

st.title(Geospatial Financial Dashboard - Branch Growth Segmentation")
st.markdown("""
**Disclaimer:**Semua data yang disajikan di sini sepenuhnya bersifat sintetis dan diacak untuk menjaga kerahasiaan data serta mematuhi peraturan NDA, dengan tetap mempertahankan kedalaman arsitektur dan logisnya.
""")

# Load dataset dummy yang aman
@st.cache_data
def load_data():
    return pd.read_csv("df_dummy.csv")

df = load_data()

# Tampilkan ringkasan metrik makro
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Branches", f"{len(df):,}")
col2.metric("Avg Growth", f"{df['Persen Growth'].mean():.2f}%")
col3.metric("Max Growth", f"{df['Persen Growth'].max():.2f}%")
col4.metric("Min Growth", f"{df['Persen Growth'].min():.2f}%")

# Sidebar untuk memilih metode segmentasi statistik
st.sidebar.header("Filter & Settings")
selected_method = st.sidebar.selectbox(
    "Choose Segmentation Method for Mapping:",
    ["Kategori_IQR", "Kategori_By_StdDev", "Kategori_Percentile", "Kategori_KPI_Atasan", "Kategori_ZScore"]
)

# Inisialisasi peta dasar (pusat di Indonesia)
m = folium.Map(location=[-2.5489, 118.0149], zoom_start=5, control_scale=True)

# Palet warna otomatis berdasarkan kategori segmentasi
color_palette = {
    "Extreme High": "purple", "Normal": "blue",
    "Tinggi": "green", "Sedang": "orange", "Rendah": "red",
    "Atas": "green", "Tengah": "blue", "Bawah": "red",
    "Sangat Baik": "darkgreen", "Baik": "green", "Cukup": "orange", "Kurang": "red",
    "Extreme Superstar": "purple", "High Performer": "darkblue", "Low Performer": "orange"
}

feature_group = folium.FeatureGroup(name=selected_method)

# Plot koordinat cabang dummy ke peta
for _, row in df.dropna(subset=['latitude_cabang', 'longitude_cabang']).iterrows():
    cat_val = row[selected_method]
    color = color_palette.get(cat_val, "gray")
    
    # Isi popup interaktif saat marker diklik
    popup_text = f"""
    <b>Branch ID:</b> {row['cabang']}<br>
    <b>Tenure:</b> {row['lama_buka_bulan']} months<br>
    <b>Jan25 Omset:</b> Rp {row['Omset Jan25']:,.0f}<br>
    <b>Mei26 Omset:</b> Rp {row['Omset Mei26']:,.0f}<br>
    <b>Growth:</b> {row['Persen Growth']}%<br>
    <b>Segment:</b> {cat_val}
    """
    
    folium.CircleMarker(
        location=[row['latitude_cabang'], row['longitude_cabang']],
        radius=5,
        color=color,
        fill=True,
        fill_color=color,
        fill_opacity=0.7,
        popup=folium.Popup(popup_text, max_width=300)
    ).add_to(feature_group)

feature_group.add_to(m)
folium.LayerControl().add_to(m)

# Tampilkan Peta ke Dashboard
st.subheader(f"Geospatial Distribution Map ({selected_method})")
folium_static(m, width=1200, height=600)

# Tampilkan tabel data mentah di bagian bawah
st.subheader("Data Overview Table")
st.dataframe(df)

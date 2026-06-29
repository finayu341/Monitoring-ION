import os
import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import pydeck as pdk
from geopy.geocoders import Nominatim
import time
from streamlit_folium import st_folium
import folium


class Daerah:

    @staticmethod
    def get_top_daerah(df):
        df = df.copy()
        df.columns = df.columns.str.strip().str.upper()

        if 'DAERAH' not in df.columns or 'KENDALA' not in df.columns:
            return "-", 0

        # hitung daerah terbanyak
        rekom = (
            df.groupby('DAERAH')['KENDALA']
            .value_counts()
            .groupby(level=0)
            .head(1)
            .reset_index(name='Jumlah')
        )

        if rekom.empty:
            return "-", 0

        daerah_terbanyak = rekom.loc[rekom['Jumlah'].idxmax()]

        return daerah_terbanyak['DAERAH'], int(daerah_terbanyak['Jumlah'])


    @staticmethod
    def show(df):
        st.markdown("""
        <div style="background: linear-gradient(90deg, #4b6cb7 0%, #182848 100%);
                    padding: 20px; border-radius: 10px; margin-bottom: 25px;">
            <h2 style="color: white; margin: 0; text-align: center;">📍 Data Daerah</h2>   
        </div>
        """, unsafe_allow_html=True)

        df.columns = df.columns.str.strip().str.upper()

        rekom = (
            df.groupby('DAERAH')['KENDALA']
            .value_counts()
            .groupby(level=0)
            .head(1)
            .reset_index(name='Jumlah')
        )

        daerah_terbanyak = rekom.loc[rekom['Jumlah'].idxmax()]
        top_daerah = daerah_terbanyak['DAERAH']
        total_daerah = int(daerah_terbanyak['Jumlah'])

        st.markdown("---")
        st.write("### 🗺️ Peta Sebaran Gangguan")

        @st.cache_data
        def ambil_koordinat(daerah_list):
            geolocator = Nominatim(user_agent="geoapi_daerah")
            lokasi_data = []
            for daerah in daerah_list:
                try:
                    location = geolocator.geocode(f"{daerah}, Indonesia")
                    if location:
                        lokasi_data.append({
                            "DAERAH": daerah,
                            "latitude": location.latitude,
                            "longitude": location.longitude
                        })
                    time.sleep(1)  # jeda agar tidak diblokir oleh Nominatim
                except:
                    continue
            return pd.DataFrame(lokasi_data)
        
        # ==============================
        # 🧩 DATA PREPARATION
        # --- Ambil koordinat (cache otomatis) ---
        lokasi_file = "koordinat_PIKS.csv"
        if os.path.exists(lokasi_file):
            lokasi_df = pd.read_csv(lokasi_file)
        else:
            lokasi_df = ambil_koordinat(rekom['DAERAH'].dropna().unique())
            lokasi_df.to_csv(lokasi_file, index=False)

        # menggabngkan koordinat dengan data jumlah gangguan
        lokasi_df = lokasi_df.merge(rekom[['DAERAH', 'Jumlah']], on='DAERAH', how='left')

        # menentukan provinsi berdasarkan nama daerah (bisa kamu sesuaikan logikanya)
        lokasi_df['PROVINSI'] = lokasi_df['DAERAH'].apply(lambda x: x.split(',')[0] if ',' in x else x)
        prov_df = lokasi_df.groupby('PROVINSI', as_index=False).agg({
            'latitude': 'mean',
            'longitude': 'mean',
            'Jumlah': 'sum'
        })


        # ==============================
        # 🗺️ PEMBUATAN PETA
        # ==============================
        m = folium.Map(location=[-2.5, 118.0], zoom_start=5, tiles="CartoDB positron")

        # --- Layer Provinsi ---
        prov_layer = folium.FeatureGroup(name="WILAYAH").add_to(m)
        for _, row in prov_df.iterrows():
            folium.CircleMarker(
                location=[row["latitude"], row["longitude"]],
                radius=6 + (row["Jumlah"] / prov_df["Jumlah"].max()) * 10,
                color="blue",
                fill=True,
                fill_opacity=0.5,
                popup=f"<b>{row['PROVINSI']}</b><br>Total Gangguan: {row['Jumlah']}"
            ).add_to(prov_layer)

        # --- Layer Control ---
        folium.LayerControl(collapsed=False).add_to(m)

        # ==============================
        # 🔄 TOGGLE LAYER BERDASARKAN ZOOM
        # ==============================
        m.get_root().html.add_child(folium.Element("""
        <script>
            function toggleLayers(e) {
                const zoom = e.target.getZoom();
                const mapLayers = e.target._layers;
                let provLayer, daerahLayer;
                for (let key in mapLayers) {
                    const layer = mapLayers[key];
                    if (layer.options && layer.options.name === "Provinsi") provLayer = layer;
                    if (layer.options && layer.options.name === "Daerah") daerahLayer = layer;
                }
                if (zoom < 7) {
                    if (daerahLayer) e.target.removeLayer(daerahLayer);
                    if (provLayer) e.target.addLayer(provLayer);
                } else {
                    if (provLayer) e.target.removeLayer(provLayer);
                    if (daerahLayer) e.target.addLayer(daerahLayer);
                }
            }
            map.on('zoomend', toggleLayers);
        </script>
        """))

        # ==============================
        st_folium(m, width=900, height=550)

        return top_daerah, total_daerah
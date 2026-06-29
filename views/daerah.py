import streamlit as st
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd

class Gangguan:

    @staticmethod
    def get_top_gangguan(df):
        df.columns = df.columns.str.strip().str.upper()

        if 'KENDALA' not in df.columns:
            return "-", 0

        # Normalisasi
        df['KENDALA'] = df['KENDALA'].astype(str).str.strip().str.title()

        jenis_dipilih = [
            'Focut', 'Pengecekan Perangkat', 'Cek Keseluruhan', 'Pemasangan Baru',
            'Loss', 'Redaman Tinggi/Besar', 'Redaman Loss', 'Perapihan Kabel',
            'Geser Perangkat', 'Kabel Putus', 'MT ODP'
        ]

        df_filtered = df[df['KENDALA'].isin(jenis_dipilih)]
        if df_filtered.empty:
            return "-", 0

        gangguan_count = df_filtered['KENDALA'].value_counts()

        return gangguan_count.index[0], gangguan_count.iloc[0]


    @staticmethod
    def show(df):
            st.markdown("""
            <div style="background: linear-gradient(90deg, #4b6cb7 0%, #182848 100%);
                        padding: 20px; border-radius: 10px; margin-bottom: 25px;">
                <h2 style="color: white; margin: 0; text-align: center;">📊 Analisis Jenis Gangguan</h2>
            </div>
            """, unsafe_allow_html=True)

            df.columns = df.columns.str.strip().str.upper()

            if 'KENDALA' not in df.columns:
                st.warning("Kolom 'KENDALA' tidak ditemukan di dataset!")
                return

            # Normalisasi Kendala
            df['KENDALA'] = df['KENDALA'].astype(str).str.strip().str.title()


            # Filter Waktu
            # ==============================
            filter_option = st.radio(
                "Filter berdasarkan:",
                ("Semua", "Tanggal Tertentu"),
                horizontal=True
            )

            df_filtered = df.copy()
            pilihan = "Semua"

            # Kondisi jika kolom tanggal tersedia
            if 'TGL LAPORAN' in df.columns:
                df['TGL LAPORAN'] = pd.to_datetime(df['TGL LAPORAN'], errors='coerce', dayfirst=True)
                
                if filter_option == "Tanggal Tertentu":
                    col1, col2 = st.columns(2)
                    with col1:
                        start_date = st.date_input(
                            "Tanggal Mulai",
                            value=df['TGL LAPORAN'].min().date() if not df['TGL LAPORAN'].isna().all() else pd.to_datetime('today').date(),
                            min_value=df['TGL LAPORAN'].min().date() if not df['TGL LAPORAN'].isna().all() else pd.to_datetime('2020-01-01').date(),
                            max_value=df['TGL LAPORAN'].max().date() if not df['TGL LAPORAN'].isna().all() else pd.to_datetime('today').date()
                        )
                    with col2:
                        end_date = st.date_input(
                            "Tanggal Selesai",
                            value=df['TGL LAPORAN'].max().date() if not df['TGL LAPORAN'].isna().all() else pd.to_datetime('today').date(),
                            min_value=df['TGL LAPORAN'].min().date() if not df['TGL LAPORAN'].isna().all() else pd.to_datetime('2020-01-01').date(),
                            max_value=df['TGL LAPORAN'].max().date() if not df['TGL LAPORAN'].isna().all() else pd.to_datetime('today').date()
                        )
                    
                    # Konversi ke datetime untuk filtering
                    start_dt = pd.to_datetime(start_date)
                    end_dt = pd.to_datetime(end_date)
                    
                    # Filter data berdasarkan rentang tanggal
                    df_filtered = df[(df['TGL LAPORAN'] >= start_dt) & (df['TGL LAPORAN'] <= end_dt)]
                    pilihan = f"{start_date} sampai {end_date}"

            else:
                st.warning("⚠️ Kolom 'TGL LAPORAN' tidak ditemukan! Filter waktu dinonaktifkan.")
                filter_option = "Semua"
                pilihan = "Semua"

            # Daftar gangguan terdeteksi
            jenis_dipilih = [
                'Focut', 'Pengecekan Perangkat', 'Cek Keseluruhan', 'Pemasangan Baru',
                'Loss', 'Redaman Tinggi/Besar', 'Redaman Loss', 'Perapihan Kabel',
                'Geser Perangkat', 'Kabel Putus', 'MT ODP'
            ]

            df_filtered = df_filtered[df_filtered['KENDALA'].isin(jenis_dipilih)]

            if df_filtered.empty:
                st.error("❌ Tidak ada data sesuai filter yang dipilih.")
                return

            gangguan_count = df_filtered['KENDALA'].value_counts()

            if filter_option != "Semua":
                st.info(f"📌 Menampilkan data berdasarkan filter: **{filter_option} - {pilihan}**")
            else:
                st.info("📌 Menampilkan seluruh data gangguan")

    
            # Grafik Barplot Gangguan
            # ==============================
            fig, ax = plt.subplots(figsize=(9, 6))
            colors = sns.color_palette("Blues_r", len(gangguan_count))

            sns.barplot(x=gangguan_count.index, y=gangguan_count.values,
                        ax=ax, palette=colors, width=0.6)

            for i, val in enumerate(gangguan_count.values):
                ax.text(i, val + 0.2, str(val), ha='center', va='bottom',
                        fontsize=10, fontweight='bold')

            ax.set_title("Frekuensi Jenis Gangguan (Tersering)",
                        fontsize=15, fontweight='bold', pad=15)
            plt.xticks(rotation=15)
            sns.despine()

            st.pyplot(fig)

            st.info(f"📈 Jenis gangguan paling sering: **{gangguan_count.index[0]}** ({gangguan_count.iloc[0]} kasus)")
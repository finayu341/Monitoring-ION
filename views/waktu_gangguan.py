import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

class WaktuGangguan:

    #Method
    @staticmethod
    def show(df):
        st.markdown("""
        <div style="background: linear-gradient(90deg, #4b6cb7 0%, #182848 100%);
                    padding: 20px; border-radius: 10px; margin-bottom: 25px;">
            <h2 style="color: white; margin: 0; text-align: center;">👥Waktu Gangguan</h2>
        </div>
        """, unsafe_allow_html=True)

        df.columns = df.columns.str.strip().str.upper()

        if 'TGL LAPORAN' not in df.columns:
            st.warning("Kolom 'TGL LAPORAN' tidak ditemukan!")
            return

        df['TGL LAPORAN'] = pd.to_datetime(df['TGL LAPORAN'], errors='coerce', dayfirst=True)
        # Hanya ambil bulan dan tahun saja, hapus hari
        df['bulan'] = df['TGL LAPORAN'].dt.month_name()
        df['tahun'] = df['TGL LAPORAN'].dt.year


        # Container untuk filter
        with st.container():
            # Hanya menyisakan filter tahun saja
            tahun_unik = sorted(df['tahun'].dropna().unique())
            tahun_terpilih = st.selectbox(
                "Pilih Tahun:",
                options=["Semua Tahun"] + [int(t) for t in tahun_unik if pd.notna(t)],
                index=0
            )

        # Terapkan filter
        df_filtered = df.copy()
        
        if tahun_terpilih != "Semua Tahun":
            df_filtered = df_filtered[df_filtered['tahun'] == tahun_terpilih]

        # Status filter
        st.markdown("---")
        
        # Tampilkan status filter
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.info(f"**Filter Aktif:** Tahun: {tahun_terpilih} | Total Kasus: {len(df_filtered)}")
        
        with col2:
            if len(df_filtered) > 0:
                st.success("✅ Data Ditemukan")
            else:
                st.error("❌ Tidak Ada Data")


        # Diagram Gangguan Per Bulan
        st.write("#### 📈 Diagram Batang - Gangguan per Bulan")
        
        if tahun_terpilih != "Semua Tahun":
            # Tampilkan semua bulan dalam tahun yang dipilih
            df_bulan = df[df['tahun'] == tahun_terpilih]
            gangguan_bulan = df_bulan['bulan'].value_counts()
        else:
            # Tampilkan semua bulan dari semua tahun
            gangguan_bulan = df['bulan'].value_counts()
        
        # Urutkan berdasarkan urutan bulan
        bulan_urutan = ['January', 'February', 'March', 'April', 'May', 'June', 
                       'July', 'August', 'September', 'October', 'November', 'December']
        gangguan_bulan = gangguan_bulan.reindex([b for b in bulan_urutan if b in gangguan_bulan.index], fill_value=0)
        
        fig, ax = plt.subplots(figsize=(14, 7))
        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD', 
                 '#98D8C8', '#F7DC6F', '#BB8FCE', '#85C1E9', '#82E0AA', '#F8C471']
        bars = ax.bar(gangguan_bulan.index, gangguan_bulan.values, color=colors, 
                     edgecolor='white', linewidth=2, alpha=0.8)
        
        ax.set_title(f"🗓️ DISTRIBUSI GANGGUAN PER BULAN\nTahun: {tahun_terpilih}", 
                    fontsize=16, fontweight='bold', pad=20)
        ax.set_xlabel("Bulan", fontweight='bold', fontsize=12)
        ax.set_ylabel("Jumlah Gangguan", fontweight='bold', fontsize=12)
        plt.xticks(rotation=45)
        
        # Tambahkan nilai di atas bar
        for bar in bars:
            height = bar.get_height()
            if height > 0:
                ax.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                        f'{int(height)}',
                        ha='center', va='bottom', fontweight='bold', fontsize=11)
        
        ax.grid(axis='y', alpha=0.3)
        ax.set_axisbelow(True)
        ax.set_facecolor('#f8f9fa')
        
        st.pyplot(fig)
        
        # Statistik untuk bulan
        if not gangguan_bulan.empty:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric(
                    label="📈 Bulan Tertinggi", 
                    value=gangguan_bulan.idxmax(), 
                    delta=f"{gangguan_bulan.max()} kasus"
                )
            with col2:
                st.metric(
                    label="📉 Bulan Terendah", 
                    value=gangguan_bulan.idxmin(), 
                    delta=f"{gangguan_bulan.min()} kasus"
                )
            with col3:
                st.metric(
                    label="📦 Total Kasus", 
                    value=gangguan_bulan.sum()
                )
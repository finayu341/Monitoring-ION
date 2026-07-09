import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

class Pelanggan:

    #Method
    @staticmethod
    def show(df):
    # Style header
        st.markdown("""
        <div style="background: linear-gradient(90deg, #4b6cb7 0%, #182848 100%);
                    padding: 20px; border-radius: 10px; margin-bottom: 25px;">
            <h2 style="color: white; margin: 0; text-align: center;">👥 DATA PELANGGAN</h2>
        </div>
        """, unsafe_allow_html=True)

        df.columns = df.columns.str.strip().str.upper()

        # Hitung Pelanggan pelanggan
        df_pelanggan = df.groupby(['ID PELANGGAN', 'NAMA PELANGGAN']).agg({
            'DURASI_PENANGANAN': 'mean',
            'KENDALA': 'count'
        }).rename(columns={
            'KENDALA': 'JUMLAH_GANGGUAN',
            'DURASI_PENANGANAN': 'RATA2_DURASI'
        }).reset_index()


        # Konversi durasi ke hari jika > 48 jam
        if df_pelanggan['RATA2_DURASI'].max() > 48:
            df_pelanggan['RATA2_DURASI_HARI'] = (df_pelanggan['RATA2_DURASI'] / 24).round(2)
            label_durasi = "Rata-rata Durasi Penanganan (hari)"
        else:
            df_pelanggan['RATA2_DURASI_HARI'] = df_pelanggan['RATA2_DURASI'].round(2)
            label_durasi = "Rata-rata Durasi Penanganan (jam)"


        # 🔍 FITUR PENCARIAN 
        # ============================
        st.write("### Cari Data Pelanggan")
        search_term = st.text_input("Masukkan Nama atau ID Pelanggan:")

        if search_term:
            hasil_cari = df[
                df['NAMA PELANGGAN'].astype(str).str.contains(search_term, case=False, na=False) |
                df['ID PELANGGAN'].astype(str).str.contains(search_term, case=False, na=False)
            ]
            if not hasil_cari.empty:
                st.success(f"Ditemukan {len(hasil_cari)} hasil untuk: *{search_term}*")
                st.dataframe(hasil_cari)
            else:
                st.warning(f"Tidak ditemukan pelanggan dengan kata kunci: *{search_term}*")
        else:
            st.info("Ketik nama atau ID pelanggan untuk mencari data pelanggan tertentu.")
            st.write("### Data Pelanggan")
            st.dataframe(df.sample(min(10, len(df))).reset_index(drop=True))

        
        # =====================
        st.markdown("---")
        st.markdown("### REKAP DATA PELANGGAN")

        # Diagram Batang 1: Top 10 Pelanggan dengan Gangguan Terbanyak
        st.write("#### 📈 10 Pelanggan dengan Gangguan Terbanyak")
        
        top_10_gangguan = df_pelanggan.nlargest(10, 'JUMLAH_GANGGUAN')

        top_10_gangguan['ID PELANGGAN'] = top_10_gangguan['ID PELANGGAN'].astype(str)
        top_10_gangguan['NAMA PELANGGAN'] = top_10_gangguan['NAMA PELANGGAN'].astype(str)

        labels = top_10_gangguan['NAMA PELANGGAN'].str[:20] + " (" + top_10_gangguan['ID PELANGGAN'] + ")"

        fig1, ax1 = plt.subplots(figsize=(12, 6))
        bars1 = ax1.bar(
            labels,
            top_10_gangguan['NAMA PELANGGAN'].str[:20] + " (" + top_10_gangguan['ID PELANGGAN'].astype(str) + ")",
            top_10_gangguan['JUMLAH_GANGGUAN'],
            color='#FF6B6B',
            alpha=0.8,
            edgecolor='darkred'
        )
        
        ax1.set_title("10 Pelanggan dengan Jumlah Gangguan Terbanyak", fontsize=16, fontweight='bold', pad=20)
        ax1.set_xlabel("Nama Pelanggan (ID)", fontweight='bold')
        ax1.set_ylabel("Jumlah Gangguan", fontweight='bold')
        plt.xticks(rotation=45, ha='right')
        
        # Tambahkan nilai di atas bar
        for bar in bars1:
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                    f'{int(height)}', ha='center', va='bottom', fontweight='bold')
        
        ax1.grid(axis='y', alpha=0.3)
        ax1.set_axisbelow(True)
        plt.tight_layout()
        st.pyplot(fig1)

        # Diagram Batang 2: Top 10 Pelanggan dengan Durasi Penanganan Terlama
        st.write("#### ⏱️ 10 Pelanggan dengan Durasi Penanganan Terlama")
        
        top_10_durasi = df_pelanggan.nlargest(10, 'RATA2_DURASI_HARI')

        top_10_durasi['ID PELANGGAN'] = top_10_durasi['ID PELANGGAN'].astype(str)
        labels2 = top_10_durasi['NAMA PELANGGAN'].astype(str).str[:20] + \
                " (" + top_10_durasi['ID PELANGGAN'] + ")"

        fig2, ax2 = plt.subplots(figsize=(12, 6))

        bars2 = ax2.bar(
            labels2,
            top_10_durasi['RATA2_DURASI_HARI'],  # Hanya height
            color='#4ECDC4',
            alpha=0.8,
            edgecolor='darkgreen'
        )

        ax2.set_title(f"10 Pelanggan dengan {label_durasi} Terlama", fontsize=16, fontweight='bold', pad=20)
        ax2.set_xlabel("Nama Pelanggan (ID)", fontweight='bold')
        ax2.set_ylabel(label_durasi, fontweight='bold')
        plt.xticks(rotation=45, ha='right')

        # Tambah nilai
        for bar in bars2:
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                    f'{height:.1f}', ha='center', va='bottom', fontweight='bold')

        ax2.grid(axis='y', alpha=0.3)
        ax2.set_axisbelow(True)
        plt.tight_layout()
        st.pyplot(fig2)

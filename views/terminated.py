import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

class Terminated:

    #Method
    @staticmethod
    def show(df):
        st.markdown("""
        <div style="background: linear-gradient(90deg, #4b6cb7 0%, #182848 100%);
                    padding: 20px; border-radius: 10px; margin-bottom: 25px;">
            <h2 style="color: white; margin: 0; text-align: center;">📉 Analisis Potensi Pelanggan Berisiko Terminated</h2>
        </div>
        """, unsafe_allow_html=True)

        df.columns = df.columns.str.strip().str.upper()

        if 'durasi_penanganan' not in df.columns:
            if 'TGL LAPORAN' in df.columns and 'TGL PENANGANAN' in df.columns:
                df['durasi_penanganan'] = (df['TGL PENANGANAN'] - df['TGL LAPORAN']).dt.days
            else:
                st.error("Kolom TGL LAPORAN atau TGL PENANGANAN tidak ditemukan.")
                return

        df['Status Berisiko'] = df['durasi_penanganan'].apply(lambda x: 'Berisiko' if x > 7 else 'Aman')
        terminate = df['Status Berisiko'].value_counts(normalize=True) * 100

        fig, ax = plt.subplots(figsize=(6, 4))  
        colors = ['#00C851', '#ff4444']  
        
        bars = sns.barplot(x=terminate.index, y=terminate.values, palette=colors, ax=ax, alpha=0.8)
        
        # Tambahkan nilai di atas bar
        for i, v in enumerate(terminate.values):
            ax.text(i, v + 1, f"{v:.1f}%", ha='center', fontweight='bold', fontsize=10)
        
        # style
        ax.set_title("📊 Persentase Pelanggan Berisiko Terminated", fontweight='bold', pad=15)
        ax.set_ylabel("Persentase (%)", fontweight='bold')
        ax.set_xlabel("Status", fontweight='bold')
        ax.grid(axis='y', alpha=0.3)
        ax.set_axisbelow(True)
        
        # Hapus spines 
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        
        plt.tight_layout()
        st.pyplot(fig)

        st.markdown("---")
        
        # Section Pelanggan Berisiko 
        st.markdown("""
        <div style="background: linear-gradient(135deg, #ff6b6b 0%, #ee5a52 100%);
                    padding: 15px; border-radius: 10px; margin-bottom: 20px;">
            <h3 style="color: white; margin: 0; text-align: center;">🚨 Pelanggan Berisiko Terminated Tinggi</h3>
        </div>
        """, unsafe_allow_html=True)
        
        churn_list = df[df['Status Berisiko'] == 'Berisiko'][['ID PELANGGAN', 'NAMA PELANGGAN', 'durasi_penanganan']].head(5)
        churn_list = churn_list.reset_index(drop=True)
        
        # style
        st.dataframe(
            churn_list,
            column_config={
                "ID PELANGGAN": "🆔 ID Pelanggan",
                "NAMA PELANGGAN": "👤 Nama Pelanggan", 
                "durasi_penanganan": st.column_config.NumberColumn(
                    "⏱️ Durasi (hari)",
                    help="Durasi penanganan dalam hari",
                    format="%d hari"
                )
            },
            use_container_width=True
        )

        # Info box
        risiko_persen = (terminate['Berisiko'] if 'Berisiko' in terminate else 0)
        
        if risiko_persen > 0:
            st.error(f"""
            ⚠️ **PERINGATAN:** Terdapat **{risiko_persen:.1f}%** pelanggan berisiko terminated!
            
            Pelanggan dengan durasi penanganan > 7 hari berpotensi mengalami ketidakpuasan 
            dan berisiko menghentikan layanan.
            """)
        else:
            st.success("""
            ✅ **BAIK:** Tidak ada pelanggan yang berisiko terminated!
            
            Semua pelanggan memiliki durasi penanganan yang wajar (≤ 7 hari).
            """)
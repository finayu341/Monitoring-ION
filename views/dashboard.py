import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from views.teknisi import get_top_teknisi
from views.gangguan import Gangguan
from views.daerah import Daerah

class Dashboard:

    @staticmethod
    def show(df):
        # Header dengan gradient yang lebih modern
        st.markdown("""
        <div style="background: linear-gradient(90deg, #4b6cb7 0%, #182848 100%);
                    padding: 25px; border-radius: 15px; margin-bottom: 30px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
            <h2 style="color: white; margin: 0; text-align: center; font-size: 32px;">📊 DASHBOARD ANALYTICS</h2>
        </div>
        """, unsafe_allow_html=True)

        df.columns = df.columns.str.strip().str.upper()

        # 1️⃣ Analisis Jenis Gangguan
        top_name, total = Gangguan.get_top_gangguan(df)

        # 2️⃣ Daerah dengan gangguan tertinggi
        top_daerah, total_daerah = Daerah.get_top_daerah(df)

        # 3️⃣ Pelanggan
        total_pelanggan = df['ID PELANGGAN'].nunique() if 'ID PELANGGAN' in df.columns else 0

        # 4️⃣ Total Kasus Gangguan
        total_kendala = df['KENDALA'].count()

        # 5 Waktu Gangguan (rata-rata durasi)
        df['bulan'] = df['TGL LAPORAN'].dt.month_name()
        df['tahun'] = df['TGL LAPORAN'].dt.year

        # Bulan
        gangguan_bulan = df['bulan'].value_counts()
        top_bulan = gangguan_bulan.idxmax()
        jumlah_bulan = gangguan_bulan.max()

        # Tahun 
        gangguan_tahun = (
            df['tahun']
            .dropna()
            .astype(int)
            .value_counts()
            .sort_index()
        )
        top_tahun = gangguan_tahun.idxmax()
        jumlah_tahun = gangguan_tahun.max()

        # 6 Terminated Risk
        if 'DURASI_PENANGANAN' in df.columns:
            df['Status Berisiko'] = df['DURASI_PENANGANAN'].apply(lambda x: 'Berisiko' if x > 7 else 'Aman')
            churn_rate = df['Status Berisiko'].value_counts(normalize=True).get('Berisiko', 0) * 100
        else:
            churn_rate = 0

        # 7 teknisi
        top_teknisi, total_teknisi = get_top_teknisi(df)

        # ============================
        st.markdown("""
        <h3 style="color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px; margin-bottom: 20px;">
            📈 HASIL DATA
        </h3>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        col3, col4 = st.columns(2)
        col5, col6 = st.columns(2) 
        col7, col8 = st.columns(2)

        # Kotak 1 - Jenis Gangguan
        with col1:
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
                        padding: 20px; border-radius: 15px; margin-bottom: 20px; 
                        box-shadow: 0 4px 8px rgba(0,0,0,0.05); border: 1px solid #e0e0e0;">
                <div style="display: flex; align-items: center; margin-bottom: 10px;">
                    <div style="background-color: #3498db; color: white; border-radius: 50%; width: 40px; height: 40px; 
                                display: flex; align-items: center; justify-content: center; margin-right: 10px;">
                        🧩
                    </div>
                    <h4 style="margin:0; color: #2c3e50;">Jenis Gangguan Tertinggi</h4>
                </div>
                <p style="font-size:22px; margin:10px 0; font-weight: bold; color: #2c3e50;">{top_name}</p>
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <p style="color: #7f8c8d; margin:0;">Total Kasus</p>
                    <span style="background-color: #3498db; color: white; padding: 3px 10px; border-radius: 12px; font-size: 14px;">
                        {total}
                    </span>
                </div>
            </div>
            """, unsafe_allow_html=True)

        # Kotak 2 - Daerah
        with col2:
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%);
                        padding: 20px; border-radius: 15px; margin-bottom: 20px; 
                        box-shadow: 0 4px 8px rgba(0,0,0,0.05); border: 1px solid #e0e0e0;">
                <div style="display: flex; align-items: center; margin-bottom: 10px;">
                    <div style="background-color: #e67e22; color: white; border-radius: 50%; width: 40px; height: 40px; 
                                display: flex; align-items: center; justify-content: center; margin-right: 10px;">
                        📍
                    </div>
                    <h4 style="margin:0; color: #2c3e50;">Daerah Terbanyak Gangguan</h4>
                </div>
                <p style="font-size:22px; margin:10px 0; font-weight: bold; color: #2c3e50;">{top_daerah}</p>
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <p style="color: #7f8c8d; margin:0;">Total Kasus</p>
                    <span style="background-color: #e67e22; color: white; padding: 3px 10px; border-radius: 12px; font-size: 14px;">
                        {total_daerah}
                    </span>
                </div>
            </div>
            """, unsafe_allow_html=True)

        # kotak 3 - pelanggan
        with col3:
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #d299c2 0%, #fef9d7 100%);
                        padding: 20px; border-radius: 15px; margin-bottom: 20px; 
                        box-shadow: 0 4px 8px rgba(0,0,0,0.05); border: 1px solid #e0e0e0;">
                <div style="display: flex; align-items: center; margin-bottom: 10px;">
                    <div style="background-color: #9b59b6; color: white; border-radius: 50%; width: 40px; height: 40px; 
                                display: flex; align-items: center; justify-content: center; margin-right: 10px;">
                        👥
                    </div>
                    <h4 style="margin:0; color: #2c3e50;">Total Pelanggan</h4>
                </div>
                <p style="font-size:28px; margin:10px 0; font-weight: bold; color: #2c3e50; text-align: center;">{total_pelanggan}</p>
                <p style="color: #7f8c8d; margin:0; text-align: center;">Jumlah pelanggan aktif</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Kotak 4 - Total Kasus
        with col4:
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #89f7fe 0%, #66a6ff 100%);
                        padding: 20px; border-radius: 15px; margin-bottom: 20px; 
                        box-shadow: 0 4px 8px rgba(0,0,0,0.05); border: 1px solid #e0e0e0;">
                <div style="display: flex; align-items: center; margin-bottom: 10px;">
                    <div style="background-color: #2980b9; color: white; border-radius: 50%; width: 40px; height: 40px; 
                                display: flex; align-items: center; justify-content: center; margin-right: 10px;">
                        ⚙️
                    </div>
                    <h4 style="margin:0; color: #2c3e50;">Total Kasus Gangguan</h4>
                </div>
                <p style="font-size:28px; margin:10px 0; font-weight: bold; color: #2c3e50; text-align: center;">{total_kendala}</p>
                <p style="color: #7f8c8d; margin:0; text-align: center;">Kasus yang ditangani</p>
            </div>
            """, unsafe_allow_html=True)

        # Kotak 5 - Rekap Waktu
        with col5:
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #a3bded 0%, #6991c7 100%);
                        padding: 20px; border-radius: 15px; margin-bottom: 20px; 
                        box-shadow: 0 4px 8px rgba(0,0,0,0.05); border: 1px solid #e0e0e0;">
                <div style="display: flex; align-items: center; margin-bottom: 10px;">
                    <div style="background-color: #34495e; color: white; border-radius: 50%; width: 40px; height: 40px; 
                                display: flex; align-items: center; justify-content: center; margin-right: 10px;">
                        ⏱️
                    </div>
                    <h4 style="margin:0; color: #2c3e50;">Rekap Waktu Gangguan</h4>
                </div>
                <div style="margin-top: 15px;">
                    <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                        <span style="color: #7f8c8d;">Bulan Tertinggi:</span>
                        <span style="font-weight: bold; color: #2c3e50;">{top_bulan} ({jumlah_bulan})</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                        <span style="color: #7f8c8d;">Tahun Tertinggi:</span>
                        <span style="font-weight: bold; color: #2c3e50;">{top_tahun} ({jumlah_tahun})</span>
                    </div>
                </div>
                <p style="color: #7f8c8d; margin:10px 0 0 0; font-size: 12px;">Data dari tanggal penanganan</p>
            </div>
            """, unsafe_allow_html=True)

        # Kotak 6 - Terminated Risk
        with col6:
            # Tentukan warna berdasarkan tingkat risiko
            risk_color = "#e74c3c" if churn_rate > 10 else "#f39c12" if churn_rate > 5 else "#2ecc71"
            
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%);
                        padding: 20px; border-radius: 15px; margin-bottom: 20px; 
                        box-shadow: 0 4px 8px rgba(0,0,0,0.05); border: 1px solid #e0e0e0;">
                <div style="display: flex; align-items: center; margin-bottom: 10px;">
                    <div style="background-color: {risk_color}; color: white; border-radius: 50%; width: 40px; height: 40px; 
                                display: flex; align-items: center; justify-content: center; margin-right: 10px;">
                        📉
                    </div>
                    <h4 style="margin:0; color: #2c3e50;">Pelanggan Berisiko</h4>
                </div>
                <p style="font-size:28px; margin:10px 0; font-weight: bold; color: {risk_color}; text-align: center;">{churn_rate:.2f}%</p>
                <div style="background-color: #f5f5f5; border-radius: 10px; height: 10px; margin: 15px 0;">
                    <div style="background-color: {risk_color}; height: 100%; width: {min(churn_rate, 100)}%; border-radius: 10px;"></div>
                </div>
                <p style="color: #7f8c8d; margin:0; text-align: center;">Persentase pelanggan berisiko tinggi</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Kotak 7 - Teknisi
        with col7:
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
                        padding: 20px; border-radius: 15px; margin-bottom: 20px; 
                        box-shadow: 0 4px 8px rgba(0,0,0,0.05); border: 1px solid #e0e0e0;">
                <div style="display: flex; align-items: center; margin-bottom: 10px;">
                    <div style="background-color: #8e44ad; color: white; border-radius: 50%; width: 40px; height: 40px; 
                                display: flex; align-items: center; justify-content: center; margin-right: 10px;">
                        👨‍🔧
                    </div>
                    <h4 style="margin:0; color: #2c3e50;">Teknisi Teraktif</h4>
                </div>
                <p style="font-size:22px; margin:10px 0; font-weight: bold; color: #2c3e50;">{top_teknisi}</p>
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <p style="color: #7f8c8d; margin:0;">Total Penanganan</p>
                    <span style="background-color: #8e44ad; color: white; padding: 3px 10px; border-radius: 12px; font-size: 14px;">
                        {total_teknisi}
                    </span>
                </div>
            </div>
            """, unsafe_allow_html=True)
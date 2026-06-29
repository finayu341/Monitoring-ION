import streamlit as st
import pandas as pd
import numpy as np
import os

class DataLoader:
    @staticmethod
    @st.cache_data
    def load_data(path=None):
        """
        Load data dari file Excel.
        Jika path tidak diberikan, akan menggunakan file default 'data_kotor.xlsx'
        """
        # Jika path tidak diberikan, coba gunakan file default
        if path is None:
            if os.path.exists('data_kotor.xlsx'):
                path = 'data_kotor.xlsx'
            else:
                st.error("❌ File default 'data_kotor.xlsx' tidak ditemukan.")
                return pd.DataFrame()
        
        # Cek apakah file exists
        if not os.path.exists(path):
            st.error(f"❌ File tidak ditemukan di lokasi: {path}")
            return pd.DataFrame()

        try:
            # Load data dari Excel
            df = pd.read_excel(path)
            
            # Jika DataFrame kosong
            if df.empty:
                st.warning("⚠️ File Excel kosong atau tidak berisi data.")
                return df

            # Standardize column names to uppercase
            df.columns = df.columns.str.upper()

            # Convert date columns
            for col in ['TGL LAPORAN', 'TGL PENANGANAN']:
                if col in df.columns:
                    df[col] = pd.to_datetime(df[col], errors='coerce')

            # Calculate duration if both date columns exist
            if 'TGL LAPORAN' in df.columns and 'TGL PENANGANAN' in df.columns:
                df['durasi_penanganan'] = (df['TGL PENANGANAN'] - df['TGL LAPORAN']).dt.days

            # Add KENDALA column if not exists
            if 'KENDALA' not in df.columns:
                # Coba cari kolom keterangan dengan berbagai kemungkinan nama
                keterangan_cols = [col for col in df.columns if 'keterangan' in col.lower() or 'KETERANGAN' in col]
                
                if keterangan_cols:
                    keterangan_col = keterangan_cols[0]
                    df['KENDALA'] = np.where(
                        df[keterangan_col].astype(str).str.contains("redaman", case=False, na=False),
                        "Redaman Besar", "Lainnya"
                    )
                else:
                    df['KENDALA'] = "Lainnya"

            st.success(f"✅ Data berhasil dimuat ({len(df)} baris)")
            return df

        except Exception as e:
            st.error(f"❌ Error saat memuat data: {str(e)}")
            return pd.DataFrame()
import pandas as pd
import numpy as np
import os
import streamlit as st


class DataLoader:

    # Baca file Excel mentah
    @staticmethod
    def _read_excel(path):
    
        df = pd.read_excel(path, header=1)
        kolom_1 = [str(c).strip().upper() for c in df.columns]

        if "ID PELANGGAN" not in kolom_1:
            df_alt = pd.read_excel(path, header=0)
            kolom_0 = [str(c).strip().upper() for c in df_alt.columns]
            if "ID PELANGGAN" in kolom_0:
                df = df_alt

        return df

    # Standarisasi nama kolom
    # ------------------------------------------------------------------
    @staticmethod
    def standarize_columns(df):
        """Standarisasi nama kolom menjadi huruf kapital & rapi (tanpa spasi ganda)."""
        df = df.copy()
        df.columns = (
            df.columns
            .astype(str)
            .str.strip()
            .str.upper()
            .str.replace(r"\s+", " ", regex=True)
        )

        rename_map = {
            "TEKNISI YANG BERTUGAS": "TEKNISI",
        }
        df = df.rename(columns=rename_map)
        return df

    # Hapus baris tidak valid (pemisah bulan / header berulang)
    # ------------------------------------------------------------------
    @staticmethod
    def remove_invalid_rows(df):

        df = df.copy()
        before = len(df)

        bulan = [
            "JANUARI", "FEBRUARI", "MARET", "APRIL", "MEI", "JUNI",
            "JULI", "AGUSTUS", "SEPTEMBER", "OKTOBER", "NOVEMBER", "DESEMBER",
        ]
        pattern_bulan = "|".join(bulan)

        id_col = "ID PELANGGAN"
        other_cols = [c for c in df.columns if c != id_col]

        if id_col in df.columns:
            mengandung_bulan = df[id_col].astype(str).str.upper().str.contains(
                pattern_bulan, na=False, regex=True
            )
            kolom_lain_kosong = df[other_cols].isna().all(axis=1)
            is_bulan = mengandung_bulan & kolom_lain_kosong
        else:
            is_bulan = pd.Series(False, index=df.index)

        def is_repeated_header(row):
            matches = sum(
                1 for col, val in row.items()
                if str(val).strip().upper() == str(col).strip().upper()
            )
            return matches >= 1

        is_header = df.apply(is_repeated_header, axis=1)

        mask_invalid = is_bulan | is_header
        df = df[~mask_invalid].reset_index(drop=True)

        after = len(df)
        print(f"🧹 {before - after} baris tidak valid dihapus "
              f"(pemisah bulan / header berulang), sisa {after} baris")
        return df

    # Hapus baris yang sama sekali kosong
    # ------------------------------------------------------------------
    @staticmethod
    def drop_empty_rows(df):
    
        df = df.copy()
        before = len(df)
        df = df.dropna(how="all")
        after = len(df)
        print(f"🧹 {before - after} baris kosong dihapus (sisa {after} baris)")
        return df.reset_index(drop=True)

    # Isi ulang ID PELANGGAN & NAMA PELANGGAN (forward fill)
    # ------------------------------------------------------------------
    @staticmethod
    def fill_customer_id(df, id_cols=("ID PELANGGAN", "NAMA PELANGGAN")):
        """
        Isi ulang ID PELANGGAN & NAMA PELANGGAN secara berulang (forward
        fill) ke bawah, karena pada file sumber sel tersebut merupakan hasil
        merge cell di Excel sehingga hanya terisi pada baris pertama tiap
        pelanggan.
        """
        df = df.copy()
        for col in id_cols:
            if col in df.columns:
                df[col] = df[col].ffill()
            else:
                print(f"⚠️  Kolom '{col}' tidak ditemukan, dilewati.")
        return df

    # 5. Seragamkan penulisan KENDALA
    # ------------------------------------------------------------------
    KENDALA_REPLACEMENTS = {
        r"FO\s*CUT": "FOCUT",                  # "FO CUT" / "FO  CUT" -> "FOCUT"
        r"CEK\s*PERANGKA\b": "CEK PERANGKAT",  # perbaiki typo "PERANGKA"
        r"PERAPIAN": "PERAPIHAN",              # samakan ejaan "perapian/perapihan"
    }

    @classmethod
    def standardize_kendala(cls, df, col="KENDALA"):
       
        df = df.copy()
        if col not in df.columns:
            print(f"⚠️  Kolom '{col}' tidak ditemukan, dilewati.")
            return df

        teks = df[col].astype(str).str.strip().str.upper()
        teks = teks.str.replace(r"\s+", " ", regex=True)

        for pola, pengganti in cls.KENDALA_REPLACEMENTS.items():
            teks = teks.str.replace(pola, pengganti, regex=True)

        # Kembalikan nilai kosong asli (yang tadinya NaN) agar tetap NaN
        teks = teks.mask(df[col].isna())

        df[col] = teks
        print(f"🔤 Kolom '{col}' berhasil diseragamkan penulisannya")
        return df

    # Isi missing KENDALA dengan modus
    # ------------------------------------------------------------------
    @staticmethod
    def fill_missing_kendala(df, col="KENDALA"):
        """Isi missing value pada KENDALA dengan nilai paling sering muncul (modus)."""
        df = df.copy()
        if col not in df.columns:
            print(f"⚠️  Kolom '{col}' tidak ditemukan, dilewati.")
            return df

        missing_before = df[col].isna().sum()
        if missing_before == 0:
            return df

        modus_series = df[col].mode(dropna=True)
        if modus_series.empty:
            print(f"⚠️  Tidak bisa menghitung modus '{col}' (semua nilai kosong).")
            return df

        nilai_modus = modus_series.iloc[0]
        df[col] = df[col].fillna(nilai_modus)
        print(f"🩹 {missing_before} nilai kosong pada '{col}' diisi dengan "
              f"modus: '{nilai_modus}'")
        return df

    # Konversi kolom tanggal ke datetime
    # ------------------------------------------------------------------
    @staticmethod
    def convert_dates(df, date_cols=("TGL LAPORAN", "TGL PENANGANAN")):
        """Konversi kolom tanggal ke format datetime."""
        df = df.copy()
        for col in date_cols:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors="coerce", dayfirst=False)
            else:
                print(f"⚠️  Kolom '{col}' tidak ditemukan, dilewati.")
        return df

    # Isi missing TGL LAPORAN dengan TGL PENANGANAN sebelumnya
    # ------------------------------------------------------------------
    @staticmethod
    def fill_missing_tgl_laporan(df,
                                  id_col="ID PELANGGAN",
                                  col_lapor="TGL LAPORAN",
                                  col_tangani="TGL PENANGANAN"):
       
        df = df.copy()
        if id_col not in df.columns or col_lapor not in df.columns or col_tangani not in df.columns:
            print(f"⚠️  Kolom '{id_col}'/'{col_lapor}'/'{col_tangani}' tidak lengkap, dilewati.")
            return df

        missing_before = df[col_lapor].isna().sum()
        if missing_before == 0:
            return df

        tgl_penanganan_sebelumnya = df.groupby(id_col)[col_tangani].shift(1)
        df[col_lapor] = df[col_lapor].fillna(tgl_penanganan_sebelumnya)

        missing_after = df[col_lapor].isna().sum()
        print(f"🩹 {missing_before - missing_after} nilai kosong pada '{col_lapor}' "
              f"diisi dengan tanggal penanganan sebelumnya "
              f"({missing_after} masih kosong karena tidak ada riwayat sebelumnya)")
        return df

    # Hitung durasi penanganan
    # ------------------------------------------------------------------
    @staticmethod
    def add_durasi_penanganan(df,
                               col_lapor="TGL LAPORAN",
                               col_tangani="TGL PENANGANAN",
                               new_col="DURASI_PENANGANAN"):
        """Buat kolom durasi penanganan (dalam hari)."""
        df = df.copy()
        if col_lapor in df.columns and col_tangani in df.columns:
            df[new_col] = (df[col_tangani] - df[col_lapor]).dt.days
        else:
            print(f"⚠️  Tidak bisa menghitung durasi, kolom '{col_lapor}' "
                  f"atau '{col_tangani}' tidak ditemukan.")
            df[new_col] = np.nan
        return df


    # ENTRY POINT — dipanggil dari app.py: DataLoader.load_data(path)
    # ------------------------------------------------------------------
    @staticmethod
    @st.cache_data
    def load_data(path=None):
        """
        Load & olah data dari file Excel sampai siap pakai.
        Jika path tidak diberikan, akan menggunakan file default
        'data_kotor.xlsx'.
        """
        if path is None:
            if os.path.exists("data_kotor.xlsx"):
                path = "data_kotor.xlsx"
            else:
                st.error("❌ File default 'data_kotor.xlsx' tidak ditemukan.")
                return pd.DataFrame()

        if not os.path.exists(path):
            st.error(f"❌ File tidak ditemukan di lokasi: {path}")
            return pd.DataFrame()

        try:
            df = DataLoader._read_excel(path)

            if df.empty:
                st.warning("⚠️ File Excel kosong atau tidak berisi data.")
                return df

            df = DataLoader.standarize_columns(df)
            df = DataLoader.remove_invalid_rows(df)
            df = DataLoader.drop_empty_rows(df)
            df = DataLoader.fill_customer_id(df)
            df = DataLoader.standardize_kendala(df)
            df = DataLoader.fill_missing_kendala(df)
            df = DataLoader.convert_dates(df)
            df = DataLoader.fill_missing_tgl_laporan(df)
            df = DataLoader.add_durasi_penanganan(df)

            st.success(f"✅ Data berhasil dimuat ({len(df)} baris)")
            return df

        except Exception as e:
            st.error(f"❌ Error saat memuat data: {str(e)}")
            return pd.DataFrame()
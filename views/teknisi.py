import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from io import BytesIO


# Fungsi untuk membersihkan & memproses data teknisi 
# ======================================================
def preprocess_teknisi(df):
    df = df.copy()
    df.columns = df.columns.str.strip().str.upper()

    if 'TEKNISI' not in df.columns or 'TGL PENANGANAN' not in df.columns:
        return None  # tanda dataset tidak valid

    df['TEKNISI'] = (
        df['TEKNISI']
        .astype(str)
        .str.upper()
        .str.replace(r'TS\s*[:\-~]*', '', regex=True)   # hapus TS
        .str.replace(r'TIM.*', '', regex=True)          # hapus TIM
        .str.replace(r'\(.*?\)', '', regex=True)        # hapus isi kurung
        .str.replace(r'[^A-Z,& ]', '', regex=True)      # hanya huruf, spasi, koma, &
        .str.replace(r'\s+', ' ', regex=True)           # rapikan spasi
        .str.strip()
    )

    # Pisahkan teknisi
    df = df.assign(
        TEKNISI=df['TEKNISI'].str.split(r'\s*&\s*|\s*,\s*|\s*DAN\s*', regex=True)
    ).explode('TEKNISI')

    df['TEKNISI'] = (
        df['TEKNISI']
        .str.strip()
        .str.replace(r'[^A-Z ]', '', regex=True)
        .str.replace(r'\s+', ' ', regex=True)
    )

    df['TEKNISI'] = df['TEKNISI'].str.strip().replace(['', ' ', 'NULL', None], '-')

    # Convert tanggal
    df['TGL PENANGANAN'] = pd.to_datetime(df['TGL PENANGANAN'], errors='coerce', dayfirst=True)
    df = df.dropna(subset=['TGL PENANGANAN'])

    return df


# Method 1: teknisi terbanyak
# ======================================================
def get_top_teknisi(df):
    df_clean = preprocess_teknisi(df)
    if df_clean is None or df_clean.empty:
        return "-", 0

    counts = df_clean['TEKNISI'].value_counts()
    if counts.empty:
        return "-", 0

    return counts.index[0], counts.iloc[0]


#============================================
def generate_pdf(df_export):
    buffer = BytesIO()

    doc = SimpleDocTemplate(buffer, pagesize=A4)
    elements = []
    styles = getSampleStyleSheet()

    title = Paragraph("Laporan Detail Kinerja Teknisi", styles['Title'])
    elements.append(title)
    elements.append(Spacer(1, 12))

    # siapkan data
    table_data = [df_export.columns.tolist()] + df_export.astype(str).values.tolist()

    table = Table(table_data)

    table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#5b5fa8')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('GRID', (0,0), (-1,-1), 0.5, colors.black),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 8),
        ('ALIGN', (0,0), (-1,-1), 'CENTER')
    ]))

    elements.append(table)

    doc.build(elements)
    buffer.seek(0)

    return buffer

# ======================================================
class Teknisi:

    @staticmethod
    def show(df):
        st.markdown("""
        <div style="background-color:#5b5fa8;padding:20px;border-radius:10px;margin-bottom:20px">
            <h2 style="color:white;text-align:center;margin:0;">Kinerja Teknisi</h2>
        </div>
        """, unsafe_allow_html=True)

        df_clean = preprocess_teknisi(df)

        if df_clean is None or df_clean.empty:
            st.warning("Data teknisi tidak tersedia")
            return

        # =============================
        # FILTER
        # =============================
        st.markdown("### Pilih Teknisi")

        col1, col2, col3 = st.columns(3)

        with col1:
            tanggal_range = st.date_input(
                "Pilih Rentang Tanggal",
                []
            )

        with col2:
            teknisi_list = ["Semua Teknisi"] + sorted(df_clean['TEKNISI'].unique().tolist())
            selected_teknisi = st.selectbox("Teknisi", teknisi_list)

        with col3:
            wilayah_list = ["Semua"] + sorted(df['DAERAH'].dropna().unique().tolist()) if 'DAERAH' in df.columns else ["Semua"]
            selected_wilayah = st.selectbox("Wilayah", wilayah_list)

        df_filtered = df_clean.copy()

        # filter teknisi
        if selected_teknisi != "Semua Teknisi":
            df_filtered = df_filtered[df_filtered['TEKNISI'] == selected_teknisi]

        # filter wilayah
        if selected_wilayah != "Semua" and 'DAERAH' in df.columns:
            df_filtered = df_filtered[df['DAERAH'] == selected_wilayah]

        # filter tanggal
        if len(tanggal_range) == 2:
            start, end = pd.to_datetime(tanggal_range[0]), pd.to_datetime(tanggal_range[1])
            df_filtered = df_filtered[
                (df_filtered['TGL PENANGANAN'] >= start) &
                (df_filtered['TGL PENANGANAN'] <= end)
            ]

        # =============================
        # METRICS
        # =============================
        total_penanganan = len(df_filtered)

        rata_durasi = df_filtered['DURASI_PENANGANAN'].mean() if 'DURASI_PENANGANAN' in df_filtered.columns else 0

        sla = 0
        if 'DURASI_PENANGANAN' in df_filtered.columns:
            sla = (df_filtered['DURASI_PENANGANAN'] <= 1).mean() * 100

        top_gangguan = "-"
        if 'KENDALA' in df_filtered.columns:
            top_gangguan = df_filtered['KENDALA'].mode()[0]

        col1, col2, col3, col4 = st.columns(4)

        col1.metric("TOTAL PENANGANAN", f"{total_penanganan:,}")
        col2.metric("RATA-RATA WAKTU RESPON", f"{rata_durasi:.1f} Hari")
        col3.metric("PERSENTASE SLA (<24 JAM)", f"{sla:.0f}%")
        col4.metric("GANGGUAN TERTINGGI", top_gangguan)

        # =============================
        # CHART
        # =============================
        col1, col2 = st.columns(2)

        # TOP 5 TEKNISI
        with col1:
            st.markdown("#### TOP 5 TERTINGGI")

            top_teknisi = df_filtered['TEKNISI'].value_counts().head(5)

            fig, ax = plt.subplots(figsize=(6, 4))
            sns.barplot(
                x=top_teknisi.values,
                y=top_teknisi.index,
                palette="Blues_r",
                ax=ax
            )

            for i, v in enumerate(top_teknisi.values):
                ax.text(v + 1, i, str(v), va='center')

            ax.set_xlabel("Jumlah Kasus")
            ax.set_ylabel("")
            st.pyplot(fig)

        # PIE CHART
        with col2:
            st.markdown("#### DISTRIBUSI GANGGUAN")

            if 'KENDALA' in df_filtered.columns:
                distribusi = df_filtered['KENDALA'].value_counts().head(5)

                fig2, ax2 = plt.subplots()
                ax2.pie(
                    distribusi.values,
                    labels=distribusi.index,
                    autopct='%1.0f%%'
                )
                ax2.set_title("Distribusi Gangguan")
                st.pyplot(fig2)

        # =============================
        # DETAIL TABLE
        # =============================
        st.markdown("### DETAIL TEKNISI")

        cols = ['TEKNISI', 'KENDALA', 'DAERAH', 'DURASI_PENANGANAN']
        cols = [c for c in cols if c in df_filtered.columns]

        df_export = df_filtered[cols].head(20)

        st.dataframe(
            df_export,
            use_container_width=True
        )

        # DOWNLOAD PDF
        pdf_file = generate_pdf(df_export)

        # CSS tombol download
        st.markdown("""
        <style>
        div.stDownloadButton > button {
            background-color: #5b5fa8;
            color: white;
            border: none;
            border-radius: 8px;
            padding: 0.5rem 1rem;
            font-weight: bold;
            width: 100%;
        }

        div.stDownloadButton > button:hover {
            background-color: #4a4e90;
            color: white;
            border: none;
        }

        div.stDownloadButton > button:focus {
            box-shadow: none;
        }
        </style>
        """, unsafe_allow_html=True)

        # DOWNLOAD PDF
        pdf_file = generate_pdf(df_export)

        st.download_button(
            label="📄 Download Detail Teknisi (PDF)",
            data=pdf_file,
            file_name="laporan_teknisi.pdf",
            mime="application/pdf"
        )
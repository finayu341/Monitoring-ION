import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
from data_loader import DataLoader
import os
import json

from views.dashboard import Dashboard
from views.gangguan import Gangguan
from views.teknisi import Teknisi
from views.daerah import Daerah
from views.pelanggan import Pelanggan
from views.waktu_gangguan import WaktuGangguan
from views.terminated import Terminated

# ===============================================================
# ⚙️ SETUP DASAR
# ===============================================================
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")
st.set_page_config(page_title="CUSTOBASE.com", layout="wide")

# ===============================================================
# PERSISTENT STORAGE UNTUK FILE UPLOAD

UPLOAD_DIR = "uploaded_data"
UPLOAD_PATH = os.path.join(UPLOAD_DIR, "current_upload.xlsx")
UPLOAD_META_PATH = os.path.join(UPLOAD_DIR, "current_upload_meta.json")

os.makedirs(UPLOAD_DIR, exist_ok=True)


def _read_upload_meta():
    """Baca nama file asli dari metadata, kalau ada."""
    if os.path.exists(UPLOAD_META_PATH):
        try:
            with open(UPLOAD_META_PATH, "r", encoding="utf-8") as f:
                return json.load(f).get("file_name")
        except Exception:
            return None
    return None


def _write_upload_meta(file_name):
    with open(UPLOAD_META_PATH, "w", encoding="utf-8") as f:
        json.dump({"file_name": file_name}, f)


if 'current_data_file' not in st.session_state:
    if os.path.exists(UPLOAD_PATH):
        # Sudah pernah ada file yang di-upload sebelumnya -> tetap pakai itu
        st.session_state.current_data_file = UPLOAD_PATH
        st.session_state.file_name = _read_upload_meta() or "current_upload.xlsx"
        st.session_state.is_uploaded_file = True
    elif os.path.exists('data_kotor.xlsx'):
        # Belum pernah ada upload -> pakai file default
        st.session_state.current_data_file = 'data_kotor.xlsx'
        st.session_state.file_name = 'data_kotor.xlsx'
        st.session_state.is_uploaded_file = False
    else:
        st.session_state.current_data_file = None
        st.session_state.file_name = None
        st.session_state.is_uploaded_file = False


# Fungsi untuk handle upload file
def handle_file_upload():
    uploaded_file = st.sidebar.file_uploader(
        "📤 Upload File Excel",
        type=['xlsx', 'xls'],
        help="Upload file Excel dengan data gangguan"
    )

    if uploaded_file is not None:
        try:
            # Simpan/timpa file ke path TETAP, bukan tempfile random,
            with open(UPLOAD_PATH, "wb") as f:
                f.write(uploaded_file.getvalue())

            _write_upload_meta(uploaded_file.name)

            # Update session state dengan file yang baru saja diupload
            st.session_state.current_data_file = UPLOAD_PATH
            st.session_state.file_name = uploaded_file.name
            st.session_state.is_uploaded_file = True

            st.sidebar.success(f"✅ File '{uploaded_file.name}' berhasil diupload!")

            # Clear cache agar data terload ulang
            st.cache_data.clear()
            return True
        except Exception as e:
            st.sidebar.error(f"❌ Error saat upload file: {e}")
            return False
    return False


# ===============================================================
# SIDEBAR
# ===============================================================
st.markdown("""
<style>
.sidebar .sidebar-content {
    background-image: linear-gradient(#2e7bcf,#2e7bcf);
    color: white;
}
.stRadio > div {
    flex-direction: column;
    align-items: stretch;
}
.stRadio > div > label {
    background-color: #f0f2f6;
    padding: 10px 15px;
    margin-bottom: 5px;
    border-radius: 5px;
    transition: all 0.3s ease;
    border-left: 4px solid #2e7bcf;
}
.stRadio > div > label:hover {
    background-color: #e1e5eb;
    transform: translateX(5px);
}
.stRadio > div > label > div:first-child {
    font-weight: 600;
}
.sidebar-header {
    font-size: 1.5rem;
    font-weight: 700;
    color: #1f3a60;
    margin-bottom: 1rem;
    text-align: center;
    padding-bottom: 10px;
    border-bottom: 2px solid #2e7bcf;
}
.upload-info {
    background-color: #e8f4fd;
    padding: 10px;
    border-radius: 5px;
    margin: 10px 0;
    border-left: 4px solid #2e7bcf;
}
</style>
""", unsafe_allow_html=True)

st.sidebar.markdown('<p class="sidebar-header">📊 Menu Analisis</p>', unsafe_allow_html=True)

pilihan = st.sidebar.radio(
    "Pilih fitur analisis:",
    (
        "Dashboard",
        "Jenis Gangguan",
        "Teknisi",
        "Daerah",
        "Pelanggan",
        "Waktu Gangguan",
        "Analisis Terminated"
    ),
    label_visibility="collapsed"
)

# ===============================================================
# MAIN CONTENT
# ===============================================================
if st.session_state.current_data_file:
    # Load data dengan file yang sedang aktif
    df = DataLoader.load_data(st.session_state.current_data_file)

    if not df.empty:
        # Fitur
        menu_map = {
            "Dashboard": Dashboard(),
            "Jenis Gangguan": Gangguan(),
            "Teknisi": Teknisi(),
            "Daerah": Daerah(),
            "Pelanggan": Pelanggan(),
            "Waktu Gangguan": WaktuGangguan(),
            "Analisis Terminated": Terminated(),
        }

        menu_map[pilihan].show(df)

    else:
        st.error("⚠️ Data tidak berhasil dimuat. Pastikan file Excel memiliki format yang benar.")
else:
    st.warning("👈 Silakan upload file Excel melalui sidebar untuk memulai analisis.")


# Bagian upload file di sidebar
st.sidebar.markdown('<p class="sidebar-header">📂 Upload Data</p>', unsafe_allow_html=True)

# Upload file (kalau ada file baru, otomatis menimpa file lama di disk)
file_uploaded = handle_file_upload()

# Info file yang sedang digunakan
if st.session_state.current_data_file:
    file_name = st.session_state.get('file_name', os.path.basename(st.session_state.current_data_file))
    status_label = 'File upload' if st.session_state.get('is_uploaded_file') else 'File default'
    st.sidebar.markdown(f"""
    <div class="upload-info">
    <strong>📁 File Aktif:</strong><br>
    {file_name}<br>
    <small>{status_label}</small>
    </div>
    """, unsafe_allow_html=True)
else:
    st.sidebar.warning("⚠️ Tidak ada file data. Silakan upload file Excel.")

# Tombol reload data
if st.sidebar.button("🔄 Reload Data"):
    if st.session_state.current_data_file:
        st.cache_data.clear()
        st.success("Data di-refresh ✨")
        st.rerun()
    else:
        st.warning("Tidak ada file data untuk di-refresh")
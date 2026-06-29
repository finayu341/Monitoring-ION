import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
from data_loader import DataLoader
import os
import tempfile

# Import semua view
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

# Session state untuk menyimpan path file yang di-upload
if 'current_data_file' not in st.session_state:
    # File default jika belum ada upload
    if os.path.exists('data_kotor.xlsx'):
        st.session_state.current_data_file = 'data_kotor.xlsx'
    else:
        st.session_state.current_data_file = None

# Fungsi untuk handle upload file
def handle_file_upload():
    uploaded_file = st.sidebar.file_uploader(
        "📤 Upload File Excel", 
        type=['xlsx', 'xls'],
        help="Upload file Excel dengan data gangguan"
    )
    
    if uploaded_file is not None:
        try:
            # Simpan file ke temporary directory
            with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp_file:
                tmp_file.write(uploaded_file.getvalue())
                tmp_path = tmp_file.name
            
            # Update session state dengan path file baru
            st.session_state.current_data_file = tmp_path
            st.session_state.file_name = uploaded_file.name
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

# Upload file
file_uploaded = handle_file_upload()

# Info file yang sedang digunakan
if st.session_state.current_data_file:
    file_name = st.session_state.get('file_name', os.path.basename(st.session_state.current_data_file))
    st.sidebar.markdown(f"""
    <div class="upload-info">
    <strong>📁 File Aktif:</strong><br>
    {file_name}<br>
    <small>{'File upload' if file_uploaded else 'File default'}</small>
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
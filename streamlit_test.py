import streamlit as st
import pandas as pd
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
import json
from io import BytesIO

st.title("🔗 Gabungkan Beberapa File JSON Menjadi Satu")

# 1. Upload beberapa file JSON
uploaded_files = st.file_uploader("Upload beberapa file JSON", type="json", accept_multiple_files=True)

if uploaded_files:
    combined_data = []

    for uploaded_file in uploaded_files:
        try:
            data = json.load(uploaded_file)
            if isinstance(data, dict):
                # Kalau JSON format dict numerik {"0": {...}, "1": {...}} → ubah ke list
                data = list(data.values())
            elif not isinstance(data, list):
                st.warning(f"Format file {uploaded_file.name} tidak dikenali, dilewati.")
                continue

            combined_data.extend(data)
            st.success(f"✅ Berhasil membaca: {uploaded_file.name} ({len(data)} entri)")
        except Exception as e:
            st.error(f"❌ Gagal membaca file {uploaded_file.name}: {e}")

    # 2. Tampilkan hasil gabungan sementara
    if combined_data:
        df = pd.DataFrame(combined_data)
        st.write("📝 Preview Gabungan Data:", df)

        # 3. Tombol download JSON gabungan
        json_str = json.dumps(combined_data, ensure_ascii=False, indent=2)
        json_bytes = BytesIO(json_str.encode("utf-8"))

        st.download_button(
            label="📥 Download Gabungan JSON",
            data=json_bytes,
            file_name="data_putusan_mk_gabungan.json",
            mime="application/json"
        )
    else:
        st.warning("⚠️ Tidak ada data valid untuk digabungkan.")


# Data contoh
data = {
    "Nama": ["Peraturan A", "Peraturan B", "Peraturan C", "Peraturan D", "Peraturan E"],
    "Jenis": ["UU", "PP", "Permen", "UU", "PP"],
    "Tahun": [2021, 2019, 2023, 2020, 2018],
    "Deskripsi": [
        "Detail tentang Peraturan A.",
        "Detail tentang Peraturan B.",
        "Detail tentang Peraturan C.",
        "Detail tentang Peraturan D.",
        "Detail tentang Peraturan E."
    ]
}
df = pd.DataFrame(data)

# 🔹 Urutkan 'Jenis' secara default ("UU" → "PP" → "Permen")
custom_order = ["UU", "PP", "Permen"]
df["Jenis"] = pd.Categorical(df["Jenis"], categories=custom_order, ordered=True)
df = df.sort_values("Jenis")  # Urutkan berdasarkan kategori custom

# 🔹 Toggle (Semua default `False`)
toggle_filter = st.toggle("Aktifkan Filter?", value=False)
toggle_sort = st.toggle("Aktifkan Sorting?", value=False)

if toggle_filter:
    jenis_filter = st.multiselect("Filter Jenis Peraturan:", options=df["Jenis"].unique(), default=df["Jenis"].unique())
else:
    jenis_filter = df["Jenis"].unique()

if toggle_sort:
    sort_option = st.selectbox("Urutkan berdasarkan:", ["Nama", "Jenis", "Tahun"])
    sort_order = st.radio("Urutan:", ["Ascending", "Descending"])
else:
    sort_option, sort_order = None, None

# 🔹 **Filter Data**
filtered_df = df[df["Jenis"].isin(jenis_filter)] if toggle_filter else df.copy()

# 🔹 **Sorting dengan Urutan Kustom (Hanya jika toggle_sort True)**
if toggle_sort:
    filtered_df["Jenis"] = pd.Categorical(filtered_df["Jenis"], categories=custom_order, ordered=True)
    ascending = True if sort_order == "Ascending" else False
    filtered_df = filtered_df.sort_values(by=sort_option, ascending=ascending)

# 🔹 **CSS untuk Scrollable Table**
st.markdown(
    """
    <style>
        .scroll-container {
            max-height: 300px;
            overflow-y: auto;
            border: 1px solid #ddd;
            padding-right: 10px;
        }
        .header {
            font-weight: bold;
            background-color: #f0f0f0;
            padding: 8px 0;
            border-bottom: 2px solid #ccc;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# 🔹 **Tampilkan Tabel**
st.write("### 📜 Daftar Peraturan:")

# 🔸 **Header Kolom**
col1, col2, col3, col4 = st.columns([3, 2, 2, 3])
with col1:
    st.subheader('Nama')
with col2:
    st.subheader('Jenis')
with col3:
    st.subheader('Tahun')
with col4:
    st.subheader('Aksi')

# 🔹 **Scrollable Table**
st.markdown('<div class="scroll-container">', unsafe_allow_html=True)

# 🔸 **Isi Tabel**
# if toggle_sort or toggle_filter:
for i in range(len(filtered_df)):
    col1, col2, col3, col4 = st.columns([3, 2, 2, 3])
    
    with col1:
        st.write(filtered_df.iloc[i]["Nama"])
    with col2:
        with st.popover(filtered_df.iloc[i]["Jenis"]):
            st.write(filtered_df.iloc[i]["Jenis"])
    with col3:
        st.write(filtered_df.iloc[i]["Tahun"])
    with col4:
        with st.popover("ℹ️ Info"):
            st.write(filtered_df.iloc[i]["Deskripsi"])
# else:
# for i in range(len(df)):
#     col1, col2, col3, col4 = st.columns([3, 2, 2, 3])
#     with col1:
#         st.write(df.iloc[i]["Nama"])
#     with col2:
#         with st.popover(df.iloc[i]["Jenis"]):
#             st.write(df.iloc[i]["Jenis"])
#     with col3:
#         st.write(df.iloc[i]["Tahun"])
#     with col4:
#         with st.popover("ℹ️ Info"):
#             st.write(df.iloc[i]["Deskripsi"])

st.markdown('</div>', unsafe_allow_html=True)  # Tutup div scroll-container

# Contoh data
data = {
    'Nama': [f'Mahasiswa {i}' for i in range(1, 71)],
    'Nilai': [i + 60 for i in range(70)]
}
df = pd.DataFrame(data)

# Konfigurasi dasar
rows_per_page = 10
total_pages = (len(df) - 1) // rows_per_page + 1
max_page_buttons = 3

# Inisialisasi state
if 'current_page' not in st.session_state:
    st.session_state.current_page = 1

# Fungsi untuk update halaman
def go_to_page(p):
    st.session_state.current_page = p

# Data slicing
start_idx = (st.session_state.current_page - 1) * rows_per_page
end_idx = start_idx + rows_per_page
data_page = df[start_idx:end_idx]

# Tampilkan data pakai columns (bebas ganti ke style lain)
for _, row in data_page.iterrows():
    col1, col2 = st.columns([1, 1])
    with col1:
        st.markdown(f"**Nama:** {row['Nama']}")
    with col2:
        st.markdown(f"**Nilai:** {row['Nilai']}")
    st.markdown("---")

col1, col2, col3 = st.columns([1, 2, 1])

with col1:        # Tombol Previous
    st.button(
        "⬅️ Prev",
        on_click=lambda: go_to_page(max(1, st.session_state.current_page - 1)),
        disabled=st.session_state.current_page == 1
    )

with col2:
    # Tombol halaman dinamis
    start_page = max(1, st.session_state.current_page - 1)
    end_page = min(total_pages, start_page + max_page_buttons - 1)

    # Geser window jika kita sudah di halaman terakhir
    if end_page - start_page < max_page_buttons - 1:
        start_page = max(1, end_page - max_page_buttons + 1)

    page_cols = st.columns(max_page_buttons)
    for i, page_num in enumerate(range(start_page, end_page + 1)):
        with page_cols[i]:
            st.button(
                str(page_num),
                on_click=lambda p=page_num: go_to_page(p),
                disabled=(st.session_state.current_page == page_num)
            )

with col3:
    # Tombol Next
    st.button(
        "Next ➡️",
        on_click=lambda: go_to_page(min(total_pages, st.session_state.current_page + 1)),
        disabled=st.session_state.current_page == total_pages
    )

# Judul aplikasi
st.title("Scraping Wikipedia - Serafim")
st.write("Scraping isi dari [Wikipedia: Serafim](https://id.wikipedia.org/wiki/Serafim) dan filter dengan kata kunci.")

# Fungsi untuk scrapping isi paragraf dari Wikipedia
@st.cache_data
def get_paragraphs():
    url = "https://id.wikipedia.org/wiki/Serafim"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")

    paragraphs = soup.find_all(".badge.badge-light-primary.mb-2")
    cleaned_paragraphs = [p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True)]

    return cleaned_paragraphs

# Ambil data
paragraph1 = get_paragraphs()

# Ambil semua kata unik dari paragraf sebagai pilihan filter
words_set = set()
for para in paragraph1:
    for word in para.split():
        if word.isalpha() and len(word) > 3:  # hanya kata alfabetik & > 3 huruf
            words_set.add(word.capitalize())

# Urutkan kata untuk multiselect
sorted_words = sorted(words_set)

# Multiselect UI
selected_keywords = st.multiselect("Pilih kata kunci untuk filter paragraf:", sorted_words)

# Tampilkan hasil
if selected_keywords:
    st.subheader("Hasil Filter:")
    for para in paragraph1:
        if any(keyword.lower() in para.lower() for keyword in selected_keywords):
            st.write(para)
else:
    st.subheader("Semua Paragraf:")
    for para in paragraph1:
        st.write(para)

st.title("Scraping Wikipedia + Filter dengan Checkbox")

# Fungsi untuk ambil paragraf
@st.cache_data
def get_paragraphs():
    url = "https://putusan3.mahkamahagung.go.id/search.html?q=sengketa"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    paragraphs = soup.find_all("p")
    return [p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True)]

paragraph2 = get_paragraphs()

# Checkbox filter
with st.expander("Filter Data"):
    st.subheader("Filter Paragraf Berdasarkan Kata Kunci:")
    show_malaikat = st.checkbox("Malaikat")
    show_tuhan = st.checkbox("Tuhan")
    show_sayap = st.checkbox("Sayap")

# Tampilkan hasil
st.subheader("Hasil Paragraf:")

# Jika ada checkbox dipilih, filter berdasarkan isinya
if show_malaikat or show_tuhan or show_sayap:
    for para in paragraph2:
        if (
            (show_malaikat and "malaikat" in para.lower()) or
            (show_tuhan and "tuhan" in para.lower()) or
            (show_sayap and "sayap" in para.lower())
        ):
            st.write(para)
else:
    # Jika tidak ada filter aktif, tampilkan semua
    for para in paragraph2:
        st.write(para)

def get_paragraphs_with_selenium():
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Mode headless
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument('--no-proxy-server')
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.get("https://peraturan.bpk.go.id/Search?keywords=guru&tentang=&nomor=")

    time.sleep(5)  # Tunggu agar JavaScript selesai memuat

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    driver.quit()

    paragraphs = soup.find_all(class_="badge badge-light-primary mb-2")
    cleaned_paragraphs = [p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True)]
    
    return cleaned_paragraphs

paragraph3 = get_paragraphs_with_selenium()

for para3 in paragraph3:
    st.write(para)


from scraper_manager import (init_driver, get_page_links, cari_di_file_json, simpan_ke_json)
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import streamlit as st
import pandas as pd

@st.cache_data(show_spinner="Mengambil data peraturan...")
def cached_peraturan(start_url, max_pages):
    return scrape_peraturan_website(start_url, max_pages)

def scrape_peraturan_website(start_url, max_pages):
    driver = init_driver()
    visited = set()
    to_visit = [start_url]
    halaman_peraturan = {} # Dictionary untuk menyimpan pasangan {kata: detail}

    try: 
        while to_visit and len(visited) < max_pages:
            url = to_visit.pop(0)
            if url in visited:
                continue
            print(f"Scraping: {url}")
            try:
                driver.get(url)
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".page-link")))
            except Exception as e:
                print(f"Error mengakses {url}: {e}")
                continue

            visited.add(url)
            print(f"Scraped URL: {url}, Status: {driver.title}")

            try:
                card_elements = driver.find_elements(By.CSS_SELECTOR, ".flex-grow-1")
                if not card_elements:
                    print(f"Tidak ada data di {url}, tidak ditandai visited.")
                    continue
                for card in card_elements:
                    try:
                        # Cek dan ambil isi elemen tingkat
                        tingkat = card.find_element(By.CSS_SELECTOR, ".col-lg-8.fw-semibold.fs-5.text-gray-600").text.strip()

                        try:
                            isi_tingkat = card.find_element(By.CSS_SELECTOR, ".card-rounded.bg-primary.bg-opacity-5.p-6.mb-5").text.strip()
                        except:
                            isi_tingkat = tingkat

                        tentang = card.find_element(By.CSS_SELECTOR, ".col-lg-10.fs-2.fw-bold.pe-4").text.strip()
                        # Ambil status dan isi status (jika ada lebih dari satu)
                        try:
                            cari_status = card.find_elements(By.CSS_SELECTOR, ".col-lg-2")
                            status = [s.text.strip() for s in cari_status if s.text.strip()]
                        except:
                            status = []

                        try:
                            cari_isi_status = card.find_elements(By.CSS_SELECTOR, ".col-lg-10")
                            isi_status = [s.text.strip() for s in cari_isi_status if s.text.strip()]
                        except:
                            isi_status = []
                                    
                        pdf = card.find_element(By.CSS_SELECTOR, "a[href$='.pdf']").get_attribute("href")
                        # Simpan jika 'tentang' tidak kosong
                        if tentang:
                            halaman_peraturan[tentang] = (tingkat, isi_tingkat, status, isi_status, pdf)

                    except Exception as e:
                        print(f"Error saat memproses kartu: {e}")
                
            except Exception as e:
                print(f"Error saat mengekstrak data dari {url}: {e}")

            peraturan_links = get_page_links(driver, start_url, ".page-link")
            for link in peraturan_links:
                if link not in visited and link not in to_visit:
                    to_visit.append(link)
    finally:
        driver.quit()

    return halaman_peraturan

# def is_kata_kunci_lokal(q):
#     return any(kw in q.lower() for kw in ["royalti", "musik"])

def tampilkan_peraturan(df_peraturan):
    mapping = {
        r"Undang-undang Dasar": "UUD 1945",
        r"Ketetapan MPR": "TAP MPR",
        r"Undang-undang": "UU",
        r"Peraturan Pemerintah Pengganti Undang-Undang": "Perpu",
        r"Peraturan Pemerintah": "PP",
        r"Peraturan Presiden": "Perpres",
        r"Keputusan Presiden": "Keppres",
        r"Instruksi Presiden": "Inpres",
        r"Peraturan Kementerian": "PERMEN",
        r"Peraturan Menteri": "Permen",
        r"Keputusan Menteri": "Kepmen",
        r"Peraturan Daerah": "Perda",
        r"Peraturan Gubernur": "Pergub"
    }

    def cari_tingkat(kalimat):
        return next((singkat for panjang, singkat in mapping.items() if panjang in kalimat), kalimat)

    df_peraturan["Tingkat"] = df_peraturan["Tingkat"].apply(cari_tingkat)
    semua_kategori = list(mapping.values()) + list(df_peraturan.loc[~df_peraturan["Tingkat"].isin(mapping.values()), "Tingkat"].unique())
    df_peraturan["Tingkat"] = pd.Categorical(df_peraturan["Tingkat"], categories=semua_kategori, ordered=True)
    df_peraturan = df_peraturan.sort_values("Tingkat")  # Urutkan berdasarkan kategori custom

    # # 🔹 Toggle (Semua default `False`)
    toggle_filter = st.toggle("Aktifkan Filter?", value=False)

    if toggle_filter:
        tingkat_filter = st.multiselect("Filter Jenis Peraturan:", options=semua_kategori, default=df_peraturan["Tingkat"].unique())
    else:
        tingkat_filter = df_peraturan["Tingkat"].unique()

    # # 🔹 **Filter Data**
    filtered_df_peraturan = df_peraturan[df_peraturan["Tingkat"].isin(tingkat_filter)] if toggle_filter else df_peraturan.copy()
    
    st.subheader("Data peraturan yang ditemukan:")
    # 🔸 **Header Kolom**
    col1, col2, col3, col4 = st.columns([2, 3, 2, 2])
    with col1:
        st.subheader('Tingkat')
    with col2:
        st.subheader('Tentang')
    with col3:
        st.subheader('Status')
    with col4:
        st.subheader('Dokumen')

    st.markdown('</div>', unsafe_allow_html=True)

    for i in range(len(filtered_df_peraturan)):
        col1, col2, col3, col4 = st.columns([2, 3, 2, 2])
        
        with col1:
            with st.popover(str(filtered_df_peraturan.iloc[i]["Tingkat"])):
                st.write(filtered_df_peraturan.iloc[i]["Isi Tingkat"])
        with col2:
            st.write(filtered_df_peraturan.iloc[i]["Tentang"])
        with col3:
            statuses = filtered_df_peraturan.iloc[i]["Status"]
            isi_statuses = filtered_df_peraturan.iloc[i]["Isi Status"]

            if not isinstance(statuses, list):
                statuses = [statuses]
                isi_statuses = [isi_statuses]

            # Filter berdasarkan isi_status yang mengandung "Dicabut dengan" atau "Mencabut"
            filtered_statuses = []
            filtered_isi_statuses = []

            for status, isi in zip(statuses, isi_statuses):
                if "Dicabut dengan" in status or "Mencabut" in status:
                    filtered_statuses.append(status)
                    filtered_isi_statuses.append(isi)
            
            for status, isi in zip(filtered_statuses, filtered_isi_statuses):
                with st.popover(status):
                    st.write(isi)
        with col4:
            pdf_url = filtered_df_peraturan.iloc[i]["PDF"]
            if pdf_url:
                st.markdown(
                    f"""
                    <a href="{pdf_url}" target="_blank">
                        <button style="background-color:#4CAF50;color:white;padding:5px 10px;border:none;border-radius:5px;cursor:pointer;">
                            Download PDF
                        </button>
                    </a>
                    """,
                    unsafe_allow_html=True
                )
            else:
                st.write("Tidak ada PDF")
                
        # 🔹 Tambahkan garis pembatas
        st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# Fungsi scraping spesifik per tingkat
def hasil_scraping_peraturan_spesifik(kalimat, jenis_tingkat):
    # Misalnya: jenis=10 untuk Keppres, jenis=8 untuk PP, dll
    # Kamu bisa buat mapping jika scraping berdasarkan jenis ID
    mapping_jenis_id = {
        "UU": 7,
        "Perpu": 39,
        "PP": 8,
        "Perpres": 214,
        "Keppres": 9,
        "Inpres": 10,
    }

    jenis_id = mapping_jenis_id.get(jenis_tingkat)
    if not jenis_id:
        return pd.DataFrame()

    query = kalimat.replace(" ", "+")
    url = f"https://peraturan.bpk.go.id/Search?keywords={query}&jenis={jenis_id}"
    hasil = cached_peraturan(url, max_pages=20)  # Fungsi scraper kamu

    if hasil:
        return pd.DataFrame([
            {
                "Tingkat": tingkat,
                "Isi Tingkat": isi_tingkat,
                "Tentang": tentang,
                "Status": status,
                "Isi Status": isi_status,
                "PDF": pdf
            }
            for tentang, (tingkat, isi_tingkat, status, isi_status, pdf) in hasil.items()
        ])
    return pd.DataFrame()

def lengkapi_data_tingkat(kalimat, df_sudah_ada):
    tingkat_lengkap = ["UUD 1945", "TAP MPR", "UU", "Perpu", "PP", "Perpres", "Keppres", "Inpres"]
    tingkat_tersedia = df_sudah_ada["Tingkat"].dropna().unique().tolist()
    tingkat_kurang = [t for t in tingkat_lengkap if t not in tingkat_tersedia]

    hasil_scraping_lengkap = []

    for tingkat in tingkat_kurang:
        #st.info(f"🔄 Melengkapi data untuk jenis '{tingkat}'...")

        # Di sini kamu bisa sesuaikan scraping berdasarkan tingkat
        df_scraped = hasil_scraping_peraturan_spesifik(kalimat, tingkat)

        if not df_scraped.empty:
            hasil_scraping_lengkap.append(df_scraped)

    if hasil_scraping_lengkap:
        df_hasil = pd.concat(hasil_scraping_lengkap, ignore_index=True)
        return df_hasil
    return pd.DataFrame()

def hasil_peraturan(kalimat_peraturan):
    if kalimat_peraturan:
        
        peraturan_json = "C:/Users/ASUS/Downloads/data_peraturan_gabungan.json"
        df_peraturan_lokal = cari_di_file_json(kalimat_peraturan, peraturan_json, "Tentang", "Isi Tingkat")
        
        if not df_peraturan_lokal.empty:
            df_lengkap = lengkapi_data_tingkat(kalimat_peraturan, df_peraturan_lokal)

            if not df_lengkap.empty:
                tampilkan_peraturan(df_lengkap)
                simpan_ke_json(df_lengkap, peraturan_json, "Tentang")  
            else:
                tampilkan_peraturan(df_peraturan_lokal)
        else:
            st.session_state["kalimat_perkara"] = kalimat_peraturan
            query_peraturan = kalimat_peraturan.replace(" ", "+")
            peraturan_url = f"https://peraturan.bpk.go.id/Search?keywords={query_peraturan}&tentang=&nomor=&jenis=7&jenis=39&jenis=8&jenis=214&jenis=9&jenis=10&jenis=11&jenis=12&jenis=13&jenis=15&jenis=16" #(semua data : c)
            #peraturan_url = f"https://peraturan.bpk.go.id/Search?keywords={query_peraturan}&tentang=&nomor="
            halaman_peraturan = cached_peraturan(peraturan_url, max_pages=20)
            st.session_state["halaman_peraturan"] = halaman_peraturan               

            if halaman_peraturan:
                df_peraturan = pd.DataFrame([
                    {
                        "Tingkat": tingkat,
                        "Isi Tingkat": isi_tingkat,
                        "Tentang": tentang,
                        "Status": status,
                        "Isi Status": isi_status,
                        "PDF": pdf
                    } 
                    for tentang, (tingkat, isi_tingkat, status, isi_status, pdf) in halaman_peraturan.items()
                ])

                if not df_peraturan.empty:
                    tampilkan_peraturan(df_peraturan)
                    # 💾 Simpan hasil scraping ke file JSON agar cache bertambah
                    simpan_ke_json(df_peraturan, peraturan_json, "Tentang")

            else:
                st.write("Data tidak ditemukan")
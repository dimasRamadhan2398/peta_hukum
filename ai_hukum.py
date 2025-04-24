import streamlit as st
import pandas as pd
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from urllib.parse import urlparse, urljoin

# Konfigurasi Chrome agar berjalan tanpa GUI
chrome_options = Options()
chrome_options.add_argument("--headless")  # Mode headless
chrome_options.add_argument("--disable-gpu")  # Menonaktifkan GPU (untuk stabilitas)
chrome_options.add_argument("--no-sandbox") 
chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

def get_peraturan_page(driver, base_url):
    """Fungsi untuk mengambil semua link internal dari halaman saat ini."""
    page_links = set()
    elements =  driver.find_elements(By.CSS_SELECTOR, ".page-link")
    base_domain = urlparse(base_url).netloc
    for element in elements:
        href = element.get_attribute("href")
        if href:
            parsed_href = urlparse(href)
            # Jika href kosong atau masih di domain yang sama, tambahkan link tersebut
            if parsed_href.netloc == "" or parsed_href.netloc == base_domain:
                full_url = urljoin(base_url, href)
                page_links.add(full_url)
    return page_links

def get_putusan_ma_page(driver, base_url):
    """Fungsi untuk mengambil semua link internal dari halaman saat ini."""
    page_links = set()
    elements = driver.find_elements(By.CSS_SELECTOR, ".page-link")
    base_domain = urlparse(base_url).netloc
    for element in elements:
        href = element.get_attribute("href")
        if href:
            parsed_href = urlparse(href)
            # Jika href kosong atau masih di domain yang sama, tambahkan link tersebut
            if parsed_href.netloc == "" or parsed_href.netloc == base_domain:
                full_url = urljoin(base_url, href)
                page_links.add(full_url)
    return page_links

def get_putusan_mk_page(driver, base_url):
    """Fungsi untuk mengambil semua link internal dari halaman saat ini."""
    page_links = set()
    elements = driver.find_elements(By.CSS_SELECTOR, ".pagination li")
    base_domain = urlparse(base_url).netloc
    for element in elements:
        href = element.get_attribute("href")
        if href:
            parsed_href = urlparse(href)
            # Jika href kosong atau masih di domain yang sama, tambahkan link tersebut
            if parsed_href.netloc == "" or parsed_href.netloc == base_domain:
                full_url = urljoin(base_url, href)
                page_links.add(full_url)
    return page_links

@st.cache_data(show_spinner="Mengambil data dari website...")
def cached_scrape(start_url, max_pages=5):
    return scrape_peraturan_website(start_url, max_pages)

def scrape_peraturan_website(start_url, max_pages=5):
    visited = set()
    to_visit = [start_url]
    halaman_peraturan = {} # Dictionary untuk menyimpan pasangan {kata: detail}

    while to_visit and len(visited) < max_pages:
        url = to_visit.pop(0)
        if url in visited:
            continue
        print(f"Scraping: {url}")
        try:
            driver.get(url)
            time.sleep(1)
        except Exception as e:
            print(f"Error mengakses {url}: {e}")
            continue
        visited.add(url)

        print(f"Scraped URL: {url}, Status: {driver.title}")

        try:
            card_elements = driver.find_elements(By.CSS_SELECTOR, ".flex-grow-1")
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

        new_links = get_peraturan_page(driver, start_url)
        for link in new_links:
            if link not in visited and link not in to_visit:
                to_visit.append(link)

    return halaman_peraturan

# def peraturan_spesifik(nomor_spesifik):
#     query_spesifik = kalimat_perkara.replace(" ", "+")
#     spesifik_url = f"https://peraturan.bpk.go.id/Search?keywords={query_spesifik}&tentang=&nomor=&jenis={nomor_spesifik}"
#     st.session_state["halaman_spesifik"] = cached_scrape(spesifik_url, max_pages=5)
#     halaman_spesifik = st.session_state.get("halaman_spesifik", {})

#     df_spesifik = pd.DataFrame([
#         {
#             "Tingkat": tingkat,
#             "Isi Tingkat": isi_tingkat,
#             "Tentang": tentang,
#             "Status": status,
#             "Isi Status": isi_status,
#             "PDF": pdf
#         } 
#         for tentang, (tingkat, isi_tingkat, status, isi_status, pdf) in halaman_spesifik.items()
#     ])

#     # Gabungkan ke DataFrame utama
#     df_peraturan = pd.concat([df_peraturan, df_spesifik], ignore_index=True)

def scrape_putusan_ma_website(start_url, max_pages=5):
    visited = set()
    to_visit = [start_url]
    halaman_putusan_ma = {} # Dictionary untuk menyimpan pasangan {kata: detail}

    while to_visit and len(visited) < max_pages:
        url = to_visit.pop(0)
        if url in visited:
            continue
        print(f"Scraping: {url}")
        try:
            driver.get(url)
            time.sleep(1)
        except Exception as e:
            print(f"Error mengakses {url}: {e}")
            continue
        visited.add(url)

        print(f"Scraped URL: {url}, Status: {driver.title}")

        try:
            putusan_ma_elements = driver.find_elements(By.CSS_SELECTOR, ".d-inline-block h2")
            detail_ma_elements = driver.find_elements(By.CSS_SELECTOR, ".blog_details p")
            #pdf_elements = driver.find_elements(By.CSS_SELECTOR, ".col-lg-6 a[href$='.pdf']")
            print(f"Putusan MA ditemukan: {[putusan_ma.text for putusan_ma in putusan_ma_elements]}")
            print(f"Detail Putusan MA ditemukan: {[detail_ma.text for detail_ma in detail_ma_elements]}")
            # for pdf_link in pdf_elements:
            #     print(f"PDF ditemukan: {pdf_link.get_attribute('href')}")
            # pdf_urls = [link.get_attribute("href") for link in pdf_elements]

            for putusan_ma, detail_ma in zip(putusan_ma_elements, detail_ma_elements):
                putusan_ma_text = putusan_ma.text.strip()
                detail_ma_text = detail_ma.text.strip()
                if putusan_ma_text:
                    halaman_putusan_ma[putusan_ma_text] = (detail_ma_text)
        except Exception as e:
            print(f"Error saat mengekstrak data dari {url}: {e}")

        new_links = get_putusan_ma_page(driver, start_url)
        for link in new_links:
            if link not in visited and link not in to_visit:
                to_visit.append(link)

    return halaman_putusan_ma

def scrape_putusan_mk_website(start_url, max_pages=10):
    visited = set()
    to_visit = [start_url]
    halaman_putusan_mk = {} # Dictionary untuk menyimpan pasangan {kata: detail}

    while to_visit and len(visited) < max_pages:
        url = to_visit.pop(0)
        if url in visited:
            continue
        print(f"Scraping: {url}")
        try:
            driver.get(url)
            time.sleep(1)
        except Exception as e:
            print(f"Error mengakses {url}: {e}")
            continue
        visited.add(url)

        print(f"Scraped URL: {url}, Status: {driver.title}")

         # Ekstraksi data halaman perturan (sesuaikan selector CSS jika perlu)
        try:
            putusan_mk_elements = driver.find_elements(By.CSS_SELECTOR, ".d-flex.justify-content-between.align-items-center p")
            detail_mk_elements = driver.find_elements(By.CSS_SELECTOR, ".text-primary")
            #pdf_elements = driver.find_elements(By.CSS_SELECTOR, ".col-lg-6 a[href$='.pdf']")
            print(f"Putusan MK ditemukan: {[putusan_mk.text for putusan_mk in putusan_mk_elements]}")
            print(f"Detail Putusan MK ditemukan: {[detail_mk.text for detail_mk in detail_mk_elements]}")
            # for pdf_link in pdf_elements:
            #     print(f"PDF ditemukan: {pdf_link.get_attribute('href')}")
            # pdf_urls = [link.get_attribute("href") for link in pdf_elements]

            for putusan_mk, detail_mk in zip(putusan_mk_elements, detail_mk_elements):
                putusan_mk_text = putusan_mk.text.strip()
                detail_mk_text = detail_mk.text.strip()
                if putusan_mk_text:
                    halaman_putusan_mk[putusan_mk_text] = (detail_mk_text)
        except Exception as e:
            print(f"Error saat mengekstrak data dari {url}: {e}")

        new_links = get_putusan_mk_page(driver, start_url)
        for link in new_links:
            if link not in visited and link not in to_visit:
                to_visit.append(link)

    return halaman_putusan_mk

if __name__ == "__main__":

    st.title("Tools AI Hukum")
    kalimat_perkara = st.text_input("Masukkan perkara")
    #kalimat_perkara = st.text_input("Masukkan perkara", key="kalimat_perkara")
    # st.button("Cari Peraturan & Putusan", on_click=jalankan_scraping)

    # 🔁 Proses pencarian data hanya dilakukan jika tombol ditekan ATAU data sudah ada di session_state
    #if st.button("Cari Peraturan & Putusan"):
    st.button("Cari Peraturan & Putusan")
    st.session_state["kalimat_perkara"] = kalimat_perkara
    peraturan, putusan_ma, putusan_mk = st.tabs(["Peraturan", "Putusan MA", "Putusan MK"])  
    with peraturan:
        if kalimat_perkara:
            query_peraturan = kalimat_perkara.replace(" ", "+")
            peraturan_url = f"https://peraturan.bpk.go.id/Search?keywords={query_peraturan}&tentang=&nomor=&jenis=7&jenis=39&jenis=8&jenis=214&jenis=9&jenis=10&jenis=11&jenis=12&jenis=13&jenis=15&jenis=16"
            st.session_state["halaman_peraturan"] = cached_scrape(peraturan_url, max_pages=10)
            halaman_peraturan = st.session_state.get("halaman_peraturan", {})
        
            if halaman_peraturan:
                st.subheader("Data peraturan yang ditemukan:")
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

                mapping = {
                    r"Undang-undang Dasar": "UUD 1945",
                    r"Ketetapan MPR": "TAP MPR",
                    r"Undang-undang": "UU",
                    r"Peraturan Pemerintah Pengganti Undang-Undang": "Perpu",
                    r"Peraturan Pemerintah": "PP",
                    r"Peraturan Presiden": "Perpres",
                    r"Keputusan Presiden": "Keppres",
                    r"Instruksi Presiden": "Inpres",
                    r"Peraturan Kementerian": "Permen",
                    r"Keputusan Menteri": "Kepmen",
                    r"Peraturan Daerah": "Perda",
                    r"Peraturan Gubernur": "Pergub",
                    r"Peraturan Bupati": "Perbup"
                }

                def cari_tingkat(kalimat):
                    return next((singkat for panjang, singkat in mapping.items() if panjang in kalimat), None)

                df_peraturan["Tingkat"] = df_peraturan["Tingkat"].apply(cari_tingkat)
                df_peraturan["Tingkat"] = pd.Categorical(df_peraturan["Tingkat"], categories=mapping.values(), ordered=True)
                df_peraturan = df_peraturan.sort_values("Tingkat")  # Urutkan berdasarkan kategori custom

                # # 🔹 Toggle (Semua default `False`)
                toggle_filter = st.toggle("Aktifkan Filter?", value=False)

                if toggle_filter:
                    tingkat_filter = st.multiselect("Filter Jenis Peraturan:", options=mapping.values(), default=df_peraturan["Tingkat"].unique())
                else:
                    tingkat_filter = df_peraturan["Tingkat"].unique()

                # if 'Perda' in tingkat_filter:
                #     peraturan_spesifik(19)
                # if 'Pergub'in tingkat_filter:
                #     peraturan_spesifik(20)
                # if 'Perbup' in tingkat_filter:
                #     peraturan_spesifik(23)

                # # 🔹 **Filter Data**
                filtered_df_peraturan = df_peraturan[df_peraturan["Tingkat"].isin(tingkat_filter)] if tingkat_filter else df_peraturan.copy()

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
                            #st.write(filtered_df_peraturan.iloc[i]["PDF"])
                    # 🔹 Tambahkan garis pembatas
                    st.markdown("<hr>", unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.write("Tidak ada data peraturan yang ditemukan.")

    with putusan_ma:
        if kalimat_perkara:
            #query_putusan_ma = urlencode({"keyword": kalimat_perkara})
            query_putusan_ma = kalimat_perkara.replace(" ", "+") 
            
            putusan_ma_url = f"https://jdih.mahkamahagung.go.id/search-result?search={query_putusan_ma}&jenis_dokumen=&bentuk_peraturan=&year="

            print("Memulai proses scraping...")  
            halaman_putusan_ma = scrape_putusan_ma_website(putusan_ma_url, max_pages=2) 

            if halaman_putusan_ma:
                st.subheader("Data putusan MA yang ditemukan:")
                df_putusan_ma = pd.DataFrame([
                    {
                        "Putusan MA": putusan_ma,
                        "Detail": detail_ma,
                    } 
                    for putusan_ma, detail_ma in halaman_putusan_ma.items()
                ])
                #st.dataframe(df_putusan_ma)

                st.markdown('<div class="scroll-container">', unsafe_allow_html=True)
                # 🔸 **Header Kolom**
                col1, col2 = st.columns([1, 1])
                with col1:
                    st.subheader('Putusan MA')
                with col2:
                    st.subheader('Detail')

                st.markdown('</div>', unsafe_allow_html=True)

                # 🔹 **Scrollable Table**
                st.markdown('<div class="scroll-container">', unsafe_allow_html=True)

                # 🔸 **Isi Tabel**
                # if toggle_sort or toggle_filter:
                # for i in range(len(filtered_df_putusan_ma)):
                #     col1, col2, col3 = st.columns([3, 2, 2])
                    
                #     with col1:
                #         with st.popover(str(filtered_df_putusan_ma.iloc[i]["Tingkat"])):
                #             st.write(filtered_df_putusan_ma.iloc[i]["Isi Tingkat"])
                #     with col2:
                #         st.write(filtered_df_putusan_ma.iloc[i]["Tentang"])
                #     with col3:
                #         st.write(filtered_df_putusan_ma.iloc[i]["Isi Status"])
                    
                # else:
                for i in range(len(df_putusan_ma)):
                    col1, col2, = st.columns([1, 1])
                    with col1:
                        st.write(df_putusan_ma.iloc[i]["Putusan MA"])
                    with col2:
                        st.write(df_putusan_ma.iloc[i]["Detail"])

                st.markdown('</div>', unsafe_allow_html=True)
                #st.dataframe(df_peraturan, column_config={"PDF": st.column_config.LinkColumn("PDF Link")})
                #create_clickable_df(df_peraturan)
            else:
                st.write("Tidak ada data putusan MA yang ditemukan.")

    with putusan_mk:
        if kalimat_perkara:
            #query_putusan_mk = urlencode({"keyword": kalimat_perkara})
            query_putusan_mk = kalimat_perkara.replace(" ", "+")
            putusan_mk_url = f"https://jdih.mkri.id/dokumen/index?DokumenSearch%5Bjudul%5D={query_putusan_mk}"

            print("Memulai proses scraping...")
            halaman_putusan_mk = scrape_putusan_mk_website(putusan_mk_url, max_pages=2)

            if halaman_putusan_mk:
                st.subheader("Data putusan MK yang ditemukan:")
                df_putusan_mk = pd.DataFrame([
                    {
                        "Putusan MK": putusan_mk,
                        "Detail": detail_mk,
                    } 
                    for putusan_mk, detail_mk in halaman_putusan_mk.items()
                ])
                #st.dataframe(df_putusan_mk)
                st.markdown('<div class="scroll-container">', unsafe_allow_html=True)
                # 🔸 **Header Kolom**
                col1, col2 = st.columns([1, 1])
                with col1:
                    st.subheader('Putusan MK')
                with col2:
                    st.subheader('Detail')

                st.markdown('</div>', unsafe_allow_html=True)

                # 🔹 **Scrollable Table**
                st.markdown('<div class="scroll-container">', unsafe_allow_html=True)

                # 🔸 **Isi Tabel**
                # if toggle_sort or toggle_filter:
                # for i in range(len(filtered_df_putusan_mk)):
                #     col1, col2, col3 = st.columns([3, 2, 2])
                    
                #     with col1:
                #         with st.popover(str(filtered_df_putusan_mk.iloc[i]["Tingkat"])):
                #             st.write(filtered_df_putusan_mk.iloc[i]["Isi Tingkat"])
                #     with col2:
                #         st.write(filtered_df_putusan_mk.iloc[i]["Tentang"])
                #     with col3:
                #         st.write(filtered_df_putusan_mk.iloc[i]["Isi Status"])
                    
                # else:
                for i in range(len(df_putusan_mk)):
                    col1, col2 = st.columns([1, 1])
                    with col1:
                        st.write(df_putusan_mk.iloc[i]["Putusan MK"])
                    with col2:
                        st.write(df_putusan_mk.iloc[i]["Detail"])

                st.markdown('</div>', unsafe_allow_html=True)
                #st.dataframe(df_peraturan, column_config={"PDF": st.column_config.LinkColumn("PDF Link")})
                #create_clickable_df(df_peraturan)
            else:
                st.write("Tidak ada data putusan MK yang ditemukan.")
driver.quit()

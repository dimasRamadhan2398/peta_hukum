import streamlit as st
import pandas as pd
import time
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from urllib.parse import urlparse, urljoin


# Konfigurasi Chrome agar berjalan tanpa GUI
def init_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Mode headless
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument('--no-proxy-server')
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    service = Service("C:/Users/ASUS/Downloads/chromedriver-win64/chromedriver-win64/chromedriver.exe")
    driver = webdriver.Chrome(service=service, options=chrome_options)

    return driver

def get_page_links(driver, base_url, links):
    page_links = set()
    try:
        elements =  driver.find_elements(By.CSS_SELECTOR, links)
    except Exception as e:
        print(f"Error saat mengambil elemen: {e}")
        return set()
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

@st.cache_data
def cached_peraturan(start_url, max_pages=3):
    return scrape_peraturan_website(start_url, max_pages)

def scrape_peraturan_website(start_url, max_pages=3):
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

            peraturan_links = get_page_links(driver, start_url, ".page-link")
            for link in peraturan_links:
                if link not in visited and link not in to_visit:
                    to_visit.append(link)
    finally:
        driver.quit()

    return halaman_peraturan

def get_pdf_link_from_detail_page(driver):
    pdf_link = None
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".portfolio-meta.nobottommargin"))
        )
        pdf_elements = driver.find_elements(By.CSS_SELECTOR, ".portfolio-meta.nobottommargin a")
        for el in pdf_elements:
            href = el.get_attribute("href")
            if href and "/pdf/" in href:
                pdf_link = href
                break
    except Exception as e:
        print("Gagal mendapatkan link PDF:", e)
    return pdf_link

@st.cache_data
def cached_putusan_ma(start_url, max_pages=3):
    return scrape_putusan_ma_website(start_url, max_pages)

def scrape_putusan_ma_website(start_url, max_pages=3):
    driver = init_driver()
    visited = set()
    to_visit = [start_url]
    halaman_putusan_ma = {} # Dictionary untuk menyimpan pasangan {kata: detail}
    
    try:
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
                card_elements = driver.find_elements(By.CSS_SELECTOR, '.entry-c')
                for card in card_elements:
                    try:
                        judul_putusan_ma = card.find_element(By.XPATH, './/strong/a').text.strip()
                        print("Judul MA ditemukan :", judul_putusan_ma)
                        detail_putusan_ma = card.find_element(By.CSS_SELECTOR, ".nobottommargin").text.strip()
                        print("Detail MA ditemukan", detail_putusan_ma)

                        detail_link = card.find_element(By.XPATH, './/strong/a').get_attribute("href")
                        driver.get(detail_link)
                        time.sleep(1)

                        pdf_putusan_ma = get_pdf_link_from_detail_page(driver)
                        print("Link PDF ditemukan:", pdf_putusan_ma if pdf_putusan_ma else "Tidak ada PDF")

                        if judul_putusan_ma:
                            halaman_putusan_ma[judul_putusan_ma] = (detail_putusan_ma, pdf_putusan_ma)

                        driver.back()
                        time.sleep(1)

                    except Exception as e:
                        print(f"Error saat memproses kartu: {e}")
                
            except Exception as e:
                print(f"Error saat mengekstrak data dari {url}: {e}")

            putusan_ma_links = get_page_links(driver, start_url, ".page-link")
            for link in  putusan_ma_links:
                if link not in visited and link not in to_visit:
                    to_visit.append(link)
    finally:
        driver.quit()

    return halaman_putusan_ma


@st.cache_data
def cached_putusan_mk(start_url, max_pages=3):
    return scrape_putusan_mk_website(start_url, max_pages)

def scrape_putusan_mk_website(start_url, max_pages=3):
    driver = init_driver()
    visited = set()
    to_visit = [start_url]
    halaman_putusan_mk = {} # Dictionary untuk menyimpan pasangan {kata: detail}

    try:
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
                card_elements = driver.find_elements(By.CSS_SELECTOR, ".content-persidangan-isi")
                for card in card_elements:
                    try:
                        nomor_putusan_mk = ""
                        pokok_perkara_mk = ""
                        amar_putusan_mk = ""
                        status_putusan_mk = ""
                        pdf_putusan_mk = ""

                        baris_data = card.find_elements(By.XPATH, "./div")  # Ambil semua <div> langsung di bawah .content-persidangan-isi

                        for baris in baris_data:
                            kolom = baris.find_elements(By.XPATH, "./div")  # Ambil 3 <div> dalam setiap baris
                            if len(kolom) >= 3:
                                label = kolom[0].text.strip()
                                nilai = kolom[2].text.strip()

                                if label == "Nomor":
                                    nomor_putusan_mk = nilai
                                elif label == "Pokok Perkara":
                                    pokok_perkara_mk = nilai
                                elif label == "Amar Putusan":
                                    amar_putusan_mk = nilai
                                elif label == "Status":
                                    status_putusan_mk = nilai
                                elif label == "File Pendukung":
                                    try:
                                        a_tag = kolom[2].find_element(By.TAG_NAME, "a")
                                        href = a_tag.get_attribute("href")
                                        pdf_putusan_mk = urljoin(driver.current_url, href)
                                    except:
                                        pdf_putusan_mk = ""
            
                        if pokok_perkara_mk:
                            halaman_putusan_mk[pokok_perkara_mk] = (nomor_putusan_mk, amar_putusan_mk, status_putusan_mk, pdf_putusan_mk)

                    except Exception as e:
                        print(f"Error saat memproses kartu: {e}")
                
            except Exception as e:
                print(f"Error saat mengekstrak data dari {url}: {e}")

            finally:
                driver.quit()

            putusan_mk_links = get_page_links(driver, start_url, ".pager2 a")
            for link in putusan_mk_links:
                if link not in visited and link not in to_visit:
                    to_visit.append(link)
    finally:
        driver.quit()

    return halaman_putusan_mk

if __name__ == "__main__":

    st.title("Tools AI Hukum")
    kalimat_perkara = st.text_input("Masukkan perkara")
    # Inisialisasi session_state jika belum ada
    cari = st.button("Cari Peraturan & Putusan")
    peraturan, putusan_ma, putusan_mk = st.tabs(["Peraturan", "Putusan MA", "Putusan MK"])  
    with peraturan:
        if cari and kalimat_perkara:
            st.session_state["kalimat_perkara"] = kalimat_perkara
            query_peraturan = kalimat_perkara.replace(" ", "+")
            peraturan_url = f"https://peraturan.bpk.go.id/Search?keywords={query_peraturan}&tentang=&nomor=&jenis=7&jenis=39&jenis=8&jenis=214&jenis=9&jenis=10&jenis=11&jenis=12&jenis=13&jenis=15&jenis=16"
            with st.spinner("Mengambil data peraturan..."):
                halaman_peraturan = cached_peraturan(peraturan_url, max_pages=3)
                st.session_state["halaman_peraturan"] = halaman_peraturan               

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

                # Download sebagai JSON
                json_data = filtered_df_peraturan.to_json(orient="records", force_ascii=False)
                st.download_button(
                    label="Download sebagai JSON",
                    data=json_data,
                    file_name='data_peraturan_bpk.json',
                    mime='application/json',
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
                            
                    # 🔹 Tambahkan garis pembatas
                    st.markdown("<hr>", unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.write("Tidak ada data peraturan yang ditemukan.")
                st.warning("Tidak ada hasil dari peraturan — mungkin koneksi lambat atau situs sedang error.")
        else:
            halaman_peraturan = st.session_state.get("halaman_peraturan", {})
            
    with putusan_ma:
        if cari and kalimat_perkara:
            query_putusan_ma = kalimat_perkara.replace(" ", "+") 
            putusan_ma_url = f"https://putusan3.mahkamahagung.go.id/search.html?q={query_putusan_ma}"
            with st.spinner("Mengambil data Putusan MA..."):
                halaman_putusan_ma = cached_putusan_ma(putusan_ma_url, max_pages=3)
                st.session_state["halaman_putusan_ma"] = halaman_putusan_ma 
                
            if halaman_putusan_ma:
                st.subheader("Data putusan MA yang ditemukan:")
                df_putusan_ma = pd.DataFrame([
                    {
                        "Putusan MA": judul_putusan_ma,
                        "Detail": detail_putusan_ma,
                        "Dokumen": pdf_putusan_ma
                    } 
                    for judul_putusan_ma, (detail_putusan_ma, pdf_putusan_ma) in halaman_putusan_ma.items()
                ])
                #st.dataframe(df_putusan_ma)

                st.markdown('<div class="scroll-container">', unsafe_allow_html=True)
                # 🔸 **Header Kolom**
                col1, col2, col3 = st.columns([1, 1, 1])
                with col1:
                    st.subheader('Putusan MA')
                with col2:
                    st.subheader('Detail')
                with col3:
                    st.subheader('Dokumen')

                st.markdown('</div>', unsafe_allow_html=True)

                # 🔹 **Scrollable Table**
                st.markdown('<div class="scroll-container">', unsafe_allow_html=True)

                for i in range(len(df_putusan_ma)):
                    col1, col2, col3 = st.columns([1, 1, 1])
                    with col1:
                        st.write(df_putusan_ma.iloc[i]["Putusan MA"])
                    with col2:
                        st.write(df_putusan_ma.iloc[i]["Detail"])
                    with col3:
                        pdf_url = df_putusan_ma.iloc[i]["Dokumen"]
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
                    st.markdown("<hr>", unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.write("Tidak ada data putusan MA yang ditemukan.")
                st.warning("Tidak ada hasil dari putusan MA — mungkin koneksi lambat atau situs sedang error.")
        else:
            halaman_putusan_ma = st.session_state.get("halaman_putusan_ma", {})

    with putusan_mk:
        if cari and kalimat_perkara:
            query_putusan_mk = kalimat_perkara.replace(" ", "+")
            putusan_mk_url = f"https://www.mkri.id/index.php?page=web.Putusan&id=1&kat=5&cari={query_putusan_mk}"
            with st.spinner("Mengambil data peraturan..."):
                halaman_putusan_mk = cached_putusan_mk(putusan_mk_url, max_pages=3)
                st.session_state["halaman_putusan_mk"] = halaman_putusan_mk

            if halaman_putusan_mk:
                st.subheader("Data putusan MK yang ditemukan:")
                df_putusan_mk = pd.DataFrame([
                    {
                        "Nomor": nomor_putusan_mk,
                        "Pokok Perkara": pokok_perkara_mk,
                        "Amar": amar_putusan_mk,
                        "Status": status_putusan_mk,
                        "Dokumen": pdf_putusan_mk
                    } 
                    for pokok_perkara_mk, (nomor_putusan_mk, amar_putusan_mk, status_putusan_mk, pdf_putusan_mk) in halaman_putusan_mk.items()
                ])
                #st.dataframe(df_putusan_mk)
                st.markdown('<div class="scroll-container">', unsafe_allow_html=True)
                # 🔸 **Header Kolom**
                col1, col2, col3, col4, col5 = st.columns([1, 1, 1, 1, 1])
                with col1:
                    st.subheader('Nomor')
                with col2:
                    st.subheader('Pokok Perkara')
                with col3:
                    st.subheader('Amar')
                with col4:
                    st.subheader('Status')
                with col5:
                    st.subheader('Dokumen')

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
                    col1, col2, col3, col4, col5 = st.columns([1, 1, 1, 1, 1])
                    with col1:
                        st.write(df_putusan_mk.iloc[i]["Nomor"])
                    with col2:
                        st.write(df_putusan_mk.iloc[i]["Pokok Perkara"])
                    with col3:
                        st.write(df_putusan_mk.iloc[i]["Amar"])
                    with col4:
                        st.write(df_putusan_mk.iloc[i]["Status"])
                    with col5:
                        pdf_url = df_putusan_mk.iloc[i]["Dokumen"]
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
                    st.markdown('</div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
                #st.dataframe(df_peraturan, column_config={"PDF": st.column_config.LinkColumn("PDF Link")})
                #create_clickable_df(df_peraturan)
            else:
                st.write("Tidak ada data putusan MK yang ditemukan.")
                st.warning("Tidak ada hasil dari MK — mungkin koneksi lambat atau situs sedang error.")
        else:
            halaman_putusan_mk = st.session_state.get("halaman_putusan_mk", {})

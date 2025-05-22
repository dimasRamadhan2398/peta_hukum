from scraper_manager import (init_driver, get_page_links, cari_di_file_json, simpan_ke_json)
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from urllib.parse import urljoin
import streamlit as st
import pandas as pd

@st.cache_data(show_spinner="Mengambil data Putusan MK...")
def cached_putusan_mk(start_url, max_pages):
    return scrape_putusan_mk_website(start_url, max_pages)

def scrape_putusan_mk_website(start_url, max_pages):
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
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".pager2 a")))
            except Exception as e:
                print(f"Error mengakses {url}: {e}")
                continue
            visited.add(url)

            print(f"Scraped URL: {url}, Status: {driver.title}")

            try:
                card_elements = driver.find_elements(By.CSS_SELECTOR, ".content-persidangan-isi")
                if not card_elements:
                    print(f"Tidak ada data di {url}, tidak ditandai visited.")
                    continue
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

def tampilkan_putusan_mk(df_putusan_mk):
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

    for i in range(len(df_putusan_mk)):
        col1, col2, col3, col4, col5 = st.columns([1, 1, 1, 1, 1])
        with col1:
            st.write(df_putusan_mk.iloc[i]["Nomor"])
        with col2:
            st.write(df_putusan_mk.iloc[i]["Pokok Perkara"])
        with col3:
            with st.popover(df_putusan_mk.iloc[i]["Status"]):
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

def hasil_putusan_mk(kalimat_putusan_mk):

    putusan_mk_json = "C:/Users/ASUS/Downloads/data_putusan_mk_gabungan.json"
    df_putusan_mk_lokal = cari_di_file_json(kalimat_putusan_mk, putusan_mk_json, "Pokok Perkara", "Pokok Perkara")
    
    if not df_putusan_mk_lokal.empty:
        tampilkan_putusan_mk(df_putusan_mk_lokal)
    else:
        st.session_state["kalimat_perkara"] = kalimat_putusan_mk
        query_putusan_mk = kalimat_putusan_mk.replace(" ", "+") 
        putusan_mk_url = f"https://www.mkri.id/index.php?page=web.Putusan&id=1&kat=2&cari={query_putusan_mk}" #(semua data : c)
        halaman_putusan_mk = cached_putusan_mk(putusan_mk_url, max_pages=20)
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

            st.markdown('<div class="scroll-container">', unsafe_allow_html=True)

            if not df_putusan_mk.empty:
                tampilkan_putusan_mk(df_putusan_mk)
                simpan_ke_json(df_putusan_mk, putusan_mk_json, "Pokok Perkara")
            
        else:
            st.write("Tidak ada data putusan MK yang ditemukan.")
            st.warning("Tidak ada hasil dari MK — mungkin koneksi lambat atau situs sedang error.")

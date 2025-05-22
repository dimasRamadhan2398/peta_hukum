from scraper_manager import (init_driver, get_page_links, cari_di_file_json, simpan_ke_json)
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import streamlit as st
import pandas as pd

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

@st.cache_data(show_spinner="Mengambil data Putusan MA...")
def cached_putusan_ma(start_url, max_pages):
    return scrape_putusan_ma_website(start_url, max_pages)

def scrape_putusan_ma_website(start_url, max_pages):
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
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".page-link")))
            except Exception as e:
                print(f"Error mengakses {url}: {e}")
                continue
            visited.add(url)

            print(f"Scraped URL: {url}, Status: {driver.title}")

            try:
                card_elements = driver.find_elements(By.CSS_SELECTOR, '.entry-c')
                if not card_elements:
                    print(f"Tidak ada data di {url}, tidak ditandai visited.")
                    continue
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

                        if detail_putusan_ma:
                            halaman_putusan_ma[detail_putusan_ma] = (judul_putusan_ma, pdf_putusan_ma)

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

def tampilkan_putusan_ma(df_putusan_ma):
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
            with st.popover("Baca Selengkapnya"):
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

# def is_kata_kunci_lokal(q):
#     return any(kw in q.lower() for kw in ["royalti", "musik"])

def hasil_putusan_ma(kalimat_putusan_ma):
    if kalimat_putusan_ma:

        putusan_ma_json = "C:/Users/ASUS/Downloads/data_putusan_ma_gabungan.json"
        df_putusan_ma_lokal = cari_di_file_json(kalimat_putusan_ma, putusan_ma_json, "Detail", "Detail")

        if not df_putusan_ma_lokal.empty:       
            tampilkan_putusan_ma(df_putusan_ma_lokal)
        else:
            st.session_state["kalimat_perkara"] = kalimat_putusan_ma
            query_putusan_ma = kalimat_putusan_ma.replace(" ", "+") 
            putusan_ma_url = f"https://putusan3.mahkamahagung.go.id/search.html?q={query_putusan_ma}&jenis_doc=putusan" #(Semua data : c)
            #putusan_ma_url = f"https://putusan3.mahkamahagung.go.id/search.html?q={query_putusan_ma}&jenis_doc=putusan&page=131"  #(Data royalti musik)
            halaman_putusan_ma = cached_putusan_ma(putusan_ma_url, max_pages=20)
            st.session_state["halaman_putusan_ma"] = halaman_putusan_ma 
                
            if halaman_putusan_ma:
                st.subheader("Data putusan MA yang ditemukan:")
                df_putusan_ma = pd.DataFrame([
                    {
                        "Putusan MA": judul_putusan_ma,
                        "Detail": detail_putusan_ma,
                        "Dokumen": pdf_putusan_ma
                    } 
                    for detail_putusan_ma, (judul_putusan_ma, pdf_putusan_ma) in halaman_putusan_ma.items()
                ])

                if not df_putusan_ma.empty:
                    tampilkan_putusan_ma(df_putusan_ma)
                    simpan_ke_json(df_putusan_ma, putusan_ma_json, "Detail")

            else:
                st.write("Tidak ada data putusan MA yang ditemukan.")
                st.warning("Tidak ada hasil dari putusan MA — mungkin koneksi lambat atau situs sedang error.")

import streamlit as st
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from fuzzywuzzy import process
from urllib.parse import urlparse, urljoin, urlencode 

# Konfigurasi Chrome agar berjalan tanpa GUI
chrome_options = Options()
chrome_options.add_argument("--headless")  # Mode headless
chrome_options.add_argument("--disable-gpu")  # Menonaktifkan GPU (untuk stabilitas)
chrome_options.add_argument("--window-size=1920x1080")  # Simulasi ukuran layar penuh
chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

def get_jdih_page(driver, base_url):
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

def scrape_website(start_url, max_pages=2):
    """
    Fungsi untuk melakukan scraping pada website mulai dari start_url.
    Mengunjungi hingga max_pages halaman dan mengumpulkan data glossary.
    Asumsikan bahwa setiap halaman memiliki data glossary dalam elemen
    dengan class 'term' (kata) dan 'detail' (deskripsi).
    """
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

         # Ekstraksi data halaman perturan (sesuaikan selector CSS jika perlu)
        try:
            #peraturan_elements = driver.find_elements(By.CSS_SELECTOR, ".col-lg-8")
            judul_elements = driver.find_elements(By.CSS_SELECTOR, ".col-lg-10.fs-2.fw-bold.pe-4")
            detail_elements = driver.find_elements(By.CSS_SELECTOR, ".mb-8")
            print(f"Judul ditemukan: {[judul.text for judul in judul_elements]}")
            print(f"Detail ditemukan: {[detail.text for detail in detail_elements]}")

            for judul, detail in zip(judul_elements, detail_elements):
                #peraturan_text = peraturan.text.strip()
                judul_text = judul.text.strip()
                detail_text = detail.text.strip()
                if judul_text:
                    halaman_peraturan[judul_text] = detail_text
        except Exception as e:
            print(f"Error saat mengekstrak data dari {url}: {e}")

        new_links = get_jdih_page(driver, start_url)
        for link in new_links:
            if link not in visited and link not in to_visit:
                to_visit.append(link)

    return halaman_peraturan

def cocokkan_kalimat(kalimat, halamana_peraturan, threshold=70):
    """
    Fungsi untuk mencocokkan kata-kata di dalam kalimat dengan
    kata-kata unik yang ada di dictionary glossary menggunakan fuzzy matching.
    Hasil yang memenuhi ambang batas (threshold) akan dikembalikan.
    """
    istilah = list(halamana_peraturan.keys())
    hasil_pencocokkan = {}
    kata_dalam_kalimat = kalimat.split()

    for kata in kata_dalam_kalimat:
        # Mencari kata yang paling mirip dengan masing-masing kata dalam kalimat
        cocok = process.extractOne(kata, istilah)
        if cocok and cocok[1] >= threshold:
            kecocokan_terbaik = cocok[0]
            hasil_pencocokkan[kecocokan_terbaik] = halamana_peraturan[kecocokan_terbaik]

    return hasil_pencocokkan

if __name__ == "__main__":

    st.title("Tools AI Hukum")
    kalimat_perkara = st.text_input("Masukkan perkara")
    
    if st.button("Cari Peraturan"):
        if kalimat_perkara:
            #query = urlencode({"keyword": kalimat_perkara})
            query = kalimat_perkara.replace(" ", "+")
            start_url = f"https://peraturan.bpk.go.id/Search?keywords={query}&tentang=&nomor="

            print("Memulai proses scraping...")
            halaman_peraturan = scrape_website(start_url, max_pages=2)

            if halaman_peraturan:
                st.subheader("Data peraturan perkara yang ditemukan:")
                for judul, detail in halaman_peraturan.items():
                    st.write(f"Judul: {judul}")
                    st.write(f"Detail: {detail}")
                else:
                    st.write("Tidak ada data peraturan yang ditemukan.")

driver.quit()

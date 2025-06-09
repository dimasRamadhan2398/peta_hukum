from urllib.parse import urlparse, urljoin
import pandas as pd
import textwrap
import os
import json
import re

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
        text = element.text.strip()
        if not text.isdigit():
            continue
        if href:
            parsed_href = urlparse(href)
            # Jika href kosong atau masih di domain yang sama, tambahkan link tersebut
            if parsed_href.netloc == "" or parsed_href.netloc == base_domain:
                full_url = urljoin(base_url, href)
                page_links.add(full_url)
    return page_links

def cari_di_file_json(kalimat_perkara, path_json, column):
    try:
        with open(path_json, "r", encoding="utf-8") as f:
            data = json.load(f)
        df = pd.DataFrame(data)
    except:
        return pd.DataFrame()

    query_words = kalimat_perkara.lower().split()
    pattern = r"(?i)" + r"|".join(re.escape(word) for word in query_words)  # regex OR

    return df[df[column].str.lower().str.contains(pattern, na=False)]

def rapihkan_text(isi: str, max_line_width=100):
    # Hapus karakter newline berturut-turut, spasi ekstra, dll.
    isi_bersih = re.sub(r"\s*\n\s*", " ", isi).strip()

    # Pisah berdasarkan titik sebagai akhir kalimat (kecuali untuk singkatan seperti No. atau Tn.)
    kalimat_list = re.split(r'(?<=[a-z0-9])\.(\s+)', isi_bersih)

    # Gabungkan kembali kalimat dan spasi setelah titik
    kalimat_list = ["".join(kalimat_list[i:i+2]) for i in range(0, len(kalimat_list), 2)]

    # Bersihkan spasi dan baris kosong
    kalimat_list = [k.strip() for k in kalimat_list if k.strip()]

    # Format sebagai bullet point (dengan wrap agar tidak panjang horizontalnya)
    hasil = "\n\n".join([f"• {textwrap.fill(kalimat, width=max_line_width)}" for kalimat in kalimat_list])

    return hasil

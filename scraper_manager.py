from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from urllib.parse import urlparse, urljoin
import pandas as pd
import os
import json

def init_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Mode headless
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument('--no-proxy-server')
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    service = Service("chromedriver.exe")
    #service = Service(ChromeDriverManager().install())
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

def cari_di_file_json(kalimat_peraturan, path_json, drop_subset, column):
    if not os.path.exists(path_json):
        return pd.DataFrame()

    with open(path_json, encoding="utf-8") as f:
        data = json.load(f)
    #list_data = list(data.values())
    df_json = pd.DataFrame(data)
    df_json = df_json.drop_duplicates(subset=[drop_subset])
    df_json = df_json[df_json[column].str.contains(kalimat_peraturan, case=False, na=False)]
    return df_json

def simpan_ke_json(df_new, path, drop_subset):
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            existing = json.load(f)
            if isinstance(existing, dict):
                existing = list(existing.values())
    else:
        existing = []

    df_existing = pd.DataFrame(existing)
    combined = pd.concat([df_existing, df_new], ignore_index=True)
    combined = combined.drop_duplicates(drop_subset)  # Hindari duplikat

    with open(path, "w", encoding="utf-8") as f:
        json.dump(combined.to_dict(orient="records"), f, ensure_ascii=False, indent=2)

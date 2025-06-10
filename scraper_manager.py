from urllib.parse import urlparse, urljoin
import pandas as pd
import textwrap
import os
import json
import re

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

def rapihkan_text(teks):
    # Pisahkan berdasarkan titik koma
    potongan = re.split(r';\s*', teks)

    # Bersihkan dan buang potongan kosong
    potongan_bersih = [p.strip().replace('\n', ' ') for p in potongan if p.strip()]

    return potongan_bersih

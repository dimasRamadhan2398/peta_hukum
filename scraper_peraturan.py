from scraper_manager import cari_di_file_json, rapihkan_text
from urllib.parse import urlparse, urljoin
import streamlit as st
import pandas as pd
import time
import re

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
        r"Peraturan Kementerian": "permen",
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
    toggle_filter = st.toggle("Aktifkan Filter?", value=False, key="filter_peraturan")

    if toggle_filter:
        tingkat_filter = st.multiselect("Filter Jenis Peraturan:", options=df_peraturan["Tingkat"].unique(), default=df_peraturan["Tingkat"].unique())
    else:
        tingkat_filter = df_peraturan["Tingkat"].unique()

    # # 🔹 **Filter Data**
    filtered_df_peraturan = df_peraturan[df_peraturan["Tingkat"].isin(tingkat_filter)] if toggle_filter else df_peraturan.copy()

    st.markdown("""
    <style>
    .horizontal-scroll-container {
        display: flex;
        overflow-x: auto;
        gap: 1rem;
        padding-bottom: 1rem;
        margin-bottom: 1rem;
    }
    .peraturan-card {
        flex: 0 0 auto;
        min-width: 300px;
        background-color: #f9f9f9;
        border-radius: 12px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.1);
        padding: 1rem;
    }
    .peraturan-card h4 {
        margin-top: 0;
    }
    </style>
    """, unsafe_allow_html=True)

    st.subheader("📋 Data Peraturan (Geser ke samping 👉 jika di mobile)")

    if df_peraturan.empty:
        st.warning("📭 Data tidak ditemukan.")
        return

    # Buat kontainer scroll horizontal
    st.markdown('<div class="horizontal-scroll-container">', unsafe_allow_html=True)

    for _, row in filtered_df_peraturan.iterrows():
        st.markdown('<div class="peraturan-card">', unsafe_allow_html=True)
        st.markdown(f"<h4>{row['Tentang']}</h4>", unsafe_allow_html=True)
        st.markdown(f"**Tingkat**: {row['Tingkat']}")

        with st.expander("📘 Isi Tingkat"):
            st.markdown(rapihkan_text(row["Isi Tingkat"]))

        with st.expander("Detail Status"):
            for status_item in row["Detail Status"]:
                st.markdown(f"**{status_item['status']}**")
                for isi in status_item["items"]:
                    st.markdown(f"- {isi['Deskripsi Isi Status']}")
                    if isi["PDF Isi Status"]:
                        st.markdown(f"[📄 Unduh PDF]({isi['PDF Isi Status']})")

        if row["PDF"]:
            st.markdown(f"[📥 Unduh Dokumen PDF]({row['PDF']})", unsafe_allow_html=True)
        else:
            st.write("❌ Tidak ada PDF")

        st.markdown('</div>', unsafe_allow_html=True)  # Tutup card

    st.markdown('</div>', unsafe_allow_html=True)
    
def hasil_peraturan(kalimat_peraturan):
    if kalimat_peraturan:
        
        peraturan_json = "data_peraturan_gabungan_baru.json"
        df_peraturan_lokal = cari_di_file_json(kalimat_peraturan, peraturan_json, "Tentang")
        if not df_peraturan_lokal.empty:
            tampilkan_peraturan(df_peraturan_lokal)
        else:
            st.warning("🔍 Data tidak ditemukan.")

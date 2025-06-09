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

    st.subheader("Data Peraturan")

    for _, row in filtered_df_peraturan.iterrows():
        st.markdown(f"<h4>{row['Tentang']}</h4>", unsafe_allow_html=True)
        st.markdown(f"**Tingkat** : {row['Tingkat']}")
        st.markdown(f"{(row["Isi Tingkat"])}")

        with st.expander("Detail Status"):
            for status_item in row["Detail Status"]:
                st.markdown(f"**{status_item['status']}**")
                for isi in status_item["items"]:
                    st.markdown(f"- {isi['Deskripsi Isi Status']}")
                    if isi["PDF Isi Status"]:
                        st.markdown(
                                f"""
                                <a href="{isi["PDF Isi Status"]}" target="_blank" download>
                                    <button style="margin-top:5px;margin-bottom:10px;background-color:#4CAF50;color:white;padding:5px 10px;border:none;border-radius:5px;">
                                        Download PDF
                                    </button>
                                </a>
                                """,
                                unsafe_allow_html=True
                            )
        if row["PDF"]:
            st.markdown(
                f"""
                <a href="{row["PDF"]}" target="_blank" download>
                    <button style="margin-top:5px;margin-bottom:10px;background-color:#4CAF50;color:white;padding:5px 10px;border:none;border-radius:5px;">
                        Download PDF
                    </button>
                </a>
                """,
                unsafe_allow_html=True
            )
        else:
            st.write("❌ Tidak ada PDF")
            
        st.markdown('<hr>', unsafe_allow_html=True)  # Tutup card
    
def hasil_peraturan(kalimat_peraturan):
    if kalimat_peraturan:
        
        peraturan_json = "data_peraturan_gabungan_baru.json"
        df_peraturan_lokal = cari_di_file_json(kalimat_peraturan, peraturan_json, "Tentang")
        if not df_peraturan_lokal.empty:
            tampilkan_peraturan(df_peraturan_lokal)
        else:
            st.warning("🔍 Data tidak ditemukan.")

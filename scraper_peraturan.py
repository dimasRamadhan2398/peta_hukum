from scraper_manager import cari_di_file_json
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
    
    st.subheader("Data peraturan yang ditemukan:")
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
            for status_item in filtered_df_peraturan.iloc[i]["Detail Status"]:
                status_label = status_item["status"]
                with st.popover(status_label):
                    for isi in status_item["items"]:
                        st.markdown(f"**{isi['Deskripsi Isi Status']}**", unsafe_allow_html=True)
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
                        else:
                            st.write("🔍 PDF tidak ditemukan.")

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

def hasil_peraturan(kalimat_peraturan):
    if kalimat_peraturan:
        
        peraturan_json = "C:/Users/Dimas/Downloads/ai_hukum/data_peraturan_gabungan_baru.json"
        df_peraturan_lokal = cari_di_file_json(kalimat_peraturan, peraturan_json, "Tentang")
        if not df_peraturan_lokal.empty:
            tampilkan_peraturan(df_peraturan_lokal)
        else:
            st.warning("🔍 Data tidak ditemukan.")

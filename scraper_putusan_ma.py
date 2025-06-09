from scraper_manager import (cari_di_file_json, rapihkan_text)
import time
import streamlit as st
import pandas as pd
import re

def tampilkan_putusan_ma(df_putusan_ma):

    def extract_year_ma(judul):
        years = re.findall(r'\b(19\d{2}|20\d{2})\b', judul)
        return max(map(int, years)) if years else None

    df_putusan_ma["Tahun"] = df_putusan_ma["Putusan MA"].apply(extract_year_ma)
    df_putusan_ma = df_putusan_ma.sort_values("Tahun", ascending=False, na_position="last")

    # # 🔹 Toggle (Semua default `False`)
    toggle_filter = st.toggle("Aktifkan Filter?", value=False, key="filter_putusan_ma")

    if toggle_filter:
        tahun_options = sorted(df_putusan_ma["Tahun"].dropna().unique(), reverse=True)
        tahun_filter = st.multiselect("Filter Tahun Putusan MA :", options=tahun_options, default=tahun_options)
    else:
        tahun_filter = df_putusan_ma["Tahun"].unique()

    # # 🔹 **Filter Data**
    filtered_df_putusan_ma = df_putusan_ma[df_putusan_ma["Tahun"].isin(tahun_filter)] if toggle_filter else df_putusan_ma.copy()

    st.markdown('<div class="scroll-container">', unsafe_allow_html=True)
    # 🔸 **Header Kolom**
    col1, col2 = st.columns([2, 1])
    with col1:
        st.subheader('Putusan MA')
    with col2:
        st.subheader('Dokumen')

    st.markdown('</div>', unsafe_allow_html=True)

    # 🔹 **Scrollable Table**
    st.markdown('<div class="scroll-container">', unsafe_allow_html=True)

    max_preview_length = 300

    for i in range(len(filtered_df_putusan_ma)):
        col1, col2  = st.columns([2, 1])            
        with col1:
            with st.popover(filtered_df_putusan_ma.iloc[i]["Putusan MA"]):
                full_text = filtered_df_putusan_ma.iloc[i]["Detail"]
                if len(full_text) > max_preview_length:
                    preview_text = full_text[:max_preview_length].rsplit(' ', 1)[0] + "..."
                    st.write(preview_text)
                    with st.expander("Read More"):
                        st.markdown(rapihkan_text(full_text))
                else:
                    st.markdown(rapihkan_text(full_text))
                # with st.popover("Baca Selengkapnya"):
                #     st.markdown(rapihkan_text(filtered_df_putusan_ma.iloc[i]["Detail"])) 
        with col2:
            pdf_url = filtered_df_putusan_ma.iloc[i]["Dokumen"]
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

def hasil_putusan_ma(kalimat_putusan_ma):
    if kalimat_putusan_ma:

        putusan_ma_json = "data_putusan_ma_gabungan_baru.json"
        df_putusan_ma_lokal = cari_di_file_json(kalimat_putusan_ma, putusan_ma_json, "Kata Kunci")
        if not df_putusan_ma_lokal.empty:
            tampilkan_putusan_ma(df_putusan_ma_lokal)
        else:
            st.warning("🔍 Data tidak ditemukan.")

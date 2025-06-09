from scraper_manager import (cari_di_file_json, rapihkan_text)
from urllib.parse import urljoin
import streamlit as st
import pandas as pd
import re

def tampilkan_putusan_mk(df_putusan_mk):

    def extract_year_mk(nomor):
        years = re.findall(r'\b(19\d{2}|20\d{2})\b', nomor)
        return max(map(int, years)) if years else None

    df_putusan_mk["Tahun"] = df_putusan_mk["Nomor"].apply(extract_year_mk)
    df_putusan_mk = df_putusan_mk.sort_values("Tahun", ascending=False, na_position="last")

    # # 🔹 Toggle (Semua default `False`)
    toggle_filter = st.toggle("Aktifkan Filter?", value=False, key="filter_putusan_mk")

    if toggle_filter:
        tahun_options = sorted(df_putusan_mk["Tahun"].dropna().unique(), reverse=True)
        tahun_filter = st.multiselect("Filter Tahun Putusan MK :", options=tahun_options, default=tahun_options)
    else:
        tahun_filter = df_putusan_mk["Tahun"].unique()

    # # 🔹 **Filter Data**
    filtered_df_putusan_mk = df_putusan_mk[df_putusan_mk["Tahun"].isin(tahun_filter)] if toggle_filter else df_putusan_mk.copy()

    # 🔸 **Header Kolom**
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        st.subheader('Nomor')
    with col2:
        st.subheader('Status')
    with col3:
        st.subheader('Dokumen')        

    st.markdown('</div>', unsafe_allow_html=True)

    # 🔹 **Scrollable Table**
    st.markdown('<div class="scroll-container">', unsafe_allow_html=True)

    max_preview_length = 300

    for i in range(len(filtered_df_putusan_mk)):
        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            with st.popover(filtered_df_putusan_mk.iloc[i]["Nomor"]):
                st.write(filtered_df_putusan_mk.iloc[i]["Pokok Perkara"])
        with col2:
            with st.popover(filtered_df_putusan_mk.iloc[i]["Status"]):
                full_text = filtered_df_putusan_mk.iloc[i]["Amar"]
                if len(full_text) > max_preview_length:
                    preview_text = full_text[:max_preview_length].rsplit(' ', 1)[0] + "..."
                    st.write(preview_text)
                    with st.expander("Read More"):
                        st.markdown(rapihkan_text(full_text))
                else:
                    st.markdown(rapihkan_text(full_text))
                # with st.popover("Amar Putusan"):
                #     st.markdown(rapihkan_text(filtered_df_putusan_mk.iloc[i]["Amar"]))  
        with col3:
            pdf_url = filtered_df_putusan_mk.iloc[i]["Dokumen"]
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
    if kalimat_putusan_mk:
        putusan_mk_json = "data_putusan_mk_gabungan_baru.json"
        df_putusan_mk_lokal = cari_di_file_json(kalimat_putusan_mk, putusan_mk_json, "Kata Kunci")
        if not df_putusan_mk_lokal.empty:
            tampilkan_putusan_mk(df_putusan_mk_lokal)             
        else:
            st.warning("🔍 Data tidak ditemukan.")

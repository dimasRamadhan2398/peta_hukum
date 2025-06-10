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

    st.subheader("Data Putusan MK")

    for _, row in filtered_df_putusan_mk.iterrows():
        st.markdown(f"<h4>{row['Pokok Perkara']}</h4>", unsafe_allow_html=True)
        st.markdown(f"**Nomor** : {row['Nomor']}")

        with st.expander(f"**Status** : {row['Status']}"):
            st.markdown(f"**{row['Amar']}**")
                
        if row["Dokumen"]:
            st.markdown(
                f"""
                <a href="{row["Dokumen"]}" target="_blank" download>
                    <button style="margin-top:5px;margin-bottom:10px;background-color:#4CAF50;color:white;padding:5px 10px;border:none;border-radius:5px;">
                        Download PDF
                    </button>
                </a>
                """,
                unsafe_allow_html=True
            )
        else:
            st.write("❌ Tidak ada PDF")
            
        st.markdown('<hr>', unsafe_allow_html=True)

def hasil_putusan_mk(kalimat_putusan_mk):
    if kalimat_putusan_mk:
        putusan_mk_json = "data_putusan_mk_gabungan_baru.json"
        df_putusan_mk_lokal = cari_di_file_json(kalimat_putusan_mk, putusan_mk_json, "Kata Kunci")
        if not df_putusan_mk_lokal.empty:
            tampilkan_putusan_mk(df_putusan_mk_lokal)             
        else:
            st.warning("🔍 Data tidak ditemukan.")

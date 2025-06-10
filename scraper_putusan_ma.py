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

    st.subheader("Data Putusan MA")

    for _, row in filtered_df_putusan_ma.iterrows():
        st.markdown(f"<h4>{row['Putusan MA']}</h4>", unsafe_allow_html=True)
        st.markdown(f"**Tentang** : {row['Kata Kunci']}")

        with st.expander("Detail Putusan"):
            st.markdown(f"**{row['Detail']}**")
                            
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

def hasil_putusan_ma(kalimat_putusan_ma):
    if kalimat_putusan_ma:

        putusan_ma_json = "data_putusan_ma_gabungan_baru.json"
        df_putusan_ma_lokal = cari_di_file_json(kalimat_putusan_ma, putusan_ma_json, "Kata Kunci")
        if not df_putusan_ma_lokal.empty:
            tampilkan_putusan_ma(df_putusan_ma_lokal)
        else:
            st.warning("🔍 Data tidak ditemukan.")

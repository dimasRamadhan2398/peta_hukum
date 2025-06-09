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

    # Deteksi ukuran layar dan simpan ke session_state
    st.markdown("""
        <script>
        const isMobile = window.innerWidth < 768;
        const queryParams = new URLSearchParams(window.location.search);
        queryParams.set("device", isMobile ? "mobile" : "desktop");
        window.history.replaceState(null, null, "?" + queryParams.toString());
        </script>
    """, unsafe_allow_html=True)
    
    device = st.query_params().get("device", ["desktop"])[0]
    is_mobile = device == "mobile"

    # # 🔹 Toggle (Semua default `False`)
    toggle_filter = st.toggle("Aktifkan Filter?", value=False, key="filter_peraturan")

    if toggle_filter:
        tingkat_filter = st.multiselect("Filter Jenis Peraturan:", options=df_peraturan["Tingkat"].unique(), default=df_peraturan["Tingkat"].unique())
    else:
        tingkat_filter = df_peraturan["Tingkat"].unique()

    # # 🔹 **Filter Data**
    filtered_df_peraturan = df_peraturan[df_peraturan["Tingkat"].isin(tingkat_filter)] if toggle_filter else df_peraturan.copy()

    st.subheader("📋 Data peraturan yang ditemukan:")

    for i in range(len(filtered_df_peraturan)):
        row = filtered_df_peraturan.iloc[i]

    if is_mobile:
        st.markdown("### 🔹 Peraturan")
        st.markdown(f"**Tingkat:** {row['Tingkat']}")
        st.markdown(f"**Tentang:** {row['Tentang']}")

        with st.expander("📋 Isi Tingkat"):
            st.markdown(rapihkan_text(row["Isi Tingkat"]))

        with st.expander("📎 Detail Status"):
            for status_item in row["Detail Status"]:
                st.markdown(f"**{status_item['status']}**")
                for isi in status_item["items"]:
                    st.markdown(f"- {isi['Deskripsi Isi Status']}")
                    if isi["PDF Isi Status"]:
                        st.markdown(f"[📄 Unduh PDF]({isi['PDF Isi Status']})")

        if row["PDF"]:
            st.markdown(f"[📥 Unduh Dokumen PDF]({row['PDF']})")
        else:
            st.write("❌ Tidak ada PDF.")

        st.markdown("---")
    else:
        col1, col2, col3, col4 = st.columns([2, 3, 2, 2])
        with col1:
            with st.popover(str(row["Tingkat"])):
                st.markdown(rapihkan_text(row["Isi Tingkat"]))
        with col2:
            st.write(row["Tentang"])
        with col3:
            for status_item in row["Detail Status"]:
                with st.popover(status_item["status"]):
                    for isi in status_item["items"]:
                        st.markdown(f"**{isi['Deskripsi Isi Status']}**")
                        if isi["PDF Isi Status"]:
                            st.markdown(f"[📄 Unduh PDF]({isi['PDF Isi Status']})")
        with col4:
            if row["PDF"]:
                st.markdown(f"[📥 Unduh PDF]({row['PDF']})")
            else:
                st.write("❌ Tidak ada PDF")

        st.markdown("<hr>", unsafe_allow_html=True)

def hasil_peraturan(kalimat_peraturan):
    if kalimat_peraturan:
        
        peraturan_json = "data_peraturan_gabungan_baru.json"
        df_peraturan_lokal = cari_di_file_json(kalimat_peraturan, peraturan_json, "Tentang")
        if not df_peraturan_lokal.empty:
            tampilkan_peraturan(df_peraturan_lokal)
        else:
            st.warning("🔍 Data tidak ditemukan.")

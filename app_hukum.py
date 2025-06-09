import streamlit as st
from scraper_peraturan import hasil_peraturan
from scraper_putusan_ma import hasil_putusan_ma
from scraper_putusan_mk import hasil_putusan_mk

st.title("Tools AI Hukum")
kalimat_perkara = st.text_input("Masukkan perkara")
# Inisialisasi session_state jika belum ada
cari = st.button("Cari Peraturan & Putusan")
peraturan, putusan_ma, putusan_mk = st.tabs(["Peraturan", "Putusan MA", "Putusan MK"])  
with peraturan:
    hasil_peraturan(kalimat_perkara)

with putusan_ma:
    hasil_putusan_ma(kalimat_perkara)

with putusan_mk:
    hasil_putusan_mk(kalimat_perkara)

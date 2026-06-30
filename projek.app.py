import streamlit as st
from datetime import datetime
import pandas as pd
import plotly.graph_objects as go
import time
import requests
from streamlit_lottie import st_lottie

# 1. Konfigurasi Halaman Utama
st.set_page_config(page_title="Kalkulator BMI", page_icon="⚖️", layout="centered")

# Fungsi pembantu untuk mengambil animasi stiker dari web Lottie
def muat_stiker_lottie(url: str):
    try:
        respons = requests.get(url)
        if respons.status_code == 200:
            return respons.json()
    except:
        return None

# Memuat aset stiker animasi bergerak secara online
stiker_kesehatan = muat_stiker_lottie("https://lottiefiles.com")
stiker_sukses = muat_stiker_lottie("https://lottiefiles.com")

# 2. Inisialisasi Penyimpanan Riwayat Data (Session State)
if "riwayat" not in st.session_state:
    st.session_state.riwayat = []

# Fungsi logika kalkulator BMI
def hitung_bmi(berat, tinggi):
    return berat / (tinggi ** 2)

def tentukan_kategori(bmi):
    if bmi < 18.5:
        return "Kekurangan berat badan", "#3498db"  # Biru
    elif 18.5 <= bmi < 25.0:
        return "Berat badan normal", "#2ecc71"      # Hijau
    elif 25.0 <= bmi < 30.0:
        return "Kelebihan berat badan", "#f39c12"  # Oranye
    else:
        return "Obesitas", "#e74c3c"                # Merah

# 3. Tata Letak Header & Stiker Animasi Utama
kolom_judul, kolom_stiker = st.columns([2, 1])
with kolom_judul:
    st.title("⚖️ Kalkulator BMI Sederhana")
    st.write("Pantau indeks massa tubuh idealmu secara berkala lewat diagram tren interaktif!")
with kolom_stiker:
    if stiker_kesehatan:
        st_lottie(stiker_kesehatan, height=130, key="stiker_utama")

st.write("---")

# 4. Form Input Pengguna
kolom_input1, kolom_input2 = st.columns(2)
with kolom_input1:
    berat = st.number_input("Berat badan Anda (kg):", min_value=1.0, value=65.0, step=0.1)
with kolom_input2:
    tinggi_cm = st.number_input("Tinggi badan Anda (cm):", min_value=50.0, value=170.0, step=1.0)

# Tombol Eksekusi Perhitungan
if st.button("🔍 Hitung & Simpan Skor BMI", use_container_width=True):
    if tinggi_cm > 0:
        # Efek animasi memuat (loading bar)
        with st.spinner("Sedang memproses data kesehatan Anda..."):
            bilah_progres = st.progress(0)
            for persen in range(100):
                time.sleep(0.003)
                bilah_progres.progress(persen + 1)
            bilah_progres.empty()

        # Rumus BMI
        tinggi_meter = tinggi_cm / 100
        skor_bmi = hitung_bmi(berat, tinggi_meter)
        kategori, warna_tema = tentukan_kategori(skor_bmi)
        waktu_sekarang = datetime.now().strftime("%d-%m-%Y %H:%M")

        st.balloons()
        
        # Tampilan Hasil beserta Stiker Animasi Centang Sukses
        kolom_hasil, kolom_anim_sukses = st.columns([2, 1])
        with kolom_hasil:
            st.markdown(
                f"""
                <div style="background-color:{warna_tema}; padding:22px; border-radius:12px; text-align:center; color:white; margin-bottom:15px;">
                    <h2 style="margin:0; color:white; font-size:26px;">Skor BMI: {skor_bmi:.2f}</h2>
                    <h3 style="margin:6px 0; color:white; font-weight:bold; font-size:20px;">{kategori}</h3>
                    <p style="margin:0; font-size:13px; opacity:0.85;">🕒 Diperiksa pada: {waktu_sekarang}</p>
                </div>
                """,
                unsafe_allow_html=True
            )
        with kolom_anim_sukses:
            if stiker_sukses:
                st_lottie(stiker_sukses, height=135, key="stiker_berhasil")

        # Memasukkan data pengecekan ke dalam daftar memori
        st.session_state.riwayat.append({
            "Waktu": waktu_sekarang,
            "Berat (kg)": berat,
            "Tinggi (cm)": tinggi_cm,
            "Skor BMI": round(skor_bmi, 2),
            "Kategori": kategori
        })
    else:
        st.error("Masukkan tinggi badan yang valid di atas angka 0!")

# 5. Visualisasi Diagram Garis Tren Berkala
if st.session_state.riwayat:
    st.write("---")
    st.subheader("📈 Diagram Garis Riwayat Tren BMI")
    
    # Konversi list riwayat menjadi struktur data tabel pandas
    tabel_data = pd.DataFrame(st.session_state.riwayat)
    
    # Membuat sumbu X unik gabungan antara urutan indeks ke- dan waktu pengisian
    tabel_data["Label Sumbu X"] = "Pengecekan ke-" + (tabel_data.index + 1).astype(str) + "<br>" + tabel_data["Waktu"]

    # Inisialisasi diagram garis Plotly
    grafik_garis = go.Figure()

    # Konstruksi jalur garis dan titik koordinat nilai BMI
    grafik_garis.add_trace(go.Scatter(
        x=tabel_data["Label Sumbu X"],
        y=tabel_data["Skor BMI"],
        mode="lines+markers+text",
        text=tabel_data["Skor BMI"],
        textposition="top center",
        line=dict(color="#5758bb", width=3, shape="spline"),
        marker=dict(size=11, color="#5758bb", line=dict(width=2, color="white")),
        name="Skor BMI Anda"
    ))

    # Menambahkan garis bantu batas ambang standar kesehatan (Horizontal Lines)
    grafik_garis.add_hline(y=18.5, line_dash="dash", line_color="#3498db", annotation_text="Batas Kurus (18.5)")
    grafik_garis.add_hline(y=25.0, line_dash="dash", line_color="#2ecc71", annotation_text="Batas Normal (25.0)")
    grafik_garis.add_hline(y=30.0, line_dash="dash", line_color="#e74c3c", annotation_text="Mulai Obesitas (30.0)")

    # Konfigurasi gaya tampilan grafik agar rapi
    grafik_garis.update_layout(
        xaxis_title="Garis Waktu Pengambilan Data",
        yaxis_title="Skala Nilai BMI",
        template="plotly_white",
        height=460,
        margin=dict(l=25, r=25, t=35, b=85)
    )

    # Menampilkan grafik ke dalam halaman aplikasi web Streamlit
    st.plotly_chart(grafik_garis, use_container_width=True)

    # Rincian log tabel data mentah
    with st.expander("📂 Buka Dokumen Riwayat Detail (Tabel)"):
        st.dataframe(tabel_data[["Waktu", "Berat (kg)", "Tinggi (cm)", "Skor BMI", "Kategori"]], use_container_width=True)

    # Tombol Penghapusan Sesi Memori
    if st.button("🗑️ Kosongkan Seluruh Riwayat", use_container_width=True):
        st.session_state.riwayat = []
        st.rerun()

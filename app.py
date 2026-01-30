import streamlit as st
import pandas as pd
import plotly.express as px

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(
    page_title="Dashboard Kepatuhan LHKPN",
    layout="wide"
)

st.title("📊 Dashboard Kepatuhan Pelaporan LHKPN")
st.caption("Periode Januari – Maret 2026")

# =========================
# FUNGSI UTIL
# =========================
def normalisasi_kolom(df):
    df.columns = (
        df.columns
        .str.strip()
        .str.upper()
        .str.replace(r"\s+", " ", regex=True)
    )
    return df

def status_lhkpn(row):
    if row["JAN"] == 1:
        return "🟢 Hijau", 100
    elif row["FEB"] == 1:
        return "🟡 Kuning", 75
    elif row["MAR"] == 1:
        return "🔴 Merah", 50
    else:
        return "⚫ Hitam", 0

# =========================
# SIDEBAR - UPLOAD
# =========================
st.sidebar.header("📁 Upload Data LHKPN")

file_jan = st.sidebar.file_uploader("File Januari", type=["xlsx"])
file_feb = st.sidebar.file_uploader("File Februari", type=["xlsx"])
file_mar = st.sidebar.file_uploader("File Maret", type=["xlsx"])

if not (file_jan and file_feb and file_mar):
    st.info("Silakan upload file Januari, Februari, dan Maret")
    st.stop()

# =========================
# LOAD & NORMALISASI DATA
# =========================
df_jan = normalisasi_kolom(pd.read_excel(file_jan))
df_feb = normalisasi_kolom(pd.read_excel(file_feb))
df_mar = normalisasi_kolom(pd.read_excel(file_mar))

# =========================
# DEBUG KOLOM (AMAN DIHAPUS NANTI)
# =========================
st.sidebar.write("Kolom File:", df_jan.columns.tolist())

# =========================
# PENANDA BULAN
# =========================
df_jan["JAN"] = 1
df_feb["FEB"] = 1
df_mar["MAR"] = 1

# =========================
# KOLOM KUNCI (SESUAI FILE LHKPN)
# =========================
kolom_kunci = [
    "NIK",
    "NAMA_WL",
    "SUB UNIT KERJA",
    "UNIT KERJA"
]

# =========================
# VALIDASI KOLOM WAJIB
# =========================
for kolom in kolom_kunci:
    if kolom not in df_jan.columns:
        st.error(f"Kolom '{kolom}' tidak ditemukan di file")
        st.stop()

# =========================
# MERGE DATA
# =========================
df = (
    df_jan[kolom_kunci + ["JAN"]]
    .merge(df_feb[kolom_kunci + ["FEB"]], on=kolom_kunci, how="outer")
    .merge(df_mar[kolom_kunci + ["MAR"]], on=kolom_kunci, how="outer")
)

df[["JAN", "FEB", "MAR"]] = df[["JAN", "FEB", "MAR"]].fillna(0)

# =========================
# STATUS & SKOR
# =========================
df[["STATUS", "SKOR"]] = df.apply(
    lambda r: pd.Series(status_lhkpn(r)),
    axis=1
)

# =========================
# FILTER
# =========================
unit_filter = st.sidebar.multiselect(
    "Filter Unit Kerja",
    sorted(df["UNIT KERJA"].dropna().unique())
)

if unit_filter:
    df = df[df["UNIT KERJA"].isin(unit_filter)]

# =========================
# KPI
# =========================
total = len(df)
hijau = len(df[df["STATUS"] == "🟢 Hijau"])
hitam = len(df[df["STATUS"] == "⚫ Hitam"])

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Wajib Lapor", total)
col2.metric("🟢 Hijau", hijau)
col3.metric("⚫ Belum Lapor", hitam)

kepatuhan = round(((total - hitam) / total) * 100, 2) if total else 0
col4.metric("Tingkat Kepatuhan", f"{kepatuhan} %")

# =========================
# GRAFIK STATUS
# =========================
fig = px.pie(
    df,
    names="STATUS",
    title="Distribusi Status Kepatuhan LHKPN",
    hole=0.4
)
st.plotly_chart(fig, use_container_width=True)

# =========================
# RANKING SUB UNIT
# =========================
ranking_subunit = (
    df.groupby("SUB UNIT KERJA", dropna=False)
    .agg(
        Total_WL=("NIK", "count"),
        Skor_Rata=("SKOR", "mean")
    )
    .sort_values("Skor_Rata", ascending=False)
    .reset_index()
)

st.subheader("🏆 Ranking Sub Unit Kerja")
st.dataframe(ranking_subunit, use_container_width=True)

# =========================
# DATA DETAIL INDIVIDU
# =========================
st.subheader("📋 Data Individu Wajib Lapor")
st.dataframe(
    df.sort_values("SKOR", ascending=False),
    use_container_width=True
)

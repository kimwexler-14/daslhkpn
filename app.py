import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Dashboard Kepatuhan LHKPN",
    layout="wide"
)

st.title("📊 Dashboard Kepatuhan Pelaporan LHKPN")
st.caption("Periode Januari – Maret 2026")

# =========================
# UPLOAD FILE
# =========================
st.sidebar.header("📁 Upload Data")

file_jan = st.sidebar.file_uploader("File Januari", type=["xlsx"])
file_feb = st.sidebar.file_uploader("File Februari", type=["xlsx"])
file_mar = st.sidebar.file_uploader("File Maret", type=["xlsx"])

if not (file_jan and file_feb and file_mar):
    st.info("Silakan upload ketiga file (Jan, Feb, Mar)")
    st.stop()

# =========================
# LOAD DATA
# =========================
df_jan = pd.read_excel(file_jan)
df_feb = pd.read_excel(file_feb)
df_mar = pd.read_excel(file_mar)

df_jan["JAN"] = 1
df_feb["FEB"] = 1
df_mar["MAR"] = 1

kolom_kunci = [
    "NIK", "NAMA", "SUB UNIT KERJA", "UNIT KERJA"
]

df = (
    df_jan[kolom_kunci + ["JAN"]]
    .merge(df_feb[kolom_kunci + ["FEB"]], on=kolom_kunci, how="outer")
    .merge(df_mar[kolom_kunci + ["MAR"]], on=kolom_kunci, how="outer")
)

df[["JAN", "FEB", "MAR"]] = df[["JAN", "FEB", "MAR"]].fillna(0)

# =========================
# STATUS & SKOR
# =========================
def status_lhkpn(row):
    if row["JAN"] == 1:
        return "🟢 Hijau", 100
    elif row["FEB"] == 1:
        return "🟡 Kuning", 75
    elif row["MAR"] == 1:
        return "🔴 Merah", 50
    else:
        return "⚫ Hitam", 0

df[["STATUS", "SKOR"]] = df.apply(
    lambda x: pd.Series(status_lhkpn(x)), axis=1
)

# =========================
# FILTER
# =========================
unit = st.sidebar.multiselect(
    "Filter Unit Kerja",
    df["UNIT KERJA"].unique()
)

if unit:
    df = df[df["UNIT KERJA"].isin(unit)]

# =========================
# KPI
# =========================
col1, col2, col3, col4 = st.columns(4)

total = len(df)
hijau = len(df[df["STATUS"] == "🟢 Hijau"])
hitam = len(df[df["STATUS"] == "⚫ Hitam"])

col1.metric("Total Wajib Lapor", total)
col2.metric("🟢 Hijau", hijau)
col3.metric("⚫ Belum Lapor", hitam)
col4.metric("Tingkat Kepatuhan", f"{round((total-hitam)/total*100,2)} %")

# =========================
# GRAFIK STATUS
# =========================
fig = px.pie(
    df,
    names="STATUS",
    title="Distribusi Status LHKPN",
    hole=0.4
)
st.plotly_chart(fig, use_container_width=True)

# =========================
# RANKING SUB UNIT
# =========================
ranking_subunit = (
    df.groupby("SUB UNIT KERJA")
    .agg(
        Total=("NIK", "count"),
        Skor=("SKOR", "mean")
    )
    .sort_values("Skor", ascending=False)
    .reset_index()
)

st.subheader("🏆 Ranking Sub Unit Kerja")
st.dataframe(ranking_subunit)

# =========================
# DATA DETAIL
# =========================
st.subheader("📋 Data Individu")
st.dataframe(
    df.sort_values("SKOR", ascending=False),
    use_container_width=True
)

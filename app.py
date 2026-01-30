import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide", page_title="DSS Kepatuhan LHKPN")

st.title("📊 Dashboard Kepatuhan LHKPN 2026")
st.subheader("Periode Pelaporan: Januari - Maret")

# --- SIDEBAR: UPLOAD FILE ---
st.sidebar.header("Upload Sumber Data")
file_jan = st.sidebar.file_uploader("Upload Data Januari", type=['csv', 'xlsx'])
file_feb = st.sidebar.file_uploader("Upload Data Februari", type=['csv', 'xlsx'])
file_mar = st.sidebar.file_uploader("Upload Data Maret", type=['csv', 'xlsx'])
file_master = st.sidebar.file_uploader("Upload Master Pegawai (Wajib Lapor)", type=['csv', 'xlsx'])

if file_master and file_jan:
    # Load Data
    df_master = pd.read_excel(file_master) # Asumsi file excel
    df_jan = pd.read_excel(file_jan)
    df_feb = pd.read_excel(file_feb) if file_feb else pd.DataFrame()
    df_mar = pd.read_excel(file_mar) if file_mar else pd.DataFrame()

    # --- LOGIKA KATEGORISASI ---
    def check_status(row):
        nik = row['NIK']
        if nik in df_jan['NIK'].values:
            return 'HIJAU (Januari)'
        elif not df_feb.empty and nik in df_feb['NIK'].values:
            return 'KUNING (Februari)'
        elif not df_mar.empty and nik in df_mar['NIK'].values:
            return 'MERAH (Maret)'
        else:
            return 'HITAM (Belum Lapor)'

    df_master['Status Kepatuhan'] = df_master.apply(check_status, axis=1)

    # --- BAGIAN 1: GLOBAL KPI ---
    col1, col2, col3, col4 = st.columns(4)
    total = len(df_master)
    hijau = len(df_master[df_master['Status Kepatuhan'] == 'HIJAU (Januari)'])
    kuning = len(df_master[df_master['Status Kepatuhan'] == 'KUNING (Februari)'])
    hitam = len(df_master[df_master['Status Kepatuhan'] == 'HITAM (Belum Lapor)'])

    col1.metric("Total Wajib Lapor", total)
    col2.metric("Patuh Awal (Hijau)", hijau)
    col3.metric("Patuh (Kuning)", kuning)
    col4.error(f"Belum Lapor: {hitam}")

    # --- BAGIAN 2: RANKING SUB-UNIT ---
    st.write("### 🏆 Ranking Kepatuhan per Sub-Unit Kerja")
    
    # Hitung persentase patuh per sub-unit
    ranking_dept = df_master.groupby('Sub Unit Kerja').apply(
        lambda x: (x['Status Kepatuhan'] != 'HITAM (Belum Lapor)').sum() / len(x) * 100
    ).reset_index(name='Persentase Kepatuhan')
    
    ranking_dept = ranking_dept.sort_values(by='Persentase Kepatuhan', ascending=False)
    
    fig_rank = px.bar(ranking_dept, x='Persentase Kepatuhan', y='Sub Unit Kerja', orientation='h',
                 color='Persentase Kepatuhan', color_continuous_scale='RdYlGn')
    st.plotly_chart(fig_rank, use_container_width=True)

    # --- BAGIAN 3: DETAIL DATA INDIVIDU ---
    st.write("### 🔍 Detail Status Individu")
    search = st.text_input("Cari Nama atau NIK")
    if search:
        df_master = df_master[df_master['Nama'].str.contains(search, case=False)]

    # Memberi warna pada tabel
    def color_status(val):
        if 'HIJAU' in val: color = '#28a745'
        elif 'KUNING' in val: color = '#ffc107'
        elif 'MERAH' in val: color = '#dc3545'
        else: color = '#000000; color: white'
        return f'background-color: {color}'

    st.dataframe(df_master.style.applymap(color_status, subset=['Status Kepatuhan']), use_container_width=True)

else:
    st.info("Silakan upload minimal File Master Pegawai dan File Januari untuk memulai.")

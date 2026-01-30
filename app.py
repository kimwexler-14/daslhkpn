import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide", page_title="DSS Kepatuhan LHKPN")

# Styling CSS untuk tampilan warna status
st.markdown("""
    <style>
    .status-box { padding: 10px; border-radius: 5px; color: white; text-align: center; font-weight: bold; }
    .hijau { background-color: #28a745; }
    .kuning { background-color: #ffc107; color: black; }
    .merah { background-color: #dc3545; }
    .hitam { background-color: #000000; }
    </style>
    """, unsafe_allow_html=True)

st.title("📊 Dashboard DSS Kepatuhan LHKPN 2026")
st.info("Sistem akan membandingkan data Januari - Maret untuk menentukan kategori kepatuhan.")

# --- SIDEBAR UPLOAD ---
st.sidebar.header("Upload Data Bulanan")
file_jan = st.sidebar.file_uploader("1. File Januari (Basis Data)", type=['xlsx', 'csv'])
file_feb = st.sidebar.file_uploader("2. File Februari", type=['xlsx', 'csv'])
file_mar = st.sidebar.file_uploader("3. File Maret", type=['xlsx', 'csv'])

if file_jan:
    # Membaca data
    df_jan = pd.read_excel(file_jan)
    # Gunakan NIK atau Nama sebagai Key (Sesuaikan dengan nama kolom di file Anda)
    key_col = 'NIK' 
    status_col = 'STATUS_LHKPN' # Contoh nama kolom status di file Anda
    
    # Inisialisasi DataFrame Utama dari file Januari
    df_final = df_jan.copy()
    
    # Fungsi Logika Warna
    def assign_color(row):
        # 1. Cek Januari
        if row[status_col].lower() == 'sudah lapor':
            return 'HIJAU'
        
        # 2. Cek Februari (Jika file diupload)
        if file_feb:
            df_feb = pd.read_excel(file_feb)
            status_feb = df_feb.loc[df_feb[key_col] == row[key_col], status_col].values
            if len(status_feb) > 0 and status_feb[0].lower() == 'sudah lapor':
                return 'KUNING'
        
        # 3. Cek Maret (Jika file diupload)
        if file_mar:
            df_mar = pd.read_excel(file_mar)
            status_mar = df_mar.loc[df_mar[key_col] == row[key_col], status_col].values
            if len(status_mar) > 0 and status_mar[0].lower() == 'sudah lapor':
                return 'MERAH'
        
        return 'HITAM'

    # Eksekusi Kategorisasi
    if st.sidebar.button("Proses Data"):
        df_final['Kategori'] = df_final.apply(assign_color, axis=1)
        
        # --- RINGKASAN ATAS ---
        cols = st.columns(4)
        counts = df_final['Kategori'].value_counts()
        
        cols[0].metric("Sangat Patuh (Jan)", counts.get('HIJAU', 0))
        cols[1].metric("Patuh (Feb)", counts.get('KUNING', 0))
        cols[2].metric("Last Minute (Mar)", counts.get('MERAH', 0))
        cols[3].metric("BELUM LAPOR", counts.get('HITAM', 0), delta_color="inverse")

        # --- RANKING PER SUB-UNIT ---
        st.divider()
        st.subheader("🏆 Ranking Kepatuhan per Sub-Unit Kerja")
        
        # Hitung Persentase Kepatuhan (Hijau+Kuning+Merah) / Total
        df_rank = df_final.groupby('SUB_UNIT').apply(
            lambda x: (x['Kategori'] != 'HITAM').sum() / len(x) * 100
        ).reset_index(name='Persentase')
        df_rank = df_rank.sort_values('Persentase', ascending=False)
        
        fig = px.bar(df_rank, x='Persentase', y='SUB_UNIT', orientation='h', 
                     color='Persentase', color_continuous_scale='RdYlGn',
                     title="Sub-Unit Paling Patuh")
        st.plotly_chart(fig, use_container_width=True)

        # --- TABEL DETAIL ---
        st.subheader("🔍 Detail Data Individu")
        
        # Pewarnaan Tabel
        def color_row(val):
            color = ''
            if val == 'HIJAU': color = 'background-color: #28a745; color: white'
            elif val == 'KUNING': color = 'background-color: #ffc107; color: black'
            elif val == 'MERAH': color = 'background-color: #dc3545; color: white'
            elif val == 'HITAM': color = 'background-color: #000000; color: white'
            return color

        st.dataframe(df_final.style.applymap(color_row, subset=['Kategori']), use_container_width=True)
        
        # Fitur Download Laporan Hasil Olahan
        csv = df_final.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Download Laporan Hasil Ranking (CSV)", csv, "Laporan_Kepatuhan.csv", "text/csv")
else:
    st.warning("Silakan unggah file Januari sebagai basis data utama.")

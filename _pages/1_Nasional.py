import streamlit as st
import pandas as pd
import plotly.express as px
from utils import load_data

st.header("Insight Demografi & Manajemen Risiko (Nasional)")

df = load_data()


# 1. KPI UTAMA (FULL ANGKA)
st.subheader("1. Key Performance Indicators")
col1, col2, col3, col4 = st.columns(4)

total_penerima = df['jumlah_penerima_manfaat'].sum()
total_satpen = df['jumlah_satuan_pendidikan'].sum()
total_kondisi_khusus = df['jumlah_kondisi_khusus'].sum()
total_negeri = df['jumlah_satpen_negeri'].sum()
total_swasta = df['jumlah_satpen_swasta'].sum()

col1.metric("Total Penerima Manfaat", f"{total_penerima:,}")
col2.metric("Total Satuan Pendidikan", f"{total_satpen:,}")
col3.metric("Total Kebutuhan Khusus", f"{total_kondisi_khusus:,}")
col4.metric("Komposisi (Negeri vs Swasta)", f"{total_negeri:,} vs {total_swasta:,}")

st.markdown("---")

# 2. INSIGHT DEMOGRAFI
st.subheader("2. Insight Demografi Penerima Manfaat")
c1, c2 = st.columns(2)

with c1:
    df_gender = df.groupby('jenjang')[['jumlah_laki', 'jumlah_perempuan']].sum().reset_index()
    fig_gender = px.bar(df_gender, x='jenjang', y=['jumlah_laki', 'jumlah_perempuan'], 
                        title="Profil Demografi Berdasarkan Jenjang", barmode='stack')
    st.plotly_chart(fig_gender, use_container_width=True)

with c2:
    df_status = pd.DataFrame({
        'Status': ['Negeri', 'Swasta'],
        'Jumlah': [total_negeri, total_swasta]
    })
    fig_status = px.pie(df_status, names='Status', values='Jumlah', hole=0.5, 
                        title="Status Penerima (Negeri vs Swasta)")
    st.plotly_chart(fig_status, use_container_width=True)

st.markdown("---")

# 3. INSIGHT MANAJEMEN RISIKO
st.subheader("3. Insight Manajemen Risiko")
risiko_cols = ['jumlah_alergi', 'jumlah_fobia', 'jumlah_intoleransi', 'jumlah_kondisi_khusus']
df_risiko_total = pd.DataFrame({
    'Kondisi': risiko_cols,
    'Total': [df[col].sum() for col in risiko_cols]
})

c3, c4 = st.columns(2)
with c3:
    fig_risiko_pie = px.pie(df_risiko_total, names='Kondisi', values='Total', hole=0.4,
                            title="Distribusi Manajemen Risiko")
    st.plotly_chart(fig_risiko_pie, use_container_width=True)

with c4:
    df_risiko_jenjang = df.groupby('jenjang')[risiko_cols].sum().reset_index()
    fig_risiko_bar = px.bar(df_risiko_jenjang, x='jenjang', y=risiko_cols, barmode='stack',
                            title="Risiko Berdasarkan Jenjang Pendidikan")
    st.plotly_chart(fig_risiko_bar, use_container_width=True)

# Treemap and others omitted for brevity

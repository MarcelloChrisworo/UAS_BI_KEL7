import streamlit as st
import plotly.express as px
from utils import load_data

st.header("📍 Insight Detail Per Provinsi")

df = load_data()

provinsi_list = sorted(df['provinsi'].unique())
selected_prov = st.selectbox("Pilih Provinsi:", provinsi_list)

df_prov = df[df['provinsi'] == selected_prov]

# 1. Total Penerima Manfaat
total_penerima_prov = df_prov['jumlah_penerima_manfaat'].sum()
st.metric(f"Total Penerima Manfaat - {selected_prov}", f"{total_penerima_prov:,}")

st.markdown("---")
c1, c2 = st.columns(2)

with c1:
    # Status Penerima (Bar Stacked)
    df_status_prov = df_prov.groupby('jenjang')[['jumlah_satpen_negeri', 'jumlah_satpen_swasta']].sum().reset_index()
    fig_status_prov = px.bar(df_status_prov, x='jenjang', y=['jumlah_satpen_negeri', 'jumlah_satpen_swasta'], 
                             barmode='stack', title="Status Satpen di Provinsi Tersebut")
    st.plotly_chart(fig_status_prov, use_container_width=True)

with c2:
    # Distribusi per Jenjang
    df_jenjang_prov = df_prov.groupby('jenjang')['jumlah_penerima_manfaat'].sum().reset_index()
    fig_jenjang_prov = px.bar(df_jenjang_prov, x='jenjang', y='jumlah_penerima_manfaat', 
                              title="Distribusi Penerima per Jenjang")
    st.plotly_chart(fig_jenjang_prov, use_container_width=True)

st.markdown("---")

# Identifikasi Kecamatan Terpadat (Top 10)
st.subheader("Top 10 Kecamatan Terpadat")
df_kecamatan = df_prov.groupby('kecamatan')['jumlah_penerima_manfaat'].sum().reset_index()
df_kecamatan_top10 = df_kecamatan.sort_values(by='jumlah_penerima_manfaat', ascending=False).head(10)

fig_kecamatan = px.bar(df_kecamatan_top10, x='jumlah_penerima_manfaat', y='kecamatan', orientation='h',
                       title=f"10 Kecamatan dengan Penerima Terbanyak di {selected_prov}")
fig_kecamatan.update_layout(yaxis={'categoryorder':'total ascending'})
st.plotly_chart(fig_kecamatan, use_container_width=True)

st.markdown("---")

# Manajemen Risiko Provinsi (Bar Stacked)
st.subheader("Manajemen Risiko di Tingkat Provinsi")
risiko_cols = ['jumlah_alergi', 'jumlah_fobia', 'jumlah_intoleransi', 'jumlah_kondisi_khusus']
df_risiko_kec = df_prov.groupby('kabupaten_kota')[risiko_cols].sum().reset_index()

fig_risiko_prov = px.bar(df_risiko_kec, x='kabupaten_kota', y=risiko_cols, barmode='stack',
                         title="Risiko Berdasarkan Kabupaten/Kota")
fig_risiko_prov.update_layout(xaxis_tickangle=-45)
st.plotly_chart(fig_risiko_prov, use_container_width=True)
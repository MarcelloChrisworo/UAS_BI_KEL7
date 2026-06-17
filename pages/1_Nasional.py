import streamlit as st
import pandas as pd
import plotly.express as px
from utils import load_data

st.header("🇮🇩 Insight Demografi & Manajemen Risiko (Nasional)")

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
    # Profil Demografi jenjang pendidikan, laki, perempuan (Stacked Bar)
    df_gender = df.groupby('jenjang')[['jumlah_laki', 'jumlah_perempuan']].sum().reset_index()
    fig_gender = px.bar(df_gender, x='jenjang', y=['jumlah_laki', 'jumlah_perempuan'], 
                        title="Profil Demografi Berdasarkan Jenjang", barmode='stack')
    st.plotly_chart(fig_gender, use_container_width=True)

with c2:
    # Status Penerima (Donut Chart)
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

# Prepare Risk Data
risiko_cols = ['jumlah_alergi', 'jumlah_fobia', 'jumlah_intoleransi', 'jumlah_kondisi_khusus']
df_risiko_total = pd.DataFrame({
    'Kondisi': risiko_cols,
    'Total': [df[col].sum() for col in risiko_cols]
})

c3, c4 = st.columns(2)
with c3:
    # Manajemen Risiko Total (Donut)
    fig_risiko_pie = px.pie(df_risiko_total, names='Kondisi', values='Total', hole=0.4,
                            title="Distribusi Manajemen Risiko")
    st.plotly_chart(fig_risiko_pie, use_container_width=True)

with c4:
    # Manajemen Risiko per Jenjang (Bar Stacked)
    df_risiko_jenjang = df.groupby('jenjang')[risiko_cols].sum().reset_index()
    fig_risiko_bar = px.bar(df_risiko_jenjang, x='jenjang', y=risiko_cols, barmode='stack',
                            title="Risiko Berdasarkan Jenjang Pendidikan")
    st.plotly_chart(fig_risiko_bar, use_container_width=True)

# Manajemen Risiko per Provinsi (Treemap)
st.write("**Sebaran Risiko per Provinsi**")
df_risiko_prov = df.groupby('provinsi')[risiko_cols].sum().reset_index()
df_risiko_prov_melt = df_risiko_prov.melt(id_vars='provinsi', value_vars=risiko_cols, var_name='Risiko', value_name='Total')
fig_treemap = px.treemap(df_risiko_prov_melt, path=[px.Constant("Indonesia"), 'provinsi', 'Risiko'], values='Total',
                         title="Komposisi Risiko per Provinsi")
st.plotly_chart(fig_treemap, use_container_width=True)

# Heatmap Insight
st.write("**Matriks Risiko Kesehatan vs Jenjang Pendidikan**")
fig_heat = px.density_heatmap(df, x='jenjang', y='provinsi', z='total_risiko', histfunc='sum',
                              title="Heatmap Risiko (Provinsi vs Jenjang)")
st.plotly_chart(fig_heat, use_container_width=True)

# Multivariet Analysis (Parallel Categories)
st.write("**Analisis Alur Multivariat (Provinsi -> Jenjang -> Risiko)**")
df['Dominasi_Sekolah'] = df.apply(lambda x: 'Dominan Negeri' if x['jumlah_satpen_negeri'] > x['jumlah_satpen_swasta'] else 'Dominan Swasta', axis=1)

df_flow = df.groupby(['provinsi', 'jenjang', 'Dominasi_Sekolah'])[['jumlah_alergi']].sum().reset_index()
top_provs = df_flow.groupby('provinsi')['jumlah_alergi'].sum().nlargest(10).index
df_flow_top = df_flow[df_flow['provinsi'].isin(top_provs)]

fig_flow = px.parallel_categories(df_flow_top, dimensions=['provinsi', 'jenjang', 'Dominasi_Sekolah'],
                                  color="jumlah_alergi", color_continuous_scale=px.colors.sequential.Inferno,
                                  title="Alur Dominasi Sekolah & Kasus Alergi (Top 10 Provinsi)")
st.plotly_chart(fig_flow, use_container_width=True)
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json

# =====================================================
# CONFIG
# =====================================================

st.set_page_config(
    page_title="Dashboard MBG Indonesia",
    page_icon="📊",
    layout="wide"
)

# =====================================================
# LOAD DATA
# =====================================================

@st.cache_data
def load_data():
    return pd.read_csv(
        "MASTER_DATASET_MBG_BI2026.csv"
    )

@st.cache_data
def load_geojson():
    with open(
        "38 Provinsi Indonesia - Provinsi.json",
        "r",
        encoding="utf-8"
    ) as f:
        return json.load(f)

df = load_data()
geojson = load_geojson()

# =====================================================
# FEATURE ENGINEERING
# =====================================================

df["total_risiko"] = (
    df["jumlah_alergi"]
    + df["jumlah_fobia"]
    + df["jumlah_intoleransi"]
)

# =====================================================
# NORMALISASI PROVINSI UNTUK PETA
# =====================================================

df["provinsi_map"] = (
    df["provinsi"]
    .str.replace(
        "Prov. ",
        "",
        regex=False
    )
)

df["provinsi_map"] = (
    df["provinsi_map"]
    .replace({
        "D.K.I. Jakarta": "DKI Jakarta",
        "D.I. Yogyakarta": "DI Yogyakarta"
    })
)

# =====================================================
# SIDEBAR
# =====================================================

st.sidebar.title("🎛 Filter Dashboard")

selected_provinsi = st.sidebar.selectbox(
    "Provinsi",
    ["Semua"] +
    sorted(
        df["provinsi"].unique()
    )
)

selected_jenjang = st.sidebar.selectbox(
    "Jenjang",
    ["Semua"] +
    sorted(
        df["jenjang"].unique()
    )
)

filtered_df = df.copy()

if selected_provinsi != "Semua":
    filtered_df = filtered_df[
        filtered_df["provinsi"]
        == selected_provinsi
    ]

if selected_jenjang != "Semua":
    filtered_df = filtered_df[
        filtered_df["jenjang"]
        == selected_jenjang
    ]

# =====================================================
# HEADER
# =====================================================

st.title(
    "📊 Dashboard Business Intelligence MBG Indonesia"
)

st.markdown("""
Dashboard ini menyajikan analisis persebaran Program Makan Bergizi Gratis (MBG)
berdasarkan penerima manfaat, kondisi khusus, risiko kesehatan, dan satuan pendidikan
di seluruh Indonesia.
""")

st.markdown("---")

# =====================================================
# KPI NASIONAL
# =====================================================

total_penerima = (
    filtered_df[
        "jumlah_penerima_manfaat"
    ].sum()
)

total_satpen = (
    filtered_df[
        "jumlah_satpen_negeri"
    ].sum()
    +
    filtered_df[
        "jumlah_satpen_swasta"
    ].sum()
)

total_khusus = (
    filtered_df[
        "jumlah_kondisi_khusus"
    ].sum()
)

total_risiko = (
    filtered_df[
        "total_risiko"
    ].sum()
)

jumlah_provinsi = (
    filtered_df[
        "provinsi"
    ].nunique()
)

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric(
        "👥 Penerima",
        f"{total_penerima:,}"
    )

with col2:
    st.metric(
        "🏫 Satpen",
        f"{total_satpen:,}"
    )

with col3:
    st.metric(
        "⚠️ Risiko",
        f"{total_risiko:,}"
    )

with col4:
    st.metric(
        "🩺 Kondisi Khusus",
        f"{total_khusus:,}"
    )

with col5:
    st.metric(
        "📍 Provinsi",
        jumlah_provinsi
    )

st.markdown("---")

# =====================================================
# EXECUTIVE INSIGHT
# =====================================================

st.subheader(
    "🎯 Executive Insight Nasional"
)

prov_terbesar = (
    filtered_df
    .groupby("provinsi")
    [
        "jumlah_penerima_manfaat"
    ]
    .sum()
    .idxmax()
)

prov_risiko = (
    filtered_df
    .groupby("provinsi")
    [
        "total_risiko"
    ]
    .sum()
    .idxmax()
)

jenjang_terbesar = (
    filtered_df
    .groupby("jenjang")
    [
        "jumlah_penerima_manfaat"
    ]
    .sum()
    .idxmax()
)

gender_laki = (
    filtered_df[
        "jumlah_laki"
    ].sum()
)

gender_perempuan = (
    filtered_df[
        "jumlah_perempuan"
    ].sum()
)

gender_dominan = (
    "Laki-Laki"
    if gender_laki >
    gender_perempuan
    else "Perempuan"
)

st.info(
    f"""
### Ringkasan Nasional

📌 Provinsi dengan penerima manfaat terbesar adalah **{prov_terbesar}**

📌 Provinsi dengan total risiko tertinggi adalah **{prov_risiko}**

📌 Jenjang pendidikan dengan penerima manfaat terbesar adalah **{jenjang_terbesar}**

📌 Gender penerima manfaat dominan adalah **{gender_dominan}**

📌 Total penerima manfaat mencapai **{total_penerima:,} peserta**
yang tersebar di **{jumlah_provinsi} provinsi**
"""
)

st.markdown("---")

# =====================================================
# TABS
# =====================================================

tab1, tab2 = st.tabs(
    [
        "🇮🇩 Insight Nasional",
        "📍 Insight Provinsi"
    ]
)

tab1, tab2 = st.tabs(
    [
        "🇮🇩 Insight Nasional",
        "📍 Insight Provinsi"
    ]
)

with tab1:

    st.header("🇮🇩 Insight Nasional")

    # =====================================================
    # CHOROPLETH MAP
    # =====================================================

    st.subheader(
        "🗺️ Persebaran Penerima Manfaat Indonesia"
    )

    map_df = (
        filtered_df
        .groupby("provinsi_map")
        ["jumlah_penerima_manfaat"]
        .sum()
        .reset_index()
    )

    fig_map = px.choropleth(
        map_df,
        geojson=geojson,
        locations="provinsi_map",
        featureidkey="properties.PROVINSI",
        color="jumlah_penerima_manfaat",
        projection="mercator",
        title="Penerima Manfaat per Provinsi",
        color_continuous_scale="Blues"
    )

    fig_map.update_geos(
        fitbounds="locations",
        visible=False
    )

    st.plotly_chart(
        fig_map,
        use_container_width=True
    )

    st.markdown("---")

    # =====================================================
    # TREEMAP
    # =====================================================

    st.subheader(
        "🌳 Treemap Provinsi → Jenjang"
    )

    treemap_data = (
        filtered_df
        .groupby(
            [
                "provinsi",
                "jenjang"
            ]
        )[
            "jumlah_penerima_manfaat"
        ]
        .sum()
        .reset_index()
    )

    fig_tree = px.treemap(
        treemap_data,
        path=[
            "provinsi",
            "jenjang"
        ],
        values="jumlah_penerima_manfaat",
        title="Kontribusi Penerima Manfaat Berdasarkan Provinsi dan Jenjang"
    )

    st.plotly_chart(
        fig_tree,
        use_container_width=True
    )

    st.markdown("---")

    # =====================================================
    # DEMOGRAFI NASIONAL
    # =====================================================

    st.subheader(
        "👨‍🎓 Demografi Nasional"
    )

    demo = (
        filtered_df
        .groupby("jenjang")
        [
            [
                "jumlah_laki",
                "jumlah_perempuan"
            ]
        ]
        .sum()
        .reset_index()
    )

    fig_demo = px.bar(
        demo,
        x="jenjang",
        y=[
            "jumlah_laki",
            "jumlah_perempuan"
        ],
        barmode="stack",
        title="Distribusi Gender per Jenjang"
    )

    st.plotly_chart(
        fig_demo,
        use_container_width=True
    )

    st.markdown("---")

    # =====================================================
    # TOP 10 PROVINSI
    # =====================================================

    col1, col2 = st.columns(2)

    with col1:

        top_prov = (
            filtered_df
            .groupby("provinsi")
            [
                "jumlah_penerima_manfaat"
            ]
            .sum()
            .sort_values(
                ascending=False
            )
            .head(10)
            .reset_index()
        )

        fig_top = px.bar(
            top_prov,
            x="jumlah_penerima_manfaat",
            y="provinsi",
            orientation="h",
            title="Top 10 Provinsi Penerima Manfaat"
        )

        st.plotly_chart(
            fig_top,
            use_container_width=True
        )

    with col2:

        top_risk = (
            filtered_df
            .groupby("provinsi")
            [
                "total_risiko"
            ]
            .sum()
            .sort_values(
                ascending=False
            )
            .head(10)
            .reset_index()
        )

        fig_risk = px.bar(
            top_risk,
            x="total_risiko",
            y="provinsi",
            orientation="h",
            title="Top 10 Provinsi Risiko"
        )

        st.plotly_chart(
            fig_risk,
            use_container_width=True
        )

    st.markdown("---")

    # =====================================================
    # SATPEN & KONDISI KHUSUS
    # =====================================================

    col1, col2 = st.columns(2)

    with col1:

        satpen = pd.DataFrame({
            "Status": [
                "Negeri",
                "Swasta"
            ],
            "Jumlah": [
                filtered_df[
                    "jumlah_satpen_negeri"
                ].sum(),
                filtered_df[
                    "jumlah_satpen_swasta"
                ].sum()
            ]
        })

        fig_satpen = px.pie(
            satpen,
            names="Status",
            values="Jumlah",
            title="Komposisi Satpen"
        )

        st.plotly_chart(
            fig_satpen,
            use_container_width=True
        )

    with col2:

        khusus = (
            filtered_df
            .groupby("provinsi")
            [
                "jumlah_kondisi_khusus"
            ]
            .sum()
            .sort_values(
                ascending=False
            )
            .head(10)
            .reset_index()
        )

        fig_khusus = px.bar(
            khusus,
            x="jumlah_kondisi_khusus",
            y="provinsi",
            orientation="h",
            title="Top 10 Kondisi Khusus"
        )

        st.plotly_chart(
            fig_khusus,
            use_container_width=True
        )

    st.markdown("---")

    # =====================================================
    # KOMPOSISI RISIKO NASIONAL
    # =====================================================

    st.subheader(
        "⚠️ Komposisi Risiko Nasional"
    )

    risiko_df = pd.DataFrame({
        "Kategori": [
            "Alergi",
            "Fobia",
            "Intoleransi"
        ],
        "Jumlah": [
            filtered_df[
                "jumlah_alergi"
            ].sum(),
            filtered_df[
                "jumlah_fobia"
            ].sum(),
            filtered_df[
                "jumlah_intoleransi"
            ].sum()
        ]
    })

    fig_risiko = px.pie(
        risiko_df,
        names="Kategori",
        values="Jumlah",
        title="Komposisi Risiko Nasional"
    )

    st.plotly_chart(
        fig_risiko,
        use_container_width=True
    )

    with tab1:
        # =====================================================
        # SCATTER ANALYSIS
        # =====================================================

        st.markdown("---")

    st.subheader(
        "📈 Hubungan Risiko dan Penerima Manfaat"
    )

    prov_summary = (
        filtered_df
        .groupby("provinsi")
        .agg({
            "jumlah_penerima_manfaat":"sum",
            "total_risiko":"sum"
        })
        .reset_index()
    )

    fig_scatter = px.scatter(
        prov_summary,
        x="jumlah_penerima_manfaat",
        y="total_risiko",
        size="jumlah_penerima_manfaat",
        color="provinsi",
        hover_name="provinsi",
        title="Hubungan Risiko dan Penerima Manfaat"
    )

    st.plotly_chart(
        fig_scatter,
        use_container_width=True
    )

    # =====================================================
    # RASIO RISIKO
    # =====================================================

    st.markdown("---")

    st.subheader(
        "⚡ Rasio Risiko terhadap Penerima Manfaat"
    )

    rasio = (
        filtered_df
        .groupby("provinsi")
        .agg({
            "jumlah_penerima_manfaat":"sum",
            "total_risiko":"sum"
        })
        .reset_index()
    )

    rasio["rasio_risiko"] = (
        rasio["total_risiko"]
        /
        rasio["jumlah_penerima_manfaat"]
    ) * 100

    fig_ratio = px.bar(
        rasio
        .sort_values(
            "rasio_risiko",
            ascending=False
        )
        .head(10),
        x="rasio_risiko",
        y="provinsi",
        orientation="h",
        title="Top 10 Rasio Risiko Tertinggi (%)"
    )

    st.plotly_chart(
        fig_ratio,
        use_container_width=True
    )

    # =====================================================
    # HEATMAP KORELASI
    # =====================================================

    st.markdown("---")

    st.subheader(
        "🔥 Heatmap Korelasi"
    )

    corr = filtered_df[
        [
            "jumlah_penerima_manfaat",
            "jumlah_laki",
            "jumlah_perempuan",
            "jumlah_alergi",
            "jumlah_fobia",
            "jumlah_intoleransi",
            "jumlah_kondisi_khusus"
        ]
    ].corr()

    fig_heatmap = px.imshow(
        corr,
        text_auto=True,
        aspect="auto",
        title="Korelasi Antar Variabel"
    )

    st.plotly_chart(
        fig_heatmap,
        use_container_width=True
    )

# =====================================================
# TAB 2 - INSIGHT PROVINSI
# =====================================================

with tab2:

    st.header(
        "📍 Insight Provinsi"
    )

    provinsi = st.selectbox(
        "Pilih Provinsi",
        sorted(
            df["provinsi"].unique()
        )
    )

    data_prov = df[
        df["provinsi"]
        == provinsi
    ]

    data_prov["total_risiko"] = (
        data_prov["jumlah_alergi"]
        +
        data_prov["jumlah_fobia"]
        +
        data_prov["jumlah_intoleransi"]
    )

    # =====================================================
    # KPI PROVINSI
    # =====================================================

    penerima_prov = (
        data_prov[
            "jumlah_penerima_manfaat"
        ].sum()
    )

    risiko_prov = (
        data_prov[
            "total_risiko"
        ].sum()
    )

    khusus_prov = (
        data_prov[
            "jumlah_kondisi_khusus"
        ].sum()
    )

    satpen_prov = (
        data_prov[
            "jumlah_satpen_negeri"
        ].sum()
        +
        data_prov[
            "jumlah_satpen_swasta"
        ].sum()
    )

    col1,col2,col3,col4 = st.columns(4)

    col1.metric(
        "👥 Penerima",
        f"{penerima_prov:,}"
    )

    col2.metric(
        "⚠️ Risiko",
        f"{risiko_prov:,}"
    )

    col3.metric(
        "🩺 Kondisi Khusus",
        f"{khusus_prov:,}"
    )

    col4.metric(
        "🏫 Satpen",
        f"{satpen_prov:,}"
    )

    # =====================================================
    # INSIGHT OTOMATIS
    # =====================================================

    kec_terbesar = (
        data_prov
        .groupby("kecamatan")
        [
            "jumlah_penerima_manfaat"
        ]
        .sum()
        .idxmax()
    )

    jenjang_terbesar = (
        data_prov
        .groupby("jenjang")
        [
            "jumlah_penerima_manfaat"
        ]
        .sum()
        .idxmax()
    )

    risiko_dict = {
        "Alergi":
        data_prov[
            "jumlah_alergi"
        ].sum(),

        "Fobia":
        data_prov[
            "jumlah_fobia"
        ].sum(),

        "Intoleransi":
        data_prov[
            "jumlah_intoleransi"
        ].sum()
    }

    risiko_dominan = max(
        risiko_dict,
        key=risiko_dict.get
    )

    st.success(
        f"""
### Insight {provinsi}

📌 Kecamatan dengan penerima manfaat terbesar adalah **{kec_terbesar}**

📌 Jenjang dominan adalah **{jenjang_terbesar}**

📌 Risiko dominan adalah **{risiko_dominan}**

📌 Total penerima manfaat mencapai **{penerima_prov:,}**
        """
    )

    st.markdown("---")

    # =====================================================
    # RADAR CHART
    # =====================================================

    st.subheader(
        "🕸️ Profil Risiko Provinsi"
    )

    radar_df = pd.DataFrame({
        "Kategori":[
            "Alergi",
            "Fobia",
            "Intoleransi"
        ],
        "Jumlah":[
            data_prov[
                "jumlah_alergi"
            ].sum(),

            data_prov[
                "jumlah_fobia"
            ].sum(),

            data_prov[
                "jumlah_intoleransi"
            ].sum()
        ]
    })

    fig_radar = px.line_polar(
        radar_df,
        r="Jumlah",
        theta="Kategori",
        line_close=True
    )

    fig_radar.update_traces(
        fill="toself"
    )

    st.plotly_chart(
        fig_radar,
        use_container_width=True
    )

    # =====================================================
    # GENDER DISTRIBUTION
    # =====================================================

    st.subheader(
        "👨‍👩‍👧 Distribusi Gender"
    )

    gender_df = pd.DataFrame({
        "Gender":[
            "Laki-Laki",
            "Perempuan"
        ],
        "Jumlah":[
            data_prov[
                "jumlah_laki"
            ].sum(),

            data_prov[
                "jumlah_perempuan"
            ].sum()
        ]
    })

    fig_gender = px.pie(
        gender_df,
        names="Gender",
        values="Jumlah"
    )

    st.plotly_chart(
        fig_gender,
        use_container_width=True
    )

    # =====================================================
    # TOP KECAMATAN
    # =====================================================

    st.subheader(
        "🏆 Top 10 Kecamatan"
    )

    top_kec = (
        data_prov
        .groupby("kecamatan")
        [
            "jumlah_penerima_manfaat"
        ]
        .sum()
        .sort_values(
            ascending=False
        )
        .head(10)
        .reset_index()
    )

    fig_kec = px.bar(
        top_kec,
        x="jumlah_penerima_manfaat",
        y="kecamatan",
        orientation="h"
    )

    st.plotly_chart(
        fig_kec,
        use_container_width=True
    )

    # =====================================================
    # RANKING KECAMATAN
    # =====================================================

    st.subheader(
        "📋 Ranking Kecamatan"
    )

    ranking = (
        data_prov
        .groupby("kecamatan")
        .agg({
            "jumlah_penerima_manfaat":"sum",
            "total_risiko":"sum",
            "jumlah_kondisi_khusus":"sum"
        })
        .reset_index()
        .sort_values(
            "jumlah_penerima_manfaat",
            ascending=False
        )
    )

    st.dataframe(
        ranking,
        use_container_width=True
    )

# =====================================================
# DOWNLOAD DATA
# =====================================================

st.markdown("---")

st.header(
    "⬇️ Download Dataset"
)

csv = filtered_df.to_csv(
    index=False
)

st.download_button(
    label="Download CSV",
    data=csv,
    file_name="dashboard_mbg.csv",
    mime="text/csv"
)

# =====================================================
# FOOTER
# =====================================================

st.markdown("---")

st.caption(
    "Dashboard Business Intelligence MBG Indonesia | Streamlit + Plotly"
)
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from utils import JENJANG_ORDER, load_data, load_geojson

df_all = load_data()
geo = load_geojson()
df_all["total_peserta_didik"] = df_all["jumlah_laki"] + df_all["jumlah_perempuan"]

jenjang_urut = [j for j in JENJANG_ORDER if j in df_all["jenjang"].unique()]

st.title("Dashboard BI — Program Makan Bergizi Gratis 2026")
st.caption("Data Nasional MBG | Juni 2026")
st.markdown("---")

# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR — FILTER GLOBAL
# ══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.header("Filter Data")

    # Tahun
    semua_tahun = sorted(df_all["tahun"].unique().tolist())
    pilih_tahun = st.multiselect(
        "Tahun", semua_tahun, placeholder="Semua tahun (default)"
    )

    # Provinsi
    df_tmp0 = df_all[df_all["tahun"].isin(pilih_tahun)] if pilih_tahun else df_all
    semua_prov = sorted(df_tmp0["provinsi"].unique().tolist())
    pilih_prov = st.multiselect(
        "Provinsi", semua_prov, placeholder="Semua provinsi (default)"
    )

    # Kabupaten — ikut provinsi
    df_tmp = df_tmp0[df_tmp0["provinsi"].isin(pilih_prov)] if pilih_prov else df_tmp0
    semua_kab = sorted(df_tmp["kabupaten_kota"].unique().tolist())
    pilih_kab = st.multiselect(
        "Kabupaten/Kota", semua_kab, placeholder="Semua kabupaten/kota"
    )

    # Kecamatan — ikut kabupaten
    df_tmp2 = df_tmp[df_tmp["kabupaten_kota"].isin(pilih_kab)] if pilih_kab else df_tmp
    semua_kec = sorted(df_tmp2["kecamatan"].unique().tolist())
    pilih_kec = st.multiselect("Kecamatan", semua_kec, placeholder="Semua kecamatan")

    # Jenjang
    pilih_jenjang = st.multiselect("Jenjang", jenjang_urut, default=jenjang_urut)

    # Status sekolah
    pilih_status = st.selectbox("Status Sekolah", ["Semua", "Negeri", "Swasta"])

    st.markdown("---")
    st.caption("Kosongkan = tampilkan semua")

# ── Apply filter ───────────────────────────────────────────────────────────────
df = df_all.copy()
if pilih_tahun:
    df = df[df["tahun"].isin(pilih_tahun)]
if pilih_prov:
    df = df[df["provinsi"].isin(pilih_prov)]
if pilih_kab:
    df = df[df["kabupaten_kota"].isin(pilih_kab)]
if pilih_kec:
    df = df[df["kecamatan"].isin(pilih_kec)]
if pilih_jenjang:
    df = df[df["jenjang"].isin(pilih_jenjang)]
if pilih_status != "Semua":
    df = df[df["status_sekolah"] == pilih_status]

if len(df) == 0:
    st.error("Tidak ada data untuk filter ini. Coba perluas pilihan.")
    st.stop()

n_tahun = df["tahun"].nunique()
n_prov = df["provinsi"].nunique()
n_kab = df["kabupaten_kota"].nunique()
n_kec = df["kecamatan"].nunique()
st.info(
    f"Filter aktif: **{n_tahun} tahun** | **{n_prov} provinsi** | **{n_kab} kabupaten/kota** | **{n_kec} kecamatan**"
)

# ══════════════════════════════════════════════════════════════════════════════
# TAB NAVIGASI
# ══════════════════════════════════════════════════════════════════════════════
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs(
    [
        "Ringkasan",
        "Wilayah",
        "Demografi",
        "Kondisi Khusus",
        "Penerima Manfaat",
        "Sekolah",
        "Tren & Perbandingan",
    ]
)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — RINGKASAN EKSEKUTIF
# ══════════════════════════════════════════════════════════════════════════════
with tab1:
    st.subheader("Ringkasan Eksekutif")

    total_satpen = int(df["jumlah_satuan_pendidikan"].sum())
    total_laki = int(df["jumlah_laki"].sum())
    total_perempuan = int(df["jumlah_perempuan"].sum())
    total_penerima = int(df["jumlah_penerima_manfaat"].sum())
    total_kk = int(df["jumlah_kondisi_khusus"].sum())
    total_negeri = int(df["jumlah_satpen_negeri"].sum())
    total_swasta = int(df["jumlah_satpen_swasta"].sum())
    total_peserta = total_laki + total_perempuan

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Satuan Pendidikan", f"{total_satpen:,}")
    k2.metric("Peserta Didik Laki-laki", f"{total_laki:,}")
    k3.metric("Peserta Didik Perempuan", f"{total_perempuan:,}")
    k4.metric("Penerima Manfaat", f"{total_penerima:,}")

    k5, k6, k7 = st.columns(3)
    k5.metric("Peserta Didik Kondisi Khusus", f"{total_kk:,}")
    k6.metric("Sekolah Negeri", f"{total_negeri:,}")
    k7.metric("Sekolah Swasta", f"{total_swasta:,}")

    st.markdown("---")

    c1, c2, c3 = st.columns(3)
    with c1:
        fig = go.Figure(
            go.Pie(
                labels=["Laki-laki", "Perempuan"],
                values=[total_laki, total_perempuan],
                hole=0.55,
                marker_colors=["#1f77b4", "#e377c2"],
                textinfo="label+percent",
            )
        )
        fig.update_layout(
            title="Komposisi Gender Peserta Didik",
            height=270,
            margin=dict(t=40, b=0, l=0, r=0),
            legend=dict(orientation="h", y=-0.15),
        )
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        fig = go.Figure(
            go.Pie(
                labels=["Negeri", "Swasta"],
                values=[total_negeri, total_swasta],
                hole=0.55,
                marker_colors=["#2ca02c", "#ff7f0e"],
                textinfo="label+percent",
            )
        )
        fig.update_layout(
            title="Komposisi Sekolah Negeri vs Swasta",
            height=270,
            margin=dict(t=40, b=0, l=0, r=0),
            legend=dict(orientation="h", y=-0.15),
        )
        st.plotly_chart(fig, use_container_width=True)

    with c3:
        fig = go.Figure(
            go.Pie(
                labels=["Alergi", "Fobia Makanan", "Intoleransi"],
                values=[
                    int(df["jumlah_alergi"].sum()),
                    int(df["jumlah_fobia"].sum()),
                    int(df["jumlah_intoleransi"].sum()),
                ],
                hole=0.55,
                marker_colors=["#d62728", "#9467bd", "#8c564b"],
                textinfo="label+percent",
            )
        )
        fig.update_layout(
            title="Profil Kondisi Khusus",
            height=270,
            margin=dict(t=40, b=0, l=0, r=0),
            legend=dict(orientation="h", y=-0.15),
        )
        st.plotly_chart(fig, use_container_width=True)

    # Top 10 provinsi
    df_top = df.groupby("provinsi", as_index=False)["jumlah_penerima_manfaat"].sum()
    df_top = df_top.nlargest(10, "jumlah_penerima_manfaat").sort_values(
        "jumlah_penerima_manfaat"
    )
    fig = px.bar(
        df_top,
        x="jumlah_penerima_manfaat",
        y="provinsi",
        orientation="h",
        color="jumlah_penerima_manfaat",
        color_continuous_scale="Blues",
        title="Top 10 Provinsi — Penerima Manfaat",
        labels={"jumlah_penerima_manfaat": "Penerima Manfaat", "provinsi": "Provinsi"},
    )
    fig.update_layout(coloraxis_showscale=False)
    st.plotly_chart(fig, use_container_width=True)

    # Insight
    top_prov = df.groupby("provinsi")["jumlah_penerima_manfaat"].sum().idxmax()
    top_kk = df.groupby("provinsi")["jumlah_kondisi_khusus"].sum().idxmax()
    top_jen = df.groupby("jenjang")["jumlah_penerima_manfaat"].sum().idxmax()
    st.info(f"""
**Temuan Utama:**
- Provinsi penerima manfaat terbanyak: **{top_prov}**
- Provinsi kondisi khusus terbanyak: **{top_kk}**
- Jenjang penerima manfaat terbanyak: **{top_jen}**
- Gender dominan: **{"Laki-laki" if total_laki > total_perempuan else "Perempuan"}** (selisih {abs(total_laki - total_perempuan):,} peserta didik)
- Proporsi kondisi khusus dari penerima: **{total_kk / total_penerima * 100:.2f}%**
    """)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — ANALISIS WILAYAH
# ══════════════════════════════════════════════════════════════════════════════
with tab2:
    st.subheader("Analisis Wilayah")

    df_geo = df.groupby("provinsi_map", as_index=False).agg(
        jumlah_penerima_manfaat=("jumlah_penerima_manfaat", "sum"),
        jumlah_kondisi_khusus=("jumlah_kondisi_khusus", "sum"),
        jumlah_satuan_pendidikan=("jumlah_satuan_pendidikan", "sum"),
        total_peserta_didik=("total_peserta_didik", "sum"),
    )

    metrik_peta = st.radio(
        "Tampilkan di peta:",
        [
            "jumlah_penerima_manfaat",
            "jumlah_kondisi_khusus",
            "jumlah_satuan_pendidikan",
            "total_peserta_didik",
        ],
        format_func=lambda x: {
            "jumlah_penerima_manfaat": "Penerima Manfaat",
            "jumlah_kondisi_khusus": "Peserta Didik Kondisi Khusus",
            "jumlah_satuan_pendidikan": "Satuan Pendidikan",
            "total_peserta_didik": "Total Peserta Didik",
        }[x],
        horizontal=True,
    )

    label_map = {
        "jumlah_penerima_manfaat": "Penerima Manfaat",
        "jumlah_kondisi_khusus": "Kondisi Khusus",
        "jumlah_satuan_pendidikan": "Satuan Pendidikan",
        "total_peserta_didik": "Total Peserta Didik",
    }

   # ── FIXED PETA CHOROPLETH INDONESIA (pakai engine maplibre, bukan geo/d3) ────
    fig_peta = px.choropleth_map(
        df_geo,
        geojson=geo,
        locations="provinsi_map",
        featureidkey="properties.PROVINSI",  # <── GeoJSON kamu pakai key "PROVINSI", bukan "PRV_NAME"
        color=metrik_peta,
        color_continuous_scale="YlOrRd",
        title=f"Peta {label_map[metrik_peta]} per Provinsi",
        labels={metrik_peta: label_map[metrik_peta], "provinsi_map": "Provinsi"},
        hover_data={
            "jumlah_penerima_manfaat": ":,", 
            "jumlah_kondisi_khusus": ":,",
            "jumlah_satuan_pendidikan": ":,",
        },
        map_style="carto-positron",
        center={"lat": -2.5, "lon": 118},
        zoom=3.6,
        opacity=0.8,
    )
    
    fig_peta.update_layout(margin={"r": 0, "t": 40, "l": 0, "b": 0}, height=500)
    st.plotly_chart(fig_peta, use_container_width=True)
    # ────────────────────────────────────────────────────────────────────────────
    # ────────────────────────────────────────────────────────────────────────────
    # Ranking provinsi
    df_rank = df.groupby("provinsi", as_index=False).agg(
        penerima=("jumlah_penerima_manfaat", "sum"),
        kondisi_khusus=("jumlah_kondisi_khusus", "sum"),
    )
    c1, c2 = st.columns(2)
    with c1:
        fig = px.bar(
            df_rank.nlargest(15, "penerima").sort_values("penerima"),
            x="penerima",
            y="provinsi",
            orientation="h",
            color="penerima",
            color_continuous_scale="Blues",
            title="Top 15 Provinsi — Penerima Manfaat",
            labels={"penerima": "Penerima Manfaat", "provinsi": ""},
        )
        fig.update_layout(coloraxis_showscale=False, height=430)
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        fig = px.bar(
            df_rank.nlargest(15, "kondisi_khusus").sort_values("kondisi_khusus"),
            x="kondisi_khusus",
            y="provinsi",
            orientation="h",
            color="kondisi_khusus",
            color_continuous_scale="Reds",
            title="Top 15 Provinsi — Peserta Kondisi Khusus",
            labels={"kondisi_khusus": "Kondisi Khusus", "provinsi": ""},
        )
        fig.update_layout(coloraxis_showscale=False, height=430)
        st.plotly_chart(fig, use_container_width=True)

    # Treemap
    df_tree = df.groupby(["provinsi", "kabupaten_kota"], as_index=False).agg(
        penerima=("jumlah_penerima_manfaat", "sum"),
        kondisi_khusus=("jumlah_kondisi_khusus", "sum"),
    )
    df_tree = df_tree[df_tree["penerima"] > 0]
    if not df_tree.empty:
        fig = px.treemap(
            df_tree,
            path=[px.Constant("Indonesia"), "provinsi", "kabupaten_kota"],
            values="penerima",
            color="kondisi_khusus",
            color_continuous_scale="RdYlGn_r",
            title="Treemap Penerima Manfaat → Provinsi → Kabupaten/Kota (Warna = Kondisi Khusus)",
            labels={"penerima": "Penerima Manfaat", "kondisi_khusus": "Kondisi Khusus"},
        )
        fig.update_layout(height=500)
        st.plotly_chart(fig, use_container_width=True)

    # Top 20 kecamatan
    df_kec = df.groupby(
        ["provinsi", "kabupaten_kota", "kecamatan"], as_index=False
    ).agg(
        penerima=("jumlah_penerima_manfaat", "sum"),
        kondisi_khusus=("jumlah_kondisi_khusus", "sum"),
    )
    df_kec["label"] = (
        df_kec["provinsi"].str.replace("Prov. ", "") + " / " + df_kec["kecamatan"]
    )
    top20 = df_kec.nlargest(20, "kondisi_khusus").sort_values("kondisi_khusus")
    fig = px.bar(
        top20,
        x="kondisi_khusus",
        y="label",
        orientation="h",
        color="kondisi_khusus",
        color_continuous_scale="Reds",
        title="Top 20 Kecamatan — Peserta Kondisi Khusus Terbanyak",
        labels={"kondisi_khusus": "Kondisi Khusus", "label": ""},
    )
    fig.update_layout(coloraxis_showscale=False, height=560)
    st.plotly_chart(fig, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — ANALISIS DEMOGRAFI
# ══════════════════════════════════════════════════════════════════════════════
with tab3:
    st.subheader("Analisis Demografi")

    # Gender per jenjang
    df_gj = (
        df.groupby("jenjang")[["jumlah_laki", "jumlah_perempuan"]].sum().reset_index()
    )
    df_gj["jenjang"] = pd.Categorical(
        df_gj["jenjang"], categories=jenjang_urut, ordered=True
    )
    df_gj = df_gj.sort_values("jenjang")
    fig = px.bar(
        df_gj,
        x="jenjang",
        y=["jumlah_laki", "jumlah_perempuan"],
        barmode="group",
        color_discrete_map={"jumlah_laki": "#1f77b4", "jumlah_perempuan": "#e377c2"},
        title="Distribusi Gender per Jenjang Pendidikan",
        labels={
            "value": "Jumlah Peserta Didik",
            "variable": "Gender",
            "jenjang": "Jenjang",
        },
    )
    fig.for_each_trace(
        lambda t: t.update(
            name={"jumlah_laki": "Laki-laki", "jumlah_perempuan": "Perempuan"}.get(
                t.name, t.name
            )
        )
    )
    st.plotly_chart(fig, use_container_width=True)

    # Gender gap per provinsi
    df_gap = df.groupby("provinsi", as_index=False).agg(
        laki=("jumlah_laki", "sum"),
        perempuan=("jumlah_perempuan", "sum"),
    )
    df_gap["total"] = df_gap["laki"] + df_gap["perempuan"]
    df_gap["selisih_persen"] = (
        (df_gap["laki"] - df_gap["perempuan"]) / df_gap["total"] * 100
    ).round(2)
    df_gap = df_gap.sort_values("selisih_persen")
    fig = px.bar(
        df_gap,
        x="selisih_persen",
        y="provinsi",
        orientation="h",
        color="selisih_persen",
        color_continuous_scale="RdBu_r",
        color_continuous_midpoint=0,
        title="Ketimpangan Gender per Provinsi (+ Laki-laki lebih banyak, − Perempuan lebih banyak)",
        labels={"selisih_persen": "Selisih (%)", "provinsi": ""},
    )
    fig.update_layout(coloraxis_showscale=False, height=520)
    st.plotly_chart(fig, use_container_width=True)

    # Heatmap peserta didik
    df_heat = (
        df.groupby(["provinsi", "jenjang"])["total_peserta_didik"].sum().reset_index()
    )
    df_pivot = df_heat.pivot(
        index="provinsi", columns="jenjang", values="total_peserta_didik"
    ).fillna(0)
    fig = px.imshow(
        df_pivot,
        color_continuous_scale="Blues",
        title="Heatmap Total Peserta Didik (Provinsi × Jenjang)",
        aspect="auto",
        text_auto=".0f",
    )
    fig.update_layout(height=max(400, n_prov * 18))
    st.plotly_chart(fig, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 4 — ANALISIS KONDISI KHUSUS
# ══════════════════════════════════════════════════════════════════════════════
with tab4:
    st.subheader("Analisis Kondisi Khusus")

    total_alergi = int(df["jumlah_alergi"].sum())
    total_fobia = int(df["jumlah_fobia"].sum())
    total_intoler = int(df["jumlah_intoleransi"].sum())
    total_kk4 = int(df["jumlah_kondisi_khusus"].sum())

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Kondisi Khusus", f"{total_kk4:,}")
    m2.metric("Alergi", f"{total_alergi:,}")
    m3.metric("Fobia Makanan", f"{total_fobia:,}")
    m4.metric("Intoleransi", f"{total_intoler:,}")
    st.markdown("---")

    c1, c2 = st.columns(2)
    with c1:
        df_kk_j = (
            df.groupby("jenjang")[
                ["jumlah_alergi", "jumlah_fobia", "jumlah_intoleransi"]
            ]
            .sum()
            .reset_index()
        )
        df_kk_j["jenjang"] = pd.Categorical(
            df_kk_j["jenjang"], categories=jenjang_urut, ordered=True
        )
        df_kk_j = df_kk_j.sort_values("jenjang").rename(
            columns={
                "jumlah_alergi": "Alergi",
                "jumlah_fobia": "Fobia Makanan",
                "jumlah_intoleransi": "Intoleransi",
            }
        )
        fig = px.bar(
            df_kk_j,
            x="jenjang",
            y=["Alergi", "Fobia Makanan", "Intoleransi"],
            barmode="stack",
            color_discrete_sequence=["#d62728", "#9467bd", "#8c564b"],
            title="Kondisi Khusus per Jenjang Pendidikan",
            labels={
                "value": "Jumlah",
                "variable": "Jenis Kondisi",
                "jenjang": "Jenjang",
            },
        )
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        df_kk_p = df.groupby("provinsi")["jumlah_kondisi_khusus"].sum().reset_index()
        df_kk_p = df_kk_p.nlargest(15, "jumlah_kondisi_khusus").sort_values(
            "jumlah_kondisi_khusus"
        )
        fig = px.bar(
            df_kk_p,
            x="jumlah_kondisi_khusus",
            y="provinsi",
            orientation="h",
            color="jumlah_kondisi_khusus",
            color_continuous_scale="Reds",
            title="Top 15 Provinsi — Kondisi Khusus",
            labels={"jumlah_kondisi_khusus": "Kondisi Khusus", "provinsi": ""},
        )
        fig.update_layout(coloraxis_showscale=False, height=420)
        st.plotly_chart(fig, use_container_width=True)

    # Heatmap kondisi khusus
    df_hkk = (
        df.groupby(["provinsi", "jenjang"])["jumlah_kondisi_khusus"].sum().reset_index()
    )
    df_hkk_pivot = df_hkk.pivot(
        index="provinsi", columns="jenjang", values="jumlah_kondisi_khusus"
    ).fillna(0)
    fig = px.imshow(
        df_hkk_pivot,
        color_continuous_scale="YlOrRd",
        title="Heatmap Kondisi Khusus (Provinsi × Jenjang)",
        aspect="auto",
        text_auto=".0f",
    )
    fig.update_layout(height=max(400, n_prov * 18))
    st.plotly_chart(fig, use_container_width=True)

    # Negeri vs Swasta
    c3, c4 = st.columns(2)
    with c3:
        df_ns = (
            df.groupby("status_sekolah", as_index=False)
            .agg(
                Alergi=("jumlah_alergi", "sum"),
                Fobia_Makanan=("jumlah_fobia", "sum"),
                Intoleransi=("jumlah_intoleransi", "sum"),
                Kondisi_Khusus=("jumlah_kondisi_khusus", "sum"),
            )
            .rename(
                columns={
                    "status_sekolah": "Status Sekolah",
                    "Fobia_Makanan": "Fobia Makanan",
                    "Kondisi_Khusus": "Kondisi Khusus",
                }
            )
        )
        fig = px.bar(
            df_ns,
            x="Status Sekolah",
            y=["Alergi", "Fobia Makanan", "Intoleransi", "Kondisi Khusus"],
            barmode="group",
            title="Kondisi Khusus: Sekolah Negeri vs Swasta",
            labels={"value": "Jumlah", "variable": "Jenis"},
        )
        st.plotly_chart(fig, use_container_width=True)

    with c4:
        df_jns = df.groupby(["jenjang", "status_sekolah"], as_index=False).agg(
            kondisi_khusus=("jumlah_kondisi_khusus", "sum")
        )
        fig = px.bar(
            df_jns,
            x="jenjang",
            y="kondisi_khusus",
            color="status_sekolah",
            barmode="group",
            color_discrete_map={"Negeri": "#2ca02c", "Swasta": "#ff7f0e"},
            title="Kondisi Khusus per Jenjang & Status Sekolah",
            labels={
                "kondisi_khusus": "Kondisi Khusus",
                "jenjang": "Jenjang",
                "status_sekolah": "Status Sekolah",
            },
        )
        st.plotly_chart(fig, use_container_width=True)

    top_prov_kk = df_kk_p.iloc[-1]["provinsi"]
    top_jen_kk = (
        df_kk_j.assign(
            total=lambda x: x[["Alergi", "Fobia Makanan", "Intoleransi"]].sum(axis=1)
        )
        .nlargest(1, "total")["jenjang"]
        .values[0]
    )
    st.warning(f"""
**Insight Kondisi Khusus:**
- Provinsi kondisi khusus terbanyak: **{top_prov_kk}**
- Jenjang dengan kebutuhan inklusif terbesar: **{top_jen_kk}**
- Alergi mendominasi: **{total_alergi / total_kk4 * 100:.1f}%** dari total kondisi khusus
    """)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 5 — ANALISIS PENERIMA MANFAAT
# ══════════════════════════════════════════════════════════════════════════════
with tab5:
    st.subheader("Analisis Penerima Manfaat")

    df_pm_prov = (
        df.groupby("provinsi", as_index=False)
        .agg(
            penerima=("jumlah_penerima_manfaat", "sum"),
            kondisi_khusus=("jumlah_kondisi_khusus", "sum"),
            satuan_pendidikan=("jumlah_satuan_pendidikan", "sum"),
        )
        .sort_values("penerima")
    )

    c1, c2 = st.columns(2)
    with c1:
        fig = px.bar(
            df_pm_prov,
            x="penerima",
            y="provinsi",
            orientation="h",
            color="penerima",
            color_continuous_scale="Blues",
            title="Penerima Manfaat per Provinsi",
            labels={"penerima": "Penerima Manfaat", "provinsi": ""},
        )
        fig.update_layout(coloraxis_showscale=False, height=560)
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        fig = px.scatter(
            df_pm_prov,
            x="penerima",
            y="kondisi_khusus",
            size="satuan_pendidikan",
            color="kondisi_khusus",
            color_continuous_scale="Reds",
            hover_name="provinsi",
            title="Penerima Manfaat vs Kondisi Khusus per Provinsi (Ukuran = Satuan Pendidikan)",
            labels={
                "penerima": "Penerima Manfaat",
                "kondisi_khusus": "Kondisi Khusus",
                "satuan_pendidikan": "Satuan Pendidikan",
            },
        )
        fig.update_layout(coloraxis_showscale=False, height=560)
        st.plotly_chart(fig, use_container_width=True)

    # Penerima per jenjang
    df_pm_j = df.groupby("jenjang", as_index=False).agg(
        penerima=("jumlah_penerima_manfaat", "sum")
    )
    df_pm_j["jenjang"] = pd.Categorical(
        df_pm_j["jenjang"], categories=jenjang_urut, ordered=True
    )
    df_pm_j = df_pm_j.sort_values("jenjang")
    fig = px.bar(
        df_pm_j,
        x="jenjang",
        y="penerima",
        color="penerima",
        color_continuous_scale="Blues",
        title="Penerima Manfaat per Jenjang Pendidikan",
        labels={"penerima": "Penerima Manfaat", "jenjang": "Jenjang"},
        text="penerima",
    )
    fig.update_traces(texttemplate="%{text:,.0f}", textposition="outside")
    fig.update_layout(coloraxis_showscale=False)
    st.plotly_chart(fig, use_container_width=True)

    # Matriks prioritas
    st.markdown("#### Prioritas Intervensi")
    rata_penerima = df_pm_prov["penerima"].mean()
    median_kk5 = df_pm_prov["kondisi_khusus"].median()
    df_pm_prov["prioritas"] = df_pm_prov.apply(
        lambda r: (
            "Prioritas Tinggi"
            if (r["penerima"] < rata_penerima and r["kondisi_khusus"] > median_kk5)
            else (
                "Perlu Perhatian"
                if r["penerima"] < rata_penerima
                else "Sudah Baik"
            )
        ),
        axis=1,
    )
    fig = px.scatter(
        df_pm_prov,
        x="penerima",
        y="kondisi_khusus",
        size="satuan_pendidikan",
        color="prioritas",
        hover_name="provinsi",
        color_discrete_map={
            "Prioritas Tinggi": "#d62728",
            "Perlu Perhatian": "#ff7f0e",
            "Sudah Baik": "#2ca02c",
        },
        title="Matriks Prioritas: Penerima Manfaat vs Kondisi Khusus",
        labels={
            "penerima": "Penerima Manfaat",
            "kondisi_khusus": "Kondisi Khusus",
            "prioritas": "Kategori",
        },
    )
    fig.add_vline(
        x=rata_penerima,
        line_dash="dash",
        line_color="gray",
        annotation_text="Rata-rata penerima",
    )
    fig.add_hline(
        y=median_kk5,
        line_dash="dash",
        line_color="gray",
        annotation_text="Median kondisi khusus",
    )
    fig.update_layout(height=500)
    st.plotly_chart(fig, use_container_width=True)

    prov_prior = df_pm_prov[df_pm_prov["prioritas"] == "Prioritas Tinggi"][
        "provinsi"
    ].tolist()
    st.warning(f"""
**Insight Penerima Manfaat:**
- Provinsi prioritas intervensi: **{", ".join(prov_prior) if prov_prior else "Tidak ada"}**
- Wilayah kuadran kiri-atas = penerima sedikit namun kondisi khusus tinggi (percepatan distribusi diperlukan)
    """)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 6 — ANALISIS SEKOLAH
# ══════════════════════════════════════════════════════════════════════════════
with tab6:
    st.subheader("Analisis Sekolah")

    c1, c2 = st.columns(2)
    with c1:
        df_ns_j = df.groupby("jenjang", as_index=False).agg(
            Negeri=("jumlah_satpen_negeri", "sum"),
            Swasta=("jumlah_satpen_swasta", "sum"),
        )
        df_ns_j["jenjang"] = pd.Categorical(
            df_ns_j["jenjang"], categories=jenjang_urut, ordered=True
        )
        df_ns_j = df_ns_j.sort_values("jenjang")
        fig = px.bar(
            df_ns_j,
            x="jenjang",
            y=["Negeri", "Swasta"],
            barmode="stack",
            color_discrete_map={"Negeri": "#2ca02c", "Swasta": "#ff7f0e"},
            title="Komposisi Sekolah Negeri vs Swasta per Jenjang",
            labels={
                "value": "Jumlah Satuan Pendidikan",
                "variable": "Status",
                "jenjang": "Jenjang",
            },
        )
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        df_pct = df.groupby("provinsi", as_index=False).agg(
            negeri=("jumlah_satpen_negeri", "sum"),
            swasta=("jumlah_satpen_swasta", "sum"),
        )
        df_pct["total"] = df_pct["negeri"] + df_pct["swasta"]
        df_pct["persen_negeri"] = (df_pct["negeri"] / df_pct["total"] * 100).round(1)
        df_pct = df_pct.sort_values("persen_negeri")
        fig = px.bar(
            df_pct,
            x="persen_negeri",
            y="provinsi",
            orientation="h",
            color="persen_negeri",
            color_continuous_scale="Greens",
            title="Persentase Sekolah Negeri per Provinsi",
            labels={"persen_negeri": "% Sekolah Negeri", "provinsi": ""},
        )
        fig.add_vline(x=50, line_dash="dash", line_color="red", annotation_text="50%")
        fig.update_layout(coloraxis_showscale=False, height=520)
        st.plotly_chart(fig, use_container_width=True)

    # Efisiensi per jenjang
    df_eff = df.groupby("jenjang", as_index=False).agg(
        satuan_pendidikan=("jumlah_satuan_pendidikan", "sum"),
        penerima=("jumlah_penerima_manfaat", "sum"),
        kondisi_khusus=("jumlah_kondisi_khusus", "sum"),
    )
    df_eff["penerima_per_satpen"] = (
        df_eff["penerima"] / df_eff["satuan_pendidikan"].replace(0, np.nan)
    ).round(1)
    df_eff["kondisi_per_satpen"] = (
        df_eff["kondisi_khusus"] / df_eff["satuan_pendidikan"].replace(0, np.nan)
    ).round(2)
    df_eff["jenjang"] = pd.Categorical(
        df_eff["jenjang"], categories=jenjang_urut, ordered=True
    )
    df_eff = df_eff.sort_values("jenjang")

    c3, c4 = st.columns(2)
    with c3:
        fig = px.bar(
            df_eff,
            x="jenjang",
            y="penerima_per_satpen",
            color="penerima_per_satpen",
            color_continuous_scale="Purples",
            title="Rata-rata Penerima Manfaat per Satuan Pendidikan",
            labels={
                "penerima_per_satpen": "Penerima per Satuan Pendidikan",
                "jenjang": "Jenjang",
            },
            text="penerima_per_satpen",
        )
        fig.update_traces(texttemplate="%{text:.0f}", textposition="outside")
        fig.update_layout(coloraxis_showscale=False)
        st.plotly_chart(fig, use_container_width=True)

    with c4:
        fig = px.bar(
            df_eff,
            x="jenjang",
            y="kondisi_per_satpen",
            color="kondisi_per_satpen",
            color_continuous_scale="Oranges",
            title="Rata-rata Kondisi Khusus per Satuan Pendidikan",
            labels={
                "kondisi_per_satpen": "Kondisi Khusus per Satuan Pendidikan",
                "jenjang": "Jenjang",
            },
            text="kondisi_per_satpen",
        )
        fig.update_traces(texttemplate="%{text:.1f}", textposition="outside")
        fig.update_layout(coloraxis_showscale=False)
        st.plotly_chart(fig, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 7 — TREN & PERBANDINGAN WILAYAH
# ══════════════════════════════════════════════════════════════════════════════
with tab7:
    st.subheader("Tren & Perbandingan Wilayah")

    # ── PERBANDINGAN ANTAR PROVINSI ────────────────────────────────────────────
    st.markdown("### Perbandingan Antar Provinsi")
    semua_prov_list = sorted(df["provinsi"].unique().tolist())

    if len(semua_prov_list) < 2:
        st.warning("Pilih minimal 2 provinsi di filter sidebar untuk membandingkan.")
    else:
        col_sel1, col_sel2 = st.columns(2)
        with col_sel1:
            prov_a = st.selectbox("Provinsi A:", semua_prov_list, index=0, key="prov_a")
        with col_sel2:
            prov_b = st.selectbox(
                "Provinsi B:",
                semua_prov_list,
                index=min(1, len(semua_prov_list) - 1),
                key="prov_b",
            )

        df_a = df[df["provinsi"] == prov_a]
        df_b = df[df["provinsi"] == prov_b]

        metrik_banding = {
            "Penerima Manfaat": "jumlah_penerima_manfaat",
            "Peserta Didik Laki-laki": "jumlah_laki",
            "Peserta Didik Perempuan": "jumlah_perempuan",
            "Kondisi Khusus": "jumlah_kondisi_khusus",
            "Alergi": "jumlah_alergi",
            "Fobia Makanan": "jumlah_fobia",
            "Intoleransi": "jumlah_intoleransi",
            "Satuan Pendidikan": "jumlah_satuan_pendidikan",
        }

        # KPI perbandingan
        st.markdown(f"#### Perbandingan: **{prov_a}** vs **{prov_b}**")
        baris = []
        for nama, col in metrik_banding.items():
            val_a = int(df_a[col].sum())
            val_b = int(df_b[col].sum())
            baris.append(
                {"Metrik": nama, prov_a: val_a, prov_b: val_b, "Selisih": val_a - val_b}
            )
        df_banding = pd.DataFrame(baris)

        st.dataframe(
            df_banding.style.format(
                {prov_a: "{:,}", prov_b: "{:,}", "Selisih": "{:,}"}
            ),
            use_container_width=True,
            hide_index=True,
        )

        # Chart perbandingan
        df_banding_melt = df_banding.melt(
            id_vars="Metrik",
            value_vars=[prov_a, prov_b],
            var_name="Provinsi",
            value_name="Nilai",
        )
        fig = px.bar(
            df_banding_melt,
            x="Metrik",
            y="Nilai",
            color="Provinsi",
            barmode="group",
            title=f"Perbandingan {prov_a} vs {prov_b}",
            labels={"Nilai": "Jumlah", "Metrik": "Indikator"},
        )
        fig.update_layout(xaxis_tickangle=-30)
        st.plotly_chart(fig, use_container_width=True)

        # Radar perbandingan
        metrik_radar = list(metrik_banding.keys())
        val_a_list = [int(df_a[col].sum()) for col in metrik_banding.values()]
        val_b_list = [int(df_b[col].sum()) for col in metrik_banding.values()]
        max_vals = [max(a, b) for a, b in zip(val_a_list, val_b_list)]
        norm_a = [v / m * 100 if m > 0 else 0 for v, m in zip(val_a_list, max_vals)]
        norm_b = [v / m * 100 if m > 0 else 0 for v, m in zip(val_b_list, max_vals)]

        fig_radar = go.Figure()
        fig_radar.add_trace(
            go.Scatterpolar(
                r=norm_a + [norm_a[0]],
                theta=metrik_radar + [metrik_radar[0]],
                fill="toself",
                name=prov_a,
                line_color="#1f77b4",
            )
        )
        fig_radar.add_trace(
            go.Scatterpolar(
                r=norm_b + [norm_b[0]],
                theta=metrik_radar + [metrik_radar[0]],
                fill="toself",
                name=prov_b,
                line_color="#d62728",
            )
        )
        fig_radar.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
            title=f"Radar Chart Perbandingan: {prov_a} vs {prov_b} (Dinormalisasi)",
            height=450,
        )
        st.plotly_chart(fig_radar, use_container_width=True)

        # Perbandingan per jenjang
        df_aj = (
            df_a.groupby("jenjang", as_index=False)["jumlah_penerima_manfaat"]
            .sum()
            .assign(Provinsi=prov_a)
        )
        df_bj = (
            df_b.groupby("jenjang", as_index=False)["jumlah_penerima_manfaat"]
            .sum()
            .assign(Provinsi=prov_b)
        )
        df_abj = pd.concat([df_aj, df_bj])
        fig = px.bar(
            df_abj,
            x="jenjang",
            y="jumlah_penerima_manfaat",
            color="Provinsi",
            barmode="group",
            title=f"Penerima Manfaat per Jenjang: {prov_a} vs {prov_b}",
            labels={
                "jumlah_penerima_manfaat": "Penerima Manfaat",
                "jenjang": "Jenjang",
            },
        )
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # ── PARETO & LORENZ ────────────────────────────────────────────────────────
    st.markdown("### Distribusi & Ketimpangan")

    df_pareto = df.groupby("provinsi", as_index=False)["jumlah_penerima_manfaat"].sum()
    df_pareto = df_pareto.sort_values("jumlah_penerima_manfaat", ascending=False)
    df_pareto["kumulatif_persen"] = (
        df_pareto["jumlah_penerima_manfaat"].cumsum()
        / df_pareto["jumlah_penerima_manfaat"].sum()
        * 100
    ).round(2)

    c1, c2 = st.columns(2)
    with c1:
        fig = go.Figure()
        fig.add_trace(
            go.Bar(
                x=df_pareto["provinsi"],
                y=df_pareto["jumlah_penerima_manfaat"],
                name="Penerima Manfaat",
                marker_color="#1f77b4",
            )
        )
        fig.add_trace(
            go.Scatter(
                x=df_pareto["provinsi"],
                y=df_pareto["kumulatif_persen"],
                name="Kumulatif (%)",
                yaxis="y2",
                line=dict(color="red"),
                mode="lines+markers",
            )
        )
        fig.update_layout(
            title="Pareto — Penerima Manfaat per Provinsi",
            yaxis=dict(title="Penerima Manfaat"),
            yaxis2=dict(
                title="Kumulatif (%)", overlaying="y", side="right", range=[0, 110]
            ),
            xaxis_tickangle=-45,
            height=420,
            legend=dict(orientation="h", y=1.08),
        )
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        arr = np.sort(df_pareto["jumlah_penerima_manfaat"].values)
        lorenz = np.insert(np.cumsum(arr) / arr.sum(), 0, 0)
        x_eq = np.linspace(0, 1, len(lorenz))
        gini = round(1 - 2 * np.trapezoid(lorenz, x_eq), 3)
        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                x=x_eq,
                y=lorenz,
                fill="tonexty",
                name="Distribusi aktual",
                line_color="#1f77b4",
            )
        )
        fig.add_trace(
            go.Scatter(
                x=[0, 1],
                y=[0, 1],
                name="Distribusi merata",
                line=dict(color="red", dash="dash"),
            )
        )
        fig.update_layout(
            title=f"Kurva Lorenz — Ketimpangan Distribusi Penerima Manfaat (Gini = {gini})",
            xaxis_title="Proporsi Kumulatif Provinsi",
            yaxis_title="Proporsi Kumulatif Penerima Manfaat",
            height=420,
        )
        st.plotly_chart(fig, use_container_width=True)

    ketimpangan = "Tinggi" if gini > 0.4 else "Sedang" if gini > 0.25 else "Merata"
    st.info(f"""
**Insight Tren & Ketimpangan:**
- Koefisien Gini: **{gini}** → Ketimpangan distribusi penerima manfaat antar provinsi: **{ketimpangan}**
- Sebagian kecil provinsi menyerap mayoritas penerima manfaat (lihat Pareto)
    """)

    # ── BOX PLOT ───────────────────────────────────────────────────────────────
    st.markdown("### Sebaran Data per Jenjang")
    c3, c4 = st.columns(2)
    with c3:
        fig = px.box(
            df,
            x="jenjang",
            y="jumlah_penerima_manfaat",
            color="jenjang",
            title="Sebaran Penerima Manfaat per Jenjang",
            labels={
                "jumlah_penerima_manfaat": "Penerima Manfaat",
                "jenjang": "Jenjang",
            },
        )
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    with c4:
        fig = px.box(
            df,
            x="jenjang",
            y="jumlah_kondisi_khusus",
            color="jenjang",
            title="Sebaran Kondisi Khusus per Jenjang",
            labels={"jumlah_kondisi_khusus": "Kondisi Khusus", "jenjang": "Jenjang"},
        )
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
from pathlib import Path
import pandas as pd
import json
import streamlit as st

@st.cache_data
def load_data():
    base = Path(__file__).resolve().parent
    csv_path = base / "MASTER_DATASET_MBG_BI2026.csv"
    df = pd.read_csv(csv_path)

    # Modify/Standardize Date dengan format='mixed' agar tidak error
    if 'date_pull' in df.columns:
        df['date_pull'] = pd.to_datetime(df['date_pull'], format='mixed', errors='coerce')

    # Feature Engineering
    for col in ["jumlah_alergi", "jumlah_fobia", "jumlah_intoleransi"]:
        if col not in df.columns:
            df[col] = 0
    df["total_risiko"] = (df["jumlah_alergi"] + df["jumlah_fobia"] + df["jumlah_intoleransi"])

    # Normalisasi Provinsi untuk Peta
    if 'provinsi' in df.columns:
        df["provinsi_map"] = df["provinsi"].astype(str).str.replace("Prov. ", "", regex=False)
        df["provinsi_map"] = df["provinsi_map"].replace({
            "D.K.I. Jakarta": "DKI Jakarta",
            "D.I. Yogyakarta": "DI Yogyakarta"
        })

    return df

@st.cache_data
def load_geojson():
    base = Path(__file__).resolve().parent
    geo_path = base / "38 Provinsi Indonesia - Provinsi.json"
    with open(geo_path, "r", encoding="utf-8") as f:
        return json.load(f)
import pandas as pd
import json
import streamlit as st

@st.cache_data
def load_data():
    df = pd.read_csv("MASTER_DATASET_MBG_BI2026.csv")
    
    # Modify/Standardize Date dengan format='mixed' agar tidak error
    df['date_pull'] = pd.to_datetime(df['date_pull'], format='mixed')
    
    # Feature Engineering
    df["total_risiko"] = (df["jumlah_alergi"] + df["jumlah_fobia"] + df["jumlah_intoleransi"])
    
    # Normalisasi Provinsi untuk Peta
    df["provinsi_map"] = df["provinsi"].str.replace("Prov. ", "", regex=False)
    df["provinsi_map"] = df["provinsi_map"].replace({
        "D.K.I. Jakarta": "DKI Jakarta",
        "D.I. Yogyakarta": "DI Yogyakarta"
    })
    
    return df

@st.cache_data
def load_geojson():
    with open("38 Provinsi Indonesia - Provinsi.json", "r", encoding="utf-8") as f:
        return json.load(f)
import streamlit as st

st.set_page_config(
    page_title="Dashboard MBG Indonesia",
    page_icon="🍲",
    layout="wide"
)

st.image("https://images.unsplash.com/photo-1577896851231-70ef18881754?q=80&w=2070&auto=format&fit=crop", use_column_width=True)
st.title("Sistem Informasi Makan Bergizi Gratis (MBG)")
st.markdown("---")

# Define pages
pg_nasional = st.Page("pages/1_Nasional.py", title="Dashboard General", icon="🇮🇩")
pg_provinsi = st.Page("pages/2_Provinsi.py", title="Insight Per Provinsi", icon="📍")

# Setup Navigation
pg = st.navigation([pg_nasional, pg_provinsi])
pg.run()
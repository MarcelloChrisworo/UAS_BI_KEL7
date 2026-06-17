import streamlit as st
import runpy
from pathlib import Path

st.set_page_config(
    page_title="Dashboard MBG Indonesia",
    page_icon="🍲",
    layout="wide"
)

# Use `width` instead of the deprecated `use_column_width`
st.image(
    "https://akcdn.detik.net.id/visual/2025/05/07/sejumlah-siswa-saat-pelaksanaan-program-cek-kesehatan-gratis-untuk-sekolah-dan-remaja-di-sdn-jati-03-pagi-pulo-gadung-jakarta--1746599011863_169.jpeg?w=900&q=80",
    width=900,
)
st.title("Sistem Informasi Makan Bergizi Gratis (MBG)")
st.markdown("---")

# Simple navigation: run the desired page script from the `pages/` folder
base_dir = Path(__file__).resolve().parent
pages = {
    "Dashboard General": str(base_dir / "_pages" / "1_Nasional.py"),
    "Insight Per Provinsi": str(base_dir / "_pages" / "2_Provinsi.py"),
}

st.sidebar.title("Navigation")
main_options = ["Ringkasan Statistik"] + list(pages.keys())
selection = st.sidebar.radio("Pilih halaman:", main_options, index=0)

if selection in pages:
    runpy.run_path(pages[selection], run_name="__main__")
elif selection == "Ringkasan Statistik":
    st.header("Ringkasan Statistik — MBG Dataset")
    from utils import load_data
    import pandas as pd

    df = load_data()

    # Ringkasan metrik utama
    n_rows, n_cols = df.shape
    year_vals = df['tahun'].dropna().unique() if 'tahun' in df.columns else []
    year_text = ', '.join(map(str, year_vals[:3])) if len(year_vals) > 0 else 'N/A'
    n_prov = int(df['provinsi'].nunique()) if 'provinsi' in df.columns else 'N/A'

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Baris", f"{n_rows}")
    c2.metric("Kolom / Variabel", f"{n_cols}")
    c3.metric("Tahun Data", year_text)
    c4.metric("Provinsi", f"{n_prov}")

    st.markdown("---")

    # Deskripsi singkat
    st.subheader("Deskripsi Dataset")
    st.markdown(
        "- Dataset memuat data agregat tahun terkait infrastruktur pendidikan dan demografi siswa.\n"
        "- Unit pengamatan: tingkat Kecamatan per Jenjang Pendidikan.\n"
        "- Kolom utama: demografi (laki/perempuan), indikator kesehatan (alergi, fobia, intoleransi), jumlah penerima manfaat, dsb."
    )

    st.subheader("Statistik Deskriptif")
    # Tampilkan ringkasan numerik dan missing count
    if n_rows > 0:
        num_desc = df.select_dtypes(include=['number']).describe().T
        st.dataframe(num_desc)

        st.subheader("Jumlah Nilai Hilang per Kolom")
        missing = df.isna().sum().rename('missing').to_frame()
        missing['percent'] = (missing['missing'] / n_rows * 100).round(2)
        st.dataframe(missing.sort_values('missing', ascending=False))

        st.subheader("Contoh Data (5 baris)")
        st.dataframe(df.head())

        # Kamus Data (ringkasan arti nama kolom)
        st.subheader("Kamus Data")
        col_descriptions = {
            'jumlah_penerima_manfaat': 'Jumlah total penerima manfaat program',
            'jumlah_satuan_pendidikan': 'Jumlah satuan pendidikan yang terlibat',
            'jumlah_kondisi_khusus': 'Jumlah peserta dengan kondisi khusus',
            'jumlah_satpen_negeri': 'Jumlah satuan pendidikan negeri',
            'jumlah_satpen_swasta': 'Jumlah satuan pendidikan swasta',
            'jumlah_laki': 'Jumlah peserta laki-laki',
            'jumlah_perempuan': 'Jumlah peserta perempuan',
            'provinsi': 'Nama provinsi',
            'jenjang': 'Jenjang pendidikan (SD/SMP/SMA dll)',
            'date_pull': 'Tanggal data diambil'
        }

        kamus_rows = []
        for col in df.columns:
            desc = col_descriptions.get(col, '')
            if not desc:
                # generate simple fallback description
                desc = col.replace('_', ' ').capitalize()
            kamus_rows.append({'kolom': col, 'arti': desc})

        kamus_df = __import__('pandas').DataFrame(kamus_rows)
        # ensure simple string columns to avoid pyarrow conversion issues
        kamus_df['kolom'] = kamus_df['kolom'].astype(str)
        kamus_df['arti'] = kamus_df['arti'].astype(str)
        st.dataframe(kamus_df)
    else:
        st.info("Dataset kosong — tidak ada baris untuk ditampilkan.")

        
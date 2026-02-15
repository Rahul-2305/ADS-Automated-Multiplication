import streamlit as st
import altair as alt 
import pandas as pd
import numpy as np 
import re
import time
from datetime import datetime
import os
from io import BytesIO
import zipfile

## FUNCTION ZONE STARTS - DO NOT TOUCH ANYTHING HERE ###

def rename_file(file_name):
    base_name, ext = os.path.splitext(file_name)
    version_pattern = r'_V(\d+)$'
    match = re.search(version_pattern, base_name)
    if match:
        new_version = int(match.group(1)) + 1
        new_base = base_name[:match.start()] + f"_V{new_version}"
    else:
        new_version = 1
        new_base = base_name + "_V1"

    return new_base + ext, f"V{new_version}"

def apply_factor_logic(ads_df, factor_df):
    ads_df = ads_df.copy()
    for cols in factor_df.columns[1:]:
        for year in factor_df["Year"]:
            factor_value = factor_df[factor_df["Year"] == year][cols].values[0]
            if cols in ads_df.columns and year in ads_df["Mapping"].values:
                col_to_mod = [cols]
                ads_df.loc[ads_df["Mapping"] == year, col_to_mod] *= factor_value
    
    return ads_df

## FUNCTION ZONE ENDS - DO NOT TOUCH HERE ###

# ======================
# MAIN APP
# ======================

start_time = time.perf_counter()

st.header("ADS Automated Multiplication V2.0")
st.write("Useful for PMF multiplication, Support Multiplication etc.")
st.info("Now upload multiple ADS and 1 factor file only")
st.warning('Can maybe run 4 or 5 files in deployed mode but in local mode, can run more models', icon="⚠️")

st.markdown(
    """
    <div style='text-align: center; margin-top: 10px; margin-bottom: 10px;'>
        <a href="https://github.com/Rahul-2305/ADS-Automated-Multiplication/tree/main" target="_blank">
            <button style="
                background-color:#063970;
                color:white;
                padding:10px 20px;
                border:none;
                border-radius:8px;
                font-size:16px;
                cursor:pointer;">
                HOW TO USE ?
            </button>
        </a>
    </div>
    """,
    unsafe_allow_html=True
)


uploaded_files = st.file_uploader(
    "Upload ADS CSV files",
    accept_multiple_files=True,
    type=["csv"]
)

factor_file = st.file_uploader(
    "Upload Factor Excel File (Multi-Sheet Supported)",
    type=["xlsx"]
)

processed_outputs = []

if uploaded_files and factor_file:

    excel_file = pd.ExcelFile(factor_file, engine="openpyxl")
    available_sheets = excel_file.sheet_names

    st.success("Files loaded successfully")
    st.write("Available Sheets in Factor File:", available_sheets)

    st.subheader("Map Each ADS to a Factor Sheet")

    sheet_mapping = {}

    st.markdown("###")

    # Centered layout container
    left_spacer, main_container, right_spacer = st.columns([1, 4, 1])

    with main_container:

        for file in uploaded_files:

            row_col1, row_col2 = st.columns([3, 2])

            with row_col1:
                st.markdown(
                    f"<div style='padding-top:8px; font-size:18px; font-weight:500;'>"
                    f"{file.name}</div>",
                    unsafe_allow_html=True
                )

            with row_col2:
                selected_sheet = st.selectbox(
                    "",
                    options=available_sheets,
                    key=file.name
                )

            sheet_mapping[file.name] = selected_sheet

            st.markdown(
                "<hr style='margin-top:8px; margin-bottom:8px;'>",
                unsafe_allow_html=True
            )

    st.markdown("###")

    if st.button("🚀 Start Processing"):

        progress = st.progress(0)
        step = 100 // len(uploaded_files)

        for i, file in enumerate(uploaded_files):

            ads_df = pd.read_csv(file)
            selected_sheet = sheet_mapping[file.name]

            factor_df = pd.read_excel(
                excel_file,
                sheet_name=selected_sheet
            )

            output_df = apply_factor_logic(ads_df, factor_df)

            processed_outputs.append({
                "name": file.name,
                "df": output_df
            })

            progress.progress(min((i + 1) * step, 100))

        st.success("Processing Completed ✅")


if processed_outputs:

    st.header("Download Output")

    zip_buffer = BytesIO()

    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zipf:
        for item in processed_outputs:

            new_name, folder = rename_file(item["name"])

            csv_buffer = BytesIO()
            item["df"].to_csv(csv_buffer, index=False)
            csv_buffer.seek(0)

            zipf.writestr(f"{folder}/{new_name}", csv_buffer.getvalue())

    zip_buffer.seek(0)

    st.download_button(
        label="⬇️ Download All Processed Files (ZIP)",
        data=zip_buffer,
        file_name=f"ADS_Multiplied_Output_{datetime.now().strftime('%m-%d-%Y')}.zip",
        mime="application/zip"
    )


end_time = time.perf_counter()
runtime = end_time - start_time
st.caption(f"Process took {runtime:.2f} seconds")

with st.expander("About this App"):
    st.write("Created by Beeraboina Rahul")
    st.write("Made in Python & Streamlit")
    st.write("Know more about Beeraboina Rahul at https://rahul-2305.github.io/Website/")

col1, col2 = st.columns(2)

left, center, right = st.columns([1, 2, 1])

with center:
    col1, col2 = st.columns(2)

    with col1:
        if st.button("🎈 Want some Balloons"):
            st.balloons()

    with col2:
        if st.button("❄️ Want some Snow"):
            st.snow()


st.caption("© 2025 Beeraboina Rahul")


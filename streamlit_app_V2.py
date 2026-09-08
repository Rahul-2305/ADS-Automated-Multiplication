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

            factor_value = factor_df[
                factor_df["Year"] == year
            ][cols].values[0]

            if cols in ads_df.columns and year in ads_df["Mapping"].values:

                # Only modify the actual multiplication column.
                # Do NOT convert the complete ADS dataframe.
                mask = ads_df["Mapping"] == year

                # Convert only this target column to a multiplication-safe
                # numeric dtype. Other columns such as Period, Geography,
                # G_P, Mapping, etc. remain completely untouched.
                ads_df[cols] = pd.to_numeric(
                    ads_df[cols],
                    errors="raise"
                ).astype(float)

                ads_df.loc[mask, cols] = (
                    ads_df.loc[mask, cols] * factor_value
                )

    return ads_df


## FUNCTION ZONE ENDS - DO NOT TOUCH HERE ###


# ======================
# MAIN APP
# ======================

start_time = time.perf_counter()

st.header("ADS Automated Multiplication V2.0")

st.write(
    "Useful for PMF multiplication, Support Multiplication etc."
)

st.info(
    "Now upload multiple ADS and 1 factor file only"
)

st.warning(
    "Can maybe run 4 or 5 files in deployed mode but in local mode, "
    "can run more models",
    icon="⚠️"
)


st.markdown(
    """
    <div style='text-align: center; margin-top: 10px; margin-bottom: 10px;'>
        <a href="https://github.com/Rahul-2305/ADS-Automated-Multiplication/tree/main"
           target="_blank">
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


# ======================
# FILE UPLOAD
# ======================

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


# ======================
# PROCESSING
# ======================

if uploaded_files and factor_file:

    excel_file = pd.ExcelFile(
        factor_file,
        engine="openpyxl"
    )

    available_sheets = excel_file.sheet_names

    st.success("Files loaded successfully")

    st.write(
        "Available Sheets in Factor File:",
        available_sheets
    )


    st.subheader("Map Each ADS to a Factor Sheet")

    sheet_mapping = {}

    st.markdown("###")


    # ======================
    # FILE → SHEET MAPPING
    # ======================

    left_spacer, main_container, right_spacer = st.columns(
        [1, 4, 1]
    )

    with main_container:

        for file in uploaded_files:

            row_col1, row_col2 = st.columns(
                [3, 2]
            )

            with row_col1:

                st.markdown(
                    f"""
                    <div style='
                        padding-top:8px;
                        font-size:18px;
                        font-weight:500;
                    '>
                        {file.name}
                    </div>
                    """,
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


    # ======================
    # START PROCESSING
    # ======================

    if st.button("🚀 Start Processing"):

        processing_start = time.perf_counter()

        progress = st.progress(0)

        status_text = st.empty()

        total_files = len(uploaded_files)


        for i, file in enumerate(uploaded_files):

            file_start = time.perf_counter()

            status_text.write(
                f"Processing {file.name} "
                f"({i + 1}/{total_files})..."
            )


            # ----------------------
            # READ ADS
            # ----------------------

            ads_df = pd.read_csv(file)


            # ----------------------
            # READ FACTOR SHEET
            # ----------------------

            selected_sheet = sheet_mapping[file.name]

            factor_df = pd.read_excel(
                excel_file,
                sheet_name=selected_sheet
            )


            # ----------------------
            # APPLY MULTIPLICATION
            # ----------------------

            output_df = apply_factor_logic(
                ads_df,
                factor_df
            )


            # ----------------------
            # STORE OUTPUT
            # ----------------------

            processed_outputs.append(
                {
                    "name": file.name,
                    "df": output_df
                }
            )


            # ----------------------
            # PROGRESS
            # ----------------------

            percentage = int(
                ((i + 1) / total_files) * 100
            )

            progress.progress(
                percentage
            )


            file_time = (
                time.perf_counter()
                - file_start
            )

            status_text.write(
                f"Completed {file.name} "
                f"({file_time:.2f} sec)"
            )


        total_processing_time = (
            time.perf_counter()
            - processing_start
        )


        progress.progress(100)

        st.success(
            f"Processing Completed ✅ "
            f"in {total_processing_time:.2f} seconds"
        )

        status_text.empty()


# ======================
# DOWNLOAD OUTPUT
# ======================

if processed_outputs:

    st.header("Download Output")


    zip_buffer = BytesIO()


    with zipfile.ZipFile(
        zip_buffer,
        "w",
        zipfile.ZIP_DEFLATED
    ) as zipf:

        for item in processed_outputs:

            new_name, folder = rename_file(
                item["name"]
            )


            csv_buffer = BytesIO()

            item["df"].to_csv(
                csv_buffer,
                index=False
            )

            csv_buffer.seek(0)


            zipf.writestr(
                f"{folder}/{new_name}",
                csv_buffer.getvalue()
            )


    zip_buffer.seek(0)


    st.download_button(
        label="⬇️ Download All Processed Files (ZIP)",
        data=zip_buffer,
        file_name=(
            f"ADS_Multiplied_Output_"
            f"{datetime.now().strftime('%m-%d-%Y')}.zip"
        ),
        mime="application/zip"
    )


# ======================
# RUNTIME
# ======================

end_time = time.perf_counter()

runtime = end_time - start_time

st.caption(
    f"Process took {runtime:.2f} seconds"
)


# ======================
# ABOUT
# ======================

with st.expander("About this App"):

    st.write("Created by Beeraboina Rahul")

    st.write(
        "Made in Python & Streamlit"
    )

    st.write(
        "Know more about Beeraboina Rahul at "
        "https://beeraboina-rahul-website.streamlit.app/"
    )


# ======================
# FUN BUTTONS
# ======================

left, center, right = st.columns(
    [1, 2, 1]
)

with center:

    col1, col2 = st.columns(2)


    with col1:

        if st.button("🎈 Want some Balloons"):

            st.balloons()


    with col2:

        if st.button("❄️ Want some Snow"):

            st.snow()


st.caption("© 2025 Beeraboina Rahul")

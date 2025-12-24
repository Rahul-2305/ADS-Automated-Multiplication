import streamlit as st
import altair as alt 
import pandas as pd
import numpy as np 
import re
import time
from datetime import time, datetime
import time
import os
from io import BytesIO
import zipfile

## FUNCTION ZONE STARTS - DO NOT TOUCH ANYTHING HERE ###

#   FILE_RENAMING VERSION FUNCTION
## + Searches for a String V_{some_number} in the file name for knowing the version.
## + If no V_{some_number}, Then assigns a V_1 to the file name,
## + If a V_{some_number} is present, then increments it by 1

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

#    FACTOR LOGIC
##   Multiplies a certain factor in the support stream in a particulat time period
##   Fastens up the process

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

start_time = time.perf_counter()
st.header("ADS Automated multiplication")
st.write("")
st.write("Useful for PMF multiplication, Support Multiplication etc.")

st.subheader('Please input your ADS file/files here')

uploaded_files = st.file_uploader("Please select CSV files only",
                                 accept_multiple_files=True,
                                 type=["csv"])


st.subheader('Please input your Factor Sheet for multiplication')
with st.expander("Don't know what factor sheets is ?"):
    st.write("This is for multiplying factors into ADS for adjusting the Support Stream.")
    st.write("It can be any variable as long as you know the variable name")
    st.write("Here is what your input factor sheet should look like:")
    st.image("https://private-user-images.githubusercontent.com/83655233/529969021-face185d-ee66-4346-b56e-ec1c6eb5b989.png?jwt=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3NjY1NzEyNDAsIm5iZiI6MTc2NjU3MDk0MCwicGF0aCI6Ii84MzY1NTIzMy81Mjk5NjkwMjEtZmFjZTE4NWQtZWU2Ni00MzQ2LWI1NmUtZWMxYzZlYjViOTg5LnBuZz9YLUFtei1BbGdvcml0aG09QVdTNC1ITUFDLVNIQTI1NiZYLUFtei1DcmVkZW50aWFsPUFLSUFWQ09EWUxTQTUzUFFLNFpBJTJGMjAyNTEyMjQlMkZ1cy1lYXN0LTElMkZzMyUyRmF3czRfcmVxdWVzdCZYLUFtei1EYXRlPTIwMjUxMjI0VDEwMDkwMFomWC1BbXotRXhwaXJlcz0zMDAmWC1BbXotU2lnbmF0dXJlPWViM2Q3NzE3N2E3ZWIwNzhhOTU5ZThjYmY2OWM2ODJlZDQ5NDZiMDFlZmY4N2M0ZTRjYTg3MmRjMWFiZDMxODgmWC1BbXotU2lnbmVkSGVhZGVycz1ob3N0In0.RR-Jl2CdSAsCad5pmzbyTAD7crrWv0Kc9tSMz54solI")
    st.write("If Image is unavailable, then refer to the this link :https://github.com/Rahul-2305/ADS-Automated-Multiplication:")

factor_file = st.file_uploader("Please select a xlsx file only")

processed_outputs = []

if uploaded_files and factor_file:
  factor_df = pd.read_excel(factor_file, engine="openpyxl")
  st.success(f"{len(uploaded_files)} ADS files + Factor file loaded")

  progress = st.progress(0)
  step = 100 // len(uploaded_files)

  for i, file in enumerate(uploaded_files):
      ads_df = pd.read_csv(file)
      output_df = apply_factor_logic(ads_df, factor_df)
      processed_outputs.append({
            "name": file.name,
            "df": output_df
        })
      progress.progress(min((i + 1) * step, 100))

if processed_outputs:
    st.header("Output")
    
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
st.write(f"Process took {runtime:.2f} second")

with st.expander("About this App"):
  st.write("Created by Beeraboina Rahul")
  st.write("Made in Python & Streamlit")
  st.write("Click on the below link to know more about Beeraboina Rahul")
  st.write("https://rahul-2305.github.io/Website/")


if st.button("Want some balloons 🎈"):
    st.balloons() 

st.caption("© 2025 Beeraboina Rahul")



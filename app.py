import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="Online Retail Dashboard",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Online Retail Automated Reporting")
st.markdown("### Sales Dashboard")

# --------------------------------------------------
# UPLOAD DATASET
# --------------------------------------------------

st.sidebar.header("📂 Upload Dataset")

uploaded_file = st.sidebar.file_uploader(
    "Choose the Online Retail II Excel file",
    type=["xlsx"]
)

if uploaded_file is None:
    st.info("Please upload the Online Retail II Excel file to continue.")
    st.stop()

# --------------------------------------------------
# LOAD EXCEL SHEETS
# --------------------------------------------------

xls = pd.ExcelFile(uploaded_file)

df_2009 = pd.read_excel(xls, sheet_name="Year 2009-2010")
df_2010 = pd.read_excel(xls, sheet_name="Year 2010-2011")
# --------------------------------------------------
# REPORTING PERIOD FILTER
# --------------------------------------------------
st.sidebar.header("📅 Reporting Period")
selected_period = st.sidebar.selectbox(
    "Select Reporting Period",
    ["Both Years", "Year 2009-2010", "Year 2010-2011"]
)
if selected_period == "Both Years":
    df = pd.concat([df_2009, df_2010], ignore_index=True)
elif selected_period == "Year 2009-2010":
    df = df_2009.copy()
else:
    df = df_2010.copy()

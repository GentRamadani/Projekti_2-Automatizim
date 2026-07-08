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


# --------------------------------------------------
# PREVIOUS PERIOD FOR COMPARISON
# --------------------------------------------------

if selected_period == "Year 2010-2011":
    df_prev = df_2009.copy()
elif selected_period == "Year 2009-2010":
    df_prev = df_2010.copy()
else:
    df_prev = df_2009.copy()


# --------------------------------------------------
# DATA CLEANING FUNCTION
# --------------------------------------------------

def clean_data(data):
    data = data.copy()
    data["Customer ID"] = data["Customer ID"].fillna("Unknown")
    data["Description"] = data["Description"].fillna("Unknown")
    data = data.drop_duplicates()
    data = data[data["Quantity"] > 0]
    data = data[data["Price"] > 0]
    data["InvoiceDate"] = pd.to_datetime(data["InvoiceDate"])
    data["Revenue"] = data["Quantity"] * data["Price"]
    return data

df_clean = clean_data(df)
df_prev_clean = clean_data(df_prev)

# --------------------------------------------------
# KPI CALCULATION FUNCTION
# --------------------------------------------------

def calculate_kpis(data):
    revenue = data["Revenue"].sum()
    orders = data["Invoice"].nunique()
    customers = data[data["Customer ID"] != "Unknown"]["Customer ID"].nunique()
    anonymous = data[data["Customer ID"] == "Unknown"]["Invoice"].nunique()
    products = data["Quantity"].sum()
    return revenue, orders, customers, anonymous, products

# CURRENT KPIs
curr_revenue, curr_orders, curr_customers, curr_anonymous, curr_products = calculate_kpis(df_clean)

# PREVIOUS KPIs
prev_revenue, prev_orders, prev_customers, prev_anonymous, prev_products = calculate_kpis(df_prev_clean)

# --------------------------------------------------
# % CHANGE FUNCTION
# --------------------------------------------------

def pct_change(current, previous):
    if previous == 0:
        return 0
    return ((current - previous) / previous) * 100

# --------------------------------------------------
# KPI CARDS
# --------------------------------------------------

st.markdown("---")
st.subheader("📌 Key Performance Indicators (vs Previous Period)")

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    if selected_period == "Both Years":
        st.metric("💰 Total Revenue", f"£{curr_revenue:,.2f}")
    else:
        st.metric("💰 Total Revenue", f"£{curr_revenue:,.2f}",
                  f"{pct_change(curr_revenue, prev_revenue):+.1f}%")

with col2:
    if selected_period == "Both Years":
        st.metric("🧾 Total Orders", f"{curr_orders:,}")
    else:
        st.metric("🧾 Total Orders", f"{curr_orders:,}",
                  f"{pct_change(curr_orders, prev_orders):+.1f}%")

with col3:
    if selected_period == "Both Years":
        st.metric("👥 Total Customers", f"{curr_customers:,}")
    else:
        st.metric("👥 Total Customers", f"{curr_customers:,}",
                  f"{pct_change(curr_customers, prev_customers):+.1f}%")

with col4:
    if selected_period == "Both Years":
        st.metric("🕵️ Anonymous Customers", f"{curr_anonymous:,}")
    else:
        st.metric("🕵️ Anonymous Customers", f"{curr_anonymous:,}",
                  f"{pct_change(curr_anonymous, prev_anonymous):+.1f}%")

with col5:
    if selected_period == "Both Years":
        st.metric("📦 Products Sold", f"{curr_products:,}")
    else:
        st.metric("📦 Products Sold", f"{curr_products:,}",
                  f"{pct_change(curr_products, prev_products):+.1f}%")
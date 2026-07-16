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

sheet_names = xls.sheet_names

dfs = {}

for sheet in sheet_names:
    temp = pd.read_excel(xls, sheet_name=sheet)
    temp["Sheet"] = sheet
    dfs[sheet] = temp

# --------------------------------------------------
# REPORTING PERIOD FILTER
# --------------------------------------------------

st.sidebar.header("📅 Select Sheets")

selected_sheets = st.sidebar.multiselect(
    "Choose one or more sheets",
    options=sheet_names,
    default=sheet_names
)

if len(selected_sheets) == 0:
    st.warning("Please select at least one sheet.")
    st.stop()

df = pd.concat(
    [dfs[sheet] for sheet in selected_sheets],
    ignore_index=True
)

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

# --------------------------------------------------
# KPI CARDS
# --------------------------------------------------

st.markdown("---")
st.subheader("📌 Key Performance Indicators")

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric(
        "💰 Total Revenue",
        f"£{curr_revenue:,.2f}"
    )

with col2:
    st.metric(
        "🧾 Total Orders",
        f"{curr_orders:,}"
    )

with col3:
    st.metric(
        "👥 Total Customers",
        f"{curr_customers:,}"
    )

with col4:
    st.metric(
        "🕵️ Anonymous Customers",
        f"{curr_anonymous:,}"
    )

with col5:
    st.metric(
        "📦 Products Sold",
        f"{curr_products:,}"
    )

st.markdown("---")


tab1, tab2, tab3 = st.tabs([
    "📅 Monthly",
    "📦 Products",
    "🌍 Countries"
])


# --------------------------------------------------
# MONTHLY ANALYSIS
# --------------------------------------------------

with tab1:

    df_clean["YearMonth"] = df_clean["InvoiceDate"].dt.to_period("M")

    monthly_revenue = (
        df_clean.groupby("YearMonth")["Revenue"]
        .sum()
        .reset_index()
    )

    monthly_revenue["YearMonth"] = monthly_revenue["YearMonth"].astype(str)


    st.subheader("📈 Monthly Revenue Trend")

    fig, ax = plt.subplots(figsize=(12,5))

    sns.lineplot(
        data=monthly_revenue,
        x="YearMonth",
        y="Revenue",
        marker="o",
        color="#1f77b4",
        linewidth=2.5,
        ax=ax
    )

    fig.tight_layout()
    ax.set_title("Monthly Revenue Trend")
    ax.set_xlabel("Month")
    ax.set_ylabel("Revenue (£)")
    plt.xticks(rotation=45)

    st.pyplot(fig)

    st.subheader("📈 Përshkrimi i grafikut")

    st.write(
        """
Ky grafik paraqet ndryshimin e të ardhurave totale nga muaji në muaj gjatë periudhës së zgjedhur.

Ai ndihmon në identifikimin e muajve me performancë më të lartë ose më të ulët 
dhe tregon trendin e përgjithshëm të shitjeve.

**Shënim:** Boshti Y përdor formatin shkencor për vlera të mëdha.

Për shembull:
`1e6 = 1,000,000`, pra vlera 1.5 në grafik përfaqëson
£1,500,000 të ardhura.
"""
)

    


    # --------------------------------------------------
    # BEST PERFORMING MONTH ANALYSIS
    # --------------------------------------------------

    monthly_summary = (
        df_clean.groupby("YearMonth")
        .agg(
            Revenue=("Revenue", "sum"),
        )
        .reset_index()
    )

    best_month_name = monthly_summary.loc[
        monthly_summary["Revenue"].idxmax(),
        "YearMonth"
    ]

    best_month_data = df_clean[
        df_clean["YearMonth"] == best_month_name
    ]


    # --------------------------------------------------
    # BEST & WORST MONTH
    # --------------------------------------------------

    best_month = monthly_revenue.loc[
        monthly_revenue["Revenue"].idxmax()
    ]

    worst_month = monthly_revenue.loc[
        monthly_revenue["Revenue"].idxmin()
    ]


    # --------------------------------------------------
    # WORST MONTH DEEP ANALYSIS
    # --------------------------------------------------

    worst_month_name = worst_month["YearMonth"]

    worst_month_data = df_clean[
        df_clean["YearMonth"] == worst_month_name
    ]


    # Orders
    worst_orders = worst_month_data["Invoice"].nunique()


    # Customers
    worst_customers = (
        worst_month_data[
            worst_month_data["Customer ID"] != "Unknown"
        ]["Customer ID"]
        .nunique()
    )


    # Average Order Value
    worst_aov = (
        worst_month_data["Revenue"].sum()
        /
        worst_orders
    )


    # Top Products in worst month
    worst_top_products = (
        worst_month_data
        .groupby("Description")["Revenue"]
        .sum()
        .sort_values(ascending=False)
        .head(5)
    )


    st.markdown("---")

    st.subheader("🔎 Worst Month Analysis")


    st.write(
        f"""
### 📉 Weakest Month: {worst_month_name}

During this month:

- 🧾 Total Orders: **{worst_orders:,}**
- 👥 Active Customers: **{worst_customers:,}**
- 💳 Average Order Value: **£{worst_aov:,.2f}**

### 🏆 Top Products During This Month:
"""
    )


    st.dataframe(
        worst_top_products.reset_index()
        .rename(
            columns={
                "Description":"Product",
                "Revenue":"Revenue (£)"
            }
        )
    )


    st.markdown("---")
    st.subheader("🏆 Best & Worst Performing Month")

    col1, col2 = st.columns(2)

    with col1:
        st.success(
            f"""
### 🥇 Best Month

**{best_month['YearMonth']}**

Revenue: **£{best_month['Revenue']:,.2f}**
"""
        )

    with col2:
        st.error(
            f"""
### 📉 Worst Month

**{worst_month['YearMonth']}**

Revenue: **£{worst_month['Revenue']:,.2f}**
"""
        )



# --------------------------------------------------
# PRODUCTS
# --------------------------------------------------

with tab2:

    product_summary = (
        df_clean[
            (~df_clean["Description"].str.contains(
                "adjust|amazon|fee|manual|postage|discount|bank|bad debt",
                case=False,
                na=False
            ))
            &
            (df_clean["Description"] != "Unknown")
        ]
        .groupby("Description")
        .agg(
            Revenue=("Revenue", "sum"),
            Quantity=("Quantity", "sum")
        )
    )

    product_summary["Revenue per Unit"] = (
        product_summary["Revenue"] /
        product_summary["Quantity"]
    )

    product_summary = product_summary[
    product_summary["Quantity"] >= 10
]


    best_product_revenue = (
        product_summary
        .sort_values(
            by="Revenue",
            ascending=False
        )
        .index[0]
    )

    best_product_revenue_value = (
        product_summary
        .sort_values(
            by="Revenue",
            ascending=False
        )
        .iloc[0]["Revenue"]
    )


    best_product_quantity = (
        product_summary
        .sort_values(
            by="Quantity",
            ascending=False
        )
        .index[0]
    )

    best_product_quantity_value = (
        product_summary
        .sort_values(
            by="Quantity",
            ascending=False
        )
        .iloc[0]["Quantity"]
    )

    best_product_unit = (
        product_summary
        .sort_values(
            by="Revenue per Unit",
            ascending=False
        )
        .index[0]
    )

    best_product_unit_value = (
        product_summary
        .sort_values(
            by="Revenue per Unit",
            ascending=False
        )
        .iloc[0]["Revenue per Unit"]
    )

    st.subheader("⭐ Best Product Performance")


    col1, col2, col3 = st.columns(3)


    with col1:
        st.markdown("### 💰 Top Product (Revenue)")
        st.write(best_product_revenue)
        st.metric(
            "Revenue",
            f"£{best_product_revenue_value:,.2f}"
    )



    with col2:
        st.markdown("### 📦 Top Product (Quantity)")
        st.write(best_product_quantity)
        st.metric(
            "Quantity Sold",
            f"{best_product_quantity_value:,.0f} units"
        )

    with col3:
        st.markdown("### 💷 Highest Revenue per Unit")
        st.write(best_product_unit)
        st.metric(
            "Revenue per Unit",
            f"£{best_product_unit_value:,.2f} / unit"
        )


    st.markdown("---")


    # --------------------------------------------------
    # TOP 10 PRODUCTS
    # --------------------------------------------------

    top_products = (
        df_clean[
            (~df_clean["Description"].str.contains(
                "adjust|amazon|fee|manual|postage|discount|bank|bad debt",
                case=False,
                na=False
            ))
            &
            (df_clean["Description"] != "Unknown")
        ]
        .groupby("Description")["Revenue"]
        .sum()
        .sort_values(ascending=False)
        .head(10)
    )


    st.subheader("🏆 Top 10 Products by Revenue")


    fig, ax = plt.subplots(figsize=(12,6))


    sns.barplot(
        x=top_products.values,
        y=top_products.index,
        color="#ff7f0e",
        ax=ax
    )


    fig.tight_layout()

    ax.set_title("Top 10 Products by Revenue")
    ax.set_xlabel("Revenue (£)")
    ax.set_ylabel("Product")


    st.pyplot(fig)


    # --------------------------------------------------
    # TOP 10 PRODUCTS BY REVENUE PER UNIT
    # --------------------------------------------------

    top_unit_products = (
        product_summary[
            product_summary["Quantity"] >= 50
        ]
        .sort_values(
            by="Revenue per Unit",
            ascending=False
        )
        .head(10)
    )


    st.subheader("💷 Top 10 Products by Revenue per Unit")


    fig, ax = plt.subplots(figsize=(12,6))


    sns.barplot(
        data=top_unit_products.reset_index(),
        x="Revenue per Unit",
        y="Description",
        color="#9467bd",
        ax=ax
    )


    ax.set_title("Top 10 Products by Revenue per Unit")
    ax.set_xlabel("Revenue per Unit (£)")
    ax.set_ylabel("Product")


    fig.tight_layout()

    st.pyplot(fig)



# --------------------------------------------------
# COUNTRIES
# --------------------------------------------------

with tab3:

    top_countries = (
        df_clean.groupby("Country")["Revenue"]
        .sum()
        .sort_values(ascending=False)
        .head(10)
    )


    st.subheader("🌍 Top 10 Countries by Revenue")


    fig, ax = plt.subplots(figsize=(12,6))


    sns.barplot(
        x=top_countries.values,
        y=top_countries.index,
        color="#2ca02c",
        ax=ax
    )


    fig.tight_layout()

    ax.set_title("Top 10 Countries by Revenue")
    ax.set_xlabel("Revenue (£)")
    ax.set_ylabel("Country")

    st.pyplot(fig)



    # --------------------------------------------------
    # Country Performance Table
    # --------------------------------------------------

    country_analysis = (
        df_clean.groupby("Country")
        .agg(
            Revenue=("Revenue","sum"),
            Orders=("Invoice","nunique"),
            Customers=("Customer ID","nunique")
        )
        .sort_values(
            by="Revenue",
            ascending=False
        )
    )


    st.markdown("---")
    st.subheader("📊 Country Performance Table")

    st.dataframe(country_analysis.head(10))



    # --------------------------------------------------
    # AVERAGE ORDER VALUE BY COUNTRY
    # --------------------------------------------------

    country_analysis["Average Order Value"] = (
        country_analysis["Revenue"] /
        country_analysis["Orders"]
    )


    st.markdown("---")
    st.subheader("💳 Average Order Value by Country")


    avg_order_value = (
        country_analysis["Average Order Value"]
        .sort_values(ascending=False)
        .head(10)
    )


    fig, ax = plt.subplots(figsize=(12,6))


    sns.barplot(
        x=avg_order_value.values,
        y=avg_order_value.index,
        color="#9467bd",
        ax=ax
    )


    ax.set_title("Average Order Value by Country")
    ax.set_xlabel("Average Order Value (£)")
    ax.set_ylabel("Country")


    fig.tight_layout()

    st.pyplot(fig)
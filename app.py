import streamlit as st
import pandas as pd
import plotly.express as px

# -----------------------------
# Load & Cache Dataset
# -----------------------------
@st.cache_data
def load_data():
    DATA_PATH = "Online Retail.xlsx"
    df = pd.read_excel(DATA_PATH)
    df = df.dropna(subset=["Description", "CustomerID"])
    df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"])
    df["TotalAmount"] = df["Quantity"] * df["UnitPrice"]
    return df

df = load_data()

# -----------------------------
# Sidebar Filters
# -----------------------------
st.sidebar.header("🔧 Dashboard Controls")

countries = df["Country"].unique()
selected_country = st.sidebar.selectbox("Select Country", ["All"] + sorted(list(countries)))

min_date, max_date = df["InvoiceDate"].min(), df["InvoiceDate"].max()
date_range = st.sidebar.date_input("Select Date Range", [min_date, max_date], 
                                   min_value=min_date, max_value=max_date)

product_search = st.sidebar.text_input("Search Product")

# Build Query for Filtering
query_conditions = []
if selected_country != "All":
    query_conditions.append(f"Country == '{selected_country}'")

query_conditions.append(f"InvoiceDate >= '{date_range[0]}' and InvoiceDate <= '{date_range[1]}'")

if product_search:
    query_conditions.append(f"Description.str.contains('{product_search}', case=False, na=False)")

if query_conditions:
    query_str = " & ".join(query_conditions)
    df_filtered = df.query(query_str)
else:
    df_filtered = df.copy()

# -----------------------------
# KPIs
# -----------------------------
total_sales = df_filtered["TotalAmount"].sum()
total_orders = df_filtered["InvoiceNo"].nunique()
unique_customers = df_filtered["CustomerID"].nunique()
avg_order_value = total_sales / total_orders if total_orders > 0 else 0

st.title("📊 E-Commerce Sales Dashboard")

col1, col2, col3, col4 = st.columns(4)
col1.metric("💰 Total Sales", f"${total_sales:,.0f}")
col2.metric("🛒 Total Orders", f"{total_orders}")
col3.metric("👥 Unique Customers", f"{unique_customers}")
col4.metric("📦 Avg. Order Value", f"${avg_order_value:,.2f}")

# -----------------------------
# Charts (One Below Another)
# -----------------------------
st.subheader("📊 Data Visualizations")
st.subheader("📈 Top 10 Products")
top_products = df_filtered["Description"].value_counts().head(10)
fig1 = px.bar(top_products, x=top_products.values, y=top_products.index,
              orientation='h', title="Top 10 Products")
st.plotly_chart(fig1, use_container_width=True)

st.subheader("📈 Sales Over Time")
sales_time = df_filtered.groupby(df_filtered["InvoiceDate"].dt.date)["TotalAmount"].sum()
fig2 = px.line(sales_time, x=sales_time.index, y=sales_time.values, title="Sales Trend Over Time")
st.plotly_chart(fig2, use_container_width=True)

st.subheader("📈 Sales by Country")
country_sales = df_filtered.groupby("Country")["TotalAmount"].sum().sort_values(ascending=False).head(8)
fig3 = px.pie(country_sales, values=country_sales.values, names=country_sales.index, title="Top Countries by Sales")
st.plotly_chart(fig3, use_container_width=True)

st.subheader("📈 Quantity vs Price Distribution")
scatter_sample = df_filtered.sample(min(500, len(df_filtered)), random_state=42)
fig4 = px.scatter(scatter_sample, x="Quantity", y="UnitPrice", color="Country",
                  title="Quantity vs Price Distribution")
st.plotly_chart(fig4, use_container_width=True)


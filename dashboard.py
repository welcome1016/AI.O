import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# Set page config
st.set_page_config(page_title="PC Sales Dashboard", layout="wide", initial_sidebar_state="expanded")

# Load data
@st.cache_data
def load_data():
    df = pd.read_csv('pc_data.csv')
    # Convert date columns
    df['Purchase Date'] = pd.to_datetime(df['Purchase Date'], errors='coerce')
    df['Ship Date'] = pd.to_datetime(df['Ship Date'], errors='coerce')
    return df

df = load_data()

# Title
st.title("📊 PC Sales Analytics Dashboard")
st.markdown("---")

# Sidebar for filters
st.sidebar.header("🔍 Filters")
selected_continent = st.sidebar.multiselect("Continent", df['Continent'].unique(), default=df['Continent'].unique())
selected_shop = st.sidebar.multiselect("Shop Name", df['Shop Name'].unique(), default=df['Shop Name'].unique()[:5])
selected_channel = st.sidebar.multiselect("Channel", df['Channel'].unique(), default=df['Channel'].unique())

# Apply filters
filtered_df = df[
    (df['Continent'].isin(selected_continent)) &
    (df['Shop Name'].isin(selected_shop)) &
    (df['Channel'].isin(selected_channel))
]

# Key Metrics
st.header("📈 Key Metrics")
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    total_sales = filtered_df['Sale Price'].sum()
    st.metric("Total Sales", f"${total_sales:,.0f}")

with col2:
    total_cost = filtered_df['Cost Price'].sum()
    st.metric("Total Cost", f"${total_cost:,.0f}")

with col3:
    avg_profit = (filtered_df['Sale Price'] - filtered_df['Cost Price']).mean()
    st.metric("Avg Profit/Sale", f"${avg_profit:,.0f}")

with col4:
    total_discount = filtered_df['Discount Amount'].sum()
    st.metric("Total Discounts", f"${total_discount:,.0f}")

with col5:
    transaction_count = len(filtered_df)
    st.metric("Transaction Count", f"{transaction_count:,}")

st.markdown("---")

# Dimensions Overview
st.header("🏷️ Dimension Tables")

# Expand to 9 dimension tables
tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9 = st.tabs([
    "Geographic", "Products", "Customers", "Sales People", "Transactions",
    "Time", "Pricing", "Technical Specs", "Shop Metrics"
])

with tab1:
    st.subheader("Geographic Dimensions")
    geo_dims = filtered_df[['Continent', 'Country or State', 'Province or City', 'Shop Name', 'Shop Age']].drop_duplicates().reset_index(drop=True)
    st.dataframe(geo_dims, use_container_width=True)
    st.info(f"Total unique locations: {len(geo_dims)}")

with tab2:
    st.subheader("Product Dimensions")
    prod_dims = filtered_df[['PC Make', 'PC Model', 'Storage Type', 'Storage Capacity', 'RAM', 'PC Market Price']].drop_duplicates().reset_index(drop=True)
    st.dataframe(prod_dims, use_container_width=True)
    st.info(f"Total unique products: {len(prod_dims)}")

with tab3:
    st.subheader("Customer Dimensions")
    cust_dims = filtered_df[['Customer Name', 'Customer Surname', 'Customer Contact Number', 'Customer Email Address', 'Credit Score']].drop_duplicates().reset_index(drop=True)
    st.dataframe(cust_dims, use_container_width=True)
    st.info(f"Total unique customers: {len(cust_dims)}")

with tab4:
    st.subheader("Sales Person Dimensions")
    sales_dims = filtered_df[['Sales Person Name', 'Sales Person Department', 'Total Sales per Employee']].drop_duplicates().reset_index(drop=True)
    st.dataframe(sales_dims, use_container_width=True)
    st.info(f"Total unique sales people: {len(sales_dims)}")

with tab5:
    st.subheader("Transaction Dimensions")
    trans_dims = filtered_df[['Payment Method', 'Channel', 'Priority', 'Discount Amount', 'Finance Amount', 'Cost of Repairs']].drop_duplicates().reset_index(drop=True)
    st.dataframe(trans_dims, use_container_width=True)

with tab6:
    st.subheader("Time Dimensions")
    time_df = filtered_df[['Purchase Date', 'Ship Date']].drop_duplicates().reset_index(drop=True).copy()
    # add components where possible
    time_df['Purchase Year'] = time_df['Purchase Date'].dt.year
    time_df['Purchase Month'] = time_df['Purchase Date'].dt.month
    time_df['Purchase Day'] = time_df['Purchase Date'].dt.day
    st.dataframe(time_df, use_container_width=True)
    st.info(f"Total unique time points: {len(time_df)}")

with tab7:
    st.subheader("Pricing Dimensions")
    pricing_dims = filtered_df[['Cost Price', 'Sale Price', 'Discount Amount', 'PC Market Price', 'Finance Amount']].drop_duplicates().reset_index(drop=True)
    st.dataframe(pricing_dims, use_container_width=True)
    st.info(f"Total unique pricing rows: {len(pricing_dims)}")

with tab8:
    st.subheader("Technical Specs")
    tech_dims = filtered_df[['RAM', 'Storage Type', 'Storage Capacity']].drop_duplicates().reset_index(drop=True)
    st.dataframe(tech_dims, use_container_width=True)
    st.info(f"Total unique technical spec sets: {len(tech_dims)}")

with tab9:
    st.subheader("Shop Metrics")
    shop_dims = filtered_df[['Shop Name', 'Shop Age', 'Total Sales per Employee']].drop_duplicates().reset_index(drop=True)
    st.dataframe(shop_dims, use_container_width=True)
    st.info(f"Total unique shops: {len(shop_dims)}")

st.markdown("---")

# Fact Table
st.header("💾 Fact Table - Sales Transactions")
fact_table = filtered_df[[
    'Shop Name', 'PC Make', 'PC Model', 'Customer Name', 'Sales Person Name',
    'Cost Price', 'Sale Price', 'Discount Amount', 'Finance Amount',
    'Cost of Repairs', 'Total Sales per Employee', 'PC Market Price',
    'Purchase Date', 'Ship Date', 'Payment Method', 'Channel'
]].copy()

st.dataframe(fact_table, use_container_width=True, height=400)

# Download option
csv = fact_table.to_csv(index=False)
st.download_button(
    label="Download Fact Table as CSV",
    data=csv,
    file_name="fact_table.csv",
    mime="text/csv"
)

st.markdown("---")

# Analysis Section
st.header("📊 Analysis & Insights")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Sales by Continent")
    sales_continent = filtered_df.groupby('Continent')['Sale Price'].sum().sort_values(ascending=False)
    fig1 = px.bar(sales_continent, title="Total Sales by Continent", labels={'value': 'Sales ($)', 'index': 'Continent'})
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    st.subheader("Sales by PC Make")
    sales_make = filtered_df.groupby('PC Make')['Sale Price'].sum().sort_values(ascending=False).head(10)
    fig2 = px.bar(sales_make, title="Top 10 PC Makes by Sales", labels={'value': 'Sales ($)', 'index': 'PC Make'})
    st.plotly_chart(fig2, use_container_width=True)

col3, col4 = st.columns(2)

with col3:
    st.subheader("Sales by Payment Method")
    sales_payment = filtered_df.groupby('Payment Method')['Sale Price'].sum()
    fig3 = px.pie(values=sales_payment.values, names=sales_payment.index, title="Sales Distribution by Payment Method")
    st.plotly_chart(fig3, use_container_width=True)

with col4:
    st.subheader("Sales by Channel")
    sales_channel = filtered_df.groupby('Channel')['Sale Price'].sum()
    fig4 = px.pie(values=sales_channel.values, names=sales_channel.index, title="Sales Distribution by Channel")
    st.plotly_chart(fig4, use_container_width=True)

# Top performers
col5, col6 = st.columns(2)

with col5:
    st.subheader("Top 10 Sales People")
    top_sales = filtered_df.groupby('Sales Person Name')['Total Sales per Employee'].sum().sort_values(ascending=False).head(10)
    fig5 = px.bar(top_sales, title="Top 10 Sales People by Total Sales", labels={'value': 'Total Sales ($)', 'index': 'Sales Person'})
    st.plotly_chart(fig5, use_container_width=True)

with col6:
    st.subheader("Top 10 Shops")
    top_shops = filtered_df.groupby('Shop Name')['Sale Price'].sum().sort_values(ascending=False).head(10)
    fig6 = px.bar(top_shops, title="Top 10 Shops by Sales", labels={'value': 'Sales ($)', 'index': 'Shop Name'})
    st.plotly_chart(fig6, use_container_width=True)

st.markdown("---")

# Data Quality Info
st.header("ℹ️ Data Quality")
col_info1, col_info2, col_info3 = st.columns(3)

with col_info1:
    st.metric("Total Records", len(filtered_df))

with col_info2:
    st.metric("Null Values", filtered_df.isnull().sum().sum())

with col_info3:
    st.metric("Date Range", f"{filtered_df['Purchase Date'].min().strftime('%Y-%m-%d')} to {filtered_df['Purchase Date'].max().strftime('%Y-%m-%d')}")

st.info("Dashboard created with Streamlit • Data source: pc_data.csv")

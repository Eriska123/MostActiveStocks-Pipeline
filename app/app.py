import streamlit as st
import pandas as pd
import pyodbc
import plotly.express as px
from streamlit_autorefresh import st_autorefresh

# Refresh every 60 seconds
st_autorefresh(interval=60 * 1000, key="refresh")

@st.cache_data(ttl=60)
def load_data():
    conn = get_connection()
    df = pd.read_sql("""
        SELECT s.symbol, s.company_name,
               sp.price, sp.change,
               sp.percent_change, sp.volume,
               sp.last_updated
        FROM stock_prices sp
        JOIN stocks s ON sp.stock_id = s.stock_id
    """, conn)
    conn.close()
    return df

# =====================================================
# PAGE CONFIG
# =====================================================
st.set_page_config(
    page_title="Most Active Stocks Dashboard",
    layout="wide"
)

st.title("📊 Portfolio-Level Stocks Dashboard")
st.caption("Interactive dashboard with KPIs, charts, and filters")

# =====================================================
# DATABASE CONNECTION
# =====================================================
def get_connection():
    return pyodbc.connect(
        "DRIVER={ODBC Driver 17 for SQL Server};"
        "SERVER=localhost\\SQLEXPRESS;"  # adjust as needed
        "DATABASE=StockDB;"
        "Trusted_Connection=yes;"
    )

# =====================================================
# LOAD DATA
# =====================================================
@st.cache_data
def load_data():
    conn = get_connection()
    query = """
    SELECT 
        s.symbol,
        s.company_name,
        sp.price,
        sp.change,
        sp.percent_change,
        sp.volume,
        sp.last_updated
    FROM stock_prices sp
    JOIN stocks s ON sp.stock_id = s.stock_id
    """
    df = pd.read_sql(query, conn)
    conn.close()
    df["last_updated"] = pd.to_datetime(df["last_updated"])
    return df

df = load_data()
if df.empty:
    st.warning("⚠️ No data available.")
    st.stop()

# =====================================================
# SIDEBAR FILTERS
# =====================================================
st.sidebar.header("Filters")

symbols = st.sidebar.multiselect(
    "Select Stocks",
    options=df["symbol"].unique(),
    default=df["symbol"].unique()
)

date_range = st.sidebar.date_input(
    "Select Date Range",
    value=[df["last_updated"].min().date(), df["last_updated"].max().date()]
)

# Apply filters
filtered_df = df[
    (df["symbol"].isin(symbols)) &
    (df["last_updated"].dt.date.between(date_range[0], date_range[1]))
]

if filtered_df.empty:
    st.warning("⚠️ No data after filtering.")
    st.stop()

latest_df = filtered_df.sort_values("last_updated").groupby("symbol").last().reset_index()

# =====================================================
# KPI LAYER
# =====================================================
total_volume = latest_df["volume"].sum()
top_stock = latest_df.loc[latest_df["volume"].idxmax()]
avg_price = latest_df["price"].mean()
top_gainer = latest_df.loc[latest_df["percent_change"].idxmax()]
top_loser = latest_df.loc[latest_df["percent_change"].idxmin()]

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Total Market Volume", f"{total_volume:,.0f}")
col2.metric("Top Stock", top_stock["symbol"], f"Vol: {top_stock['volume']:,.0f}")
col3.metric("Average Price", f"${avg_price:,.2f}")
col4.metric("Top Gainer", top_gainer["symbol"], f"{top_gainer['percent_change']:.2f}%")
col5.metric("Top Loser", top_loser["symbol"], f"{top_loser['percent_change']:.2f}%")

st.divider()

# =====================================================
# TOP N STOCKS BY VOLUME
# =====================================================
st.subheader("📊 Top N Stocks by Volume")
top_n = st.slider("Select Top N Stocks", 5, 20, 10)
top_volume_df = latest_df.nlargest(top_n, "volume")
st.bar_chart(top_volume_df.set_index("symbol")["volume"])

# =====================================================
# MARKET SHARE PIE CHART
# =====================================================
st.subheader("📈 Market Share (%) by Volume")
market_share_df = latest_df.copy()
market_share_df["market_share"] = market_share_df["volume"] / market_share_df["volume"].sum() * 100

fig_share = px.pie(
    market_share_df,
    names="symbol",
    values="market_share",
    title="Market Share by Volume"
)
st.plotly_chart(fig_share, use_container_width=True)

# =====================================================
# PRICE TREND OVER TIME
# =====================================================
st.subheader("📈 Price Trend Over Time")
selected_stock = st.selectbox("Select Stock for Trend", latest_df["symbol"].unique())
stock_history = filtered_df[filtered_df["symbol"] == selected_stock].sort_values("last_updated")

fig_trend = px.line(
    stock_history,
    x="last_updated",
    y="price",
    title=f"{selected_stock} Price Trend"
)
st.plotly_chart(fig_trend, use_container_width=True)

# =====================================================
# DATA TABLE (VALIDATION)
# =====================================================
st.subheader("📋 Latest Market Snapshot")
st.dataframe(latest_df, use_container_width=True)
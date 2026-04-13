# =====================================================
# IMPORTS
# =====================================================
import streamlit as st
import pandas as pd

# Auto-refresh (every 60 seconds)
from streamlit_autorefresh import st_autorefresh
st_autorefresh(interval=60 * 1000, key="refresh")

# =====================================================
# PAGE CONFIG
# =====================================================
st.set_page_config(
    page_title="Stock Market Dashboard",
    layout="wide"
)

st.title("📊 Stock Market Decision Dashboard")
st.caption("Real-time insights from Most Active Stocks")

# =====================================================
# LOAD DATA (CACHED)
# =====================================================
@st.cache_data(ttl=60)
def load_data():
    try:
        # Try both paths (local + cloud safe)
        try:
            df = pd.read_csv("data/MostActiveStocks.csv")
        except:
            df = pd.read_csv("../data/MostActiveStocks.csv")

        # Ensure correct types
        df["Price"] = pd.to_numeric(df["Price"], errors="coerce")
        df["Change"] = pd.to_numeric(df["Change"], errors="coerce")
        df["PercentChange"] = pd.to_numeric(df["PercentChange"], errors="coerce")
        df["Volume"] = pd.to_numeric(df["Volume"], errors="coerce")

        return df.dropna()

    except Exception as e:
        st.error(f"❌ Error loading data: {e}")
        return pd.DataFrame()

# Load data
df = load_data()

if df.empty:
    st.warning("No data available.")
    st.stop()

# =====================================================
# KPI SECTION
# =====================================================
st.subheader("📌 Key Market Indicators")

col1, col2, col3, col4 = st.columns(4)

# KPIs
top_stock = df.loc[df["Volume"].idxmax()]
avg_price = df["Price"].mean()
total_volume = df["Volume"].sum()
top_gainer = df.loc[df["PercentChange"].idxmax()]

col1.metric("Top Stock (Volume)", top_stock["Symbol"])
col2.metric("Average Price", f"${avg_price:,.2f}")
col3.metric("Total Volume", f"{total_volume:,.0f}")
col4.metric("Top Gainer", top_gainer["Symbol"])

# =====================================================
# FILTER
# =====================================================
st.subheader("🔍 Filter Stocks")

selected_symbols = st.multiselect(
    "Select Stocks",
    options=df["Symbol"].unique(),
    default=df["Symbol"].unique()[:10]
)

filtered_df = df[df["Symbol"].isin(selected_symbols)]

# =====================================================
# TABLE
# =====================================================
st.subheader("📋 Stock Data")

st.dataframe(filtered_df, use_container_width=True)

# =====================================================
# CHARTS
# =====================================================
st.subheader("📈 Market Insights")

col1, col2 = st.columns(2)

with col1:
    st.write("### Price Distribution")
    st.bar_chart(filtered_df.set_index("Symbol")["Price"])

with col2:
    st.write("### Volume Distribution")
    st.bar_chart(filtered_df.set_index("Symbol")["Volume"])

# =====================================================
# TOP MOVERS
# =====================================================
st.subheader("🚀 Top Movers")

col1, col2 = st.columns(2)

with col1:
    st.write("### 🔺 Top Gainers")
    gainers = df.sort_values(by="PercentChange", ascending=False).head(5)
    st.dataframe(gainers[["Symbol", "PercentChange"]])

with col2:
    st.write("### 🔻 Top Losers")
    losers = df.sort_values(by="PercentChange", ascending=True).head(5)
    st.dataframe(losers[["Symbol", "PercentChange"]])

# =====================================================
# FOOTER
# =====================================================
st.markdown("---")
st.caption("⚡ Auto-refresh every 60 seconds | Data via Yahoo Finance")
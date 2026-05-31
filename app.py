import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import time

# --------------------------------------------------
# STREAMLIT PAGE CONFIG
# --------------------------------------------------
st.set_page_config(
    page_title="SBI Live TWAP Tracker",
    page_icon="📈",
    layout="wide"
)

st.title("📈 SBI Live TWAP Tracker")
st.markdown(
    """
    Real-time Time-Weighted Average Price (TWAP) dashboard for
    SBI (SBIN.NS) listed on NSE.
    """
)

# --------------------------------------------------
# SBI TICKER
# --------------------------------------------------
ticker_symbol = "SBIN.NS"

# --------------------------------------------------
# SIDEBAR SETTINGS
# --------------------------------------------------
st.sidebar.header("TWAP Settings")

interval = st.sidebar.selectbox(
    "Time Interval",
    ["1m", "2m", "5m", "15m", "30m", "60m"],
    index=0
)

auto_refresh = st.sidebar.checkbox(
    "Enable Live Tracking",
    value=True
)

refresh_rate = st.sidebar.slider(
    "Refresh Rate (seconds)",
    min_value=10,
    max_value=120,
    value=30
)

# --------------------------------------------------
# PLACEHOLDERS
# --------------------------------------------------
error_placeholder = st.empty()
metrics_placeholder = st.empty()
chart_placeholder = st.empty()
table_placeholder = st.empty()

# --------------------------------------------------
# DATA FETCH FUNCTION
# --------------------------------------------------
def fetch_and_calculate(ticker, time_interval):
    try:
        stock = yf.Ticker(ticker)

        df = stock.history(
            period="1d",
            interval=time_interval
        )

        if df.empty:
            return None

        # Typical Price
        df["Typical_Price"] = (
            df["High"] +
            df["Low"] +
            df["Close"]
        ) / 3

        # TWAP Calculation
        df["TWAP"] = df["Typical_Price"].expanding().mean()

        return df

    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return None


# --------------------------------------------------
# DASHBOARD UPDATE
# --------------------------------------------------
def update_dashboard():

    df = fetch_and_calculate(
        ticker_symbol,
        interval
    )

    if df is None or df.empty:
        error_placeholder.error(
            "Unable to fetch SBI data from Yahoo Finance."
        )
        return

    error_placeholder.empty()

    latest_price = df["Close"].iloc[-1]
    latest_twap = df["TWAP"].iloc[-1]

    open_price = df["Open"].iloc[0]

    price_change = latest_price - open_price
    price_change_pct = (
        (price_change / open_price) * 100
    )

    high_price = df["High"].max()
    low_price = df["Low"].min()

    # --------------------------------------------------
    # METRICS
    # --------------------------------------------------
    with metrics_placeholder.container():

        col1, col2, col3, col4 = st.columns(4)

        col1.metric(
            "Current Price",
            f"₹{latest_price:.2f}",
            f"{price_change:.2f} ({price_change_pct:.2f}%)"
        )

        col2.metric(
            "Current TWAP",
            f"₹{latest_twap:.2f}"
        )

        col3.metric(
            "Day High",
            f"₹{high_price:.2f}"
        )

        col4.metric(
            "Day Low",
            f"₹{low_price:.2f}"
        )

    # --------------------------------------------------
    # CHART
    # --------------------------------------------------
    with chart_placeholder.container():

        fig = go.Figure()

        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=df["Close"],
                mode="lines",
                name="SBI Price",
                line=dict(
                    color="#00B4D8",
                    width=2
                )
            )
        )

        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=df["TWAP"],
                mode="lines",
                name="TWAP",
                line=dict(
                    color="#FFA500",
                    width=3,
                    dash="dash"
                )
            )
        )

        fig.update_layout(
            title="SBI (SBIN.NS) Live Price vs TWAP",
            xaxis_title="Time",
            yaxis_title="Price (₹)",
            template="plotly_dark",
            hovermode="x unified",
            height=600,
            margin=dict(
                l=20,
                r=20,
                t=50,
                b=20
            )
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    # --------------------------------------------------
    # DATA TABLE
    # --------------------------------------------------
    with table_placeholder.container():

        st.subheader("Latest TWAP Data")

        display_df = df[
            [
                "Open",
                "High",
                "Low",
                "Close",
                "Volume",
                "TWAP"
            ]
        ].copy()

        st.dataframe(
            display_df.tail(20),
            use_container_width=True
        )


# --------------------------------------------------
# MAIN EXECUTION
# --------------------------------------------------
if auto_refresh:

    update_dashboard()

    time.sleep(refresh_rate)

    st.rerun()

else:

    update_dashboard()

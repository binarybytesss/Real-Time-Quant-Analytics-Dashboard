import streamlit as st

from ingestion import start_ingestion
from storage import get_ticks_df, resample_ticks
from analytics import (
    compute_zscore,
    compute_spread,
    rolling_correlation,
    hedge_ratio_ols,
    rolling_hedge_ratio,
    adf_test
)

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Real-Time Quant Analytics",
    layout="wide"
)

st.title("📊 Real-Time Quant Analytics Dashboard")

# ---------------- SIDEBAR ----------------
st.sidebar.header("Controls")

symbols_input = st.sidebar.text_input(
    "Symbols (comma separated)",
    "btcusdt,ethusdt"
)

timeframe = st.sidebar.selectbox(
    "Resample Timeframe",
    ["1s", "1m", "5m"]
)

alert_threshold = st.sidebar.slider(
    "Z-score Alert Threshold",
    1.0, 3.0, 2.0, 0.1
)

if st.sidebar.button("Start Ingestion"):
    symbols = [s.strip() for s in symbols_input.split(",") if s.strip()]
    start_ingestion(symbols)
    st.sidebar.success("Ingestion started")

st.divider()

# ---------------- TABS ----------------
tab_prices, tab_analytics, tab_export = st.tabs(
    ["📈 Prices", "📊 Analytics", "📥 Export"]
)

# ---------------- LOAD DATA ----------------
df = get_ticks_df()

if df.empty:
    st.info("Waiting for live data from Binance WebSocket…")
    st.stop()

resampled = resample_ticks(df, timeframe)

expected_cols = {"symbol", "timestamp", "price"}
if not expected_cols.issubset(resampled.columns):
    st.error(f"Unexpected data schema: {list(resampled.columns)}")
    st.stop()

# ---------------- PRICES TAB ----------------
with tab_prices:
    st.subheader("Live Prices (per symbol)")

    for sym in resampled["symbol"].unique():
        st.markdown(f"### {sym.upper()}")
        st.line_chart(
            resampled[resampled["symbol"] == sym],
            x="timestamp",
            y="price",
            height=250
        )

# ---------------- ANALYTICS TAB ----------------
with tab_analytics:
    st.subheader("Z-Score")

    z = compute_zscore(resampled["price"])
    st.line_chart(z)

    if len(z) > 0 and abs(z.iloc[-1]) > alert_threshold:
        st.error(f"⚠️ Z-score Alert: {z.iloc[-1]:.2f}")

    symbols_present = set(resampled["symbol"].unique())

    if {"btcusdt", "ethusdt"}.issubset(symbols_present):
        # ---------- Spread ----------
        st.subheader("BTC–ETH Spread")
        spread = compute_spread(resampled, "btcusdt", "ethusdt")
        st.line_chart(spread)

        # ---------- CURRENT HEDGE RATIO (METRIC) ----------
        hedge_ratio = hedge_ratio_ols(resampled, "btcusdt", "ethusdt")
        if hedge_ratio is not None:
            st.metric(
                label="Current OLS Hedge Ratio (BTC vs ETH)",
                value=round(hedge_ratio, 4)
            )

        # ---------- ROLLING HEDGE RATIO (CHART) ----------
        st.subheader("Rolling OLS Hedge Ratio")
        rolling_hr = rolling_hedge_ratio(resampled, "btcusdt", "ethusdt")
        st.line_chart(rolling_hr)

        # ---------- Rolling Correlation ----------
        st.subheader("Rolling Correlation (BTC vs ETH)")
        corr = rolling_correlation(resampled, "btcusdt", "ethusdt")
        st.line_chart(corr)

        # ---------- ADF TEST ----------
        st.subheader("ADF Stationarity Test (Spread)")
        if st.button("Run ADF Test on BTC–ETH Spread"):
            pval = adf_test(spread)
            if pval is not None:
                st.write(f"ADF Test p-value: **{pval:.4f}**")
                if pval < 0.05:
                    st.success("Spread is likely mean-reverting (stationary)")
                else:
                    st.warning("Spread may not be stationary")

    # ---------- SUMMARY ----------
    st.subheader("Summary Statistics")
    st.dataframe(
        resampled.groupby("symbol")["price"]
        .agg(["mean", "std", "min", "max"])
    )

# ---------------- EXPORT TAB ----------------
with tab_export:
    st.subheader("Download Resampled Data")

    csv = resampled.to_csv(index=False).encode("utf-8")

    st.download_button(
        label="Download CSV",
        data=csv,
        file_name=f"resampled_{timeframe}.csv",
        mime="text/csv",
        key="download_csv"
    )

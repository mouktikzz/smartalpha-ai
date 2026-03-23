import streamlit as st
import yfinance as yf
from crew import stock_crew

st.set_page_config(page_title="SmartAlpha AI", page_icon="📊", layout="wide")

st.title("📊 SmartAlpha AI — Stock Analysis Assistant")

stock_symbol = st.text_input("Enter Stock Symbol (e.g., AAPL, TSLA)").strip().upper()

if st.button("Analyze"):
    if not stock_symbol:
        st.warning("⚠️ Please enter a stock symbol")
        st.stop()

    stock = yf.Ticker(stock_symbol)

    hist = stock.history(period="1mo")
    if hist.empty:
        st.error("❌ Invalid stock symbol or no data available")
        st.stop()

    fast_info = stock.fast_info

    price = fast_info.get("last_price", "N/A")
    change = fast_info.get("regular_market_change", 0)
    change_percent = fast_info.get("regular_market_change_percent", 0)

    st.subheader(f"📊 Analysis for {stock_symbol}")

    col1, col2, col3 = st.columns(3)
    col1.metric("Price", f"${price}")
    col2.metric("Change", f"{round(change,2)}")
    col3.metric("% Change", f"{round(change_percent,2)}%")

    st.subheader("📈 Price Chart (1 Month)")
    st.line_chart(hist["Close"])

    st.divider()

    st.subheader("🤖 AI Analysis")

    with st.spinner("Running AI agents..."):
        result = stock_crew.kickoff(inputs={"stock": stock_symbol})

    response = result.raw
    st.markdown(response)

    response_lower = response.lower()

    if "buy" in response_lower:
        st.success("🟢 BUY Recommendation")
    elif "sell" in response_lower:
        st.error("🔴 SELL Recommendation")
    else:
        st.warning("🟡 HOLD Recommendation")

    st.markdown("---")
    st.caption("⚡ Powered by CrewAI + Yahoo Finance")

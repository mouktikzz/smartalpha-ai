import streamlit as st
import yfinance as yf
from crew import stock_crew

st.set_page_config(page_title="Smartalpha AI", page_icon="📊", layout="wide")

st.title("📊 AI Stock Analysis & Trading Assistant")

# Input
stock_symbol = st.text_input("Enter Stock Symbol").upper()

if st.button("Analyze"):
    if not stock_symbol:
        st.warning("⚠️ Please enter a stock symbol")
        st.stop()  

    # --- Fetch basic stock data ---
    stock = yf.Ticker(stock_symbol)
    hist = stock.history(period="1mo")
    info = stock.info

    price = info.get("regularMarketPrice", "N/A")
    change = info.get("regularMarketChange", 0)
    change_percent = info.get("regularMarketChangePercent", 0)

    # --- Metrics ---
    col1, col2, col3 = st.columns(3)

    col1.metric("Price", f"${price}")
    col2.metric("Change", f"{round(change,2)}")
    col3.metric("% Change", f"{round(change_percent,2)}%")

    # --- Chart ---
    st.subheader("📈 Price Chart (1 Month)")
    st.line_chart(hist["Close"])

    # --- AI Agents ---
    st.subheader("🤖 AI Analysis")

    with st.spinner("Running AI agents..."):
        result = stock_crew.kickoff(inputs={"stock": stock_symbol})

    response = result.raw

    st.markdown(response)

    # Decision highlight
    if "Buy" in response:
        st.success("🟢 BUY Recommendation")
    elif "Sell" in response:
        st.error("🔴 SELL Recommendation")
    else:
        st.warning("🟡 HOLD Recommendation")

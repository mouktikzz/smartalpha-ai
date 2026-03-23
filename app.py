import streamlit as st
import yfinance as yf
from crew import stock_crew
import re

st.set_page_config(page_title="SmartAlpha AI", page_icon="📊", layout="wide")

st.title("📊 SmartAlpha AI — Stock Analysis Assistant")

stock_symbol = st.text_input("Enter Stock Symbol (e.g., AAPL, TSLA)").strip().upper()

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

    response = result.tasks_output[-1].raw

    # Clean formatting
    response = re.sub(r'\s+', ' ', response)
    response = re.sub(r'(?<=\b[A-Z])\s(?=[A-Z]\b)', '', response)

    st.write(response)

    response_lower = response.lower()

    if "buy" in response_lower:
        st.success("🟢 BUY Recommendation")
    elif "sell" in response_lower:
        st.error("🔴 SELL Recommendation")
    else:
        st.warning("🟡 HOLD Recommendation")

    st.markdown("---")
    st.caption("⚡ Powered by CrewAI + Yahoo Finance")

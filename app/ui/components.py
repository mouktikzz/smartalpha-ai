import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots

from app.models.schemas import (
    AnalysisResult,
    NewsArticle,
    StockMetrics,
    TechnicalIndicators,
    TickerMatch,
)

PERIOD_LABELS = {
    "1mo": "1 Month",
    "3mo": "3 Months",
    "6mo": "6 Months",
    "1y": "1 Year",
}


def render_ticker_selector(matches: list[TickerMatch]) -> str | None:
    if not matches:
        st.error("No matching companies found. Try a different name or ticker.")
        return None

    if len(matches) == 1:
        match = matches[0]
        st.success(f"Resolved: **{match.symbol}** — {match.name}")
        return match.symbol

    options = {f"{m.symbol} — {m.name}": m.symbol for m in matches}
    selected = st.selectbox(
        "Multiple matches found — select the correct company:",
        options=list(options.keys()),
    )
    return options[selected]


def render_metrics(metrics: StockMetrics) -> None:
    st.subheader("Key Metrics")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric(
        "Current Price",
        f"${metrics.current_price:,.2f}" if metrics.current_price else "N/A",
        f"{metrics.daily_change_percent:.2f}%" if metrics.daily_change_percent else None,
    )
    col2.metric(
        "Volume",
        f"{metrics.volume:,}" if metrics.volume else "N/A",
        f"Avg: {metrics.average_volume:,}" if metrics.average_volume else None,
    )
    col3.metric(
        "Market Cap",
        _format_large_number(metrics.market_cap),
    )
    col4.metric(
        "P/E Ratio",
        f"{metrics.pe_ratio:.2f}" if metrics.pe_ratio else "N/A",
    )

    col5, col6, col7, col8 = st.columns(4)
    col5.metric(
        "52W High",
        f"${metrics.fifty_two_week_high:,.2f}" if metrics.fifty_two_week_high else "N/A",
    )
    col6.metric(
        "52W Low",
        f"${metrics.fifty_two_week_low:,.2f}" if metrics.fifty_two_week_low else "N/A",
    )
    col7.metric(
        "Beta",
        f"{metrics.beta:.2f}" if metrics.beta else "N/A",
    )
    col8.metric(
        "Dividend Yield",
        f"{metrics.dividend_yield * 100:.2f}%" if metrics.dividend_yield else "N/A",
    )


def render_charts(histories: dict[str, pd.DataFrame], symbol: str) -> None:
    st.subheader("Price Charts")

    tabs = st.tabs([PERIOD_LABELS[p] for p in histories])
    for tab, (period, history) in zip(tabs, histories.items()):
        with tab:
            fig = go.Figure()
            fig.add_trace(
                go.Scatter(
                    x=history.index,
                    y=history["Close"],
                    mode="lines",
                    name="Close",
                    line=dict(color="#1f77b4", width=2),
                )
            )
            if len(history) >= 50:
                fig.add_trace(
                    go.Scatter(
                        x=history.index,
                        y=history["Close"].rolling(50).mean(),
                        mode="lines",
                        name="SMA 50",
                        line=dict(color="#ff7f0e", width=1, dash="dash"),
                    )
                )
            fig.update_layout(
                title=f"{symbol} — {PERIOD_LABELS[period]} Trend",
                xaxis_title="Date",
                yaxis_title="Price",
                hovermode="x unified",
                height=400,
                margin=dict(l=40, r=40, t=50, b=40),
            )
            st.plotly_chart(fig, use_container_width=True)


def render_technical_indicators(technical: TechnicalIndicators, history: pd.DataFrame) -> None:
    st.subheader("Technical Indicators")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("50-Day MA", f"${technical.sma_50:,.2f}" if technical.sma_50 else "N/A")
    col2.metric("200-Day MA", f"${technical.sma_200:,.2f}" if technical.sma_200 else "N/A")
    col3.metric("RSI (14)", f"{technical.rsi_14}" if technical.rsi_14 else "N/A")
    col4.metric("Trend", technical.technical_trend)

    col5, col6, col7, col8 = st.columns(4)
    col5.metric("MACD Line", f"{technical.macd_line}" if technical.macd_line else "N/A")
    col6.metric("Signal Line", f"{technical.macd_signal}" if technical.macd_signal else "N/A")
    daily_vol = f"{technical.daily_volatility * 100:.2f}%" if technical.daily_volatility else "N/A"
    ann_vol = f"{technical.annualized_volatility * 100:.2f}%" if technical.annualized_volatility else "N/A"
    col7.metric("Daily Volatility", daily_vol)
    col8.metric("Annualized Volatility", ann_vol)

    if len(history) >= 30:
        close = history["Close"]
        ema_12 = close.ewm(span=12, adjust=False).mean()
        ema_26 = close.ewm(span=26, adjust=False).mean()
        macd = ema_12 - ema_26
        signal = macd.ewm(span=9, adjust=False).mean()

        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, row_heights=[0.7, 0.3], vertical_spacing=0.05)

        fig.add_trace(go.Scatter(x=history.index, y=close, name="Price", line=dict(color="#1f77b4")), row=1, col=1)
        if len(close) >= 50:
            fig.add_trace(
                go.Scatter(x=history.index, y=close.rolling(50).mean(), name="SMA 50", line=dict(dash="dash")),
                row=1,
                col=1,
            )
        fig.add_trace(go.Scatter(x=history.index, y=macd, name="MACD", line=dict(color="#2ca02c")), row=2, col=1)
        fig.add_trace(go.Scatter(x=history.index, y=signal, name="Signal", line=dict(color="#d62728")), row=2, col=1)

        fig.update_layout(height=500, title="Price & MACD", hovermode="x unified")
        st.plotly_chart(fig, use_container_width=True)


def render_news_sentiment(articles: list[NewsArticle], sentiment_result=None) -> None:
    st.subheader("News Sentiment")

    if sentiment_result:
        render_sentiment_card(sentiment_result)

    with st.expander("Recent Headlines", expanded=True):
        if not articles:
            st.info("No recent news articles available for this stock.")
            return
        for article in articles[:8]:
            if article.link:
                st.markdown(f"- [{article.title}]({article.link}) — *{article.publisher}*")
            else:
                st.markdown(f"- **{article.title}** — *{article.publisher}*")


def render_sentiment_card(sentiment_result) -> None:
    colors = {"Bullish": "green", "Neutral": "orange", "Bearish": "red"}
    color = colors.get(sentiment_result.overall_sentiment, "gray")

    st.markdown(
        f"""
        <div style="padding:16px;border-radius:8px;border-left:4px solid {color};
        background:rgba(0,0,0,0.03);margin-bottom:12px;">
            <h4 style="margin:0;">Sentiment: {sentiment_result.overall_sentiment}</h4>
            <p style="margin:4px 0 0 0;">Score: {sentiment_result.sentiment_score:.2f}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if sentiment_result.summary:
        st.write(sentiment_result.summary)


def render_risk_card(risk_result) -> None:
    st.subheader("Risk Analysis")

    colors = {"Low": "green", "Medium": "orange", "High": "red"}
    color = colors.get(risk_result.risk_level, "gray")

    st.markdown(
        f"""
        <div style="padding:16px;border-radius:8px;border-left:4px solid {color};
        background:rgba(0,0,0,0.03);margin-bottom:12px;">
            <h4 style="margin:0;">Risk Level: {risk_result.risk_level}</h4>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.write(risk_result.explanation)
    if risk_result.key_factors:
        st.markdown("**Key Factors:**")
        for factor in risk_result.key_factors:
            st.markdown(f"- {factor}")


def render_recommendation(result: AnalysisResult) -> None:
    st.subheader("Final Recommendation")

    rec = result.recommendation
    rec_colors = {"BUY": "green", "HOLD": "orange", "SELL": "red"}
    color = rec_colors.get(rec.recommendation, "gray")

    st.markdown(
        f"""
        <div style="padding:20px;border-radius:10px;border:2px solid {color};
        background:rgba(0,0,0,0.02);text-align:center;margin-bottom:16px;">
            <h2 style="margin:0;color:{color};">{rec.recommendation}</h2>
            <p style="margin:8px 0 0 0;font-size:1.2em;">Confidence: {rec.confidence}%</p>
            <p style="margin:4px 0 0 0;">Horizon: {rec.investment_horizon or 'N/A'}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns(3)
    col1.metric("Risk", rec.risk_level)
    col2.metric("Sentiment", rec.sentiment)
    col3.metric("Technical Trend", rec.technical_trend)

    with st.expander("Key Reasons", expanded=True):
        for reason in rec.reasons:
            st.markdown(f"- {reason}")

    with st.expander("Risks", expanded=False):
        for risk in rec.risks:
            st.markdown(f"- {risk}")


def _format_large_number(value: float | None) -> str:
    if value is None:
        return "N/A"
    if value >= 1e12:
        return f"${value / 1e12:.2f}T"
    if value >= 1e9:
        return f"${value / 1e9:.2f}B"
    if value >= 1e6:
        return f"${value / 1e6:.2f}M"
    return f"${value:,.0f}"

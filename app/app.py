import json

import pandas as pd
import streamlit as st
from dotenv import load_dotenv

from app.logging_config import setup_logging
from app.models.schemas import NewsArticle
from app.services.exceptions import (
    APIError,
    DataUnavailableError,
    EmptyInputError,
    InvalidTickerError,
    NetworkError,
    SmartAlphaError,
)
from app.services.news_service import NewsService
from app.services.risk_analysis import RiskAnalysisService
from app.services.stock_service import StockService
from app.services.technical_analysis import TechnicalAnalysisService
from app.services.ticker_resolver import TickerResolver
from app.ui.components import (
    render_charts,
    render_metrics,
    render_news_sentiment,
    render_recommendation,
    render_risk_card,
    render_technical_indicators,
    render_ticker_selector,
)

load_dotenv()
logger = setup_logging()

st.set_page_config(
    page_title="SmartAlpha AI",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)


@st.cache_data(ttl=300, show_spinner=False)
def cached_resolve_ticker(query: str) -> list[dict]:
    matches = TickerResolver().resolve(query)
    return [m.model_dump() for m in matches]


@st.cache_data(ttl=120, show_spinner=False)
def cached_fetch_stock(symbol: str) -> dict:
    metrics, history = StockService().validate_and_fetch(symbol)
    return {
        "metrics": metrics.model_dump(),
        "history": history.reset_index().to_json(date_format="iso"),
    }


@st.cache_data(ttl=300, show_spinner=False)
def cached_fetch_history(symbol: str, period: str) -> str:
    history = StockService().fetch_history(symbol, period)
    return history.reset_index().to_json(date_format="iso")


@st.cache_data(ttl=300, show_spinner=False)
def cached_fetch_news(symbol: str) -> list[dict]:
    articles = NewsService().fetch_news(symbol)
    return [a.model_dump() for a in articles]


def _history_from_json(data: str) -> pd.DataFrame:
    df = pd.read_json(data)
    if "Date" in df.columns:
        df["Date"] = pd.to_datetime(df["Date"])
        df = df.set_index("Date")
    elif "Datetime" in df.columns:
        df["Datetime"] = pd.to_datetime(df["Datetime"])
        df = df.set_index("Datetime")
    return df


def _handle_error(exc: SmartAlphaError) -> None:
    messages = {
        EmptyInputError: "Please enter a company name or ticker symbol.",
        InvalidTickerError: str(exc),
        DataUnavailableError: str(exc),
        APIError: f"Market data API error: {exc}",
        NetworkError: str(exc),
    }
    st.error(messages.get(type(exc), str(exc)))
    logger.error("User-facing error: %s", exc)


def render_sidebar() -> dict:
    st.sidebar.header("Settings")
    run_agents = st.sidebar.toggle("Run AI Agent Analysis", value=True)
    cache_ttl = st.sidebar.selectbox("Cache TTL (minutes)", [2, 5, 10], index=1)
    show_json = st.sidebar.checkbox("Show raw JSON output", value=False)
    st.sidebar.markdown("---")
    st.sidebar.caption("Powered by CrewAI + Yahoo Finance")
    return {"run_agents": run_agents, "cache_ttl": cache_ttl, "show_json": show_json}


def main() -> None:
    st.title("📊 SmartAlpha AI")
    st.caption("Multi-agent financial analysis platform")

    settings = render_sidebar()

    st.markdown("### Stock Search")
    query = st.text_input(
        "Enter company name or ticker (e.g., Apple, AAPL, Tesla, NVDA)",
        placeholder="Apple",
        key="stock_query",
    )

    analyze_clicked = st.button("Analyze", type="primary", use_container_width=False)

    if not analyze_clicked:
        st.info("Enter a company name or ticker symbol and click **Analyze** to begin.")
        return

    logger.info("User requested analysis for: %s", query)

    try:
        with st.spinner("Resolving company..."):
            match_dicts = cached_resolve_ticker(query.strip())
            from app.models.schemas import TickerMatch

            matches = [TickerMatch(**m) for m in match_dicts]
    except SmartAlphaError as exc:
        _handle_error(exc)
        return

    symbol = render_ticker_selector(matches)
    if not symbol:
        return

    logger.info("Symbol resolved: %s", symbol)

    try:
        with st.spinner(f"Fetching market data for {symbol}..."):
            stock_data = cached_fetch_stock(symbol)
            from app.models.schemas import StockMetrics

            metrics = StockMetrics(**stock_data["metrics"])
            history = _history_from_json(stock_data["history"])
    except SmartAlphaError as exc:
        _handle_error(exc)
        logger.error("Stock data fetch failed for %s: %s", symbol, exc)
        return

    technical = TechnicalAnalysisService().analyze(symbol, history)

    periods = ["1mo", "3mo", "6mo", "1y"]
    histories = {"1y": history}
    with st.spinner("Loading historical charts..."):
        for period in periods[:-1]:
            try:
                histories[period] = _history_from_json(cached_fetch_history(symbol, period))
            except SmartAlphaError:
                histories[period] = history.tail(max(20, len(history) // 4))

    try:
        with st.spinner("Fetching news..."):
            news_dicts = cached_fetch_news(symbol)
            articles = [NewsArticle(**n) for n in news_dicts]
    except SmartAlphaError as exc:
        st.warning(f"News unavailable: {exc}")
        articles = []
        logger.warning("News fetch failed for %s: %s", symbol, exc)

    baseline_risk = RiskAnalysisService().assess(metrics, technical, history)

    st.divider()
    render_metrics(metrics)
    st.divider()
    render_charts(histories, symbol)
    st.divider()
    render_technical_indicators(technical, history)
    st.divider()

    analysis_result = None

    if settings["run_agents"]:
        news_payload = [{"title": a.title, "publisher": a.publisher} for a in articles]

        with st.spinner("Running AI agents (Financial, News, Risk, Advisor)..."):
            try:
                from app.crew import run_analysis_crew

                analysis_result = run_analysis_crew(
                    symbol=symbol,
                    metrics=metrics,
                    technical=technical,
                    history=history,
                    news_articles=news_payload,
                )
                logger.info(
                    "Agent recommendation for %s: %s (%d%%)",
                    symbol,
                    analysis_result.recommendation.recommendation,
                    analysis_result.recommendation.confidence,
                )
            except Exception as exc:
                st.error(f"AI agent execution failed: {exc}")
                logger.exception("Crew execution failed for %s", symbol)

        if analysis_result:
            render_news_sentiment(articles, analysis_result.news_sentiment)
            st.divider()
            render_risk_card(analysis_result.risk_assessment)
            st.divider()
            render_recommendation(analysis_result)

            if settings["show_json"]:
                with st.expander("Structured JSON Output"):
                    st.json(json.loads(analysis_result.model_dump_json()))
    else:
        render_news_sentiment(articles)
        st.divider()
        render_risk_card(baseline_risk)
        st.info("Enable **Run AI Agent Analysis** in the sidebar for the full recommendation.")

    st.markdown("---")
    st.caption(f"Analysis for {metrics.company_name} ({symbol}) — data refreshed from live sources")


if __name__ == "__main__":
    main()

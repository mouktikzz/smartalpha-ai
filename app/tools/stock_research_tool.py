import json

import yfinance as yf
from crewai.tools import tool


@tool("Live Stock Data Tool")
def get_stock_data(stock_symbol: str) -> str:
    """
    Retrieves comprehensive live stock data for a given ticker symbol.

    Parameters:
        stock_symbol: Ticker symbol (e.g., AAPL, TSLA, MSFT).

    Returns:
        JSON string with price, volume, market cap, P/E, beta, and 52-week range.
    """
    stock = yf.Ticker(stock_symbol)
    info = stock.info or {}

    data = {
        "symbol": stock_symbol.upper(),
        "price": info.get("regularMarketPrice") or info.get("currentPrice"),
        "change_percent": info.get("regularMarketChangePercent"),
        "volume": info.get("volume") or info.get("regularMarketVolume"),
        "average_volume": info.get("averageVolume"),
        "market_cap": info.get("marketCap"),
        "pe_ratio": info.get("trailingPE") or info.get("forwardPE"),
        "fifty_two_week_high": info.get("fiftyTwoWeekHigh"),
        "fifty_two_week_low": info.get("fiftyTwoWeekLow"),
        "beta": info.get("beta"),
        "dividend_yield": info.get("dividendYield"),
    }

    if data["price"] is None:
        return json.dumps({"error": f"Could not fetch data for {stock_symbol}"})

    return json.dumps(data, indent=2)


@tool("Stock News Tool")
def get_stock_news(stock_symbol: str) -> str:
    """
    Retrieves recent news headlines for a given stock symbol.

    Parameters:
        stock_symbol: Ticker symbol (e.g., AAPL, TSLA).

    Returns:
        JSON string with recent news headlines and publishers.
    """
    stock = yf.Ticker(stock_symbol)
    raw_news = stock.news or []

    headlines = []
    for item in raw_news[:8]:
        content = item.get("content", item)
        title = content.get("title") or item.get("title", "")
        if title:
            provider = content.get("provider", {})
            publisher = provider.get("displayName", "") if isinstance(provider, dict) else ""
            headlines.append({"title": title, "publisher": publisher})

    return json.dumps({"symbol": stock_symbol.upper(), "headlines": headlines}, indent=2)

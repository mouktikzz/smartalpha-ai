import logging

import pandas as pd
import yfinance as yf

from app.models.schemas import StockMetrics
from app.services.exceptions import APIError, DataUnavailableError, InvalidTickerError, NetworkError

logger = logging.getLogger("smartalpha.stock_service")

PERIOD_MAP = {
    "1mo": "1 Month",
    "3mo": "3 Months",
    "6mo": "6 Months",
    "1y": "1 Year",
}


class StockService:
    """Fetch and validate live stock market data."""

    def validate_and_fetch(self, symbol: str) -> tuple[StockMetrics, pd.DataFrame]:
        symbol = symbol.strip().upper()
        logger.info("Fetching stock data for %s", symbol)

        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info or {}
            history = ticker.history(period="1y")
        except ConnectionError as exc:
            logger.error("Network error fetching %s: %s", symbol, exc)
            raise NetworkError("Network error while fetching stock data.") from exc
        except Exception as exc:
            logger.error("API error fetching %s: %s", symbol, exc)
            raise APIError("Failed to retrieve stock data from market API.") from exc

        if history.empty:
            logger.warning("No historical data for %s", symbol)
            raise DataUnavailableError(
                f"No market data available for '{symbol}'. The stock may be delisted or invalid."
            )

        price = (
            info.get("regularMarketPrice")
            or info.get("currentPrice")
            or (history["Close"].iloc[-1] if not history.empty else None)
        )

        if price is None:
            raise InvalidTickerError(f"'{symbol}' is not a valid or recognized ticker symbol.")

        metrics = StockMetrics(
            symbol=symbol,
            company_name=info.get("longName") or info.get("shortName") or symbol,
            current_price=float(price),
            daily_change=_safe_float(info.get("regularMarketChange")),
            daily_change_percent=_safe_float(info.get("regularMarketChangePercent")),
            volume=_safe_int(info.get("volume") or info.get("regularMarketVolume")),
            average_volume=_safe_int(info.get("averageVolume")),
            market_cap=_safe_float(info.get("marketCap")),
            pe_ratio=_safe_float(info.get("trailingPE") or info.get("forwardPE")),
            fifty_two_week_high=_safe_float(info.get("fiftyTwoWeekHigh")),
            fifty_two_week_low=_safe_float(info.get("fiftyTwoWeekLow")),
            beta=_safe_float(info.get("beta")),
            dividend_yield=_safe_float(info.get("dividendYield")),
            currency=info.get("currency", "USD"),
        )

        logger.info("Successfully fetched metrics for %s", symbol)
        return metrics, history

    def fetch_history(self, symbol: str, period: str) -> pd.DataFrame:
        symbol = symbol.strip().upper()
        logger.info("Fetching %s history for %s", period, symbol)

        try:
            history = yf.Ticker(symbol).history(period=period)
        except ConnectionError as exc:
            raise NetworkError("Network error while fetching historical data.") from exc
        except Exception as exc:
            raise APIError("Failed to retrieve historical data.") from exc

        if history.empty:
            raise DataUnavailableError(f"No historical data available for '{symbol}' ({period}).")

        return history


def _safe_float(value) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _safe_int(value) -> int | None:
    if value is None:
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None

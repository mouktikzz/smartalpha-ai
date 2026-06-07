import logging
import re

import yfinance as yf

from app.models.schemas import TickerMatch
from app.services.exceptions import APIError, EmptyInputError, NetworkError

logger = logging.getLogger("smartalpha.ticker_resolver")


class TickerResolver:
    """Resolve company names or ticker symbols to tradable symbols."""

    TICKER_PATTERN = re.compile(r"^[A-Z]{1,5}(\.[A-Z]{1,2})?$")

    def resolve(self, query: str) -> list[TickerMatch]:
        query = (query or "").strip()
        if not query:
            raise EmptyInputError("Please enter a company name or ticker symbol.")

        logger.info("Resolving ticker for query: %s", query)

        if self._looks_like_ticker(query):
            match = self._resolve_direct_ticker(query.upper())
            return [match] if match else self._search(query)

        return self._search(query)

    def _looks_like_ticker(self, query: str) -> bool:
        return bool(self.TICKER_PATTERN.match(query.upper()))

    def _resolve_direct_ticker(self, symbol: str) -> TickerMatch | None:
        try:
            info = yf.Ticker(symbol).info
            if not info or info.get("regularMarketPrice") is None and info.get("currentPrice") is None:
                if not info.get("shortName") and not info.get("longName"):
                    return None
            return TickerMatch(
                symbol=symbol,
                name=info.get("longName") or info.get("shortName") or symbol,
                exchange=info.get("exchange", ""),
                quote_type=info.get("quoteType", "EQUITY"),
            )
        except Exception as exc:
            logger.warning("Direct ticker lookup failed for %s: %s", symbol, exc)
            return None

    def _search(self, query: str) -> list[TickerMatch]:
        try:
            search = yf.Search(query, max_results=10)
            quotes = getattr(search, "quotes", None) or []
        except ConnectionError as exc:
            logger.error("Network error during ticker search: %s", exc)
            raise NetworkError("Unable to connect to market data service. Check your network.") from exc
        except Exception as exc:
            logger.error("Ticker search API failure: %s", exc)
            raise APIError("Ticker search failed. Please try again later.") from exc

        matches: list[TickerMatch] = []
        seen: set[str] = set()

        for quote in quotes:
            symbol = quote.get("symbol", "")
            if not symbol or symbol in seen:
                continue
            if quote.get("quoteType", "").upper() not in ("EQUITY", "ETF", ""):
                continue

            seen.add(symbol)
            matches.append(
                TickerMatch(
                    symbol=symbol,
                    name=quote.get("longname") or quote.get("shortname") or symbol,
                    exchange=quote.get("exchange", ""),
                    quote_type=quote.get("quoteType", "EQUITY"),
                )
            )

        logger.info("Found %d matches for query '%s'", len(matches), query)
        return matches

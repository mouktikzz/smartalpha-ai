import logging
from datetime import datetime

import yfinance as yf

from app.models.schemas import NewsArticle
from app.services.exceptions import APIError, NetworkError

logger = logging.getLogger("smartalpha.news_service")


class NewsService:
    """Fetch company-related news headlines."""

    def fetch_news(self, symbol: str, limit: int = 10) -> list[NewsArticle]:
        symbol = symbol.strip().upper()
        logger.info("Fetching news for %s", symbol)

        try:
            raw_news = yf.Ticker(symbol).news or []
        except ConnectionError as exc:
            logger.error("Network error fetching news for %s: %s", symbol, exc)
            raise NetworkError("Network error while fetching news.") from exc
        except Exception as exc:
            logger.error("News API failure for %s: %s", symbol, exc)
            raise APIError("Failed to retrieve news data.") from exc

        articles: list[NewsArticle] = []
        for item in raw_news[:limit]:
            content = item.get("content", item)
            title = content.get("title") or item.get("title", "")
            if not title:
                continue

            provider = content.get("provider", {})
            publisher = provider.get("displayName", "") if isinstance(provider, dict) else ""
            link = ""
            if isinstance(content.get("canonicalUrl"), dict):
                link = content["canonicalUrl"].get("url", "")
            elif isinstance(content.get("clickThroughUrl"), dict):
                link = content["clickThroughUrl"].get("url", "")

            pub_date = content.get("pubDate") or content.get("displayTime") or item.get("providerPublishTime")
            published_at = _format_timestamp(pub_date)

            articles.append(
                NewsArticle(
                    title=title,
                    publisher=publisher,
                    link=link,
                    published_at=published_at,
                )
            )

        logger.info("Retrieved %d news articles for %s", len(articles), symbol)
        return articles


def _format_timestamp(value) -> str:
    if value is None:
        return ""
    try:
        if isinstance(value, (int, float)):
            return datetime.fromtimestamp(value).strftime("%Y-%m-%d %H:%M")
        return str(value)
    except (OSError, ValueError, OverflowError):
        return str(value)

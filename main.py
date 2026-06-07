"""CLI entry point for SmartAlpha AI."""

from dotenv import load_dotenv

from app.crew import run_analysis_crew
from app.logging_config import setup_logging
from app.services.news_service import NewsService
from app.services.stock_service import StockService
from app.services.technical_analysis import TechnicalAnalysisService
from app.services.ticker_resolver import TickerResolver

load_dotenv()
logger = setup_logging()


def run(query: str) -> None:
    logger.info("CLI analysis requested for: %s", query)

    matches = TickerResolver().resolve(query)
    if not matches:
        print("No matches found.")
        return

    symbol = matches[0].symbol
    print(f"Resolved: {symbol} — {matches[0].name}")

    metrics, history = StockService().validate_and_fetch(symbol)
    technical = TechnicalAnalysisService().analyze(symbol, history)
    articles = NewsService().fetch_news(symbol)
    news_payload = [{"title": a.title, "publisher": a.publisher} for a in articles]

    result = run_analysis_crew(symbol, metrics, technical, history, news_payload)
    print(result.model_dump_json(indent=2))


if __name__ == "__main__":
    run("Apple")

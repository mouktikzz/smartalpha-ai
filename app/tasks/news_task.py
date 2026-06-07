from crewai import Task

from app.agents.news_agent import create_news_agent
from app.models.schemas import NewsSentimentResult


def create_news_sentiment_task() -> Task:
    return Task(
        description=(
            "Analyze recent news for {stock}. "
            "Pre-fetched headlines: {news_json}. "
            "Use the Stock News Tool for the latest headlines. "
            "Classify overall sentiment as Bullish, Neutral, or Bearish. "
            "Provide a sentiment score from -1.0 (very bearish) to 1.0 (very bullish). "
            "List the top 3-5 recent headlines."
        ),
        expected_output=(
            "News sentiment analysis with:\n"
            "- Overall sentiment (Bullish/Neutral/Bearish)\n"
            "- Sentiment score (-1.0 to 1.0)\n"
            "- Top recent headlines\n"
            "- Brief sentiment summary"
        ),
        agent=create_news_agent(),
        output_pydantic=NewsSentimentResult,
    )

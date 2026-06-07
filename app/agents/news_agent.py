from crewai import Agent

from app.agents.llm_config import get_llm
from app.tools.stock_research_tool import get_stock_news


def create_news_agent() -> Agent:
    return Agent(
        role="Financial News Analyst",
        goal=(
            "Fetch and analyze the latest company-related news, classify sentiment as "
            "Bullish, Neutral, or Bearish, and generate a sentiment score."
        ),
        backstory=(
            "You are a financial news analyst who specializes in reading market headlines "
            "and extracting sentiment signals. You never rely on outdated knowledge — "
            "only on freshly retrieved news data."
        ),
        llm=get_llm(),
        tools=[get_stock_news],
        verbose=True,
    )

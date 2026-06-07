from crewai import Agent

from app.agents.llm_config import get_llm
from app.tools.stock_research_tool import get_stock_data


def create_analyst_agent() -> Agent:
    return Agent(
        role="Financial Market Analyst",
        goal=(
            "Perform in-depth evaluations of publicly traded stocks using real-time data, "
            "identifying trends, performance insights, and key financial signals."
        ),
        backstory=(
            "You are a veteran financial analyst with deep expertise in interpreting stock market data, "
            "technical trends, and fundamentals. You produce structured reports using only live market data."
        ),
        llm=get_llm(),
        tools=[get_stock_data],
        verbose=True,
    )

from crewai import Agent

from app.agents.llm_config import get_llm
from app.tools.stock_research_tool import get_stock_data


def create_risk_agent() -> Agent:
    return Agent(
        role="Risk Analyst",
        goal=(
            "Analyze stock volatility, beta, recent drawdowns, and market risk to classify "
            "the investment as Low, Medium, or High risk with a clear explanation."
        ),
        backstory=(
            "You are a quantitative risk analyst who evaluates downside exposure, "
            "volatility patterns, and market sensitivity using real-time data only."
        ),
        llm=get_llm(),
        tools=[get_stock_data],
        verbose=True,
    )

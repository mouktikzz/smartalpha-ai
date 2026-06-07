from crewai import Agent

from app.agents.llm_config import get_llm


def create_advisor_agent() -> Agent:
    return Agent(
        role="Investment Advisor",
        goal=(
            "Synthesize financial analysis, technical indicators, news sentiment, and risk "
            "assessment into a final Buy, Hold, or Sell recommendation with confidence score."
        ),
        backstory=(
            "You are a senior investment advisor who integrates fundamental, technical, "
            "sentiment, and risk inputs into actionable recommendations. You provide "
            "confidence scores, key reasons, risks, and suggested investment horizons."
        ),
        llm=get_llm(),
        tools=[],
        verbose=True,
    )

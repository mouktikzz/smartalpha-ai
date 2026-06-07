from crewai import Task

from app.agents.advisor_agent import create_advisor_agent
from app.models.schemas import InvestmentRecommendation


def create_investment_recommendation_task(context: list[Task]) -> Task:
    return Task(
        description=(
            "Provide a final investment recommendation for {stock} by synthesizing:\n"
            "1. Financial analysis from the analyst\n"
            "2. News sentiment analysis\n"
            "3. Risk assessment\n"
            "4. Technical trend: {technical_trend}\n\n"
            "Output a Buy, Hold, or Sell recommendation with:\n"
            "- Confidence score (0-100%)\n"
            "- Key reasons (3-5 points)\n"
            "- Key risks (2-3 points)\n"
            "- Suggested investment horizon (e.g., Short-term, Medium-term, Long-term)"
        ),
        expected_output=(
            "Final investment recommendation in structured format with "
            "recommendation, confidence, risk_level, sentiment, technical_trend, "
            "reasons, risks, and investment_horizon."
        ),
        agent=create_advisor_agent(),
        output_pydantic=InvestmentRecommendation,
        context=context,
    )

from crewai import Task

from app.agents.risk_agent import create_risk_agent
from app.models.schemas import RiskAssessmentResult


def create_risk_assessment_task() -> Task:
    return Task(
        description=(
            "Assess investment risk for {stock}. "
            "Pre-fetched metrics: {metrics_json}. "
            "Technical indicators: {technical_json}. "
            "Quantitative baseline risk: {baseline_risk_json}. "
            "Use live data tools to verify. Classify as Low, Medium, or High risk "
            "with explanation covering volatility, beta, drawdowns, and market risk."
        ),
        expected_output=(
            "Risk assessment with:\n"
            "- Risk level (Low/Medium/High)\n"
            "- Explanation of risk classification\n"
            "- Key risk factors (3-5 bullet points)"
        ),
        agent=create_risk_agent(),
        output_pydantic=RiskAssessmentResult,
    )

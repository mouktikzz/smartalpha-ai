from crewai import Task

from app.agents.analyst_agent import create_analyst_agent


def create_financial_analysis_task() -> Task:
    return Task(
        description=(
            "Analyze the stock {stock} using live market data. "
            "Pre-fetched metrics: {metrics_json}. "
            "Technical indicators: {technical_json}. "
            "Use the Live Stock Data Tool to verify and supplement. "
            "Summarize price action, fundamentals, volume trends, and key observations."
        ),
        expected_output=(
            "A structured financial analysis covering:\n"
            "- Current price and daily change\n"
            "- Volume vs average volume\n"
            "- Valuation metrics (P/E, market cap)\n"
            "- 52-week range position\n"
            "- Key performance observations"
        ),
        agent=create_analyst_agent(),
    )

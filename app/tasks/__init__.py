from app.tasks.analyse_task import create_financial_analysis_task
from app.tasks.news_task import create_news_sentiment_task
from app.tasks.recommendation_task import create_investment_recommendation_task
from app.tasks.risk_task import create_risk_assessment_task

__all__ = [
    "create_financial_analysis_task",
    "create_news_sentiment_task",
    "create_risk_assessment_task",
    "create_investment_recommendation_task",
]

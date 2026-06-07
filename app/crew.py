import json
import logging

import pandas as pd
from crewai import Crew

from app.models.schemas import (
    AnalysisResult,
    InvestmentRecommendation,
    NewsSentimentResult,
    RiskAssessmentResult,
    StockMetrics,
    TechnicalIndicators,
)
from app.services.risk_analysis import RiskAnalysisService
from app.tasks.analyse_task import create_financial_analysis_task
from app.tasks.news_task import create_news_sentiment_task
from app.tasks.recommendation_task import create_investment_recommendation_task
from app.tasks.risk_task import create_risk_assessment_task

logger = logging.getLogger("smartalpha.crew")


def run_analysis_crew(
    symbol: str,
    metrics: StockMetrics,
    technical: TechnicalIndicators,
    history: pd.DataFrame,
    news_articles: list[dict[str, str]],
) -> AnalysisResult:
    """Execute the multi-agent crew and return structured analysis."""
    baseline_risk = RiskAnalysisService().assess(metrics, technical, history)

    inputs = {
        "stock": symbol,
        "metrics_json": metrics.model_dump_json(),
        "technical_json": technical.model_dump_json(),
        "technical_trend": technical.technical_trend,
        "news_json": json.dumps(news_articles),
        "baseline_risk_json": baseline_risk.model_dump_json(),
    }

    analysis_task = create_financial_analysis_task()
    news_task = create_news_sentiment_task()
    risk_task = create_risk_assessment_task()
    recommendation_task = create_investment_recommendation_task(
        context=[analysis_task, news_task, risk_task]
    )

    crew = Crew(
        agents=[
            analysis_task.agent,
            news_task.agent,
            risk_task.agent,
            recommendation_task.agent,
        ],
        tasks=[analysis_task, news_task, risk_task, recommendation_task],
        verbose=True,
    )

    logger.info("Starting crew execution for %s", symbol)
    result = crew.kickoff(inputs=inputs)
    logger.info("Crew execution completed for %s", symbol)

    news_output = _extract_pydantic(result, NewsSentimentResult, index=1)
    risk_output = _extract_pydantic(result, RiskAssessmentResult, index=2)
    recommendation = _extract_pydantic(result, InvestmentRecommendation, index=3)

    if recommendation is None:
        recommendation = _fallback_recommendation(technical, news_output, risk_output, baseline_risk)

    if news_output is None:
        news_output = NewsSentimentResult(
            overall_sentiment="Neutral",
            sentiment_score=0.0,
            top_headlines=[a.get("title", "") for a in news_articles[:5]],
            summary="Unable to parse agent sentiment output.",
        )

    if risk_output is None:
        risk_output = baseline_risk

    return AnalysisResult(
        symbol=symbol,
        company_name=metrics.company_name,
        metrics=metrics,
        technical=technical,
        news_sentiment=news_output,
        risk_assessment=risk_output,
        recommendation=recommendation,
    )


def _extract_pydantic(result, model_class, index: int):
    try:
        output = result.tasks_output[index]
        if output.pydantic:
            return output.pydantic
        return model_class.model_validate_json(output.raw)
    except Exception as exc:
        logger.warning("Failed to parse %s from crew output: %s", model_class.__name__, exc)
        return None


def _fallback_recommendation(
    technical: TechnicalIndicators,
    news: NewsSentimentResult | None,
    risk: RiskAssessmentResult | None,
    baseline_risk: RiskAssessmentResult,
) -> InvestmentRecommendation:
    sentiment = news.overall_sentiment if news else "Neutral"
    risk_level = risk.risk_level if risk else baseline_risk.risk_level

    if technical.technical_trend == "Uptrend" and sentiment == "Bullish":
        rec = "BUY"
        confidence = 70
    elif technical.technical_trend == "Downtrend" and sentiment == "Bearish":
        rec = "SELL"
        confidence = 70
    else:
        rec = "HOLD"
        confidence = 55

    return InvestmentRecommendation(
        recommendation=rec,
        confidence=confidence,
        risk_level=risk_level,
        sentiment=sentiment,
        technical_trend=technical.technical_trend,
        reasons=["Based on combined technical and sentiment signals."],
        risks=["Agent output parsing failed — review raw analysis."],
        investment_horizon="Medium-term",
    )

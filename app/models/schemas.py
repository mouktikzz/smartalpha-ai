from typing import Literal, Optional

from pydantic import BaseModel, Field


class TickerMatch(BaseModel):
    symbol: str
    name: str
    exchange: str = ""
    quote_type: str = ""


class StockMetrics(BaseModel):
    symbol: str
    company_name: str
    current_price: Optional[float] = None
    daily_change: Optional[float] = None
    daily_change_percent: Optional[float] = None
    volume: Optional[int] = None
    average_volume: Optional[int] = None
    market_cap: Optional[float] = None
    pe_ratio: Optional[float] = None
    fifty_two_week_high: Optional[float] = None
    fifty_two_week_low: Optional[float] = None
    beta: Optional[float] = None
    dividend_yield: Optional[float] = None
    currency: str = "USD"


class TechnicalIndicators(BaseModel):
    symbol: str
    sma_50: Optional[float] = None
    sma_200: Optional[float] = None
    rsi_14: Optional[float] = None
    macd_line: Optional[float] = None
    macd_signal: Optional[float] = None
    daily_volatility: Optional[float] = None
    annualized_volatility: Optional[float] = None
    technical_trend: Literal["Uptrend", "Downtrend", "Sideways"] = "Sideways"


class NewsArticle(BaseModel):
    title: str
    publisher: str = ""
    link: str = ""
    published_at: str = ""


class NewsSentimentResult(BaseModel):
    overall_sentiment: Literal["Bullish", "Neutral", "Bearish"]
    sentiment_score: float = Field(ge=-1.0, le=1.0)
    top_headlines: list[str] = Field(default_factory=list)
    summary: str = ""


class RiskAssessmentResult(BaseModel):
    risk_level: Literal["Low", "Medium", "High"]
    explanation: str
    key_factors: list[str] = Field(default_factory=list)


class InvestmentRecommendation(BaseModel):
    recommendation: Literal["BUY", "HOLD", "SELL"]
    confidence: int = Field(ge=0, le=100)
    risk_level: Literal["Low", "Medium", "High"]
    sentiment: Literal["Bullish", "Neutral", "Bearish"]
    technical_trend: Literal["Uptrend", "Downtrend", "Sideways"]
    reasons: list[str] = Field(default_factory=list)
    risks: list[str] = Field(default_factory=list)
    investment_horizon: str = ""


class AnalysisResult(BaseModel):
    symbol: str
    company_name: str
    metrics: StockMetrics
    technical: TechnicalIndicators
    news_sentiment: NewsSentimentResult
    risk_assessment: RiskAssessmentResult
    recommendation: InvestmentRecommendation

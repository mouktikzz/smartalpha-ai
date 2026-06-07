import logging

import numpy as np
import pandas as pd

from app.models.schemas import RiskAssessmentResult, StockMetrics, TechnicalIndicators

logger = logging.getLogger("smartalpha.risk_analysis")


class RiskAnalysisService:
    """Quantitative risk assessment from market data."""

    def assess(
        self,
        metrics: StockMetrics,
        technical: TechnicalIndicators,
        history: pd.DataFrame,
    ) -> RiskAssessmentResult:
        logger.info("Assessing risk for %s", metrics.symbol)

        factors: list[str] = []
        risk_score = 0

        beta = metrics.beta
        if beta is not None:
            if beta > 1.5:
                risk_score += 2
                factors.append(f"High beta ({beta:.2f}) indicates above-market volatility")
            elif beta > 1.0:
                risk_score += 1
                factors.append(f"Beta ({beta:.2f}) is moderately above market average")
            else:
                factors.append(f"Beta ({beta:.2f}) suggests lower market sensitivity")

        ann_vol = technical.annualized_volatility
        if ann_vol is not None:
            if ann_vol > 0.5:
                risk_score += 2
                factors.append(f"High annualized volatility ({ann_vol * 100:.1f}%)")
            elif ann_vol > 0.3:
                risk_score += 1
                factors.append(f"Moderate annualized volatility ({ann_vol * 100:.1f}%)")
            else:
                factors.append(f"Relatively low annualized volatility ({ann_vol * 100:.1f}%)")

        drawdown = self._max_drawdown(history["Close"])
        if drawdown is not None:
            if drawdown < -0.3:
                risk_score += 2
                factors.append(f"Significant recent drawdown ({drawdown * 100:.1f}%)")
            elif drawdown < -0.15:
                risk_score += 1
                factors.append(f"Notable recent drawdown ({drawdown * 100:.1f}%)")
            else:
                factors.append(f"Limited recent drawdown ({drawdown * 100:.1f}%)")

        if metrics.current_price and metrics.fifty_two_week_high and metrics.fifty_two_week_low:
            range_position = (metrics.current_price - metrics.fifty_two_week_low) / (
                metrics.fifty_two_week_high - metrics.fifty_two_week_low
            )
            if range_position > 0.9:
                risk_score += 1
                factors.append("Trading near 52-week high — potential pullback risk")
            elif range_position < 0.1:
                factors.append("Trading near 52-week low — elevated downside uncertainty")

        if technical.rsi_14 is not None:
            if technical.rsi_14 > 70:
                risk_score += 1
                factors.append(f"RSI ({technical.rsi_14}) suggests overbought conditions")
            elif technical.rsi_14 < 30:
                factors.append(f"RSI ({technical.rsi_14}) suggests oversold conditions")

        if risk_score >= 4:
            level = "High"
            explanation = (
                "Multiple risk indicators point to elevated volatility and downside exposure. "
                "Position sizing and stop-loss discipline are recommended."
            )
        elif risk_score >= 2:
            level = "Medium"
            explanation = (
                "Risk is moderate with a mix of favorable and cautionary signals. "
                "Monitor key support levels and macro conditions."
            )
        else:
            level = "Low"
            explanation = (
                "Risk indicators are relatively subdued. "
                "Still subject to broader market movements and company-specific events."
            )

        return RiskAssessmentResult(
            risk_level=level,
            explanation=explanation,
            key_factors=factors,
        )

    def _max_drawdown(self, close: pd.Series) -> float | None:
        if close.empty:
            return None
        rolling_max = close.cummax()
        drawdown = (close - rolling_max) / rolling_max
        return float(drawdown.min())

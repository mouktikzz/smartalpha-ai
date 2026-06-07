import logging

import numpy as np
import pandas as pd

from app.models.schemas import TechnicalIndicators

logger = logging.getLogger("smartalpha.technical_analysis")


class TechnicalAnalysisService:
    """Calculate technical indicators from historical price data."""

    def analyze(self, symbol: str, history: pd.DataFrame) -> TechnicalIndicators:
        logger.info("Calculating technical indicators for %s", symbol)

        close = history["Close"].dropna()
        if len(close) < 20:
            logger.warning("Insufficient data for full technical analysis on %s", symbol)
            return TechnicalIndicators(symbol=symbol)

        sma_50 = float(close.tail(50).mean()) if len(close) >= 50 else None
        sma_200 = float(close.tail(200).mean()) if len(close) >= 200 else None
        rsi_14 = self._calculate_rsi(close, 14)
        macd_line, macd_signal = self._calculate_macd(close)
        daily_returns = close.pct_change().dropna()
        daily_vol = float(daily_returns.std()) if len(daily_returns) > 1 else None
        annualized_vol = float(daily_vol * np.sqrt(252)) if daily_vol is not None else None

        current_price = float(close.iloc[-1])
        trend = self._determine_trend(current_price, sma_50, sma_200, rsi_14)

        return TechnicalIndicators(
            symbol=symbol,
            sma_50=sma_50,
            sma_200=sma_200,
            rsi_14=rsi_14,
            macd_line=macd_line,
            macd_signal=macd_signal,
            daily_volatility=daily_vol,
            annualized_volatility=annualized_vol,
            technical_trend=trend,
        )

    def _calculate_rsi(self, close: pd.Series, period: int = 14) -> float | None:
        if len(close) < period + 1:
            return None

        delta = close.diff()
        gain = delta.clip(lower=0)
        loss = -delta.clip(upper=0)

        avg_gain = gain.rolling(window=period).mean()
        avg_loss = loss.rolling(window=period).mean()

        rs = avg_gain.iloc[-1] / avg_loss.iloc[-1] if avg_loss.iloc[-1] != 0 else 0
        rsi = 100 - (100 / (1 + rs))
        return round(float(rsi), 2)

    def _calculate_macd(self, close: pd.Series) -> tuple[float | None, float | None]:
        if len(close) < 26:
            return None, None

        ema_12 = close.ewm(span=12, adjust=False).mean()
        ema_26 = close.ewm(span=26, adjust=False).mean()
        macd = ema_12 - ema_26
        signal = macd.ewm(span=9, adjust=False).mean()

        return round(float(macd.iloc[-1]), 4), round(float(signal.iloc[-1]), 4)

    def _determine_trend(
        self,
        price: float,
        sma_50: float | None,
        sma_200: float | None,
        rsi: float | None,
    ) -> str:
        bullish_signals = 0
        bearish_signals = 0

        if sma_50 is not None and price > sma_50:
            bullish_signals += 1
        elif sma_50 is not None:
            bearish_signals += 1

        if sma_200 is not None and price > sma_200:
            bullish_signals += 1
        elif sma_200 is not None:
            bearish_signals += 1

        if sma_50 is not None and sma_200 is not None:
            if sma_50 > sma_200:
                bullish_signals += 1
            else:
                bearish_signals += 1

        if rsi is not None:
            if rsi > 55:
                bullish_signals += 1
            elif rsi < 45:
                bearish_signals += 1

        if bullish_signals > bearish_signals:
            return "Uptrend"
        if bearish_signals > bullish_signals:
            return "Downtrend"
        return "Sideways"

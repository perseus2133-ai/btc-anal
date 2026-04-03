"""
indicators.py
─────────────
기술적 지표를 계산하는 모듈.
순수 pandas/numpy만 사용하여 Streamlit Cloud 호환성 보장.
"""

import pandas as pd
import numpy as np


# ─────────────────────────────────────────────
# 개별 지표 계산 함수
# ─────────────────────────────────────────────

def _sma(series: pd.Series, length: int) -> pd.Series:
    """Simple Moving Average."""
    return series.rolling(window=length).mean()


def _ema(series: pd.Series, length: int) -> pd.Series:
    """Exponential Moving Average."""
    return series.ewm(span=length, adjust=False).mean()


def add_moving_averages(df: pd.DataFrame) -> pd.DataFrame:
    """이동평균선 MA 20, 50, 200을 추가한다."""
    df["MA20"] = _sma(df["close"], 20)
    df["MA50"] = _sma(df["close"], 50)
    df["MA200"] = _sma(df["close"], 200)
    return df


def add_macd(df: pd.DataFrame) -> pd.DataFrame:
    """MACD (12, 26, 9) 지표를 추가한다."""
    ema12 = _ema(df["close"], 12)
    ema26 = _ema(df["close"], 26)
    df["MACD"] = ema12 - ema26
    df["MACD_signal"] = _ema(df["MACD"], 9)
    df["MACD_hist"] = df["MACD"] - df["MACD_signal"]
    return df


def add_rsi(df: pd.DataFrame, period: int = 14) -> pd.DataFrame:
    """RSI(14) 지표를 추가한다."""
    delta = df["close"].diff()
    gain = delta.where(delta > 0, 0.0)
    loss = -delta.where(delta < 0, 0.0)

    avg_gain = gain.ewm(alpha=1 / period, min_periods=period, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1 / period, min_periods=period, adjust=False).mean()

    rs = avg_gain / avg_loss.replace(0, np.nan)
    df["RSI"] = 100 - (100 / (1 + rs))
    return df


def add_bollinger_bands(df: pd.DataFrame) -> pd.DataFrame:
    """볼린저 밴드 (20, 2)를 추가한다."""
    df["BB_mid"] = _sma(df["close"], 20)
    std = df["close"].rolling(window=20).std()
    df["BB_upper"] = df["BB_mid"] + 2 * std
    df["BB_lower"] = df["BB_mid"] - 2 * std
    df["BB_width"] = (df["BB_upper"] - df["BB_lower"]) / df["BB_mid"]
    bb_range = df["BB_upper"] - df["BB_lower"]
    df["BB_pct"] = (df["close"] - df["BB_lower"]) / bb_range.replace(0, np.nan)
    return df


def add_obv(df: pd.DataFrame) -> pd.DataFrame:
    """OBV(On-Balance Volume) 및 거래량 이동평균을 추가한다."""
    direction = np.sign(df["close"].diff())
    df["OBV"] = (df["volume"] * direction).fillna(0).cumsum()
    df["Vol_MA20"] = _sma(df["volume"], 20)
    return df


# ─────────────────────────────────────────────
# 통합 계산
# ─────────────────────────────────────────────

def calculate_all(df: pd.DataFrame) -> pd.DataFrame:
    """모든 기술적 지표를 한 번에 계산한다."""
    df = add_moving_averages(df)
    df = add_macd(df)
    df = add_rsi(df)
    df = add_bollinger_bands(df)
    df = add_obv(df)
    return df

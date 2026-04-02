"""
indicators.py
─────────────
기술적 지표를 계산하는 모듈.
pandas_ta를 사용하여 MA, MACD, RSI, 볼린저 밴드, OBV를 계산한다.
"""

import pandas as pd
import pandas_ta as ta


# ─────────────────────────────────────────────
# 개별 지표 계산 함수
# ─────────────────────────────────────────────

def add_moving_averages(df: pd.DataFrame) -> pd.DataFrame:
    """이동평균선 MA 20, 50, 200을 추가한다."""
    df["MA20"] = ta.sma(df["close"], length=20)
    df["MA50"] = ta.sma(df["close"], length=50)
    df["MA200"] = ta.sma(df["close"], length=200)
    return df


def add_macd(df: pd.DataFrame) -> pd.DataFrame:
    """MACD (12, 26, 9) 지표를 추가한다."""
    macd = ta.macd(df["close"], fast=12, slow=26, signal=9)
    df["MACD"] = macd.iloc[:, 0]        # MACD line
    df["MACD_hist"] = macd.iloc[:, 1]   # Histogram
    df["MACD_signal"] = macd.iloc[:, 2] # Signal line
    return df


def add_rsi(df: pd.DataFrame, period: int = 14) -> pd.DataFrame:
    """RSI(14) 지표를 추가한다."""
    df["RSI"] = ta.rsi(df["close"], length=period)
    return df


def add_bollinger_bands(df: pd.DataFrame) -> pd.DataFrame:
    """볼린저 밴드 (20, 2)를 추가한다."""
    bb = ta.bbands(df["close"], length=20, std=2)
    df["BB_lower"] = bb.iloc[:, 0]   # Lower band
    df["BB_mid"] = bb.iloc[:, 1]     # Middle band (SMA 20)
    df["BB_upper"] = bb.iloc[:, 2]   # Upper band
    df["BB_width"] = bb.iloc[:, 3]   # Bandwidth
    df["BB_pct"] = bb.iloc[:, 4]     # %B
    return df


def add_obv(df: pd.DataFrame) -> pd.DataFrame:
    """OBV(On-Balance Volume) 및 거래량 이동평균을 추가한다."""
    df["OBV"] = ta.obv(df["close"], df["volume"])
    df["Vol_MA20"] = ta.sma(df["volume"], length=20)
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


if __name__ == "__main__":
    # 테스트용
    from data_collector import fetch_ohlcv

    df = fetch_ohlcv("BTC/USDT", "1h", 300)
    df = calculate_all(df)
    print(df.tail(5).to_string())

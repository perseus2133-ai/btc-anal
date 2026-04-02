"""
data_collector.py
─────────────────
Binance 거래소에서 BTC/USDT OHLCV 데이터를 수집하는 모듈.
ccxt 라이브러리를 사용하여 1시간봉 및 4시간봉 데이터를 가져온다.
"""

import ccxt
import pandas as pd
from datetime import datetime


def create_exchange():
    """Binance 거래소 객체를 생성한다."""
    exchange = ccxt.binance({
        "enableRateLimit": True,
        "options": {"defaultType": "spot"},
    })
    return exchange


def fetch_ohlcv(
    symbol: str = "BTC/USDT",
    timeframe: str = "1h",
    limit: int = 300,
) -> pd.DataFrame:
    """
    Binance에서 OHLCV 데이터를 수집하여 DataFrame으로 반환한다.

    Parameters
    ----------
    symbol : str
        거래 심볼 (기본: BTC/USDT)
    timeframe : str
        타임프레임 (1h, 4h 등)
    limit : int
        캔들 수 (최대 1000, 기본 300)

    Returns
    -------
    pd.DataFrame
        columns: datetime, open, high, low, close, volume
    """
    exchange = create_exchange()

    print(f"  ▸ {symbol} {timeframe} 데이터 수집 중 (최근 {limit}개 캔들)...")
    raw = exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)

    df = pd.DataFrame(raw, columns=["timestamp", "open", "high", "low", "close", "volume"])
    df["datetime"] = pd.to_datetime(df["timestamp"], unit="ms")
    df.set_index("datetime", inplace=True)
    df.drop(columns=["timestamp"], inplace=True)

    # 숫자형 변환
    for col in ["open", "high", "low", "close", "volume"]:
        df[col] = df[col].astype(float)

    print(f"  ✔ {len(df)}개 캔들 수집 완료  |  기간: {df.index[0]} → {df.index[-1]}")
    return df


def fetch_multi_timeframe(
    symbol: str = "BTC/USDT",
    timeframes: list[str] | None = None,
    limit: int = 300,
) -> dict[str, pd.DataFrame]:
    """
    여러 타임프레임의 OHLCV를 한 번에 수집한다.

    Returns
    -------
    dict[str, pd.DataFrame]
        {timeframe: DataFrame} 딕셔너리
    """
    if timeframes is None:
        timeframes = ["1h", "4h"]

    result = {}
    for tf in timeframes:
        result[tf] = fetch_ohlcv(symbol, timeframe=tf, limit=limit)
    return result


if __name__ == "__main__":
    data = fetch_multi_timeframe()
    for tf, df in data.items():
        print(f"\n[{tf}] shape={df.shape}")
        print(df.tail(3))

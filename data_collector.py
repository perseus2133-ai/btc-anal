"""
data_collector.py
─────────────────
OHLCV 데이터를 수집하는 모듈.
Binance 차단 시 Bybit, OKX 순으로 자동 폴백.
"""

import ccxt
import pandas as pd


EXCHANGE_FALLBACKS = ["bybit", "binance", "okx", "gate"]


def create_exchange(name: str = "bybit"):
    """거래소 객체를 생성한다."""
    exchange_class = getattr(ccxt, name)
    exchange = exchange_class({
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
    OHLCV 데이터를 수집하여 DataFrame으로 반환한다.
    여러 거래소를 순차 시도하여 지역 제한을 우회한다.
    """
    last_error = None

    for ex_name in EXCHANGE_FALLBACKS:
        try:
            exchange = create_exchange(ex_name)
            print(f"  ▸ [{ex_name}] {symbol} {timeframe} 데이터 수집 중 (최근 {limit}개)...")
            raw = exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)

            df = pd.DataFrame(raw, columns=["timestamp", "open", "high", "low", "close", "volume"])
            df["datetime"] = pd.to_datetime(df["timestamp"], unit="ms")
            df.set_index("datetime", inplace=True)
            df.drop(columns=["timestamp"], inplace=True)

            for col in ["open", "high", "low", "close", "volume"]:
                df[col] = df[col].astype(float)

            print(f"  ✔ {len(df)}개 캔들 수집 완료 ({ex_name})  |  {df.index[0]} → {df.index[-1]}")
            return df

        except Exception as e:
            last_error = e
            print(f"  ⚠ [{ex_name}] 실패: {e}")
            continue

    raise RuntimeError(f"모든 거래소 연결 실패. 마지막 에러: {last_error}")


def fetch_multi_timeframe(
    symbol: str = "BTC/USDT",
    timeframes: list[str] | None = None,
    limit: int = 300,
) -> dict[str, pd.DataFrame]:
    """여러 타임프레임의 OHLCV를 한 번에 수집한다."""
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

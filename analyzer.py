"""
analyzer.py
───────────
기술적 지표를 종합하여 시장 상태를 진단하는 모듈.
강세(Bullish), 약세(Bearish), 횡보(Neutral) 판단 알고리즘.
"""

import pandas as pd
from dataclasses import dataclass, field


@dataclass
class Signal:
    """개별 시그널 판단 결과"""
    name: str
    score: float          # +1 bullish, -1 bearish, 0 neutral
    weight: float = 1.0   # 가중치
    reason: str = ""

    @property
    def weighted_score(self) -> float:
        return self.score * self.weight


@dataclass
class AnalysisResult:
    """종합 분석 결과"""
    signals: list[Signal] = field(default_factory=list)
    total_score: float = 0.0
    outlook: str = "Neutral"
    outlook_kr: str = "횡보"
    confidence: float = 0.0  # 0~100%
    current_price: float = 0.0
    summary: str = ""

    def to_dict(self) -> dict:
        return {
            "전망": f"{self.outlook} ({self.outlook_kr})",
            "신뢰도": f"{self.confidence:.0f}%",
            "현재가": f"${self.current_price:,.2f}",
            "종합점수": f"{self.total_score:+.1f}",
        }


# ─────────────────────────────────────────────
# 개별 시그널 판단 함수
# ─────────────────────────────────────────────

def _check_ma_alignment(row: pd.Series) -> Signal:
    """이동평균 정배열/역배열 판단."""
    ma20, ma50, ma200 = row.get("MA20"), row.get("MA50"), row.get("MA200")

    if pd.isna(ma200):
        return Signal("MA 정배열", 0, 1.0, "MA200 데이터 부족")

    if ma20 > ma50 > ma200:
        return Signal("MA 정배열", 1, 1.0, f"MA20({ma20:,.0f}) > MA50({ma50:,.0f}) > MA200({ma200:,.0f}) — 강한 상승 추세")
    elif ma20 < ma50 < ma200:
        return Signal("MA 정배열", -1, 1.0, f"MA20({ma20:,.0f}) < MA50({ma50:,.0f}) < MA200({ma200:,.0f}) — 강한 하락 추세")
    else:
        return Signal("MA 정배열", 0, 1.0, "혼조세 — 정배열/역배열 미완성")


def _check_macd(row: pd.Series) -> Signal:
    """MACD 시그널 판단."""
    macd = row.get("MACD")
    signal = row.get("MACD_signal")
    hist = row.get("MACD_hist")

    if pd.isna(macd) or pd.isna(signal):
        return Signal("MACD", 0, 1.0, "MACD 데이터 부족")

    if macd > signal and hist > 0:
        return Signal("MACD", 1, 1.0, f"MACD({macd:.1f}) > Signal({signal:.1f}), Hist > 0 — 매수 모멘텀")
    elif macd < signal and hist < 0:
        return Signal("MACD", -1, 1.0, f"MACD({macd:.1f}) < Signal({signal:.1f}), Hist < 0 — 매도 모멘텀")
    else:
        return Signal("MACD", 0, 1.0, "MACD 교차 근접 — 방향성 불명확")


def _check_rsi(row: pd.Series) -> Signal:
    """RSI 과매수/과매도 판단 (가중치 2배)."""
    rsi = row.get("RSI")

    if pd.isna(rsi):
        return Signal("RSI", 0, 2.0, "RSI 데이터 부족")

    if rsi > 70:
        return Signal("RSI", -1, 2.0, f"RSI {rsi:.1f} — ⚠️ 과매수 영역, 조정 가능성")
    elif rsi < 30:
        return Signal("RSI", 1, 2.0, f"RSI {rsi:.1f} — ⚠️ 과매도 영역, 반등 가능성")
    elif 50 < rsi <= 70:
        return Signal("RSI", 0.5, 2.0, f"RSI {rsi:.1f} — 건강한 상승 구간")
    elif 30 <= rsi <= 50:
        return Signal("RSI", -0.5, 2.0, f"RSI {rsi:.1f} — 약세 구간")
    else:
        return Signal("RSI", 0, 2.0, f"RSI {rsi:.1f}")


def _check_bollinger(row: pd.Series) -> Signal:
    """볼린저 밴드 위치 판단."""
    close = row.get("close")
    bb_upper = row.get("BB_upper")
    bb_mid = row.get("BB_mid")
    bb_lower = row.get("BB_lower")

    if pd.isna(bb_mid):
        return Signal("볼린저 밴드", 0, 1.0, "BB 데이터 부족")

    if close > bb_upper:
        return Signal("볼린저 밴드", -0.5, 1.0, f"가격이 상단 밴드 돌파 — 과열 가능성")
    elif close > bb_mid:
        return Signal("볼린저 밴드", 0.5, 1.0, f"가격이 중간선 위 — 상승 우위")
    elif close < bb_lower:
        return Signal("볼린저 밴드", 0.5, 1.0, f"가격이 하단 밴드 이탈 — 반등 가능성")
    else:
        return Signal("볼린저 밴드", -0.5, 1.0, f"가격이 중간선 아래 — 하락 우위")


def _check_volume(df: pd.DataFrame) -> Signal:
    """거래량 동반 여부 판단 (가중치 2배)."""
    if len(df) < 5:
        return Signal("거래량", 0, 2.0, "데이터 부족")

    recent = df.tail(5)
    last = recent.iloc[-1]
    obv_values = recent["OBV"].values

    vol_ma = last.get("Vol_MA20")
    current_vol = last.get("volume")

    if pd.isna(vol_ma) or pd.isna(current_vol):
        return Signal("거래량", 0, 2.0, "거래량 MA 데이터 부족")

    # 가격 변화 방향
    price_change = recent["close"].iloc[-1] - recent["close"].iloc[0]
    # OBV 방향
    obv_change = obv_values[-1] - obv_values[0]

    vol_ratio = current_vol / vol_ma if vol_ma > 0 else 1.0

    if price_change > 0 and obv_change > 0 and vol_ratio > 1.2:
        return Signal(
            "거래량", 1, 2.0,
            f"가격↑ + OBV↑ + 거래량 {vol_ratio:.1f}x 평균 — 강한 상승 동반"
        )
    elif price_change > 0 and (obv_change < 0 or vol_ratio < 0.8):
        return Signal(
            "거래량", -1, 2.0,
            f"가격↑인데 OBV↓ 또는 거래량 부족({vol_ratio:.1f}x) — ⚠️ 다이버전스"
        )
    elif price_change < 0 and obv_change < 0 and vol_ratio > 1.2:
        return Signal(
            "거래량", -1, 2.0,
            f"가격↓ + OBV↓ + 높은 거래량 — 매도 압력 강함"
        )
    elif price_change < 0 and vol_ratio < 0.8:
        return Signal(
            "거래량", 0.5, 2.0,
            f"가격↓이나 거래량 낮음({vol_ratio:.1f}x) — 하락 동력 약화"
        )
    else:
        return Signal("거래량", 0, 2.0, f"거래량 비율 {vol_ratio:.1f}x — 특이사항 없음")


# ─────────────────────────────────────────────
# 종합 분석
# ─────────────────────────────────────────────

def analyze(df: pd.DataFrame) -> AnalysisResult:
    """
    DataFrame의 마지막 행(최신 캔들)을 기준으로 종합 분석을 수행한다.

    Parameters
    ----------
    df : pd.DataFrame
        기술적 지표가 계산된 OHLCV DataFrame

    Returns
    -------
    AnalysisResult
        분석 결과 객체
    """
    last = df.iloc[-1]

    signals = [
        _check_ma_alignment(last),
        _check_macd(last),
        _check_rsi(last),
        _check_bollinger(last),
        _check_volume(df),
    ]

    # 가중 점수 합산
    total_weighted = sum(s.weighted_score for s in signals)
    max_possible = sum(s.weight for s in signals)  # 모두 +1일 때 최대값

    # 전망 판단
    if total_weighted >= 2.0:
        outlook, outlook_kr = "Bullish", "강세"
    elif total_weighted <= -2.0:
        outlook, outlook_kr = "Bearish", "약세"
    else:
        outlook, outlook_kr = "Neutral", "횡보"

    # 신뢰도: 점수의 절대값을 최대값 기준 백분율로
    confidence = min(abs(total_weighted) / max_possible * 100, 100)

    # 요약 문장
    if outlook == "Bullish":
        summary = "기술적 지표들이 전반적으로 상승을 가리키고 있습니다. 향후 24시간 내 추가 상승이 예상됩니다."
    elif outlook == "Bearish":
        summary = "기술적 지표들이 하락 신호를 보이고 있습니다. 향후 24시간 내 조정 또는 하락이 예상됩니다."
    else:
        summary = "기술적 지표가 혼조세를 보이고 있습니다. 향후 24시간은 횡보 가능성이 높습니다."

    return AnalysisResult(
        signals=signals,
        total_score=total_weighted,
        outlook=outlook,
        outlook_kr=outlook_kr,
        confidence=confidence,
        current_price=float(last["close"]),
        summary=summary,
    )


if __name__ == "__main__":
    from data_collector import fetch_ohlcv
    from indicators import calculate_all

    df = fetch_ohlcv("BTC/USDT", "1h", 300)
    df = calculate_all(df)
    result = analyze(df)

    print(f"\n전망: {result.outlook} ({result.outlook_kr})")
    print(f"신뢰도: {result.confidence:.0f}%")
    print(f"점수: {result.total_score:+.1f}")
    for s in result.signals:
        print(f"  [{s.name}] score={s.weighted_score:+.1f}  {s.reason}")

"""
main.py
───────
BTC/USDT 기술적 분석 프로그램 — 메인 오케스트레이터.

사용법:
    python main.py
"""

import sys
from datetime import datetime

from data_collector import fetch_multi_timeframe
from indicators import calculate_all
from analyzer import analyze
from visualizer import generate_chart
from report import print_full_report


def run():
    """메인 실행 함수."""
    print()
    print("=" * 60)
    print("  🚀  BTC/USDT Technical Analysis Engine")
    print(f"  📅  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    # ── Step 1: 데이터 수집 ──
    print("\n📡 [1/4] 데이터 수집 중...")
    try:
        data = fetch_multi_timeframe(
            symbol="BTC/USDT",
            timeframes=["1h", "4h"],
            limit=300,
        )
    except Exception as e:
        print(f"\n  ❌ 데이터 수집 실패: {e}")
        print("  💡 인터넷 연결을 확인하거나 VPN을 사옹해 보세요.")
        sys.exit(1)

    df_1h = data["1h"]
    df_4h = data["4h"]

    # ── Step 2: 기술적 지표 계산 ──
    print("\n📐 [2/4] 기술적 지표 계산 중...")
    df_1h = calculate_all(df_1h)
    df_4h = calculate_all(df_4h)
    print("  ✔ MA(20,50,200), MACD, RSI, 볼린저 밴드, OBV 계산 완료")

    # ── Step 3: 시장 분석 ──
    print("\n🧠 [3/4] 시장 상태 분석 중...")
    result_1h = analyze(df_1h)
    result_4h = analyze(df_4h)
    print(f"  ✔ 1시간봉: {result_1h.outlook} ({result_1h.outlook_kr})")
    print(f"  ✔ 4시간봉: {result_4h.outlook} ({result_4h.outlook_kr})")

    # ── Step 4: 차트 생성 ──
    print("\n📊 [4/4] 차트 생성 중...")
    chart_1h = generate_chart(df_1h, "1h", "btc_analysis_1h.png", last_n=100)
    chart_4h = generate_chart(df_4h, "4h", "btc_analysis_4h.png", last_n=100)

    # ── 리포트 출력 ──
    print_full_report(df_1h, df_4h, result_1h, result_4h)

    print(f"  📁 차트 파일:")
    print(f"     • {chart_1h}")
    print(f"     • {chart_4h}")
    print()


if __name__ == "__main__":
    run()

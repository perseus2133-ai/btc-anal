"""
app.py
──────
BTC/USDT Technical Analysis — Streamlit Dashboard.
메인 앱 엔트리 포인트. Streamlit Cloud에서 바로 실행 가능.

사용법:
    streamlit run app.py
"""

import streamlit as st
import pandas as pd
from datetime import datetime

from data_collector import fetch_ohlcv
from indicators import calculate_all
from analyzer import analyze
from components.charts import create_main_chart
from components.charts_3d import create_3d_scatter, create_3d_surface, create_3d_trajectory
from components.metrics import (
    render_custom_css,
    render_header,
    render_kpi_cards,
    render_signals,
    create_gauge_chart,
    render_disclaimer,
)

# ─────────────────────────────────────────────
# 페이지 설정
# ─────────────────────────────────────────────

st.set_page_config(
    page_title="BTC/USDT Technical Analysis",
    page_icon="🔮",
    layout="wide",
    initial_sidebar_state="expanded",
)

render_custom_css()


# ─────────────────────────────────────────────
# 사이드바
# ─────────────────────────────────────────────

with st.sidebar:
    st.markdown("### ⚙️ Settings")

    timeframe = st.selectbox(
        "📐 Timeframe",
        options=["1h", "4h", "15m", "1d"],
        index=0,
        help="분석할 타임프레임을 선택하세요.",
    )

    candle_count = st.slider(
        "🕯️ Candle Count",
        min_value=50,
        max_value=500,
        value=200,
        step=50,
        help="분석할 캔들 수",
    )

    chart_display = st.slider(
        "📊 Chart Display",
        min_value=30,
        max_value=200,
        value=100,
        step=10,
        help="차트에 표시할 최근 캔들 수",
    )

    st.markdown("---")

    refresh_btn = st.button("🔄 Refresh Data", use_container_width=True, type="primary")

    st.markdown("---")
    st.markdown(
        f"<div style='text-align:center; color:#94a3b8; font-size:0.75rem;'>"
        f"Last update<br>{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        f"</div>",
        unsafe_allow_html=True,
    )


# ─────────────────────────────────────────────
# 데이터 로드 (캐싱)
# ─────────────────────────────────────────────

@st.cache_data(ttl=300, show_spinner=False)
def load_data(symbol: str, tf: str, limit: int):
    """데이터를 수집하고 지표를 계산한다. 5분간 캐싱."""
    df = fetch_ohlcv(symbol, tf, limit)
    df = calculate_all(df)
    result = analyze(df)
    return df, result


# ─────────────────────────────────────────────
# 메인 콘텐츠
# ─────────────────────────────────────────────

render_header()

# 데이터 로드
try:
    with st.spinner("📡 Binance에서 데이터를 수집하고 있습니다..."):
        if refresh_btn:
            st.cache_data.clear()
        df, result = load_data("BTC/USDT", timeframe, candle_count)

except Exception as e:
    st.error(f"❌ 데이터 수집에 실패했습니다: {e}")
    st.info("💡 인터넷 연결을 확인하거나 VPN을 사용해 보세요.")
    st.stop()

# KPI 카드
render_kpi_cards(result, df)

st.markdown("<div style='height: 1.5rem'></div>", unsafe_allow_html=True)

# ─── 탭 구조 ───
tab1, tab2, tab3, tab4 = st.tabs([
    "📈  Chart Analysis",
    "🔮  3D Visualization",
    "🎯  Signals",
    "📋  Report",
])

# ─── 탭 1: 차트 분석 ───
with tab1:
    display_df = df.tail(chart_display)
    fig = create_main_chart(display_df, timeframe)
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": True})

    # 주요 지표 테이블
    with st.expander("📊 Indicator Details", expanded=False):
        last = df.iloc[-1]
        cols = st.columns(3)

        with cols[0]:
            st.markdown("**이동평균선**")
            for ma in ["MA20", "MA50", "MA200"]:
                val = last.get(ma)
                if pd.notna(val):
                    diff = ((last["close"] - val) / val) * 100
                    emoji = "🟢" if diff >= 0 else "🔴"
                    st.markdown(f"{emoji} {ma}: **${val:,.2f}** ({diff:+.2f}%)")

        with cols[1]:
            st.markdown("**모멘텀**")
            rsi = last.get("RSI")
            if pd.notna(rsi):
                st.markdown(f"RSI(14): **{rsi:.1f}**")
            macd = last.get("MACD")
            if pd.notna(macd):
                st.markdown(f"MACD: **{macd:.2f}**")
            macd_s = last.get("MACD_signal")
            if pd.notna(macd_s):
                st.markdown(f"Signal: **{macd_s:.2f}**")

        with cols[2]:
            st.markdown("**볼린저 밴드**")
            for bb, label in [("BB_upper", "Upper"), ("BB_mid", "Middle"), ("BB_lower", "Lower")]:
                val = last.get(bb)
                if pd.notna(val):
                    st.markdown(f"{label}: **${val:,.2f}**")

# ─── 탭 2: 3D 시각화 ───
with tab2:
    st.markdown("#### 🎲 3D Interactive Charts")
    st.caption("마우스로 드래그하여 회전, 스크롤로 확대/축소할 수 있습니다.")

    display_df_3d = df.tail(chart_display)

    # 3D Scatter
    fig_scatter = create_3d_scatter(display_df_3d, timeframe)
    st.plotly_chart(fig_scatter, use_container_width=True)

    col3d_1, col3d_2 = st.columns(2)

    with col3d_1:
        fig_surface = create_3d_surface(display_df_3d, timeframe)
        st.plotly_chart(fig_surface, use_container_width=True)

    with col3d_2:
        fig_traj = create_3d_trajectory(display_df_3d, timeframe)
        st.plotly_chart(fig_traj, use_container_width=True)

# ─── 탭 3: 시그널 ───
with tab3:
    col_gauge, col_signals = st.columns([1, 2])

    with col_gauge:
        st.markdown("#### 🧭 Market Sentiment")
        gauge = create_gauge_chart(result)
        st.plotly_chart(gauge, use_container_width=True)

        # 전망 배지
        outlook_cls = {
            "Bullish": "outlook-bullish",
            "Bearish": "outlook-bearish",
            "Neutral": "outlook-neutral",
        }.get(result.outlook, "outlook-neutral")

        st.markdown(
            f"<div style='text-align:center; margin-top:0.5rem;'>"
            f"<span class='outlook-badge {outlook_cls}'>"
            f"{result.outlook} ({result.outlook_kr})</span></div>",
            unsafe_allow_html=True,
        )

    with col_signals:
        st.markdown("#### 🔍 Signal Breakdown")
        render_signals(result)

# ─── 탭 4: 리포트 ───
with tab4:
    st.markdown("#### 📋 Analysis Report")

    # 종합 리포트 카드
    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, #f8fafc, #f1f5f9);
        border: 1px solid #e2e8f0;
        border-radius: 16px;
        padding: 2rem;
        margin-bottom: 1.5rem;
    ">
        <h3 style="color:#334155; margin:0 0 1rem 0;">🔮 향후 24시간 전망</h3>
        <p style="font-size:1.1rem; color:#475569; line-height:1.7;">
            {result.summary}
        </p>
        <div style="margin-top:1rem; display:flex; gap:2rem; flex-wrap:wrap;">
            <div>
                <span style="color:#94a3b8; font-size:0.8rem;">종합 점수</span><br>
                <span style="font-size:1.3rem; font-weight:700; color:#334155;">{result.total_score:+.1f}</span>
            </div>
            <div>
                <span style="color:#94a3b8; font-size:0.8rem;">신뢰도</span><br>
                <span style="font-size:1.3rem; font-weight:700; color:#334155;">{result.confidence:.0f}%</span>
            </div>
            <div>
                <span style="color:#94a3b8; font-size:0.8rem;">현재가</span><br>
                <span style="font-size:1.3rem; font-weight:700; color:#334155;">${result.current_price:,.2f}</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 시그널 요약 테이블
    signal_data = []
    for s in result.signals:
        signal_data.append({
            "시그널": s.name,
            "점수": f"{s.weighted_score:+.1f}",
            "가중치": f"x{s.weight:.0f}" if s.weight > 1 else "-",
            "판단 근거": s.reason,
        })
    st.dataframe(
        pd.DataFrame(signal_data),
        use_container_width=True,
        hide_index=True,
    )

    # 데이터 내보내기
    with st.expander("📥 Export Raw Data"):
        csv = df.tail(50).to_csv()
        st.download_button(
            label="Download CSV",
            data=csv,
            file_name=f"btc_analysis_{timeframe}_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            mime="text/csv",
        )

# 면책조항
render_disclaimer()

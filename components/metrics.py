"""
components/metrics.py
─────────────────────
KPI 카드, 전망 게이지, 시그널 표시 컴포넌트.
"""

import streamlit as st
import plotly.graph_objects as go
from analyzer import AnalysisResult


def render_custom_css():
    """프리미엄 라이트 테마 CSS를 주입한다."""
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

    /* 전체 폰트 */
    html, body, [class*="st-"] {
        font-family: 'Inter', sans-serif;
    }

    /* 메인 헤더 */
    .main-header {
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 50%, #a78bfa 100%);
        padding: 2rem 2.5rem;
        border-radius: 20px;
        color: white;
        margin-bottom: 1.5rem;
        box-shadow: 0 10px 40px rgba(99,102,241,0.2);
        position: relative;
        overflow: hidden;
    }
    .main-header::before {
        content: '';
        position: absolute;
        top: -50%;
        right: -20%;
        width: 300px;
        height: 300px;
        background: rgba(255,255,255,0.08);
        border-radius: 50%;
    }
    .main-header h1 {
        margin: 0;
        font-size: 1.8rem;
        font-weight: 800;
        letter-spacing: -0.5px;
    }
    .main-header p {
        margin: 0.3rem 0 0 0;
        font-size: 0.95rem;
        opacity: 0.85;
    }

    /* KPI 카드 */
    .kpi-card {
        background: white;
        border: 1px solid #e2e8f0;
        border-radius: 16px;
        padding: 1.3rem 1.5rem;
        box-shadow: 0 2px 12px rgba(0,0,0,0.04);
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    .kpi-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.08);
    }
    .kpi-card .kpi-icon {
        font-size: 1.8rem;
        margin-bottom: 0.3rem;
    }
    .kpi-card .kpi-label {
        font-size: 0.78rem;
        font-weight: 600;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 0.8px;
        margin-bottom: 0.2rem;
    }
    .kpi-card .kpi-value {
        font-size: 1.6rem;
        font-weight: 800;
        color: #1e293b;
        line-height: 1.2;
    }
    .kpi-card .kpi-sub {
        font-size: 0.8rem;
        font-weight: 500;
        margin-top: 0.2rem;
    }
    .kpi-sub.up { color: #10b981; }
    .kpi-sub.down { color: #ef4444; }
    .kpi-sub.neutral { color: #94a3b8; }

    /* 전망 배지 */
    .outlook-badge {
        display: inline-block;
        padding: 0.5rem 1.5rem;
        border-radius: 50px;
        font-size: 1rem;
        font-weight: 700;
        letter-spacing: 0.5px;
    }
    .outlook-bullish {
        background: linear-gradient(135deg, #d1fae5, #a7f3d0);
        color: #065f46;
    }
    .outlook-bearish {
        background: linear-gradient(135deg, #fee2e2, #fca5a5);
        color: #991b1b;
    }
    .outlook-neutral {
        background: linear-gradient(135deg, #fef3c7, #fde68a);
        color: #92400e;
    }

    /* 시그널 카드 */
    .signal-card {
        background: white;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 1rem 1.2rem;
        margin-bottom: 0.7rem;
        display: flex;
        align-items: center;
        gap: 1rem;
        box-shadow: 0 1px 6px rgba(0,0,0,0.03);
    }
    .signal-dot {
        width: 12px;
        height: 12px;
        border-radius: 50%;
        flex-shrink: 0;
    }
    .signal-dot.positive { background: #10b981; box-shadow: 0 0 8px rgba(16,185,129,0.4); }
    .signal-dot.negative { background: #ef4444; box-shadow: 0 0 8px rgba(239,68,68,0.4); }
    .signal-dot.neutral { background: #94a3b8; }
    .signal-name {
        font-weight: 600;
        font-size: 0.9rem;
        color: #334155;
        min-width: 80px;
    }
    .signal-score {
        font-weight: 700;
        font-size: 0.95rem;
        min-width: 50px;
        text-align: center;
    }
    .signal-score.positive { color: #10b981; }
    .signal-score.negative { color: #ef4444; }
    .signal-score.neutral { color: #94a3b8; }
    .signal-reason {
        font-size: 0.82rem;
        color: #64748b;
        flex: 1;
    }

    /* 탭 스타일 보정 */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: #f1f5f9;
        padding: 6px;
        border-radius: 12px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        font-weight: 600;
        font-size: 0.9rem;
    }

    /* 면책조항 */
    .disclaimer {
        text-align: center;
        font-size: 0.75rem;
        color: #94a3b8;
        padding: 1.5rem 0;
        border-top: 1px solid #e2e8f0;
        margin-top: 2rem;
    }
    </style>
    """, unsafe_allow_html=True)


def render_header():
    """메인 헤더를 렌더링한다."""
    st.markdown("""
    <div class="main-header">
        <h1>🔮 BTC/USDT Technical Analysis</h1>
        <p>Real-time technical analysis powered by Binance data & multi-indicator scoring</p>
    </div>
    """, unsafe_allow_html=True)


def render_kpi_cards(result: AnalysisResult, df=None):
    """KPI 카드 4개를 렌더링한다."""
    cols = st.columns(4)

    # 1. 현재 가격
    price = result.current_price
    if df is not None and len(df) > 1:
        prev_price = df["close"].iloc[-2]
        pct_change = ((price - prev_price) / prev_price) * 100
        sub_class = "up" if pct_change >= 0 else "down"
        sub_text = f"{'▲' if pct_change >= 0 else '▼'} {abs(pct_change):.2f}%"
    else:
        sub_class = "neutral"
        sub_text = ""

    with cols[0]:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-icon">💰</div>
            <div class="kpi-label">Current Price</div>
            <div class="kpi-value">${price:,.2f}</div>
            <div class="kpi-sub {sub_class}">{sub_text}</div>
        </div>
        """, unsafe_allow_html=True)

    # 2. RSI
    rsi = None
    if df is not None and "RSI" in df.columns:
        rsi = df["RSI"].iloc[-1]

    rsi_display = f"{rsi:.1f}" if rsi and not __import__('math').isnan(rsi) else "N/A"
    if rsi and not __import__('math').isnan(rsi):
        if rsi > 70:
            rsi_sub = "⚠️ 과매수"
            rsi_class = "down"
        elif rsi < 30:
            rsi_sub = "⚠️ 과매도"
            rsi_class = "up"
        else:
            rsi_sub = "정상 범위"
            rsi_class = "neutral"
    else:
        rsi_sub = ""
        rsi_class = "neutral"

    with cols[1]:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-icon">📊</div>
            <div class="kpi-label">RSI (14)</div>
            <div class="kpi-value">{rsi_display}</div>
            <div class="kpi-sub {rsi_class}">{rsi_sub}</div>
        </div>
        """, unsafe_allow_html=True)

    # 3. 종합 점수
    score = result.total_score
    sc_class = "up" if score > 0 else "down" if score < 0 else "neutral"
    with cols[2]:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-icon">🎯</div>
            <div class="kpi-label">Total Score</div>
            <div class="kpi-value">{score:+.1f}</div>
            <div class="kpi-sub {sc_class}">신뢰도 {result.confidence:.0f}%</div>
        </div>
        """, unsafe_allow_html=True)

    # 4. 전망
    outlook_cls = {
        "Bullish": "outlook-bullish",
        "Bearish": "outlook-bearish",
        "Neutral": "outlook-neutral",
    }.get(result.outlook, "outlook-neutral")
    emoji = {"Bullish": "🟢", "Bearish": "🔴", "Neutral": "🟡"}.get(result.outlook, "⚪")

    with cols[3]:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-icon">{emoji}</div>
            <div class="kpi-label">24H Outlook</div>
            <div style="margin-top:0.3rem;">
                <span class="outlook-badge {outlook_cls}">{result.outlook} ({result.outlook_kr})</span>
            </div>
        </div>
        """, unsafe_allow_html=True)


def render_signals(result: AnalysisResult):
    """시그널 카드들을 렌더링한다."""
    for s in result.signals:
        dot_class = "positive" if s.weighted_score > 0 else "negative" if s.weighted_score < 0 else "neutral"
        score_class = dot_class
        score_str = f"{s.weighted_score:+.1f}"
        weight_str = f" (x{s.weight:.0f})" if s.weight > 1 else ""

        st.markdown(f"""
        <div class="signal-card">
            <div class="signal-dot {dot_class}"></div>
            <div class="signal-name">{s.name}{weight_str}</div>
            <div class="signal-score {score_class}">{score_str}</div>
            <div class="signal-reason">{s.reason}</div>
        </div>
        """, unsafe_allow_html=True)


def create_gauge_chart(result: AnalysisResult) -> go.Figure:
    """전망 게이지 차트를 생성한다."""
    # 점수를 0-100 범위로 매핑
    max_score = sum(s.weight for s in result.signals)
    gauge_val = ((result.total_score + max_score) / (2 * max_score)) * 100

    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=gauge_val,
        number=dict(suffix="%", font=dict(size=28)),
        title=dict(text="Market Sentiment", font=dict(size=16, color="#334155")),
        gauge=dict(
            axis=dict(range=[0, 100], tickwidth=1, tickcolor="#e2e8f0"),
            bar=dict(color="#6366f1", thickness=0.3),
            bgcolor="white",
            borderwidth=2,
            bordercolor="#e2e8f0",
            steps=[
                dict(range=[0, 30], color="#fee2e2"),
                dict(range=[30, 45], color="#fef3c7"),
                dict(range=[45, 55], color="#f1f5f9"),
                dict(range=[55, 70], color="#d1fae5"),
                dict(range=[70, 100], color="#a7f3d0"),
            ],
            threshold=dict(
                line=dict(color="#1e293b", width=3),
                thickness=0.8,
                value=gauge_val,
            ),
        ),
    ))

    fig.update_layout(
        paper_bgcolor="white",
        font=dict(family="Inter, sans-serif", color="#334155"),
        height=280,
        margin=dict(l=30, r=30, t=60, b=20),
    )

    return fig


def render_disclaimer():
    """면책조항 렌더링."""
    st.markdown("""
    <div class="disclaimer">
        ⚠️ 이 분석은 기술적 지표에 기반한 참고 자료로, 투자 권유가 아닙니다.
        투자 결정은 본인의 판단과 책임 하에 이루어져야 합니다.
    </div>
    """, unsafe_allow_html=True)

"""
components/charts.py
────────────────────
Plotly 2D 인터랙티브 차트 모듈.
캔들차트, RSI, MACD, 거래량을 밝은 테마로 렌더링한다.
"""

import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd

# ─────────────────────────────────────────────
# 색상 팔레트 (밝은 테마)
# ─────────────────────────────────────────────

COLORS = {
    "bg": "#ffffff",
    "plot_bg": "#fafbfe",
    "grid": "#e2e8f0",
    "text": "#334155",
    "text_light": "#94a3b8",
    "green": "#10b981",
    "red": "#ef4444",
    "blue": "#6366f1",
    "purple": "#8b5cf6",
    "orange": "#f59e0b",
    "cyan": "#06b6d4",
    "pink": "#ec4899",
    "ma20": "#6366f1",
    "ma50": "#f59e0b",
    "ma200": "#ef4444",
    "bb_fill": "rgba(99,102,241,0.06)",
    "bb_line": "rgba(99,102,241,0.25)",
}

LAYOUT_COMMON = dict(
    paper_bgcolor=COLORS["bg"],
    plot_bgcolor=COLORS["plot_bg"],
    font=dict(family="Inter, sans-serif", color=COLORS["text"], size=12),
    margin=dict(l=60, r=30, t=50, b=40),
    hovermode="x unified",
    hoverlabel=dict(bgcolor="white", font_size=12, bordercolor="#e2e8f0"),
)


def create_main_chart(df: pd.DataFrame, timeframe: str = "1h") -> go.Figure:
    """
    캔들차트 + MA + BB + 거래량 + RSI + MACD 4패널 차트를 생성한다.
    """
    fig = make_subplots(
        rows=4, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.03,
        row_heights=[0.45, 0.15, 0.2, 0.2],
        subplot_titles=[
            f"BTC/USDT  [{timeframe}]",
            "Volume",
            "RSI (14)",
            "MACD (12, 26, 9)",
        ],
    )

    # ─── 1. 캔들차트 ───
    fig.add_trace(go.Candlestick(
        x=df.index,
        open=df["open"], high=df["high"],
        low=df["low"], close=df["close"],
        increasing=dict(line=dict(color=COLORS["green"]), fillcolor=COLORS["green"]),
        decreasing=dict(line=dict(color=COLORS["red"]), fillcolor=COLORS["red"]),
        name="Price",
        showlegend=False,
    ), row=1, col=1)

    # 이동평균선
    for ma, color, name in [
        ("MA20", COLORS["ma20"], "MA 20"),
        ("MA50", COLORS["ma50"], "MA 50"),
        ("MA200", COLORS["ma200"], "MA 200"),
    ]:
        if ma in df.columns and df[ma].notna().any():
            fig.add_trace(go.Scatter(
                x=df.index, y=df[ma],
                mode="lines",
                line=dict(color=color, width=1.5),
                name=name,
                opacity=0.85,
            ), row=1, col=1)

    # 볼린저 밴드
    if "BB_upper" in df.columns:
        fig.add_trace(go.Scatter(
            x=df.index, y=df["BB_upper"],
            mode="lines",
            line=dict(color=COLORS["bb_line"], width=1, dash="dot"),
            name="BB Upper",
            showlegend=False,
        ), row=1, col=1)
        fig.add_trace(go.Scatter(
            x=df.index, y=df["BB_lower"],
            mode="lines",
            line=dict(color=COLORS["bb_line"], width=1, dash="dot"),
            fill="tonexty",
            fillcolor=COLORS["bb_fill"],
            name="BB Lower",
            showlegend=False,
        ), row=1, col=1)

    # ─── 2. 거래량 ───
    vol_colors = [COLORS["green"] if c >= o else COLORS["red"]
                  for o, c in zip(df["open"], df["close"])]

    fig.add_trace(go.Bar(
        x=df.index, y=df["volume"],
        marker_color=vol_colors,
        opacity=0.5,
        name="Volume",
        showlegend=False,
    ), row=2, col=1)

    if "Vol_MA20" in df.columns:
        fig.add_trace(go.Scatter(
            x=df.index, y=df["Vol_MA20"],
            mode="lines",
            line=dict(color=COLORS["orange"], width=1.5),
            name="Vol MA20",
            showlegend=False,
        ), row=2, col=1)

    # ─── 3. RSI ───
    if "RSI" in df.columns:
        fig.add_trace(go.Scatter(
            x=df.index, y=df["RSI"],
            mode="lines",
            line=dict(color=COLORS["purple"], width=2),
            name="RSI",
            showlegend=False,
        ), row=3, col=1)

        # 과매수/과매도 라인
        fig.add_hline(y=70, line=dict(color=COLORS["red"], width=1, dash="dash"),
                      opacity=0.5, row=3, col=1)
        fig.add_hline(y=30, line=dict(color=COLORS["green"], width=1, dash="dash"),
                      opacity=0.5, row=3, col=1)
        fig.add_hline(y=50, line=dict(color=COLORS["text_light"], width=0.5, dash="dot"),
                      opacity=0.3, row=3, col=1)

        # 영역 채우기
        fig.add_hrect(y0=70, y1=100, fillcolor=COLORS["red"], opacity=0.04,
                      line_width=0, row=3, col=1)
        fig.add_hrect(y0=0, y1=30, fillcolor=COLORS["green"], opacity=0.04,
                      line_width=0, row=3, col=1)

    # ─── 4. MACD ───
    if "MACD" in df.columns:
        fig.add_trace(go.Scatter(
            x=df.index, y=df["MACD"],
            mode="lines",
            line=dict(color=COLORS["cyan"], width=1.8),
            name="MACD",
        ), row=4, col=1)

        fig.add_trace(go.Scatter(
            x=df.index, y=df["MACD_signal"],
            mode="lines",
            line=dict(color=COLORS["orange"], width=1.5),
            name="Signal",
        ), row=4, col=1)

        hist_colors = [COLORS["green"] if h >= 0 else COLORS["red"]
                       for h in df["MACD_hist"]]
        fig.add_trace(go.Bar(
            x=df.index, y=df["MACD_hist"],
            marker_color=hist_colors,
            opacity=0.4,
            name="Histogram",
            showlegend=False,
        ), row=4, col=1)

    # ─── 레이아웃 ───
    fig.update_layout(
        **LAYOUT_COMMON,
        height=900,
        xaxis_rangeslider_visible=False,
        legend=dict(
            orientation="h",
            yanchor="bottom", y=1.02,
            xanchor="right", x=1,
            bgcolor="rgba(255,255,255,0.8)",
            bordercolor=COLORS["grid"],
            borderwidth=1,
        ),
    )

    # 서브플롯 제목 스타일
    for annotation in fig.layout.annotations:
        annotation.font = dict(size=13, color=COLORS["text"], family="Inter, sans-serif")

    # Y축 설정
    fig.update_yaxes(gridcolor=COLORS["grid"], gridwidth=0.5, row=1, col=1)
    fig.update_yaxes(gridcolor=COLORS["grid"], gridwidth=0.5, row=2, col=1)
    fig.update_yaxes(gridcolor=COLORS["grid"], gridwidth=0.5, range=[10, 90], row=3, col=1)
    fig.update_yaxes(gridcolor=COLORS["grid"], gridwidth=0.5, row=4, col=1)

    # X축
    fig.update_xaxes(gridcolor=COLORS["grid"], gridwidth=0.5)

    return fig

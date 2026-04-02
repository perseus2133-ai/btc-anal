"""
components/charts_3d.py
───────────────────────
Plotly 3D 시각화 모듈.
Price-RSI-Volume 3D Scatter, 가격 지형 Surface, Trajectory 차트를 생성한다.
"""

import plotly.graph_objects as go
import pandas as pd
import numpy as np

# 밝은 테마 색상
COLORS = {
    "bg": "#ffffff",
    "text": "#334155",
    "green": "#10b981",
    "red": "#ef4444",
    "blue": "#6366f1",
    "purple": "#8b5cf6",
}

LAYOUT_3D_COMMON = dict(
    paper_bgcolor="#ffffff",
    font=dict(family="Inter, sans-serif", color="#334155", size=11),
    margin=dict(l=10, r=10, t=50, b=10),
)


def create_3d_scatter(df: pd.DataFrame, timeframe: str = "1h") -> go.Figure:
    """
    Price-RSI-Volume 3D Scatter Chart.
    X=시간 인덱스, Y=가격, Z=RSI, 점 크기=거래량, 색=상승/하락.
    """
    data = df.dropna(subset=["RSI"]).copy()
    data["time_idx"] = range(len(data))

    # 거래량 정규화 (점 크기)
    vol_norm = (data["volume"] - data["volume"].min()) / (data["volume"].max() - data["volume"].min() + 1e-10)
    marker_size = 4 + vol_norm * 16

    # 상승/하락 색
    colors = [COLORS["green"] if c >= o else COLORS["red"]
              for o, c in zip(data["open"], data["close"])]

    fig = go.Figure(data=[go.Scatter3d(
        x=data["time_idx"],
        y=data["close"],
        z=data["RSI"],
        mode="markers",
        marker=dict(
            size=marker_size,
            color=colors,
            opacity=0.75,
            line=dict(width=0.5, color="rgba(255,255,255,0.5)"),
        ),
        text=[
            f"Time: {idx.strftime('%m/%d %H:%M')}<br>"
            f"Price: ${c:,.2f}<br>"
            f"RSI: {r:.1f}<br>"
            f"Volume: {v:,.0f}"
            for idx, c, r, v in zip(data.index, data["close"], data["RSI"], data["volume"])
        ],
        hoverinfo="text",
    )])

    # 과매수/과매도 평면
    x_range = [data["time_idx"].min(), data["time_idx"].max()]
    y_range = [data["close"].min(), data["close"].max()]

    for z_val, color, name in [(70, "rgba(239,68,68,0.08)", "과매수"), (30, "rgba(16,185,129,0.08)", "과매도")]:
        fig.add_trace(go.Surface(
            x=np.array(x_range),
            y=np.array(y_range),
            z=np.full((2, 2), z_val),
            colorscale=[[0, color], [1, color]],
            showscale=False,
            name=name,
            opacity=0.3,
            hoverinfo="skip",
        ))

    fig.update_layout(
        **LAYOUT_3D_COMMON,
        title=dict(
            text=f"🔮 Price × RSI × Volume  [{timeframe}]",
            font=dict(size=16, color=COLORS["text"]),
        ),
        height=600,
        scene=dict(
            xaxis=dict(title="Time Index", backgroundcolor="#f8fafc", gridcolor="#e2e8f0"),
            yaxis=dict(title="Price ($)", backgroundcolor="#f8fafc", gridcolor="#e2e8f0"),
            zaxis=dict(title="RSI", backgroundcolor="#f8fafc", gridcolor="#e2e8f0", range=[10, 90]),
            bgcolor="#fafbfe",
            camera=dict(eye=dict(x=1.8, y=-1.5, z=0.8)),
        ),
    )

    return fig


def create_3d_surface(df: pd.DataFrame, timeframe: str = "1h") -> go.Figure:
    """
    3D Surface Chart — 가격 지형 시각화.
    X=시간, Y=지표 인덱스(MA20, MA50, BB_mid, close), Z=가격값.
    """
    data = df.dropna(subset=["MA20", "MA50"]).tail(80).copy()

    # 지형 데이터 구성
    indicator_names = []
    z_data = []

    for name, col in [("BB Lower", "BB_lower"), ("MA20", "MA20"), ("Close", "close"),
                       ("MA50", "MA50"), ("BB Upper", "BB_upper")]:
        if col in data.columns and data[col].notna().any():
            indicator_names.append(name)
            z_data.append(data[col].values)

    if not z_data:
        return go.Figure()

    z_array = np.array(z_data)
    x_vals = list(range(len(data)))
    y_vals = list(range(len(indicator_names)))

    fig = go.Figure(data=[go.Surface(
        x=x_vals,
        y=y_vals,
        z=z_array,
        colorscale=[
            [0.0, "#6366f1"],
            [0.25, "#8b5cf6"],
            [0.5, "#a78bfa"],
            [0.75, "#f59e0b"],
            [1.0, "#ef4444"],
        ],
        opacity=0.88,
        contours=dict(
            z=dict(show=True, usecolormap=True, highlightcolor="white", project_z=True),
        ),
        colorbar=dict(
            title=dict(text="Price ($)", side="right"),
            tickformat="$,.0f",
        ),
        hovertemplate=(
            "Time: %{x}<br>"
            "Layer: %{y}<br>"
            "Value: $%{z:,.2f}<extra></extra>"
        ),
    )])

    fig.update_layout(
        **LAYOUT_3D_COMMON,
        title=dict(
            text=f"🏔️ Price Terrain Surface  [{timeframe}]",
            font=dict(size=16, color=COLORS["text"]),
        ),
        height=600,
        scene=dict(
            xaxis=dict(title="Time →", backgroundcolor="#f8fafc", gridcolor="#e2e8f0"),
            yaxis=dict(
                title="Indicator",
                backgroundcolor="#f8fafc",
                gridcolor="#e2e8f0",
                tickvals=y_vals,
                ticktext=indicator_names,
            ),
            zaxis=dict(
                title="Price ($)",
                backgroundcolor="#f8fafc",
                gridcolor="#e2e8f0",
                tickformat="$,.0f",
            ),
            bgcolor="#fafbfe",
            camera=dict(eye=dict(x=1.5, y=-1.8, z=1.0)),
        ),
    )

    return fig


def create_3d_trajectory(df: pd.DataFrame, timeframe: str = "1h") -> go.Figure:
    """
    MACD-RSI-Price 3D Trajectory.
    가격 궤적을 3축 공간에서 시간순 라인으로 표시한다.
    """
    data = df.dropna(subset=["RSI", "MACD"]).tail(120).copy()

    # 시간 순 색상 그라데이션
    n = len(data)
    t_norm = np.linspace(0, 1, n)

    fig = go.Figure()

    # 궤적 라인
    fig.add_trace(go.Scatter3d(
        x=data["MACD"],
        y=data["RSI"],
        z=data["close"],
        mode="lines+markers",
        line=dict(
            color=t_norm,
            colorscale=[
                [0.0, "rgba(99,102,241,0.3)"],
                [0.5, "#8b5cf6"],
                [1.0, "#ef4444"],
            ],
            width=4,
        ),
        marker=dict(
            size=3,
            color=t_norm,
            colorscale=[
                [0.0, "rgba(99,102,241,0.4)"],
                [0.5, "#8b5cf6"],
                [1.0, "#ef4444"],
            ],
            colorbar=dict(title=dict(text="시간 →"), tickvals=[0, 1], ticktext=["과거", "현재"]),
        ),
        text=[
            f"{idx.strftime('%m/%d %H:%M')}<br>"
            f"MACD: {m:.1f}<br>"
            f"RSI: {r:.1f}<br>"
            f"Price: ${p:,.2f}"
            for idx, m, r, p in zip(data.index, data["MACD"], data["RSI"], data["close"])
        ],
        hoverinfo="text",
        name="Trajectory",
    ))

    # 시작/끝 점 강조
    for i, label, color, symbol in [
        (0, "Start", COLORS["blue"], "diamond"),
        (-1, "Now", COLORS["red"], "circle"),
    ]:
        row = data.iloc[i]
        fig.add_trace(go.Scatter3d(
            x=[row["MACD"]],
            y=[row["RSI"]],
            z=[row["close"]],
            mode="markers+text",
            marker=dict(size=10, color=color, symbol=symbol, line=dict(width=2, color="white")),
            text=[label],
            textposition="top center",
            textfont=dict(size=12, color=color),
            showlegend=False,
        ))

    # RSI 기준선 (수직면)
    macd_range = [data["MACD"].min(), data["MACD"].max()]
    price_range = [data["close"].min(), data["close"].max()]

    fig.update_layout(
        **LAYOUT_3D_COMMON,
        title=dict(
            text=f"🚀 MACD × RSI × Price Trajectory  [{timeframe}]",
            font=dict(size=16, color=COLORS["text"]),
        ),
        height=600,
        scene=dict(
            xaxis=dict(title="MACD", backgroundcolor="#f8fafc", gridcolor="#e2e8f0"),
            yaxis=dict(title="RSI", backgroundcolor="#f8fafc", gridcolor="#e2e8f0", range=[10, 90]),
            zaxis=dict(title="Price ($)", backgroundcolor="#f8fafc", gridcolor="#e2e8f0", tickformat="$,.0f"),
            bgcolor="#fafbfe",
            camera=dict(eye=dict(x=1.6, y=-1.4, z=1.0)),
        ),
        showlegend=False,
    )

    return fig

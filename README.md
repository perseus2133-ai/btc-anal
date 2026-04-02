# 🔮 BTC/USDT Technical Analysis Dashboard

Real-time Bitcoin technical analysis dashboard powered by Binance data, featuring interactive 2D/3D charts and multi-indicator market diagnosis.

![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Plotly](https://img.shields.io/badge/Plotly-3F4F75?style=for-the-badge&logo=plotly&logoColor=white)

## 🚀 Features

- **실시간 데이터**: Binance API를 통한 BTC/USDT OHLCV 수집
- **기술적 지표**: MA(20/50/200), MACD, RSI(14), Bollinger Bands, OBV
- **시장 진단**: 가중 점수 기반 Bullish/Bearish/Neutral 판단
- **3D 시각화**: Price×RSI×Volume Scatter, Price Terrain Surface, Trajectory
- **인터랙티브 차트**: Plotly 기반 줌/패닝/호버
- **프리미엄 UI**: 밝은 테마, KPI 카드, 게이지, 시그널 카드

## 📦 Installation

```bash
git clone https://github.com/YOUR_USERNAME/swift-halo.git
cd swift-halo
pip install -r requirements.txt
```

## ▶️ Run Locally

```bash
streamlit run app.py
```

## ☁️ Deploy on Streamlit Cloud

1. Push this repository to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub repository
4. Set **Main file path** to `app.py`
5. Click **Deploy** — done!

## 📁 Project Structure

```
swift-halo/
├── .streamlit/
│   └── config.toml          # Theme & server config
├── components/
│   ├── charts.py             # Plotly 2D charts
│   ├── charts_3d.py          # Plotly 3D visualizations
│   └── metrics.py            # KPI cards, gauge, CSS
├── app.py                    # Streamlit main app
├── data_collector.py         # Binance data fetching (ccxt)
├── indicators.py             # Technical indicators
├── analyzer.py               # Market state diagnosis
├── main.py                   # CLI version
├── requirements.txt          # Dependencies
└── README.md
```

## ⚠️ Disclaimer

This tool is for educational and informational purposes only. It is not financial advice. Always do your own research before making investment decisions.

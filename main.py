import os
from datetime import datetime, timezone
from typing import Optional

import requests
import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

API_KEY = os.getenv("TWELVE_DATA_API_KEY", "").strip()
app = FastAPI(title="AI Trading Analysis Web App")
app.mount("/static", StaticFiles(directory="static"), name="static")

PAIRS = {
    "EUR/USD": "EUR/USD",
    "GBP/USD": "GBP/USD",
    "USD/JPY": "USD/JPY",
    "AUD/USD": "AUD/USD",
    "USD/CHF": "USD/CHF",
}

@app.get("/")
def home():
    return FileResponse("static/index.html")

@app.get("/api/health")
def health():
    return {"status": "ok", "provider_configured": bool(API_KEY)}

def calc_rsi(close, period=14):
    delta = close.diff()
    gain = delta.clip(lower=0).ewm(alpha=1/period, adjust=False).mean()
    loss = (-delta.clip(upper=0)).ewm(alpha=1/period, adjust=False).mean()
    rs = gain / loss.replace(0, 1e-12)
    return 100 - (100 / (1 + rs))

@app.get("/api/analyze")
def analyze(pair: str = "EUR/USD", market: str = "forex"):
    market = market.lower()
    if market == "otc":
        return {
            "market": "otc", "pair": pair, "signal": "UNAVAILABLE",
            "message": "Quotex OTC ke liye verified official public feed configured nahi. Is liye koi OTC signal generate nahi kiya gaya.",
            "provider": None
        }
    if market != "forex":
        raise HTTPException(400, "Market must be forex or otc.")
    if pair not in PAIRS:
        raise HTTPException(400, "Unsupported pair.")
    if not API_KEY:
        raise HTTPException(503, "Server par TWELVE_DATA_API_KEY configure nahi hui.")
    try:
        response = requests.get(
            "https://api.twelvedata.com/time_series",
            params={"symbol": PAIRS[pair], "interval": "1min", "outputsize": 100,
                    "apikey": API_KEY, "format": "JSON"},
            timeout=20
        )
        response.raise_for_status()
        payload = response.json()
        if "values" not in payload:
            raise RuntimeError(payload.get("message", "Provider ne candle data nahi diya."))
        df = pd.DataFrame(payload["values"])
        for col in ["open", "high", "low", "close"]:
            df[col] = pd.to_numeric(df[col], errors="coerce")
        df = df.sort_values("datetime").dropna(subset=["close"]).reset_index(drop=True)
        if len(df) < 30:
            raise RuntimeError("Insufficient candles from data provider.")

        close = df["close"]
        ema9 = close.ewm(span=9, adjust=False).mean()
        ema21 = close.ewm(span=21, adjust=False).mean()
        ema12 = close.ewm(span=12, adjust=False).mean()
        ema26 = close.ewm(span=26, adjust=False).mean()
        macd = ema12 - ema26
        macd_signal = macd.ewm(span=9, adjust=False).mean()
        rsi = calc_rsi(close)

        score, reasons = 0, []
        if ema9.iloc[-1] > ema21.iloc[-1]:
            score += 1
            reasons.append("EMA 9, EMA 21 se upar hai")
        else:
            score -= 1
            reasons.append("EMA 9, EMA 21 se neeche hai")
        if macd.iloc[-1] > macd_signal.iloc[-1]:
            score += 1
            reasons.append("MACD bullish hai")
        else:
            score -= 1
            reasons.append("MACD bearish hai")
        rv = float(rsi.iloc[-1])
        if 50 < rv < 70:
            score += 1
            reasons.append("RSI bullish momentum zone mein hai")
        elif 30 < rv < 50:
            score -= 1
            reasons.append("RSI bearish momentum zone mein hai")
        else:
            reasons.append("RSI extreme/neutral hai; ehtiyat")

        if score >= 2 and rv < 70:
            signal = "UP"
        elif score <= -2 and rv > 30:
            signal = "DOWN"
        else:
            signal = "WAIT"

        return {
            "market": "forex", "pair": pair, "timeframe": "1 minute",
            "signal": signal, "score": score, "score_max": 3,
            "last_close": float(close.iloc[-1]),
            "last_candle_time": str(df["datetime"].iloc[-1]),
            "ema9": float(ema9.iloc[-1]), "ema21": float(ema21.iloc[-1]),
            "rsi14": rv, "macd": float(macd.iloc[-1]),
            "reasons": reasons,
            "provider": "Twelve Data",
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "warning": "Yeh rule-based indicator analysis hai, trained AI forecast nahi. Signal next candle ki guarantee nahi deta."
        }
    except requests.RequestException as exc:
        raise HTTPException(502, f"Market data request failed: {exc}")
    except Exception as exc:
        raise HTTPException(502, str(exc))

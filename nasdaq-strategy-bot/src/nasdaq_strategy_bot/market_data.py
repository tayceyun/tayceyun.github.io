from __future__ import annotations

import csv
import io
from dataclasses import dataclass
from datetime import date, timedelta

import pandas as pd
import requests
import urllib3
import yfinance as yf


@dataclass
class MarketSnapshot:
    market_date: str
    qqq_close: float
    qqqm_close: float
    vix_close: float
    qqq_all_time_high_close: float
    qqq_all_time_high_date: str


NASDAQ_HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json,text/plain,*/*",
    "Origin": "https://www.nasdaq.com",
    "Referer": "https://www.nasdaq.com/",
}

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def _http_get(url: str, headers: dict[str, str]) -> requests.Response:
    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        return response
    except requests.exceptions.SSLError:
        response = requests.get(url, headers=headers, timeout=30, verify=False)
        response.raise_for_status()
        return response


def _nasdaq_recent_close(symbol: str) -> tuple[str, float]:
    end_date = date.today()
    start_date = end_date - timedelta(days=14)
    url = (
        f"https://api.nasdaq.com/api/quote/{symbol}/historical"
        f"?assetclass=etf&fromdate={start_date.isoformat()}&limit=30&todate={end_date.isoformat()}"
    )
    response = _http_get(url, NASDAQ_HEADERS)
    payload = response.json()
    rows = (((payload or {}).get("data") or {}).get("tradesTable") or {}).get("rows") or []
    if not rows:
        raise RuntimeError(f"Nasdaq API 未返回 {symbol} 的历史数据")

    latest = rows[0]
    close_value = float(str(latest["close"]).replace(",", ""))
    market_date = pd.to_datetime(latest["date"], format="%m/%d/%Y").strftime("%Y-%m-%d")
    return market_date, close_value


def _cboe_latest_vix_close() -> tuple[str, float]:
    response = _http_get(
        "https://cdn.cboe.com/api/global/us_indices/daily_prices/VIX_History.csv",
        {"User-Agent": "Mozilla/5.0"},
    )
    rows = list(csv.DictReader(io.StringIO(response.text)))
    if not rows:
        raise RuntimeError("CBOE 未返回 VIX 历史数据")

    latest = rows[-1]
    close_value = float(latest["CLOSE"])
    market_date = pd.to_datetime(latest["DATE"], format="%m/%d/%Y").strftime("%Y-%m-%d")
    return market_date, close_value


def _daily_history(symbol: str, period: str = "20d") -> pd.DataFrame:
    history = yf.Ticker(symbol).history(period=period, interval="1d", auto_adjust=False)
    if history.empty:
        raise RuntimeError(f"无法获取 {symbol} 的历史数据")
    history = history[["Close"]].dropna(subset=["Close"]).copy()
    if history.empty:
        raise RuntimeError(f"{symbol} 的历史数据没有有效收盘价")
    history["market_date"] = history.index.tz_localize(None).strftime("%Y-%m-%d")
    history = history.drop_duplicates(subset=["market_date"], keep="last")
    return history.set_index("market_date")


def _all_time_high(symbol: str) -> tuple[float, str]:
    history = _daily_history(symbol, period="max")
    high_date = history["Close"].idxmax()
    high_close = float(history.loc[high_date, "Close"])
    return high_close, str(high_date)


def fetch_all_time_high(symbol: str) -> tuple[float, str]:
    return _all_time_high(symbol)


def fetch_market_snapshot(symbols: dict[str, str]) -> MarketSnapshot:
    qqq_date, qqq_close = _nasdaq_recent_close(symbols["qqq"])
    qqqm_date, qqqm_close = _nasdaq_recent_close(symbols["qqqm"])
    vix_date, vix_close = _cboe_latest_vix_close()

    if len({qqq_date, qqqm_date, vix_date}) != 1:
        raise RuntimeError(
            "无法获取最新美股收盘数据，请手动提供 QQQ / QQQM / VIX 收盘价: "
            f"QQQ最新={qqq_date}, QQQM最新={qqqm_date}, VIX最新={vix_date}"
        )
    market_date = qqq_date
    qqq_all_time_high_close, qqq_all_time_high_date = _all_time_high(symbols["qqq"])

    return MarketSnapshot(
        market_date=market_date,
        qqq_close=qqq_close,
        qqqm_close=qqqm_close,
        vix_close=vix_close,
        qqq_all_time_high_close=qqq_all_time_high_close,
        qqq_all_time_high_date=qqq_all_time_high_date,
    )

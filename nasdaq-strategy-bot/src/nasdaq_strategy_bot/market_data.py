from __future__ import annotations

from dataclasses import dataclass

import pandas as pd
import yfinance as yf


@dataclass
class MarketSnapshot:
    market_date: str
    qqq_close: float
    qqqm_close: float
    vix_close: float


def _daily_history(symbol: str) -> pd.DataFrame:
    history = yf.Ticker(symbol).history(period="20d", interval="1d", auto_adjust=False)
    if history.empty:
        raise RuntimeError(f"无法获取 {symbol} 的历史数据")
    history = history[["Close"]].dropna(subset=["Close"]).copy()
    if history.empty:
        raise RuntimeError(f"{symbol} 的历史数据没有有效收盘价")
    history["market_date"] = history.index.tz_localize(None).strftime("%Y-%m-%d")
    history = history.drop_duplicates(subset=["market_date"], keep="last")
    return history.set_index("market_date")


def fetch_market_snapshot(symbols: dict[str, str]) -> MarketSnapshot:
    qqq_history = _daily_history(symbols["qqq"])
    qqqm_history = _daily_history(symbols["qqqm"])
    vix_history = _daily_history(symbols["vix"])

    common_dates = sorted(
        set(qqq_history.index) & set(qqqm_history.index) & set(vix_history.index)
    )
    if not common_dates:
        raise RuntimeError(
            "无法找到 QQQ、QQQM、VIX 的共同交易日: "
            f"QQQ最近={qqq_history.index[-1]}, QQQM最近={qqqm_history.index[-1]}, VIX最近={vix_history.index[-1]}"
        )

    market_date = common_dates[-1]
    qqq_close = float(qqq_history.loc[market_date, "Close"])
    qqqm_close = float(qqqm_history.loc[market_date, "Close"])
    vix_close = float(vix_history.loc[market_date, "Close"])

    return MarketSnapshot(
        market_date=market_date,
        qqq_close=qqq_close,
        qqqm_close=qqqm_close,
        vix_close=vix_close,
    )

from __future__ import annotations

from dataclasses import dataclass

import yfinance as yf


@dataclass
class MarketSnapshot:
    market_date: str
    qqq_close: float
    qqqm_close: float
    vix_close: float


def _latest_close(symbol: str) -> tuple[str, float]:
    history = yf.Ticker(symbol).history(period="20d", interval="1d", auto_adjust=False)
    if history.empty:
        raise RuntimeError(f"无法获取 {symbol} 的历史数据")
    last_index = history.index[-1]
    market_date = last_index.tz_localize(None).strftime("%Y-%m-%d") if getattr(last_index, "tzinfo", None) else last_index.strftime("%Y-%m-%d")
    close_value = float(history.iloc[-1]["Close"])
    return market_date, close_value


def fetch_market_snapshot(symbols: dict[str, str]) -> MarketSnapshot:
    qqq_date, qqq_close = _latest_close(symbols["qqq"])
    qqqm_date, qqqm_close = _latest_close(symbols["qqqm"])
    vix_date, vix_close = _latest_close(symbols["vix"])

    if len({qqq_date, qqqm_date, vix_date}) != 1:
        raise RuntimeError(
            "市场数据日期不一致，暂不生成日报: "
            f"QQQ={qqq_date}, QQQM={qqqm_date}, VIX={vix_date}"
        )

    return MarketSnapshot(
        market_date=qqq_date,
        qqq_close=qqq_close,
        qqqm_close=qqqm_close,
        vix_close=vix_close,
    )

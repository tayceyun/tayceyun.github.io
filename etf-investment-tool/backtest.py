#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
策略回测工具
支持自定义股票代码、时间范围，验证9维度加权评分策略的有效性
"""

# 禁用 SSL 验证
import ssl
import os
import urllib3

ssl._create_default_https_context = ssl._create_unverified_context
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
os.environ['CURL_CA_BUNDLE'] = ''
os.environ['REQUESTS_CA_BUNDLE'] = ''

import requests

# 全局禁用 SSL 验证的推荐做法：monkey patch requests.Session.__init__，让所有实例默认 verify=False
_orig_init = requests.Session.__init__
def _patched_init(self, *args, **kwargs):
    _orig_init(self, *args, **kwargs)
    self.verify = False
requests.Session.__init__ = _patched_init

import argparse
import akshare as ak
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box
import csv

console = Console()

# 权重配置（与stock_analyzer.py保持一致）
WEIGHTS = {
    "ma_system": 0.25,
    "rsi": 0.15,
    "volume": 0.15,
    "cost_relation": 0.12,
    "macd": 0.10,
    "price_change": 0.10,
    "bollinger": 0.05,
    "market": 0.05,
    "sector": 0.03,
}


def get_historical_data(code: str, days: int = 250, start_date: str = None, end_date: str = None) -> pd.DataFrame:
    """获取历史数据"""
    try:
        # 判断是股票还是ETF
        if code.startswith('1') or code.startswith('5'):
            # ETF
            df = ak.fund_etf_hist_em(symbol=code, period="daily", adjust="qfq")
        else:
            # 股票
            df = ak.stock_zh_a_hist(symbol=code, period="daily", adjust="qfq")
        
        if df.empty:
            return None
        
        df['日期'] = pd.to_datetime(df['日期'])
        df = df.sort_values('日期').reset_index(drop=True)
        
        # 按日期范围筛选
        if start_date:
            df = df[df['日期'] >= pd.to_datetime(start_date)]
        if end_date:
            df = df[df['日期'] <= pd.to_datetime(end_date)]
        
        # 按天数筛选
        if not start_date and not end_date:
            df = df.tail(days + 120)  # 多取120天用于计算均线
        
        return df
    except Exception as e:
        console.print(f"[red]获取数据失败: {e}[/red]")
        return None


def calculate_indicators(df: pd.DataFrame, idx: int) -> dict:
    """计算技术指标"""
    if idx < 60:
        return None
    
    current_data = df.iloc[:idx+1]
    current_price = float(current_data['收盘'].iloc[-1])
    
    # 均线
    ma5 = float(current_data['收盘'].tail(5).mean())
    ma30 = float(current_data['收盘'].tail(30).mean())
    ma60 = float(current_data['收盘'].tail(60).mean())
    
    # RSI
    delta = current_data['收盘'].diff()
    gain = (delta.where(delta > 0, 0)).tail(14).mean()
    loss = (-delta.where(delta < 0, 0)).tail(14).mean()
    if loss == 0:
        rsi = 100
    else:
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
    
    # 成交量比
    vol_5 = current_data['成交量'].tail(5).mean()
    vol_20 = current_data['成交量'].tail(20).mean()
    vol_ratio = vol_5 / vol_20 if vol_20 > 0 else 1
    
    # MACD
    exp12 = current_data['收盘'].ewm(span=12, adjust=False).mean()
    exp26 = current_data['收盘'].ewm(span=26, adjust=False).mean()
    dif = exp12 - exp26
    dea = dif.ewm(span=9, adjust=False).mean()
    
    current_dif = float(dif.iloc[-1])
    current_dea = float(dea.iloc[-1])
    prev_dif = float(dif.iloc[-2]) if len(dif) > 1 else current_dif
    prev_dea = float(dea.iloc[-2]) if len(dea) > 1 else current_dea
    
    if prev_dif <= prev_dea and current_dif > current_dea:
        macd_cross = "golden"
    elif prev_dif >= prev_dea and current_dif < current_dea:
        macd_cross = "death"
    else:
        macd_cross = "none"
    
    # 布林带
    ma20 = current_data['收盘'].tail(20).mean()
    std20 = current_data['收盘'].tail(20).std()
    boll_upper = float(ma20 + 2 * std20)
    boll_lower = float(ma20 - 2 * std20)
    
    # 涨跌幅
    daily_change = (current_price - float(current_data['收盘'].iloc[-2])) / float(current_data['收盘'].iloc[-2]) * 100
    price_5_ago = float(current_data['收盘'].iloc[-6]) if len(current_data) > 5 else current_price
    weekly_change = (current_price - price_5_ago) / price_5_ago * 100
    
    return {
        "current_price": current_price,
        "ma5": ma5,
        "ma30": ma30,
        "ma60": ma60,
        "rsi": rsi,
        "vol_ratio": vol_ratio,
        "dif": current_dif,
        "dea": current_dea,
        "macd_cross": macd_cross,
        "boll_upper": boll_upper,
        "boll_lower": boll_lower,
        "daily_change": daily_change,
        "weekly_change": weekly_change,
    }


def calculate_dimension_scores(data: dict, cost: float) -> dict:
    """计算各维度得分"""
    if data is None:
        return {dim: 0 for dim in WEIGHTS.keys()}
    
    scores = {}
    current_price = data["current_price"]
    ma5, ma30, ma60 = data["ma5"], data["ma30"], data["ma60"]
    
    # 1. 均线系统
    if current_price < ma60 and ma5 < ma30 < ma60:
        scores["ma_system"] = 10
    elif current_price < ma60:
        scores["ma_system"] = 7
    elif current_price < ma30:
        scores["ma_system"] = 4
    elif current_price < ma5:
        scores["ma_system"] = 2
    elif current_price < ma5 * 1.03:
        scores["ma_system"] = 0
    elif current_price < ma5 * 1.05:
        scores["ma_system"] = -2
    elif current_price < ma30 * 1.10:
        scores["ma_system"] = -5
    elif current_price < ma60 * 1.15:
        scores["ma_system"] = -7
    else:
        scores["ma_system"] = -10
    
    # 2. RSI
    rsi = data["rsi"]
    if rsi < 20:
        scores["rsi"] = 10
    elif rsi < 30:
        scores["rsi"] = 7
    elif rsi < 40:
        scores["rsi"] = 4
    elif rsi < 60:
        scores["rsi"] = 0
    elif rsi < 70:
        scores["rsi"] = -4
    elif rsi < 80:
        scores["rsi"] = -7
    else:
        scores["rsi"] = -10
    
    # 3. 成交量
    vol_ratio = data["vol_ratio"]
    daily_change = data["daily_change"]
    if vol_ratio < 0.7 and daily_change < 0:
        scores["volume"] = 8
    elif vol_ratio < 0.8:
        scores["volume"] = 4
    elif vol_ratio < 1.2:
        scores["volume"] = 0
    elif vol_ratio < 1.5 and daily_change > 0:
        scores["volume"] = -2
    elif vol_ratio >= 1.5 and daily_change < 0:
        scores["volume"] = -3
    else:
        scores["volume"] = -5
    
    # 4. 成本关系
    profit_pct = (current_price - cost) / cost * 100 if cost > 0 else 0
    if profit_pct < -25:
        scores["cost_relation"] = 10
    elif profit_pct < -15:
        scores["cost_relation"] = 7
    elif profit_pct < -5:
        scores["cost_relation"] = 4
    elif profit_pct < 5:
        scores["cost_relation"] = 0
    elif profit_pct < 15:
        scores["cost_relation"] = -3
    elif profit_pct < 30:
        scores["cost_relation"] = -6
    else:
        scores["cost_relation"] = -9
    
    # 5. MACD
    if data["macd_cross"] == "golden":
        scores["macd"] = 8
    elif data["macd_cross"] == "death":
        scores["macd"] = -8
    elif data["dif"] > data["dea"] and data["dif"] > 0:
        scores["macd"] = 3
    elif data["dif"] > data["dea"]:
        scores["macd"] = 1
    elif data["dif"] < data["dea"] and data["dif"] < 0:
        scores["macd"] = -3
    else:
        scores["macd"] = -1
    
    # 6. 涨跌幅
    weekly_change = data["weekly_change"]
    if weekly_change < -12:
        scores["price_change"] = 10
    elif weekly_change < -8:
        scores["price_change"] = 7
    elif daily_change < -5:
        scores["price_change"] = 5
    elif abs(weekly_change) < 3:
        scores["price_change"] = 0
    elif daily_change > 5:
        scores["price_change"] = -5
    elif weekly_change > 10:
        scores["price_change"] = -8
    elif weekly_change > 15:
        scores["price_change"] = -10
    else:
        scores["price_change"] = -2 if weekly_change > 0 else 2
    
    # 7. 布林带
    if current_price <= data["boll_lower"]:
        scores["bollinger"] = 5
    elif current_price < (data["boll_upper"] + data["boll_lower"]) / 2:
        scores["bollinger"] = 2
    elif current_price < data["boll_upper"]:
        scores["bollinger"] = -2
    else:
        scores["bollinger"] = -5
    
    # 8. 大盘（简化）
    scores["market"] = 0
    
    # 9. 板块（简化）
    scores["sector"] = 0
    
    return scores


def calculate_weighted_score(scores: dict) -> float:
    """计算加权总分"""
    total = 0
    for dim, weight in WEIGHTS.items():
        total += scores.get(dim, 0) * weight
    return total


def run_backtest(code: str, df: pd.DataFrame, initial_cash: float = 100000, initial_shares: int = 0, cost: float = 0):
    """运行回测"""
    
    # 初始化
    cash = initial_cash
    shares = initial_shares
    if cost == 0 and len(df) > 60:
        cost = float(df.iloc[60]['收盘'])  # 初始成本取第一个有效交易日价格
    
    trades = []  # 交易记录
    daily_records = []  # 每日记录
    portfolio_values = []  # 组合价值
    
    start_idx = 60  # 从第60天开始（需要计算60日均线）
    
    for idx in range(start_idx, len(df)):
        date = df.iloc[idx]['日期']
        indicators = calculate_indicators(df, idx)
        
        if indicators is None:
            continue
        
        current_price = indicators["current_price"]
        scores = calculate_dimension_scores(indicators, cost)
        weighted_score = calculate_weighted_score(scores)
        
        # 记录每日数据
        daily_record = {
            "日期": date.strftime("%Y-%m-%d"),
            "收盘价": current_price,
            "MA5": indicators["ma5"],
            "MA30": indicators["ma30"],
            "MA60": indicators["ma60"],
            "RSI": indicators["rsi"],
            "加权评分": weighted_score,
        }
        daily_records.append(daily_record)
        
        # 交易逻辑
        action = None
        trade_shares = 0
        reason = ""
        
        if weighted_score >= 5.0:
            # 大力加仓：40%现金
            buy_amount = cash * 0.4
            trade_shares = int(buy_amount / current_price / 100) * 100
            if trade_shares >= 100 and cash >= trade_shares * current_price:
                action = "买入"
                reason = f"大力加仓(评分{weighted_score:.2f})"
                cash -= trade_shares * current_price
                shares += trade_shares
                # 更新成本
                if shares > 0:
                    total_cost = cost * (shares - trade_shares) + current_price * trade_shares
                    cost = total_cost / shares
                    
        elif weighted_score >= 3.0:
            # 正常加仓：25%现金
            buy_amount = cash * 0.25
            trade_shares = int(buy_amount / current_price / 100) * 100
            if trade_shares >= 100 and cash >= trade_shares * current_price:
                action = "买入"
                reason = f"正常加仓(评分{weighted_score:.2f})"
                cash -= trade_shares * current_price
                shares += trade_shares
                if shares > 0:
                    total_cost = cost * (shares - trade_shares) + current_price * trade_shares
                    cost = total_cost / shares
                    
        elif weighted_score >= 1.5:
            # 小仓加仓：15%现金
            buy_amount = cash * 0.15
            trade_shares = int(buy_amount / current_price / 100) * 100
            if trade_shares >= 100 and cash >= trade_shares * current_price:
                action = "买入"
                reason = f"小仓加仓(评分{weighted_score:.2f})"
                cash -= trade_shares * current_price
                shares += trade_shares
                if shares > 0:
                    total_cost = cost * (shares - trade_shares) + current_price * trade_shares
                    cost = total_cost / shares
                    
        elif weighted_score <= -5.0:
            # 大力减仓：40%持仓
            trade_shares = int(shares * 0.4 / 100) * 100
            if trade_shares >= 100:
                action = "卖出"
                reason = f"大力减仓(评分{weighted_score:.2f})"
                cash += trade_shares * current_price
                shares -= trade_shares
                
        elif weighted_score <= -3.0:
            # 正常减仓：25%持仓
            trade_shares = int(shares * 0.25 / 100) * 100
            if trade_shares >= 100:
                action = "卖出"
                reason = f"正常减仓(评分{weighted_score:.2f})"
                cash += trade_shares * current_price
                shares -= trade_shares
                
        elif weighted_score <= -1.5:
            # 小仓减仓：15%持仓
            trade_shares = int(shares * 0.15 / 100) * 100
            if trade_shares >= 100:
                action = "卖出"
                reason = f"小仓减仓(评分{weighted_score:.2f})"
                cash += trade_shares * current_price
                shares -= trade_shares
        
        # 记录交易
        if action:
            trades.append({
                "日期": date.strftime("%Y-%m-%d"),
                "操作": action,
                "价格": current_price,
                "数量": trade_shares,
                "金额": trade_shares * current_price,
                "评分": weighted_score,
                "原因": reason,
                "持仓": shares,
                "现金": cash,
            })
        
        # 记录组合价值
        portfolio_value = cash + shares * current_price
        portfolio_values.append({
            "日期": date,
            "组合价值": portfolio_value,
            "持仓数量": shares,
            "现金": cash,
            "股价": current_price,
        })
    
    return {
        "trades": trades,
        "daily_records": daily_records,
        "portfolio_values": portfolio_values,
        "final_cash": cash,
        "final_shares": shares,
        "final_cost": cost,
    }


def calculate_metrics(portfolio_values: list, df: pd.DataFrame, initial_value: float) -> dict:
    """计算回测指标"""
    if not portfolio_values:
        return {}
    
    values = [pv["组合价值"] for pv in portfolio_values]
    final_value = values[-1]
    
    # 总收益率
    total_return = (final_value - initial_value) / initial_value * 100
    
    # 持有收益率（买入持有）
    start_price = df.iloc[60]['收盘']
    end_price = df.iloc[-1]['收盘']
    hold_return = (end_price - start_price) / start_price * 100
    
    # 超额收益
    excess_return = total_return - hold_return
    
    # 年化收益率
    days = len(portfolio_values)
    annual_return = (1 + total_return / 100) ** (252 / days) - 1 if days > 0 else 0
    annual_return *= 100
    
    # 最大回撤
    peak = values[0]
    max_drawdown = 0
    for v in values:
        if v > peak:
            peak = v
        drawdown = (peak - v) / peak * 100
        if drawdown > max_drawdown:
            max_drawdown = drawdown
    
    # 日收益率
    daily_returns = []
    for i in range(1, len(values)):
        ret = (values[i] - values[i-1]) / values[i-1]
        daily_returns.append(ret)
    
    # 波动率
    volatility = np.std(daily_returns) * np.sqrt(252) * 100 if daily_returns else 0
    
    # 夏普比率（假设无风险利率3%）
    risk_free = 0.03
    avg_return = np.mean(daily_returns) * 252 if daily_returns else 0
    sharpe = (avg_return - risk_free) / (volatility / 100) if volatility > 0 else 0
    
    return {
        "initial_value": initial_value,
        "final_value": final_value,
        "total_return": total_return,
        "hold_return": hold_return,
        "excess_return": excess_return,
        "annual_return": annual_return,
        "max_drawdown": max_drawdown,
        "volatility": volatility,
        "sharpe": sharpe,
        "trading_days": days,
    }


def calculate_trade_stats(trades: list) -> dict:
    """计算交易统计"""
    if not trades:
        return {"total": 0, "buys": 0, "sells": 0, "win_rate": 0, "profit_factor": 0}
    
    buys = [t for t in trades if t["操作"] == "买入"]
    sells = [t for t in trades if t["操作"] == "卖出"]
    
    # 简化胜率计算：卖出价格 > 买入均价
    profits = []
    losses = []
    
    for i, sell in enumerate(sells):
        # 找之前的买入
        prev_buys = [b for b in buys if b["日期"] < sell["日期"]]
        if prev_buys:
            avg_buy_price = sum(b["价格"] * b["数量"] for b in prev_buys) / sum(b["数量"] for b in prev_buys)
            profit = (sell["价格"] - avg_buy_price) * sell["数量"]
            if profit > 0:
                profits.append(profit)
            else:
                losses.append(abs(profit))
    
    win_rate = len(profits) / len(sells) * 100 if sells else 0
    avg_profit = np.mean(profits) if profits else 0
    avg_loss = np.mean(losses) if losses else 1
    profit_factor = avg_profit / avg_loss if avg_loss > 0 else 0
    
    return {
        "total": len(trades),
        "buys": len(buys),
        "sells": len(sells),
        "win_rate": win_rate,
        "profit_factor": profit_factor,
        "total_profit": sum(profits),
        "total_loss": sum(losses),
    }


def print_summary(code: str, metrics: dict, trade_stats: dict, start_date: str, end_date: str):
    """打印摘要报告"""
    console.print()
    console.print(Panel.fit(
        f"[bold cyan]📈 策略回测摘要[/bold cyan]\n"
        f"[bold]{code}[/bold]\n"
        f"[dim]{start_date} ~ {end_date} (共{metrics.get('trading_days', 0)}个交易日)[/dim]",
        border_style="cyan"
    ))
    
    # 收益对比
    table1 = Table(title="[bold]收益对比[/bold]", box=box.ROUNDED)
    table1.add_column("指标", style="cyan")
    table1.add_column("策略收益", justify="right")
    table1.add_column("持有收益", justify="right")
    table1.add_column("超额收益", justify="right")
    
    total_ret = metrics.get("total_return", 0)
    hold_ret = metrics.get("hold_return", 0)
    excess_ret = metrics.get("excess_return", 0)
    
    table1.add_row(
        "总收益率",
        f"[{'green' if total_ret >= 0 else 'red'}]{total_ret:+.2f}%[/]",
        f"[{'green' if hold_ret >= 0 else 'red'}]{hold_ret:+.2f}%[/]",
        f"[{'green' if excess_ret >= 0 else 'red'}]{excess_ret:+.2f}%[/]",
    )
    table1.add_row(
        "年化收益率",
        f"[{'green' if metrics.get('annual_return', 0) >= 0 else 'red'}]{metrics.get('annual_return', 0):+.2f}%[/]",
        "-",
        "-",
    )
    
    console.print(table1)
    
    # 交易统计
    table2 = Table(title="[bold]交易统计[/bold]", box=box.ROUNDED)
    table2.add_column("指标", style="cyan")
    table2.add_column("数值", justify="right")
    
    table2.add_row("总交易次数", f"{trade_stats.get('total', 0)}次")
    table2.add_row("买入次数", f"{trade_stats.get('buys', 0)}次")
    table2.add_row("卖出次数", f"{trade_stats.get('sells', 0)}次")
    table2.add_row("胜率", f"{trade_stats.get('win_rate', 0):.1f}%")
    table2.add_row("盈亏比", f"{trade_stats.get('profit_factor', 0):.2f}")
    
    console.print(table2)
    
    # 风险指标
    table3 = Table(title="[bold]风险指标[/bold]", box=box.ROUNDED)
    table3.add_column("指标", style="cyan")
    table3.add_column("数值", justify="right")
    
    table3.add_row("最大回撤", f"[red]-{metrics.get('max_drawdown', 0):.2f}%[/red]")
    table3.add_row("夏普比率", f"{metrics.get('sharpe', 0):.2f}")
    table3.add_row("波动率", f"{metrics.get('volatility', 0):.2f}%")
    
    console.print(table3)
    
    # 策略评价
    excess = metrics.get("excess_return", 0)
    win_rate = trade_stats.get("win_rate", 0)
    
    if excess > 0 and win_rate > 50:
        evaluation = "[bold green]✅ 策略有效[/bold green]"
    elif excess > 0 or win_rate > 50:
        evaluation = "[bold yellow]⚠️ 策略一般[/bold yellow]"
    else:
        evaluation = "[bold red]❌ 策略无效[/bold red]"
    
    console.print(Panel(
        f"{evaluation}\n"
        f"超额收益: {excess:+.2f}%，胜率: {win_rate:.1f}%",
        title="[bold]策略评价[/bold]",
        border_style="green" if excess > 0 else "red",
    ))


def print_detail(trades: list, daily_records: list, show_all: bool = False):
    """打印详细数据"""
    console.print()
    console.print(Panel.fit(
        "[bold magenta]📋 交易明细记录[/bold magenta]",
        border_style="magenta"
    ))
    
    # 交易记录
    if trades:
        table = Table(title="[bold]交易操作记录[/bold]", box=box.ROUNDED)
        table.add_column("日期", width=12)
        table.add_column("操作", width=6)
        table.add_column("价格", justify="right", width=8)
        table.add_column("数量", justify="right", width=8)
        table.add_column("金额", justify="right", width=10)
        table.add_column("评分", justify="right", width=8)
        table.add_column("原因", width=24)
        
        display_trades = trades if show_all else trades[:20]
        for t in display_trades:
            color = "green" if t["操作"] == "买入" else "red"
            table.add_row(
                t["日期"],
                f"[{color}]{t['操作']}[/]",
                f"{t['价格']:.3f}",
                str(t["数量"]),
                f"¥{t['金额']:.0f}",
                f"{t['评分']:+.2f}",
                t["原因"],
            )
        
        if len(trades) > 20 and not show_all:
            table.add_row("...", "...", "...", "...", "...", "...", f"[dim]共{len(trades)}条记录[/dim]")
        
        console.print(table)
    else:
        console.print("[yellow]无交易记录[/yellow]")


def export_data(code: str, trades: list, daily_records: list, output_dir: str = "."):
    """导出数据到CSV"""
    # 导出交易记录
    trades_file = f"{output_dir}/backtest_{code}_trades.csv"
    if trades:
        with open(trades_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=trades[0].keys())
            writer.writeheader()
            writer.writerows(trades)
        console.print(f"[green]✅ 交易记录已导出: {trades_file}[/green]")
    
    # 导出每日数据
    daily_file = f"{output_dir}/backtest_{code}_daily.csv"
    if daily_records:
        with open(daily_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=daily_records[0].keys())
            writer.writeheader()
            writer.writerows(daily_records)
        console.print(f"[green]✅ 每日数据已导出: {daily_file}[/green]")


def main():
    parser = argparse.ArgumentParser(description="策略回测工具")
    parser.add_argument("--code", "-c", required=True, help="股票/ETF代码，多个用逗号分隔")
    parser.add_argument("--days", "-d", type=int, default=250, help="回测天数（默认250天）")
    parser.add_argument("--start", "-s", help="开始日期（YYYY-MM-DD）")
    parser.add_argument("--end", "-e", help="结束日期（YYYY-MM-DD）")
    parser.add_argument("--cash", type=float, default=100000, help="初始资金（默认10万）")
    parser.add_argument("--shares", type=int, default=0, help="初始持仓（默认0）")
    parser.add_argument("--cost", type=float, default=0, help="持仓成本（默认0）")
    parser.add_argument("--export", action="store_true", help="导出CSV文件")
    parser.add_argument("--detail", action="store_true", help="显示所有交易记录")
    
    args = parser.parse_args()
    
    codes = args.code.split(",")
    
    for code in codes:
        code = code.strip()
        console.print(f"\n[bold]正在回测 {code}...[/bold]")
        
        # 获取数据
        df = get_historical_data(code, args.days, args.start, args.end)
        if df is None or len(df) < 100:
            console.print(f"[red]数据不足，跳过 {code}[/red]")
            continue
        
        # 运行回测
        result = run_backtest(
            code, df,
            initial_cash=args.cash,
            initial_shares=args.shares,
            cost=args.cost
        )
        
        # 计算指标
        initial_value = args.cash + args.shares * (args.cost if args.cost > 0 else float(df.iloc[60]['收盘']))
        metrics = calculate_metrics(result["portfolio_values"], df, initial_value)
        trade_stats = calculate_trade_stats(result["trades"])
        
        # 日期范围
        start_date = df.iloc[60]['日期'].strftime("%Y-%m-%d")
        end_date = df.iloc[-1]['日期'].strftime("%Y-%m-%d")
        
        # 输出报告
        print_summary(code, metrics, trade_stats, start_date, end_date)
        print_detail(result["trades"], result["daily_records"], args.detail)
        
        # 导出数据
        if args.export:
            export_data(code, result["trades"], result["daily_records"])
    
    console.print()


if __name__ == "__main__":
    main()


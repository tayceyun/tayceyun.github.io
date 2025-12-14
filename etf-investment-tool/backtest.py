#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
策略回测工具
支持自定义股票代码、时间范围，验证策略有效性
- 9维度加权评分策略
- 网格交易策略
- 目标价策略（买入条件：现价 ≤ 目标价）
数据源：Tushare Pro / Baostock
"""

import argparse
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box
import csv

from data_source import get_historical_data

console = Console()

# 权重配置（与原 stock_analyzer.py 保持一致）
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


def run_score_backtest(code: str, df: pd.DataFrame, initial_cash: float = 100000, 
                       initial_shares: int = 0, cost: float = 0):
    """运行评分策略回测"""
    
    cash = initial_cash
    shares = initial_shares
    if cost == 0 and len(df) > 60:
        cost = float(df.iloc[60]['收盘'])
    
    trades = []
    portfolio_values = []
    
    start_idx = 60
    
    for idx in range(start_idx, len(df)):
        date = df.iloc[idx]['日期']
        indicators = calculate_indicators(df, idx)
        
        if indicators is None:
            continue
        
        current_price = indicators["current_price"]
        scores = calculate_dimension_scores(indicators, cost)
        weighted_score = calculate_weighted_score(scores)
        
        action = None
        trade_shares = 0
        reason = ""
        
        if weighted_score >= 5.0:
            buy_amount = cash * 0.4
            trade_shares = int(buy_amount / current_price / 100) * 100
            if trade_shares >= 100 and cash >= trade_shares * current_price:
                action = "买入"
                reason = f"大力加仓(评分{weighted_score:.2f})"
                cash -= trade_shares * current_price
                shares += trade_shares
                if shares > 0:
                    total_cost = cost * (shares - trade_shares) + current_price * trade_shares
                    cost = total_cost / shares
                    
        elif weighted_score >= 3.0:
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
                    
        elif weighted_score <= -5.0:
            trade_shares = int(shares * 0.4 / 100) * 100
            if trade_shares >= 100:
                action = "卖出"
                reason = f"大力减仓(评分{weighted_score:.2f})"
                cash += trade_shares * current_price
                shares -= trade_shares
                
        elif weighted_score <= -3.0:
            trade_shares = int(shares * 0.25 / 100) * 100
            if trade_shares >= 100:
                action = "卖出"
                reason = f"正常减仓(评分{weighted_score:.2f})"
                cash += trade_shares * current_price
                shares -= trade_shares
        
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
        "portfolio_values": portfolio_values,
        "final_cash": cash,
        "final_shares": shares,
        "final_cost": cost,
    }


def run_target_price_backtest(code: str, df: pd.DataFrame, initial_cash: float = 100000,
                               profit_target: float = 0.10, stop_loss: float = 0.08,
                               score_factor: float = 0.5, use_dynamic: bool = True):
    """动态目标价策略回测（结合9维度评分）
    
    策略逻辑：
    - 基础目标价 = MA20×40% + MA60×40% + 月K低点×20%
    - 动态目标价 = 基础目标价 × (1 + 加权评分 × score_factor%)
      - 评分高（看多）→ 目标价上调 → 更容易触发买入
      - 评分低（看空）→ 目标价下调 → 需要更大跌幅才买入
    - 买入条件：现价 ≤ 动态目标价
    - 卖出条件：
      - 止盈：现价 ≥ 买入价 × (1 + profit_target)
      - 止损：现价 ≤ 买入价 × (1 - stop_loss)
      - 技术面恶化：加权评分 ≤ -5
    
    Args:
        code: 股票代码
        df: 日线数据 DataFrame
        initial_cash: 初始资金
        profit_target: 止盈比例（默认 10%）
        stop_loss: 止损比例（默认 8%）
        score_factor: 评分调整系数（默认 0.5，即评分每1分调整0.5%）
        use_dynamic: 是否使用动态目标价（False则使用简单目标价）
    
    Returns:
        dict with trades, portfolio_values, metrics
    """
    cash = initial_cash
    shares = 0
    cost = 0  # 用于计算成本关系维度
    
    trades = []
    portfolio_values = []
    positions = []  # 记录每笔买入的成本
    
    start_idx = 60  # 需要足够数据计算 MA60
    
    # 初始化成本（用于评分系统的成本关系维度）
    if len(df) > 60:
        cost = float(df.iloc[60]['收盘'])
    
    for idx in range(start_idx, len(df)):
        date = df.iloc[idx]['日期']
        current_data = df.iloc[:idx+1]
        current_price = float(current_data['收盘'].iloc[-1])
        
        # 计算技术指标和9维度评分
        indicators = calculate_indicators(df, idx)
        dimension_scores = calculate_dimension_scores(indicators, cost) if indicators else {}
        weighted_score = calculate_weighted_score(dimension_scores)
        
        # 计算基础目标价
        ma20 = float(current_data['收盘'].tail(20).mean())
        ma60 = float(current_data['收盘'].tail(60).mean())
        monthly_low = float(current_data['最低'].tail(60).min())
        base_target = ma20 * 0.4 + ma60 * 0.4 + monthly_low * 0.2
        
        # 计算动态目标价（根据评分调整）
        if use_dynamic:
            # 评分范围 -10 到 +10，调整范围 -5% 到 +5%（默认 score_factor=0.5）
            score_adjustment = weighted_score * score_factor / 100
            dynamic_target = base_target * (1 + score_adjustment)
        else:
            dynamic_target = base_target
        
        action = None
        trade_shares = 0
        reason = ""
        
        # 1. 先检查卖出条件
        for pos in positions[:]:
            if pos["status"] != "holding":
                continue
            
            buy_price = pos["buy_price"]
            pos_shares = pos["shares"]
            
            # 止盈
            if current_price >= buy_price * (1 + profit_target):
                action = "卖出"
                trade_shares = pos_shares
                profit_pct = (current_price - buy_price) / buy_price * 100
                reason = f"止盈 +{profit_pct:.1f}%"
                cash += trade_shares * current_price
                shares -= trade_shares
                pos["status"] = "sold_profit"
                pos["sell_price"] = current_price
                pos["sell_date"] = date.strftime("%Y-%m-%d")
                break
            
            # 止损
            if current_price <= buy_price * (1 - stop_loss):
                action = "卖出"
                trade_shares = pos_shares
                loss_pct = (current_price - buy_price) / buy_price * 100
                reason = f"止损 {loss_pct:.1f}%"
                cash += trade_shares * current_price
                shares -= trade_shares
                pos["status"] = "sold_loss"
                pos["sell_price"] = current_price
                pos["sell_date"] = date.strftime("%Y-%m-%d")
                break
            
            # 技术面恶化卖出（评分极低）
            if weighted_score <= -5:
                action = "卖出"
                trade_shares = pos_shares
                loss_pct = (current_price - buy_price) / buy_price * 100
                reason = f"技术面恶化 (评分{weighted_score:.1f}, {'盈' if loss_pct >= 0 else '亏'}{abs(loss_pct):.1f}%)"
                cash += trade_shares * current_price
                shares -= trade_shares
                pos["status"] = "sold_technical"
                pos["sell_price"] = current_price
                pos["sell_date"] = date.strftime("%Y-%m-%d")
                break
        
        # 2. 检查买入条件：现价 ≤ 动态目标价
        if action is None and current_price <= dynamic_target:
            # 根据评分决定买入仓位
            if weighted_score >= 5:
                buy_ratio = 0.40  # 评分高，大力加仓
            elif weighted_score >= 3:
                buy_ratio = 0.30  # 评分较高，正常加仓
            elif weighted_score >= 0:
                buy_ratio = 0.20  # 评分中性，谨慎加仓
            else:
                buy_ratio = 0.10  # 评分低，小仓位试探
            
            buy_amount = cash * buy_ratio
            trade_shares = int(buy_amount / current_price / 100) * 100
            
            if trade_shares >= 100 and cash >= trade_shares * current_price:
                action = "买入"
                discount_pct = (dynamic_target - current_price) / dynamic_target * 100
                reason = f"现价{current_price:.2f}≤动态目标{dynamic_target:.2f} (折价{discount_pct:.1f}%, 评分{weighted_score:.1f})"
                cash -= trade_shares * current_price
                shares += trade_shares
                
                # 更新持仓成本
                if shares > 0:
                    total_cost = cost * (shares - trade_shares) + current_price * trade_shares
                    cost = total_cost / shares
                
                positions.append({
                    "buy_price": current_price,
                    "shares": trade_shares,
                    "buy_date": date.strftime("%Y-%m-%d"),
                    "base_target": base_target,
                    "dynamic_target": dynamic_target,
                    "weighted_score": weighted_score,
                    "status": "holding"
                })
        
        if action:
            trades.append({
                "日期": date.strftime("%Y-%m-%d"),
                "操作": action,
                "价格": current_price,
                "数量": trade_shares,
                "金额": trade_shares * current_price,
                "基础目标": round(base_target, 2),
                "动态目标": round(dynamic_target, 2),
                "评分": round(weighted_score, 2),
                "原因": reason,
                "持仓": shares,
                "现金": round(cash, 2),
            })
        
        portfolio_value = cash + shares * current_price
        portfolio_values.append({
            "日期": date,
            "组合价值": portfolio_value,
            "持仓数量": shares,
            "现金": cash,
            "股价": current_price,
            "基础目标": base_target,
            "动态目标": dynamic_target,
            "评分": weighted_score,
        })
    
    # 统计交易结果
    profit_trades = len([p for p in positions if p["status"] == "sold_profit"])
    loss_trades = len([p for p in positions if p["status"] == "sold_loss"])
    technical_sells = len([p for p in positions if p["status"] == "sold_technical"])
    holding_trades = len([p for p in positions if p["status"] == "holding"])
    total_closed = profit_trades + loss_trades + technical_sells
    win_rate = profit_trades / total_closed * 100 if total_closed > 0 else 0
    
    return {
        "trades": trades,
        "portfolio_values": portfolio_values,
        "final_cash": cash,
        "final_shares": shares,
        "positions": positions,
        "trade_stats": {
            "profit_trades": profit_trades,
            "loss_trades": loss_trades,
            "technical_sells": technical_sells,
            "holding_trades": holding_trades,
            "win_rate": win_rate,
        }
    }


def run_grid_backtest(code: str, df: pd.DataFrame, initial_cash: float = 100000,
                      initial_shares: int = 0, grid_step: float = 3.5,
                      base_amount: float = 2000):
    """运行网格交易策略回测"""
    
    cash = initial_cash
    shares = initial_shares
    
    trades = []
    portfolio_values = []
    grid_positions = []  # 记录每格买入
    
    start_idx = 60
    
    for idx in range(start_idx, len(df)):
        date = df.iloc[idx]['日期']
        current_data = df.iloc[:idx+1]
        current_price = float(current_data['收盘'].iloc[-1])
        
        # 动态计算中枢价格
        ma20 = float(current_data['收盘'].tail(20).mean())
        ma60 = float(current_data['收盘'].tail(60).mean())
        monthly_low = float(current_data['最低'].tail(60).min())
        center_price = ma20 * 0.4 + ma60 * 0.4 + monthly_low * 0.2
        
        # 计算网格档位
        grid_levels = [center_price]
        for i in range(1, 7):
            grid_levels.append(center_price * (1 - grid_step * i / 100))
        
        # 确定当前所在格
        current_level = 0
        for i, level in enumerate(grid_levels):
            if current_price >= level:
                current_level = i
                break
        else:
            current_level = len(grid_levels) - 1
        
        action = None
        trade_shares = 0
        reason = ""
        
        # 买入逻辑：价格跌破新的格子
        for i, pos in enumerate(grid_positions):
            if pos["status"] == "pending" and current_price <= pos["trigger_price"]:
                # 触发买入
                deviation = abs((current_price - center_price) / center_price * 100)
                buy_amount = base_amount * (1 + deviation * 0.5 / 100)
                trade_shares = int(buy_amount / current_price / 100) * 100
                
                if trade_shares >= 100 and cash >= trade_shares * current_price:
                    action = "买入"
                    reason = f"触发格{pos['grid_level']}买入"
                    cash -= trade_shares * current_price
                    shares += trade_shares
                    pos["status"] = "holding"
                    pos["buy_price"] = current_price
                    pos["shares"] = trade_shares
                    pos["buy_date"] = date.strftime("%Y-%m-%d")
                break
        
        # 检查是否需要添加新的网格
        if not action:
            existing_levels = [p["grid_level"] for p in grid_positions]
            for i in range(1, len(grid_levels)):
                if i not in existing_levels and current_price < grid_levels[i-1]:
                    grid_positions.append({
                        "grid_level": i,
                        "trigger_price": grid_levels[i],
                        "status": "pending"
                    })
        
        # 卖出逻辑：价格涨回上一格
        for pos in grid_positions:
            if pos["status"] == "holding" and pos["grid_level"] > 0:
                sell_trigger = grid_levels[pos["grid_level"] - 1]
                if current_price >= sell_trigger:
                    trade_shares = pos.get("shares", 0)
                    if trade_shares >= 100:
                        action = "卖出"
                        reason = f"涨回格{pos['grid_level']-1}卖出"
                        cash += trade_shares * current_price
                        shares -= trade_shares
                        pos["status"] = "sold"
                        pos["sell_price"] = current_price
                        pos["sell_date"] = date.strftime("%Y-%m-%d")
                    break
        
        if action:
            trades.append({
                "日期": date.strftime("%Y-%m-%d"),
                "操作": action,
                "价格": current_price,
                "数量": trade_shares,
                "金额": trade_shares * current_price,
                "原因": reason,
                "持仓": shares,
                "现金": cash,
            })
        
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
        "portfolio_values": portfolio_values,
        "final_cash": cash,
        "final_shares": shares,
        "grid_positions": grid_positions,
    }


def calculate_metrics(portfolio_values: list, df: pd.DataFrame, initial_value: float) -> dict:
    """计算回测指标"""
    if not portfolio_values:
        return {}
    
    values = [pv["组合价值"] for pv in portfolio_values]
    final_value = values[-1]
    
    total_return = (final_value - initial_value) / initial_value * 100
    
    start_price = df.iloc[60]['收盘']
    end_price = df.iloc[-1]['收盘']
    hold_return = (end_price - start_price) / start_price * 100
    
    excess_return = total_return - hold_return
    
    days = len(portfolio_values)
    annual_return = (1 + total_return / 100) ** (252 / days) - 1 if days > 0 else 0
    annual_return *= 100
    
    peak = values[0]
    max_drawdown = 0
    for v in values:
        if v > peak:
            peak = v
        drawdown = (peak - v) / peak * 100
        if drawdown > max_drawdown:
            max_drawdown = drawdown
    
    daily_returns = []
    for i in range(1, len(values)):
        ret = (values[i] - values[i-1]) / values[i-1]
        daily_returns.append(ret)
    
    volatility = np.std(daily_returns) * np.sqrt(252) * 100 if daily_returns else 0
    
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


def print_summary(code: str, strategy: str, metrics: dict, trades: list, 
                  start_date: str, end_date: str, trade_stats: dict = None,
                  strategy_params: dict = None):
    """打印摘要报告"""
    console.print()
    console.print(Panel.fit(
        f"[bold cyan]📈 {strategy}策略回测摘要[/bold cyan]\n"
        f"[bold]{code}[/bold]\n"
        f"[dim]{start_date} ~ {end_date} (共{metrics.get('trading_days', 0)}个交易日)[/dim]",
        border_style="cyan"
    ))
    
    # 策略参数（目标价策略）
    if strategy_params:
        table0 = Table(title="[bold]策略参数[/bold]", box=box.ROUNDED)
        table0.add_column("参数", style="cyan")
        table0.add_column("数值", justify="left")
        
        if "formula" in strategy_params:
            table0.add_row("基础目标价", strategy_params["formula"])
        if "dynamic_formula" in strategy_params:
            table0.add_row("动态调整", strategy_params["dynamic_formula"])
        if "score_factor" in strategy_params:
            table0.add_row("评分系数", f"{strategy_params['score_factor']}%/分")
        if "profit_target" in strategy_params:
            table0.add_row("止盈比例", f"{strategy_params['profit_target']*100:.0f}%")
        if "stop_loss" in strategy_params:
            table0.add_row("止损比例", f"{strategy_params['stop_loss']*100:.0f}%")
        
        console.print(table0)
    
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
    buys = [t for t in trades if t["操作"] == "买入"]
    sells = [t for t in trades if t["操作"] == "卖出"]
    
    table2 = Table(title="[bold]交易统计[/bold]", box=box.ROUNDED)
    table2.add_column("指标", style="cyan")
    table2.add_column("数值", justify="right")
    
    table2.add_row("总交易次数", f"{len(trades)}次")
    table2.add_row("买入次数", f"{len(buys)}次")
    table2.add_row("卖出次数", f"{len(sells)}次")
    
    # 目标价策略额外统计
    if trade_stats:
        table2.add_row("止盈次数", f"[green]{trade_stats.get('profit_trades', 0)}次[/green]")
        table2.add_row("止损次数", f"[red]{trade_stats.get('loss_trades', 0)}次[/red]")
        if trade_stats.get('technical_sells', 0) > 0:
            table2.add_row("技术面卖出", f"[yellow]{trade_stats.get('technical_sells', 0)}次[/yellow]")
        table2.add_row("持仓中", f"{trade_stats.get('holding_trades', 0)}笔")
        table2.add_row("胜率", f"[bold]{trade_stats.get('win_rate', 0):.1f}%[/bold]")
    
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
    
    if excess > 5:
        evaluation = "[bold green]✅ 策略非常有效[/bold green]"
    elif excess > 0:
        evaluation = "[bold green]✅ 策略有效[/bold green]"
    elif excess > -5:
        evaluation = "[bold yellow]⚠️ 策略一般[/bold yellow]"
    else:
        evaluation = "[bold red]❌ 策略无效[/bold red]"
    
    console.print(Panel(
        f"{evaluation}\n超额收益: {excess:+.2f}%",
        title="[bold]策略评价[/bold]",
        border_style="green" if excess > 0 else "red",
    ))


def main():
    parser = argparse.ArgumentParser(description="策略回测工具")
    parser.add_argument("--code", "-c", required=True, help="股票/ETF代码")
    parser.add_argument("--strategy", "-s", choices=["score", "grid", "target"], default="score",
                        help="策略类型: score(评分) 或 grid(网格) 或 target(目标价)")
    parser.add_argument("--days", "-d", type=int, default=250, help="回测天数（默认250天）")
    parser.add_argument("--start", help="开始日期（YYYY-MM-DD）")
    parser.add_argument("--end", help="结束日期（YYYY-MM-DD）")
    parser.add_argument("--cash", type=float, default=100000, help="初始资金（默认10万）")
    parser.add_argument("--shares", type=int, default=0, help="初始持仓（默认0）")
    parser.add_argument("--grid-step", type=float, default=3.5, help="网格间距（默认3.5%%）")
    parser.add_argument("--profit-target", type=float, default=0.10, help="止盈比例（默认10%%）")
    parser.add_argument("--stop-loss", type=float, default=0.08, help="止损比例（默认8%%）")
    parser.add_argument("--score-factor", type=float, default=0.5, help="评分调整系数（默认0.5，即评分每1分调整0.5%%目标价）")
    parser.add_argument("--simple-target", action="store_true", help="使用简单目标价（不用评分调整）")
    parser.add_argument("--export", action="store_true", help="导出CSV文件")
    
    args = parser.parse_args()
    
    strategy_names = {
        "score": "评分",
        "grid": "网格交易",
        "target": "目标价"
    }
    
    console.print(f"\n[bold]正在回测 {args.code} ({strategy_names[args.strategy]}策略)...[/bold]")
    
    # 获取数据（统一使用 Baostock）
    console.print("[dim]使用 Baostock 数据源...[/dim]")
    df = get_historical_data(args.code, args.start, args.end, args.days)
    
    if df is None or len(df) < 100:
        console.print(f"[red]数据不足，无法回测（需要至少100条记录）[/red]")
        return
    
    console.print(f"[dim]获取到 {len(df)} 条数据[/dim]")
    
    # 运行回测
    trade_stats = None
    strategy_params = None
    
    if args.strategy == "target":
        use_dynamic = not args.simple_target
        result = run_target_price_backtest(
            args.code, df,
            initial_cash=args.cash,
            profit_target=args.profit_target,
            stop_loss=args.stop_loss,
            score_factor=args.score_factor,
            use_dynamic=use_dynamic
        )
        strategy_name = "动态目标价" if use_dynamic else "简单目标价"
        trade_stats = result.get("trade_stats")
        strategy_params = {
            "formula": "基础目标价 = MA20×40% + MA60×40% + 月K低点×20%",
            "profit_target": args.profit_target,
            "stop_loss": args.stop_loss,
        }
        if use_dynamic:
            strategy_params["dynamic_formula"] = f"动态目标价 = 基础目标价 × (1 + 评分×{args.score_factor}%)"
            strategy_params["score_factor"] = args.score_factor
    elif args.strategy == "grid":
        result = run_grid_backtest(
            args.code, df,
            initial_cash=args.cash,
            initial_shares=args.shares,
            grid_step=args.grid_step
        )
        strategy_name = "网格交易"
    else:
        result = run_score_backtest(
            args.code, df,
            initial_cash=args.cash,
            initial_shares=args.shares
        )
        strategy_name = "评分"
    
    # 计算指标
    initial_value = args.cash + args.shares * float(df.iloc[60]['收盘'])
    metrics = calculate_metrics(result["portfolio_values"], df, initial_value)
    
    # 日期范围
    start_date = df.iloc[60]['日期'].strftime("%Y-%m-%d")
    end_date = df.iloc[-1]['日期'].strftime("%Y-%m-%d")
    
    # 输出终端报告
    print_summary(args.code, strategy_name, metrics, result["trades"], start_date, end_date,
                  trade_stats=trade_stats, strategy_params=strategy_params)
    
    # 导出CSV数据
    if args.export and result["trades"]:
        filename = f"backtest_{args.code}_{args.strategy}.csv"
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=result["trades"][0].keys())
            writer.writeheader()
            writer.writerows(result["trades"])
        console.print(f"[green]✅ 交易记录已导出: {filename}[/green]")
    
    console.print()


if __name__ == "__main__":
    main()

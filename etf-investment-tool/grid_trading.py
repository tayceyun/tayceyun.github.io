#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
网格交易模块
铜陵有色专用，实现动态网格交易策略
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import pandas as pd
import numpy as np

# 数据目录
DATA_DIR = Path(__file__).parent / "data"
POSITIONS_FILE = DATA_DIR / "grid_positions.json"


def ensure_data_dir():
    """确保数据目录存在"""
    DATA_DIR.mkdir(exist_ok=True)


def load_positions() -> Dict:
    """加载持仓记录"""
    ensure_data_dir()
    if POSITIONS_FILE.exists():
        with open(POSITIONS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}


def save_positions(positions: Dict):
    """保存持仓记录"""
    ensure_data_dir()
    with open(POSITIONS_FILE, 'w', encoding='utf-8') as f:
        json.dump(positions, f, ensure_ascii=False, indent=2)


def calculate_target_price(df: pd.DataFrame) -> float:
    """计算目标中枢价格（ETF模式）
    
    公式：MA20×40% + MA60×40% + 月K低点×20%
    
    Args:
        df: 日线数据 DataFrame，需包含 '收盘', '最低' 列
    
    Returns:
        目标中枢价格
    """
    if df.empty or len(df) < 60:
        return 0.0
    
    # MA20 和 MA60
    ma20 = float(df['收盘'].tail(20).mean())
    ma60 = float(df['收盘'].tail(60).mean())
    
    # 近3个月最低点（约60个交易日）
    monthly_low = float(df['最低'].tail(60).min())
    
    # 加权计算
    target_price = ma20 * 0.4 + ma60 * 0.4 + monthly_low * 0.2
    
    return round(target_price, 3)


def calculate_grid_step(df: pd.DataFrame, days: int = 20) -> float:
    """基于 ATR 计算建议网格间距
    
    Args:
        df: 日线数据
        days: 计算 ATR 的天数
    
    Returns:
        建议网格间距（百分比，如 3.5 表示 3.5%）
    """
    if df.empty or len(df) < days:
        return 3.0  # 默认 3%
    
    recent = df.tail(days)
    high = recent['最高']
    low = recent['最低']
    close = recent['收盘']
    
    # 计算 True Range
    tr1 = high - low
    tr2 = abs(high - close.shift(1))
    tr3 = abs(low - close.shift(1))
    
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    atr = tr.mean()
    
    # ATR 百分比
    current_price = float(close.iloc[-1])
    atr_pct = (atr / current_price) * 100
    
    # 建议网格间距 = ATR% × 1.5（覆盖 1.5 倍日波动）
    grid_step = round(atr_pct * 1.5, 1)
    
    # 限制在合理范围内 2% - 6%
    grid_step = max(2.0, min(6.0, grid_step))
    
    return grid_step


def calculate_buy_amount(base_amount: float, deviation_pct: float, 
                         coefficient: float = 0.5) -> float:
    """计算动态买入金额
    
    越跌买越多：买入金额 = 基础金额 × (1 + 偏离幅度 × 系数)
    
    Args:
        base_amount: 基础买入金额
        deviation_pct: 偏离中枢的百分比（负数表示低于中枢）
        coefficient: 放大系数
    
    Returns:
        实际买入金额
    """
    # 偏离越大，买入越多
    multiplier = 1 + abs(deviation_pct) * coefficient / 100
    return round(base_amount * multiplier, 2)


def get_grid_levels(center_price: float, grid_step: float, 
                    grid_count: int = 6) -> List[float]:
    """计算网格价格档位
    
    Args:
        center_price: 中枢价格
        grid_step: 网格间距（百分比）
        grid_count: 向下网格数量
    
    Returns:
        网格价格列表（从高到低）
    """
    levels = [center_price]
    for i in range(1, grid_count + 1):
        level = center_price * (1 - grid_step * i / 100)
        levels.append(round(level, 3))
    return levels


def analyze_grid_position(code: str, df: pd.DataFrame, config: Dict) -> Dict:
    """分析网格交易状态，生成次日操作计划
    
    Args:
        code: 股票代码
        df: 日线数据
        config: 股票配置（包含 available_cash, core_shares 等）
    
    Returns:
        分析结果字典
    """
    if df.empty:
        return {"error": "数据获取失败"}
    
    current_price = float(df['收盘'].iloc[-1])
    
    # 计算中枢价格和网格间距
    center_price = calculate_target_price(df)
    grid_step = calculate_grid_step(df)
    
    # 获取网格档位
    grid_levels = get_grid_levels(center_price, grid_step)
    
    # 加载历史持仓
    positions = load_positions()
    stock_positions = positions.get(code, {
        "name": config.get("name", ""),
        "center_price": center_price,
        "grid_step": grid_step,
        "positions": [],
        "available_cash": config.get("available_cash", 10000),
        "core_shares": config.get("core_shares", 0),
        "last_update": datetime.now().strftime("%Y-%m-%d")
    })
    
    # 当前偏离中枢的幅度
    deviation_pct = (current_price - center_price) / center_price * 100
    
    # 确定当前所在网格层级
    current_level = 0
    for i, level in enumerate(grid_levels):
        if current_price >= level:
            current_level = i
            break
    else:
        current_level = len(grid_levels) - 1
    
    # 生成次日操作计划
    buy_plan = None
    sell_plan = None
    
    available_cash = stock_positions.get("available_cash", 10000)
    base_amount = config.get("base_amount", 2000)
    
    # 买入计划：下一格触发价
    if current_level < len(grid_levels) - 1:
        next_buy_level = grid_levels[current_level + 1]
        buy_deviation = (next_buy_level - center_price) / center_price * 100
        buy_amount = calculate_buy_amount(base_amount, buy_deviation)
        buy_shares = int(buy_amount / next_buy_level / 100) * 100
        
        if buy_shares >= 100 and available_cash >= buy_amount:
            buy_plan = {
                "trigger_price": next_buy_level,
                "deviation_pct": round((next_buy_level - current_price) / current_price * 100, 1),
                "shares": buy_shares,
                "amount": round(buy_shares * next_buy_level, 2),
                "grid_level": current_level + 1
            }
    
    # 卖出计划：涨回上一格
    holding_positions = [p for p in stock_positions.get("positions", []) 
                         if p.get("status") == "holding"]
    
    if holding_positions and current_level > 0:
        # 找到最近一次买入的持仓
        last_buy = max(holding_positions, key=lambda x: x.get("grid_level", 0))
        if last_buy.get("grid_level", 0) > 0:
            sell_trigger = grid_levels[last_buy["grid_level"] - 1]
            if sell_trigger > current_price:
                sell_plan = {
                    "trigger_price": sell_trigger,
                    "deviation_pct": round((sell_trigger - current_price) / current_price * 100, 1),
                    "shares": last_buy.get("shares", 0),
                    "buy_price": last_buy.get("buy_price", 0),
                    "expected_profit": round((sell_trigger - last_buy.get("buy_price", 0)) 
                                            * last_buy.get("shares", 0), 2),
                    "grid_level": last_buy["grid_level"]
                }
    
    # 止盈计划：高于中枢 5% 以上
    profit_take_plan = None
    if current_price > center_price * 1.05 and holding_positions:
        total_holding = sum(p.get("shares", 0) for p in holding_positions)
        sell_shares = int(total_holding * 0.2 / 100) * 100  # 卖出 20%
        if sell_shares >= 100:
            profit_take_plan = {
                "trigger_price": round(center_price * 1.05, 3),
                "shares": sell_shares,
                "reason": "止盈(高于中枢5%)"
            }
    
    return {
        "code": code,
        "name": config.get("name", ""),
        "current_price": current_price,
        "center_price": center_price,
        "grid_step": grid_step,
        "deviation_pct": round(deviation_pct, 1),
        "current_level": current_level,
        "grid_levels": grid_levels,
        "available_cash": available_cash,
        "holding_positions": holding_positions,
        "buy_plan": buy_plan,
        "sell_plan": sell_plan,
        "profit_take_plan": profit_take_plan,
        "last_update": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }


def record_trade(code: str, trade_type: str, price: float, shares: int, 
                 grid_level: int = 0):
    """记录交易
    
    Args:
        code: 股票代码
        trade_type: 'buy' 或 'sell'
        price: 成交价格
        shares: 成交股数
        grid_level: 网格层级
    """
    positions = load_positions()
    
    if code not in positions:
        positions[code] = {
            "positions": [],
            "available_cash": 0
        }
    
    if trade_type == "buy":
        positions[code]["positions"].append({
            "grid_level": grid_level,
            "buy_price": price,
            "shares": shares,
            "buy_date": datetime.now().strftime("%Y-%m-%d"),
            "status": "holding"
        })
        positions[code]["available_cash"] -= price * shares
    
    elif trade_type == "sell":
        # 标记对应持仓为已卖出
        for pos in positions[code]["positions"]:
            if pos.get("grid_level") == grid_level and pos.get("status") == "holding":
                pos["status"] = "sold"
                pos["sell_price"] = price
                pos["sell_date"] = datetime.now().strftime("%Y-%m-%d")
                break
        positions[code]["available_cash"] += price * shares
    
    positions[code]["last_update"] = datetime.now().strftime("%Y-%m-%d")
    save_positions(positions)


def init_grid_position(code: str, name: str, available_cash: float, 
                       core_shares: int, cost: float):
    """初始化网格持仓记录
    
    Args:
        code: 股票代码
        name: 股票名称
        available_cash: 可用资金
        core_shares: 核心仓位股数
        cost: 成本价
    """
    positions = load_positions()
    
    positions[code] = {
        "name": name,
        "center_price": cost,  # 初始中枢用成本价
        "grid_step": 3.5,  # 默认
        "positions": [{
            "grid_level": 0,
            "buy_price": cost,
            "shares": core_shares,
            "buy_date": "initial",
            "status": "holding"
        }],
        "available_cash": available_cash,
        "core_shares": core_shares,
        "last_update": datetime.now().strftime("%Y-%m-%d")
    }
    
    save_positions(positions)
    print(f"已初始化 {name} ({code}) 网格持仓记录")


# 测试
if __name__ == "__main__":
    # 初始化测试数据
    init_grid_position(
        code="000630",
        name="铜陵有色",
        available_cash=15000,
        core_shares=3000,
        cost=4.25
    )
    
    print("\n网格持仓记录:")
    print(json.dumps(load_positions(), ensure_ascii=False, indent=2))



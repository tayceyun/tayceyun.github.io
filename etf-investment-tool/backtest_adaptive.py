#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自适应网格交易回测 v2.0

核心改进：
1. 走势识别优化：60天回看期，调整ADX阈值，增加均线排列确认
2. 动态底仓：根据趋势强度调整 0-50%
3. 趋势跟踪模式：强趋势时使用 MA 突破策略
4. 历史表现选择：回看3个月收益对比选择最优策略
"""

import os
import argparse
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box
from typing import Tuple, Dict, List, Optional

from data_source import get_stock_10min_baostock, get_stock_daily_baostock

console = Console()

# 本地数据目录
DATA_DIR = os.path.join(os.path.dirname(__file__), "market_data")
DAILY_DIR = os.path.join(DATA_DIR, "daily")
MIN5_DIR = os.path.join(DATA_DIR, "5min")


# ============================================================================
# 46只行业龙头股配置（更新）
# ============================================================================

STOCK_LIST = {
    # 消费行业
    "600519": "贵州茅台",
    "000858": "五粮液",
    "600887": "伊利股份",
    "603288": "海天味业",
    # 科技/半导体行业
    "688981": "中芯国际",
    "002371": "北方华创",
    "603501": "韦尔股份",
    "002230": "科大讯飞",
    "002475": "立讯精密",
    # 新能源行业
    "300750": "宁德时代",
    "002594": "比亚迪",
    "601012": "隆基绿能",
    "300274": "阳光电源",
    "600900": "长江电力",
    # 医药生物行业
    "300760": "迈瑞医疗",
    "600276": "恒瑞医药",
    "603259": "药明康德",
    "600436": "片仔癀",
    "300015": "爱尔眼科",
    # 金融行业
    "601398": "工商银行",
    "600036": "招商银行",
    "601318": "中国平安",
    "600030": "中信证券",
    "601628": "中国人寿",
    # 高端制造/军工
    "600031": "三一重工",
    "600760": "中航沈飞",
    "600893": "航发动力",
    "601138": "工业富联",
    "601766": "中国中车",
    # 人工智能/算力
    "002415": "海康威视",
    "603019": "中科曙光",
    "000938": "紫光股份",
    # 汽车行业
    "601238": "长城汽车",
    "600660": "福耀玻璃",
    "600741": "华域汽车",
    # 家电行业
    "000333": "美的集团",
    "000651": "格力电器",
    "600690": "海尔智家",
    # 资源/周期行业
    "601088": "中国神华",
    "601899": "紫金矿业",
    "601857": "中国石油",
    "600019": "宝钢股份",
    "600309": "万华化学",
    # 通信行业
    "600941": "中国移动",
    "000063": "中兴通讯",
    "300628": "亿联网络",
}


# ============================================================================
# 本地数据读取
# ============================================================================

def load_daily_data(code: str) -> pd.DataFrame:
    """从本地加载日K数据"""
    file_path = os.path.join(DAILY_DIR, f"{code}.csv")
    if os.path.exists(file_path):
        df = pd.read_csv(file_path, parse_dates=['日期'])
        return df.sort_values('日期').reset_index(drop=True)
    return pd.DataFrame()


def load_5min_data(code: str) -> pd.DataFrame:
    """从本地加载5分钟数据"""
    file_path = os.path.join(MIN5_DIR, f"{code}.csv")
    if os.path.exists(file_path):
        df = pd.read_csv(file_path, parse_dates=['日期', 'datetime'])
        return df.sort_values('datetime').reset_index(drop=True)
    return pd.DataFrame()


def get_daily_data(code: str, start_date: str = None, end_date: str = None,
                   use_local: bool = True) -> pd.DataFrame:
    """获取日K数据，优先使用本地数据"""
    if use_local:
        df = load_daily_data(code)
        if not df.empty:
            if start_date:
                df = df[df['日期'] >= pd.to_datetime(start_date)]
            if end_date:
                df = df[df['日期'] <= pd.to_datetime(end_date)]
            return df
    
    # 回退到网络获取
    days = 500 if not start_date else None
    return get_stock_daily_baostock(code, start_date, end_date, days=days or 500)


def get_minute_data(code: str, start_date: str = None, end_date: str = None,
                    use_local: bool = True) -> pd.DataFrame:
    """获取分钟数据，优先使用本地5分钟数据"""
    if use_local:
        df = load_5min_data(code)
        if not df.empty:
            if start_date:
                df = df[df['日期'] >= pd.to_datetime(start_date)]
            if end_date:
                df = df[df['日期'] <= pd.to_datetime(end_date)]
            return df
    
    # 回退到网络获取10分钟数据
    days = 35 if not start_date else None
    return get_stock_10min_baostock(code, start_date, end_date, days=days or 35)


# ============================================================================
# 走势类型识别模块 v2.0（优化版）
# ============================================================================

def calculate_trend_indicators_v2(df: pd.DataFrame, lookback: int = 60) -> Optional[Dict]:
    """
    计算走势识别所需的技术指标（优化版）
    
    改进：
    1. 延长回看期到60天
    2. 增加均线排列判断
    3. 增加价格位置判断
    
    Args:
        df: 日线数据 DataFrame
        lookback: 回看天数（默认60天）
    
    Returns:
        指标字典
    """
    if df.empty or len(df) < lookback:
        return None
    
    # 取最近 lookback 天数据
    df = df.tail(lookback).copy()
    
    close = df['收盘']
    high = df['最高']
    low = df['最低']
    
    # 1. 涨跌幅（总收益）
    price_change = (close.iloc[-1] - close.iloc[0]) / close.iloc[0] * 100
    
    # 2. 振幅（最高-最低）/ 起始价
    amplitude = (high.max() - low.min()) / close.iloc[0] * 100
    
    # 3. 振幅/涨跌幅比（震荡特征）
    if abs(price_change) > 0.1:
        volatility_ratio = amplitude / abs(price_change)
    else:
        volatility_ratio = 100  # 涨跌幅接近0，认为是高震荡
    
    # 4. ADX（趋势强度）
    adx = calculate_adx(df)
    
    # 5. 计算多条均线
    ma5 = close.rolling(window=5).mean()
    ma20 = close.rolling(window=20).mean()
    ma60 = close.rolling(window=min(60, len(close))).mean()
    
    # 6. 均线排列判断
    if len(ma60.dropna()) > 0:
        ma5_last = ma5.iloc[-1]
        ma20_last = ma20.iloc[-1]
        ma60_last = ma60.iloc[-1]
        
        # 多头排列: MA5 > MA20 > MA60
        bullish_alignment = (ma5_last > ma20_last > ma60_last)
        # 空头排列: MA5 < MA20 < MA60
        bearish_alignment = (ma5_last < ma20_last < ma60_last)
    else:
        bullish_alignment = False
        bearish_alignment = False
    
    # 7. 价格位置（相对于MA20）
    if len(ma20.dropna()) > 0:
        price_position = (close.iloc[-1] - ma20.iloc[-1]) / ma20.iloc[-1] * 100
    else:
        price_position = 0
    
    # 8. 均线斜率（5天变化）
    if len(ma20.dropna()) >= 5:
        ma_slope = (ma20.iloc[-1] - ma20.iloc[-5]) / ma20.iloc[-5] * 100
    else:
        ma_slope = 0
    
    # 9. 价格与MA20的穿越次数
    if len(ma20.dropna()) > 0:
        above_ma = close > ma20
        crossings = (above_ma != above_ma.shift(1)).sum()
    else:
        crossings = 0
    
    return {
        "price_change": price_change,
        "amplitude": amplitude,
        "volatility_ratio": volatility_ratio,
        "adx": adx,
        "ma_slope": ma_slope,
        "ma_crossings": crossings,
        "bullish_alignment": bullish_alignment,
        "bearish_alignment": bearish_alignment,
        "price_position": price_position,
        "current_price": close.iloc[-1],
        "ma5": ma5.iloc[-1] if len(ma5.dropna()) > 0 else None,
        "ma20": ma20.iloc[-1] if len(ma20.dropna()) > 0 else None,
        "ma60": ma60.iloc[-1] if len(ma60.dropna()) > 0 else None,
    }


def calculate_adx(df: pd.DataFrame, period: int = 14) -> float:
    """ADX 计算"""
    if len(df) < period * 2:
        return 15  # 默认值
    
    high = df['最高']
    low = df['最低']
    close = df['收盘']
    
    # +DM 和 -DM
    plus_dm = high.diff()
    minus_dm = -low.diff()
    
    plus_dm = plus_dm.where((plus_dm > minus_dm) & (plus_dm > 0), 0)
    minus_dm = minus_dm.where((minus_dm > plus_dm) & (minus_dm > 0), 0)
    
    # TR
    tr1 = high - low
    tr2 = abs(high - close.shift(1))
    tr3 = abs(low - close.shift(1))
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    
    # 平滑
    atr = tr.rolling(window=period).mean()
    plus_di = 100 * (plus_dm.rolling(window=period).mean() / (atr + 0.0001))
    minus_di = 100 * (minus_dm.rolling(window=period).mean() / (atr + 0.0001))
    
    # DX 和 ADX
    dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di + 0.0001)
    adx = dx.rolling(window=period).mean()
    
    return float(adx.iloc[-1]) if not pd.isna(adx.iloc[-1]) else 15


def identify_market_type_v2(indicators: Dict, lookback_days: int = 60) -> Tuple[str, str, Dict]:
    """
    识别走势类型（优化版）
    
    改进：
    1. ADX阈值调整：>25强趋势，20-25弱趋势，<20震荡
    2. 增加均线排列确认
    3. 更细致的趋势强度分级
    
    Args:
        indicators: 技术指标字典
        lookback_days: 回看天数
    
    Returns:
        (走势类型, 类型名称, 详情)
    """
    if indicators is None:
        return "unknown", "数据不足", {}
    
    scores = {
        "sideways": 0,  # 震荡得分
        "trend": 0,     # 趋势得分
    }
    reasons = []
    
    adx = indicators["adx"]
    
    # 1. ADX 判断（权重：35%）- 调整阈值
    if adx < 20:
        scores["sideways"] += 35
        reasons.append(f"ADX={adx:.1f}<20(震荡)")
    elif adx >= 20 and adx < 25:
        scores["sideways"] += 15
        scores["trend"] += 20
        reasons.append(f"ADX={adx:.1f}(弱趋势)")
    elif adx >= 25 and adx < 30:
        scores["trend"] += 35
        reasons.append(f"ADX={adx:.1f}(中等趋势)")
    else:  # adx >= 30
        scores["trend"] += 40
        reasons.append(f"ADX={adx:.1f}(强趋势)")
    
    # 2. 均线排列（权重：25%）- 新增
    if indicators["bullish_alignment"]:
        scores["trend"] += 25
        reasons.append("均线多头排列")
    elif indicators["bearish_alignment"]:
        scores["trend"] += 25
        reasons.append("均线空头排列")
    else:
        scores["sideways"] += 20
        reasons.append("均线交织")
    
    # 3. 振幅/涨跌幅比（权重：20%）
    vol_ratio = indicators["volatility_ratio"]
    if vol_ratio > 3:
        scores["sideways"] += 20
        reasons.append(f"振幅比={vol_ratio:.1f}>3")
    elif vol_ratio < 2:
        scores["trend"] += 20
        reasons.append(f"振幅比={vol_ratio:.1f}<2")
    else:
        scores["sideways"] += 10
        scores["trend"] += 10
    
    # 4. 均线斜率（权重：10%）
    ma_slope = indicators["ma_slope"]
    if abs(ma_slope) < 1:
        scores["sideways"] += 10
    elif abs(ma_slope) > 3:
        scores["trend"] += 10
        reasons.append(f"MA斜率{ma_slope:+.1f}%")
    else:
        scores["sideways"] += 5
        scores["trend"] += 5
    
    # 5. MA穿越次数（权重：10%）
    crossings = indicators["ma_crossings"]
    crossing_threshold = lookback_days * 0.25
    if crossings > crossing_threshold:
        scores["sideways"] += 10
        reasons.append(f"穿越{crossings}次(频繁)")
    elif crossings < lookback_days * 0.1:
        scores["trend"] += 10
        reasons.append(f"穿越{crossings}次(稀少)")
    
    # 判断走势类型
    if scores["sideways"] > scores["trend"]:
        market_type = "sideways"
        type_name = "震荡型"
        trend_strength = 0
    else:
        market_type = "trend"
        # 判断趋势方向和强度
        price_change = indicators["price_change"]
        
        if price_change > 0:
            direction = "up"
            if adx >= 30 and indicators["bullish_alignment"]:
                type_name = "强上涨趋势"
                trend_strength = 3
            elif adx >= 25:
                type_name = "中等上涨趋势"
                trend_strength = 2
            else:
                type_name = "弱上涨趋势"
                trend_strength = 1
        else:
            direction = "down"
            if adx >= 30 and indicators["bearish_alignment"]:
                type_name = "强下跌趋势"
                trend_strength = -3
            elif adx >= 25:
                type_name = "中等下跌趋势"
                trend_strength = -2
            else:
                type_name = "弱下跌趋势"
                trend_strength = -1
    
    return market_type, type_name, {
        "sideways_score": scores["sideways"],
        "trend_score": scores["trend"],
        "trend_strength": trend_strength if market_type == "trend" else 0,
        "reasons": reasons,
        "indicators": indicators,
        "adx": adx,
    }


# ============================================================================
# 动态底仓策略选择（优化版）
# ============================================================================

def select_strategy_v2(market_type: str, details: Dict) -> Dict:
    """
    根据走势类型和趋势强度选择策略（优化版）
    
    动态底仓比例：
    | 市场类型 | ADX范围 | 底仓比例 | 策略名称 |
    |---------|--------|---------|---------|
    | 强上涨趋势 | >30 | 50% | 激进混合 |
    | 中等上涨 | 25-30 | 35% | 标准混合 |
    | 弱上涨/震荡 | 20-25 | 20% | 保守混合 |
    | 纯震荡 | <20 | 10% | 网格为主 |
    | 下跌趋势 | >20 | 0% | 纯网格/观望 |
    
    Args:
        market_type: "sideways" 或 "trend"
        details: 走势识别详情
    
    Returns:
        策略配置
    """
    adx = details.get("adx", 15)
    trend_strength = details.get("trend_strength", 0)
    indicators = details.get("indicators", {})
    
    if market_type == "sideways":
        # 纯震荡：低底仓 + 网格
        if adx < 15:
            return {
                "name": "纯网格",
                "mode": "grid",
                "enable_base_position": False,
                "base_position_ratio": 0,
                "grid_step": 2.5,
                "description": "低波动震荡，纯网格策略"
            }
        else:
            return {
                "name": "网格为主",
                "mode": "grid",
                "enable_base_position": True,
                "base_position_ratio": 0.1,
                "grid_step": 2.5,
                "description": "震荡市，10%底仓+网格"
            }
    
    else:  # trend
        if trend_strength >= 3:  # 强上涨
            return {
                "name": "激进混合",
                "mode": "trend_following",
                "enable_base_position": True,
                "base_position_ratio": 0.5,
                "grid_step": 3.0,
                "description": "强上涨趋势，50%底仓，启用趋势跟踪"
            }
        elif trend_strength == 2:  # 中等上涨
            return {
                "name": "标准混合",
                "mode": "hybrid",
                "enable_base_position": True,
                "base_position_ratio": 0.35,
                "grid_step": 2.5,
                "description": "中等上涨，35%底仓+网格"
            }
        elif trend_strength == 1:  # 弱上涨
            return {
                "name": "保守混合",
                "mode": "hybrid",
                "enable_base_position": True,
                "base_position_ratio": 0.2,
                "grid_step": 2.5,
                "description": "弱上涨，20%底仓+网格"
            }
        elif trend_strength <= -2:  # 中强下跌
            return {
                "name": "观望",
                "mode": "grid",
                "enable_base_position": False,
                "base_position_ratio": 0,
                "grid_step": 3.5,
                "description": "下跌趋势，纯网格+宽间距"
            }
        else:  # 弱下跌
            return {
                "name": "轻仓网格",
                "mode": "grid",
                "enable_base_position": False,
                "base_position_ratio": 0,
                "grid_step": 3.0,
                "description": "弱下跌，纯网格策略"
            }


# ============================================================================
# 趋势跟踪策略
# ============================================================================

def run_trend_following_strategy(df: pd.DataFrame, initial_cash: float,
                                  base_position_ratio: float) -> Dict:
    """
    趋势跟踪策略
    
    触发条件：ADX>30 且 均线多头排列 且 价格在MA20上方
    
    策略逻辑：
    - 买入：价格回踩MA20时加仓
    - 卖出：价格跌破MA20减仓
    - 止损：价格跌破MA60清仓
    
    Args:
        df: 分钟K线数据
        initial_cash: 初始资金
        base_position_ratio: 底仓比例
    
    Returns:
        回测结果
    """
    if df.empty or len(df) < 100:
        return {"strategy_return": 0, "grid_profit": 0, "trades_count": 0, "final_value": initial_cash}
    
    start_price = float(df['收盘'].iloc[0])
    end_price = float(df['收盘'].iloc[-1])
    
    cash = initial_cash
    shares = 0
    trades = []
    
    # 计算均线（使用收盘价）
    df = df.copy()
    df['ma5'] = df['收盘'].rolling(window=5).mean()
    df['ma20'] = df['收盘'].rolling(window=20).mean()
    df['ma60'] = df['收盘'].rolling(window=60).mean()
    
    # 初始建仓（底仓）
    base_invest = initial_cash * base_position_ratio
    base_shares = int(base_invest / start_price / 100) * 100
    if base_shares >= 100:
        cash -= base_shares * start_price
        shares += base_shares
        trades.append({"type": "base_buy", "price": start_price, "shares": base_shares})
    
    # 剩余资金用于趋势加仓
    add_position_cash = initial_cash * 0.3  # 预留30%用于加仓
    position_added = False
    
    for idx in range(60, len(df)):
        row = df.iloc[idx]
        current_price = float(row['收盘'])
        ma20 = float(row['ma20']) if pd.notna(row['ma20']) else current_price
        ma60 = float(row['ma60']) if pd.notna(row['ma60']) else current_price
        
        # 买入：价格回踩MA20附近（在MA20上下2%内）且未加仓
        if not position_added and shares > 0:
            if abs(current_price - ma20) / ma20 < 0.02 and current_price > ma60:
                add_shares = int(add_position_cash / current_price / 100) * 100
                if add_shares >= 100 and cash >= add_shares * current_price:
                    cash -= add_shares * current_price
                    shares += add_shares
                    position_added = True
                    trades.append({"type": "trend_add", "price": current_price, "shares": add_shares})
        
        # 卖出：价格跌破MA60 止损
        if shares > 0 and current_price < ma60 * 0.98:
            # 清仓止损
            cash += shares * current_price
            trades.append({"type": "stop_loss", "price": current_price, "shares": shares})
            shares = 0
            break
    
    # 计算结果
    final_value = cash + shares * end_price
    strategy_return = (final_value - initial_cash) / initial_cash * 100
    
    return {
        "strategy_return": strategy_return,
        "grid_profit": 0,
        "trades_count": len(trades),
        "final_value": final_value,
    }


# ============================================================================
# 网格策略
# ============================================================================

def run_grid_strategy(df: pd.DataFrame, initial_cash: float, base_amount: float,
                      grid_step: float, enable_base_position: bool,
                      base_position_ratio: float) -> Dict:
    """执行网格策略"""
    if df.empty or len(df) < 10:
        return {"strategy_return": 0, "grid_profit": 0, "trades_count": 0, "final_value": initial_cash}
    
    start_price = float(df['收盘'].iloc[0])
    end_price = float(df['收盘'].iloc[-1])
    
    cash = initial_cash
    shares = 0
    trades = []
    grid_positions = []
    
    # 底仓
    if enable_base_position:
        base_invest = initial_cash * base_position_ratio
        base_shares = int(base_invest / start_price / 100) * 100
        if base_shares >= 100:
            cash -= base_shares * start_price
            shares += base_shares
    
    # 中枢价格
    center_price = start_price
    
    # 网格档位
    grid_levels = {}
    grid_levels[0] = center_price
    for i in range(1, 7):
        grid_levels[i] = center_price * (1 - grid_step * i / 100)
    for i in range(-1, -3, -1):
        grid_levels[i] = center_price * (1 - grid_step * i / 100)
    
    triggered_levels = set()
    
    for idx in range(len(df)):
        row = df.iloc[idx]
        current_price = float(row['收盘'])
        current_high = float(row['最高'])
        current_low = float(row['最低'])
        
        # 买入逻辑
        for level_idx in range(1, 7):
            trigger_price = grid_levels[level_idx]
            existing = [p for p in grid_positions if p["grid_level"] == level_idx and p["status"] == "holding"]
            if existing:
                continue
            
            if current_low <= trigger_price and level_idx not in triggered_levels:
                deviation = abs((trigger_price - center_price) / center_price * 100)
                buy_amount = base_amount * (1 + deviation * 0.15)
                trade_shares = int(buy_amount / trigger_price / 100) * 100
                
                if trade_shares >= 100 and cash >= trade_shares * trigger_price:
                    cash -= trade_shares * trigger_price
                    shares += trade_shares
                    triggered_levels.add(level_idx)
                    grid_positions.append({
                        "grid_level": level_idx,
                        "buy_price": trigger_price,
                        "shares": trade_shares,
                        "status": "holding"
                    })
                    trades.append("buy")
                    break
        
        # 卖出逻辑
        for pos in grid_positions:
            if pos["status"] != "holding":
                continue
            
            level_idx = pos["grid_level"]
            sell_level = level_idx - 1
            
            if sell_level in grid_levels:
                sell_trigger = grid_levels[sell_level]
                if current_high >= sell_trigger:
                    trade_shares = pos["shares"]
                    cash += trade_shares * sell_trigger
                    shares -= trade_shares
                    pos["status"] = "sold"
                    pos["profit"] = (sell_trigger - pos["buy_price"]) * trade_shares
                    if level_idx in triggered_levels:
                        triggered_levels.remove(level_idx)
                    trades.append("sell")
                    break
    
    # 计算结果
    final_value = cash + shares * end_price
    strategy_return = (final_value - initial_cash) / initial_cash * 100
    grid_profit = sum(p.get("profit", 0) for p in grid_positions if p["status"] == "sold")
    
    return {
        "strategy_return": strategy_return,
        "grid_profit": grid_profit,
        "trades_count": len(trades),
        "final_value": final_value,
    }


# ============================================================================
# 历史表现策略选择
# ============================================================================

def evaluate_historical_performance(code: str, end_date: str,
                                     lookback_months: int = 3) -> Dict:
    """
    基于历史表现选择策略
    
    回看过去3个月各策略模拟收益，选择历史胜率更高的策略
    
    Args:
        code: 股票代码
        end_date: 结束日期
        lookback_months: 回看月数
    
    Returns:
        各策略历史表现及推荐策略
    """
    end_dt = datetime.strptime(end_date, "%Y-%m-%d")
    
    results = {
        "grid": [],      # 纯网格
        "hybrid": [],    # 混合策略
        "trend": [],     # 趋势跟踪
    }
    
    for i in range(lookback_months):
        # 计算该月的日期范围
        month_end = end_dt - timedelta(days=30 * i)
        month_start = month_end - timedelta(days=30)
        
        start_str = month_start.strftime("%Y-%m-%d")
        end_str = month_end.strftime("%Y-%m-%d")
        
        # 获取数据
        df = get_minute_data(code, start_str, end_str)
        if df.empty or len(df) < 50:
            continue
        
        # 计算持有收益
        start_price = float(df['收盘'].iloc[0])
        end_price = float(df['收盘'].iloc[-1])
        hold_return = (end_price - start_price) / start_price * 100
        
        # 模拟各策略
        grid_result = run_grid_strategy(df, 100000, 2000, 2.5, False, 0)
        hybrid_result = run_grid_strategy(df, 100000, 2000, 2.5, True, 0.3)
        trend_result = run_trend_following_strategy(df, 100000, 0.4)
        
        results["grid"].append(grid_result["strategy_return"] - hold_return)
        results["hybrid"].append(hybrid_result["strategy_return"] - hold_return)
        results["trend"].append(trend_result["strategy_return"] - hold_return)
    
    # 计算平均超额收益
    avg_results = {}
    for strategy, returns in results.items():
        if returns:
            avg_results[strategy] = sum(returns) / len(returns)
        else:
            avg_results[strategy] = 0
    
    # 选择最佳策略
    best_strategy = max(avg_results, key=avg_results.get)
    
    return {
        "avg_excess_returns": avg_results,
        "best_strategy": best_strategy,
        "details": results
    }


# ============================================================================
# 自适应回测核心 v2.0
# ============================================================================

def run_adaptive_backtest_v2(code: str, year: int, month: int,
                              initial_cash: float = 100000,
                              base_amount: float = 2000,
                              lookback_days: int = 60,
                              use_historical_selection: bool = False) -> Dict:
    """
    自适应策略回测 v2.0
    
    流程：
    1. 获取60天回看期数据，识别走势类型
    2. 根据走势类型和趋势强度动态选择策略
    3. （可选）参考历史表现调整策略
    4. 执行回测
    """
    # 计算日期范围
    start_date = f"{year}-{month:02d}-01"
    if month == 12:
        end_date = f"{year + 1}-01-01"
    else:
        end_date = f"{year}-{month + 1:02d}-01"
    
    end_dt = datetime.strptime(end_date, "%Y-%m-%d") - timedelta(days=1)
    end_date = end_dt.strftime("%Y-%m-%d")
    
    if datetime.strptime(start_date, "%Y-%m-%d") > datetime.now():
        return None
    
    if end_dt > datetime.now():
        end_date = datetime.now().strftime("%Y-%m-%d")
    
    # 获取回看期日线数据（用于识别走势）
    lookback_start = (datetime.strptime(start_date, "%Y-%m-%d") - timedelta(days=lookback_days + 10)).strftime("%Y-%m-%d")
    daily_df = get_daily_data(code, lookback_start, start_date)
    
    if daily_df.empty or len(daily_df) < lookback_days // 2:
        return {"status": "数据不足", "year": year, "month": month}
    
    # 识别走势类型（使用优化版）
    indicators = calculate_trend_indicators_v2(daily_df, lookback=lookback_days)
    market_type, type_name, details = identify_market_type_v2(indicators, lookback_days)
    
    # 选择策略（使用优化版）
    strategy = select_strategy_v2(market_type, details)
    
    # （可选）历史表现调整
    if use_historical_selection:
        hist_perf = evaluate_historical_performance(code, start_date)
        # 如果历史表现明显更好，可以覆盖策略选择
        # 这里简化处理，仅记录
        strategy["historical_best"] = hist_perf.get("best_strategy")
    
    # 获取分钟数据
    df = get_minute_data(code, start_date, end_date)
    
    if df.empty or len(df) < 50:
        return {"status": "数据不足", "year": year, "month": month, "market_type": type_name}
    
    # 根据策略模式执行回测
    if strategy["mode"] == "trend_following":
        result = run_trend_following_strategy(
            df=df,
            initial_cash=initial_cash,
            base_position_ratio=strategy["base_position_ratio"]
        )
    else:
        result = run_grid_strategy(
            df=df,
            initial_cash=initial_cash,
            base_amount=base_amount,
            grid_step=strategy["grid_step"],
            enable_base_position=strategy["enable_base_position"],
            base_position_ratio=strategy["base_position_ratio"]
        )
    
    # 计算持有收益
    start_price = float(df['收盘'].iloc[0])
    end_price = float(df['收盘'].iloc[-1])
    hold_return = (end_price - start_price) / start_price * 100
    
    return {
        "status": "完成",
        "year": year,
        "month": month,
        "code": code,
        "market_type": market_type,
        "market_type_name": type_name,
        "trend_strength": details.get("trend_strength", 0),
        "adx": details.get("adx", 0),
        "strategy_name": strategy["name"],
        "strategy_mode": strategy["mode"],
        "base_position_ratio": strategy["base_position_ratio"],
        "strategy_description": strategy["description"],
        "start_price": start_price,
        "end_price": end_price,
        "hold_return": hold_return,
        "strategy_return": result["strategy_return"],
        "excess_return": result["strategy_return"] - hold_return,
        "grid_profit": result["grid_profit"],
        "trades_count": result["trades_count"],
        "details": details,
    }


# ============================================================================
# 固定策略回测（用于对比）
# ============================================================================

def run_fixed_strategy_backtest(code: str, year: int, month: int,
                                 strategy_type: str,
                                 initial_cash: float = 100000,
                                 base_amount: float = 2000) -> Dict:
    """固定策略回测（纯网格或混合策略）"""
    start_date = f"{year}-{month:02d}-01"
    if month == 12:
        end_date = f"{year + 1}-01-01"
    else:
        end_date = f"{year}-{month + 1:02d}-01"
    
    end_dt = datetime.strptime(end_date, "%Y-%m-%d") - timedelta(days=1)
    end_date = end_dt.strftime("%Y-%m-%d")
    
    if datetime.strptime(start_date, "%Y-%m-%d") > datetime.now():
        return None
    
    if end_dt > datetime.now():
        end_date = datetime.now().strftime("%Y-%m-%d")
    
    df = get_minute_data(code, start_date, end_date)
    
    if df.empty or len(df) < 50:
        return {"status": "数据不足"}
    
    if strategy_type == "grid":
        result = run_grid_strategy(df, initial_cash, base_amount, 2.5, False, 0)
    elif strategy_type == "trend":
        result = run_trend_following_strategy(df, initial_cash, 0.4)
    else:  # hybrid
        result = run_grid_strategy(df, initial_cash, base_amount, 2.5, True, 0.3)
    
    start_price = float(df['收盘'].iloc[0])
    end_price = float(df['收盘'].iloc[-1])
    hold_return = (end_price - start_price) / start_price * 100
    
    return {
        "status": "完成",
        "strategy_return": result["strategy_return"],
        "excess_return": result["strategy_return"] - hold_return,
        "hold_return": hold_return,
    }


# ============================================================================
# 批量回测
# ============================================================================

def run_batch_backtest(year: int = 2025, stocks: Dict = None,
                       use_v2: bool = True):
    """对多只股票进行批量回测"""
    if stocks is None:
        stocks = STOCK_LIST
    
    version = "v2.0" if use_v2 else "v1.0"
    lookback = 60 if use_v2 else 20
    
    console.print()
    console.print(Panel.fit(
        f"[bold cyan]📊 {year}年 自适应策略批量回测 ({version})[/bold cyan]\n"
        f"[dim]回看期: {lookback}天 | 动态底仓 | 趋势跟踪[/dim]\n"
        f"[dim]共{len(stocks)}只股票[/dim]",
        border_style="cyan"
    ))
    
    all_results = []
    
    for code, name in stocks.items():
        console.print(f"\n[bold]回测 {name}({code})[/bold]")
        
        yearly_adaptive = []
        yearly_grid = []
        yearly_hybrid = []
        
        for month in range(1, 13):
            # 自适应策略
            if use_v2:
                adaptive = run_adaptive_backtest_v2(code, year, month, lookback_days=lookback)
            else:
                adaptive = run_adaptive_backtest_v2(code, year, month, lookback_days=20)
            
            if adaptive is None or adaptive.get("status") == "数据不足":
                continue
            
            # 纯网格
            grid = run_fixed_strategy_backtest(code, year, month, "grid")
            
            # 混合策略
            hybrid = run_fixed_strategy_backtest(code, year, month, "hybrid")
            
            if grid and grid.get("status") == "完成":
                yearly_adaptive.append(adaptive)
                yearly_grid.append(grid)
                yearly_hybrid.append(hybrid)
                
                # 输出详情
                market_type = adaptive.get("market_type_name", "未知")[:4]
                strategy = adaptive.get("strategy_name", "未知")[:4]
                adx = adaptive.get("adx", 0)
                base_ratio = adaptive.get("base_position_ratio", 0) * 100
                excess = adaptive.get("excess_return", 0)
                
                color = "green" if excess > 0 else "red"
                best_mark = ""
                if excess > grid.get("excess_return", 0) and excess > hybrid.get("excess_return", 0):
                    best_mark = " [green]✓[/green]"
                
                console.print(
                    f"  {month:2d}月: {market_type} ADX={adx:.0f} → {strategy}({base_ratio:.0f}%) "
                    f"| [{color}]超额:{excess:+.1f}%[/]{best_mark}"
                )
        
        if yearly_adaptive:
            # 汇总该股票结果
            total_adaptive = sum(r.get("excess_return", 0) for r in yearly_adaptive)
            total_grid = sum(r.get("excess_return", 0) for r in yearly_grid)
            total_hybrid = sum(r.get("excess_return", 0) for r in yearly_hybrid)
            
            # 统计走势类型分布
            sideways_count = sum(1 for r in yearly_adaptive if r.get("market_type") == "sideways")
            trend_count = len(yearly_adaptive) - sideways_count
            
            # 趋势跟踪使用次数
            trend_following_count = sum(1 for r in yearly_adaptive if r.get("strategy_mode") == "trend_following")
            
            all_results.append({
                "code": code,
                "name": name,
                "months": len(yearly_adaptive),
                "sideways_months": sideways_count,
                "trend_months": trend_count,
                "trend_following_used": trend_following_count,
                "adaptive_excess": total_adaptive,
                "grid_excess": total_grid,
                "hybrid_excess": total_hybrid,
                "adaptive_wins": total_adaptive > max(total_grid, total_hybrid),
            })
    
    # 输出汇总表格
    if all_results:
        print_summary_table(all_results, year, version)
    
    return all_results


def print_summary_table(results: List[Dict], year: int, version: str = "v2.0"):
    """打印汇总表格"""
    console.print()
    table = Table(title=f"[bold]{year}年 自适应策略 {version} 汇总[/bold]", box=box.ROUNDED)
    table.add_column("股票", style="cyan")
    table.add_column("走势分布", justify="center")
    table.add_column("趋势跟踪", justify="center")
    table.add_column("自适应超额", justify="right")
    table.add_column("纯网格超额", justify="right")
    table.add_column("混合超额", justify="right")
    table.add_column("最佳策略", justify="center")
    
    adaptive_wins = 0
    grid_wins = 0
    hybrid_wins = 0
    
    for r in results:
        # 走势分布
        trend_dist = f"震{r['sideways_months']}趋{r['trend_months']}"
        trend_follow = f"{r.get('trend_following_used', 0)}次"
        
        # 找最佳
        strategies = [
            ("自适应", r["adaptive_excess"]),
            ("纯网格", r["grid_excess"]),
            ("混合", r["hybrid_excess"])
        ]
        best_name, best_val = max(strategies, key=lambda x: x[1])
        
        if best_name == "自适应":
            adaptive_wins += 1
            best_color = "green"
        elif best_name == "纯网格":
            grid_wins += 1
            best_color = "yellow"
        else:
            hybrid_wins += 1
            best_color = "cyan"
        
        adaptive_color = "green" if r["adaptive_excess"] >= 0 else "red"
        grid_color = "green" if r["grid_excess"] >= 0 else "red"
        hybrid_color = "green" if r["hybrid_excess"] >= 0 else "red"
        
        table.add_row(
            f"{r['name']}",
            trend_dist,
            trend_follow,
            f"[{adaptive_color}]{r['adaptive_excess']:+.1f}%[/]",
            f"[{grid_color}]{r['grid_excess']:+.1f}%[/]",
            f"[{hybrid_color}]{r['hybrid_excess']:+.1f}%[/]",
            f"[bold {best_color}]{best_name}[/]"
        )
    
    console.print(table)
    
    # 统计摘要
    total_adaptive = sum(r["adaptive_excess"] for r in results)
    total_grid = sum(r["grid_excess"] for r in results)
    total_hybrid = sum(r["hybrid_excess"] for r in results)
    
    console.print()
    summary = Table(title="[bold]策略胜出统计[/bold]", box=box.ROUNDED)
    summary.add_column("策略", style="cyan")
    summary.add_column("胜出股票数", justify="center")
    summary.add_column("累计超额收益", justify="right")
    summary.add_column("平均超额收益", justify="right")
    
    summary.add_row(
        "[bold green]自适应策略 v2.0[/bold green]",
        f"{adaptive_wins}/{len(results)}",
        f"{total_adaptive:+.1f}%",
        f"{total_adaptive/len(results):+.2f}%"
    )
    summary.add_row(
        "纯网格策略",
        f"{grid_wins}/{len(results)}",
        f"{total_grid:+.1f}%",
        f"{total_grid/len(results):+.2f}%"
    )
    summary.add_row(
        "混合策略(30%底仓)",
        f"{hybrid_wins}/{len(results)}",
        f"{total_hybrid:+.1f}%",
        f"{total_hybrid/len(results):+.2f}%"
    )
    
    console.print(summary)
    
    # 最终评价
    best_total = max([
        ("自适应策略 v2.0", total_adaptive),
        ("纯网格策略", total_grid),
        ("混合策略", total_hybrid)
    ], key=lambda x: x[1])
    
    improvement = total_adaptive - max(total_grid, total_hybrid)
    
    console.print(Panel(
        f"[bold green]🏆 {best_total[0]} 整体表现最佳[/bold green]\n\n"
        f"自适应策略累计超额: {total_adaptive:+.1f}%\n"
        f"纯网格策略累计超额: {total_grid:+.1f}%\n"
        f"混合策略累计超额: {total_hybrid:+.1f}%\n\n"
        f"自适应策略胜出: {adaptive_wins}/{len(results)} 只股票\n"
        f"相比固定策略提升: {improvement:+.1f}%",
        title="[bold]最终结论[/bold]",
        border_style="green" if best_total[0].startswith("自适应") else "yellow",
    ))


def main():
    parser = argparse.ArgumentParser(description="自适应网格策略回测 v2.0")
    parser.add_argument("--year", "-y", type=int, default=2025, help="回测年份")
    parser.add_argument("--code", "-c", help="单只股票代码（不指定则批量回测）")
    parser.add_argument("--lookback", "-l", type=int, default=60, help="走势识别回看天数（默认60）")
    parser.add_argument("--v1", action="store_true", help="使用v1.0版本（20天回看期）")
    parser.add_argument("--historical", action="store_true", help="启用历史表现策略选择")
    
    args = parser.parse_args()
    
    use_v2 = not args.v1
    lookback = args.lookback if use_v2 else 20
    
    if args.code:
        # 单只股票回测
        name = STOCK_LIST.get(args.code, args.code)
        version = "v2.0" if use_v2 else "v1.0"
        console.print(f"\n[bold]回测 {name}({args.code}) {args.year}年 ({version})[/bold]")
        console.print(f"[dim]回看期: {lookback}天 | 历史选择: {'启用' if args.historical else '禁用'}[/dim]\n")
        
        for month in range(1, 13):
            result = run_adaptive_backtest_v2(
                args.code, args.year, month,
                lookback_days=lookback,
                use_historical_selection=args.historical
            )
            if result and result.get("status") == "完成":
                adx = result.get("adx", 0)
                base_ratio = result.get("base_position_ratio", 0) * 100
                console.print(
                    f"  {month:2d}月: {result['market_type_name']} (ADX={adx:.0f}) → "
                    f"{result['strategy_name']}({base_ratio:.0f}%) | "
                    f"超额:{result['excess_return']:+.2f}%"
                )
    else:
        # 批量回测
        run_batch_backtest(year=args.year, use_v2=use_v2)
    
    console.print()


if __name__ == "__main__":
    main()

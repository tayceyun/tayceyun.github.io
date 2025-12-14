#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能网格交易回测
改进点：
1. 趋势识别 + 策略切换
2. 动态中枢跟随
3. 自适应网格间距（ATR）
4. 风控机制（持仓限制、止损）
"""

import argparse
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box

from data_source import get_stock_10min_baostock, get_stock_daily_baostock

console = Console()


# ============================================================================
# 技术指标计算
# ============================================================================

def calculate_atr(df: pd.DataFrame, period: int = 14) -> pd.Series:
    """计算 ATR（平均真实波幅）"""
    high = df['最高']
    low = df['最低']
    close = df['收盘']
    
    tr1 = high - low
    tr2 = abs(high - close.shift(1))
    tr3 = abs(low - close.shift(1))
    
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    atr = tr.rolling(window=period).mean()
    
    return atr


def calculate_adx(df: pd.DataFrame, period: int = 14) -> pd.Series:
    """计算 ADX（趋势强度指标）"""
    high = df['最高']
    low = df['最低']
    close = df['收盘']
    
    # +DM 和 -DM
    plus_dm = high.diff()
    minus_dm = -low.diff()
    
    plus_dm = plus_dm.where((plus_dm > minus_dm) & (plus_dm > 0), 0)
    minus_dm = minus_dm.where((minus_dm > plus_dm) & (minus_dm > 0), 0)
    
    # ATR
    tr1 = high - low
    tr2 = abs(high - close.shift(1))
    tr3 = abs(low - close.shift(1))
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    
    # 平滑
    atr_smooth = tr.rolling(window=period).mean()
    plus_di = 100 * (plus_dm.rolling(window=period).mean() / atr_smooth)
    minus_di = 100 * (minus_dm.rolling(window=period).mean() / atr_smooth)
    
    # DX 和 ADX
    dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di + 0.0001)
    adx = dx.rolling(window=period).mean()
    
    return adx, plus_di, minus_di


def calculate_ma_slope(df: pd.DataFrame, period: int = 20, lookback: int = 5) -> pd.Series:
    """计算均线斜率（用于判断趋势方向）"""
    ma = df['收盘'].rolling(window=period).mean()
    slope = (ma - ma.shift(lookback)) / ma.shift(lookback) * 100
    return slope


def calculate_rsi(df: pd.DataFrame, period: int = 14) -> pd.Series:
    """计算 RSI"""
    delta = df['收盘'].diff()
    gain = delta.where(delta > 0, 0).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / (loss + 0.0001)
    rsi = 100 - (100 / (1 + rs))
    return rsi


# ============================================================================
# 趋势识别
# ============================================================================

def identify_trend(adx: float, ma_slope: float, plus_di: float, minus_di: float) -> str:
    """
    识别当前趋势类型
    
    Returns:
        "uptrend": 上涨趋势
        "downtrend": 下跌趋势  
        "sideways": 震荡行情
    """
    # ADX < 20: 无明显趋势（震荡）
    # ADX >= 25: 有趋势
    
    if pd.isna(adx) or pd.isna(ma_slope):
        return "sideways"
    
    if adx < 20:
        return "sideways"
    elif adx >= 25:
        if ma_slope > 0.5 and plus_di > minus_di:
            return "uptrend"
        elif ma_slope < -0.5 and minus_di > plus_di:
            return "downtrend"
        else:
            return "sideways"
    else:  # ADX 20-25: 弱趋势
        if ma_slope > 1.0:
            return "uptrend"
        elif ma_slope < -1.0:
            return "downtrend"
        else:
            return "sideways"


# ============================================================================
# 智能网格策略
# ============================================================================

def run_smart_grid_backtest(code: str, year: int, month: int,
                             initial_cash: float = 100000,
                             base_grid_step: float = 2.5,
                             base_amount: float = 2000,
                             max_position_ratio: float = 0.5,
                             enable_dynamic_center: bool = True,
                             enable_trend_filter: bool = True,
                             enable_adaptive_grid: bool = True,
                             enable_base_position: bool = False,
                             base_position_ratio: float = 0.3,
                             verbose: bool = False) -> dict:
    """
    智能网格回测
    
    Args:
        code: 股票代码
        year: 年份
        month: 月份
        initial_cash: 初始资金
        base_grid_step: 基础网格间距（%）
        base_amount: 基础买入金额
        max_position_ratio: 最大持仓比例
        enable_dynamic_center: 启用动态中枢
        enable_trend_filter: 启用趋势过滤
        enable_adaptive_grid: 启用自适应网格间距
        verbose: 详细输出
    
    Returns:
        回测结果
    """
    # 计算月份起止日期
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
    
    # 获取10分钟数据
    df = get_stock_10min_baostock(code, start_date, end_date, days=35)
    
    if df.empty or len(df) < 50:
        return {"status": "数据不足", "year": year, "month": month}
    
    # 计算技术指标
    df['atr'] = calculate_atr(df, period=14)
    df['adx'], df['plus_di'], df['minus_di'] = calculate_adx(df, period=14)
    df['ma_slope'] = calculate_ma_slope(df, period=20, lookback=5)
    df['rsi'] = calculate_rsi(df, period=14)
    df['ma20'] = df['收盘'].rolling(window=20).mean()
    
    # 初始化
    start_price = float(df['收盘'].iloc[0])
    end_price = float(df['收盘'].iloc[-1])
    
    cash = initial_cash
    shares = 0
    trades = []
    grid_positions = []
    base_shares = 0  # 底仓股数
    
    # 底仓模式：期初买入一定比例作为底仓（不参与网格交易）
    if enable_base_position:
        base_invest = initial_cash * base_position_ratio
        base_shares = int(base_invest / start_price / 100) * 100
        if base_shares >= 100:
            cash -= base_shares * start_price
            shares += base_shares
            trades.append({
                "time": str(df.iloc[0]['datetime']),
                "action": "底仓",
                "price": start_price,
                "shares": base_shares,
                "reason": f"期初建仓{base_position_ratio*100:.0f}%",
                "trend": "-",
                "center": start_price,
                "grid_step": 0
            })
    
    # 动态中枢（初始为期初价格）
    center_price = start_price
    last_center_update = start_price
    
    # 统计
    trend_stats = {"uptrend": 0, "downtrend": 0, "sideways": 0}
    skipped_by_trend = 0
    
    for idx in range(50, len(df)):  # 需要足够数据计算指标
        row = df.iloc[idx]
        current_price = float(row['收盘'])
        current_high = float(row['最高'])
        current_low = float(row['最低'])
        current_time = row['datetime']
        
        # 获取技术指标
        atr = float(row['atr']) if not pd.isna(row['atr']) else current_price * 0.02
        adx = float(row['adx']) if not pd.isna(row['adx']) else 15
        plus_di = float(row['plus_di']) if not pd.isna(row['plus_di']) else 25
        minus_di = float(row['minus_di']) if not pd.isna(row['minus_di']) else 25
        ma_slope = float(row['ma_slope']) if not pd.isna(row['ma_slope']) else 0
        rsi = float(row['rsi']) if not pd.isna(row['rsi']) else 50
        
        # ========== 1. 趋势识别 ==========
        trend = identify_trend(adx, ma_slope, plus_di, minus_di)
        trend_stats[trend] += 1
        
        # ========== 2. 动态中枢更新 ==========
        if enable_dynamic_center:
            price_change_from_center = (current_price - last_center_update) / last_center_update * 100
            
            if trend == "uptrend" and price_change_from_center > 5:
                # 上涨趋势，价格涨5%以上，中枢上移3%
                center_price = center_price * 1.03
                last_center_update = current_price
            elif trend == "downtrend" and price_change_from_center < -5:
                # 下跌趋势，价格跌5%以上，中枢下移3%
                center_price = center_price * 0.97
                last_center_update = current_price
        
        # ========== 3. 自适应网格间距 ==========
        if enable_adaptive_grid:
            atr_pct = (atr / current_price) * 100
            grid_step = max(1.5, min(4.0, atr_pct * 1.5))
        else:
            grid_step = base_grid_step
        
        # ========== 4. 计算当前网格档位 ==========
        grid_levels = {}
        grid_levels[0] = center_price
        for i in range(1, 7):
            grid_levels[i] = center_price * (1 - grid_step * i / 100)
        for i in range(-1, -3, -1):
            grid_levels[i] = center_price * (1 - grid_step * i / 100)
        
        action = None
        trade_shares = 0
        trade_price = 0
        reason = ""
        
        # ========== 5. 买入逻辑（带趋势过滤） ==========
        for level_idx in range(1, 7):
            trigger_price = grid_levels[level_idx]
            
            # 检查是否已在该格有持仓
            existing = [p for p in grid_positions if p["grid_level"] == level_idx and p["status"] == "holding"]
            if existing:
                continue
            
            if current_low <= trigger_price:
                # 趋势过滤
                if enable_trend_filter:
                    if trend == "downtrend" and level_idx <= 2:
                        # 下跌趋势中，前两格不买（等更低价）
                        skipped_by_trend += 1
                        continue
                    if trend == "uptrend" and level_idx >= 4:
                        # 上涨趋势中，深度网格不买（可能是假跌）
                        skipped_by_trend += 1
                        continue
                
                # 风控：检查持仓比例
                current_position_value = shares * current_price
                if current_position_value >= initial_cash * max_position_ratio:
                    continue
                
                # 计算买入金额（RSI越低买越多）
                rsi_factor = 1.0 + (50 - min(rsi, 50)) / 100  # RSI30 -> 1.2倍
                deviation = abs((trigger_price - center_price) / center_price * 100)
                buy_amount = base_amount * (1 + deviation * 0.15) * rsi_factor
                
                trade_shares = int(buy_amount / trigger_price / 100) * 100
                
                if trade_shares >= 100 and cash >= trade_shares * trigger_price:
                    action = "买入"
                    trade_price = trigger_price
                    reason = f"格{level_idx} ({trend[:3]})"
                    cash -= trade_shares * trade_price
                    shares += trade_shares
                    
                    grid_positions.append({
                        "grid_level": level_idx,
                        "buy_price": trade_price,
                        "shares": trade_shares,
                        "buy_time": str(current_time),
                        "trend": trend,
                        "center": center_price,
                        "status": "holding"
                    })
                    break
        
        # ========== 6. 卖出逻辑 ==========
        if not action:
            for pos in grid_positions:
                if pos["status"] != "holding":
                    continue
                
                level_idx = pos["grid_level"]
                buy_center = pos.get("center", center_price)
                
                # 使用买入时的中枢计算卖出触发价
                sell_level = level_idx - 1
                if sell_level >= 0:
                    sell_trigger = buy_center * (1 - grid_step * sell_level / 100)
                else:
                    sell_trigger = buy_center * (1 - grid_step * sell_level / 100)
                
                if current_high >= sell_trigger:
                    trade_shares = pos["shares"]
                    trade_price = sell_trigger
                    profit = (trade_price - pos["buy_price"]) * trade_shares
                    profit_pct = (trade_price - pos["buy_price"]) / pos["buy_price"] * 100
                    
                    action = "卖出"
                    reason = f"格{sell_level} +{profit:.0f}"
                    cash += trade_shares * trade_price
                    shares -= trade_shares
                    
                    pos["status"] = "sold"
                    pos["sell_price"] = trade_price
                    pos["profit"] = profit
                    pos["profit_pct"] = profit_pct
                    break
        
        # ========== 7. 趋势止损 ==========
        if enable_trend_filter and trend == "downtrend" and shares > 0:
            # 下跌趋势 + RSI > 70（超买反弹后）：减仓
            if rsi > 70:
                for pos in grid_positions:
                    if pos["status"] == "holding":
                        trade_shares = pos["shares"]
                        trade_price = current_price
                        profit = (trade_price - pos["buy_price"]) * trade_shares
                        
                        action = "止损"
                        reason = f"趋势止损 {profit:+.0f}"
                        cash += trade_shares * trade_price
                        shares -= trade_shares
                        
                        pos["status"] = "stopped"
                        pos["sell_price"] = trade_price
                        pos["profit"] = profit
                        break
        
        if action:
            trades.append({
                "time": str(current_time),
                "action": action,
                "price": trade_price,
                "shares": trade_shares,
                "reason": reason,
                "trend": trend,
                "center": round(center_price, 2),
                "grid_step": round(grid_step, 2)
            })
    
    # 计算结果
    final_value = cash + shares * end_price
    total_return = (final_value - initial_cash) / initial_cash * 100
    hold_return = (end_price - start_price) / start_price * 100
    excess_return = total_return - hold_return
    
    completed_grids = [p for p in grid_positions if p["status"] == "sold"]
    holding_grids = [p for p in grid_positions if p["status"] == "holding"]
    stopped_grids = [p for p in grid_positions if p["status"] == "stopped"]
    
    grid_profit = sum(p.get("profit", 0) for p in completed_grids)
    stop_loss = sum(p.get("profit", 0) for p in stopped_grids)
    holding_pnl = sum((end_price - p["buy_price"]) * p["shares"] for p in holding_grids)
    
    return {
        "year": year,
        "month": month,
        "status": "完成",
        "data_count": len(df),
        "start_price": start_price,
        "end_price": end_price,
        "strategy_return": total_return,
        "hold_return": hold_return,
        "excess_return": excess_return,
        "grid_profit": grid_profit,
        "stop_loss": stop_loss,
        "holding_pnl": holding_pnl,
        "completed_grids": len(completed_grids),
        "holding_grids": len(holding_grids),
        "stopped_grids": len(stopped_grids),
        "trades": trades,
        "trend_stats": trend_stats,
        "skipped_by_trend": skipped_by_trend,
        "final_shares": shares,
        "final_cash": cash,
        "final_value": final_value,
    }


def run_comparison_backtest(code: str, year: int = 2025,
                            initial_cash: float = 100000,
                            base_grid_step: float = 2.5,
                            base_amount: float = 2000):
    """
    对比回测：普通网格 vs 智能网格 vs 混合策略（底仓+网格）
    """
    console.print()
    console.print(Panel.fit(
        f"[bold cyan]📊 {year}年 三种策略对比回测[/bold cyan]\n"
        f"[bold]股票代码: {code}[/bold]\n"
        f"[dim]普通网格 | 智能网格 | 混合策略（30%底仓+网格）[/dim]",
        border_style="cyan"
    ))
    
    smart_results = []
    basic_results = []
    hybrid_results = []
    
    for month in range(1, 13):
        console.print(f"[dim]回测 {year}年{month}月...[/dim]", end=" ")
        
        # 普通网格（关闭所有智能功能）
        basic = run_smart_grid_backtest(
            code=code, year=year, month=month,
            initial_cash=initial_cash,
            base_grid_step=base_grid_step,
            base_amount=base_amount,
            enable_dynamic_center=False,
            enable_trend_filter=False,
            enable_adaptive_grid=False,
            enable_base_position=False
        )
        
        # 智能网格
        smart = run_smart_grid_backtest(
            code=code, year=year, month=month,
            initial_cash=initial_cash,
            base_grid_step=base_grid_step,
            base_amount=base_amount,
            enable_dynamic_center=True,
            enable_trend_filter=True,
            enable_adaptive_grid=True,
            enable_base_position=False
        )
        
        # 混合策略：30%底仓 + 网格
        hybrid = run_smart_grid_backtest(
            code=code, year=year, month=month,
            initial_cash=initial_cash,
            base_grid_step=base_grid_step,
            base_amount=base_amount,
            enable_dynamic_center=True,
            enable_trend_filter=True,
            enable_adaptive_grid=True,
            enable_base_position=True,
            base_position_ratio=0.3
        )
        
        if smart is None or basic is None or hybrid is None:
            console.print("[yellow]跳过[/yellow]")
            continue
        
        if smart["status"] == "数据不足":
            console.print("[yellow]数据不足[/yellow]")
            continue
        
        smart_results.append(smart)
        basic_results.append(basic)
        hybrid_results.append(hybrid)
        
        basic_excess = basic["excess_return"]
        smart_excess = smart["excess_return"]
        hybrid_excess = hybrid["excess_return"]
        
        # 找出最佳策略
        best = max([(basic_excess, "普通"), (smart_excess, "智能"), (hybrid_excess, "混合")], key=lambda x: x[0])
        
        console.print(f"普通:{basic_excess:+.1f}% 智能:{smart_excess:+.1f}% [bold cyan]混合:{hybrid_excess:+.1f}%[/] (最佳:{best[1]})")
    
    if not smart_results:
        console.print("[red]没有有效回测结果[/red]")
        return
    
    # 汇总表格
    console.print()
    table = Table(title=f"[bold]{year}年 月度对比 - {code}[/bold]", box=box.ROUNDED)
    table.add_column("月份", style="cyan", justify="center")
    table.add_column("持有", justify="right")
    table.add_column("普通网格", justify="right")
    table.add_column("智能网格", justify="right")
    table.add_column("混合策略", justify="right", style="bold")
    table.add_column("最佳", justify="center")
    
    total_basic_excess = 0
    total_smart_excess = 0
    total_hybrid_excess = 0
    hybrid_wins = 0
    
    for b, s, h in zip(basic_results, smart_results, hybrid_results):
        hold = s["hold_return"]
        basic_excess = b["excess_return"]
        smart_excess = s["excess_return"]
        hybrid_excess = h["excess_return"]
        
        total_basic_excess += basic_excess
        total_smart_excess += smart_excess
        total_hybrid_excess += hybrid_excess
        
        # 找最佳
        results = [("普通", basic_excess), ("智能", smart_excess), ("混合", hybrid_excess)]
        best_name, best_val = max(results, key=lambda x: x[0])
        
        if hybrid_excess >= max(basic_excess, smart_excess):
            hybrid_wins += 1
            best_name = "混合"
        elif smart_excess >= basic_excess:
            best_name = "智能"
        else:
            best_name = "普通"
        
        hold_color = "green" if hold >= 0 else "red"
        basic_color = "green" if basic_excess >= 0 else "red"
        smart_color = "green" if smart_excess >= 0 else "red"
        hybrid_color = "green" if hybrid_excess >= 0 else "red"
        
        table.add_row(
            f"{s['month']}月",
            f"[{hold_color}]{hold:+.1f}%[/]",
            f"[{basic_color}]{basic_excess:+.1f}%[/]",
            f"[{smart_color}]{smart_excess:+.1f}%[/]",
            f"[{hybrid_color}]{hybrid_excess:+.1f}%[/]",
            f"[bold cyan]{best_name}[/]"
        )
    
    # 汇总行
    table.add_row("", "", "", "", "", "", style="dim")
    table.add_row(
        "[bold]合计[/bold]",
        "-",
        f"[{'green' if total_basic_excess >= 0 else 'red'}]{total_basic_excess:+.1f}%[/]",
        f"[{'green' if total_smart_excess >= 0 else 'red'}]{total_smart_excess:+.1f}%[/]",
        f"[bold {'green' if total_hybrid_excess >= 0 else 'red'}]{total_hybrid_excess:+.1f}%[/]",
        "-",
        style="bold"
    )
    
    console.print(table)
    
    # 统计摘要
    console.print()
    summary = Table(title="[bold]对比摘要[/bold]", box=box.ROUNDED)
    summary.add_column("指标", style="cyan")
    summary.add_column("普通网格", justify="right")
    summary.add_column("智能网格", justify="right")
    summary.add_column("混合策略", justify="right", style="bold")
    
    avg_basic = total_basic_excess / len(basic_results)
    avg_smart = total_smart_excess / len(smart_results)
    avg_hybrid = total_hybrid_excess / len(hybrid_results)
    
    summary.add_row(
        "累计超额收益",
        f"[{'green' if total_basic_excess >= 0 else 'red'}]{total_basic_excess:+.2f}%[/]",
        f"[{'green' if total_smart_excess >= 0 else 'red'}]{total_smart_excess:+.2f}%[/]",
        f"[bold {'green' if total_hybrid_excess >= 0 else 'red'}]{total_hybrid_excess:+.2f}%[/]"
    )
    summary.add_row(
        "月均超额收益",
        f"{avg_basic:+.2f}%",
        f"{avg_smart:+.2f}%",
        f"[bold]{avg_hybrid:+.2f}%[/]"
    )
    
    # 网格利润对比
    total_basic_profit = sum(r["grid_profit"] for r in basic_results)
    total_smart_profit = sum(r["grid_profit"] for r in smart_results)
    total_hybrid_profit = sum(r["grid_profit"] for r in hybrid_results)
    
    summary.add_row(
        "累计网格利润",
        f"+{total_basic_profit:.0f}元",
        f"+{total_smart_profit:.0f}元",
        f"[bold]+{total_hybrid_profit:.0f}元[/]"
    )
    
    summary.add_row(
        "混合策略胜出",
        "-",
        "-",
        f"[bold cyan]{hybrid_wins}/{len(hybrid_results)}[/]"
    )
    
    console.print(summary)
    
    # 评价
    best_strategy = max([
        ("普通网格", total_basic_excess),
        ("智能网格", total_smart_excess),
        ("混合策略", total_hybrid_excess)
    ], key=lambda x: x[1])
    
    if best_strategy[0] == "混合策略":
        evaluation = "[bold green]✅ 混合策略（底仓+网格）表现最佳[/bold green]"
        suggestion = "在趋势行情中，底仓捕获趋势收益，网格捕获波动收益"
    elif best_strategy[0] == "智能网格":
        evaluation = "[bold green]✅ 智能网格表现最佳[/bold green]"
        suggestion = "趋势过滤和动态中枢发挥作用"
    else:
        evaluation = "[bold yellow]⚠️ 普通网格表现最佳[/bold yellow]"
        suggestion = "简单策略在该股票上效果更好"
    
    console.print(Panel(
        f"{evaluation}\n\n"
        f"普通网格累计超额: {total_basic_excess:+.2f}%\n"
        f"智能网格累计超额: {total_smart_excess:+.2f}%\n"
        f"[bold]混合策略累计超额: {total_hybrid_excess:+.2f}%[/bold]\n\n"
        f"混合策略胜出月份: {hybrid_wins}/{len(hybrid_results)} ({hybrid_wins/len(hybrid_results)*100:.0f}%)\n\n"
        f"[dim]{suggestion}[/dim]",
        title="[bold]策略评价[/bold]",
        border_style="green" if total_hybrid_excess > max(total_basic_excess, total_smart_excess) else "yellow",
    ))
    
    return {
        "basic_results": basic_results,
        "smart_results": smart_results,
        "hybrid_results": hybrid_results,
        "summary": {
            "basic_total_excess": total_basic_excess,
            "smart_total_excess": total_smart_excess,
            "hybrid_total_excess": total_hybrid_excess,
            "hybrid_wins": hybrid_wins,
        }
    }


def main():
    parser = argparse.ArgumentParser(description="智能网格交易回测")
    parser.add_argument("--code", "-c", required=True, help="股票代码")
    parser.add_argument("--year", "-y", type=int, default=2025, help="回测年份")
    parser.add_argument("--cash", type=float, default=100000, help="初始资金")
    parser.add_argument("--grid-step", "-g", type=float, default=2.5, help="基础网格间距%%")
    parser.add_argument("--base-amount", "-b", type=float, default=2000, help="基础买入金额")
    parser.add_argument("--compare", action="store_true", help="对比智能网格与普通网格")
    
    args = parser.parse_args()
    
    if args.compare:
        run_comparison_backtest(
            code=args.code,
            year=args.year,
            initial_cash=args.cash,
            base_grid_step=args.grid_step,
            base_amount=args.base_amount
        )
    else:
        # 只运行智能网格
        console.print(Panel.fit(
            f"[bold cyan]📊 {args.year}年 智能网格回测[/bold cyan]\n"
            f"[bold]股票代码: {args.code}[/bold]",
            border_style="cyan"
        ))
        
        results = []
        for month in range(1, 13):
            console.print(f"[dim]回测 {args.year}年{month}月...[/dim]", end=" ")
            
            result = run_smart_grid_backtest(
                code=args.code,
                year=args.year,
                month=month,
                initial_cash=args.cash,
                base_grid_step=args.grid_step,
                base_amount=args.base_amount
            )
            
            if result is None:
                console.print("[yellow]跳过[/yellow]")
                continue
            
            if result["status"] == "数据不足":
                console.print("[yellow]数据不足[/yellow]")
                continue
            
            results.append(result)
            excess = result["excess_return"]
            color = "green" if excess >= 0 else "red"
            console.print(f"[{color}]超额: {excess:+.2f}%[/]")
        
        if results:
            total_excess = sum(r["excess_return"] for r in results)
            console.print(f"\n[bold]累计超额收益: [{['red', 'green'][total_excess >= 0]}]{total_excess:+.2f}%[/][/bold]")
    
    console.print()


if __name__ == "__main__":
    main()


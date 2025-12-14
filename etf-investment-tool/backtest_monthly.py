#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
月度网格交易批量回测
支持输入不同股票代码，逐月测试网格交易有效性
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


def run_single_month_backtest(code: str, year: int, month: int, 
                               initial_cash: float = 100000,
                               grid_step: float = 2.5, 
                               base_amount: float = 2000,
                               verbose: bool = False) -> dict:
    """运行单月网格回测
    
    Args:
        code: 股票代码
        year: 年份
        month: 月份
        initial_cash: 初始资金
        grid_step: 网格间距（%）
        base_amount: 基础买入金额
        verbose: 是否显示详细信息
    
    Returns:
        回测结果字典
    """
    # 计算月份的起止日期
    start_date = f"{year}-{month:02d}-01"
    if month == 12:
        end_date = f"{year + 1}-01-01"
    else:
        end_date = f"{year}-{month + 1:02d}-01"
    
    # 调整结束日期为月末
    end_dt = datetime.strptime(end_date, "%Y-%m-%d") - timedelta(days=1)
    end_date = end_dt.strftime("%Y-%m-%d")
    
    # 如果是未来月份，跳过
    if datetime.strptime(start_date, "%Y-%m-%d") > datetime.now():
        return None
    
    # 调整结束日期不超过今天
    if end_dt > datetime.now():
        end_date = datetime.now().strftime("%Y-%m-%d")
    
    if verbose:
        console.print(f"[dim]获取 {year}年{month}月 数据 ({start_date} ~ {end_date})...[/dim]")
    
    # 获取10分钟数据
    df = get_stock_10min_baostock(code, start_date, end_date, days=35)
    
    if df.empty or len(df) < 20:
        if verbose:
            console.print(f"[yellow]  {year}年{month}月 数据不足 ({len(df)}条)[/yellow]")
        return {
            "year": year,
            "month": month,
            "status": "数据不足",
            "data_count": len(df) if not df.empty else 0
        }
    
    # 获取期初和期末价格
    start_price = float(df['收盘'].iloc[0])
    end_price = float(df['收盘'].iloc[-1])
    high_price = float(df['最高'].max())
    low_price = float(df['最低'].min())
    
    # 使用期初价格作为中枢
    center_price = start_price
    
    # 计算网格档位（向下6档，向上2档）
    grid_levels = {}
    grid_levels[0] = center_price
    for i in range(1, 7):
        grid_levels[i] = center_price * (1 - grid_step * i / 100)
    for i in range(-1, -3, -1):
        grid_levels[i] = center_price * (1 - grid_step * i / 100)
    
    # 回测逻辑
    cash = initial_cash
    shares = 0
    trades = []
    grid_positions = []
    triggered_levels = set()
    
    for idx in range(len(df)):
        row = df.iloc[idx]
        current_price = float(row['收盘'])
        current_high = float(row['最高'])
        current_low = float(row['最低'])
        current_time = row['datetime']
        
        action = None
        trade_shares = 0
        trade_price = 0
        
        # 买入逻辑
        for level_idx in range(1, 7):
            trigger_price = grid_levels[level_idx]
            if current_low <= trigger_price and level_idx not in triggered_levels:
                deviation = abs((trigger_price - center_price) / center_price * 100)
                buy_amount = base_amount * (1 + deviation * 0.15)
                trade_shares = int(buy_amount / trigger_price / 100) * 100
                
                if trade_shares >= 100 and cash >= trade_shares * trigger_price:
                    action = "买入"
                    trade_price = trigger_price
                    cash -= trade_shares * trade_price
                    shares += trade_shares
                    triggered_levels.add(level_idx)
                    
                    grid_positions.append({
                        "grid_level": level_idx,
                        "buy_price": trade_price,
                        "shares": trade_shares,
                        "status": "holding"
                    })
                    break
        
        # 卖出逻辑
        if not action:
            for pos in grid_positions:
                if pos["status"] != "holding":
                    continue
                
                level_idx = pos["grid_level"]
                sell_level = level_idx - 1
                
                if sell_level in grid_levels:
                    sell_trigger = grid_levels[sell_level]
                    if current_high >= sell_trigger:
                        trade_shares = pos["shares"]
                        trade_price = sell_trigger
                        profit = (trade_price - pos["buy_price"]) * trade_shares
                        
                        action = "卖出"
                        cash += trade_shares * trade_price
                        shares -= trade_shares
                        
                        pos["status"] = "sold"
                        pos["profit"] = profit
                        
                        if level_idx in triggered_levels:
                            triggered_levels.remove(level_idx)
                        break
        
        if action:
            trades.append({"action": action, "price": trade_price, "shares": trade_shares})
    
    # 计算结果
    final_value = cash + shares * end_price
    total_return = (final_value - initial_cash) / initial_cash * 100
    hold_return = (end_price - start_price) / start_price * 100
    excess_return = total_return - hold_return
    
    completed_grids = [p for p in grid_positions if p["status"] == "sold"]
    holding_grids = [p for p in grid_positions if p["status"] == "holding"]
    grid_profit = sum(p.get("profit", 0) for p in completed_grids)
    
    # 持仓浮动盈亏
    holding_pnl = sum((end_price - p["buy_price"]) * p["shares"] for p in holding_grids)
    
    buy_count = len([t for t in trades if t["action"] == "买入"])
    sell_count = len([t for t in trades if t["action"] == "卖出"])
    
    return {
        "year": year,
        "month": month,
        "status": "完成",
        "data_count": len(df),
        "start_price": start_price,
        "end_price": end_price,
        "high_price": high_price,
        "low_price": low_price,
        "amplitude": (high_price - low_price) / start_price * 100,  # 振幅
        "strategy_return": total_return,
        "hold_return": hold_return,
        "excess_return": excess_return,
        "grid_profit": grid_profit,
        "holding_pnl": holding_pnl,
        "completed_grids": len(completed_grids),
        "holding_grids": len(holding_grids),
        "buy_count": buy_count,
        "sell_count": sell_count,
        "final_shares": shares,
        "final_cash": cash,
        "final_value": final_value,
    }


def run_yearly_backtest(code: str, year: int = 2025,
                        initial_cash: float = 100000,
                        grid_step: float = 2.5,
                        base_amount: float = 2000):
    """运行全年逐月回测
    
    Args:
        code: 股票代码
        year: 年份
        initial_cash: 初始资金
        grid_step: 网格间距（%）
        base_amount: 基础买入金额
    """
    console.print()
    console.print(Panel.fit(
        f"[bold cyan]📊 {year}年 月度网格交易回测[/bold cyan]\n"
        f"[bold]股票代码: {code}[/bold]\n"
        f"[dim]网格间距: {grid_step}% | 基础金额: {base_amount}元 | 初始资金: {initial_cash}元[/dim]",
        border_style="cyan"
    ))
    
    results = []
    
    # 逐月回测
    for month in range(1, 13):
        console.print(f"[dim]回测 {year}年{month}月...[/dim]", end=" ")
        result = run_single_month_backtest(
            code=code,
            year=year,
            month=month,
            initial_cash=initial_cash,
            grid_step=grid_step,
            base_amount=base_amount,
            verbose=False
        )
        
        if result is None:
            console.print(f"[yellow]跳过（未来月份）[/yellow]")
            continue
        
        if result["status"] == "数据不足":
            console.print(f"[yellow]数据不足[/yellow]")
        else:
            excess = result["excess_return"]
            color = "green" if excess >= 0 else "red"
            console.print(f"[{color}]超额收益: {excess:+.2f}%[/]")
        
        results.append(result)
    
    if not results:
        console.print("[red]没有可用的回测结果[/red]")
        return
    
    # 过滤有效结果
    valid_results = [r for r in results if r["status"] == "完成"]
    
    if not valid_results:
        console.print("[red]没有有效的回测结果[/red]")
        return
    
    # 打印汇总表格
    console.print()
    table = Table(title=f"[bold]{year}年 月度网格回测汇总 - {code}[/bold]", box=box.ROUNDED)
    table.add_column("月份", style="cyan", justify="center")
    table.add_column("期初价", justify="right")
    table.add_column("期末价", justify="right")
    table.add_column("振幅", justify="right")
    table.add_column("持有收益", justify="right")
    table.add_column("策略收益", justify="right")
    table.add_column("超额收益", justify="right")
    table.add_column("网格利润", justify="right")
    table.add_column("完成轮次", justify="center")
    table.add_column("持仓中", justify="center")
    
    total_strategy = 0
    total_hold = 0
    total_excess = 0
    total_grid_profit = 0
    total_completed = 0
    win_months = 0
    
    for r in valid_results:
        hold_ret = r["hold_return"]
        strat_ret = r["strategy_return"]
        excess = r["excess_return"]
        
        hold_color = "green" if hold_ret >= 0 else "red"
        strat_color = "green" if strat_ret >= 0 else "red"
        excess_color = "green" if excess >= 0 else "red"
        
        if excess >= 0:
            win_months += 1
        
        table.add_row(
            f"{r['month']}月",
            f"{r['start_price']:.2f}",
            f"{r['end_price']:.2f}",
            f"{r['amplitude']:.1f}%",
            f"[{hold_color}]{hold_ret:+.2f}%[/]",
            f"[{strat_color}]{strat_ret:+.2f}%[/]",
            f"[bold {excess_color}]{excess:+.2f}%[/]",
            f"+{r['grid_profit']:.0f}",
            str(r["completed_grids"]),
            str(r["holding_grids"])
        )
        
        total_strategy += strat_ret
        total_hold += hold_ret
        total_excess += excess
        total_grid_profit += r["grid_profit"]
        total_completed += r["completed_grids"]
    
    # 添加汇总行
    table.add_row("", "", "", "", "", "", "", "", "", "", style="dim")
    table.add_row(
        "[bold]合计/平均[/bold]",
        "-",
        "-",
        f"{np.mean([r['amplitude'] for r in valid_results]):.1f}%",
        f"[{'green' if total_hold >= 0 else 'red'}]{total_hold:+.2f}%[/]",
        f"[{'green' if total_strategy >= 0 else 'red'}]{total_strategy:+.2f}%[/]",
        f"[bold {'green' if total_excess >= 0 else 'red'}]{total_excess:+.2f}%[/]",
        f"+{total_grid_profit:.0f}",
        str(total_completed),
        "-",
        style="bold"
    )
    
    console.print(table)
    
    # 打印统计摘要
    avg_amplitude = np.mean([r["amplitude"] for r in valid_results])
    avg_excess = total_excess / len(valid_results)
    
    console.print()
    summary_table = Table(title="[bold]统计摘要[/bold]", box=box.ROUNDED)
    summary_table.add_column("指标", style="cyan")
    summary_table.add_column("数值", justify="right")
    
    summary_table.add_row("有效月份数", f"{len(valid_results)}个月")
    summary_table.add_row("累计持有收益", f"[{'green' if total_hold >= 0 else 'red'}]{total_hold:+.2f}%[/]")
    summary_table.add_row("累计策略收益", f"[{'green' if total_strategy >= 0 else 'red'}]{total_strategy:+.2f}%[/]")
    summary_table.add_row("累计超额收益", f"[bold {'green' if total_excess >= 0 else 'red'}]{total_excess:+.2f}%[/]")
    summary_table.add_row("月均超额收益", f"[{'green' if avg_excess >= 0 else 'red'}]{avg_excess:+.2f}%[/]")
    summary_table.add_row("跑赢月份", f"[green]{win_months}[/green] / {len(valid_results)} ({win_months/len(valid_results)*100:.0f}%)")
    summary_table.add_row("累计网格利润", f"[green]+{total_grid_profit:.0f}元[/green]")
    summary_table.add_row("完成网格轮次", f"{total_completed}次")
    summary_table.add_row("月均振幅", f"{avg_amplitude:.1f}%")
    
    console.print(summary_table)
    
    # 策略评价
    if total_excess > 5:
        evaluation = "[bold green]✅ 网格策略全年表现优秀[/bold green]"
        suggestion = "网格策略在该股票上有明显优势，建议继续使用"
    elif total_excess > 0:
        evaluation = "[bold green]✅ 网格策略全年有效[/bold green]"
        suggestion = "网格策略整体跑赢持有，但优势不明显"
    elif total_excess > -5:
        evaluation = "[bold yellow]⚠️ 网格策略表现一般[/bold yellow]"
        suggestion = "网格策略与持有接近，可根据行情灵活选择"
    else:
        evaluation = "[bold red]❌ 网格策略全年跑输持有[/bold red]"
        suggestion = "该股票可能更适合趋势跟踪策略"
    
    # 分析月份特征
    high_amplitude_months = [r for r in valid_results if r["amplitude"] > 15]
    low_amplitude_months = [r for r in valid_results if r["amplitude"] < 10]
    
    if high_amplitude_months:
        high_amp_excess = np.mean([r["excess_return"] for r in high_amplitude_months])
    else:
        high_amp_excess = 0
    
    if low_amplitude_months:
        low_amp_excess = np.mean([r["excess_return"] for r in low_amplitude_months])
    else:
        low_amp_excess = 0
    
    console.print(Panel(
        f"{evaluation}\n\n"
        f"累计超额收益: {total_excess:+.2f}%\n"
        f"跑赢月份: {win_months}/{len(valid_results)} ({win_months/len(valid_results)*100:.0f}%)\n"
        f"累计网格利润: +{total_grid_profit:.0f}元\n\n"
        f"[dim]高振幅月份(>15%)平均超额: {high_amp_excess:+.2f}%[/dim]\n"
        f"[dim]低振幅月份(<10%)平均超额: {low_amp_excess:+.2f}%[/dim]\n\n"
        f"[dim]{suggestion}[/dim]",
        title="[bold]策略评价[/bold]",
        border_style="green" if total_excess > 0 else ("yellow" if total_excess > -5 else "red"),
    ))
    
    return {
        "results": valid_results,
        "summary": {
            "total_hold_return": total_hold,
            "total_strategy_return": total_strategy,
            "total_excess_return": total_excess,
            "total_grid_profit": total_grid_profit,
            "win_months": win_months,
            "total_months": len(valid_results),
        }
    }


def main():
    parser = argparse.ArgumentParser(description="月度网格交易批量回测")
    parser.add_argument("--code", "-c", required=True, help="股票代码（如 601899）")
    parser.add_argument("--year", "-y", type=int, default=2025, help="回测年份（默认2025）")
    parser.add_argument("--cash", type=float, default=100000, help="初始资金（默认10万）")
    parser.add_argument("--grid-step", "-g", type=float, default=2.5, help="网格间距%%（默认2.5%%）")
    parser.add_argument("--base-amount", "-b", type=float, default=2000, help="基础买入金额（默认2000元）")
    
    args = parser.parse_args()
    
    run_yearly_backtest(
        code=args.code,
        year=args.year,
        initial_cash=args.cash,
        grid_step=args.grid_step,
        base_amount=args.base_amount
    )
    
    console.print()


if __name__ == "__main__":
    main()


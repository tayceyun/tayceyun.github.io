#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
10分钟级别网格交易回测
铜陵有色专用，验证网格交易策略有效性
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


def run_grid_backtest_10min(code: str, days: int = 30, initial_cash: float = 100000,
                             grid_step: float = 2.5, base_amount: float = 2000,
                             show_trades: bool = True, center_mode: str = "ma",
                             custom_center: float = None):
    """10分钟级别网格交易回测
    
    Args:
        code: 股票代码，如 '601899'
        days: 回测天数
        initial_cash: 初始资金
        grid_step: 网格间距（百分比，建议2.5-3%）
        base_amount: 基础买入金额
        show_trades: 是否显示交易明细
        center_mode: 中枢计算模式 "ma"(均线), "start"(期初价格), "custom"(自定义)
        custom_center: 自定义中枢价格
    
    Returns:
        回测结果字典
    """
    console.print(f"\n[bold cyan]📊 10分钟网格交易回测[/bold cyan]")
    console.print(f"[dim]正在获取 {code} 最近 {days} 天的10分钟K线数据...[/dim]")
    
    # 获取10分钟数据
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
    
    df = get_stock_10min_baostock(code, start_date, end_date, days)
    
    if df.empty or len(df) < 50:
        console.print(f"[red]数据不足，无法回测（获取到{len(df)}条数据）[/red]")
        return None
    
    console.print(f"[green]✓ 获取到 {len(df)} 条10分钟K线数据[/green]")
    
    # 获取期初价格和当前价格
    start_price_init = float(df['收盘'].iloc[0])
    current_price = float(df['收盘'].iloc[-1])
    
    # 根据 center_mode 计算中枢价格
    if center_mode == "custom" and custom_center is not None:
        center_price = custom_center
        console.print(f"[dim]使用自定义中枢价格: {center_price:.3f}[/dim]")
    elif center_mode == "start":
        center_price = start_price_init
        console.print(f"[dim]使用期初价格作为中枢: {center_price:.3f}[/dim]")
    else:  # "ma" 模式
        console.print(f"[dim]获取日线数据计算中枢价格...[/dim]")
        daily_df = get_stock_daily_baostock(code, days=60)
        if daily_df.empty or len(daily_df) < 20:
            console.print(f"[red]无法获取足够日线数据计算中枢[/red]")
            return None
        
        # 计算中枢价格：MA20×40% + MA60×40% + 月K低点×20%
        ma20 = float(daily_df['收盘'].tail(20).mean())
        ma60 = float(daily_df['收盘'].tail(min(60, len(daily_df))).mean())
        monthly_low = float(daily_df['最低'].tail(min(60, len(daily_df))).min())
        center_price = ma20 * 0.4 + ma60 * 0.4 + monthly_low * 0.2
    
    console.print(f"[cyan]中枢价格: {center_price:.3f}[/cyan]")
    console.print(f"[cyan]当前价格: {current_price:.3f}[/cyan]")
    console.print(f"[cyan]网格间距: {grid_step}%[/cyan]")
    
    # 计算网格档位（向下6档，向上2档）
    grid_levels = {}
    grid_levels[0] = center_price  # 中枢
    for i in range(1, 7):  # 向下6档
        grid_levels[i] = center_price * (1 - grid_step * i / 100)
    for i in range(-1, -3, -1):  # 向上2档（用于止盈）
        grid_levels[i] = center_price * (1 - grid_step * i / 100)
    
    # 打印网格档位
    console.print("\n[bold]网格档位:[/bold]")
    for level_idx in sorted(grid_levels.keys()):
        price = grid_levels[level_idx]
        deviation = (price - center_price) / center_price * 100
        if level_idx == 0:
            console.print(f"  格0 (中枢): {price:.3f}")
        elif level_idx > 0:
            console.print(f"  格{level_idx}: {price:.3f} ({deviation:+.1f}%)")
        else:
            console.print(f"  格{level_idx}: {price:.3f} ({deviation:+.1f}%) [止盈区]")
    
    # 回测逻辑
    cash = initial_cash
    shares = 0
    trades = []
    grid_positions = []  # 记录每格买入情况
    portfolio_values = []
    
    # 用于追踪已触发的网格层级
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
        reason = ""
        
        # ========== 买入逻辑 ==========
        # 检查是否触发新的网格买入（价格跌破某个格子）
        for level_idx in range(1, 7):  # 格1到格6
            trigger_price = grid_levels[level_idx]
            
            # 如果当前最低价触及该网格且未被触发过
            if current_low <= trigger_price and level_idx not in triggered_levels:
                # 计算买入金额（越跌买越多）
                deviation = abs((trigger_price - center_price) / center_price * 100)
                buy_amount = base_amount * (1 + deviation * 0.15)  # 每跌1%多买15%
                trade_shares = int(buy_amount / trigger_price / 100) * 100
                
                if trade_shares >= 100 and cash >= trade_shares * trigger_price:
                    action = "买入"
                    trade_price = trigger_price
                    reason = f"触发格{level_idx} ({deviation:.1f}%偏离)"
                    cash -= trade_shares * trade_price
                    shares += trade_shares
                    triggered_levels.add(level_idx)
                    
                    grid_positions.append({
                        "grid_level": level_idx,
                        "buy_price": trade_price,
                        "shares": trade_shares,
                        "buy_time": str(current_time),
                        "status": "holding"
                    })
                    break
        
        # ========== 卖出逻辑 ==========
        # 检查持仓中是否有可以卖出的（价格涨回上一格）
        if not action:
            for pos in grid_positions:
                if pos["status"] != "holding":
                    continue
                
                level_idx = pos["grid_level"]
                sell_level = level_idx - 1  # 卖出触发格（上一格）
                
                if sell_level in grid_levels:
                    sell_trigger = grid_levels[sell_level]
                    
                    # 如果当前最高价触及卖出触发价
                    if current_high >= sell_trigger:
                        trade_shares = pos["shares"]
                        trade_price = sell_trigger
                        profit = (trade_price - pos["buy_price"]) * trade_shares
                        profit_pct = (trade_price - pos["buy_price"]) / pos["buy_price"] * 100
                        
                        action = "卖出"
                        reason = f"涨回格{sell_level} (+{profit:.0f}元, +{profit_pct:.1f}%)"
                        cash += trade_shares * trade_price
                        shares -= trade_shares
                        
                        pos["status"] = "sold"
                        pos["sell_price"] = trade_price
                        pos["sell_time"] = str(current_time)
                        pos["profit"] = profit
                        pos["profit_pct"] = profit_pct
                        
                        # 移除该格的触发标记，允许再次触发
                        if level_idx in triggered_levels:
                            triggered_levels.remove(level_idx)
                        break
        
        if action:
            trades.append({
                "时间": str(current_time),
                "操作": action,
                "价格": round(trade_price, 3),
                "数量": trade_shares,
                "金额": round(trade_shares * trade_price, 2),
                "原因": reason,
                "持仓": shares,
                "现金": round(cash, 2),
            })
        
        # 记录组合价值（用收盘价计算）
        portfolio_value = cash + shares * current_price
        portfolio_values.append({
            "时间": current_time,
            "组合价值": portfolio_value,
            "持仓": shares,
            "现金": cash,
            "股价": current_price,
        })
    
    # ========== 计算统计指标 ==========
    final_value = portfolio_values[-1]["组合价值"] if portfolio_values else initial_cash
    total_return = (final_value - initial_cash) / initial_cash * 100
    
    start_price = float(df.iloc[0]['收盘'])
    end_price = float(df.iloc[-1]['收盘'])
    hold_return = (end_price - start_price) / start_price * 100
    
    excess_return = total_return - hold_return
    
    # 统计交易
    buy_trades = [t for t in trades if t["操作"] == "买入"]
    sell_trades = [t for t in trades if t["操作"] == "卖出"]
    
    # 计算已完成网格的收益
    completed_grids = [p for p in grid_positions if p["status"] == "sold"]
    holding_grids = [p for p in grid_positions if p["status"] == "holding"]
    
    grid_profits = [p.get("profit", 0) for p in completed_grids]
    total_grid_profit = sum(grid_profits)
    avg_grid_profit = np.mean(grid_profits) if grid_profits else 0
    
    # 计算持仓中的浮动盈亏
    holding_pnl = 0
    for pos in holding_grids:
        holding_pnl += (end_price - pos["buy_price"]) * pos["shares"]
    
    # ========== 打印结果 ==========
    console.print()
    console.print(Panel.fit(
        f"[bold cyan]📈 10分钟网格交易回测结果[/bold cyan]\n"
        f"[bold]{code}[/bold]\n"
        f"[dim]{start_date} ~ {end_date} (共{len(df)}根10分钟K线)[/dim]",
        border_style="cyan"
    ))
    
    # 网格参数
    table0 = Table(title="[bold]网格参数[/bold]", box=box.ROUNDED)
    table0.add_column("参数", style="cyan")
    table0.add_column("数值", justify="right")
    table0.add_row("中枢价格", f"{center_price:.3f}")
    table0.add_row("网格间距", f"{grid_step}%")
    table0.add_row("基础买入金额", f"{base_amount:.0f}元")
    table0.add_row("初始资金", f"{initial_cash:.0f}元")
    console.print(table0)
    
    # 收益对比
    table1 = Table(title="[bold]收益对比[/bold]", box=box.ROUNDED)
    table1.add_column("指标", style="cyan")
    table1.add_column("数值", justify="right")
    
    table1.add_row("期初价格", f"{start_price:.3f}")
    table1.add_row("期末价格", f"{end_price:.3f}")
    table1.add_row("", "")
    table1.add_row("策略总收益", f"[{'green' if total_return >= 0 else 'red'}]{total_return:+.2f}%[/]")
    table1.add_row("持有收益", f"[{'green' if hold_return >= 0 else 'red'}]{hold_return:+.2f}%[/]")
    excess_color = 'green' if excess_return >= 0 else 'red'
    table1.add_row("超额收益", f"[bold {excess_color}]{excess_return:+.2f}%[/]")
    table1.add_row("", "")
    table1.add_row("期末组合价值", f"{final_value:.2f}元")
    table1.add_row("期末持仓数量", f"{shares}股")
    table1.add_row("期末现金", f"{cash:.2f}元")
    console.print(table1)
    
    # 网格交易统计
    table2 = Table(title="[bold]网格交易统计[/bold]", box=box.ROUNDED)
    table2.add_column("指标", style="cyan")
    table2.add_column("数值", justify="right")
    table2.add_row("总交易次数", f"{len(trades)}次")
    table2.add_row("买入次数", f"{len(buy_trades)}次")
    table2.add_row("卖出次数", f"{len(sell_trades)}次")
    table2.add_row("", "")
    table2.add_row("完成网格轮次", f"[green]{len(completed_grids)}次[/green]")
    table2.add_row("持仓中网格", f"[yellow]{len(holding_grids)}笔[/yellow]")
    table2.add_row("", "")
    table2.add_row("已实现网格利润", f"[green]+{total_grid_profit:.2f}元[/green]")
    table2.add_row("平均单次网格利润", f"+{avg_grid_profit:.2f}元")
    table2.add_row("持仓浮动盈亏", f"[{'green' if holding_pnl >= 0 else 'red'}]{holding_pnl:+.2f}元[/]")
    console.print(table2)
    
    # 持仓明细
    if holding_grids:
        table3 = Table(title="[bold]持仓中网格明细[/bold]", box=box.SIMPLE)
        table3.add_column("网格", style="cyan")
        table3.add_column("买入价", justify="right")
        table3.add_column("数量", justify="right")
        table3.add_column("买入时间", style="dim")
        table3.add_column("浮动盈亏", justify="right")
        
        for pos in holding_grids:
            pnl = (end_price - pos["buy_price"]) * pos["shares"]
            pnl_pct = (end_price - pos["buy_price"]) / pos["buy_price"] * 100
            table3.add_row(
                f"格{pos['grid_level']}",
                f"{pos['buy_price']:.3f}",
                str(pos["shares"]),
                pos["buy_time"][:16],
                f"[{'green' if pnl >= 0 else 'red'}]{pnl:+.0f}元 ({pnl_pct:+.1f}%)[/]"
            )
        console.print(table3)
    
    # 策略评价
    if excess_return > 3:
        evaluation = "[bold green]✅ 网格策略非常有效[/bold green]"
        eval_detail = "显著跑赢持有策略"
    elif excess_return > 0:
        evaluation = "[bold green]✅ 网格策略有效[/bold green]"
        eval_detail = "跑赢持有策略"
    elif excess_return > -2:
        evaluation = "[bold yellow]⚠️ 网格策略表现一般[/bold yellow]"
        eval_detail = "与持有策略接近"
    else:
        evaluation = "[bold red]❌ 网格策略不如持有[/bold red]"
        eval_detail = "建议调整参数或策略"
    
    # 网格适用性分析
    if len(completed_grids) > 0:
        grid_efficiency = f"网格完成率: {len(completed_grids)}/{len(buy_trades)} ({len(completed_grids)/max(len(buy_trades),1)*100:.0f}%)"
    else:
        grid_efficiency = "无完整网格轮次"
    
    console.print(Panel(
        f"{evaluation}\n\n"
        f"超额收益: {excess_return:+.2f}%\n"
        f"已实现利润: +{total_grid_profit:.2f}元\n"
        f"{grid_efficiency}\n\n"
        f"[dim]{eval_detail}[/dim]",
        title="[bold]策略评价[/bold]",
        border_style="green" if excess_return > 0 else ("yellow" if excess_return > -2 else "red"),
    ))
    
    # 打印交易明细
    if show_trades and trades:
        console.print()
        table4 = Table(title="[bold]交易明细[/bold]", box=box.SIMPLE)
        table4.add_column("时间", style="dim")
        table4.add_column("操作")
        table4.add_column("价格", justify="right")
        table4.add_column("数量", justify="right")
        table4.add_column("金额", justify="right")
        table4.add_column("原因")
        
        for t in trades[:30]:  # 只显示前30条
            op_color = "green" if t["操作"] == "买入" else "red"
            table4.add_row(
                t["时间"][5:16],  # 只显示月-日 时:分
                f"[{op_color}]{t['操作']}[/]",
                f"{t['价格']:.3f}",
                str(t["数量"]),
                f"{t['金额']:.0f}",
                t["原因"]
            )
        
        if len(trades) > 30:
            table4.add_row("...", "...", "...", "...", "...", f"(还有{len(trades)-30}条)")
        
        console.print(table4)
    
    return {
        "trades": trades,
        "portfolio_values": portfolio_values,
        "grid_positions": grid_positions,
        "metrics": {
            "initial_cash": initial_cash,
            "final_value": final_value,
            "total_return": total_return,
            "hold_return": hold_return,
            "excess_return": excess_return,
            "grid_profit": total_grid_profit,
            "grid_count": len(completed_grids),
            "holding_count": len(holding_grids),
            "holding_pnl": holding_pnl,
        },
        "params": {
            "code": code,
            "days": days,
            "grid_step": grid_step,
            "center_price": center_price,
            "base_amount": base_amount,
        }
    }


def main():
    parser = argparse.ArgumentParser(description="10分钟网格交易回测")
    parser.add_argument("--code", "-c", default="601899", help="股票代码（默认601899铜陵有色）")
    parser.add_argument("--days", "-d", type=int, default=30, help="回测天数（默认30天）")
    parser.add_argument("--cash", type=float, default=100000, help="初始资金（默认10万）")
    parser.add_argument("--grid-step", "-g", type=float, default=2.5, help="网格间距%%（默认2.5%%）")
    parser.add_argument("--base-amount", "-b", type=float, default=2000, help="基础买入金额（默认2000元）")
    parser.add_argument("--no-trades", action="store_true", help="不显示交易明细")
    parser.add_argument("--center-mode", "-m", choices=["ma", "start", "custom"], default="start",
                        help="中枢价格模式: ma(均线计算), start(期初价格), custom(自定义)")
    parser.add_argument("--center-price", type=float, default=None, help="自定义中枢价格（需配合 --center-mode custom）")
    
    args = parser.parse_args()
    
    result = run_grid_backtest_10min(
        code=args.code,
        days=args.days,
        initial_cash=args.cash,
        grid_step=args.grid_step,
        base_amount=args.base_amount,
        show_trades=not args.no_trades,
        center_mode=args.center_mode,
        custom_center=args.center_price
    )
    
    if result:
        console.print(f"\n[dim]回测完成。共{len(result['trades'])}笔交易。[/dim]\n")


if __name__ == "__main__":
    main()


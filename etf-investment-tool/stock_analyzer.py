#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
个股分析工具
- 紫金矿业：目标买入价分析（方便盘中看盘）
- 铜陵有色：网格交易分析（次日操作计划）
数据源：Tushare Pro
"""

import pandas as pd
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box

from data_source import get_stock_daily, get_index_daily
from grid_trading import (
    analyze_grid_position, calculate_target_price as calc_grid_center,
    load_positions, save_positions
)

console = Console()

# 个股配置
# 紫金矿业：目标价分析
ZIJIN_CONFIG = {
    "code": "601899",
    "name": "紫金矿业",
    "market": "sh",
    "shares": 600,
    "cost": 28.322,
}

# 铜陵有色：网格交易
TONGLING_CONFIG = {
    "code": "000630",
    "name": "铜陵有色",
    "market": "sz",
    "shares": 5200,
    "cost": 4.250,
    "core_shares": 3000,  # 核心仓位
    "available_cash": 15000,  # 可用资金
    "base_amount": 2000,  # 基础买入金额
}


def calculate_target_price(df: pd.DataFrame) -> float:
    """计算目标中枢价格（ETF模式）
    
    公式：MA20×40% + MA60×40% + 月K低点×20%
    """
    if df.empty or len(df) < 60:
        return 0.0
    
    ma20 = float(df['收盘'].tail(20).mean())
    ma60 = float(df['收盘'].tail(60).mean())
    monthly_low = float(df['最低'].tail(60).min())
    
    target_price = ma20 * 0.4 + ma60 * 0.4 + monthly_low * 0.2
    return round(target_price, 2)


def analyze_zijin() -> dict:
    """分析紫金矿业，给出目标买入价"""
    config = ZIJIN_CONFIG
    console.print(f"[dim]正在分析 {config['name']}...[/dim]")
    
    df = get_stock_daily(config["code"], days=250)
    if df.empty:
        console.print(f"[red]{config['name']} 数据获取失败[/red]")
        return None
    
    current_price = float(df['收盘'].iloc[-1])
    cost = config["cost"]
    profit_pct = (current_price - cost) / cost * 100
    
    # 计算目标价
    base_target = calculate_target_price(df)
    
    # 多档目标价
    target_levels = [
        {"label": "保守", "price": round(base_target * 0.97, 2), "deviation": 0},
        {"label": "正常", "price": round(base_target * 0.93, 2), "deviation": 0},
        {"label": "激进", "price": round(base_target * 0.88, 2), "deviation": 0},
    ]
    
    # 计算偏离现价
    for level in target_levels:
        level["deviation"] = round((level["price"] - current_price) / current_price * 100, 1)
    
    # 清除加载信息
    console.print("\033[A\033[K", end="")
    
    # 显示结果
    console.print(Panel(
        f"[bold]{config['name']}[/bold] ({config['code']})\n"
        f"现价: [cyan]{current_price:.2f}[/cyan]  "
        f"成本: {cost:.2f}  "
        f"盈亏: [{'green' if profit_pct >= 0 else 'red'}]{profit_pct:+.1f}%[/]  "
        f"持仓: {config['shares']}股",
        title="[bold orange1]紫金矿业 - 目标买入价[/bold orange1]",
        border_style="orange1",
    ))
    
    # 目标价档位表格
    target_table = Table(box=box.ROUNDED, show_header=True, header_style="bold")
    target_table.add_column("档位", width=10)
    target_table.add_column("目标价", justify="right", width=10)
    target_table.add_column("偏离现价", justify="right", width=12)
    target_table.add_column("说明", width=30)
    
    for level in target_levels:
        deviation_color = "red" if level["deviation"] < 0 else "green"
        if level["label"] == "保守":
            desc = "小幅回调即可买入"
        elif level["label"] == "正常":
            desc = "标准买入位，可正常建仓"
        else:
            desc = "大跌后加仓机会"
        
        target_table.add_row(
            level["label"],
            f"[bold cyan]{level['price']:.2f}[/bold cyan]",
            f"[{deviation_color}]{level['deviation']:+.1f}%[/]",
            f"[dim]{desc}[/dim]"
        )
    
    console.print(target_table)
    console.print()
    
    return {
        "name": config["name"],
        "code": config["code"],
        "current_price": current_price,
        "cost": cost,
        "profit_pct": profit_pct,
        "shares": config["shares"],
        "target_levels": target_levels
    }


def analyze_tongling() -> dict:
    """分析铜陵有色，给出网格交易操作计划"""
    config = TONGLING_CONFIG
    console.print(f"[dim]正在分析 {config['name']}...[/dim]")
    
    df = get_stock_daily(config["code"], days=250)
    if df.empty:
        console.print(f"[red]{config['name']} 数据获取失败[/red]")
        return None
    
    # 加载持仓记录，更新可用资金
    positions = load_positions()
    if config["code"] in positions:
        config["available_cash"] = positions[config["code"]].get("available_cash", config["available_cash"])
    
    # 分析网格状态
    result = analyze_grid_position(config["code"], df, config)
    
    # 清除加载信息
    console.print("\033[A\033[K", end="")
    
    current_price = result.get("current_price", 0)
    center_price = result.get("center_price", 0)
    deviation_pct = result.get("deviation_pct", 0)
    
    deviation_color = "red" if deviation_pct < 0 else "green"
    
    # 显示基本信息
    console.print(Panel(
        f"[bold]{config['name']}[/bold] ({config['code']})\n"
        f"现价: [cyan]{current_price:.3f}[/cyan]  "
        f"中枢: {center_price:.3f}  "
        f"偏离: [{deviation_color}]{deviation_pct:+.1f}%[/]  "
        f"网格间距: {result.get('grid_step', 0):.1f}%  "
        f"可用资金: ¥{result.get('available_cash', 0):,.0f}",
        title="[bold blue]铜陵有色 - 网格交易[/bold blue]",
        border_style="blue",
    ))
    
    # 次日操作计划
    console.print("[bold]📌 次日操作计划[/bold]")
    
    buy_plan = result.get("buy_plan")
    sell_plan = result.get("sell_plan")
    profit_take = result.get("profit_take_plan")
    
    has_plan = False
    
    if buy_plan:
        has_plan = True
        console.print(Panel(
            f"若跌至 [bold cyan]{buy_plan['trigger_price']:.3f}[/bold cyan] "
            f"({buy_plan['deviation_pct']:+.1f}%)\n"
            f"→ 买入 [bold]{buy_plan['shares']}股[/bold] "
            f"(约 ¥{buy_plan['amount']:.0f})",
            title="[green]📥 买入计划[/green]",
            border_style="green",
        ))
    
    if sell_plan:
        has_plan = True
        console.print(Panel(
            f"若涨至 [bold cyan]{sell_plan['trigger_price']:.3f}[/bold cyan] "
            f"({sell_plan['deviation_pct']:+.1f}%)\n"
            f"→ 卖出 [bold]{sell_plan['shares']}股[/bold] "
            f"(预期盈利 ¥{sell_plan.get('expected_profit', 0):.0f})",
            title="[red]📤 卖出计划[/red]",
            border_style="red",
        ))
    
    if profit_take:
        has_plan = True
        console.print(Panel(
            f"当前已高于中枢5%，建议卖出 [bold]{profit_take['shares']}股[/bold]",
            title="[yellow]💰 止盈计划[/yellow]",
            border_style="yellow",
        ))
    
    if not has_plan:
        console.print(Panel(
            "[dim]暂无操作计划，持仓观望[/dim]",
            border_style="dim",
        ))
    
    # 显示网格档位
    grid_levels = result.get("grid_levels", [])
    if grid_levels:
        grid_table = Table(title="网格档位", box=box.SIMPLE, show_header=True, header_style="dim")
        grid_table.add_column("档位", width=6)
        grid_table.add_column("价格", justify="right", width=8)
        grid_table.add_column("偏离中枢", justify="right", width=10)
        
        for i, level in enumerate(grid_levels[:6]):
            deviation = (level - center_price) / center_price * 100
            is_current = level <= current_price < (grid_levels[i-1] if i > 0 else float('inf'))
            style = "bold cyan" if is_current else ""
            grid_table.add_row(
                f"格{i}",
                f"{level:.3f}",
                f"{deviation:+.1f}%",
                style=style
            )
        
        console.print(grid_table)
    
    console.print()
    
    # 添加 name 字段
    result["name"] = config["name"]
    return result


def analyze_all_stocks() -> tuple:
    """分析所有个股"""
    console.print()
    console.print(Panel.fit(
        f"[bold magenta]个股分析系统[/bold magenta]\n"
        f"[dim]分析时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}[/dim]",
        border_style="magenta"
    ))
    console.print()
    
    # 紫金矿业：目标价分析
    zijin_result = analyze_zijin()
    
    # 铜陵有色：网格交易
    tongling_result = analyze_tongling()
    
    return zijin_result, tongling_result


def main():
    """主函数"""
    try:
        return analyze_all_stocks()
    except KeyboardInterrupt:
        console.print("\n[yellow]已取消分析[/yellow]")
        return None, None
    except Exception as e:
        console.print(f"\n[red]分析出错: {e}[/red]")
        import traceback
        traceback.print_exc()
        return None, None


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
投资分析主程序
紫金矿业目标价分析、铜陵有色网格交易
输出：终端显示 + HTML 报告
数据源：Baostock（免费）
"""

from datetime import datetime
from rich.console import Console
from rich.panel import Panel

from stock_analyzer import analyze_all_stocks
from html_report import generate_html_report

console = Console()


def main():
    """主函数"""
    console.print()
    console.print(Panel.fit(
        "[bold cyan]📊 每日投资分析系统[/bold cyan]\n"
        f"[dim]运行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}[/dim]\n"
        "[dim]数据源: Baostock（免费）[/dim]",
        border_style="cyan"
    ))
    
    try:
        # 个股分析
        console.print("\n[bold]━━━ 个股分析 ━━━[/bold]")
        zijin_result, tongling_result = analyze_all_stocks()
        
        # 生成 HTML 报告
        console.print("\n[dim]正在生成 HTML 报告...[/dim]")
        
        stock_results = [zijin_result] if zijin_result else []
        
        report_path = generate_html_report(
            etf_results=[],  # ETF 功能暂时禁用
            stock_results=stock_results,
            grid_result=tongling_result
        )
        
        console.print(f"[green]✅ HTML 报告已生成: {report_path}[/green]")
        
    except KeyboardInterrupt:
        console.print("\n[yellow]已取消分析[/yellow]")
    except Exception as e:
        console.print(f"\n[red]分析出错: {e}[/red]")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()



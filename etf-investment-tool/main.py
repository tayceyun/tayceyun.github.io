#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
投资分析主程序

功能：
1. 市场综合分析（8个核心指数 + 轮动信号）【新增】
2. 指数多周期共振分析（单个指数）
3. 个股目标价分析（支持任意股票）

输出：终端显示 + HTML 报告
数据源：Baostock + AkShare（免费）
"""

import argparse
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.markup import escape

console = Console()

# 输出目录
OUTPUT_DIR = Path(__file__).parent / "output"
OUTPUT_DIR.mkdir(exist_ok=True)


def cleanup_old_reports(report_type: str, keep_latest: int = 1, index_code: str = None):
    """
    清理旧报告，只保留最新的 N 个
    
    Args:
        report_type: 报告类型 ("market", "index", "stock", "report")
        keep_latest: 保留最新的报告数量，默认1
        index_code: 对于 index 类型，指定指数代码（如 "000300"）
    """
    if not OUTPUT_DIR.exists():
        return
    
    # 根据报告类型匹配文件
    if report_type == "market":
        pattern = "market_*.html"
    elif report_type == "index":
        if index_code:
            pattern = f"index_{index_code}_*.html"
        else:
            pattern = "index_*.html"
    elif report_type == "stock":
        pattern = "stock_*.html"
    elif report_type == "report":
        pattern = "report_*.html"
    else:
        return
    
    # 获取匹配的文件并按修改时间排序（最新在前）
    files = list(OUTPUT_DIR.glob(pattern))
    files.sort(key=lambda f: f.stat().st_mtime, reverse=True)
    
    # 删除旧文件，只保留最新的 keep_latest 个
    for old_file in files[keep_latest:]:
        try:
            old_file.unlink()
            console.print(f"[dim]已删除旧报告: {old_file.name}[/dim]")
        except Exception as e:
            console.print(f"[yellow]删除旧报告失败: {old_file.name} - {e}[/yellow]")


def analyze_market():
    """执行市场综合分析（8个核心指数 + 轮动信号）"""
    from analyzers.market_analyzer import MarketAnalyzer
    from jinja2 import Template
    
    console.print("\n[bold]━━━ 市场综合分析（8个核心指数）━━━[/bold]")
    
    analyzer = MarketAnalyzer()
    result = analyzer.analyze_market()
    
    if result is None:
        console.print("[red]市场分析失败[/red]")
        return None
    
    # 显示指数表格
    table = Table(title="8个核心指数", show_header=True, header_style="bold")
    table.add_column("指数", width=10)
    table.add_column("分类", width=6)
    table.add_column("现价", justify="right", width=9)
    table.add_column("5日%", justify="right", width=8)
    table.add_column("RSI6", justify="right", width=6)
    table.add_column("牛熊", width=10)
    table.add_column("信号", width=8)
    
    for code, r in result.indices.items():
        change_color = "green" if r.change_5d >= 0 else "red"
        signal_color = "green" if r.signal_score > 0 else "red" if r.signal_score < 0 else ""
        rsi_color = "red" if r.rsi6 > 70 else "green" if r.rsi6 < 30 else ""
        
        table.add_row(
            r.name,
            r.category,
            f"{r.current_price:.2f}",
            f"[{change_color}]{r.change_5d:+.2f}%[/{change_color}]",
            f"[{rsi_color}]{r.rsi6:.0f}[/{rsi_color}]" if rsi_color else f"{r.rsi6:.0f}",
            r.bull_bear.bull_bear_status,
            f"[{signal_color}]{r.overall_signal}[/{signal_color}]" if signal_color else r.overall_signal
        )
    
    console.print(table)
    
    # 轮动信号
    console.print(f"\n[bold]市值轮动:[/bold] {result.rotation.size_signal.value}")
    console.print(f"  {result.rotation.size_signal_desc}")
    if result.rotation.size_buy_targets:
        console.print(f"  [green]买入: {', '.join(result.rotation.size_buy_targets)}[/green]")
    if result.rotation.size_sell_targets:
        console.print(f"  [red]卖出: {', '.join(result.rotation.size_sell_targets)}[/red]")
    
    console.print(f"\n[bold]风格轮动:[/bold] {result.rotation.style_signal.value}")
    console.print(f"  {result.rotation.style_signal_desc}")
    
    # 宏观数据
    console.print(f"\n[bold]宏观数据:[/bold]")
    console.print(f"  10Y国债收益率: {result.macro.bond_yield_10y}%")
    console.print(f"  PMI: {result.macro.pmi}")
    console.print(f"  北向资金(5日): {result.macro.north_money_5d:.0f}亿")
    
    # 综合结论
    score_color = "green" if result.market_score > 0 else "red" if result.market_score < 0 else "yellow"
    console.print(f"\n[bold cyan]━━━ 综合结论 ━━━[/bold cyan]")
    console.print(f"  市场信号: [{score_color}]{result.market_signal}[/{score_color}]")
    console.print(f"  综合评分: [{score_color}]{result.market_score}[/{score_color}]")
    console.print(f"  仓位建议: {result.position_suggestion}")
    
    # 建议配置
    console.print(f"\n[bold]建议配置:[/bold]")
    for name, ratio in result.rotation.recommended_allocation.items():
        console.print(f"  {name}: {ratio*100:.0f}%")
    
    # 风险提示
    if result.risk_warnings:
        console.print(f"\n[bold red]风险提示:[/bold red]")
        for warning in result.risk_warnings:
            console.print(f"  ⚠️ {warning}")
    
    # 关注重点
    if result.focus_points:
        console.print(f"\n[bold yellow]关注重点:[/bold yellow]")
        for point in result.focus_points:
            console.print(f"  • {point}")
    
    # 生成 HTML 报告
    console.print("\n[dim]正在生成市场分析报告...[/dim]")
    
    template_path = Path(__file__).parent / "templates" / "market_report.html"
    if template_path.exists():
        with open(template_path, 'r', encoding='utf-8') as f:
            template = Template(f.read())
        
        # 转换数据为字典
        data = analyzer.to_dict(result)
        html_content = template.render(**data)
        
        # 保存报告
        report_name = f"market_{datetime.now().strftime('%Y-%m-%d_%H%M%S')}.html"
        report_path = OUTPUT_DIR / report_name
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        # 清理旧的市场报告，只保留最新的1个
        cleanup_old_reports("market", keep_latest=1)
        
        console.print(f"[green]✅ 市场分析报告已生成: {report_path}[/green]")
        return str(report_path)
    else:
        console.print("[yellow]报告模板不存在，跳过 HTML 生成[/yellow]")
        return None


def analyze_index(index_code: str = "000001"):
    """执行指数多周期分析（单个指数，保留旧功能）
    
    Args:
        index_code: 指数代码，默认上证指数
    """
    from analyzers.index_analyzer import IndexAnalyzer
    from jinja2 import Template
    
    console.print("\n[bold]━━━ 单指数多周期共振分析 ━━━[/bold]")
    
    analyzer = IndexAnalyzer(index_code)
    result = analyzer.analyze()
    
    if result is None:
        console.print("[red]指数分析失败[/red]")
        return None
    
    # 显示分析结果
    console.print(f"\n[bold cyan]{result.index_name}[/bold cyan] ({result.index_code})")
    console.print(f"当前价格: [cyan]{result.current_price}[/cyan] ({result.daily_change_pct:+.2f}%)")
    
    console.print(f"\n[bold]多周期共振:[/bold]")
    console.print(f"  共振评分: {result.multi_cycle.resonance_score}")
    console.print(f"  共振类型: {result.multi_cycle.resonance_description}")
    
    console.print(f"\n[bold]综合结论:[/bold]")
    console.print(f"  综合评分: {result.overall_score}")
    console.print(f"  综合信号: {result.overall_signal}")
    
    if result.risk_factors:
        console.print(f"\n[bold red]风险因素:[/bold red]")
        for risk in result.risk_factors:
            console.print(f"  • {risk}")
    
    # 生成 HTML 报告
    console.print("\n[dim]正在生成指数分析报告...[/dim]")
    
    template_path = Path(__file__).parent / "templates" / "index_report.html"
    if template_path.exists():
        with open(template_path, 'r', encoding='utf-8') as f:
            template = Template(f.read())
        
        # 转换数据为字典
        data = analyzer.to_dict(result)
        html_content = template.render(**data)
        
        # 保存报告
        report_name = f"index_{index_code}_{datetime.now().strftime('%Y-%m-%d_%H%M%S')}.html"
        report_path = OUTPUT_DIR / report_name
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        # 清理该指数的旧报告，只保留最新的1个
        cleanup_old_reports("index", keep_latest=1, index_code=index_code)
        
        console.print(f"[green]✅ 指数分析报告已生成: {report_path}[/green]")
        return str(report_path)
    else:
        console.print("[yellow]报告模板不存在，跳过 HTML 生成[/yellow]")
        return None


def analyze_stocks(stocks: Optional[List[Dict]] = None, code: str = None, name: str = None):
    """执行个股分析
    
    Args:
        stocks: 股票列表，每个元素为字典 {"code": "601899", "name": "紫金矿业", ...}
        code: 单只股票代码（简便模式）
        name: 单只股票名称（简便模式）
    """
    from stock_analyzer import analyze_stock, analyze_stocks as batch_analyze, to_dict
    from html_report import generate_html_report
    
    console.print("\n[bold]━━━ 个股分析 ━━━[/bold]")
    
    results = []
    
    if code:
        # 分析单只股票
        result = analyze_stock(code, name or "")
        if result:
            results.append(result)
    elif stocks:
        # 批量分析
        results = batch_analyze(stocks)
    else:
        console.print("[yellow]未指定股票，请使用 --stock 参数指定[/yellow]")
        return None
    
    if not results:
        console.print("[yellow]无分析结果[/yellow]")
        return None
    
    # 生成 HTML 报告
    console.print("\n[dim]正在生成个股分析报告...[/dim]")
    
    stock_results = [to_dict(r) for r in results]
    
    report_path = generate_html_report(
        etf_results=[],
        stock_results=stock_results
    )
    
    console.print(f"[green]✅ 个股分析报告已生成: {report_path}[/green]")
    return report_path


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="多周期共振投资分析系统",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python main.py                              # 【推荐】市场综合分析（8指数+轮动）
  python main.py -m market                    # 市场综合分析
  python main.py -m index -i 000300           # 单指数分析（沪深300）
  python main.py -m stock -s 601899           # 个股分析（紫金矿业）
  python main.py -m all -s 601899             # 市场分析 + 个股分析
        """
    )
    parser.add_argument(
        "--mode", "-m",
        choices=["market", "index", "stock", "all"],
        default="market",
        help="分析模式：market=市场综合(8指数), index=单指数, stock=个股, all=全部 (默认: market)"
    )
    parser.add_argument(
        "--index", "-i",
        default="000001",
        help="指数代码（仅index模式使用），默认 000001（上证指数）"
    )
    parser.add_argument(
        "--stock", "-s",
        help="股票代码（如 601899）"
    )
    parser.add_argument(
        "--name", "-n",
        default="",
        help="股票名称（可选）"
    )
    
    args = parser.parse_args()
    
    console.print()
    console.print(Panel.fit(
        "[bold cyan]📊 多周期共振投资分析系统[/bold cyan]\n"
        f"[dim]运行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}[/dim]\n"
        "[dim]数据源: Baostock + AkShare（免费）[/dim]",
        border_style="cyan"
    ))
    
    try:
        # 市场综合分析
        if args.mode in ["market", "all"]:
            analyze_market()
        
        # 单指数分析
        if args.mode == "index":
            analyze_index(args.index)
        
        # 个股分析
        if args.mode in ["stock", "all"]:
            if args.stock:
                analyze_stocks(code=args.stock, name=args.name)
            elif args.mode == "stock":
                console.print("[yellow]请使用 --stock 参数指定股票代码[/yellow]")
                console.print("[dim]例如: python main.py -m stock -s 601899[/dim]")
        
        console.print("\n[bold green]✅ 分析完成！[/bold green]")
        
    except KeyboardInterrupt:
        console.print("\n[yellow]已取消分析[/yellow]")
    except Exception as e:
        console.print(f"\n[red]分析出错: {escape(str(e))}[/red]")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

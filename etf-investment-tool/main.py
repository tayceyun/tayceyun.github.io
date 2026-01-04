#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
投资分析主程序

功能：
1. 指数多周期共振分析（上证指数等）
2. 个股目标价分析（支持任意股票）

输出：终端显示 + HTML 报告
数据源：Baostock（免费）
"""

import argparse
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
from rich.console import Console
from rich.panel import Panel

console = Console()

# 输出目录
OUTPUT_DIR = Path(__file__).parent / "output"
OUTPUT_DIR.mkdir(exist_ok=True)


def analyze_index(index_code: str = "000001"):
    """执行指数多周期分析
    
    Args:
        index_code: 指数代码，默认上证指数
    """
    from analyzers.index_analyzer import IndexAnalyzer
    from jinja2 import Template
    
    console.print("\n[bold]━━━ 指数多周期共振分析 ━━━[/bold]")
    
    analyzer = IndexAnalyzer(index_code)
    result = analyzer.analyze()
    
    if result is None:
        console.print("[red]指数分析失败[/red]")
        return None
    
    # 显示分析结果
    console.print(f"\n[bold cyan]{result.index_name}[/bold cyan] ({result.index_code})")
    console.print(f"当前价格: [cyan]{result.current_price}[/cyan] ({result.daily_change_pct:+.2f}%)")
    
    console.print(f"\n[bold]压力线分析:[/bold]")
    console.print(f"  压力线位置: {result.pressure_line.pressure_position}")
    console.print(f"  偏离: {result.pressure_line.deviation} ({result.pressure_line.deviation_pct:+.2f}%)")
    console.print(f"  状态: {result.pressure_line.breakthrough_status}")
    
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
        report_name = f"index_{index_code}_{datetime.now().strftime('%Y-%m-%d')}.html"
        report_path = OUTPUT_DIR / report_name
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
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
  python main.py                          # 分析上证指数
  python main.py -m index -i 000300       # 分析沪深300
  python main.py -m stock -s 601899       # 分析紫金矿业
  python main.py -m stock -s 601899 -n 紫金矿业  # 分析紫金矿业（含名称）
  python main.py -m all -i 000001 -s 601899     # 分析指数和个股
        """
    )
    parser.add_argument(
        "--mode", "-m",
        choices=["all", "index", "stock"],
        default="index",
        help="分析模式：all=全部, index=仅指数, stock=仅个股 (默认: index)"
    )
    parser.add_argument(
        "--index", "-i",
        default="000001",
        help="指数代码，默认 000001（上证指数）"
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
        "[dim]数据源: Baostock（免费）[/dim]",
        border_style="cyan"
    ))
    
    try:
        if args.mode in ["all", "index"]:
            analyze_index(args.index)
        
        if args.mode in ["all", "stock"]:
            if args.stock:
                analyze_stocks(code=args.stock, name=args.name)
            elif args.mode == "stock":
                # 如果是 stock 模式但没指定股票，提示用户
                console.print("[yellow]请使用 --stock 参数指定股票代码[/yellow]")
                console.print("[dim]例如: python main.py -m stock -s 601899[/dim]")
        
        console.print("\n[bold green]✅ 分析完成！[/bold green]")
        
    except KeyboardInterrupt:
        console.print("\n[yellow]已取消分析[/yellow]")
    except Exception as e:
        console.print(f"\n[red]分析出错: {e}[/red]")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

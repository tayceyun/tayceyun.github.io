#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
个股分析工具

功能：
- 支持任意A股股票分析
- 计算目标买入价（保守/正常/激进三档）
- 技术指标分析（MACD、RSI、均线等）
- 多周期共振分析

数据源：Baostock（免费）
"""

import pandas as pd
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box

from data_source import get_stock_daily

console = Console()


# ============= 数据模型 =============

@dataclass
class StockConfig:
    """股票配置"""
    code: str           # 股票代码（6位数字）
    name: str           # 股票名称
    market: str = ""    # 市场（sh/sz，可自动判断）
    shares: int = 0     # 持仓数量（可选）
    cost: float = 0.0   # 成本价（可选）


@dataclass
class TargetLevel:
    """目标价档位"""
    label: str          # 档位名称
    price: float        # 目标价格
    deviation: float    # 偏离现价百分比
    description: str    # 说明


@dataclass
class StockAnalysisResult:
    """个股分析结果"""
    code: str
    name: str
    current_price: float
    target_levels: List[TargetLevel]
    
    # 技术指标
    ma5: float = 0.0
    ma10: float = 0.0
    ma20: float = 0.0
    ma60: float = 0.0
    rsi: float = 0.0
    macd_signal: str = ""
    
    # 持仓信息（可选）
    shares: int = 0
    cost: float = 0.0
    profit_pct: float = 0.0
    
    # 分析时间
    analysis_time: str = ""


# ============= 核心分析类 =============

class StockAnalyzer:
    """个股分析器"""
    
    def __init__(self, code: str, name: str = "", shares: int = 0, cost: float = 0.0):
        """初始化
        
        Args:
            code: 股票代码（6位数字，如 "601899"）
            name: 股票名称（可选，如不提供则显示代码）
            shares: 持仓数量（可选）
            cost: 成本价（可选）
        """
        self.code = code
        self.name = name or code
        self.shares = shares
        self.cost = cost
        self.market = self._detect_market(code)
        
    def _detect_market(self, code: str) -> str:
        """根据代码判断市场
        
        - 6开头：上海主板
        - 0开头：深圳主板
        - 3开头：创业板
        - 688开头：科创板
        """
        if code.startswith('6'):
            return 'sh'
        elif code.startswith('0') or code.startswith('3'):
            return 'sz'
        else:
            return 'sh'
    
    def calculate_target_price(self, df: pd.DataFrame) -> float:
        """计算目标中枢价格
        
        公式：MA20×40% + MA60×40% + 近60日最低点×20%
        
        Args:
            df: 日线数据 DataFrame
        
        Returns:
            目标中枢价格
        """
        if df.empty or len(df) < 60:
            return 0.0
        
        ma20 = float(df['收盘'].tail(20).mean())
        ma60 = float(df['收盘'].tail(60).mean())
        monthly_low = float(df['最低'].tail(60).min())
        
        target_price = ma20 * 0.4 + ma60 * 0.4 + monthly_low * 0.2
        return round(target_price, 3)
    
    def calculate_ma(self, df: pd.DataFrame, period: int) -> float:
        """计算均线值"""
        if df.empty or len(df) < period:
            return 0.0
        return float(df['收盘'].tail(period).mean())
    
    def calculate_rsi(self, df: pd.DataFrame, period: int = 14) -> float:
        """计算 RSI 指标"""
        if df.empty or len(df) < period + 1:
            return 50.0
        
        delta = df['收盘'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        rs = gain / loss.replace(0, float('inf'))
        rsi = 100 - (100 / (1 + rs))
        
        return float(rsi.iloc[-1]) if pd.notna(rsi.iloc[-1]) else 50.0
    
    def calculate_macd_signal(self, df: pd.DataFrame) -> str:
        """计算 MACD 信号"""
        if df.empty or len(df) < 35:
            return "数据不足"
        
        close = df['收盘']
        ema12 = close.ewm(span=12, adjust=False).mean()
        ema26 = close.ewm(span=26, adjust=False).mean()
        dif = ema12 - ema26
        dea = dif.ewm(span=9, adjust=False).mean()
        
        # 判断信号
        dif_now = dif.iloc[-1]
        dea_now = dea.iloc[-1]
        dif_prev = dif.iloc[-2]
        dea_prev = dea.iloc[-2]
        
        if dif_now > dea_now and dif_prev <= dea_prev:
            return "金叉"
        elif dif_now < dea_now and dif_prev >= dea_prev:
            return "死叉"
        elif dif_now > dea_now:
            return "多头"
        else:
            return "空头"
    
    def analyze(self) -> Optional[StockAnalysisResult]:
        """执行分析
        
        Returns:
            分析结果，如果失败返回 None
        """
        console.print(f"[dim]正在分析 {self.name} ({self.code})...[/dim]")
        
        # 获取数据
        df = get_stock_daily(self.code, days=250)
        if df.empty:
            console.print(f"[red]{self.name} 数据获取失败[/red]")
            return None
        
        current_price = float(df['收盘'].iloc[-1])
        
        # 计算技术指标
        ma5 = self.calculate_ma(df, 5)
        ma10 = self.calculate_ma(df, 10)
        ma20 = self.calculate_ma(df, 20)
        ma60 = self.calculate_ma(df, 60)
        rsi = self.calculate_rsi(df)
        macd_signal = self.calculate_macd_signal(df)
        
        # 计算目标价
        base_target = self.calculate_target_price(df)
        
        # 生成多档目标价
        target_levels = [
            TargetLevel(
                label="保守",
                price=round(base_target * 0.97, 3),
                deviation=0,
                description="小幅回调即可买入"
            ),
            TargetLevel(
                label="正常",
                price=round(base_target * 0.93, 3),
                deviation=0,
                description="标准买入位，可正常建仓"
            ),
            TargetLevel(
                label="激进",
                price=round(base_target * 0.88, 3),
                deviation=0,
                description="大跌后加仓机会"
            ),
        ]
        
        # 计算偏离现价
        for level in target_levels:
            level.deviation = round((level.price - current_price) / current_price * 100, 1)
        
        # 计算盈亏（如果有持仓信息）
        profit_pct = 0.0
        if self.cost > 0:
            profit_pct = (current_price - self.cost) / self.cost * 100
        
        # 清除加载信息
        console.print("\033[A\033[K", end="")
        
        return StockAnalysisResult(
            code=self.code,
            name=self.name,
            current_price=current_price,
            target_levels=target_levels,
            ma5=round(ma5, 3),
            ma10=round(ma10, 3),
            ma20=round(ma20, 3),
            ma60=round(ma60, 3),
            rsi=round(rsi, 1),
            macd_signal=macd_signal,
            shares=self.shares,
            cost=self.cost,
            profit_pct=round(profit_pct, 2),
            analysis_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
    
    def display_result(self, result: StockAnalysisResult):
        """在终端显示分析结果"""
        # 头部信息
        profit_str = ""
        if result.cost > 0:
            profit_color = 'green' if result.profit_pct >= 0 else 'red'
            profit_str = f"  成本: {result.cost:.2f}  盈亏: [{profit_color}]{result.profit_pct:+.1f}%[/]"
        
        shares_str = f"  持仓: {result.shares}股" if result.shares > 0 else ""
        
        console.print(Panel(
            f"[bold]{result.name}[/bold] ({result.code})\n"
            f"现价: [cyan]{result.current_price:.3f}[/cyan]{profit_str}{shares_str}",
            title=f"[bold orange1]{result.name} - 目标买入价[/bold orange1]",
            border_style="orange1",
        ))
        
        # 目标价表格
        target_table = Table(box=box.ROUNDED, show_header=True, header_style="bold")
        target_table.add_column("档位", width=10)
        target_table.add_column("目标价", justify="right", width=10)
        target_table.add_column("偏离现价", justify="right", width=12)
        target_table.add_column("说明", width=30)
        
        for level in result.target_levels:
            deviation_color = "red" if level.deviation < 0 else "green"
            target_table.add_row(
                level.label,
                f"[bold cyan]{level.price:.3f}[/bold cyan]",
                f"[{deviation_color}]{level.deviation:+.1f}%[/]",
                f"[dim]{level.description}[/dim]"
            )
        
        console.print(target_table)
        
        # 技术指标表格
        console.print()
        tech_table = Table(title="技术指标", box=box.SIMPLE, show_header=True, header_style="dim")
        tech_table.add_column("MA5", justify="right")
        tech_table.add_column("MA10", justify="right")
        tech_table.add_column("MA20", justify="right")
        tech_table.add_column("MA60", justify="right")
        tech_table.add_column("RSI", justify="right")
        tech_table.add_column("MACD", justify="center")
        
        rsi_color = "green" if result.rsi < 30 else "red" if result.rsi > 70 else ""
        macd_color = "green" if "金叉" in result.macd_signal or "多头" in result.macd_signal else "red"
        
        tech_table.add_row(
            f"{result.ma5:.3f}",
            f"{result.ma10:.3f}",
            f"{result.ma20:.3f}",
            f"{result.ma60:.3f}",
            f"[{rsi_color}]{result.rsi:.1f}[/]",
            f"[{macd_color}]{result.macd_signal}[/]"
        )
        
        console.print(tech_table)
        console.print()


# ============= 便捷函数 =============

def analyze_stock(code: str, name: str = "", shares: int = 0, cost: float = 0.0) -> Optional[StockAnalysisResult]:
    """分析单只股票
    
    Args:
        code: 股票代码
        name: 股票名称（可选）
        shares: 持仓数量（可选）
        cost: 成本价（可选）
    
    Returns:
        分析结果
    
    Example:
        >>> result = analyze_stock("601899", "紫金矿业", shares=600, cost=28.32)
    """
    analyzer = StockAnalyzer(code, name, shares, cost)
    result = analyzer.analyze()
    if result:
        analyzer.display_result(result)
    return result


def analyze_stocks(stocks: List[Dict]) -> List[StockAnalysisResult]:
    """批量分析多只股票
    
    Args:
        stocks: 股票列表，每个元素为字典 {"code": "601899", "name": "紫金矿业", ...}
    
    Returns:
        分析结果列表
    
    Example:
        >>> stocks = [
        ...     {"code": "601899", "name": "紫金矿业", "shares": 600, "cost": 28.32},
        ...     {"code": "600519", "name": "贵州茅台"},
        ... ]
        >>> results = analyze_stocks(stocks)
    """
    results = []
    for stock in stocks:
        result = analyze_stock(
            code=stock.get("code", ""),
            name=stock.get("name", ""),
            shares=stock.get("shares", 0),
            cost=stock.get("cost", 0.0)
        )
        if result:
            results.append(result)
    return results


def to_dict(result: StockAnalysisResult) -> Dict:
    """将分析结果转换为字典（用于 JSON 序列化）"""
    return {
        "code": result.code,
        "name": result.name,
        "current_price": result.current_price,
        "target_levels": [
            {
                "label": level.label,
                "price": level.price,
                "deviation": level.deviation,
                "description": level.description
            }
            for level in result.target_levels
        ],
        "ma5": result.ma5,
        "ma10": result.ma10,
        "ma20": result.ma20,
        "ma60": result.ma60,
        "rsi": result.rsi,
        "macd_signal": result.macd_signal,
        "shares": result.shares,
        "cost": result.cost,
        "profit_pct": result.profit_pct,
        "analysis_time": result.analysis_time
    }


# ============= 命令行入口 =============

def main():
    """命令行入口"""
    import argparse
    
    parser = argparse.ArgumentParser(description="个股分析工具")
    parser.add_argument(
        "code",
        nargs="?",
        help="股票代码（如 601899）"
    )
    parser.add_argument(
        "--name", "-n",
        default="",
        help="股票名称"
    )
    parser.add_argument(
        "--shares", "-s",
        type=int,
        default=0,
        help="持仓数量"
    )
    parser.add_argument(
        "--cost", "-c",
        type=float,
        default=0.0,
        help="成本价"
    )
    
    args = parser.parse_args()
    
    console.print()
    console.print(Panel.fit(
        "[bold magenta]个股分析系统[/bold magenta]\n"
        f"[dim]分析时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}[/dim]",
        border_style="magenta"
    ))
    console.print()
    
    if args.code:
        # 分析指定股票
        analyze_stock(args.code, args.name, args.shares, args.cost)
    else:
        # 交互模式
        console.print("[yellow]请输入股票代码（如 601899）：[/yellow]", end="")
        code = input().strip()
        if code:
            console.print("[yellow]请输入股票名称（可选，直接回车跳过）：[/yellow]", end="")
            name = input().strip()
            analyze_stock(code, name)
        else:
            console.print("[red]未输入股票代码[/red]")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ETF投资目标价格分析工具 (多维度版)
基于 MA20 + MA60 + 月K低点 加权计算目标买入价格
"""

# 禁用 SSL 验证（解决公司网络代理问题）
import ssl
import os
import urllib3

ssl._create_default_https_context = ssl._create_unverified_context
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
os.environ['CURL_CA_BUNDLE'] = ''
os.environ['REQUESTS_CA_BUNDLE'] = ''

import requests
from functools import partial
requests.Session.request = partial(requests.Session.request, verify=False)

import akshare as ak
import pandas as pd
from datetime import datetime, timedelta
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box

console = Console()

# ETF配置：代码、名称、单次定投金额、溢价率阈值
# 美股QDII因额度限制常年溢价，阈值设为4%；A股ETF套利完善，阈值设为0%
ETF_CONFIG = [
    {"code": "159941", "name": "纳指100ETF", "amount": 1000, "market": "sz", "premium_threshold": 4.0, "type": "QDII"},
    {"code": "513500", "name": "标普500ETF", "amount": 500, "market": "sh", "premium_threshold": 4.0, "type": "QDII"},
    {"code": "510300", "name": "沪深300ETF", "amount": 500, "market": "sh", "premium_threshold": 0.0, "type": "A股"},
    {"code": "588000", "name": "科创50ETF", "amount": 500, "market": "sh", "premium_threshold": 0.0, "type": "A股"},
]


def get_etf_premium_rate(code: str) -> float:
    """获取ETF溢价率"""
    try:
        # 尝试获取ETF实时行情（包含溢价率）
        df = ak.fund_etf_spot_em()
        if df is not None and not df.empty:
            # 查找对应ETF
            row = df[df['代码'] == code]
            if not row.empty and '折价率' in row.columns:
                # 注意：akshare返回的是折价率，需要取负值得到溢价率
                discount_rate = float(row['折价率'].iloc[0])
                return -discount_rate  # 折价率为正表示折价，取负得溢价率
        return 0.0
    except Exception:
        return 0.0  # 获取失败时返回0


def get_etf_data(code: str, market: str) -> dict:
    """获取ETF行情数据"""
    try:
        # 获取日K线数据（最近120个交易日）
        symbol = f"{market}{code}"
        df = ak.fund_etf_hist_em(symbol=code, period="daily", adjust="qfq")
        
        if df.empty:
            return None
        
        # 确保数据按日期排序
        df['日期'] = pd.to_datetime(df['日期'])
        df = df.sort_values('日期').tail(120)
        
        # 当前价格
        current_price = float(df['收盘'].iloc[-1])
        
        # 计算均线
        ma20 = float(df['收盘'].tail(20).mean())
        ma60 = float(df['收盘'].tail(60).mean())
        
        # 计算RSI (14日)
        delta = df['收盘'].diff()
        gain = (delta.where(delta > 0, 0)).tail(14).mean()
        loss = (-delta.where(delta < 0, 0)).tail(14).mean()
        if loss == 0:
            rsi = 100
        else:
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
        
        # 获取月K线数据，计算近3个月最低点
        df_monthly = ak.fund_etf_hist_em(symbol=code, period="monthly", adjust="qfq")
        if not df_monthly.empty:
            monthly_low = float(df_monthly['最低'].tail(3).min())
        else:
            monthly_low = float(df['最低'].tail(60).min())
        
        # 计算月涨跌幅
        price_20_days_ago = float(df['收盘'].iloc[-21]) if len(df) > 20 else current_price
        monthly_change = (current_price - price_20_days_ago) / price_20_days_ago * 100
        
        # 获取溢价率
        premium_rate = get_etf_premium_rate(code)
        
        return {
            "current_price": current_price,
            "ma20": ma20,
            "ma60": ma60,
            "monthly_low": monthly_low,
            "rsi": rsi,
            "monthly_change": monthly_change,
            "premium_rate": premium_rate,
        }
    except Exception as e:
        console.print(f"[red]获取 {code} 数据失败: {e}[/red]")
        return None


def calculate_target_price(data: dict, premium_threshold: float = 0.0) -> dict:
    """计算目标买入价格和建议
    
    Args:
        data: ETF行情数据
        premium_threshold: 溢价率阈值（美股QDII为4%，A股为0%）
    """
    if data is None:
        return {"target_price": 0, "advice": "数据获取失败", "signals": [], "signal_strength": 0, "premium_status": ""}
    
    current_price = data["current_price"]
    ma20 = data["ma20"]
    ma60 = data["ma60"]
    monthly_low = data["monthly_low"]
    rsi = data["rsi"]
    monthly_change = data["monthly_change"]
    premium_rate = data.get("premium_rate", 0.0)
    
    # 加权计算基准价格 (MA20:40%, MA60:40%, 月K低点:20%)
    base_price = ma20 * 0.4 + ma60 * 0.4 + monthly_low * 0.2
    
    # 根据RSI确定基础折扣
    if rsi < 30:
        discount = 0.02  # 超卖，2%折扣
    elif rsi < 50:
        discount = 0.04  # 偏弱，4%折扣
    else:
        discount = 0.06  # 正常或偏强，6%折扣
    
    # 信号收集
    signals = []
    
    # 均线趋势加成
    if current_price < ma20:
        signals.append("短期低估")
        discount -= 0.01
    if current_price < ma60:
        signals.append("中期低估")
        discount -= 0.01
    if current_price < monthly_low * 1.05:
        signals.append("接近底部")
        discount -= 0.01
    
    # 溢价率调整：超过阈值的部分，每1%增加0.5%折扣要求
    premium_excess = premium_rate - premium_threshold
    premium_adjustment = premium_excess * 0.5 / 100  # 转换为小数
    discount += premium_adjustment
    
    # 溢价状态判断
    if premium_rate < 0:
        premium_status = "折价"
        signals.append("折价机会")
    elif premium_excess <= 0:
        premium_status = "正常"
    elif premium_excess <= 2:
        premium_status = "偏高"
    else:
        premium_status = "过高"
    
    # 确保折扣在合理范围
    discount = max(0, min(discount, 0.15))
    
    target_price = base_price * (1 - discount)
    
    # 计算信号强度
    signal_strength = len(signals)
    
    # 生成买入建议
    if current_price <= target_price:
        if signal_strength >= 2:
            advice = "强烈买入"
        else:
            advice = "正常买入"
    elif current_price <= target_price * 1.05:
        advice = "减半买入"
    else:
        advice = "暂缓买入"
    
    # 溢价过高时强制调整建议
    if premium_status == "过高":
        if "强烈买入" in advice:
            advice = "正常买入"
        elif "正常买入" in advice:
            advice = "减半买入"
        elif "减半买入" in advice:
            advice = "暂缓买入"
        advice += " [溢价高]"
    
    # 折价时提升建议
    if premium_rate < -1:  # 折价超过1%
        if "暂缓买入" in advice:
            advice = "减半买入"
        elif "减半买入" in advice:
            advice = "正常买入"
        elif "正常买入" in advice:
            advice = "强烈买入"
        advice += " [折价]"
    
    # 加仓提示
    if monthly_change < -10:
        advice += " [可加仓]"
    
    return {
        "target_price": target_price,
        "advice": advice,
        "signals": signals,
        "signal_strength": signal_strength,
        "premium_status": premium_status,
    }


def analyze_all_etfs():
    """分析所有ETF并输出结果"""
    console.print()
    console.print(Panel.fit(
        f"[bold cyan]ETF投资目标价格分析 (多维度版)[/bold cyan]\n"
        f"[dim]分析时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}[/dim]",
        border_style="cyan"
    ))
    console.print()
    
    # 创建结果表格
    table = Table(
        title="",
        box=box.ROUNDED,
        show_header=True,
        header_style="bold magenta",
    )
    
    table.add_column("ETF", style="cyan", width=12)
    table.add_column("现价", justify="right", width=8)
    table.add_column("MA20", justify="right", width=8)
    table.add_column("MA60", justify="right", width=8)
    table.add_column("月K低", justify="right", width=8)
    table.add_column("RSI", justify="right", width=6)
    table.add_column("溢价率", justify="right", width=8)
    table.add_column("月涨跌", justify="right", width=8)
    table.add_column("目标价", justify="right", width=8)
    table.add_column("建议", width=18)
    
    total_amount = 0
    buy_signals = []
    
    for etf in ETF_CONFIG:
        console.print(f"[dim]正在获取 {etf['name']} 数据...[/dim]")
        data = get_etf_data(etf["code"], etf["market"])
        result = calculate_target_price(data, etf.get("premium_threshold", 0.0))
        
        if data:
            # 根据建议设置颜色
            if "强烈买入" in result["advice"]:
                advice_style = "[bold green]"
                total_amount += etf["amount"]
                buy_signals.append(f"{etf['name']}: {result['advice']}")
            elif "正常买入" in result["advice"]:
                advice_style = "[green]"
                total_amount += etf["amount"]
                buy_signals.append(f"{etf['name']}: {result['advice']}")
            elif "减半买入" in result["advice"]:
                advice_style = "[yellow]"
                total_amount += etf["amount"] // 2
                buy_signals.append(f"{etf['name']}: {result['advice']}")
            else:
                advice_style = "[red]"
            
            # 溢价率颜色
            premium_rate = data.get("premium_rate", 0.0)
            premium_threshold = etf.get("premium_threshold", 0.0)
            premium_excess = premium_rate - premium_threshold
            if premium_rate < 0:
                premium_str = f"[green]{premium_rate:.1f}%[/green]"  # 折价绿色
            elif premium_excess <= 0:
                premium_str = f"[white]{premium_rate:.1f}%[/white]"  # 正常白色
            elif premium_excess <= 2:
                premium_str = f"[yellow]{premium_rate:.1f}%[/yellow]"  # 偏高黄色
            else:
                premium_str = f"[red]{premium_rate:.1f}%[/red]"  # 过高红色
            
            # 月涨跌颜色
            monthly_change = data["monthly_change"]
            if monthly_change >= 0:
                change_str = f"[green]+{monthly_change:.1f}%[/green]"
            else:
                change_str = f"[red]{monthly_change:.1f}%[/red]"
            
            table.add_row(
                etf["name"],
                f"{data['current_price']:.3f}",
                f"{data['ma20']:.3f}",
                f"{data['ma60']:.3f}",
                f"{data['monthly_low']:.3f}",
                f"{data['rsi']:.0f}",
                premium_str,
                change_str,
                f"{result['target_price']:.3f}",
                f"{advice_style}{result['advice']}[/]",
            )
        else:
            table.add_row(
                etf["name"],
                "-", "-", "-", "-", "-", "-", "-", "-",
                "[red]数据获取失败[/red]",
            )
    
    # 清除加载信息并显示表格
    console.print("\033[A" * len(ETF_CONFIG), end="")
    console.print(" " * 50 + "\n" * len(ETF_CONFIG), end="")
    console.print("\033[A" * len(ETF_CONFIG), end="")
    
    console.print(table)
    console.print()
    
    # 投资建议汇总
    if buy_signals:
        console.print(Panel(
            f"[bold]本次建议投入: ¥{total_amount}[/bold]\n\n" +
            "\n".join(f"• {s}" for s in buy_signals),
            title="[bold green]买入信号汇总[/bold green]",
            border_style="green",
        ))
    else:
        console.print(Panel(
            "[yellow]当前无买入信号，建议观望等待更好时机[/yellow]",
            title="[bold yellow]投资建议[/bold yellow]",
            border_style="yellow",
        ))
    
    console.print()
    
    # 算法说明
    console.print(Panel(
        "[dim]目标价计算公式: 基准价 × (1 - 折扣率)\n"
        "基准价 = MA20×40% + MA60×40% + 月K低点×20%\n"
        "折扣率: RSI<30→2%, RSI<50→4%, RSI≥50→6%\n"
        "均线/底部加成: 每满足一项减1%折扣\n"
        "溢价率调整: 超过阈值部分×0.5%加入折扣\n"
        "  └ 阈值: 美股QDII=4%, A股ETF=0%[/dim]",
        title="[dim]算法说明[/dim]",
        border_style="dim",
    ))


def main():
    """主函数"""
    try:
        analyze_all_etfs()
    except KeyboardInterrupt:
        console.print("\n[yellow]已取消分析[/yellow]")
    except Exception as e:
        console.print(f"\n[red]分析出错: {e}[/red]")
        raise


if __name__ == "__main__":
    main()


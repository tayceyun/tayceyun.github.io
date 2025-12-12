#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
个股加权评分分析工具
基于9维度加权评分系统，给出加仓/减仓建议
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

# 全局禁用 SSL 验证的推荐做法：monkey patch requests.Session.__init__，让所有实例默认 verify=False
_orig_init = requests.Session.__init__
def _patched_init(self, *args, **kwargs):
    _orig_init(self, *args, **kwargs)
    self.verify = False
requests.Session.__init__ = _patched_init

import akshare as ak
import pandas as pd
import numpy as np
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box

console = Console()

# 个股配置：代码、名称、持仓数量、成本价、核心仓位比例
STOCK_CONFIG = [
    {
        "code": "000630",
        "name": "铜陵有色",
        "market": "sz",
        "shares": 5200,
        "cost": 4.250,
        "core_ratio": 0.6,  # 核心仓位60%不动
    },
    {
        "code": "601899",
        "name": "紫金矿业",
        "market": "sh",
        "shares": 600,
        "cost": 28.322,
        "core_ratio": 0.67,  # 核心仓位67%不动
    },
]

# 权重配置
WEIGHTS = {
    "ma_system": 0.25,      # 均线系统
    "rsi": 0.15,            # RSI指标
    "volume": 0.15,         # 成交量
    "cost_relation": 0.12,  # 与成本价关系
    "macd": 0.10,           # MACD
    "price_change": 0.10,   # 日/周涨跌幅
    "bollinger": 0.05,      # 布林带
    "market": 0.05,         # 大盘走势
    "sector": 0.03,         # 板块联动
}


def get_stock_data(code: str, market: str) -> dict:
    """获取个股行情数据"""
    try:
        # 获取日K线数据（最近250个交易日）
        symbol = f"{market}{code}"
        df = ak.stock_zh_a_hist(symbol=code, period="daily", adjust="qfq")
        
        if df.empty:
            return None
        
        # 确保数据按日期排序
        df['日期'] = pd.to_datetime(df['日期'])
        df = df.sort_values('日期').tail(250)
        
        # 当前价格
        current_price = float(df['收盘'].iloc[-1])
        
        # 计算均线
        ma5 = float(df['收盘'].tail(5).mean())
        ma30 = float(df['收盘'].tail(30).mean())
        ma60 = float(df['收盘'].tail(60).mean())
        ma120 = float(df['收盘'].tail(120).mean()) if len(df) >= 120 else ma60
        
        # 计算RSI (14日)
        delta = df['收盘'].diff()
        gain = (delta.where(delta > 0, 0)).tail(14).mean()
        loss = (-delta.where(delta < 0, 0)).tail(14).mean()
        if loss == 0:
            rsi = 100
        else:
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
        
        # 计算成交量变化
        vol_5 = df['成交量'].tail(5).mean()
        vol_20 = df['成交量'].tail(20).mean()
        vol_ratio = vol_5 / vol_20 if vol_20 > 0 else 1
        
        # 计算MACD
        exp12 = df['收盘'].ewm(span=12, adjust=False).mean()
        exp26 = df['收盘'].ewm(span=26, adjust=False).mean()
        dif = exp12 - exp26
        dea = dif.ewm(span=9, adjust=False).mean()
        macd = (dif - dea) * 2
        
        current_dif = float(dif.iloc[-1])
        current_dea = float(dea.iloc[-1])
        prev_dif = float(dif.iloc[-2])
        prev_dea = float(dea.iloc[-2])
        
        # 判断金叉死叉
        if prev_dif <= prev_dea and current_dif > current_dea:
            macd_cross = "golden"  # 金叉
        elif prev_dif >= prev_dea and current_dif < current_dea:
            macd_cross = "death"  # 死叉
        else:
            macd_cross = "none"
        
        # 计算布林带
        ma20 = df['收盘'].tail(20).mean()
        std20 = df['收盘'].tail(20).std()
        boll_upper = ma20 + 2 * std20
        boll_lower = ma20 - 2 * std20
        
        # 计算日涨跌幅
        daily_change = (current_price - float(df['收盘'].iloc[-2])) / float(df['收盘'].iloc[-2]) * 100
        
        # 计算周涨跌幅
        price_5_days_ago = float(df['收盘'].iloc[-6]) if len(df) > 5 else current_price
        weekly_change = (current_price - price_5_days_ago) / price_5_days_ago * 100
        
        # 计算月涨跌幅
        price_20_days_ago = float(df['收盘'].iloc[-21]) if len(df) > 20 else current_price
        monthly_change = (current_price - price_20_days_ago) / price_20_days_ago * 100
        
        return {
            "current_price": current_price,
            "ma5": ma5,
            "ma30": ma30,
            "ma60": ma60,
            "ma120": ma120,
            "rsi": rsi,
            "vol_ratio": vol_ratio,
            "dif": current_dif,
            "dea": current_dea,
            "macd_cross": macd_cross,
            "boll_upper": float(boll_upper),
            "boll_lower": float(boll_lower),
            "boll_mid": float(ma20),
            "daily_change": daily_change,
            "weekly_change": weekly_change,
            "monthly_change": monthly_change,
        }
    except Exception as e:
        console.print(f"[red]获取 {code} 数据失败: {e}[/red]")
        return None


def get_market_sentiment() -> float:
    """获取大盘走势得分"""
    try:
        # 获取上证指数数据
        df = ak.stock_zh_index_daily(symbol="sh000001")
        if df.empty:
            return 0
        
        df = df.tail(10)
        current = float(df['close'].iloc[-1])
        prev_5 = float(df['close'].iloc[-6]) if len(df) > 5 else current
        
        change = (current - prev_5) / prev_5 * 100
        
        if change < -5:
            return -5  # 大盘暴跌
        elif change < -2:
            return -2
        elif change < 2:
            return 0  # 震荡
        elif change < 5:
            return 2
        else:
            return 5  # 大盘大涨
    except:
        return 0


def calculate_dimension_scores(data: dict, cost: float, current_price: float) -> dict:
    """计算各维度得分"""
    scores = {}
    
    if data is None:
        return {dim: 0 for dim in WEIGHTS.keys()}
    
    # 1. 均线系统得分 (-10 to +10)
    ma5, ma30, ma60 = data["ma5"], data["ma30"], data["ma60"]
    if current_price < ma60 and ma5 < ma30 < ma60:
        scores["ma_system"] = 10  # 空头排列，超跌
    elif current_price < ma60:
        scores["ma_system"] = 7
    elif current_price < ma30:
        scores["ma_system"] = 4
    elif current_price < ma5:
        scores["ma_system"] = 2
    elif current_price < ma5 * 1.03:
        scores["ma_system"] = 0
    elif current_price < ma5 * 1.05:
        scores["ma_system"] = -2
    elif current_price < ma30 * 1.10:
        scores["ma_system"] = -5
    elif current_price < ma60 * 1.15:
        scores["ma_system"] = -7
    else:
        scores["ma_system"] = -10  # 严重超涨
    
    # 2. RSI得分 (-10 to +10)
    rsi = data["rsi"]
    if rsi < 20:
        scores["rsi"] = 10
    elif rsi < 30:
        scores["rsi"] = 7
    elif rsi < 40:
        scores["rsi"] = 4
    elif rsi < 60:
        scores["rsi"] = 0
    elif rsi < 70:
        scores["rsi"] = -4
    elif rsi < 80:
        scores["rsi"] = -7
    else:
        scores["rsi"] = -10
    
    # 3. 成交量得分 (-8 to +8)
    vol_ratio = data["vol_ratio"]
    daily_change = data["daily_change"]
    
    if vol_ratio < 0.7 and daily_change < 0:
        scores["volume"] = 8  # 缩量下跌，抛压枯竭
    elif vol_ratio < 0.8:
        scores["volume"] = 4
    elif vol_ratio < 1.2:
        scores["volume"] = 0
    elif vol_ratio < 1.5 and daily_change > 0:
        scores["volume"] = -2  # 放量上涨
    elif vol_ratio >= 1.5 and daily_change < 0:
        scores["volume"] = -3  # 放量下跌，恐慌
    else:
        scores["volume"] = -5
    
    # 4. 与成本价关系得分 (-9 to +10)
    profit_pct = (current_price - cost) / cost * 100
    if profit_pct < -25:
        scores["cost_relation"] = 10
    elif profit_pct < -15:
        scores["cost_relation"] = 7
    elif profit_pct < -5:
        scores["cost_relation"] = 4
    elif profit_pct < 5:
        scores["cost_relation"] = 0
    elif profit_pct < 15:
        scores["cost_relation"] = -3
    elif profit_pct < 30:
        scores["cost_relation"] = -6
    else:
        scores["cost_relation"] = -9
    
    # 5. MACD得分 (-10 to +10)
    if data["macd_cross"] == "golden":
        scores["macd"] = 8
    elif data["macd_cross"] == "death":
        scores["macd"] = -8
    elif data["dif"] > data["dea"] and data["dif"] > 0:
        scores["macd"] = 3
    elif data["dif"] > data["dea"]:
        scores["macd"] = 1
    elif data["dif"] < data["dea"] and data["dif"] < 0:
        scores["macd"] = -3
    else:
        scores["macd"] = -1
    
    # 6. 日/周涨跌幅得分 (-10 to +10)
    weekly_change = data["weekly_change"]
    daily_change = data["daily_change"]
    
    if weekly_change < -12:
        scores["price_change"] = 10
    elif weekly_change < -8:
        scores["price_change"] = 7
    elif daily_change < -5:
        scores["price_change"] = 5
    elif abs(weekly_change) < 3:
        scores["price_change"] = 0
    elif daily_change > 5:
        scores["price_change"] = -5
    elif weekly_change > 10:
        scores["price_change"] = -8
    elif weekly_change > 15:
        scores["price_change"] = -10
    else:
        scores["price_change"] = -2 if weekly_change > 0 else 2
    
    # 7. 布林带得分 (-5 to +5)
    boll_upper, boll_lower, boll_mid = data["boll_upper"], data["boll_lower"], data["boll_mid"]
    if current_price <= boll_lower:
        scores["bollinger"] = 5
    elif current_price < boll_mid:
        scores["bollinger"] = 2
    elif current_price < boll_upper:
        scores["bollinger"] = -2
    else:
        scores["bollinger"] = -5
    
    # 8. 大盘走势得分
    scores["market"] = get_market_sentiment()
    
    # 9. 板块联动（简化：有色/矿业板块）- 暂用0
    scores["sector"] = 0
    
    return scores


def calculate_weighted_score(scores: dict) -> float:
    """计算加权总分"""
    total = 0
    for dim, weight in WEIGHTS.items():
        total += scores.get(dim, 0) * weight
    return total


def get_advice(weighted_score: float, profit_pct: float) -> tuple:
    """根据加权得分给出操作建议"""
    if weighted_score >= 5.0:
        return "🟢 大力加仓", "可用资金的40%", "bold green"
    elif weighted_score >= 3.0:
        return "🟢 正常加仓", "可用资金的25%", "green"
    elif weighted_score >= 1.5:
        return "🟡 小仓加仓", "可用资金的15%", "yellow"
    elif weighted_score >= -1.5:
        return "⚪ 持有观望", "不操作", "white"
    elif weighted_score >= -3.0:
        return "🟡 小仓减仓", "机动仓位的15%", "yellow"
    elif weighted_score >= -5.0:
        return "🟠 正常减仓", "机动仓位的25%", "dark_orange"
    else:
        return "🔴 大力减仓", "机动仓位的40%", "red"


def analyze_all_stocks():
    """分析所有个股并输出结果"""
    console.print()
    console.print(Panel.fit(
        f"[bold magenta]个股加权评分分析系统[/bold magenta]\n"
        f"[dim]分析时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}[/dim]",
        border_style="magenta"
    ))
    console.print()
    
    for stock in STOCK_CONFIG:
        console.print(f"[dim]正在分析 {stock['name']}...[/dim]")
        data = get_stock_data(stock["code"], stock["market"])
        
        if data is None:
            console.print(f"[red]{stock['name']} 数据获取失败[/red]")
            continue
        
        current_price = data["current_price"]
        cost = stock["cost"]
        profit_pct = (current_price - cost) / cost * 100
        
        # 计算各维度得分
        scores = calculate_dimension_scores(data, cost, current_price)
        weighted_score = calculate_weighted_score(scores)
        advice, amount, color = get_advice(weighted_score, profit_pct)
        
        # 清除加载信息
        console.print("\033[A\033[K", end="")
        
        # 创建股票信息面板
        console.print(Panel(
            f"[bold]{stock['name']}[/bold] ({stock['code']})\n"
            f"现价: [cyan]{current_price:.3f}[/cyan]  "
            f"成本: {cost:.3f}  "
            f"盈亏: [{'green' if profit_pct >= 0 else 'red'}]{profit_pct:+.2f}%[/]  "
            f"持仓: {stock['shares']}股",
            title=f"[bold]股票信息[/bold]",
            border_style="cyan",
        ))
        
        # 创建技术指标表格
        tech_table = Table(box=box.SIMPLE, show_header=False, padding=(0, 2))
        tech_table.add_column("指标", style="dim")
        tech_table.add_column("数值", justify="right")
        tech_table.add_column("指标", style="dim")
        tech_table.add_column("数值", justify="right")
        
        tech_table.add_row(
            "MA5", f"{data['ma5']:.3f}",
            "MA30", f"{data['ma30']:.3f}",
        )
        tech_table.add_row(
            "MA60", f"{data['ma60']:.3f}",
            "MA120", f"{data['ma120']:.3f}",
        )
        tech_table.add_row(
            "RSI", f"{data['rsi']:.1f}",
            "量比", f"{data['vol_ratio']:.2f}",
        )
        tech_table.add_row(
            "日涨跌", f"{data['daily_change']:+.2f}%",
            "周涨跌", f"{data['weekly_change']:+.2f}%",
        )
        tech_table.add_row(
            "布林上", f"{data['boll_upper']:.3f}",
            "布林下", f"{data['boll_lower']:.3f}",
        )
        
        console.print(tech_table)
        
        # 创建评分表格
        score_table = Table(
            title="[bold]9维度加权评分[/bold]",
            box=box.ROUNDED,
            show_header=True,
            header_style="bold",
        )
        score_table.add_column("维度", width=14)
        score_table.add_column("得分", justify="center", width=8)
        score_table.add_column("权重", justify="center", width=8)
        score_table.add_column("加权分", justify="center", width=10)
        
        dim_names = {
            "ma_system": "均线系统",
            "rsi": "RSI指标",
            "volume": "成交量",
            "cost_relation": "成本关系",
            "macd": "MACD",
            "price_change": "涨跌幅",
            "bollinger": "布林带",
            "market": "大盘走势",
            "sector": "板块联动",
        }
        
        for dim, weight in WEIGHTS.items():
            score = scores.get(dim, 0)
            weighted = score * weight
            score_color = "green" if score > 0 else ("red" if score < 0 else "white")
            score_table.add_row(
                dim_names[dim],
                f"[{score_color}]{score:+.1f}[/]",
                f"{weight*100:.0f}%",
                f"[{score_color}]{weighted:+.2f}[/]",
            )
        
        score_table.add_row(
            "[bold]总分[/bold]",
            "",
            "[bold]100%[/bold]",
            f"[bold {color}]{weighted_score:+.2f}[/]",
            style="bold",
        )
        
        console.print(score_table)
        
        # 操作建议
        core_shares = int(stock["shares"] * stock["core_ratio"])
        mobile_shares = stock["shares"] - core_shares
        
        console.print(Panel(
            f"[bold {color}]{advice}[/bold {color}]\n\n"
            f"建议操作量: {amount}\n"
            f"核心仓位: {core_shares}股 (不动)\n"
            f"机动仓位: {mobile_shares}股 (可操作)",
            title="[bold]操作建议[/bold]",
            border_style=color,
        ))
        
        console.print()


def main():
    """主函数"""
    try:
        analyze_all_stocks()
    except KeyboardInterrupt:
        console.print("\n[yellow]已取消分析[/yellow]")
    except Exception as e:
        console.print(f"\n[red]分析出错: {e}[/red]")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()


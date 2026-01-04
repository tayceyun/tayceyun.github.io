#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
市场综合分析器

功能：
1. 分析8个核心指数的多周期共振
2. 计算牛熊分界线状态
3. 执行轮动分析
4. 生成综合市场报告

指数分类：
- 大盘：上证指数(000001)、沪深300(000300)、上证50(000016)
- 中盘：中证500(000905)
- 小盘：中证1000(000852)、国证2000(399303)
- 成长：创业板指(399006)、科创50(000688)
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
import pandas as pd

# 添加项目根目录到路径
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from indicators.tech_indicators import (
    TechIndicators, TechIndicatorsSummary, SignalType,
    MultiPeriodRSI, BullBearLine
)
from analyzers.rotation_analyzer import (
    RotationAnalyzer, RotationResult, RotationSignal
)
from data.macro_data import get_macro_fetcher, MacroData, IndexValuation


@dataclass
class IndexAnalysisResult:
    """单个指数分析结果"""
    code: str                           # 指数代码
    name: str                           # 指数名称
    category: str                       # 分类（大盘/中盘/小盘/成长）
    
    current_price: float                # 当前价格
    change_1d: float                    # 1日涨跌幅
    change_5d: float                    # 5日涨跌幅
    change_10d: float                   # 10日涨跌幅
    change_20d: float                   # 20日涨跌幅
    
    # 多周期分析
    daily_signal: SignalType            # 日线信号
    daily_desc: str                     # 日线描述
    weekly_signal: SignalType           # 周线信号
    weekly_desc: str                    # 周线描述
    monthly_signal: SignalType          # 月线信号
    monthly_desc: str                   # 月线描述
    yearly_signal: SignalType           # 年线信号（基于长周期判断）
    yearly_desc: str                    # 年线描述
    
    # RSI多周期
    rsi6: float
    rsi12: float
    rsi24: float
    rsi_status: str
    
    # 牛熊分界线
    bull_bear: BullBearLine
    
    # 估值数据（如果有）
    valuation: Optional[IndexValuation] = None
    
    # 综合评分
    signal_score: int = 0
    overall_signal: str = "中性"


@dataclass
class MarketAnalysisResult:
    """市场综合分析结果"""
    analysis_time: str
    
    # 各指数分析结果
    indices: Dict[str, IndexAnalysisResult]
    
    # 轮动分析
    rotation: RotationResult
    
    # 宏观数据
    macro: MacroData
    
    # 综合信号
    market_signal: str                  # 市场整体信号
    market_score: int                   # 市场综合评分 (-10 到 +10)
    position_suggestion: str            # 仓位建议
    
    # 风险提示
    risk_warnings: List[str]
    
    # 关注重点
    focus_points: List[str]


class MarketAnalyzer:
    """市场综合分析器"""
    
    # 8个核心指数配置
    INDEX_CONFIG = {
        "000001": {"name": "上证指数", "category": "大盘", "market": "sh"},
        "000300": {"name": "沪深300", "category": "大盘", "market": "sh"},
        "000016": {"name": "上证50", "category": "大盘", "market": "sh"},
        "000905": {"name": "中证500", "category": "中盘", "market": "sh"},
        "000852": {"name": "中证1000", "category": "小盘", "market": "sh"},
        "399303": {"name": "国证2000", "category": "小盘", "market": "sz"},
        "399006": {"name": "创业板指", "category": "成长", "market": "sz"},
        "000688": {"name": "科创50", "category": "成长", "market": "sh"},
    }
    
    def __init__(self):
        self.tech_indicators = TechIndicators()
        self.rotation_analyzer = RotationAnalyzer()
        self.macro_fetcher = get_macro_fetcher()
        
        # 数据缓存
        self._index_data: Dict[str, Dict[str, pd.DataFrame]] = {}
    
    def load_index_data(self, index_code: str, days: int = 500) -> bool:
        """加载单个指数的数据
        
        Args:
            index_code: 指数代码
            days: 加载天数
        
        Returns:
            是否成功
        """
        try:
            from data_source import get_index_daily
            
            config = self.INDEX_CONFIG.get(index_code)
            if not config:
                print(f"[警告] 不支持的指数: {index_code}")
                return False
            
            print(f"[数据加载] 获取 {config['name']} ({index_code}) 数据...")
            
            # 获取日线数据
            daily_df = get_index_daily(index_code, days=days)
            
            if daily_df.empty:
                print(f"[警告] 无法获取 {config['name']} 数据")
                return False
            
            # 聚合周线和月线
            weekly_df = self._aggregate_to_weekly(daily_df)
            monthly_df = self._aggregate_to_monthly(daily_df)
            
            self._index_data[index_code] = {
                "daily": daily_df,
                "weekly": weekly_df,
                "monthly": monthly_df,
            }
            
            print(f"[数据加载] {config['name']}: 日线{len(daily_df)}条, 周线{len(weekly_df)}条, 月线{len(monthly_df)}条")
            return True
            
        except Exception as e:
            print(f"[错误] 加载 {index_code} 数据失败: {e}")
            return False
    
    def _aggregate_to_weekly(self, df: pd.DataFrame) -> pd.DataFrame:
        """聚合为周线数据"""
        if df.empty:
            return df
        
        df = df.copy()
        df['周'] = df['日期'].dt.to_period('W')
        
        return df.groupby('周').agg({
            '日期': 'last',
            '开盘': 'first',
            '最高': 'max',
            '最低': 'min',
            '收盘': 'last',
            '成交量': 'sum'
        }).reset_index(drop=True)
    
    def _aggregate_to_monthly(self, df: pd.DataFrame) -> pd.DataFrame:
        """聚合为月线数据"""
        if df.empty:
            return df
        
        df = df.copy()
        df['月'] = df['日期'].dt.to_period('M')
        
        return df.groupby('月').agg({
            '日期': 'last',
            '开盘': 'first',
            '最高': 'max',
            '最低': 'min',
            '收盘': 'last',
            '成交量': 'sum'
        }).reset_index(drop=True)
    
    def analyze_index(self, index_code: str) -> Optional[IndexAnalysisResult]:
        """分析单个指数
        
        Args:
            index_code: 指数代码
        
        Returns:
            IndexAnalysisResult 或 None
        """
        if index_code not in self._index_data:
            if not self.load_index_data(index_code):
                return None
        
        data = self._index_data[index_code]
        config = self.INDEX_CONFIG[index_code]
        
        daily_df = data["daily"]
        weekly_df = data["weekly"]
        monthly_df = data["monthly"]
        
        if daily_df.empty or len(daily_df) < 60:
            return None
        
        try:
            # 计算技术指标（日线）
            daily_indicators = self.tech_indicators.calculate_all(daily_df, weekly_df=weekly_df)
            
            # 计算周线指标（周线数据通常较少，降低要求）
            weekly_indicators = None
            if len(weekly_df) >= 60:
                try:
                    weekly_indicators = self.tech_indicators.calculate_all(weekly_df)
                except ValueError:
                    pass  # 数据不足，跳过
            
            # 计算月线指标（月线数据通常很少，跳过）
            monthly_indicators = None
            # 月线数据通常只有20-30条，不够计算完整指标，跳过
            
            # 获取价格和涨跌幅
            current_price = float(daily_df['收盘'].iloc[-1])
            
            def calc_change(days: int) -> float:
                if len(daily_df) > days:
                    prev = float(daily_df['收盘'].iloc[-days-1])
                    return (current_price - prev) / prev * 100
                return 0.0
            
            change_1d = calc_change(1)
            change_5d = calc_change(5)
            change_10d = calc_change(10)
            change_20d = calc_change(20)
            
            # 生成各周期描述
            daily_desc = self._generate_cycle_desc(daily_indicators, "日线")
            weekly_desc = self._generate_cycle_desc(weekly_indicators, "周线") if weekly_indicators else "数据不足"
            monthly_desc = self._generate_cycle_desc(monthly_indicators, "月线") if monthly_indicators else "数据不足"
            
            # 年线描述（基于牛熊分界线）
            yearly_desc = self._generate_yearly_desc(daily_indicators.bull_bear)
            yearly_signal = daily_indicators.bull_bear.signal
            
            # 获取估值数据
            valuation = self.macro_fetcher.get_index_valuation(index_code)
            
            # 综合信号
            overall_signal = self._determine_overall_signal(daily_indicators.signal_score)
            
            return IndexAnalysisResult(
                code=index_code,
                name=config["name"],
                category=config["category"],
                current_price=round(current_price, 2),
                change_1d=round(change_1d, 2),
                change_5d=round(change_5d, 2),
                change_10d=round(change_10d, 2),
                change_20d=round(change_20d, 2),
                daily_signal=daily_indicators.overall_signal,
                daily_desc=daily_desc,
                weekly_signal=weekly_indicators.overall_signal if weekly_indicators else SignalType.NEUTRAL,
                weekly_desc=weekly_desc,
                monthly_signal=monthly_indicators.overall_signal if monthly_indicators else SignalType.NEUTRAL,
                monthly_desc=monthly_desc,
                yearly_signal=yearly_signal,
                yearly_desc=yearly_desc,
                rsi6=daily_indicators.multi_rsi.rsi6,
                rsi12=daily_indicators.multi_rsi.rsi12,
                rsi24=daily_indicators.multi_rsi.rsi24,
                rsi_status=daily_indicators.multi_rsi.status,
                bull_bear=daily_indicators.bull_bear,
                valuation=valuation,
                signal_score=daily_indicators.signal_score,
                overall_signal=overall_signal,
            )
            
        except Exception as e:
            print(f"[错误] 分析 {config['name']} 失败: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _generate_cycle_desc(self, indicators: TechIndicatorsSummary, cycle: str) -> str:
        """生成周期描述"""
        if indicators is None:
            return "数据不足"
        
        parts = []
        
        # MACD
        if indicators.macd.cross == 'golden':
            parts.append("MACD金叉")
        elif indicators.macd.cross == 'death':
            parts.append("MACD死叉")
        elif indicators.macd.position == 'above_zero':
            parts.append("MACD零轴上方")
        else:
            parts.append("MACD零轴下方")
        
        # RSI（使用多周期RSI的RSI6）
        if indicators.multi_rsi:
            if indicators.multi_rsi.status == 'overbought':
                parts.append(f"RSI超买({indicators.multi_rsi.rsi6:.0f})")
            elif indicators.multi_rsi.status == 'oversold':
                parts.append(f"RSI超卖({indicators.multi_rsi.rsi6:.0f})")
        
        # 均线
        if indicators.ma.arrangement == 'bull':
            parts.append("均线多头")
        elif indicators.ma.arrangement == 'bear':
            parts.append("均线空头")
        
        # K线形态
        if indicators.kline.consecutive_yang >= 5:
            parts.append(f"{indicators.kline.consecutive_yang}连阳")
        elif indicators.kline.consecutive_yin >= 5:
            parts.append(f"{indicators.kline.consecutive_yin}连阴")
        
        return "，".join(parts) if parts else "无明显信号"
    
    def _generate_yearly_desc(self, bull_bear: BullBearLine) -> str:
        """生成年线描述"""
        parts = []
        
        if bull_bear.above_ma250:
            parts.append(f"站上年线({bull_bear.ma250:.0f})")
        else:
            parts.append(f"跌破年线({bull_bear.ma250:.0f})")
        
        if bull_bear.above_ma60:
            parts.append("站上季线")
        else:
            parts.append("跌破季线")
        
        if bull_bear.above_ma30w:
            parts.append("站上30周线")
        else:
            parts.append("跌破30周线")
        
        status_map = {
            'strong_bull': '强势多头',
            'bull': '多头',
            'neutral': '震荡',
            'bear': '空头',
            'strong_bear': '强势空头'
        }
        parts.append(f"【{status_map.get(bull_bear.bull_bear_status, '未知')}】")
        
        return "，".join(parts)
    
    def _determine_overall_signal(self, score: int) -> str:
        """确定综合信号"""
        if score >= 6:
            return "强多头"
        elif score >= 3:
            return "多头"
        elif score >= 1:
            return "偏多"
        elif score >= -1:
            return "中性"
        elif score >= -3:
            return "偏空"
        elif score >= -6:
            return "空头"
        else:
            return "强空头"
    
    def analyze_market(self) -> Optional[MarketAnalysisResult]:
        """执行完整的市场分析
        
        Returns:
            MarketAnalysisResult 或 None
        """
        print("\n[市场分析] 开始分析8个核心指数...")
        
        # 分析所有指数
        indices_results: Dict[str, IndexAnalysisResult] = {}
        
        for code in self.INDEX_CONFIG.keys():
            result = self.analyze_index(code)
            if result:
                indices_results[code] = result
                
                # 设置轮动分析器的数据
                self.rotation_analyzer.set_index_data(code, {
                    "current_price": result.current_price,
                    "change_5d": result.change_5d,
                    "change_10d": result.change_10d,
                    "change_20d": result.change_20d,
                    "rsi6": result.rsi6,
                    "bull_bear_status": result.bull_bear.bull_bear_status,
                    "above_ma60": result.bull_bear.above_ma60,
                    "above_ma250": result.bull_bear.above_ma250,
                })
        
        if not indices_results:
            print("[错误] 无法获取任何指数数据")
            return None
        
        # 获取宏观数据
        macro = self.macro_fetcher.get_all_macro_data()
        
        # 准备轮动分析的宏观数据
        rotation_macro = {
            "bond_yield": macro.bond_yield_10y,
            "pmi": macro.pmi,
            "north_money_5d": macro.north_money_5d,
        }
        
        # 计算PE分位差
        val_300 = self.macro_fetcher.get_index_valuation("000300")
        val_1000 = self.macro_fetcher.get_index_valuation("000852")
        val_cyb = self.macro_fetcher.get_index_valuation("399006")
        
        if val_300 and val_1000:
            rotation_macro["pe_diff_small_large"] = val_1000.pe_percentile - val_300.pe_percentile
        if val_300 and val_cyb:
            rotation_macro["pe_diff_growth_value"] = val_cyb.pe_percentile - val_300.pe_percentile
            rotation_macro["growth_rsi"] = indices_results.get("399006", {})
            if "399006" in indices_results:
                rotation_macro["growth_rsi"] = indices_results["399006"].rsi6
        
        # 执行轮动分析
        rotation_result = self.rotation_analyzer.analyze(rotation_macro)
        
        # 计算市场综合评分
        scores = [r.signal_score for r in indices_results.values()]
        market_score = sum(scores) // len(scores) if scores else 0
        
        # 生成市场信号
        market_signal = self._determine_market_signal(market_score, rotation_result)
        
        # 生成仓位建议
        position_suggestion = self._generate_position_suggestion(market_score, rotation_result)
        
        # 收集风险提示
        risk_warnings = list(rotation_result.risk_warnings)
        
        # 添加额外风险检查
        overbought_count = sum(1 for r in indices_results.values() if r.rsi_status == 'overbought')
        if overbought_count >= 4:
            risk_warnings.append(f"{overbought_count}个指数RSI超买，短期回调风险增加")
        
        oversold_count = sum(1 for r in indices_results.values() if r.rsi_status == 'oversold')
        if oversold_count >= 4:
            risk_warnings.append(f"{oversold_count}个指数RSI超卖，可能出现技术反弹")
        
        # 关注重点
        focus_points = self._identify_focus_points(indices_results, rotation_result, macro)
        
        return MarketAnalysisResult(
            analysis_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            indices=indices_results,
            rotation=rotation_result,
            macro=macro,
            market_signal=market_signal,
            market_score=market_score,
            position_suggestion=position_suggestion,
            risk_warnings=risk_warnings,
            focus_points=focus_points,
        )
    
    def _determine_market_signal(self, score: int, rotation: RotationResult) -> str:
        """确定市场整体信号"""
        if rotation.risk_warnings:
            return "谨慎"
        
        if score >= 5:
            return "强势上涨"
        elif score >= 2:
            return "温和上涨"
        elif score >= -2:
            return "震荡整理"
        elif score >= -5:
            return "温和下跌"
        else:
            return "强势下跌"
    
    def _generate_position_suggestion(self, score: int, rotation: RotationResult) -> str:
        """生成仓位建议"""
        if rotation.risk_warnings:
            return "建议仓位30%-40%，控制风险"
        
        if score >= 5:
            return "建议仓位70%-80%，积极参与"
        elif score >= 2:
            return "建议仓位50%-60%，适度乐观"
        elif score >= -2:
            return "建议仓位30%-50%，灵活应对"
        elif score >= -5:
            return "建议仓位20%-30%，防守为主"
        else:
            return "建议仓位10%-20%，规避风险"
    
    def _identify_focus_points(self, indices: Dict[str, IndexAnalysisResult],
                                rotation: RotationResult,
                                macro: MacroData) -> List[str]:
        """识别关注重点"""
        points = []
        
        # 轮动信号
        if rotation.size_signal != RotationSignal.HOLD_BALANCE:
            points.append(f"市值轮动：{rotation.size_signal.value}")
        if rotation.style_signal != RotationSignal.HOLD_BALANCE:
            points.append(f"风格轮动：{rotation.style_signal.value}")
        
        # 北向资金
        if macro.north_money_5d > 100:
            points.append(f"北向资金5日净流入{macro.north_money_5d:.0f}亿，资金情绪乐观")
        elif macro.north_money_5d < -50:
            points.append(f"北向资金5日净流出{abs(macro.north_money_5d):.0f}亿，注意资金撤离")
        
        # 牛熊线附近的指数
        for code, result in indices.items():
            bb = result.bull_bear
            # 刚站上年线
            if bb.above_ma250 and bb.price < bb.ma250 * 1.03:
                points.append(f"{result.name}刚站上年线，关注能否有效突破")
            # 刚跌破年线
            if not bb.above_ma250 and bb.price > bb.ma250 * 0.97:
                points.append(f"{result.name}刚跌破年线，关注能否企稳")
        
        return points[:5]  # 最多返回5个重点
    
    def to_dict(self, result: MarketAnalysisResult) -> Dict[str, Any]:
        """转换为字典（用于报告生成）"""
        def index_to_dict(r: IndexAnalysisResult) -> Dict:
            return {
                "code": r.code,
                "name": r.name,
                "category": r.category,
                "current_price": r.current_price,
                "change_1d": r.change_1d,
                "change_5d": r.change_5d,
                "change_10d": r.change_10d,
                "change_20d": r.change_20d,
                "daily_signal": r.daily_signal.name,
                "daily_desc": r.daily_desc,
                "weekly_signal": r.weekly_signal.name,
                "weekly_desc": r.weekly_desc,
                "monthly_signal": r.monthly_signal.name,
                "monthly_desc": r.monthly_desc,
                "yearly_signal": r.yearly_signal.name,
                "yearly_desc": r.yearly_desc,
                "rsi6": r.rsi6,
                "rsi12": r.rsi12,
                "rsi24": r.rsi24,
                "rsi_status": r.rsi_status,
                "bull_bear": {
                    "ma60": r.bull_bear.ma60,
                    "ma250": r.bull_bear.ma250,
                    "ma30w": r.bull_bear.ma30w,
                    "above_ma60": r.bull_bear.above_ma60,
                    "above_ma250": r.bull_bear.above_ma250,
                    "above_ma30w": r.bull_bear.above_ma30w,
                    "status": r.bull_bear.bull_bear_status,
                },
                "valuation": {
                    "pe": r.valuation.pe if r.valuation else None,
                    "pe_percentile": r.valuation.pe_percentile if r.valuation else None,
                    "pb": r.valuation.pb if r.valuation else None,
                    "pb_percentile": r.valuation.pb_percentile if r.valuation else None,
                } if r.valuation else None,
                "signal_score": r.signal_score,
                "overall_signal": r.overall_signal,
            }
        
        return {
            "analysis_time": result.analysis_time,
            "indices": {code: index_to_dict(r) for code, r in result.indices.items()},
            "rotation": {
                "size_signal": result.rotation.size_signal.value,
                "size_desc": result.rotation.size_signal_desc,
                "size_buy": result.rotation.size_buy_targets,
                "size_sell": result.rotation.size_sell_targets,
                "style_signal": result.rotation.style_signal.value,
                "style_desc": result.rotation.style_signal_desc,
                "style_buy": result.rotation.style_buy_targets,
                "style_sell": result.rotation.style_sell_targets,
                "overall": result.rotation.overall_signal,
                "allocation": result.rotation.recommended_allocation,
            },
            "macro": {
                "date": result.macro.date,
                "bond_yield_10y": result.macro.bond_yield_10y,
                "pmi": result.macro.pmi,
                "north_money_5d": result.macro.north_money_5d,
                "north_money_today": result.macro.north_money_today,
            },
            "market_signal": result.market_signal,
            "market_score": result.market_score,
            "position_suggestion": result.position_suggestion,
            "risk_warnings": result.risk_warnings,
            "focus_points": result.focus_points,
        }


# 测试
if __name__ == "__main__":
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    
    console = Console()
    
    console.print(Panel.fit(
        "[bold cyan]市场综合分析器测试[/bold cyan]",
        border_style="cyan"
    ))
    
    analyzer = MarketAnalyzer()
    result = analyzer.analyze_market()
    
    if result:
        # 指数表格
        table = Table(title="8个核心指数分析", show_header=True)
        table.add_column("指数", width=10)
        table.add_column("分类", width=6)
        table.add_column("现价", justify="right", width=8)
        table.add_column("5日%", justify="right", width=8)
        table.add_column("RSI6", justify="right", width=6)
        table.add_column("牛熊", width=8)
        table.add_column("信号", width=8)
        
        for code, r in result.indices.items():
            signal_color = "green" if r.signal_score > 0 else "red" if r.signal_score < 0 else ""
            table.add_row(
                r.name,
                r.category,
                f"{r.current_price:.2f}",
                f"{r.change_5d:+.2f}%",
                f"{r.rsi6:.0f}",
                r.bull_bear.bull_bear_status,
                f"[{signal_color}]{r.overall_signal}[/{signal_color}]" if signal_color else r.overall_signal
            )
        
        console.print(table)
        
        # 轮动信号
        console.print(f"\n[bold]市值轮动:[/bold] {result.rotation.size_signal.value}")
        console.print(f"  {result.rotation.size_signal_desc}")
        
        console.print(f"\n[bold]风格轮动:[/bold] {result.rotation.style_signal.value}")
        console.print(f"  {result.rotation.style_signal_desc}")
        
        # 综合结论
        console.print(f"\n[bold cyan]市场信号:[/bold cyan] {result.market_signal}")
        console.print(f"[bold cyan]综合评分:[/bold cyan] {result.market_score}")
        console.print(f"[bold cyan]仓位建议:[/bold cyan] {result.position_suggestion}")
        
        # 风险提示
        if result.risk_warnings:
            console.print("\n[bold red]风险提示:[/bold red]")
            for w in result.risk_warnings:
                console.print(f"  ⚠️ {w}")
        
        # 关注重点
        if result.focus_points:
            console.print("\n[bold yellow]关注重点:[/bold yellow]")
            for p in result.focus_points:
                console.print(f"  • {p}")
    else:
        console.print("[red]分析失败[/red]")


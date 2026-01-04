#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
指数多周期分析器

功能：
1. 获取多周期K线数据（日/周/月/年）
2. 计算各周期技术指标
3. 分析6124-5178压力线
4. 生成多周期共振信号
5. 输出综合分析报告

参考文档: docs/analysis_methodology.md
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

from indicators.tech_indicators import TechIndicators, TechIndicatorsSummary, SignalType
from analyzers.pressure_line import PressureLineCalculator, PressureLineResult


@dataclass
class CycleAnalysisResult:
    """单周期分析结果"""
    cycle: str                          # 周期名称（日线/周线/月线/年线）
    cycle_code: str                     # 周期代码（D/W/M/Y）
    indicators: TechIndicatorsSummary   # 技术指标结果
    data_count: int                     # 数据条数
    latest_date: str                    # 最新数据日期
    latest_price: float                 # 最新收盘价
    change_pct: float                   # 涨跌幅
    signal: SignalType                  # 综合信号
    signal_description: str             # 信号描述


@dataclass
class MultiCycleResonance:
    """多周期共振分析结果"""
    daily: Optional[CycleAnalysisResult] = None
    weekly: Optional[CycleAnalysisResult] = None
    monthly: Optional[CycleAnalysisResult] = None
    yearly: Optional[CycleAnalysisResult] = None
    
    resonance_score: int = 0            # 共振评分
    resonance_type: str = "neutral"     # 共振类型（strong_bull/bull/neutral/bear/strong_bear）
    resonance_description: str = ""     # 共振描述
    bullish_cycles: List[str] = field(default_factory=list)   # 多头周期列表
    bearish_cycles: List[str] = field(default_factory=list)   # 空头周期列表


@dataclass
class IndexAnalysisResult:
    """指数分析综合结果"""
    index_code: str                     # 指数代码
    index_name: str                     # 指数名称
    analysis_time: str                  # 分析时间
    
    current_price: float                # 当前价格
    daily_change_pct: float             # 日涨跌幅
    
    pressure_line: PressureLineResult   # 压力线分析
    multi_cycle: MultiCycleResonance    # 多周期共振
    
    overall_score: int                  # 综合评分（-10到+10）
    overall_signal: str                 # 综合信号
    operation_suggestion: str           # 操作建议
    risk_factors: List[str]             # 风险因素
    focus_points: List[str]             # 关注重点


class IndexAnalyzer:
    """指数多周期分析器"""
    
    # 指数配置
    INDEX_CONFIG = {
        "000001": {"name": "上证指数", "market": "sh"},
        "399001": {"name": "深证成指", "market": "sz"},
        "000300": {"name": "沪深300", "market": "sh"},
        "399006": {"name": "创业板指", "market": "sz"},
    }
    
    # 周期权重
    CYCLE_WEIGHTS = {
        "daily": 1,
        "weekly": 2,
        "monthly": 3,
        "yearly": 4,
    }
    
    def __init__(self, index_code: str = "000001"):
        """初始化指数分析器
        
        Args:
            index_code: 指数代码，默认上证指数
        """
        self.index_code = index_code
        self.index_name = self.INDEX_CONFIG.get(index_code, {}).get("name", "未知指数")
        
        self.tech_indicators = TechIndicators()
        self.pressure_calc = PressureLineCalculator()
        
        # 数据缓存
        self._daily_data: Optional[pd.DataFrame] = None
        self._weekly_data: Optional[pd.DataFrame] = None
        self._monthly_data: Optional[pd.DataFrame] = None
    
    def load_data(self, days: int = 500) -> bool:
        """加载指数数据
        
        Args:
            days: 加载最近多少天的数据
        
        Returns:
            bool: 是否加载成功
        """
        try:
            from data_source import get_index_daily
            
            print(f"[数据加载] 正在获取 {self.index_name} ({self.index_code}) 数据...")
            
            # 获取日线数据
            self._daily_data = get_index_daily(self.index_code, days=days)
            
            if self._daily_data.empty:
                print(f"[错误] 无法获取 {self.index_name} 日线数据")
                return False
            
            print(f"[数据加载] 获取到 {len(self._daily_data)} 条日线数据")
            
            # 从日线数据聚合周线和月线
            self._aggregate_weekly_data()
            self._aggregate_monthly_data()
            
            return True
            
        except Exception as e:
            print(f"[错误] 数据加载失败: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _aggregate_weekly_data(self):
        """从日线数据聚合周线数据"""
        if self._daily_data is None or self._daily_data.empty:
            return
        
        df = self._daily_data.copy()
        df['周'] = df['日期'].dt.to_period('W')
        
        self._weekly_data = df.groupby('周').agg({
            '日期': 'last',
            '开盘': 'first',
            '最高': 'max',
            '最低': 'min',
            '收盘': 'last',
            '成交量': 'sum'
        }).reset_index(drop=True)
        
        print(f"[数据加载] 聚合得到 {len(self._weekly_data)} 条周线数据")
    
    def _aggregate_monthly_data(self):
        """从日线数据聚合月线数据"""
        if self._daily_data is None or self._daily_data.empty:
            return
        
        df = self._daily_data.copy()
        df['月'] = df['日期'].dt.to_period('M')
        
        self._monthly_data = df.groupby('月').agg({
            '日期': 'last',
            '开盘': 'first',
            '最高': 'max',
            '最低': 'min',
            '收盘': 'last',
            '成交量': 'sum'
        }).reset_index(drop=True)
        
        print(f"[数据加载] 聚合得到 {len(self._monthly_data)} 条月线数据")
    
    def analyze_cycle(self, df: pd.DataFrame, cycle_name: str, 
                      cycle_code: str) -> Optional[CycleAnalysisResult]:
        """分析单个周期
        
        Args:
            df: K线数据
            cycle_name: 周期名称
            cycle_code: 周期代码
        
        Returns:
            CycleAnalysisResult: 周期分析结果
        """
        if df is None or df.empty or len(df) < 60:
            return None
        
        try:
            # 计算技术指标
            indicators = self.tech_indicators.calculate_all(df)
            
            # 获取最新数据
            latest = df.iloc[-1]
            prev = df.iloc[-2] if len(df) > 1 else latest
            
            latest_price = float(latest['收盘'])
            prev_price = float(prev['收盘'])
            change_pct = (latest_price - prev_price) / prev_price * 100
            
            # 生成信号描述
            signal_desc = self._generate_signal_description(indicators, cycle_name)
            
            return CycleAnalysisResult(
                cycle=cycle_name,
                cycle_code=cycle_code,
                indicators=indicators,
                data_count=len(df),
                latest_date=latest['日期'].strftime('%Y-%m-%d') if hasattr(latest['日期'], 'strftime') else str(latest['日期']),
                latest_price=round(latest_price, 2),
                change_pct=round(change_pct, 2),
                signal=indicators.overall_signal,
                signal_description=signal_desc
            )
            
        except Exception as e:
            print(f"[警告] {cycle_name}分析失败: {e}")
            return None
    
    def _generate_signal_description(self, indicators: TechIndicatorsSummary, 
                                      cycle_name: str) -> str:
        """生成信号描述文本"""
        parts = []
        
        # MACD 描述
        if indicators.macd.cross == 'golden':
            parts.append("MACD金叉")
        elif indicators.macd.cross == 'death':
            parts.append("MACD死叉")
        else:
            if indicators.macd.position == 'above_zero':
                parts.append("MACD零轴上方")
            else:
                parts.append("MACD零轴下方")
        
        # RSI 描述
        if indicators.rsi.status == 'overbought':
            parts.append(f"RSI超买({indicators.rsi.value})")
        elif indicators.rsi.status == 'oversold':
            parts.append(f"RSI超卖({indicators.rsi.value})")
        
        # 均线描述
        if indicators.ma.arrangement == 'bull':
            parts.append("均线多头排列")
        elif indicators.ma.arrangement == 'bear':
            parts.append("均线空头排列")
        
        # K线形态
        if indicators.kline.consecutive_yang >= 5:
            parts.append(f"{indicators.kline.consecutive_yang}连阳")
        elif indicators.kline.consecutive_yin >= 5:
            parts.append(f"{indicators.kline.consecutive_yin}连阴")
        
        if indicators.kline.pattern != 'none':
            pattern_names = {
                'yang_engulf': '阳包阴',
                'yin_engulf': '阴包阳',
                'hammer': '锤头线',
                'doji': '十字星'
            }
            parts.append(pattern_names.get(indicators.kline.pattern, ''))
        
        return "，".join(parts) if parts else "无明显信号"
    
    def analyze_multi_cycle(self) -> MultiCycleResonance:
        """分析多周期共振"""
        resonance = MultiCycleResonance()
        
        # 分析各周期
        resonance.daily = self.analyze_cycle(self._daily_data, "日线", "D")
        resonance.weekly = self.analyze_cycle(self._weekly_data, "周线", "W")
        resonance.monthly = self.analyze_cycle(self._monthly_data, "月线", "M")
        
        # 计算共振评分
        score = 0
        bullish = []
        bearish = []
        
        cycles = [
            ("daily", "日线", resonance.daily),
            ("weekly", "周线", resonance.weekly),
            ("monthly", "月线", resonance.monthly),
        ]
        
        for cycle_key, cycle_name, result in cycles:
            if result is None:
                continue
            
            weight = self.CYCLE_WEIGHTS[cycle_key]
            
            if result.signal == SignalType.BULL:
                score += weight
                bullish.append(cycle_name)
            elif result.signal == SignalType.BEAR:
                score -= weight
                bearish.append(cycle_name)
        
        resonance.resonance_score = score
        resonance.bullish_cycles = bullish
        resonance.bearish_cycles = bearish
        
        # 判断共振类型
        if score >= 5:
            resonance.resonance_type = "strong_bull"
            resonance.resonance_description = "多周期强势共振看多"
        elif score >= 2:
            resonance.resonance_type = "bull"
            resonance.resonance_description = "多周期偏多"
        elif score <= -5:
            resonance.resonance_type = "strong_bear"
            resonance.resonance_description = "多周期强势共振看空"
        elif score <= -2:
            resonance.resonance_type = "bear"
            resonance.resonance_description = "多周期偏空"
        else:
            resonance.resonance_type = "neutral"
            resonance.resonance_description = "多周期震荡"
        
        return resonance
    
    def analyze(self) -> Optional[IndexAnalysisResult]:
        """执行完整的指数分析
        
        Returns:
            IndexAnalysisResult: 综合分析结果
        """
        # 加载数据
        if not self.load_data():
            return None
        
        # 获取当前价格
        current_price = float(self._daily_data['收盘'].iloc[-1])
        prev_price = float(self._daily_data['收盘'].iloc[-2])
        daily_change_pct = (current_price - prev_price) / prev_price * 100
        
        # 压力线分析
        pressure_result = self.pressure_calc.analyze(
            current_price=current_price,
            target_date=datetime.now(),
            df=self._daily_data
        )
        
        # 多周期共振分析
        multi_cycle = self.analyze_multi_cycle()
        
        # 计算综合评分
        overall_score = self._calculate_overall_score(pressure_result, multi_cycle)
        
        # 生成综合信号
        overall_signal = self._determine_overall_signal(overall_score)
        
        # 生成操作建议
        operation_suggestion = self._generate_operation_suggestion(
            overall_score, pressure_result, multi_cycle
        )
        
        # 识别风险因素
        risk_factors = self._identify_risk_factors(pressure_result, multi_cycle)
        
        # 识别关注重点
        focus_points = self._identify_focus_points(pressure_result, multi_cycle)
        
        return IndexAnalysisResult(
            index_code=self.index_code,
            index_name=self.index_name,
            analysis_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            current_price=round(current_price, 2),
            daily_change_pct=round(daily_change_pct, 2),
            pressure_line=pressure_result,
            multi_cycle=multi_cycle,
            overall_score=overall_score,
            overall_signal=overall_signal,
            operation_suggestion=operation_suggestion,
            risk_factors=risk_factors,
            focus_points=focus_points
        )
    
    def _calculate_overall_score(self, pressure: PressureLineResult,
                                  multi_cycle: MultiCycleResonance) -> int:
        """计算综合评分"""
        score = 0
        
        # 多周期共振评分（权重 60%）
        score += multi_cycle.resonance_score
        
        # 压力线评分（权重 30%）
        if pressure.is_breakthrough:
            score += 3
        elif pressure.is_above:
            score += 1
        elif pressure.deviation_pct > -3:
            score += 0
        else:
            score -= 1
        
        # 限制范围
        return max(-10, min(10, score))
    
    def _determine_overall_signal(self, score: int) -> str:
        """确定综合信号"""
        if score >= 7:
            return "强多头"
        elif score >= 4:
            return "中多头"
        elif score >= 1:
            return "偏多"
        elif score >= -1:
            return "中性"
        elif score >= -4:
            return "偏空"
        elif score >= -7:
            return "中空头"
        else:
            return "强空头"
    
    def _generate_operation_suggestion(self, score: int, 
                                        pressure: PressureLineResult,
                                        multi_cycle: MultiCycleResonance) -> str:
        """生成操作建议"""
        suggestions = []
        
        # 基于评分的仓位建议
        if score >= 7:
            suggestions.append("建议仓位: 70-80%")
            suggestions.append("策略: 积极做多，趋势跟踪")
        elif score >= 4:
            suggestions.append("建议仓位: 50-60%")
            suggestions.append("策略: 适度做多，逢低加仓")
        elif score >= 1:
            suggestions.append("建议仓位: 30-40%")
            suggestions.append("策略: 轻仓参与，控制风险")
        elif score >= -1:
            suggestions.append("建议仓位: 20-30%")
            suggestions.append("策略: 观望为主，等待方向")
        else:
            suggestions.append("建议仓位: 10-20%")
            suggestions.append("策略: 防守为主，规避风险")
        
        # 压力线相关建议
        if pressure.is_above:
            suggestions.append(f"关注压力线支撑: {pressure.pressure_position}")
        else:
            suggestions.append(f"关注压力线突破: {pressure.pressure_position}")
        
        return "；".join(suggestions)
    
    def _identify_risk_factors(self, pressure: PressureLineResult,
                                multi_cycle: MultiCycleResonance) -> List[str]:
        """识别风险因素"""
        risks = []
        
        # RSI 超买风险
        if multi_cycle.daily and multi_cycle.daily.indicators.rsi.status == 'overbought':
            risks.append(f"日线RSI超买({multi_cycle.daily.indicators.rsi.value})，短期回调压力")
        
        # 连续上涨后的获利盘风险
        if multi_cycle.daily and multi_cycle.daily.indicators.kline.consecutive_yang >= 7:
            risks.append(f"连续{multi_cycle.daily.indicators.kline.consecutive_yang}天上涨，获利盘回吐压力")
        
        # 压力线附近的突破风险
        if 0 < pressure.deviation_pct < 3:
            risks.append("刚站上压力线，突破有效性待确认")
        
        # 多空分歧风险
        if multi_cycle.bullish_cycles and multi_cycle.bearish_cycles:
            risks.append(f"多周期信号分歧（多头:{','.join(multi_cycle.bullish_cycles)}，空头:{','.join(multi_cycle.bearish_cycles)}）")
        
        return risks
    
    def _identify_focus_points(self, pressure: PressureLineResult,
                                multi_cycle: MultiCycleResonance) -> List[str]:
        """识别关注重点"""
        focus = []
        
        # 压力线关注点
        if pressure.is_above:
            focus.append(f"压力线({pressure.pressure_position})转支撑确认")
            if not pressure.is_breakthrough:
                focus.append("3%有效突破确认")
            if pressure.days_above < 3:
                focus.append("三日原则确认")
        else:
            focus.append(f"能否突破压力线({pressure.pressure_position})")
        
        # 技术指标关注点
        if multi_cycle.daily:
            if multi_cycle.daily.indicators.macd.cross == 'golden':
                focus.append("MACD金叉后续走势")
            elif multi_cycle.daily.indicators.macd.cross == 'death':
                focus.append("MACD死叉影响")
        
        # 成交量关注点
        focus.append("成交量配合情况")
        
        return focus
    
    def to_dict(self, result: IndexAnalysisResult) -> Dict[str, Any]:
        """将分析结果转换为字典（用于报告生成）"""
        def cycle_to_dict(cycle: Optional[CycleAnalysisResult]) -> Optional[Dict]:
            if cycle is None:
                return None
            return {
                "cycle": cycle.cycle,
                "cycle_code": cycle.cycle_code,
                "latest_date": cycle.latest_date,
                "latest_price": cycle.latest_price,
                "change_pct": cycle.change_pct,
                "signal": cycle.signal.name,
                "signal_description": cycle.signal_description,
                "macd": {
                    "dif": cycle.indicators.macd.dif,
                    "dea": cycle.indicators.macd.dea,
                    "macd": cycle.indicators.macd.macd,
                    "cross": cycle.indicators.macd.cross,
                    "trend": cycle.indicators.macd.trend,
                    "position": cycle.indicators.macd.position,
                },
                "rsi": {
                    "value": cycle.indicators.rsi.value,
                    "status": cycle.indicators.rsi.status,
                },
                "ma": {
                    "ma5": cycle.indicators.ma.ma5,
                    "ma10": cycle.indicators.ma.ma10,
                    "ma20": cycle.indicators.ma.ma20,
                    "ma60": cycle.indicators.ma.ma60,
                    "ma250": cycle.indicators.ma.ma250,
                    "arrangement": cycle.indicators.ma.arrangement,
                },
                "bollinger": {
                    "upper": cycle.indicators.bollinger.upper,
                    "middle": cycle.indicators.bollinger.middle,
                    "lower": cycle.indicators.bollinger.lower,
                    "width": cycle.indicators.bollinger.width,
                    "position": cycle.indicators.bollinger.position,
                },
                "kline": {
                    "consecutive_yang": cycle.indicators.kline.consecutive_yang,
                    "consecutive_yin": cycle.indicators.kline.consecutive_yin,
                    "pattern": cycle.indicators.kline.pattern,
                },
                "signal_score": cycle.indicators.signal_score,
            }
        
        return {
            "index_code": result.index_code,
            "index_name": result.index_name,
            "analysis_time": result.analysis_time,
            "current_price": result.current_price,
            "daily_change_pct": result.daily_change_pct,
            "pressure_line": {
                "target_date": result.pressure_line.target_date,
                "position": result.pressure_line.pressure_position,
                "deviation": result.pressure_line.deviation,
                "deviation_pct": result.pressure_line.deviation_pct,
                "is_above": result.pressure_line.is_above,
                "is_breakthrough": result.pressure_line.is_breakthrough,
                "status": result.pressure_line.breakthrough_status,
                "days_above": result.pressure_line.days_above,
            },
            "multi_cycle": {
                "daily": cycle_to_dict(result.multi_cycle.daily),
                "weekly": cycle_to_dict(result.multi_cycle.weekly),
                "monthly": cycle_to_dict(result.multi_cycle.monthly),
                "yearly": cycle_to_dict(result.multi_cycle.yearly),
                "resonance_score": result.multi_cycle.resonance_score,
                "resonance_type": result.multi_cycle.resonance_type,
                "resonance_description": result.multi_cycle.resonance_description,
                "bullish_cycles": result.multi_cycle.bullish_cycles,
                "bearish_cycles": result.multi_cycle.bearish_cycles,
            },
            "overall_score": result.overall_score,
            "overall_signal": result.overall_signal,
            "operation_suggestion": result.operation_suggestion,
            "risk_factors": result.risk_factors,
            "focus_points": result.focus_points,
        }


# 测试代码
if __name__ == "__main__":
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    
    console = Console()
    
    console.print(Panel.fit(
        "[bold cyan]指数多周期分析器测试[/bold cyan]",
        border_style="cyan"
    ))
    
    analyzer = IndexAnalyzer("000001")
    result = analyzer.analyze()
    
    if result:
        # 基本信息
        console.print(f"\n[bold]{result.index_name}[/bold] ({result.index_code})")
        console.print(f"分析时间: {result.analysis_time}")
        console.print(f"当前价格: [cyan]{result.current_price}[/cyan] ({result.daily_change_pct:+.2f}%)")
        
        # 压力线分析
        console.print(f"\n[bold]压力线分析:[/bold]")
        console.print(f"  压力线位置: {result.pressure_line.pressure_position}")
        console.print(f"  偏离: {result.pressure_line.deviation} ({result.pressure_line.deviation_pct:+.2f}%)")
        console.print(f"  状态: {result.pressure_line.breakthrough_status}")
        
        # 多周期共振
        console.print(f"\n[bold]多周期共振:[/bold]")
        console.print(f"  共振评分: {result.multi_cycle.resonance_score}")
        console.print(f"  共振类型: {result.multi_cycle.resonance_description}")
        console.print(f"  多头周期: {', '.join(result.multi_cycle.bullish_cycles) or '无'}")
        console.print(f"  空头周期: {', '.join(result.multi_cycle.bearish_cycles) or '无'}")
        
        # 综合结论
        console.print(f"\n[bold]综合结论:[/bold]")
        console.print(f"  综合评分: {result.overall_score}")
        console.print(f"  综合信号: {result.overall_signal}")
        console.print(f"  操作建议: {result.operation_suggestion}")
        
        # 风险因素
        if result.risk_factors:
            console.print(f"\n[bold red]风险因素:[/bold red]")
            for risk in result.risk_factors:
                console.print(f"  • {risk}")
        
        # 关注重点
        if result.focus_points:
            console.print(f"\n[bold yellow]关注重点:[/bold yellow]")
            for point in result.focus_points:
                console.print(f"  • {point}")
    else:
        console.print("[red]分析失败[/red]")


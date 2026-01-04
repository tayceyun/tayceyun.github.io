#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
指数轮动分析器

功能：
1. 市值层级双向轮动（大盘↔中盘↔小盘）
2. 成长↔大盘双向轮动
3. 风格轮动检测
4. 趋势转变预警

参考: docs/test.md
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum
import pandas as pd

# 添加项目根目录到路径
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


class RotationSignal(Enum):
    """轮动信号类型"""
    BUY_SMALL_SELL_LARGE = "买小卖大"      # 大盘→小盘轮动
    BUY_LARGE_SELL_SMALL = "买大卖小"      # 小盘→大盘轮动
    BUY_GROWTH_SELL_VALUE = "买成长卖价值"  # 价值→成长轮动
    BUY_VALUE_SELL_GROWTH = "买价值卖成长"  # 成长→价值轮动
    HOLD_BALANCE = "均衡配置"              # 震荡市
    RISK_WARNING = "风险预警"              # 趋势转变


@dataclass
class StylePerformance:
    """风格表现"""
    style: str                # 风格名称
    indices: List[str]        # 包含的指数
    avg_change_5d: float      # 5日平均涨跌幅
    avg_change_10d: float     # 10日平均涨跌幅
    avg_change_20d: float     # 20日平均涨跌幅
    bull_bear_status: str     # 牛熊状态
    broken_indices: List[str] # 破位的指数


@dataclass
class RotationResult:
    """轮动分析结果"""
    analysis_time: str
    
    # 市值轮动
    size_signal: RotationSignal
    size_signal_desc: str
    size_buy_targets: List[str]
    size_sell_targets: List[str]
    
    # 成长/价值轮动
    style_signal: RotationSignal
    style_signal_desc: str
    style_buy_targets: List[str]
    style_sell_targets: List[str]
    
    # 风格表现
    large_cap_perf: StylePerformance
    mid_cap_perf: StylePerformance
    small_cap_perf: StylePerformance
    growth_perf: StylePerformance
    
    # 风险预警
    risk_warnings: List[str]
    broken_indices: List[str]
    
    # 综合建议
    overall_signal: str
    recommended_allocation: Dict[str, float]  # 建议配置比例


# 轮动规则阈值
ROTATION_THRESHOLDS = {
    # 流动性阈值
    "bond_yield_loose": 2.7,        # 流动性宽松（国债收益率低于此值）
    "bond_yield_tight": 3.0,        # 流动性收紧（国债收益率高于此值）
    
    # 经济周期阈值
    "pmi_expansion": 50,            # PMI扩张阈值
    "pmi_contraction": 49,          # PMI收缩阈值
    
    # PE分位差阈值
    "pe_diff_small_cheap": -10,     # 小盘相对低估
    "pe_diff_small_expensive": 20,  # 小盘相对高估
    "pe_diff_growth_expensive": 20, # 成长相对高估
    "pe_diff_growth_cheap": 10,     # 成长相对便宜
    
    # RSI阈值
    "rsi_overbought": 70,
    "rsi_oversold": 30,
    
    # 北向资金阈值
    "north_money_inflow": 100,      # 5日净流入（亿）
    "north_money_outflow": -50,     # 5日净流出（亿）
    
    # 涨跌幅差异阈值
    "performance_gap": 3.0,         # 风格涨跌幅差>3%视为明显
    
    # 破位判断
    "break_threshold": -3.0,        # 跌破均线超过3%视为破位
}


class RotationAnalyzer:
    """指数轮动分析器"""
    
    # 指数分类配置
    INDEX_CATEGORIES = {
        "large_cap": {
            "name": "大盘",
            "indices": ["000001", "000300", "000016"],
            "names": ["上证指数", "沪深300", "上证50"],
        },
        "mid_cap": {
            "name": "中盘",
            "indices": ["000905"],
            "names": ["中证500"],
        },
        "small_cap": {
            "name": "小盘",
            "indices": ["000852", "399303"],
            "names": ["中证1000", "国证2000"],
        },
        "growth": {
            "name": "成长",
            "indices": ["399006", "000688"],
            "names": ["创业板指", "科创50"],
        },
    }
    
    def __init__(self):
        self.thresholds = ROTATION_THRESHOLDS.copy()
        self._index_data: Dict[str, Any] = {}
    
    def set_index_data(self, index_code: str, data: Dict[str, Any]):
        """设置指数数据
        
        Args:
            index_code: 指数代码
            data: 包含以下字段的字典：
                - current_price: 当前价格
                - change_5d: 5日涨跌幅
                - change_10d: 10日涨跌幅
                - change_20d: 20日涨跌幅
                - rsi6: RSI(6)
                - bull_bear_status: 牛熊状态
                - above_ma60: 是否在MA60上方
                - above_ma250: 是否在MA250上方
        """
        self._index_data[index_code] = data
    
    def _get_category_performance(self, category: str) -> StylePerformance:
        """计算某个风格类别的表现"""
        config = self.INDEX_CATEGORIES[category]
        indices = config["indices"]
        names = config["names"]
        
        changes_5d = []
        changes_10d = []
        changes_20d = []
        broken = []
        bull_bear_count = {"bull": 0, "bear": 0, "neutral": 0}
        
        for i, code in enumerate(indices):
            data = self._index_data.get(code, {})
            
            changes_5d.append(data.get("change_5d", 0))
            changes_10d.append(data.get("change_10d", 0))
            changes_20d.append(data.get("change_20d", 0))
            
            # 判断是否破位
            if not data.get("above_ma60", True) and not data.get("above_ma250", True):
                broken.append(names[i])
            
            # 统计牛熊状态
            status = data.get("bull_bear_status", "neutral")
            if "bull" in status:
                bull_bear_count["bull"] += 1
            elif "bear" in status:
                bull_bear_count["bear"] += 1
            else:
                bull_bear_count["neutral"] += 1
        
        # 确定整体牛熊状态
        if bull_bear_count["bull"] > bull_bear_count["bear"]:
            overall_status = "bull"
        elif bull_bear_count["bear"] > bull_bear_count["bull"]:
            overall_status = "bear"
        else:
            overall_status = "neutral"
        
        return StylePerformance(
            style=config["name"],
            indices=names,
            avg_change_5d=sum(changes_5d) / len(changes_5d) if changes_5d else 0,
            avg_change_10d=sum(changes_10d) / len(changes_10d) if changes_10d else 0,
            avg_change_20d=sum(changes_20d) / len(changes_20d) if changes_20d else 0,
            bull_bear_status=overall_status,
            broken_indices=broken
        )
    
    def analyze_size_rotation(self, large_perf: StylePerformance,
                               mid_perf: StylePerformance,
                               small_perf: StylePerformance,
                               macro_data: Dict) -> Tuple[RotationSignal, str, List[str], List[str]]:
        """分析市值轮动信号
        
        Args:
            large_perf: 大盘表现
            mid_perf: 中盘表现
            small_perf: 小盘表现
            macro_data: 宏观数据 {bond_yield, pmi, pe_diff_small_large, north_money_5d}
        
        Returns:
            (信号, 描述, 买入目标, 卖出目标)
        """
        bond_yield = macro_data.get("bond_yield", 2.8)
        pmi = macro_data.get("pmi", 50)
        pe_diff = macro_data.get("pe_diff_small_large", 0)  # 小盘PE分位 - 大盘PE分位
        
        # 判断流动性环境
        liquidity_loose = bond_yield < self.thresholds["bond_yield_loose"]
        liquidity_tight = bond_yield > self.thresholds["bond_yield_tight"]
        
        # 判断经济周期
        economy_expansion = pmi > self.thresholds["pmi_expansion"]
        economy_contraction = pmi < self.thresholds["pmi_contraction"]
        
        # 判断估值差异
        small_cheap = pe_diff < self.thresholds["pe_diff_small_cheap"]
        small_expensive = pe_diff > self.thresholds["pe_diff_small_expensive"]
        
        # 判断涨跌幅差异
        small_vs_large_5d = small_perf.avg_change_5d - large_perf.avg_change_5d
        small_outperform = small_vs_large_5d > self.thresholds["performance_gap"]
        large_outperform = small_vs_large_5d < -self.thresholds["performance_gap"]
        
        # 综合判断轮动方向
        # 大盘→小盘：流动性宽松 + 经济扩张 + 小盘估值低
        if liquidity_loose and economy_expansion and small_cheap:
            return (
                RotationSignal.BUY_SMALL_SELL_LARGE,
                f"流动性宽松(国债{bond_yield}%) + 经济扩张(PMI {pmi}) + 小盘估值偏低",
                ["中证1000", "国证2000", "中证500"],
                ["上证50", "沪深300"]
            )
        
        # 小盘→大盘：流动性收紧 + 经济收缩 + 小盘估值高
        if liquidity_tight and economy_contraction and small_expensive:
            return (
                RotationSignal.BUY_LARGE_SELL_SMALL,
                f"流动性收紧(国债{bond_yield}%) + 经济放缓(PMI {pmi}) + 小盘估值偏高",
                ["沪深300", "上证50"],
                ["中证1000", "国证2000"]
            )
        
        # 基于表现的轮动建议（次优先级）
        if small_outperform and not small_expensive:
            return (
                RotationSignal.BUY_SMALL_SELL_LARGE,
                f"小盘近期表现强势(5日超额{small_vs_large_5d:.1f}%)，存在动量延续可能",
                ["中证1000", "中证500"],
                []
            )
        
        if large_outperform and not small_cheap:
            return (
                RotationSignal.BUY_LARGE_SELL_SMALL,
                f"大盘近期表现强势(5日超额{-small_vs_large_5d:.1f}%)，资金回流蓝筹",
                ["沪深300", "上证50"],
                []
            )
        
        # 震荡市均衡配置
        return (
            RotationSignal.HOLD_BALANCE,
            "市场风格未现明显轮动，建议均衡配置",
            ["沪深300", "中证500"],
            []
        )
    
    def analyze_style_rotation(self, large_perf: StylePerformance,
                                growth_perf: StylePerformance,
                                macro_data: Dict) -> Tuple[RotationSignal, str, List[str], List[str]]:
        """分析成长/价值轮动信号
        
        Args:
            large_perf: 大盘表现（代表价值）
            growth_perf: 成长表现
            macro_data: 宏观数据
        
        Returns:
            (信号, 描述, 买入目标, 卖出目标)
        """
        pe_diff_growth_value = macro_data.get("pe_diff_growth_value", 0)
        north_money = macro_data.get("north_money_5d", 0)
        growth_rsi = macro_data.get("growth_rsi", 50)
        
        # 判断成长板块RSI
        growth_overbought = growth_rsi > self.thresholds["rsi_overbought"]
        growth_oversold = growth_rsi < self.thresholds["rsi_oversold"]
        
        # 判断北向资金
        north_inflow = north_money > self.thresholds["north_money_inflow"]
        north_outflow = north_money < self.thresholds["north_money_outflow"]
        
        # 判断估值差异
        growth_expensive = pe_diff_growth_value > self.thresholds["pe_diff_growth_expensive"]
        growth_cheap = pe_diff_growth_value < self.thresholds["pe_diff_growth_cheap"]
        
        # 涨跌幅差异
        growth_vs_value_5d = growth_perf.avg_change_5d - large_perf.avg_change_5d
        
        # 成长→价值：成长超买 + 成长高估 + 资金流出
        if growth_overbought and growth_expensive:
            return (
                RotationSignal.BUY_VALUE_SELL_GROWTH,
                f"成长板块超买(RSI {growth_rsi:.0f}) + 估值偏高，建议切换至价值",
                ["沪深300", "上证50"],
                ["创业板指", "科创50"]
            )
        
        # 价值→成长：成长超卖 + 北向流入 + 成长低估
        if growth_oversold and north_inflow and growth_cheap:
            return (
                RotationSignal.BUY_GROWTH_SELL_VALUE,
                f"成长板块超卖(RSI {growth_rsi:.0f}) + 北向资金流入 + 估值合理",
                ["创业板指", "科创50"],
                ["沪深300", "上证50"]
            )
        
        # 基于动量
        if growth_vs_value_5d > self.thresholds["performance_gap"]:
            return (
                RotationSignal.BUY_GROWTH_SELL_VALUE,
                f"成长动量强劲(5日超额{growth_vs_value_5d:.1f}%)",
                ["创业板指", "科创50"],
                []
            )
        
        if growth_vs_value_5d < -self.thresholds["performance_gap"]:
            return (
                RotationSignal.BUY_VALUE_SELL_GROWTH,
                f"价值动量强劲(5日超额{-growth_vs_value_5d:.1f}%)",
                ["沪深300", "上证50"],
                []
            )
        
        return (
            RotationSignal.HOLD_BALANCE,
            "成长价值风格均衡，无明显轮动信号",
            [],
            []
        )
    
    def detect_risk_warnings(self, performances: List[StylePerformance]) -> Tuple[List[str], List[str]]:
        """检测风险预警
        
        Args:
            performances: 各风格表现列表
        
        Returns:
            (风险预警列表, 破位指数列表)
        """
        warnings = []
        all_broken = []
        
        # 统计破位情况
        bear_count = 0
        for perf in performances:
            all_broken.extend(perf.broken_indices)
            if perf.bull_bear_status == "bear":
                bear_count += 1
        
        # 多数风格转熊
        if bear_count >= 2:
            warnings.append(f"多数风格({bear_count}/4)转入熊市状态，需警惕趋势转变")
        
        # 有指数破位
        if all_broken:
            warnings.append(f"以下指数跌破牛熊分界线：{', '.join(all_broken)}")
        
        # 检查是否有风格大幅下跌
        for perf in performances:
            if perf.avg_change_5d < -5:
                warnings.append(f"{perf.style}板块5日跌幅{perf.avg_change_5d:.1f}%，短期超跌")
        
        return warnings, all_broken
    
    def analyze(self, macro_data: Dict = None) -> RotationResult:
        """执行完整的轮动分析
        
        Args:
            macro_data: 宏观数据字典
        
        Returns:
            RotationResult: 轮动分析结果
        """
        if macro_data is None:
            macro_data = {}
        
        # 计算各风格表现
        large_perf = self._get_category_performance("large_cap")
        mid_perf = self._get_category_performance("mid_cap")
        small_perf = self._get_category_performance("small_cap")
        growth_perf = self._get_category_performance("growth")
        
        # 市值轮动分析
        size_signal, size_desc, size_buy, size_sell = self.analyze_size_rotation(
            large_perf, mid_perf, small_perf, macro_data
        )
        
        # 成长/价值轮动分析
        style_signal, style_desc, style_buy, style_sell = self.analyze_style_rotation(
            large_perf, growth_perf, macro_data
        )
        
        # 风险预警检测
        risk_warnings, broken_indices = self.detect_risk_warnings(
            [large_perf, mid_perf, small_perf, growth_perf]
        )
        
        # 综合建议
        overall_signal = self._generate_overall_signal(
            size_signal, style_signal, risk_warnings
        )
        
        # 建议配置
        allocation = self._generate_allocation(
            size_signal, style_signal, risk_warnings
        )
        
        return RotationResult(
            analysis_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            size_signal=size_signal,
            size_signal_desc=size_desc,
            size_buy_targets=size_buy,
            size_sell_targets=size_sell,
            style_signal=style_signal,
            style_signal_desc=style_desc,
            style_buy_targets=style_buy,
            style_sell_targets=style_sell,
            large_cap_perf=large_perf,
            mid_cap_perf=mid_perf,
            small_cap_perf=small_perf,
            growth_perf=growth_perf,
            risk_warnings=risk_warnings,
            broken_indices=broken_indices,
            overall_signal=overall_signal,
            recommended_allocation=allocation
        )
    
    def _generate_overall_signal(self, size_signal: RotationSignal,
                                  style_signal: RotationSignal,
                                  warnings: List[str]) -> str:
        """生成综合信号"""
        if warnings:
            return "谨慎观望"
        
        if size_signal == RotationSignal.BUY_SMALL_SELL_LARGE:
            if style_signal == RotationSignal.BUY_GROWTH_SELL_VALUE:
                return "积极进攻（小盘成长）"
            return "偏进攻（中小盘）"
        
        if size_signal == RotationSignal.BUY_LARGE_SELL_SMALL:
            if style_signal == RotationSignal.BUY_VALUE_SELL_GROWTH:
                return "防守为主（大盘价值）"
            return "偏防守（大盘蓝筹）"
        
        return "均衡配置"
    
    def _generate_allocation(self, size_signal: RotationSignal,
                              style_signal: RotationSignal,
                              warnings: List[str]) -> Dict[str, float]:
        """生成建议配置比例"""
        if warnings:
            # 有风险预警，降低仓位
            return {
                "大盘": 0.30,
                "中盘": 0.10,
                "小盘": 0.10,
                "成长": 0.10,
                "现金": 0.40,
            }
        
        if size_signal == RotationSignal.BUY_SMALL_SELL_LARGE:
            return {
                "大盘": 0.15,
                "中盘": 0.25,
                "小盘": 0.30,
                "成长": 0.20,
                "现金": 0.10,
            }
        
        if size_signal == RotationSignal.BUY_LARGE_SELL_SMALL:
            return {
                "大盘": 0.40,
                "中盘": 0.20,
                "小盘": 0.10,
                "成长": 0.10,
                "现金": 0.20,
            }
        
        # 均衡配置
        return {
            "大盘": 0.25,
            "中盘": 0.20,
            "小盘": 0.20,
            "成长": 0.20,
            "现金": 0.15,
        }


# 便捷函数
def analyze_rotation(index_data: Dict[str, Dict], macro_data: Dict = None) -> RotationResult:
    """执行轮动分析
    
    Args:
        index_data: 指数数据字典 {code: {current_price, change_5d, ...}}
        macro_data: 宏观数据
    
    Returns:
        RotationResult
    """
    analyzer = RotationAnalyzer()
    for code, data in index_data.items():
        analyzer.set_index_data(code, data)
    return analyzer.analyze(macro_data)


# 测试
if __name__ == "__main__":
    from rich.console import Console
    from rich.panel import Panel
    
    console = Console()
    console.print(Panel.fit("[bold cyan]轮动分析器测试[/bold cyan]"))
    
    # 模拟数据
    test_data = {
        "000001": {"change_5d": 2.5, "change_10d": 4.0, "change_20d": 5.0, "rsi6": 65, "bull_bear_status": "bull", "above_ma60": True, "above_ma250": True},
        "000300": {"change_5d": 2.0, "change_10d": 3.5, "change_20d": 4.5, "rsi6": 62, "bull_bear_status": "bull", "above_ma60": True, "above_ma250": True},
        "000016": {"change_5d": 1.5, "change_10d": 3.0, "change_20d": 4.0, "rsi6": 58, "bull_bear_status": "neutral", "above_ma60": True, "above_ma250": False},
        "000905": {"change_5d": 3.5, "change_10d": 5.0, "change_20d": 6.0, "rsi6": 68, "bull_bear_status": "bull", "above_ma60": True, "above_ma250": True},
        "000852": {"change_5d": 4.5, "change_10d": 6.5, "change_20d": 8.0, "rsi6": 72, "bull_bear_status": "bull", "above_ma60": True, "above_ma250": True},
        "399303": {"change_5d": 4.0, "change_10d": 6.0, "change_20d": 7.5, "rsi6": 70, "bull_bear_status": "bull", "above_ma60": True, "above_ma250": True},
        "399006": {"change_5d": 5.0, "change_10d": 7.0, "change_20d": 9.0, "rsi6": 75, "bull_bear_status": "bull", "above_ma60": True, "above_ma250": True},
        "000688": {"change_5d": 4.8, "change_10d": 6.8, "change_20d": 8.5, "rsi6": 73, "bull_bear_status": "bull", "above_ma60": True, "above_ma250": True},
    }
    
    macro = {
        "bond_yield": 2.5,
        "pmi": 51.5,
        "pe_diff_small_large": -5,
        "pe_diff_growth_value": 15,
        "north_money_5d": 150,
        "growth_rsi": 75,
    }
    
    result = analyze_rotation(test_data, macro)
    
    console.print(f"\n[bold]市值轮动:[/bold] {result.size_signal.value}")
    console.print(f"  {result.size_signal_desc}")
    console.print(f"  买入: {result.size_buy_targets}")
    console.print(f"  卖出: {result.size_sell_targets}")
    
    console.print(f"\n[bold]风格轮动:[/bold] {result.style_signal.value}")
    console.print(f"  {result.style_signal_desc}")
    
    console.print(f"\n[bold]综合信号:[/bold] {result.overall_signal}")
    console.print(f"\n[bold]建议配置:[/bold]")
    for k, v in result.recommended_allocation.items():
        console.print(f"  {k}: {v*100:.0f}%")
    
    if result.risk_warnings:
        console.print(f"\n[bold red]风险预警:[/bold red]")
        for w in result.risk_warnings:
            console.print(f"  ⚠️ {w}")


#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
信号评分引擎

功能：
1. 加载 JSON 配置的评分规则
2. 解析条件表达式
3. 计算综合评分
4. 生成信号强度判定
5. 输出操作建议

参考文档: docs/analysis_methodology.md
"""

import json
import re
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum


class SignalLevel(Enum):
    """信号强度级别"""
    STRONG_BULL = "strong_bull"
    MODERATE_BULL = "moderate_bull"
    SLIGHT_BULL = "slight_bull"
    NEUTRAL = "neutral"
    SLIGHT_BEAR = "slight_bear"
    MODERATE_BEAR = "moderate_bear"
    STRONG_BEAR = "strong_bear"


class RiskLevel(Enum):
    """风险级别"""
    DANGER = "danger"
    WARNING = "warning"
    INFO = "info"


@dataclass
class SignalFactor:
    """信号因子"""
    name: str
    weight: int
    condition: str
    description: str
    triggered: bool = False
    value: Optional[Any] = None


@dataclass
class SignalResult:
    """信号评分结果"""
    total_score: int
    signal_level: SignalLevel
    signal_label: str
    operation_suggestion: str
    triggered_factors: List[SignalFactor] = field(default_factory=list)
    score_breakdown: Dict[str, int] = field(default_factory=dict)


@dataclass
class RiskWarning:
    """风险预警"""
    rule_name: str
    level: RiskLevel
    message: str
    condition: str


class SignalEngine:
    """信号评分引擎"""
    
    def __init__(self, config_path: Optional[str] = None):
        """初始化信号引擎
        
        Args:
            config_path: 配置文件路径，默认使用 config/signal_rules.json
        """
        if config_path is None:
            config_path = Path(__file__).parent.parent / "config" / "signal_rules.json"
        
        self.config_path = Path(config_path)
        self.config: Dict = {}
        self._load_config()
    
    def _load_config(self):
        """加载配置文件"""
        if self.config_path.exists():
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
            print(f"[信号引擎] 已加载配置: {self.config_path}")
        else:
            print(f"[警告] 配置文件不存在: {self.config_path}")
            self.config = {}
    
    def reload_config(self):
        """重新加载配置"""
        self._load_config()
    
    def evaluate_condition(self, condition: str, context: Dict[str, Any]) -> bool:
        """评估条件表达式
        
        Args:
            condition: 条件表达式字符串，如 "daily_signal == 'BULL'"
            context: 上下文变量字典
        
        Returns:
            bool: 条件是否满足
        """
        try:
            # 安全评估：只允许简单的比较表达式
            # 替换变量
            for key, value in context.items():
                if isinstance(value, str):
                    condition = condition.replace(key, f"'{value}'")
                elif value is None:
                    condition = condition.replace(key, "None")
                else:
                    condition = condition.replace(key, str(value))
            
            # 评估表达式
            result = eval(condition, {"__builtins__": {}}, {})
            return bool(result)
        except Exception as e:
            # 条件评估失败，返回 False
            return False
    
    def calculate_index_signal(self, context: Dict[str, Any]) -> SignalResult:
        """计算指数信号评分
        
        Args:
            context: 包含以下变量的字典：
                - daily_signal: 日线信号 ('BULL' / 'BEAR' / 'NEUTRAL')
                - weekly_signal: 周线信号
                - monthly_signal: 月线信号
                - deviation_pct: 压力线偏离百分比
                - volume_ratio: 成交量比率
                - north_money_inflow_days: 北向资金连续流入天数
                - north_money_outflow_days: 北向资金连续流出天数
        
        Returns:
            SignalResult: 评分结果
        """
        if "index_signal" not in self.config:
            return SignalResult(
                total_score=0,
                signal_level=SignalLevel.NEUTRAL,
                signal_label="中性",
                operation_suggestion="配置文件缺失，无法评分"
            )
        
        index_config = self.config["index_signal"]
        total_score = 0
        triggered_factors = []
        score_breakdown = {}
        
        # 1. 多周期信号评分
        if "multi_cycle" in index_config:
            cycle_score = 0
            for factor_name, factor_config in index_config["multi_cycle"].items():
                if factor_name == "description":
                    continue
                
                if self.evaluate_condition(factor_config["condition"], context):
                    weight = factor_config["weight"]
                    cycle_score += weight
                    triggered_factors.append(SignalFactor(
                        name=factor_name,
                        weight=weight,
                        condition=factor_config["condition"],
                        description=factor_config["description"],
                        triggered=True
                    ))
            
            total_score += cycle_score
            score_breakdown["multi_cycle"] = cycle_score
        
        # 2. 压力线信号评分
        if "pressure_line" in index_config:
            pressure_score = 0
            for factor_name, factor_config in index_config["pressure_line"].items():
                if factor_name == "description":
                    continue
                
                if self.evaluate_condition(factor_config["condition"], context):
                    weight = factor_config["weight"]
                    pressure_score += weight
                    triggered_factors.append(SignalFactor(
                        name=factor_name,
                        weight=weight,
                        condition=factor_config["condition"],
                        description=factor_config["description"],
                        triggered=True
                    ))
                    break  # 压力线条件互斥，只取第一个匹配的
            
            total_score += pressure_score
            score_breakdown["pressure_line"] = pressure_score
        
        # 3. 成交量信号评分
        if "volume" in index_config:
            volume_score = 0
            for factor_name, factor_config in index_config["volume"].items():
                if factor_name == "description":
                    continue
                
                if self.evaluate_condition(factor_config["condition"], context):
                    weight = factor_config["weight"]
                    volume_score += weight
                    triggered_factors.append(SignalFactor(
                        name=factor_name,
                        weight=weight,
                        condition=factor_config["condition"],
                        description=factor_config["description"],
                        triggered=True
                    ))
            
            total_score += volume_score
            score_breakdown["volume"] = volume_score
        
        # 4. 资金面信号评分（如果有数据）
        if "capital_flow" in index_config:
            capital_score = 0
            for factor_name, factor_config in index_config["capital_flow"].items():
                if factor_name == "description":
                    continue
                
                if self.evaluate_condition(factor_config["condition"], context):
                    weight = factor_config["weight"]
                    capital_score += weight
                    triggered_factors.append(SignalFactor(
                        name=factor_name,
                        weight=weight,
                        condition=factor_config["condition"],
                        description=factor_config["description"],
                        triggered=True
                    ))
            
            total_score += capital_score
            score_breakdown["capital_flow"] = capital_score
        
        # 5. 确定信号强度
        signal_level, signal_label, operation = self._determine_signal_strength(
            total_score, index_config.get("signal_strength", {})
        )
        
        return SignalResult(
            total_score=total_score,
            signal_level=signal_level,
            signal_label=signal_label,
            operation_suggestion=operation,
            triggered_factors=triggered_factors,
            score_breakdown=score_breakdown
        )
    
    def calculate_stock_signal(self, context: Dict[str, Any]) -> SignalResult:
        """计算个股信号评分
        
        Args:
            context: 包含基本面、技术面、资金面、事件面变量的字典
        
        Returns:
            SignalResult: 评分结果
        """
        if "stock_signal" not in self.config:
            return SignalResult(
                total_score=0,
                signal_level=SignalLevel.NEUTRAL,
                signal_label="中性",
                operation_suggestion="配置文件缺失，无法评分"
            )
        
        stock_config = self.config["stock_signal"]
        total_score = 0
        triggered_factors = []
        score_breakdown = {}
        
        # 遍历各个维度
        for dimension in ["fundamental", "technical", "capital", "event"]:
            if dimension not in stock_config:
                continue
            
            dim_config = stock_config[dimension]
            dim_score = 0
            
            if "factors" in dim_config:
                for factor_name, factor_config in dim_config["factors"].items():
                    if self.evaluate_condition(factor_config["condition"], context):
                        weight = factor_config["weight"]
                        dim_score += weight
                        triggered_factors.append(SignalFactor(
                            name=factor_name,
                            weight=weight,
                            condition=factor_config["condition"],
                            description=factor_config["description"],
                            triggered=True
                        ))
            
            total_score += dim_score
            score_breakdown[dimension] = dim_score
        
        # 确定信号强度
        signal_level, signal_label, operation = self._determine_signal_strength(
            total_score, stock_config.get("signal_strength", {})
        )
        
        return SignalResult(
            total_score=total_score,
            signal_level=signal_level,
            signal_label=signal_label,
            operation_suggestion=operation,
            triggered_factors=triggered_factors,
            score_breakdown=score_breakdown
        )
    
    def _determine_signal_strength(self, score: int, 
                                    strength_config: Dict) -> Tuple[SignalLevel, str, str]:
        """根据评分确定信号强度
        
        Args:
            score: 总评分
            strength_config: 信号强度配置
        
        Returns:
            Tuple[SignalLevel, str, str]: (信号级别, 标签, 操作建议)
        """
        # 默认值
        default_levels = [
            (7, SignalLevel.STRONG_BULL, "强多头", "积极做多，仓位70-80%"),
            (4, SignalLevel.MODERATE_BULL, "中多头", "适度做多，仓位50-60%"),
            (1, SignalLevel.SLIGHT_BULL, "偏多", "轻仓参与，仓位30-40%"),
            (-1, SignalLevel.NEUTRAL, "中性", "观望为主，仓位20-30%"),
            (-4, SignalLevel.SLIGHT_BEAR, "偏空", "减仓观望，仓位10-20%"),
            (-7, SignalLevel.MODERATE_BEAR, "中空头", "防守为主，仓位5-10%"),
            (-100, SignalLevel.STRONG_BEAR, "强空头", "空仓或观望"),
        ]
        
        # 从配置中读取
        if strength_config:
            for level_name, level_config in strength_config.items():
                if level_name == "description":
                    continue
                
                min_score = level_config.get("min_score", -100)
                max_score = level_config.get("max_score", 100)
                
                if min_score <= score <= max_score:
                    try:
                        signal_level = SignalLevel(level_name)
                    except ValueError:
                        signal_level = SignalLevel.NEUTRAL
                    
                    return (
                        signal_level,
                        level_config.get("label", "未知"),
                        level_config.get("operation", "")
                    )
        
        # 使用默认逻辑
        for min_score, level, label, operation in default_levels:
            if score >= min_score:
                return (level, label, operation)
        
        return (SignalLevel.STRONG_BEAR, "强空头", "空仓或观望")
    
    def check_risks(self, context: Dict[str, Any]) -> List[RiskWarning]:
        """检查风险因素
        
        Args:
            context: 上下文变量
        
        Returns:
            List[RiskWarning]: 触发的风险预警列表
        """
        warnings = []
        
        if "risk_rules" not in self.config:
            return warnings
        
        risk_config = self.config["risk_rules"]
        
        for category, rules in risk_config.items():
            if category == "description":
                continue
            
            for rule_name, rule_config in rules.items():
                if self.evaluate_condition(rule_config["condition"], context):
                    try:
                        level = RiskLevel(rule_config.get("level", "info"))
                    except ValueError:
                        level = RiskLevel.INFO
                    
                    warnings.append(RiskWarning(
                        rule_name=rule_name,
                        level=level,
                        message=rule_config.get("message", ""),
                        condition=rule_config["condition"]
                    ))
        
        return warnings
    
    def get_config_summary(self) -> Dict[str, Any]:
        """获取配置摘要"""
        return {
            "version": self.config.get("version", "unknown"),
            "update_time": self.config.get("update_time", "unknown"),
            "has_index_signal": "index_signal" in self.config,
            "has_stock_signal": "stock_signal" in self.config,
            "has_risk_rules": "risk_rules" in self.config,
        }


# 测试代码
if __name__ == "__main__":
    print("=" * 60)
    print("信号评分引擎测试")
    print("=" * 60)
    
    engine = SignalEngine()
    
    # 配置摘要
    print("\n配置摘要:")
    summary = engine.get_config_summary()
    for key, value in summary.items():
        print(f"  {key}: {value}")
    
    # 测试指数信号评分
    print("\n测试指数信号评分:")
    test_context = {
        "daily_signal": "BULL",
        "weekly_signal": "BULL",
        "monthly_signal": "NEUTRAL",
        "deviation_pct": 2.5,
        "volume_ratio": 1.2,
        "north_money_inflow_days": 3,
        "north_money_outflow_days": 0,
    }
    
    result = engine.calculate_index_signal(test_context)
    print(f"  总评分: {result.total_score}")
    print(f"  信号级别: {result.signal_level.value}")
    print(f"  信号标签: {result.signal_label}")
    print(f"  操作建议: {result.operation_suggestion}")
    print(f"  评分分解: {result.score_breakdown}")
    print(f"  触发因子:")
    for factor in result.triggered_factors:
        print(f"    - {factor.name}: {factor.description} (权重: {factor.weight})")
    
    # 测试风险检查
    print("\n测试风险检查:")
    risk_context = {
        "rsi": 78,
        "consecutive_yang": 8,
    }
    
    risks = engine.check_risks(risk_context)
    for risk in risks:
        print(f"  [{risk.level.value}] {risk.message}")


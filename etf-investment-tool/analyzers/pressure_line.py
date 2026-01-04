#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
6124-5178 压力线计算模块

历史背景：
- 2007年10月16日：上证指数创下6124.04点的历史高点
- 2015年6月12日：上证指数创下5178.19点的次高点
- 连接这两个高点形成的下降趋势线，代表A股近18年的长期压力

参考文档: docs/analysis_methodology.md
"""

from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import Tuple, Optional
import pandas as pd


@dataclass
class PressureLineResult:
    """压力线计算结果"""
    target_date: str           # 目标日期
    pressure_position: float   # 压力线位置（点位）
    current_price: float       # 当前价格
    deviation: float           # 偏离点数 (当前价格 - 压力线)
    deviation_pct: float       # 偏离百分比
    is_above: bool            # 是否站上压力线
    is_breakthrough: bool      # 是否有效突破（> 3%）
    breakthrough_status: str   # 突破状态描述
    days_above: int           # 连续站上压力线天数（用于三日原则）


@dataclass
class HistoricalPoint:
    """历史高点数据"""
    date: datetime
    value: float
    description: str


class PressureLineCalculator:
    """6124-5178 压力线计算器"""
    
    # 历史高点数据
    POINT_6124 = HistoricalPoint(
        date=datetime(2007, 10, 16),
        value=6124.04,
        description="2007年10月历史最高点"
    )
    
    POINT_5178 = HistoricalPoint(
        date=datetime(2015, 6, 12),
        value=5178.19,
        description="2015年6月次高点"
    )
    
    def __init__(self):
        """初始化压力线计算器"""
        self._calculate_line_params()
    
    def _calculate_line_params(self):
        """计算压力线参数（斜率和截距）"""
        # 时间跨度（天数）
        days_diff = (self.POINT_5178.date - self.POINT_6124.date).days
        
        # 点位差
        value_diff = self.POINT_5178.value - self.POINT_6124.value
        
        # 每日斜率
        self.daily_slope = value_diff / days_diff
        
        # 每月斜率（约30天）
        self.monthly_slope = self.daily_slope * 30
        
        # 截距（以6124点为基准）
        self.intercept = self.POINT_6124.value
        self.base_date = self.POINT_6124.date
        
        # 输出参数信息
        print(f"[压力线参数] 日斜率: {self.daily_slope:.6f}, 月斜率: {self.monthly_slope:.4f}")
    
    def get_position(self, target_date: datetime) -> float:
        """计算指定日期的压力线位置
        
        Args:
            target_date: 目标日期
        
        Returns:
            float: 压力线点位
        """
        days_diff = (target_date - self.base_date).days
        position = self.intercept + self.daily_slope * days_diff
        return round(position, 2)
    
    def get_position_by_str(self, date_str: str, fmt: str = "%Y-%m-%d") -> float:
        """通过字符串日期计算压力线位置
        
        Args:
            date_str: 日期字符串
            fmt: 日期格式
        
        Returns:
            float: 压力线点位
        """
        target_date = datetime.strptime(date_str, fmt)
        return self.get_position(target_date)
    
    def analyze(self, current_price: float, 
                target_date: Optional[datetime] = None,
                df: Optional[pd.DataFrame] = None) -> PressureLineResult:
        """分析当前价格与压力线的关系
        
        Args:
            current_price: 当前价格（指数点位）
            target_date: 目标日期，默认为今天
            df: K线数据（用于计算连续站上天数）
        
        Returns:
            PressureLineResult: 分析结果
        """
        if target_date is None:
            target_date = datetime.now()
        
        # 计算压力线位置
        pressure_position = self.get_position(target_date)
        
        # 计算偏离
        deviation = current_price - pressure_position
        deviation_pct = (deviation / pressure_position) * 100
        
        # 判断是否站上压力线
        is_above = current_price > pressure_position
        
        # 判断是否有效突破（3%法则）
        is_breakthrough = deviation_pct >= 3.0
        
        # 突破状态描述
        if is_breakthrough:
            breakthrough_status = "有效突破（≥3%）"
        elif deviation_pct > 0:
            breakthrough_status = f"站上压力线（+{deviation_pct:.2f}%），待确认"
        elif deviation_pct > -3:
            breakthrough_status = f"接近压力线（{deviation_pct:.2f}%）"
        elif deviation_pct > -10:
            breakthrough_status = f"低于压力线（{deviation_pct:.2f}%）"
        else:
            breakthrough_status = f"远离压力线（{deviation_pct:.2f}%）"
        
        # 计算连续站上压力线天数（三日原则）
        days_above = 0
        if df is not None and not df.empty and '收盘' in df.columns:
            # 从最近的日期往回检查
            for i in range(len(df) - 1, -1, -1):
                row = df.iloc[i]
                row_date = pd.to_datetime(row['日期']) if '日期' in df.columns else target_date - timedelta(days=len(df)-1-i)
                row_pressure = self.get_position(row_date)
                row_price = float(row['收盘'])
                
                if row_price > row_pressure:
                    days_above += 1
                else:
                    break
        
        return PressureLineResult(
            target_date=target_date.strftime("%Y-%m-%d"),
            pressure_position=round(pressure_position, 2),
            current_price=round(current_price, 2),
            deviation=round(deviation, 2),
            deviation_pct=round(deviation_pct, 2),
            is_above=is_above,
            is_breakthrough=is_breakthrough,
            breakthrough_status=breakthrough_status,
            days_above=days_above
        )
    
    def get_historical_positions(self, start_date: datetime, 
                                  end_date: datetime) -> pd.DataFrame:
        """获取历史压力线位置序列
        
        Args:
            start_date: 开始日期
            end_date: 结束日期
        
        Returns:
            pd.DataFrame: 包含日期和压力线位置的 DataFrame
        """
        dates = []
        positions = []
        
        current_date = start_date
        while current_date <= end_date:
            dates.append(current_date)
            positions.append(self.get_position(current_date))
            current_date += timedelta(days=1)
        
        return pd.DataFrame({
            '日期': dates,
            '压力线': positions
        })
    
    def get_key_dates(self) -> dict:
        """获取关键日期的压力线位置
        
        Returns:
            dict: 关键日期及其压力线位置
        """
        key_dates = {
            "2007-10-16 (6124高点)": self.POINT_6124.value,
            "2015-06-12 (5178高点)": self.POINT_5178.value,
            "2020-01-01": self.get_position_by_str("2020-01-01"),
            "2021-01-01": self.get_position_by_str("2021-01-01"),
            "2022-01-01": self.get_position_by_str("2022-01-01"),
            "2023-01-01": self.get_position_by_str("2023-01-01"),
            "2024-01-01": self.get_position_by_str("2024-01-01"),
            "2025-01-01": self.get_position_by_str("2025-01-01"),
            "2025-12-31": self.get_position_by_str("2025-12-31"),
            "2026-01-01": self.get_position_by_str("2026-01-01"),
        }
        return key_dates
    
    def validate_breakthrough(self, df: pd.DataFrame, 
                               target_date: Optional[datetime] = None) -> dict:
        """验证突破有效性（综合3%法则和三日原则）
        
        Args:
            df: K线数据，需包含 '日期', '收盘', '成交量' 列
            target_date: 目标日期
        
        Returns:
            dict: 验证结果
        """
        if df.empty or len(df) < 3:
            return {"valid": False, "reason": "数据不足"}
        
        if target_date is None:
            target_date = datetime.now()
        
        current_price = float(df['收盘'].iloc[-1])
        pressure_position = self.get_position(target_date)
        
        # 3% 法则验证
        deviation_pct = (current_price - pressure_position) / pressure_position * 100
        rule_3pct = deviation_pct >= 3.0
        
        # 三日原则验证
        days_above = 0
        for i in range(len(df) - 1, max(len(df) - 4, -1), -1):
            row = df.iloc[i]
            row_date = pd.to_datetime(row['日期']) if '日期' in df.columns else target_date - timedelta(days=len(df)-1-i)
            row_pressure = self.get_position(row_date)
            row_price = float(row['收盘'])
            
            if row_price > row_pressure:
                days_above += 1
            else:
                break
        
        rule_3days = days_above >= 3
        
        # 成交量验证
        volume_valid = False
        if '成交量' in df.columns:
            recent_volume = df['成交量'].tail(5).mean()
            prev_volume = df['成交量'].tail(20).head(15).mean()
            volume_ratio = recent_volume / prev_volume if prev_volume > 0 else 1
            volume_valid = volume_ratio >= 1.2  # 放量20%以上
        
        # 综合判断
        is_valid = rule_3pct and rule_3days
        
        return {
            "valid": is_valid,
            "rule_3pct": rule_3pct,
            "deviation_pct": round(deviation_pct, 2),
            "rule_3days": rule_3days,
            "days_above": days_above,
            "volume_valid": volume_valid,
            "volume_ratio": round(volume_ratio, 2) if '成交量' in df.columns else None,
            "pressure_position": round(pressure_position, 2),
            "current_price": round(current_price, 2),
            "summary": "有效突破" if is_valid else ("待确认" if deviation_pct > 0 else "未突破")
        }


# 测试代码
if __name__ == "__main__":
    print("=" * 60)
    print("6124-5178 压力线计算测试")
    print("=" * 60)
    
    calc = PressureLineCalculator()
    
    # 输出关键日期的压力线位置
    print("\n关键日期压力线位置：")
    for date_str, position in calc.get_key_dates().items():
        print(f"  {date_str}: {position:.2f}")
    
    # 测试当前日期
    today = datetime.now()
    current_position = calc.get_position(today)
    print(f"\n今日 ({today.strftime('%Y-%m-%d')}) 压力线位置: {current_position:.2f}")
    
    # 模拟分析
    test_prices = [3800, 3900, 4000, 4100]
    print("\n不同价格的压力线分析：")
    for price in test_prices:
        result = calc.analyze(price)
        print(f"  价格 {price}: {result.breakthrough_status}")


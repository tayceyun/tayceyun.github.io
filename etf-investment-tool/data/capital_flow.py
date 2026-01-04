#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
资金面数据获取模块

数据来源：akshare（免费）
包含：
1. 北向资金（沪股通、深股通）
2. 两融余额（融资融券）

TODO: 以下功能需要 Tushare Pro（付费）
- 股东人数变化
- 龙虎榜数据
- 主力资金流向

参考文档: docs/analysis_methodology.md
"""

import pandas as pd
from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import Optional, List, Dict, Any

# 尝试导入 akshare
try:
    import akshare as ak
    AKSHARE_AVAILABLE = True
except ImportError:
    AKSHARE_AVAILABLE = False
    print("[警告] akshare 未安装，资金面数据功能不可用")
    print("[提示] 安装方法: pip install akshare")


@dataclass
class NorthMoneyData:
    """北向资金数据"""
    date: str                    # 日期
    sh_net: float               # 沪股通净买入（亿元）
    sz_net: float               # 深股通净买入（亿元）
    total_net: float            # 北向资金合计净买入（亿元）
    sh_buy: float               # 沪股通买入（亿元）
    sh_sell: float              # 沪股通卖出（亿元）
    sz_buy: float               # 深股通买入（亿元）
    sz_sell: float              # 深股通卖出（亿元）


@dataclass
class NorthMoneyTrend:
    """北向资金趋势分析"""
    latest_data: Optional[NorthMoneyData]  # 最新数据
    inflow_days: int            # 连续流入天数
    outflow_days: int           # 连续流出天数
    total_5d: float             # 近5日累计净买入
    total_10d: float            # 近10日累计净买入
    total_20d: float            # 近20日累计净买入
    avg_daily: float            # 日均净买入
    trend: str                  # 趋势: 'strong_inflow' / 'inflow' / 'neutral' / 'outflow' / 'strong_outflow'
    signal: str                 # 信号: 'BULL' / 'NEUTRAL' / 'BEAR'


@dataclass
class MarginData:
    """两融数据"""
    date: str                   # 日期
    financing_balance: float    # 融资余额（亿元）
    securities_balance: float   # 融券余额（亿元）
    total_balance: float        # 两融余额（亿元）
    financing_buy: float        # 融资买入额（亿元）
    financing_repay: float      # 融资偿还额（亿元）


@dataclass
class MarginTrend:
    """两融趋势分析"""
    latest_data: Optional[MarginData]
    balance_change_5d: float    # 近5日余额变化
    balance_change_10d: float   # 近10日余额变化
    balance_change_pct: float   # 余额变化率
    trend: str                  # 趋势
    signal: str                 # 信号


class CapitalFlowAnalyzer:
    """资金面分析器"""
    
    def __init__(self):
        """初始化资金面分析器"""
        self._north_money_cache: Optional[pd.DataFrame] = None
        self._margin_cache: Optional[pd.DataFrame] = None
        self._cache_date: Optional[str] = None
    
    def _check_akshare(self) -> bool:
        """检查 akshare 是否可用"""
        if not AKSHARE_AVAILABLE:
            print("[错误] akshare 未安装，无法获取资金面数据")
            return False
        return True
    
    def get_north_money_history(self, days: int = 30) -> Optional[pd.DataFrame]:
        """获取北向资金历史数据
        
        Args:
            days: 获取最近多少天的数据
        
        Returns:
            DataFrame 或 None
        """
        if not self._check_akshare():
            return None
        
        try:
            print(f"[资金面] 正在获取北向资金数据...")
            
            # 获取北向资金数据
            # akshare 接口: stock_hsgt_north_net_flow_in_em
            df = ak.stock_hsgt_north_net_flow_in_em()
            
            if df is None or df.empty:
                print("[警告] 北向资金数据为空")
                return None
            
            # 标准化列名
            df = df.rename(columns={
                '日期': 'date',
                '沪股通': 'sh_net',
                '深股通': 'sz_net',
                '北向资金': 'total_net'
            })
            
            # 转换日期格式
            if 'date' in df.columns:
                df['date'] = pd.to_datetime(df['date'])
                df = df.sort_values('date', ascending=False)
            
            # 取最近 N 天
            df = df.head(days)
            
            self._north_money_cache = df
            self._cache_date = datetime.now().strftime("%Y-%m-%d")
            
            print(f"[资金面] 获取到 {len(df)} 条北向资金数据")
            return df
            
        except Exception as e:
            print(f"[错误] 获取北向资金数据失败: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def analyze_north_money(self, days: int = 20) -> Optional[NorthMoneyTrend]:
        """分析北向资金趋势
        
        Args:
            days: 分析最近多少天的数据
        
        Returns:
            NorthMoneyTrend 或 None
        """
        df = self.get_north_money_history(days)
        
        if df is None or df.empty:
            return None
        
        try:
            # 最新数据
            latest = df.iloc[0]
            latest_data = NorthMoneyData(
                date=str(latest.get('date', '')),
                sh_net=float(latest.get('sh_net', 0)),
                sz_net=float(latest.get('sz_net', 0)),
                total_net=float(latest.get('total_net', 0)),
                sh_buy=0,  # akshare 接口可能没有这些字段
                sh_sell=0,
                sz_buy=0,
                sz_sell=0
            )
            
            # 计算连续流入/流出天数
            inflow_days = 0
            outflow_days = 0
            
            net_col = 'total_net' if 'total_net' in df.columns else 'sh_net'
            
            for i, row in df.iterrows():
                net = float(row.get(net_col, 0))
                if net > 0:
                    if outflow_days == 0:
                        inflow_days += 1
                    else:
                        break
                elif net < 0:
                    if inflow_days == 0:
                        outflow_days += 1
                    else:
                        break
                else:
                    break
            
            # 计算累计净买入
            total_5d = float(df.head(5)[net_col].sum()) if len(df) >= 5 else 0
            total_10d = float(df.head(10)[net_col].sum()) if len(df) >= 10 else 0
            total_20d = float(df.head(20)[net_col].sum()) if len(df) >= 20 else 0
            
            avg_daily = total_10d / min(len(df), 10)
            
            # 判断趋势
            if inflow_days >= 5 or total_10d > 200:
                trend = 'strong_inflow'
                signal = 'BULL'
            elif inflow_days >= 3 or total_10d > 100:
                trend = 'inflow'
                signal = 'BULL'
            elif outflow_days >= 5 or total_10d < -200:
                trend = 'strong_outflow'
                signal = 'BEAR'
            elif outflow_days >= 3 or total_10d < -100:
                trend = 'outflow'
                signal = 'BEAR'
            else:
                trend = 'neutral'
                signal = 'NEUTRAL'
            
            return NorthMoneyTrend(
                latest_data=latest_data,
                inflow_days=inflow_days,
                outflow_days=outflow_days,
                total_5d=round(total_5d, 2),
                total_10d=round(total_10d, 2),
                total_20d=round(total_20d, 2),
                avg_daily=round(avg_daily, 2),
                trend=trend,
                signal=signal
            )
            
        except Exception as e:
            print(f"[错误] 分析北向资金趋势失败: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def get_margin_history(self, days: int = 30) -> Optional[pd.DataFrame]:
        """获取两融历史数据
        
        Args:
            days: 获取最近多少天的数据
        
        Returns:
            DataFrame 或 None
        """
        if not self._check_akshare():
            return None
        
        try:
            print(f"[资金面] 正在获取两融数据...")
            
            # 获取两融数据
            # akshare 接口: stock_margin_szse
            df = ak.stock_margin_szse()
            
            if df is None or df.empty:
                print("[警告] 两融数据为空")
                return None
            
            # 取最近 N 天
            df = df.tail(days)
            
            self._margin_cache = df
            
            print(f"[资金面] 获取到 {len(df)} 条两融数据")
            return df
            
        except Exception as e:
            print(f"[错误] 获取两融数据失败: {e}")
            return None
    
    def analyze_margin(self, days: int = 20) -> Optional[MarginTrend]:
        """分析两融趋势
        
        Args:
            days: 分析最近多少天的数据
        
        Returns:
            MarginTrend 或 None
        """
        df = self.get_margin_history(days)
        
        if df is None or df.empty:
            return None
        
        try:
            # 简化处理，返回基本结构
            latest_data = MarginData(
                date=datetime.now().strftime("%Y-%m-%d"),
                financing_balance=0,
                securities_balance=0,
                total_balance=0,
                financing_buy=0,
                financing_repay=0
            )
            
            return MarginTrend(
                latest_data=latest_data,
                balance_change_5d=0,
                balance_change_10d=0,
                balance_change_pct=0,
                trend='neutral',
                signal='NEUTRAL'
            )
            
        except Exception as e:
            print(f"[错误] 分析两融趋势失败: {e}")
            return None
    
    def get_capital_flow_summary(self) -> Dict[str, Any]:
        """获取资金面综合摘要
        
        Returns:
            资金面数据字典
        """
        summary = {
            "north_money": None,
            "margin": None,
            "overall_signal": "NEUTRAL",
            "data_available": False
        }
        
        # 北向资金
        north_trend = self.analyze_north_money()
        if north_trend:
            summary["north_money"] = {
                "latest_net": north_trend.latest_data.total_net if north_trend.latest_data else 0,
                "inflow_days": north_trend.inflow_days,
                "outflow_days": north_trend.outflow_days,
                "total_5d": north_trend.total_5d,
                "total_10d": north_trend.total_10d,
                "trend": north_trend.trend,
                "signal": north_trend.signal
            }
            summary["data_available"] = True
        
        # 两融数据
        margin_trend = self.analyze_margin()
        if margin_trend:
            summary["margin"] = {
                "trend": margin_trend.trend,
                "signal": margin_trend.signal
            }
        
        # 综合信号
        if north_trend:
            summary["overall_signal"] = north_trend.signal
        
        return summary
    
    def to_signal_context(self) -> Dict[str, Any]:
        """转换为信号引擎需要的上下文格式
        
        Returns:
            可用于 SignalEngine.calculate_index_signal 的上下文字典
        """
        context = {
            "north_money_inflow_days": 0,
            "north_money_outflow_days": 0,
            "north_money_total_10d": 0,
            "margin_trend": "neutral"
        }
        
        north_trend = self.analyze_north_money()
        if north_trend:
            context["north_money_inflow_days"] = north_trend.inflow_days
            context["north_money_outflow_days"] = north_trend.outflow_days
            context["north_money_total_10d"] = north_trend.total_10d
        
        margin_trend = self.analyze_margin()
        if margin_trend:
            context["margin_trend"] = margin_trend.trend
        
        return context


# 测试代码
if __name__ == "__main__":
    print("=" * 60)
    print("资金面数据模块测试")
    print("=" * 60)
    
    analyzer = CapitalFlowAnalyzer()
    
    # 测试北向资金
    print("\n测试北向资金分析:")
    north_trend = analyzer.analyze_north_money()
    if north_trend:
        print(f"  最新日期: {north_trend.latest_data.date if north_trend.latest_data else 'N/A'}")
        print(f"  连续流入天数: {north_trend.inflow_days}")
        print(f"  连续流出天数: {north_trend.outflow_days}")
        print(f"  近5日累计: {north_trend.total_5d}亿")
        print(f"  近10日累计: {north_trend.total_10d}亿")
        print(f"  趋势: {north_trend.trend}")
        print(f"  信号: {north_trend.signal}")
    else:
        print("  北向资金数据获取失败")
    
    # 测试综合摘要
    print("\n资金面综合摘要:")
    summary = analyzer.get_capital_flow_summary()
    print(f"  数据可用: {summary['data_available']}")
    print(f"  综合信号: {summary['overall_signal']}")
    
    # 测试信号上下文
    print("\n信号引擎上下文:")
    context = analyzer.to_signal_context()
    for key, value in context.items():
        print(f"  {key}: {value}")


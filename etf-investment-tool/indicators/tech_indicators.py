#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
技术指标计算模块
包含 MACD、RSI、均线、布林带、K线形态等常用技术指标的计算

参考文档: docs/analysis_methodology.md
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum


class SignalType(Enum):
    """信号类型枚举"""
    BULL = 1      # 多头
    NEUTRAL = 0   # 震荡/中性
    BEAR = -1     # 空头


@dataclass
class MACDResult:
    """MACD 计算结果"""
    dif: float           # 快线
    dea: float           # 慢线
    macd: float          # 柱状图 (DIF - DEA) * 2
    cross: str           # 'golden' / 'death' / 'none'
    trend: str           # 'rising' / 'falling' / 'flat'
    position: str        # 'above_zero' / 'below_zero'
    signal: SignalType   # 综合信号


@dataclass
class RSIResult:
    """RSI 计算结果"""
    value: float         # RSI 值
    status: str          # 'overbought' / 'oversold' / 'normal'
    signal: SignalType   # 综合信号


@dataclass
class MAResult:
    """均线系统计算结果"""
    ma5: float
    ma10: float
    ma20: float
    ma60: float
    ma250: float
    arrangement: str     # 'bull' / 'bear' / 'mixed'
    price_position: str  # 'above_all' / 'below_all' / 'middle'
    signal: SignalType


@dataclass
class BollingerResult:
    """布林带计算结果"""
    upper: float         # 上轨
    middle: float        # 中轨
    lower: float         # 下轨
    width: float         # 带宽百分比
    position: str        # 'above_upper' / 'near_upper' / 'middle' / 'near_lower' / 'below_lower'
    signal: SignalType


@dataclass
class KLinePattern:
    """K线形态结果"""
    consecutive_yang: int    # 连阳天数
    consecutive_yin: int     # 连阴天数
    pattern: str             # 'yang_engulf' / 'yin_engulf' / 'hammer' / 'doji' / 'none'
    signal: SignalType


@dataclass
class TechIndicatorsSummary:
    """技术指标综合结果"""
    macd: MACDResult
    rsi: RSIResult
    ma: MAResult
    bollinger: BollingerResult
    kline: KLinePattern
    overall_signal: SignalType
    signal_score: int        # 综合评分 -10 到 +10


class TechIndicators:
    """技术指标计算器"""
    
    # 默认参数
    DEFAULT_PARAMS = {
        'macd_fast': 12,
        'macd_slow': 26,
        'macd_signal': 9,
        'rsi_period': 14,
        'rsi_overbought': 70,
        'rsi_oversold': 30,
        'bollinger_period': 20,
        'bollinger_std': 2,
    }
    
    def __init__(self, params: Optional[Dict] = None):
        """初始化技术指标计算器
        
        Args:
            params: 自定义参数，覆盖默认值
        """
        self.params = {**self.DEFAULT_PARAMS, **(params or {})}
    
    def calculate_all(self, df: pd.DataFrame, price_col: str = '收盘') -> TechIndicatorsSummary:
        """计算所有技术指标
        
        Args:
            df: K线数据 DataFrame，需包含 '开盘', '最高', '最低', '收盘' 列
            price_col: 收盘价列名
        
        Returns:
            TechIndicatorsSummary: 综合指标结果
        """
        if df.empty or len(df) < 60:
            raise ValueError("数据不足，至少需要60条记录")
        
        macd = self.calculate_macd(df, price_col)
        rsi = self.calculate_rsi(df, price_col)
        ma = self.calculate_ma(df, price_col)
        bollinger = self.calculate_bollinger(df, price_col)
        kline = self.analyze_kline_pattern(df)
        
        # 计算综合评分
        signal_score = self._calculate_signal_score(macd, rsi, ma, bollinger, kline)
        
        # 确定整体信号
        if signal_score >= 3:
            overall_signal = SignalType.BULL
        elif signal_score <= -3:
            overall_signal = SignalType.BEAR
        else:
            overall_signal = SignalType.NEUTRAL
        
        return TechIndicatorsSummary(
            macd=macd,
            rsi=rsi,
            ma=ma,
            bollinger=bollinger,
            kline=kline,
            overall_signal=overall_signal,
            signal_score=signal_score
        )
    
    def calculate_macd(self, df: pd.DataFrame, price_col: str = '收盘') -> MACDResult:
        """计算 MACD 指标
        
        MACD = EMA(12) - EMA(26)
        Signal = EMA(MACD, 9)
        Histogram = (MACD - Signal) * 2
        
        Args:
            df: K线数据
            price_col: 价格列名
        
        Returns:
            MACDResult: MACD 计算结果
        """
        close = df[price_col].astype(float)
        
        fast_period = self.params['macd_fast']
        slow_period = self.params['macd_slow']
        signal_period = self.params['macd_signal']
        
        # 计算 EMA
        ema_fast = close.ewm(span=fast_period, adjust=False).mean()
        ema_slow = close.ewm(span=slow_period, adjust=False).mean()
        
        # DIF = 快线 - 慢线
        dif = ema_fast - ema_slow
        
        # DEA = DIF 的 EMA
        dea = dif.ewm(span=signal_period, adjust=False).mean()
        
        # MACD 柱状图
        macd_hist = (dif - dea) * 2
        
        current_dif = float(dif.iloc[-1])
        current_dea = float(dea.iloc[-1])
        current_macd = float(macd_hist.iloc[-1])
        
        prev_dif = float(dif.iloc[-2]) if len(dif) > 1 else current_dif
        prev_dea = float(dea.iloc[-2]) if len(dea) > 1 else current_dea
        
        # 判断金叉/死叉
        if prev_dif <= prev_dea and current_dif > current_dea:
            cross = 'golden'
        elif prev_dif >= prev_dea and current_dif < current_dea:
            cross = 'death'
        else:
            cross = 'none'
        
        # 判断趋势
        if len(macd_hist) >= 3:
            recent_macd = macd_hist.tail(3).tolist()
            if all(recent_macd[i] < recent_macd[i+1] for i in range(len(recent_macd)-1)):
                trend = 'rising'
            elif all(recent_macd[i] > recent_macd[i+1] for i in range(len(recent_macd)-1)):
                trend = 'falling'
            else:
                trend = 'flat'
        else:
            trend = 'flat'
        
        # 零轴位置
        position = 'above_zero' if current_dif > 0 else 'below_zero'
        
        # 综合信号判断
        if cross == 'golden' or (position == 'above_zero' and trend == 'rising'):
            signal = SignalType.BULL
        elif cross == 'death' or (position == 'below_zero' and trend == 'falling'):
            signal = SignalType.BEAR
        else:
            signal = SignalType.NEUTRAL
        
        return MACDResult(
            dif=round(current_dif, 4),
            dea=round(current_dea, 4),
            macd=round(current_macd, 4),
            cross=cross,
            trend=trend,
            position=position,
            signal=signal
        )
    
    def calculate_rsi(self, df: pd.DataFrame, price_col: str = '收盘') -> RSIResult:
        """计算 RSI 指标
        
        RSI = 100 - 100 / (1 + RS)
        RS = 平均涨幅 / 平均跌幅
        
        Args:
            df: K线数据
            price_col: 价格列名
        
        Returns:
            RSIResult: RSI 计算结果
        """
        close = df[price_col].astype(float)
        period = self.params['rsi_period']
        
        # 计算价格变化
        delta = close.diff()
        
        # 分离涨跌
        gain = delta.where(delta > 0, 0)
        loss = (-delta).where(delta < 0, 0)
        
        # 计算平均涨跌幅
        avg_gain = gain.rolling(window=period, min_periods=period).mean()
        avg_loss = loss.rolling(window=period, min_periods=period).mean()
        
        # 计算 RS 和 RSI
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        current_rsi = float(rsi.iloc[-1])
        
        # 判断状态
        overbought = self.params['rsi_overbought']
        oversold = self.params['rsi_oversold']
        
        if current_rsi >= overbought:
            status = 'overbought'
            signal = SignalType.BEAR  # 超买可能回调
        elif current_rsi <= oversold:
            status = 'oversold'
            signal = SignalType.BULL  # 超卖可能反弹
        else:
            status = 'normal'
            signal = SignalType.NEUTRAL
        
        return RSIResult(
            value=round(current_rsi, 2),
            status=status,
            signal=signal
        )
    
    def calculate_ma(self, df: pd.DataFrame, price_col: str = '收盘') -> MAResult:
        """计算均线系统
        
        计算 MA5, MA10, MA20, MA60, MA250
        判断多头/空头排列
        
        Args:
            df: K线数据
            price_col: 价格列名
        
        Returns:
            MAResult: 均线计算结果
        """
        close = df[price_col].astype(float)
        current_price = float(close.iloc[-1])
        
        # 计算各周期均线
        ma5 = float(close.tail(5).mean())
        ma10 = float(close.tail(10).mean())
        ma20 = float(close.tail(20).mean())
        ma60 = float(close.tail(60).mean()) if len(close) >= 60 else ma20
        ma250 = float(close.tail(250).mean()) if len(close) >= 250 else ma60
        
        # 判断均线排列
        short_mas = [ma5, ma10, ma20]
        if all(short_mas[i] >= short_mas[i+1] for i in range(len(short_mas)-1)):
            if ma20 >= ma60:
                arrangement = 'bull'  # 多头排列
            else:
                arrangement = 'mixed'
        elif all(short_mas[i] <= short_mas[i+1] for i in range(len(short_mas)-1)):
            if ma20 <= ma60:
                arrangement = 'bear'  # 空头排列
            else:
                arrangement = 'mixed'
        else:
            arrangement = 'mixed'  # 混乱排列
        
        # 判断价格相对均线位置
        if current_price > ma5 and current_price > ma10 and current_price > ma20:
            price_position = 'above_all'
        elif current_price < ma5 and current_price < ma10 and current_price < ma20:
            price_position = 'below_all'
        else:
            price_position = 'middle'
        
        # 综合信号
        if arrangement == 'bull' and price_position == 'above_all':
            signal = SignalType.BULL
        elif arrangement == 'bear' and price_position == 'below_all':
            signal = SignalType.BEAR
        else:
            signal = SignalType.NEUTRAL
        
        return MAResult(
            ma5=round(ma5, 2),
            ma10=round(ma10, 2),
            ma20=round(ma20, 2),
            ma60=round(ma60, 2),
            ma250=round(ma250, 2),
            arrangement=arrangement,
            price_position=price_position,
            signal=signal
        )
    
    def calculate_bollinger(self, df: pd.DataFrame, price_col: str = '收盘') -> BollingerResult:
        """计算布林带
        
        中轨 = MA(20)
        上轨 = 中轨 + 2 * STD(20)
        下轨 = 中轨 - 2 * STD(20)
        
        Args:
            df: K线数据
            price_col: 价格列名
        
        Returns:
            BollingerResult: 布林带计算结果
        """
        close = df[price_col].astype(float)
        current_price = float(close.iloc[-1])
        
        period = self.params['bollinger_period']
        std_dev = self.params['bollinger_std']
        
        # 计算中轨和标准差
        middle = float(close.tail(period).mean())
        std = float(close.tail(period).std())
        
        # 计算上下轨
        upper = middle + std_dev * std
        lower = middle - std_dev * std
        
        # 计算带宽百分比
        width = (upper - lower) / middle * 100
        
        # 判断价格位置
        if current_price > upper:
            position = 'above_upper'
            signal = SignalType.BEAR  # 超买区域
        elif current_price > middle + (upper - middle) * 0.5:
            position = 'near_upper'
            signal = SignalType.NEUTRAL
        elif current_price < lower:
            position = 'below_lower'
            signal = SignalType.BULL  # 超卖区域
        elif current_price < middle - (middle - lower) * 0.5:
            position = 'near_lower'
            signal = SignalType.NEUTRAL
        else:
            position = 'middle'
            signal = SignalType.NEUTRAL
        
        return BollingerResult(
            upper=round(upper, 2),
            middle=round(middle, 2),
            lower=round(lower, 2),
            width=round(width, 2),
            position=position,
            signal=signal
        )
    
    def analyze_kline_pattern(self, df: pd.DataFrame) -> KLinePattern:
        """分析K线形态
        
        识别连阳连阴、阳包阴、阴包阳、锤头线、十字星等形态
        
        Args:
            df: K线数据，需包含 '开盘', '收盘', '最高', '最低' 列
        
        Returns:
            KLinePattern: K线形态分析结果
        """
        if len(df) < 2:
            return KLinePattern(0, 0, 'none', SignalType.NEUTRAL)
        
        opens = df['开盘'].astype(float)
        closes = df['收盘'].astype(float)
        highs = df['最高'].astype(float)
        lows = df['最低'].astype(float)
        
        # 判断阳线/阴线
        is_yang = closes > opens
        
        # 计算连阳/连阴天数
        consecutive_yang = 0
        consecutive_yin = 0
        
        for i in range(len(is_yang) - 1, -1, -1):
            if is_yang.iloc[i]:
                if consecutive_yin == 0:
                    consecutive_yang += 1
                else:
                    break
            else:
                if consecutive_yang == 0:
                    consecutive_yin += 1
                else:
                    break
        
        # 识别特殊形态
        pattern = 'none'
        signal = SignalType.NEUTRAL
        
        if len(df) >= 2:
            # 最近两根K线
            prev_open = float(opens.iloc[-2])
            prev_close = float(closes.iloc[-2])
            curr_open = float(opens.iloc[-1])
            curr_close = float(closes.iloc[-1])
            curr_high = float(highs.iloc[-1])
            curr_low = float(lows.iloc[-1])
            
            # 阳包阴（看涨）
            if prev_close < prev_open and curr_close > curr_open:
                if curr_open <= prev_close and curr_close >= prev_open:
                    pattern = 'yang_engulf'
                    signal = SignalType.BULL
            
            # 阴包阳（看跌）
            elif prev_close > prev_open and curr_close < curr_open:
                if curr_open >= prev_close and curr_close <= prev_open:
                    pattern = 'yin_engulf'
                    signal = SignalType.BEAR
            
            # 锤头线（下影线长，实体小）
            body = abs(curr_close - curr_open)
            lower_shadow = min(curr_open, curr_close) - curr_low
            upper_shadow = curr_high - max(curr_open, curr_close)
            
            if body > 0 and lower_shadow > body * 2 and upper_shadow < body * 0.5:
                pattern = 'hammer'
                signal = SignalType.BULL
            
            # 十字星（实体极小）
            price_range = curr_high - curr_low
            if price_range > 0 and body / price_range < 0.1:
                pattern = 'doji'
                signal = SignalType.NEUTRAL
        
        # 连阳连阴的信号
        if consecutive_yang >= 5:
            signal = SignalType.BULL if signal == SignalType.NEUTRAL else signal
        elif consecutive_yin >= 5:
            signal = SignalType.BEAR if signal == SignalType.NEUTRAL else signal
        
        return KLinePattern(
            consecutive_yang=consecutive_yang,
            consecutive_yin=consecutive_yin,
            pattern=pattern,
            signal=signal
        )
    
    def _calculate_signal_score(self, macd: MACDResult, rsi: RSIResult,
                                 ma: MAResult, bollinger: BollingerResult,
                                 kline: KLinePattern) -> int:
        """计算综合信号评分
        
        评分范围: -10 到 +10
        
        Args:
            各项指标结果
        
        Returns:
            int: 综合评分
        """
        score = 0
        
        # MACD 评分 (权重 25%)
        if macd.signal == SignalType.BULL:
            score += 2
            if macd.cross == 'golden':
                score += 1
        elif macd.signal == SignalType.BEAR:
            score -= 2
            if macd.cross == 'death':
                score -= 1
        
        # RSI 评分 (权重 15%)
        if rsi.signal == SignalType.BULL:
            score += 1
        elif rsi.signal == SignalType.BEAR:
            score -= 1
        
        # 均线系统评分 (权重 25%)
        if ma.signal == SignalType.BULL:
            score += 2
            if ma.arrangement == 'bull':
                score += 1
        elif ma.signal == SignalType.BEAR:
            score -= 2
            if ma.arrangement == 'bear':
                score -= 1
        
        # 布林带评分 (权重 15%)
        if bollinger.signal == SignalType.BULL:
            score += 1
        elif bollinger.signal == SignalType.BEAR:
            score -= 1
        
        # K线形态评分 (权重 20%)
        if kline.signal == SignalType.BULL:
            score += 1
            if kline.consecutive_yang >= 5:
                score += 1
        elif kline.signal == SignalType.BEAR:
            score -= 1
            if kline.consecutive_yin >= 5:
                score -= 1
        
        # 限制评分范围
        return max(-10, min(10, score))
    
    def get_indicator_series(self, df: pd.DataFrame, indicator: str,
                              price_col: str = '收盘') -> pd.Series:
        """获取指标的时间序列数据（用于绘图）
        
        Args:
            df: K线数据
            indicator: 指标名称 ('macd_dif', 'macd_dea', 'macd_hist', 'rsi', 
                       'ma5', 'ma10', 'ma20', 'ma60', 'boll_upper', 'boll_mid', 'boll_lower')
            price_col: 价格列名
        
        Returns:
            pd.Series: 指标序列
        """
        close = df[price_col].astype(float)
        
        if indicator == 'macd_dif':
            ema_fast = close.ewm(span=self.params['macd_fast'], adjust=False).mean()
            ema_slow = close.ewm(span=self.params['macd_slow'], adjust=False).mean()
            return ema_fast - ema_slow
        
        elif indicator == 'macd_dea':
            dif = self.get_indicator_series(df, 'macd_dif', price_col)
            return dif.ewm(span=self.params['macd_signal'], adjust=False).mean()
        
        elif indicator == 'macd_hist':
            dif = self.get_indicator_series(df, 'macd_dif', price_col)
            dea = self.get_indicator_series(df, 'macd_dea', price_col)
            return (dif - dea) * 2
        
        elif indicator == 'rsi':
            delta = close.diff()
            gain = delta.where(delta > 0, 0)
            loss = (-delta).where(delta < 0, 0)
            avg_gain = gain.rolling(window=self.params['rsi_period'], min_periods=1).mean()
            avg_loss = loss.rolling(window=self.params['rsi_period'], min_periods=1).mean()
            rs = avg_gain / avg_loss
            return 100 - (100 / (1 + rs))
        
        elif indicator.startswith('ma'):
            period = int(indicator[2:])
            return close.rolling(window=period, min_periods=1).mean()
        
        elif indicator == 'boll_upper':
            mid = close.rolling(window=self.params['bollinger_period'], min_periods=1).mean()
            std = close.rolling(window=self.params['bollinger_period'], min_periods=1).std()
            return mid + self.params['bollinger_std'] * std
        
        elif indicator == 'boll_mid':
            return close.rolling(window=self.params['bollinger_period'], min_periods=1).mean()
        
        elif indicator == 'boll_lower':
            mid = close.rolling(window=self.params['bollinger_period'], min_periods=1).mean()
            std = close.rolling(window=self.params['bollinger_period'], min_periods=1).std()
            return mid - self.params['bollinger_std'] * std
        
        else:
            raise ValueError(f"未知指标: {indicator}")


# 测试代码
if __name__ == "__main__":
    import sys
    sys.path.insert(0, str(__file__).rsplit('/', 2)[0])
    
    from data_source import get_index_daily
    
    print("测试技术指标计算模块...")
    
    # 获取上证指数数据
    df = get_index_daily("000001", days=250)
    
    if not df.empty:
        indicators = TechIndicators()
        result = indicators.calculate_all(df)
        
        print(f"\n=== 上证指数技术指标分析 ===")
        print(f"\nMACD:")
        print(f"  DIF: {result.macd.dif}, DEA: {result.macd.dea}")
        print(f"  柱状图: {result.macd.macd}")
        print(f"  交叉: {result.macd.cross}, 趋势: {result.macd.trend}")
        print(f"  信号: {result.macd.signal.name}")
        
        print(f"\nRSI:")
        print(f"  值: {result.rsi.value}")
        print(f"  状态: {result.rsi.status}")
        print(f"  信号: {result.rsi.signal.name}")
        
        print(f"\n均线系统:")
        print(f"  MA5: {result.ma.ma5}, MA10: {result.ma.ma10}, MA20: {result.ma.ma20}")
        print(f"  MA60: {result.ma.ma60}, MA250: {result.ma.ma250}")
        print(f"  排列: {result.ma.arrangement}")
        print(f"  信号: {result.ma.signal.name}")
        
        print(f"\n布林带:")
        print(f"  上轨: {result.bollinger.upper}, 中轨: {result.bollinger.middle}, 下轨: {result.bollinger.lower}")
        print(f"  带宽: {result.bollinger.width}%")
        print(f"  位置: {result.bollinger.position}")
        
        print(f"\nK线形态:")
        print(f"  连阳: {result.kline.consecutive_yang}天, 连阴: {result.kline.consecutive_yin}天")
        print(f"  形态: {result.kline.pattern}")
        
        print(f"\n综合评分: {result.signal_score}")
        print(f"整体信号: {result.overall_signal.name}")
    else:
        print("获取数据失败")

